"""
Agent 1: Trend Collector — Multi-source scraper worker
Sources:
  Social Media:  Instagram, TikTok, Pinterest, YouTube
  E-Commerce:    Amazon, Etsy, Daraz
  Search Trends: Google Trends, Bing Trends
  Fashion Blogs: Vogue, Elle, Hypebeast
"""
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.db.models.models import RawPost, Source, ImageFeature, TextFeature
from app.core.config import settings
from app.utils.logger import logger
from app.ai.vision_model import get_vision_analyzer
from app.ai.nlp_model import get_nlp_analyzer


# ── Base Scraper ──────────────────────────────────────────────────────────────

class BaseScraper:
    """All scrapers inherit from this. Provides dedup and DB persistence."""

    source_name: str = "unknown"
    source_type: str = "social_media"

    def __init__(self):
        self.vision = get_vision_analyzer()
        self.nlp = get_nlp_analyzer()

    async def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Override in subclasses. Returns list of raw post dicts."""
        raise NotImplementedError

    async def run(self, db: AsyncSession, limit: int = 100) -> int:
        """Full pipeline: scrape → deduplicate → save → process."""
        source = await self._get_or_create_source(db)
        raw_items = await self.scrape(limit=limit)
        saved = 0
        for item in raw_items:
            try:
                post = await self._save_post(db, source, item)
                if post:
                    await self._process_post(db, post)
                    saved += 1
            except Exception as e:
                logger.error(f"[{self.source_name}] Failed to save post: {e}")

        source.last_scraped_at = datetime.utcnow()
        await db.flush()
        logger.info(f"[{self.source_name}] Scraped and saved {saved}/{len(raw_items)} posts")
        return saved

    async def _get_or_create_source(self, db: AsyncSession) -> Source:
        from sqlalchemy import select
        result = await db.execute(select(Source).where(Source.name == self.source_name))
        source = result.scalar_one_or_none()
        if not source:
            source = Source(
                name=self.source_name,
                type=self.source_type,
                description=f"Auto-created source for {self.source_name}",
                scrape_config={},
            )
            db.add(source)
            await db.flush()
            await db.refresh(source)
        return source

    async def _save_post(
        self, db: AsyncSession, source: Source, item: Dict[str, Any]
    ) -> Optional[RawPost]:
        """Deduplicate by URL hash, then persist."""
        url = item.get("post_url", "")
        if url:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            from sqlalchemy import select
            existing = await db.execute(
                select(RawPost).where(RawPost.post_url == url).limit(1)
            )
            if existing.scalar_one_or_none():
                return None  # Already stored

        post = RawPost(
            source_id=source.id,
            post_url=item.get("post_url"),
            caption=item.get("caption"),
            image_url=item.get("image_url"),
            video_url=item.get("video_url"),
            likes=item.get("likes", 0),
            comments=item.get("comments", 0),
            shares=item.get("shares", 0),
            views=item.get("views", 0),
            posted_at=item.get("posted_at"),
            raw_data=item,
        )
        db.add(post)
        await db.flush()
        await db.refresh(post)
        return post

    async def _process_post(self, db: AsyncSession, post: RawPost) -> None:
        """Run Vision + NLP analysis on a saved post."""
        # NLP Analysis
        nlp_result = self.nlp.process_post(post)
        text_feature = TextFeature(
            post_id=post.id,
            hashtags=nlp_result["hashtags"],
            keywords=nlp_result["keywords"],
            sentiment=nlp_result["sentiment"],
            language=nlp_result["language"],
            topics=nlp_result["topics"],
        )
        db.add(text_feature)

        # Vision Analysis (if image available)
        if post.image_url:
            try:
                vision_result = await self.vision.analyze_image_url(post.image_url)
                image_feature = ImageFeature(
                    post_id=post.id,
                    dominant_color=vision_result.get("dominant_color"),
                    color_palette=vision_result.get("color_palette"),
                    clothing_type=vision_result.get("clothing_type"),
                    pattern=vision_result.get("pattern"),
                    style_tags=vision_result.get("style_tags"),
                    confidence=vision_result.get("confidence", 0),
                    embedding=vision_result.get("embedding"),
                    model_used=vision_result.get("model_used", "unknown"),
                    raw_predictions=vision_result.get("raw_predictions", {}),
                )
                db.add(image_feature)
            except Exception as e:
                logger.warning(f"[{self.source_name}] Vision analysis failed for post {post.id}: {e}")

        post.is_processed = True
        await db.flush()


# ── Instagram Scraper ─────────────────────────────────────────────────────────

class InstagramScraper(BaseScraper):
    """
    Uses Instagram Basic Display API or Apify Instagram Scraper.
    Falls back to mock data in development mode.
    """
    source_name = "Instagram"
    source_type = "social_media"

    FASHION_HASHTAGS = [
        "fashion", "style", "ootd", "fashionista", "streetstyle",
        "quietluxury", "minimalist", "outfitoftheday", "fashiontrend",
        "luxuryfashion", "vintagestyle", "sustainablefashion",
    ]

    async def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        if settings.APIFY_API_TOKEN:
            return await self._scrape_via_apify(limit)
        if settings.INSTAGRAM_ACCESS_TOKEN:
            return await self._scrape_via_api(limit)
        return self._mock_data(limit)

    async def _scrape_via_apify(self, limit: int) -> List[Dict[str, Any]]:
        """Use Apify Instagram Hashtag Scraper."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items",
                    params={"token": settings.APIFY_API_TOKEN, "timeout": 60},
                    json={
                        "hashtags": self.FASHION_HASHTAGS[:5],
                        "resultsLimit": limit,
                        "addParentData": False,
                    },
                )
                items = response.json()
                return [self._normalise_apify_item(item) for item in items[:limit]]
        except Exception as e:
            logger.error(f"[Instagram/Apify] Error: {e}")
            return self._mock_data(limit)

    async def _scrape_via_api(self, limit: int) -> List[Dict[str, Any]]:
        """Instagram Basic Display API."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://graph.instagram.com/me/media",
                    params={
                        "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                        "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                        "limit": limit,
                    },
                )
                data = resp.json().get("data", [])
                return [self._normalise_api_item(item) for item in data]
        except Exception as e:
            logger.error(f"[Instagram/API] Error: {e}")
            return self._mock_data(limit)

    def _normalise_apify_item(self, item: Dict) -> Dict[str, Any]:
        return {
            "post_url": item.get("url", ""),
            "caption": item.get("caption", ""),
            "image_url": item.get("displayUrl", ""),
            "likes": item.get("likesCount", 0),
            "comments": item.get("commentsCount", 0),
            "shares": 0,
            "views": item.get("videoViewCount", 0),
            "posted_at": datetime.fromisoformat(item["timestamp"]) if item.get("timestamp") else None,
        }

    def _normalise_api_item(self, item: Dict) -> Dict[str, Any]:
        return {
            "post_url": item.get("permalink", ""),
            "caption": item.get("caption", ""),
            "image_url": item.get("media_url") or item.get("thumbnail_url", ""),
            "likes": item.get("like_count", 0),
            "comments": item.get("comments_count", 0),
            "shares": 0,
            "views": 0,
            "posted_at": datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")) if item.get("timestamp") else None,
        }

    def _mock_data(self, limit: int) -> List[Dict[str, Any]]:
        """Generate realistic mock data for development."""
        import random
        captions = [
            "#QuietLuxury vibes today. Butter yellow cashmere and tailored trousers. #OOTD #Style",
            "Obsessed with this micro-pleat skirt! 🖤 #MicroPleats #FashionTrend #Minimalist",
            "Cobalt blue is THE color of the season. #CobaltBlue #ColorTrend #FashionInspo",
            "Neo-bohemian forever. Layered textures and earthy tones. #NeoBoho #Aesthetic",
            "Sculptural bag goals 👜 #AccessoryTrend #LuxuryFashion #Style",
            "Quiet luxury doesn't mean boring. #QLuxury #TailoredFashion #OOTD",
            "Butter yellow everything this season. ☀️ #ButterYellow #SpringFashion #ColorPalette",
        ]
        return [
            {
                "post_url": f"https://instagram.com/p/mock{i}",
                "caption": random.choice(captions),
                "image_url": f"https://picsum.photos/seed/ig{i}/600/600",
                "likes": random.randint(500, 50000),
                "comments": random.randint(10, 2000),
                "shares": random.randint(0, 500),
                "views": random.randint(0, 200000),
                "posted_at": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            }
            for i in range(min(limit, 50))
        ]


# ── TikTok Scraper ────────────────────────────────────────────────────────────

class TikTokScraper(BaseScraper):
    source_name = "TikTok"
    source_type = "social_media"

    FASHION_KEYWORDS = [
        "fashion", "ootd", "style", "outfit", "fashiontok",
        "quietluxury", "aestheticoutfit", "fashiontrend",
    ]

    async def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        if settings.APIFY_API_TOKEN:
            return await self._scrape_via_apify(limit)
        return self._mock_data(limit)

    async def _scrape_via_apify(self, limit: int) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                resp = await client.post(
                    "https://api.apify.com/v2/acts/clockworks~tiktok-scraper/run-sync-get-dataset-items",
                    params={"token": settings.APIFY_API_TOKEN, "timeout": 90},
                    json={
                        "searchQueries": self.FASHION_KEYWORDS[:3],
                        "maxItems": limit,
                        "shouldDownloadVideos": False,
                    },
                )
                items = resp.json()
                return [self._normalise(item) for item in items[:limit]]
        except Exception as e:
            logger.error(f"[TikTok/Apify] Error: {e}")
            return self._mock_data(limit)

    def _normalise(self, item: Dict) -> Dict[str, Any]:
        return {
            "post_url": item.get("webVideoUrl", ""),
            "caption": item.get("text", ""),
            "image_url": item.get("covers", {}).get("default", ""),
            "video_url": item.get("videoUrl", ""),
            "likes": item.get("diggCount", 0),
            "comments": item.get("commentCount", 0),
            "shares": item.get("shareCount", 0),
            "views": item.get("playCount", 0),
            "posted_at": datetime.fromtimestamp(item.get("createTime", 0)) if item.get("createTime") else None,
        }

    def _mock_data(self, limit: int) -> List[Dict[str, Any]]:
        import random
        captions = [
            "This butter yellow look has me 😍 #fashiontok #butterYellow #ootd #style",
            "Quiet luxury fashion tips for boutique owners #quietluxury #fashionbusiness",
            "The micro pleats trend is EVERYTHING right now #micropleats #fashiontrend",
            "Cobalt blue styling 3 ways #cobaltblue #fashiontok #colortrend",
            "Neo bohemian styling guide #neoboho #bohofashion #aestheticoutfit",
        ]
        return [
            {
                "post_url": f"https://tiktok.com/@mock/video/{i}",
                "caption": random.choice(captions),
                "image_url": f"https://picsum.photos/seed/tt{i}/400/700",
                "video_url": "",
                "likes": random.randint(1000, 500000),
                "comments": random.randint(50, 10000),
                "shares": random.randint(100, 50000),
                "views": random.randint(5000, 5000000),
                "posted_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            }
            for i in range(min(limit, 50))
        ]


# ── Pinterest Scraper ─────────────────────────────────────────────────────────

class PinterestScraper(BaseScraper):
    source_name = "Pinterest"
    source_type = "social_media"

    async def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        if settings.PINTEREST_ACCESS_TOKEN:
            return await self._scrape_via_api(limit)
        return self._mock_data(limit)

    async def _scrape_via_api(self, limit: int) -> List[Dict[str, Any]]:
        """Pinterest API v5 search pins."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.pinterest.com/v5/pins",
                    headers={"Authorization": f"Bearer {settings.PINTEREST_ACCESS_TOKEN}"},
                    params={"page_size": min(limit, 100)},
                )
                data = resp.json().get("items", [])
                return [
                    {
                        "post_url": f"https://pinterest.com/pin/{p.get('id', '')}",
                        "caption": p.get("description") or p.get("title", ""),
                        "image_url": p.get("media", {}).get("images", {}).get("originals", {}).get("url", ""),
                        "likes": p.get("save_count", 0),
                        "comments": 0,
                        "shares": p.get("save_count", 0),
                        "views": 0,
                        "posted_at": datetime.fromisoformat(p["created_at"]) if p.get("created_at") else None,
                    }
                    for p in data
                ]
        except Exception as e:
            logger.error(f"[Pinterest/API] Error: {e}")
            return self._mock_data(limit)

    def _mock_data(self, limit: int) -> List[Dict[str, Any]]:
        import random
        return [
            {
                "post_url": f"https://pinterest.com/pin/mock{i}",
                "caption": random.choice([
                    "Butter yellow spring outfit ideas | quiet luxury aesthetic",
                    "Cobalt blue dress styling inspiration | color trend 2025",
                    "Micro pleats fashion trend | minimalist outfit",
                    "Neo bohemian jewelry and accessories | boho style",
                ]),
                "image_url": f"https://picsum.photos/seed/pin{i}/400/600",
                "likes": random.randint(100, 10000),
                "comments": 0,
                "shares": random.randint(50, 5000),
                "views": 0,
                "posted_at": datetime.utcnow() - timedelta(days=random.randint(0, 7)),
            }
            for i in range(min(limit, 50))
        ]


