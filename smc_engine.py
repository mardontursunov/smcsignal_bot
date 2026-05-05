"""
smc_engine.py — SMC / ICT concept detection engine for XAU/USD M15
Detects:
  - Market Structure: BOS (Break of Structure) & ChoCh (Change of Character)
  - Order Blocks (Bullish / Bearish)
  - Fair Value Gaps (Bullish / Bearish FVG)
  - Liquidity Sweeps (SSL / BSL)
  - Premium / Discount zones (50% Fib of swing)
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Literal


# ─────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────

@dataclass
class OrderBlock:
    type: Literal["bullish", "bearish"]
    top: float
    bottom: float
    index: int
    timestamp: pd.Timestamp
    mitigated: bool = False
    strength: float = 0.0          # move away from OB in % terms


@dataclass
class FairValueGap:
    type: Literal["bullish", "bearish"]
    top: float
    bottom: float
    index: int
    timestamp: pd.Timestamp
    filled: bool = False


@dataclass
class StructurePoint:
    type: Literal["HH", "HL", "LH", "LL"]
    price: float
    index: int
    timestamp: pd.Timestamp


@dataclass
class LiquiditySweep:
    type: Literal["SSL", "BSL"]        # Sell-side / Buy-side liquidity
    price: float
    index: int
    timestamp: pd.Timestamp
    swept: bool = False


@dataclass
class SMCAnalysis:
    order_blocks: list[OrderBlock] = field(default_factory=list)
    fair_value_gaps: list[FairValueGap] = field(default_factory=list)
    structure: list[StructurePoint] = field(default_factory=list)
    liquidity_sweeps: list[LiquiditySweep] = field(default_factory=list)
    trend: Literal["bullish", "bearish", "ranging"] = "ranging"
    discount_zone: tuple[float, float] = (0.0, 0.0)   # (low, 50%)
    premium_zone: tuple[float, float] = (0.0, 0.0)    # (50%, high)
    swing_high: float = 0.0
    swing_low: float = 0.0


# ─────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────

class SMCEngine:
    def __init__(self, swing_lookback: int = 5, ob_lookback: int = 50, fvg_min_gap_pct: float = 0.05):
        """
        swing_lookback  : candles left/right to confirm swing high/low
        ob_lookback     : how many candles back to search for OBs
        fvg_min_gap_pct : minimum FVG gap as % of price (filters noise)
        """
        self.swing_lookback = swing_lookback
        self.ob_lookback = ob_lookback
        self.fvg_min_gap_pct = fvg_min_gap_pct

    # ── public ────────────────────────────────

    def analyze(self, df: pd.DataFrame) -> SMCAnalysis:
        """Full SMC analysis on a candle DataFrame."""
        result = SMCAnalysis()

        swing_highs, swing_lows = self._find_swings(df)
        result.structure = self._classify_structure(df, swing_highs, swing_lows)
        result.trend = self._determine_trend(result.structure)

        if swing_highs and swing_lows:
            sh = df["high"].iloc[swing_highs[-1]]
            sl = df["low"].iloc[swing_lows[-1]]
            mid = (sh + sl) / 2
            result.swing_high = sh
            result.swing_low = sl
            result.discount_zone = (sl, mid)
            result.premium_zone = (mid, sh)

        result.order_blocks = self._find_order_blocks(df, swing_highs, swing_lows)
        result.fair_value_gaps = self._find_fvgs(df)
        result.liquidity_sweeps = self._find_liquidity_sweeps(df, swing_highs, swing_lows)

        return result

    # ── swing detection ───────────────────────

    def _find_swings(self, df: pd.DataFrame) -> tuple[list[int], list[int]]:
        n = len(df)
        k = self.swing_lookback
        highs, lows = [], []

        for i in range(k, n - k):
            window_h = df["high"].iloc[i - k: i + k + 1]
            if df["high"].iloc[i] == window_h.max():
                highs.append(i)

            window_l = df["low"].iloc[i - k: i + k + 1]
            if df["low"].iloc[i] == window_l.min():
                lows.append(i)

        return highs, lows

    # ── structure classification ──────────────

    def _classify_structure(self, df, swing_highs, swing_lows) -> list[StructurePoint]:
        points: list[StructurePoint] = []

        prev_high = prev_low = None
        for idx in sorted(swing_highs + swing_lows):
            if idx in swing_highs:
                price = df["high"].iloc[idx]
                if prev_high is None:
                    stype = "HH"
                else:
                    stype = "HH" if price > prev_high else "LH"
                prev_high = price
            else:
                price = df["low"].iloc[idx]
                if prev_low is None:
                    stype = "HL"
                else:
                    stype = "HL" if price > prev_low else "LL"
                prev_low = price

            points.append(StructurePoint(
                type=stype,
                price=price,
                index=idx,
                timestamp=df["datetime"].iloc[idx]
            ))

        return points

    def _determine_trend(self, structure: list[StructurePoint]) -> Literal["bullish", "bearish", "ranging"]:
        if len(structure) < 4:
            return "ranging"
        recent = structure[-6:]
        hh = sum(1 for s in recent if s.type == "HH")
        hl = sum(1 for s in recent if s.type == "HL")
        lh = sum(1 for s in recent if s.type == "LH")
        ll = sum(1 for s in recent if s.type == "LL")

        if hh + hl > lh + ll + 1:
            return "bullish"
        if lh + ll > hh + hl + 1:
            return "bearish"
        return "ranging"

    # ── order blocks ──────────────────────────

    def _find_order_blocks(self, df, swing_highs, swing_lows) -> list[OrderBlock]:
        obs: list[OrderBlock] = []
        n = len(df)
        start = max(0, n - self.ob_lookback)

        # Bearish OB: last bullish candle before a bearish displacement
        for i in range(start + 1, n - 1):
            # Bearish OB: bullish candle followed by strong bearish move
            if (df["close"].iloc[i] > df["open"].iloc[i] and          # current candle bullish
                    df["close"].iloc[i + 1] < df["open"].iloc[i + 1] and  # next candle bearish
                    df["open"].iloc[i + 1] < df["low"].iloc[i]):           # breaks below body
                strength = (df["open"].iloc[i] - df["close"].iloc[i + 1]) / df["close"].iloc[i] * 100
                ob = OrderBlock(
                    type="bearish",
                    top=df["high"].iloc[i],
                    bottom=df["open"].iloc[i],
                    index=i,
                    timestamp=df["datetime"].iloc[i],
                    strength=round(strength, 3)
                )
                # Check if mitigated (price came back to OB zone)
                future_highs = df["high"].iloc[i + 2:]
                ob.mitigated = bool((future_highs >= ob.bottom).any())
                obs.append(ob)

            # Bullish OB: bearish candle followed by strong bullish move
            if (df["close"].iloc[i] < df["open"].iloc[i] and           # current bearish
                    df["close"].iloc[i + 1] > df["open"].iloc[i + 1] and   # next bullish
                    df["open"].iloc[i + 1] > df["high"].iloc[i]):           # breaks above body
                strength = (df["close"].iloc[i + 1] - df["open"].iloc[i]) / df["open"].iloc[i] * 100
                ob = OrderBlock(
                    type="bullish",
                    top=df["open"].iloc[i],
                    bottom=df["low"].iloc[i],
                    index=i,
                    timestamp=df["datetime"].iloc[i],
                    strength=round(strength, 3)
                )
                future_lows = df["low"].iloc[i + 2:]
                ob.mitigated = bool((future_lows <= ob.top).any())
                obs.append(ob)

        # Return only unmitigated OBs, strongest first
        unmitigated = [o for o in obs if not o.mitigated]
        unmitigated.sort(key=lambda x: x.strength, reverse=True)
        return unmitigated[-10:]   # cap at 10 most recent & strongest

    # ── fair value gaps ───────────────────────

    def _find_fvgs(self, df: pd.DataFrame) -> list[FairValueGap]:
        fvgs: list[FairValueGap] = []
        n = len(df)
        min_gap = df["close"].mean() * self.fvg_min_gap_pct / 100

        for i in range(1, n - 1):
            # Bullish FVG: gap between candle[i-1] high and candle[i+1] low
            gap_bottom = df["high"].iloc[i - 1]
            gap_top = df["low"].iloc[i + 1]
            if gap_top > gap_bottom + min_gap:
                fvg = FairValueGap(
                    type="bullish",
                    top=gap_top,
                    bottom=gap_bottom,
                    index=i,
                    timestamp=df["datetime"].iloc[i]
                )
                # Check if filled
                future_lows = df["low"].iloc[i + 2:]
                fvg.filled = bool((future_lows <= gap_bottom).any())
                fvgs.append(fvg)

            # Bearish FVG: gap between candle[i-1] low and candle[i+1] high
            gap_top2 = df["low"].iloc[i - 1]
            gap_bottom2 = df["high"].iloc[i + 1]
            if gap_top2 > gap_bottom2 + min_gap:
                fvg = FairValueGap(
                    type="bearish",
                    top=gap_top2,
                    bottom=gap_bottom2,
                    index=i,
                    timestamp=df["datetime"].iloc[i]
                )
                future_highs = df["high"].iloc[i + 2:]
                fvg.filled = bool((future_highs >= gap_top2).any())
                fvgs.append(fvg)

        unfilled = [f for f in fvgs if not f.filled]
        return unfilled[-10:]

    # ── liquidity sweeps ──────────────────────

    def _find_liquidity_sweeps(self, df, swing_highs, swing_lows) -> list[LiquiditySweep]:
        sweeps: list[LiquiditySweep] = []
        n = len(df)

        # Equal highs = buy-side liquidity (BSL)
        for i in range(len(swing_highs) - 1):
            idx_a = swing_highs[i]
            idx_b = swing_highs[i + 1]
            price_a = df["high"].iloc[idx_a]
            price_b = df["high"].iloc[idx_b]

            # Nearly equal highs (within 0.1%)
            if abs(price_a - price_b) / price_a < 0.001:
                # Check if a future candle swept above
                future = df.iloc[idx_b + 1:]
                swept = bool((future["high"] > max(price_a, price_b)).any())
                sweeps.append(LiquiditySweep(
                    type="BSL",
                    price=max(price_a, price_b),
                    index=idx_b,
                    timestamp=df["datetime"].iloc[idx_b],
                    swept=swept
                ))

        # Equal lows = sell-side liquidity (SSL)
        for i in range(len(swing_lows) - 1):
            idx_a = swing_lows[i]
            idx_b = swing_lows[i + 1]
            price_a = df["low"].iloc[idx_a]
            price_b = df["low"].iloc[idx_b]

            if abs(price_a - price_b) / price_a < 0.001:
                future = df.iloc[idx_b + 1:]
                swept = bool((future["low"] < min(price_a, price_b)).any())
                sweeps.append(LiquiditySweep(
                    type="SSL",
                    price=min(price_a, price_b),
                    index=idx_b,
                    timestamp=df["datetime"].iloc[idx_b],
                    swept=swept
                ))

        return sweeps
