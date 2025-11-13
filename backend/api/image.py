from fastapi import APIRouter, HTTPException
from diffusers import StableDiffusionPipeline
from backend.config import settings
from backend.models import ImageRequest, ImageResponse
import torch
import base64
from io import BytesIO

router = APIRouter()

# Load the image generation model
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    use_auth_token=settings.HUGGINGFACEHUB_API_TOKEN,
    torch_dtype=torch.float32
).to(settings.MODEL_DEVICE)

@router.post("/generate", response_model=ImageResponse)
async def generate_image(req: ImageRequest):
    try:
        result = pipe(req.prompt, guidance_scale=req.guidance_scale)
        image = result.images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return ImageResponse(image_base64=encoded_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
