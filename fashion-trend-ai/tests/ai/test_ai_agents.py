"""
Tests for AI agent modules:
  - NLP Analyzer (Agent 3)
  - Vision Analyzer (Agent 2) — mock mode
  - Forecasting (Agent 4) — fallback mode
  - TrendService scoring logic
"""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai.nlp_model import NLPAnalyzer, get_nlp_analyzer
from app.ai.forecasting import ProphetForecaster, LSTMForecaster, XGBoostForecaster


# ═══════════════════════════════════════════════════════════════
# NLP ANALYZER — Agent 3
# ═══════════════════════════════════════════════════════════════

class TestNLPAnalyzer:
    def setup_method(self):
        self.nlp = NLPAnalyzer()

    def test_extract_hashtags_basic(self):
        text = "Loving this look! #QuietLuxury #OOTD #minimalist #style"
        tags = self.nlp.extract_hashtags(text)
        assert "quietluxury" in tags
        assert "ootd" in tags
        assert "minimalist" in tags

    def test_extract_hashtags_empty(self):
        assert self.nlp.extract_hashtags("") == []
        assert self.nlp.extract_hashtags(None) == []

    def test_extract_hashtags_filters_short(self):
        tags = self.nlp.extract_hashtags("#hi #ok #fashion #style")
        assert "hi" not in tags
        assert "ok" not in tags

    def test_extract_keywords_returns_list(self):
        text = "Butter yellow cashmere sweater with tailored trousers for a minimalist look"
        keywords = self.nlp.extract_keywords(text)
        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_extract_keywords_short_text(self):
        keywords = self.nlp.extract_keywords("hi")
        assert keywords == []

    def test_sentiment_positive(self):
        score = self.nlp.analyze_sentiment("This outfit is absolutely amazing and gorgeous!")
        assert score > 0

    def test_sentiment_negative(self):
        score = self.nlp.analyze_sentiment("This is terrible and ugly, I hate it")
        assert score < 0

    def test_sentiment_neutral(self):
        score = self.nlp.analyze_sentiment("A blue shirt was photographed")
        # Should be close to 0 (neutral)
        assert -0.5 <= score <= 0.5

    def test_sentiment_empty(self):
        assert self.nlp.analyze_sentiment("") == 0.0

    def test_classify_topics_style(self):
        terms = ["minimalist", "streetwear", "casual"]
        topics = self.nlp._classify_topics(terms)
        assert "Style" in topics

    def test_classify_topics_color(self):
        terms = ["color", "palette", "tonal"]
        topics = self.nlp._classify_topics(terms)
        assert "Color" in topics

    def test_classify_topics_season(self):
        terms = ["spring", "summer", "resort"]
        topics = self.nlp._classify_topics(terms)
        assert "Season" in topics

    def test_classify_topics_empty(self):
        assert self.nlp._classify_topics([]) == []

    def test_compute_engagement_score_basic(self):
        score = self.nlp.compute_engagement_score(
            likes=1000, comments=50, shares=20, views=5000, follower_count=10000
        )
        assert 0 <= score <= 100

    def test_compute_engagement_score_zero_followers(self):
        score = self.nlp.compute_engagement_score(
            likes=100, comments=5, shares=2, follower_count=0
        )
        assert score >= 0

    def test_hashtag_trend_score(self):
        score, growth = self.nlp.compute_hashtag_trend_score(
            current_count=500, previous_count=250, engagement_weight=0.7
        )
        assert 0 <= score <= 100
        assert growth == pytest.approx(100.0)

    def test_hashtag_trend_score_no_previous(self):
        score, growth = self.nlp.compute_hashtag_trend_score(
            current_count=100, previous_count=0
        )
        assert growth == 100.0

    def test_tfidf_keywords(self):
        text = "The minimalist aesthetic features clean silhouettes and neutral palettes in luxury fabric"
        kws = self.nlp._tfidf_keywords(text, top_n=5)
        assert isinstance(kws, list)
        assert len(kws) <= 5

    def test_process_post_mock(self):
        from app.db.models.models import RawPost
        post = MagicMock(spec=RawPost)
        post.caption = "#QuietLuxury butter yellow cashmere outfit inspo"
        post.likes = 2000
        post.comments = 100
        post.shares = 50

        result = self.nlp.process_post(post)
        assert "hashtags" in result
        assert "keywords" in result
        assert "sentiment" in result
        assert "topics" in result
        assert isinstance(result["hashtags"], list)


