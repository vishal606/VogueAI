"""
Agent 2: Vision Analyzer
Classifies fashion images using CLIP (OpenAI) model via HuggingFace Transformers.
Extracts: clothing type, dominant color, pattern, style tags, embeddings.
"""
import asyncio
import io
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import httpx
import numpy as np

from app.utils.logger import logger

# Lazy-loaded to avoid import errors if torch not installed
_clip_model = None
_clip_processor = None
_clip_loaded = False


def _load_clip():
    global _clip_model, _clip_processor, _clip_loaded
    if _clip_loaded:
        return _clip_model is not None
    try:
        from transformers import CLIPProcessor, CLIPModel
        import torch
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model.eval()
        _clip_loaded = True
        logger.info("[VisionAnalyzer] CLIP model loaded successfully")
        return True
    except Exception as e:
        logger.warning(f"[VisionAnalyzer] CLIP model unavailable: {e}. Using mock mode.")
        _clip_loaded = True
        return False


# Fashion label sets for zero-shot classification
CLOTHING_TYPES = [
    "dress", "blouse", "shirt", "pants", "jeans", "skirt", "jacket",
    "coat", "sweater", "hoodie", "suit", "blazer", "shorts", "leggings",
    "jumpsuit", "romper", "cardigan", "vest", "top", "bodysuit",
]

STYLE_TAGS = [
    "minimalist", "bohemian", "streetwear", "luxury", "casual", "formal",
    "vintage", "athleisure", "preppy", "edgy", "romantic", "classic",
    "avant-garde", "cottagecore", "dark academia", "quiet luxury",
]

PATTERNS = [
    "solid", "striped", "plaid", "floral", "geometric", "animal print",
    "abstract", "paisley", "polka dot", "color block", "tie-dye",
    "houndstooth", "checkered", "embroidered",
]


