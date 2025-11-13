from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field, validator
from diffusers import StableDiffusionPipeline
from backend.config.settings import HUGGINGFACEHUB_API_TOKEN, MAX_PROMPT_LENGTH
from backend.middleware.dependencies import verify_and_rate_limit
import torch
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Load the image generation model lazily
_pipe = None

def get_pipe():
    global _pipe
    if _pipe is None:
        logger.info("Loading Stable Diffusion model...")
        _pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            use_auth_token=HUGGINGFACEHUB_API_TOKEN,
            torch_dtype=torch.float32
        ).to("cpu")
        logger.info("Stable Diffusion model loaded successfully")
    return _pipe

class ImageRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation", min_length=3, max_length=MAX_PROMPT_LENGTH)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        # Basic content filtering (you may want to add more sophisticated filtering)
        prohibited_keywords = ['nsfw', 'nude', 'explicit']
        if any(keyword in v.lower() for keyword in prohibited_keywords):
            raise ValueError('Prompt contains prohibited content')
        return v.strip()

class ImageResponse(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded PNG image")
    prompt: str = Field(..., description="Original prompt used")
    processing_time: float = Field(..., description="Processing time in seconds")

@router.post("/generate", response_model=ImageResponse, status_code=status.HTTP_200_OK)
async def generate_image(
    req: ImageRequest,
    request: Request,
    api_key_info: dict = Depends(verify_and_rate_limit)
):
    """
    Generate an image from a text prompt using Stable Diffusion.
    
    - **prompt**: Text description of the image to generate
    
    Returns base64 encoded PNG image.
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Generating image for prompt: {req.prompt[:50]}... (tier: {api_key_info.get('tier', 'unknown')})")
        
        pipe = get_pipe()
        result = pipe(req.prompt, guidance_scale=8.5, num_inference_steps=50)
        image = result.images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        processing_time = time.time() - start_time
        logger.info(f"Image generation completed in {processing_time:.2f}s")

        return ImageResponse(
            image_base64=encoded_image,
            prompt=req.prompt,
            processing_time=processing_time
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate image. Please try again later."
        )
