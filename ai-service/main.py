import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from models.damage_detector import detector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SafeNZ AI Damage Detection Service", version="1.0.0")


class ImageURLRequest(BaseModel):
    image_url: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-damage-detector"}


@app.post("/analyze")
async def analyze_from_url(request: ImageURLRequest):
    """Analyze an image from a URL for damage detection."""
    if not request.image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
    result = detector.analyze_from_url(request.image_url)
    return result


@app.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Analyze an uploaded image for damage detection."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    result = detector.analyze_from_bytes(content)
    return result