# ═══════════════════════════════════════════════════════════════
# VISION ANALYZER — Agent 2 (mock mode, no GPU needed)
# ═══════════════════════════════════════════════════════════════

class TestVisionAnalyzer:
    def test_empty_result_structure(self):
        from app.ai.vision_model import VisionAnalyzer
        v = VisionAnalyzer()
        result = v._empty_result()
        assert "clothing_type" in result
        assert "dominant_color" in result
        assert "color_palette" in result
        assert "style_tags" in result
        assert "embedding" in result

    def test_name_color_red(self):
        import numpy as np
        from app.ai.vision_model import VisionAnalyzer
        v = VisionAnalyzer()
        name = v._name_color(np.array([220, 50, 50]))
        assert name == "Red"

    def test_name_color_black(self):
        import numpy as np
        from app.ai.vision_model import VisionAnalyzer
        v = VisionAnalyzer()
        name = v._name_color(np.array([20, 20, 20]))
        assert name == "Black"

    def test_name_color_white(self):
        import numpy as np
        from app.ai.vision_model import VisionAnalyzer
        v = VisionAnalyzer()
        name = v._name_color(np.array([245, 245, 245]))
        assert name == "White"

    @pytest.mark.asyncio
    async def test_analyze_image_url_bad_url(self):
        from app.ai.vision_model import VisionAnalyzer
        v = VisionAnalyzer()
        result = await v.analyze_image_url("https://this-url-does-not-exist-xyz.com/img.jpg")
        assert result["clothing_type"] is None or isinstance(result["clothing_type"], str)
        assert isinstance(result["color_palette"], list)


# ═══════════════════════════════════════════════════════════════
# FORECASTING — Agent 4
# ═══════════════════════════════════════════════════════════════

class MockPrediction:
    def __init__(self, value, days_ago):
        self.predicted_value = value
        self.prediction_date = date.today() - timedelta(days=days_ago)


def make_history(n=60, base=70.0, noise=5.0):
    import random
    return [MockPrediction(base + random.uniform(-noise, noise), n - i) for i in range(n)]


class TestProphetForecaster:
    def test_ets_fallback_rising(self):
        forecaster = ProphetForecaster()
        result = forecaster._ets_fallback(
            current=60.0,
            growth_rate=25.0,
            series=[55.0, 57.0, 59.0, 61.0, 63.0],
            horizon_days=30,
        )
        assert "predicted_value" in result
        assert "confidence" in result
        assert 0 <= result["predicted_value"] <= 100
        assert 0 <= result["confidence"] <= 1

    def test_ets_fallback_declining(self):
        forecaster = ProphetForecaster()
        result = forecaster._ets_fallback(
            current=40.0,
            growth_rate=-15.0,
            series=[50.0, 47.0, 44.0, 41.0, 38.0],
            horizon_days=30,
        )
        assert result["predicted_value"] >= 0

    def test_confidence_decay(self):
        forecaster = ProphetForecaster()
        conf_30 = forecaster._confidence_decay(0.9, 30)
        conf_90 = forecaster._confidence_decay(0.9, 90)
        conf_180 = forecaster._confidence_decay(0.9, 180)
        assert conf_30 > conf_90 > conf_180

    @pytest.mark.asyncio
    async def test_predict_uses_fallback_without_prophet(self):
        forecaster = ProphetForecaster()
        history = make_history(5)  # too few for Prophet
        result = await forecaster.predict(
            current_score=70.0, growth_rate=15.0, history=history, horizon_days=30
        )
        assert "predicted_value" in result
        assert "confidence" in result
        assert "lower_bound" in result
        assert "upper_bound" in result
        assert result["lower_bound"] <= result["predicted_value"] <= result["upper_bound"]


class TestLSTMForecaster:
    def test_ar_fallback(self):
        forecaster = LSTMForecaster()
        result = forecaster._ar_fallback(
            current=65.0,
            growth_rate=10.0,
            series=[60.0, 62.0, 64.0, 65.0, 66.0],
            horizon_days=30,
        )
        assert 0 <= result["predicted_value"] <= 100
        assert "factors" in result

    def test_ar_fallback_empty_series(self):
        forecaster = LSTMForecaster()
        result = forecaster._ar_fallback(
            current=50.0, growth_rate=5.0, series=[], horizon_days=14
        )
        assert result["predicted_value"] >= 0

    @pytest.mark.asyncio
    async def test_predict_short_history_uses_fallback(self):
        forecaster = LSTMForecaster()
        history = make_history(5)
        result = await forecaster.predict(
            current_score=55.0, growth_rate=8.0, history=history, horizon_days=30
        )
        assert "predicted_value" in result
        assert 0 <= result["predicted_value"] <= 100


