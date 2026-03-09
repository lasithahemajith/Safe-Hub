import io
import random
import logging
import httpx
from typing import Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class DamageDetector:
    """
    AI Damage Detection Service.

    In production, replace the _analyze_image_data method with a real
    TensorFlow/PyTorch model. The current implementation uses rule-based
    heuristics for demonstration purposes.
    """

    DAMAGE_LEVELS = ["none", "minor", "moderate", "severe", "catastrophic"]

    def analyze_from_url(self, image_url: str) -> dict:
        try:
            response = httpx.get(image_url, timeout=15.0)
            response.raise_for_status()
            image_data = response.content
            return self._analyze_image_data(image_data)
        except Exception as e:
            logger.error(f"Failed to fetch image from URL: {e}")
            return self._fallback_response()

    def analyze_from_bytes(self, image_bytes: bytes) -> dict:
        return self._analyze_image_data(image_bytes)

    def _analyze_image_data(self, image_bytes: bytes) -> dict:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_array = np.array(img)

            # Feature extraction
            brightness = float(np.mean(img_array))
            contrast = float(np.std(img_array))

            # Color channel analysis
            red_mean = float(np.mean(img_array[:, :, 0]))
            green_mean = float(np.mean(img_array[:, :, 1]))
            blue_mean = float(np.mean(img_array[:, :, 2]))

            # Heuristic rules (replace with real model in production)
            damage_score = 0.0

            # Dark images may indicate fire/smoke
            if brightness < 80:
                damage_score += 0.3

            # High red channel may indicate fire
            if red_mean > green_mean * 1.4 and red_mean > blue_mean * 1.4:
                damage_score += 0.35

            # Low contrast may indicate flooding (uniform water surface)
            if contrast < 40:
                damage_score += 0.2

            # High variance in specific areas may indicate structural damage
            quadrant_variance = self._quadrant_variance(img_array)
            if quadrant_variance > 60:
                damage_score += 0.25

            damage_score = min(damage_score, 1.0)
            confidence = round(0.6 + random.uniform(0.0, 0.35), 2)

            if damage_score < 0.15:
                damage_level = "none"
            elif damage_score < 0.3:
                damage_level = "minor"
            elif damage_score < 0.5:
                damage_level = "moderate"
            elif damage_score < 0.75:
                damage_level = "severe"
            else:
                damage_level = "catastrophic"

            return {
                "damage_level": damage_level,
                "confidence": confidence,
                "damage_score": round(damage_score, 3),
                "features": {
                    "brightness": round(brightness, 2),
                    "contrast": round(contrast, 2),
                    "red_mean": round(red_mean, 2),
                    "green_mean": round(green_mean, 2),
                    "blue_mean": round(blue_mean, 2),
                },
            }
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return self._fallback_response()

    def _quadrant_variance(self, img_array: np.ndarray) -> float:
        h, w = img_array.shape[:2]
        mid_h, mid_w = h // 2, w // 2
        quadrants = [
            img_array[:mid_h, :mid_w],
            img_array[:mid_h, mid_w:],
            img_array[mid_h:, :mid_w],
            img_array[mid_h:, mid_w:],
        ]
        variances = [float(np.std(q)) for q in quadrants]
        return float(np.std(variances))

    def _fallback_response(self) -> dict:
        return {
            "damage_level": "unknown",
            "confidence": 0.0,
            "damage_score": 0.0,
            "features": {},
        }


detector = DamageDetector()
