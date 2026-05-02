"""
Agent 3: Trend Analyzer — NLP pipeline
- Hashtag extraction & frequency analysis
- Keyword extraction (KeyBERT / TF-IDF fallback)
- Sentiment analysis (TextBlob / transformers)
- Engagement-weighted trend scoring
- Trend scoring algorithm
"""
import re
import asyncio
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta

from app.db.models.models import RawPost, TextFeature, Trend, Source
from app.db.schemas.schemas import TrendCreate
from app.utils.logger import logger


class NLPAnalyzer:
    """Agent 3: Extracts trends from text content of raw posts."""

    FASHION_STOP_WORDS = {
        "fashion", "style", "outfit", "look", "wear", "wearing", "ootd",
        "love", "beautiful", "amazing", "inspo", "follow", "like", "share",
        "photo", "pic", "new", "today", "day", "time", "good", "great",
    }

    def __init__(self):
        self._sentiment_available = False
        self._keybert_available = False
        self._try_load_models()

    def _try_load_models(self):
        try:
            from textblob import TextBlob
            self._TextBlob = TextBlob
            self._sentiment_available = True
            logger.info("[TrendAnalyzer] TextBlob loaded")
        except ImportError:
            logger.warning("[TrendAnalyzer] TextBlob unavailable, using heuristic sentiment")

        try:
            from keybert import KeyBERT
            self._kw_model = KeyBERT()
            self._keybert_available = True
            logger.info("[TrendAnalyzer] KeyBERT loaded")
        except ImportError:
            logger.warning("[TrendAnalyzer] KeyBERT unavailable, using TF-IDF fallback")

    # ── Text Feature Extraction ───────────────────────────────────────────────

    def extract_hashtags(self, text: str) -> List[str]:
        """Extract all hashtags from post caption."""
        if not text:
            return []
        tags = re.findall(r"#(\w+)", text.lower())
        # Filter very short or very long tags
        return [t for t in tags if 2 < len(t) < 40]

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords using KeyBERT or TF-IDF fallback."""
        if not text or len(text.strip()) < 10:
            return []

        if self._keybert_available:
            try:
                keywords = self._kw_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words="english",
                    top_n=top_n,
                )
                return [kw for kw, _ in keywords]
            except Exception as e:
                logger.warning(f"[TrendAnalyzer] KeyBERT extraction failed: {e}")

        # TF-IDF fallback
        return self._tfidf_keywords(text, top_n)

    def _tfidf_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Simple frequency-based keyword extraction."""
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        fashion_vocab = {
            "aesthetic", "collection", "trend", "season", "color", "palette",
            "texture", "fabric", "silhouette", "minimalist", "maximalist",
            "vintage", "luxury", "streetwear", "athleisure", "couture",
            "bohemian", "classic", "elegant", "chic", "edgy", "casual",
            "formal", "resort", "capsule", "wardrobe", "accessory",
        }
        scored = Counter(
            w for w in words
            if w not in self.FASHION_STOP_WORDS and (w in fashion_vocab or len(w) > 5)
        )
        return [word for word, _ in scored.most_common(top_n)]

    def analyze_sentiment(self, text: str) -> float:
        """Returns sentiment score: -1.0 (negative) to +1.0 (positive)."""
        if not text:
            return 0.0

        if self._sentiment_available:
            try:
                blob = self._TextBlob(text)
                return round(blob.sentiment.polarity, 3)
            except Exception:
                pass

        # Heuristic fallback
        positive_words = {"love", "amazing", "beautiful", "gorgeous", "perfect", "obsessed", "stunning"}
        negative_words = {"hate", "ugly", "terrible", "awful", "bad", "worst", "disappointed"}
        words = set(text.lower().split())
        pos = len(words & positive_words)
        neg = len(words & negative_words)
        if pos + neg == 0:
            return 0.0
        return round((pos - neg) / (pos + neg), 3)

    def process_post(self, post: RawPost) -> Dict[str, Any]:
        """Full NLP pipeline for a single raw post."""
        text = f"{post.caption or ''}"
        hashtags = self.extract_hashtags(text)
        keywords = self.extract_keywords(text)
        sentiment = self.analyze_sentiment(text)

        return {
            "hashtags": hashtags,
            "keywords": keywords,
            "sentiment": sentiment,
            "language": "en",
            "topics": self._classify_topics(hashtags + keywords),
        }

    def _classify_topics(self, terms: List[str]) -> List[str]:
        """Map extracted terms to high-level fashion topics."""
        topic_map = {
            "Style": {"minimalist", "maximalist", "streetwear", "bohemian", "classic", "luxe", "quiet", "casual"},
            "Color": {"color", "palette", "tonal", "monochrome", "colorful", "neutral"},
            "Fabric": {"silk", "linen", "cotton", "denim", "velvet", "knit", "leather", "satin"},
            "Season": {"spring", "summer", "fall", "winter", "resort", "holiday"},
            "Occasion": {"work", "office", "casual", "evening", "wedding", "weekend", "travel"},
        }
        found = set()
        term_set = {t.lower() for t in terms}
        for topic, keywords in topic_map.items():
            if term_set & keywords:
                found.add(topic)
        return list(found)

    # ── Trend Detection ───────────────────────────────────────────────────────

    async def detect_emerging_trends(
        self, db: AsyncSession, lookback_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Scan recent raw posts for hashtag clusters that indicate emerging trends.
        Uses engagement-weighted frequency scoring.
        """
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
        result = await db.execute(
            select(RawPost)
            .where(RawPost.scraped_at >= cutoff)
            .where(RawPost.is_processed == True)
            .limit(5000)
        )
        posts = result.scalars().all()

        if not posts:
            logger.info("[TrendAnalyzer] No recent posts to analyze")
            return []

        hashtag_scores: Dict[str, float] = {}
        hashtag_posts: Dict[str, int] = {}

        for post in posts:
            # Engagement weight: normalised score 0-1
            total_engagement = post.likes + post.comments * 3 + post.shares * 5
            engagement_weight = min(total_engagement / 10000, 1.0)

            for tag in self.extract_hashtags(post.caption or ""):
                if tag in self.FASHION_STOP_WORDS:
                    continue
                hashtag_scores[tag] = hashtag_scores.get(tag, 0) + (1 + engagement_weight)
                hashtag_posts[tag] = hashtag_posts.get(tag, 0) + 1

        # Filter: must appear in at least 3 posts, not too generic
        candidates = [
            {
                "hashtag": tag,
                "score": round(score, 2),
                "post_count": hashtag_posts[tag],
                "avg_engagement_weight": round(score / hashtag_posts[tag], 3),
            }
            for tag, score in hashtag_scores.items()
            if hashtag_posts[tag] >= 3
        ]
        candidates.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"[TrendAnalyzer] Detected {len(candidates)} candidate trends")
        return candidates[:50]

    # ── Trend Scoring Algorithm ───────────────────────────────────────────────

    def compute_engagement_score(
        self,
        likes: int,
        comments: int,
        shares: int,
        views: int = 0,
        follower_count: int = 1,
    ) -> float:
        """
        Weighted engagement rate:
          Likes: 1x, Comments: 3x (higher intent), Shares: 5x (virality), Views: 0.1x
        Normalised to 0-100.
        """
        raw = likes * 1 + comments * 3 + shares * 5 + views * 0.1
        # Normalise against follower count if available
        if follower_count > 0:
            rate = raw / follower_count * 100
        else:
            rate = raw / 1000  # fallback normalisation
        return min(round(rate, 2), 100.0)

    def compute_hashtag_trend_score(
        self,
        current_count: int,
        previous_count: int,
        engagement_weight: float = 1.0,
    ) -> Tuple[float, float]:
        """Returns (trend_score 0-100, growth_rate %)."""
        if previous_count == 0:
            growth_rate = 100.0
        else:
            growth_rate = ((current_count - previous_count) / previous_count) * 100

        # Score: recency + growth + engagement
        base_score = min(current_count / 1000, 1.0) * 40  # volume component
        growth_score = min(growth_rate / 100, 1.0) * 40   # growth component
        engagement_score = engagement_weight * 20           # engagement component
        trend_score = base_score + growth_score + engagement_score

        return round(min(trend_score, 100), 2), round(growth_rate, 2)


# Singleton
_nlp_analyzer: Optional[NLPAnalyzer] = None


def get_nlp_analyzer() -> NLPAnalyzer:
    global _nlp_analyzer
    if _nlp_analyzer is None:
        _nlp_analyzer = NLPAnalyzer()
    return _nlp_analyzer