class TestXGBoostForecaster:
    def test_linear_fallback(self):
        forecaster = XGBoostForecaster()
        result = forecaster._linear_fallback(
            current=70.0,
            growth_rate=20.0,
            series=[65.0, 67.0, 69.0, 71.0, 73.0],
            horizon_days=30,
        )
        assert 0 <= result["predicted_value"] <= 100

    def test_get_features_length(self):
        forecaster = XGBoostForecaster()
        series = [60.0, 62.0, 64.0, 66.0, 68.0, 70.0, 72.0, 74.0]
        features = forecaster._get_features(series)
        assert len(features) == 8  # lag1, lag2, lag3, rmean, rstd, growth, month, quarter

    def test_build_features_returns_pairs(self):
        forecaster = XGBoostForecaster()
        series = [float(i) for i in range(20)]
        X, y = forecaster._build_features(series)
        assert len(X) == len(y)
        assert len(X) > 0

    @pytest.mark.asyncio
    async def test_predict_short_history_fallback(self):
        forecaster = XGBoostForecaster()
        history = make_history(5)
        result = await forecaster.predict(
            current_score=80.0, growth_rate=5.0, history=history, horizon_days=30
        )
        assert "predicted_value" in result
        assert 0 <= result["predicted_value"] <= 100


# ═══════════════════════════════════════════════════════════════
# TREND SERVICE
# ═══════════════════════════════════════════════════════════════

class TestTrendService:

    def test_classify_status_emerging(self):
        from app.services.trend_service import TrendService
        svc = TrendService(None)
        assert svc.classify_status(score=40.0, growth_rate=35.0) == "emerging"

    def test_classify_status_rising(self):
        from app.services.trend_service import TrendService
        svc = TrendService(None)
        assert svc.classify_status(score=65.0, growth_rate=20.0) == "rising"

    def test_classify_status_peak(self):
        from app.services.trend_service import TrendService
        svc = TrendService(None)
        assert svc.classify_status(score=85.0, growth_rate=5.0) == "peak"

    def test_classify_status_declining(self):
        from app.services.trend_service import TrendService
        svc = TrendService(None)
        assert svc.classify_status(score=55.0, growth_rate=-15.0) == "declining"


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

class TestHelpers:

    def test_slugify(self):
        from app.utils.helpers import slugify
        assert slugify("Quiet Luxury Style") == "quiet-luxury-style"
        assert slugify("Butter Yellow!") == "butter-yellow"

    def test_format_large_number(self):
        from app.utils.helpers import format_large_number
        assert format_large_number(1_500_000) == "1.5M"
        assert format_large_number(25_000) == "25.0K"
        assert format_large_number(999) == "999"

    def test_compute_growth_rate(self):
        from app.utils.helpers import compute_growth_rate
        assert compute_growth_rate(110, 100) == pytest.approx(10.0)
        assert compute_growth_rate(100, 0) == 100.0
        assert compute_growth_rate(0, 0) == 0.0

    def test_hex_to_rgb(self):
        from app.utils.helpers import hex_to_rgb
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#C9A96E") == (201, 169, 110)

    def test_rgb_to_hex(self):
        from app.utils.helpers import rgb_to_hex
        assert rgb_to_hex(255, 0, 0) == "#FF0000"

    def test_get_season(self):
        from app.utils.helpers import get_season
        from datetime import date
        assert "Spring" in get_season(date(2025, 4, 1))
        assert "Summer" in get_season(date(2025, 7, 1))
        assert "Fall" in get_season(date(2025, 10, 1))
        assert "Winter" in get_season(date(2025, 12, 1))

    def test_chunk_list(self):
        from app.utils.helpers import chunk_list
        chunks = chunk_list([1, 2, 3, 4, 5], 2)
        assert chunks == [[1, 2], [3, 4], [5]]

    def test_clamp(self):
        from app.utils.helpers import clamp
        assert clamp(150.0, 0, 100) == 100
        assert clamp(-10.0, 0, 100) == 0
        assert clamp(50.0, 0, 100) == 50
