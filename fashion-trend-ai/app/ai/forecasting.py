"""
Agent 4: Forecast Agent
Three ML forecasters:
  - ProphetForecaster   (Meta Prophet — seasonality-aware)
  - LSTMForecaster      (PyTorch LSTM — sequence modelling)
  - XGBoostForecaster   (XGBoost — feature-based regression)

Each exposes an async predict() method returning a standardised result dict.
"""
import asyncio
import math
import random
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
import numpy as np

from app.utils.logger import logger


# ── Base ──────────────────────────────────────────────────────────────────────

class BaseForecaster:
    """Common interface all forecasters implement."""

    async def predict(
        self,
        current_score: float,
        growth_rate: float,
        history: List[Any],   # list of TrendPrediction ORM objects
        horizon_days: int = 30,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def _history_to_series(self, history: List[Any]) -> List[float]:
        """Convert ORM history list to float series sorted oldest-first."""
        sorted_h = sorted(history, key=lambda p: p.prediction_date)
        return [p.predicted_value for p in sorted_h]

    def _confidence_decay(self, base_conf: float, horizon_days: int) -> float:
        """Confidence decays with horizon: longer = less certain."""
        decay = math.exp(-horizon_days / 180)
        return round(max(base_conf * decay, 0.35), 3)


# ── Prophet Forecaster ────────────────────────────────────────────────────────

class ProphetForecaster(BaseForecaster):
    """
    Uses Meta Prophet for time-series forecasting with seasonality.
    Falls back to exponential smoothing if Prophet not installed.
    """

    async def predict(self, current_score, growth_rate, history, horizon_days=30):
        return await asyncio.get_event_loop().run_in_executor(
            None, self._predict_sync, current_score, growth_rate, history, horizon_days
        )

    def _predict_sync(self, current_score, growth_rate, history, horizon_days):
        series = self._history_to_series(history)

        try:
            from prophet import Prophet
            import pandas as pd

            # Build training dataframe
            end = date.today()
            start = end - timedelta(days=len(series))
            dates = [start + timedelta(days=i) for i in range(len(series))]

            if len(series) < 10:
                raise ValueError("Not enough history for Prophet, using fallback")

            df = pd.DataFrame({
                "ds": pd.to_datetime(dates),
                "y": series,
            })
            model = Prophet(
                seasonality_mode="multiplicative",
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.1,
                seasonality_prior_scale=10,
            )
            model.add_seasonality(name="fashion_quarter", period=91.25, fourier_order=5)
            model.fit(df)

            future = model.make_future_dataframe(periods=horizon_days)
            forecast = model.predict(future)
            pred_row = forecast.iloc[-1]
            predicted = float(pred_row["yhat"])
            lower = float(pred_row["yhat_lower"])
            upper = float(pred_row["yhat_upper"])
            predicted = min(max(predicted, 0), 100)

            confidence = self._confidence_decay(0.87, horizon_days)
            factors = {
                "trend_component": float(pred_row.get("trend", 0)),
                "weekly_seasonality": float(pred_row.get("weekly", 0)),
                "yearly_seasonality": float(pred_row.get("yearly", 0)),
                "method": "prophet",
            }
            logger.info(f"[Prophet] Predicted {predicted:.2f} at {horizon_days}d horizon")
            return {
                "predicted_value": round(predicted, 2),
                "confidence": confidence,
                "lower_bound": round(max(lower, 0), 2),
                "upper_bound": round(min(upper, 100), 2),
                "factors": factors,
            }

        except Exception as e:
            logger.warning(f"[ProphetForecaster] Prophet unavailable: {e}. Using ETS fallback.")
            return self._ets_fallback(current_score, growth_rate, series, horizon_days)

    def _ets_fallback(self, current, growth_rate, series, horizon_days):
        """Simple Exponential Triple Smoothing (Holt-Winters)."""
        alpha, beta, gamma = 0.3, 0.1, 0.1
        if len(series) < 3:
            level = current
            trend_comp = growth_rate / 100 * current / 30
        else:
            level = series[-1]
            trend_comp = (series[-1] - series[-2]) if len(series) >= 2 else 0

        for _ in range(horizon_days):
            new_level = alpha * level + (1 - alpha) * (level + trend_comp)
            new_trend = beta * (new_level - level) + (1 - beta) * trend_comp
            level, trend_comp = new_level, new_trend

        predicted = min(max(level, 0), 100)
        confidence = self._confidence_decay(0.75, horizon_days)
        return {
            "predicted_value": round(predicted, 2),
            "confidence": confidence,
            "lower_bound": round(max(predicted * 0.85, 0), 2),
            "upper_bound": round(min(predicted * 1.15, 100), 2),
            "factors": {"method": "ets_fallback", "alpha": alpha, "beta": beta},
        }


# ── LSTM Forecaster ───────────────────────────────────────────────────────────

class LSTMForecaster(BaseForecaster):
    """
    PyTorch LSTM for sequence-based trend prediction.
    Falls back to ARIMA-style differencing when torch unavailable.
    """

    SEQ_LEN = 30  # look-back window

    async def predict(self, current_score, growth_rate, history, horizon_days=30):
        return await asyncio.get_event_loop().run_in_executor(
            None, self._predict_sync, current_score, growth_rate, history, horizon_days
        )

    def _predict_sync(self, current_score, growth_rate, history, horizon_days):
        series = self._history_to_series(history)

        try:
            import torch
            import torch.nn as nn

            if len(series) < self.SEQ_LEN + 5:
                raise ValueError("Insufficient history for LSTM")

            # Normalise
            arr = np.array(series, dtype=np.float32)
            min_v, max_v = arr.min(), arr.max()
            if max_v == min_v:
                raise ValueError("Constant series — LSTM not useful")
            norm = (arr - min_v) / (max_v - min_v)

            # Build sequences
            X, y = [], []
            for i in range(len(norm) - self.SEQ_LEN):
                X.append(norm[i : i + self.SEQ_LEN])
                y.append(norm[i + self.SEQ_LEN])
            X = torch.tensor(X).unsqueeze(-1)  # (batch, seq, 1)
            y = torch.tensor(y).unsqueeze(-1)

            # Simple LSTM
            class TrendLSTM(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.lstm = nn.LSTM(1, 32, num_layers=2, batch_first=True, dropout=0.1)
                    self.fc = nn.Linear(32, 1)

                def forward(self, x):
                    out, _ = self.lstm(x)
                    return self.fc(out[:, -1, :])

            model = TrendLSTM()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
            criterion = nn.MSELoss()

            # Train (fast: 50 epochs)
            model.train()
            for _ in range(50):
                pred = model(X)
                loss = criterion(pred, y)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # Forecast horizon_days ahead iteratively
            model.eval()
            seq = torch.tensor(norm[-self.SEQ_LEN :]).unsqueeze(0).unsqueeze(-1)
            future_vals = []
            with torch.no_grad():
                for _ in range(horizon_days):
                    out = model(seq)
                    val = out.item()
                    future_vals.append(val)
                    new_input = torch.tensor([[[val]]])
                    seq = torch.cat([seq[:, 1:, :], new_input], dim=1)

            # Denormalise
            final_norm = future_vals[-1]
            predicted = float(final_norm * (max_v - min_v) + min_v)
            predicted = min(max(predicted, 0), 100)

            # Uncertainty from variance of last 7 forecasted values
            last7 = [v * (max_v - min_v) + min_v for v in future_vals[-7:]]
            std = float(np.std(last7))
            confidence = self._confidence_decay(0.82, horizon_days)

            return {
                "predicted_value": round(predicted, 2),
                "confidence": confidence,
                "lower_bound": round(max(predicted - 2 * std, 0), 2),
                "upper_bound": round(min(predicted + 2 * std, 100), 2),
                "factors": {
                    "method": "lstm",
                    "seq_len": self.SEQ_LEN,
                    "train_loss": round(loss.item(), 5),
                },
            }

        except Exception as e:
            logger.warning(f"[LSTMForecaster] PyTorch unavailable: {e}. Using AR fallback.")
            return self._ar_fallback(current_score, growth_rate, series, horizon_days)

    def _ar_fallback(self, current, growth_rate, series, horizon_days):
        """Auto-Regressive (order 3) fallback."""
        if len(series) < 3:
            series = [current] * 3
        a1, a2, a3 = 0.5, 0.3, 0.2
        vals = list(series[-3:])
        for _ in range(horizon_days):
            next_v = a1 * vals[-1] + a2 * vals[-2] + a3 * vals[-3]
            next_v = min(max(next_v, 0), 100)
            vals.append(next_v)
        predicted = vals[-1]
        confidence = self._confidence_decay(0.70, horizon_days)
        return {
            "predicted_value": round(predicted, 2),
            "confidence": confidence,
            "lower_bound": round(max(predicted * 0.88, 0), 2),
            "upper_bound": round(min(predicted * 1.12, 100), 2),
            "factors": {"method": "ar3_fallback"},
        }


# ── XGBoost Forecaster ────────────────────────────────────────────────────────

class XGBoostForecaster(BaseForecaster):
    """
    XGBoost regressor using engineered features:
    - Rolling mean/std
    - Growth rate
    - Seasonality (month, quarter)
    - Lag features
    """

    async def predict(self, current_score, growth_rate, history, horizon_days=30):
        return await asyncio.get_event_loop().run_in_executor(
            None, self._predict_sync, current_score, growth_rate, history, horizon_days
        )

    def _predict_sync(self, current_score, growth_rate, series_history, horizon_days):
        series = self._history_to_series(series_history)

        try:
            import xgboost as xgb

            if len(series) < 15:
                raise ValueError("Not enough history for XGBoost")

            # Feature engineering
            X, y = self._build_features(series)
            if len(X) < 5:
                raise ValueError("Too few samples")

            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42,
                verbosity=0,
            )
            model.fit(np.array(X), np.array(y))

            # Build features for next horizon_days steps
            extended = list(series)
            for step in range(horizon_days):
                features = self._get_features(extended)
                pred = float(model.predict(np.array([features]))[0])
                pred = min(max(pred, 0), 100)
                extended.append(pred)

            predicted = extended[-1]
            confidence = self._confidence_decay(0.79, horizon_days)

            # Feature importances as factors
            importances = model.feature_importances_.tolist()
            feature_names = ["lag1", "lag2", "lag3", "rolling_mean", "rolling_std", "growth", "month", "quarter"]
            factors = {
                "method": "xgboost",
                "feature_importance": dict(zip(feature_names[:len(importances)], importances)),
            }

            return {
                "predicted_value": round(predicted, 2),
                "confidence": confidence,
                "lower_bound": round(max(predicted * 0.87, 0), 2),
                "upper_bound": round(min(predicted * 1.13, 100), 2),
                "factors": factors,
            }

        except Exception as e:
            logger.warning(f"[XGBoostForecaster] XGBoost unavailable: {e}. Using regression fallback.")
            return self._linear_fallback(current_score, growth_rate, series, horizon_days)

    def _get_features(self, series: List[float]) -> List[float]:
        n = len(series)
        lag1 = series[-1] if n >= 1 else 0
        lag2 = series[-2] if n >= 2 else lag1
        lag3 = series[-3] if n >= 3 else lag2
        window = series[-7:] if n >= 7 else series
        rolling_mean = np.mean(window)
        rolling_std = np.std(window)
        growth = (lag1 - lag2) / (lag2 + 1e-8)
        today = date.today()
        month = today.month
        quarter = (today.month - 1) // 3 + 1
        return [lag1, lag2, lag3, rolling_mean, rolling_std, growth, month, quarter]

    def _build_features(self, series: List[float]):
        X, y = [], []
        for i in range(max(7, 3), len(series)):
            features = self._get_features(series[:i])
            X.append(features)
            y.append(series[i])
        return X, y

    def _linear_fallback(self, current, growth_rate, series, horizon_days):
        """Least-squares linear regression fallback."""
        if len(series) >= 5:
            x = np.arange(len(series))
            coeffs = np.polyfit(x, series, 1)
            predicted = np.polyval(coeffs, len(series) + horizon_days - 1)
        else:
            monthly_growth = growth_rate / 100
            predicted = current * (1 + monthly_growth) ** (horizon_days / 30)
        predicted = min(max(float(predicted), 0), 100)
        confidence = self._confidence_decay(0.68, horizon_days)
        return {
            "predicted_value": round(predicted, 2),
            "confidence": confidence,
            "lower_bound": round(max(predicted * 0.85, 0), 2),
            "upper_bound": round(min(predicted * 1.15, 100), 2),
            "factors": {"method": "linear_regression_fallback"},
        }