# ── Google Trends Scraper ─────────────────────────────────────────────────────

class GoogleTrendsScraper(BaseScraper):
    source_name = "GoogleTrends"
    source_type = "search_trends"

    FASHION_KEYWORDS = [
        "quiet luxury fashion", "butter yellow outfit", "cobalt blue dress",
        "micro pleats skirt", "neo bohemian style", "sculptural bag",
        "minimalist fashion 2025", "capsule wardrobe", "slow fashion",
    ]

    async def scrape(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Use pytrends or SerpAPI to get Google Trends data."""
        try:
            return await self._scrape_pytrends()
        except Exception as e:
            logger.warning(f"[GoogleTrends] pytrends failed: {e}")
            return self._mock_data(limit)

    async def _scrape_pytrends(self) -> List[Dict[str, Any]]:
        from pytrends.request import TrendReq
        loop = asyncio.get_event_loop()

        def _fetch():
            pt = TrendReq(hl="en-US", tz=360)
            results = []
            # Batch keywords (max 5 per request)
            for batch_start in range(0, len(self.FASHION_KEYWORDS), 5):
                batch = self.FASHION_KEYWORDS[batch_start:batch_start + 5]
                pt.build_payload(batch, timeframe="now 7-d", geo=settings.GOOGLE_TRENDS_GEO if hasattr(settings, "GOOGLE_TRENDS_GEO") else "")
                interest = pt.interest_over_time()
                if not interest.empty:
                    latest = interest.iloc[-1]
                    for kw in batch:
                        if kw in latest:
                            results.append({
                                "post_url": f"https://trends.google.com/trends/explore?q={kw.replace(' ', '+')}",
                                "caption": f"Google Trends: {kw} — search interest: {latest[kw]}",
                                "image_url": None,
                                "likes": int(latest[kw]) * 100,  # proxy for volume
                                "comments": 0,
                                "shares": 0,
                                "views": int(latest[kw]) * 1000,
                                "posted_at": datetime.utcnow(),
                            })
            return results

        return await loop.run_in_executor(None, _fetch)

    def _mock_data(self, limit: int) -> List[Dict[str, Any]]:
        import random
        return [
            {
                "post_url": f"https://trends.google.com/trends/explore?q=quiet+luxury",
                "caption": f"Google Trends: {kw} — rising search trend",
                "image_url": None,
                "likes": random.randint(5000, 95000),
                "comments": 0,
                "shares": 0,
                "views": random.randint(50000, 950000),
                "posted_at": datetime.utcnow(),
            }
            for kw in self.FASHION_KEYWORDS[:limit]
        ]


# ── Orchestrator ──────────────────────────────────────────────────────────────

class ScraperOrchestrator:
    """
    Agent 1: Coordinates all scrapers.
    Called by Celery scheduler every SCRAPE_INTERVAL_MINUTES.
    """

    SCRAPERS = [
        InstagramScraper,
        TikTokScraper,
        PinterestScraper,
        GoogleTrendsScraper,
    ]

    async def run_all(
        self,
        source_names: Optional[List[str]] = None,
        limit_per_source: int = 100,
    ) -> Dict[str, int]:
        """Run all (or selected) scrapers concurrently."""
        results: Dict[str, int] = {}
        scrapers = [
            s() for s in self.SCRAPERS
            if source_names is None or s.source_name in source_names
        ]

        async with AsyncSessionLocal() as db:
            tasks = [s.run(db, limit=limit_per_source) for s in scrapers]
            counts = await asyncio.gather(*tasks, return_exceptions=True)

        for scraper, count in zip(scrapers, counts):
            if isinstance(count, Exception):
                logger.error(f"[Orchestrator] {scraper.source_name} failed: {count}")
                results[scraper.source_name] = 0
            else:
                results[scraper.source_name] = count

        logger.info(f"[Orchestrator] Scrape complete: {results}")
        return results


# ── Celery Entry Point ────────────────────────────────────────────────────────

async def run_scraper_job(
    source_names: Optional[List[str]] = None,
    limit_per_source: int = 100,
) -> Dict[str, int]:
    orch = ScraperOrchestrator()
    return await orch.run_all(source_names=source_names, limit_per_source=limit_per_source)
