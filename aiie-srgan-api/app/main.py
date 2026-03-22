from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import UpscaleRequest, UpscaleResponse
from .utils import upscale_image

app = FastAPI(title="SRGAN API")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/sr", response_model=UpscaleResponse)
async def single_upscale(request: UpscaleRequest) -> UpscaleResponse:
    try:
        processed_image_url = await upscale_image(request.image_url)
        return UpscaleResponse(image_url=processed_image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
