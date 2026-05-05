"""
market_data.py — Fetches XAU/USD OHLCV candles from Twelve Data (free tier)
Free tier: 800 API credits/day, 8 requests/minute
"""

import requests
import pandas as pd
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)


class MarketData:
    BASE_URL = "https://api.twelvedata.com"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_candles(self, symbol: str = "XAU/USD", interval: str = "15min", outputsize: int = 200) -> pd.DataFrame:
        """
        Fetch OHLCV candles. Returns a DataFrame sorted oldest → newest.
        """
        url = f"{self.BASE_URL}/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key,
            "format": "JSON",
            "timezone": "UTC",
        }

        for attempt in range(3):
            try:
                resp = requests.get(url, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                if data.get("status") == "error":
                    raise ValueError(f"API error: {data.get('message')}")

                values = data.get("values", [])
                if not values:
                    raise ValueError("No candle data returned")

                df = pd.DataFrame(values)
                df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
                df = df.rename(columns={
                    "open": "open", "high": "high",
                    "low": "low", "close": "close", "volume": "volume"
                })
                for col in ["open", "high", "low", "close"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                if "volume" in df.columns:
                    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

                df = df.sort_values("datetime").reset_index(drop=True)
                logger.info(f"Fetched {len(df)} candles for {symbol} [{interval}]")
                return df

            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(5)

        raise RuntimeError("Failed to fetch market data after 3 attempts")

    def is_kill_zone(self) -> tuple[bool, str]:
        """
        Returns (is_in_kill_zone, zone_name).
        Kill zones (UTC):
          - London Open: 07:00–10:00 UTC
          - New York Open: 12:00–15:00 UTC
          - London Close: 15:00–16:00 UTC
        """
        now_hour = datetime.now(timezone.utc).hour
        now_minute = datetime.now(timezone.utc).minute
        now_total = now_hour * 60 + now_minute

        zones = [
            (7*60,  10*60, "🇬🇧 London Open"),
            (12*60, 15*60, "🇺🇸 New York Open"),
            (15*60, 16*60, "🔒 London Close"),
        ]
        for start, end, name in zones:
            if start <= now_total < end:
                return True, name
        return False, ""
