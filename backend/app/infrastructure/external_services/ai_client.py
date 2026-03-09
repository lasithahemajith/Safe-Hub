import httpx
from typing import Optional
from app.core.config import settings


class AIService:
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL

    async def analyze_image(self, image_url: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/analyze",
                    json={"image_url": image_url},
                )
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return None


ai_service = AIService()