class VisionAnalyzer:
    """Agent 2: Analyzes fashion images for trends."""

    def __init__(self):
        self._model_available = _load_clip()

    async def analyze_image_url(self, image_url: str) -> Dict[str, Any]:
        """
        Full pipeline:
          1. Download image
          2. Classify clothing type
          3. Extract dominant colors
          4. Detect pattern
          5. Tag style
          6. Generate CLIP embedding
        """
        try:
            image = await self._download_image(image_url)
            if image is None:
                return self._empty_result()

            clothing_type, clothing_conf = await self._classify_clothing(image)
            color_palette = self._extract_colors(image)
            pattern, pattern_conf = await self._classify_pattern(image)
            style_tags = await self._classify_styles(image)
            embedding = self._get_embedding(image) if self._model_available else None

            return {
                "clothing_type": clothing_type,
                "dominant_color": color_palette[0]["name"] if color_palette else None,
                "color_palette": color_palette,
                "pattern": pattern,
                "style_tags": style_tags,
                "confidence": clothing_conf,
                "embedding": embedding,
                "model_used": "clip-vit-base-patch32" if self._model_available else "mock",
                "raw_predictions": {
                    "clothing_confidence": clothing_conf,
                    "pattern_confidence": pattern_conf,
                },
            }
        except Exception as e:
            logger.error(f"[VisionAnalyzer] Error analyzing {image_url}: {e}")
            return self._empty_result()

    async def _download_image(self, url: str) -> Optional[Image.Image]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content)).convert("RGB")
        except Exception as e:
            logger.warning(f"[VisionAnalyzer] Could not download image {url}: {e}")
            return None

    async def _classify_clothing(self, image: Image.Image) -> Tuple[str, float]:
        if not self._model_available:
            return "dress", 0.75  # mock

        try:
            import torch
            texts = [f"a photo of a {c}" for c in CLOTHING_TYPES]
            inputs = _clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
            with torch.no_grad():
                outputs = _clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1).squeeze()
            best_idx = probs.argmax().item()
            return CLOTHING_TYPES[best_idx], round(probs[best_idx].item(), 3)
        except Exception as e:
            logger.warning(f"[VisionAnalyzer] Classification error: {e}")
            return "unknown", 0.0

    async def _classify_pattern(self, image: Image.Image) -> Tuple[str, float]:
        if not self._model_available:
            return "solid", 0.80

        try:
            import torch
            texts = [f"a {p} pattern fabric" for p in PATTERNS]
            inputs = _clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
            with torch.no_grad():
                outputs = _clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1).squeeze()
            best_idx = probs.argmax().item()
            return PATTERNS[best_idx], round(probs[best_idx].item(), 3)
        except Exception:
            return "unknown", 0.0

    async def _classify_styles(self, image: Image.Image) -> List[str]:
        if not self._model_available:
            return ["minimalist", "quiet luxury"]

        try:
            import torch
            texts = [f"a {s} fashion style" for s in STYLE_TAGS]
            inputs = _clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
            with torch.no_grad():
                outputs = _clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1).squeeze()
            # Return top 3 styles above threshold
            top_indices = (probs > 0.05).nonzero(as_tuple=True)[0].tolist()
            top_indices = sorted(top_indices, key=lambda i: probs[i], reverse=True)[:3]
            return [STYLE_TAGS[i] for i in top_indices]
        except Exception:
            return []

    def _extract_colors(self, image: Image.Image, n_colors: int = 5) -> List[Dict[str, Any]]:
        """K-means color quantization to find dominant palette."""
        try:
            from sklearn.cluster import KMeans
            img_small = image.resize((100, 100))
            pixels = np.array(img_small).reshape(-1, 3).astype(float)
            k = min(n_colors, len(pixels))
            kmeans = KMeans(n_clusters=k, n_init=3, random_state=42)
            kmeans.fit(pixels)
            centers = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            total = len(labels)
            palette = []
            for i, center in enumerate(centers):
                pct = round((labels == i).sum() / total * 100, 1)
                hex_color = "#{:02X}{:02X}{:02X}".format(*center)
                palette.append({
                    "hex": hex_color,
                    "name": self._name_color(center),
                    "percentage": pct,
                    "rgb": center.tolist(),
                })
            palette.sort(key=lambda x: x["percentage"], reverse=True)
            return palette
        except Exception as e:
            logger.warning(f"[VisionAnalyzer] Color extraction error: {e}")
            return [{"hex": "#C9A96E", "name": "Champagne", "percentage": 100.0, "rgb": [201, 169, 110]}]

    def _name_color(self, rgb: np.ndarray) -> str:
        """Map RGB to nearest named color bucket."""
        r, g, b = rgb
        COLOR_NAMES = {
            "Red": (220, 50, 50), "Pink": (220, 100, 140), "Orange": (220, 120, 50),
            "Yellow": (220, 200, 50), "Green": (50, 150, 80), "Teal": (50, 180, 170),
            "Blue": (50, 100, 200), "Navy": (30, 50, 120), "Purple": (120, 60, 180),
            "Lavender": (170, 140, 210), "Brown": (140, 90, 60), "Beige": (210, 190, 160),
            "White": (240, 240, 240), "Gray": (150, 150, 150), "Black": (30, 30, 30),
            "Gold": (200, 170, 80), "Champagne": (210, 185, 140),
        }
        min_dist = float("inf")
        best = "Unknown"
        for name, ref in COLOR_NAMES.items():
            dist = sum((a - b_) ** 2 for a, b_ in zip([r, g, b], ref)) ** 0.5
            if dist < min_dist:
                min_dist = dist
                best = name
        return best

    def _get_embedding(self, image: Image.Image) -> Optional[List[float]]:
        """Returns 512-dim CLIP image embedding for vector DB storage."""
        try:
            import torch
            inputs = _clip_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                features = _clip_model.get_image_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
            return features.squeeze().tolist()
        except Exception:
            return None

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "clothing_type": None,
            "dominant_color": None,
            "color_palette": [],
            "pattern": None,
            "style_tags": [],
            "confidence": 0.0,
            "embedding": None,
            "model_used": "none",
            "raw_predictions": {},
        }


# Singleton
_vision_analyzer: Optional[VisionAnalyzer] = None


def get_vision_analyzer() -> VisionAnalyzer:
    global _vision_analyzer
    if _vision_analyzer is None:
        _vision_analyzer = VisionAnalyzer()
    return _vision_analyzer
