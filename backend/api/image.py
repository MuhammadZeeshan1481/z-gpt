from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.config.settings import get_settings
import base64
from io import BytesIO

from backend.core.dependencies import get_current_user
from backend.db.models import User

router = APIRouter()

settings = get_settings()
_pipe = None
_device = (settings.image_device or "cpu").lower()

def _get_pipe():
    global _pipe
    if _pipe is not None:
        return _pipe
    if not settings.image_generation_enabled:
        raise RuntimeError("Image generation is disabled by configuration")
    from diffusers import StableDiffusionPipeline
    import torch
    model_id = settings.image_model or "runwayml/stable-diffusion-v1-5"
    try:
        torch_dtype = torch.float16 if _device.startswith("cuda") else torch.float32
        _pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
        ).to(_device)
        _pipe.enable_attention_slicing()
    except Exception as e:
        raise RuntimeError(f"Failed to load image pipeline: {e}")
    return _pipe

class ImageRequest(BaseModel):
    prompt: str

@router.post("/generate")
async def generate_image(req: ImageRequest, current_user: User = Depends(get_current_user)):
    try:
        if not settings.image_generation_enabled:
            raise HTTPException(status_code=503, detail="Image generation feature is disabled")
        pipe = _get_pipe()
        result = pipe(req.prompt, guidance_scale=8.5)
        image = result.images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {"image_base64": encoded_image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
