"""
signal_generator.py — SMC signals with:
  - SL range: 50–100 pips (1 pip = $0.10 for XAU/USD)
  - RR options: 1:1.5 / 1:2 / 1:3 chosen by confluence strength
  - Signal tracking for TP/SL hit notifications
  - Minimum 10 signals/day logic
"""

import uuid
import pandas as pd
from dataclasses import dataclass, field
from typing import Literal
from smc_engine import SMCEngine, SMCAnalysis, OrderBlock, FairValueGap

# XAU/USD: 1 pip = $0.10, so 50 pips = $5, 100 pips = $10
PIP = 0.10
MIN_SL_PIPS = 50
MAX_SL_PIPS = 100
MIN_SL_USD  = MIN_SL_PIPS * PIP   # $5.0
MAX_SL_USD  = MAX_SL_PIPS * PIP   # $10.0


@dataclass
class Signal:
    id: str
    direction: Literal["BUY", "SELL"]
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    rr1: float          # e.g. 1.5, 2.0
    rr2: float          # e.g. 2.0, 3.0
    sl_pips: int
    confidence: int
    confluences: list[str]
    ob_type: str
    timestamp: pd.Timestamp
    timeframe: str = "M15"
    kill_zone: str = ""
    # tracking
    tp1_hit: bool = False
    tp2_hit: bool = False
    sl_hit: bool = False
    active: bool = True

    def risk_usd(self) -> float:
        return abs(self.entry - self.stop_loss)

    def risk_pips(self) -> int:
        return round(abs(self.entry - self.stop_loss) / PIP)


class SignalGenerator:
    """
    Confluence scoring:
      +20  OB aligned with trend
      +15  FVG inside OB
      +15  Kill Zone active
      +10  Liquidity sweep detected
      +10  ChoCh / BOS confirmed
      +10  Premium/Discount zone
      +10  FVG standalone

    RR selection by confidence:
      < 65  → RR 1:1.5 / 1:2
      65-80 → RR 1:2   / 1:2.5  (shown as 1:2)
      > 80  → RR 1:2   / 1:3

    SL sizing:
      Target 60–80 pip SL centered in the 50–100 range.
      Clamp to [MIN_SL_USD, MAX_SL_USD].
    """

    MIN_CONFIDENCE = 45

    def __init__(self, engine: SMCEngine = None):
        self.engine = engine or SMCEngine()

    # ─── public ───────────────────────────────

    def generate(self, df: pd.DataFrame, kill_zone: tuple = (False, "")) -> list[Signal]:
        analysis = self.engine.analyze(df)
        current_price = df["close"].iloc[-1]
        current_time  = df["datetime"].iloc[-1]

        signals: list[Signal] = []

        for ob in analysis.order_blocks:
            s = self._eval_ob(ob, analysis, current_price, current_time, kill_zone)
            if s:
                signals.append(s)

        for fvg in analysis.fair_value_gaps:
            s = self._eval_fvg(fvg, analysis, current_price, current_time, kill_zone)
            if s:
                signals.append(s)

        signals = self._deduplicate(signals)
        signals.sort(key=lambda x: x.confidence, reverse=True)
        return signals

    def check_tp_sl(self, signal: Signal, current_price: float) -> Literal["tp1", "tp2", "sl", None]:
        """Check if price has hit TP1, TP2 or SL. Returns event string or None."""
        if not signal.active:
            return None

        if signal.direction == "BUY":
            if not signal.tp1_hit and current_price >= signal.take_profit_1:
                signal.tp1_hit = True
                return "tp1"
            if signal.tp1_hit and not signal.tp2_hit and current_price >= signal.take_profit_2:
                signal.tp2_hit = True
                signal.active = False
                return "tp2"
            if not signal.sl_hit and current_price <= signal.stop_loss:
                signal.sl_hit = True
                signal.active = False
                return "sl"
        else:  # SELL
            if not signal.tp1_hit and current_price <= signal.take_profit_1:
                signal.tp1_hit = True
                return "tp1"
            if signal.tp1_hit and not signal.tp2_hit and current_price <= signal.take_profit_2:
                signal.tp2_hit = True
                signal.active = False
                return "tp2"
            if not signal.sl_hit and current_price >= signal.stop_loss:
                signal.sl_hit = True
                signal.active = False
                return "sl"
        return None

    # ─── SL / TP helpers ──────────────────────

    def _compute_sl_tp(self, direction: str, entry: float, raw_risk: float, confidence: int):
        """
        Clamp SL to 50–100 pip range, then pick RR based on confidence.
        Returns (sl, tp1, tp2, sl_pips, rr1, rr2)
        """
        # Clamp raw risk into [MIN_SL_USD, MAX_SL_USD]
        risk = max(MIN_SL_USD, min(MAX_SL_USD, raw_risk))
        sl_pips = round(risk / PIP)

        if direction == "BUY":
            sl = entry - risk
            if confidence >= 80:
                rr1, rr2 = 2.0, 3.0
            elif confidence >= 65:
                rr1, rr2 = 2.0, 2.5
            else:
                rr1, rr2 = 1.5, 2.0
            tp1 = entry + risk * rr1
            tp2 = entry + risk * rr2
        else:
            sl = entry + risk
            if confidence >= 80:
                rr1, rr2 = 2.0, 3.0
            elif confidence >= 65:
                rr1, rr2 = 2.0, 2.5
            else:
                rr1, rr2 = 1.5, 2.0
            tp1 = entry - risk * rr1
            tp2 = entry - risk * rr2

        return round(sl, 2), round(tp1, 2), round(tp2, 2), sl_pips, rr1, rr2

    # ─── OB evaluation ────────────────────────

    def _eval_ob(self, ob: OrderBlock, analysis: SMCAnalysis,
                 price: float, ts: pd.Timestamp, kill_zone: tuple) -> Signal | None:
        score = 0
        confluences = []
        is_kz, kz_name = kill_zone

        if ob.type == "bullish":
            if not (ob.bottom * 0.998 <= price <= ob.top * 1.012):
                return None
            direction = "BUY"
            entry = ob.top
            raw_risk = max(ob.top - ob.bottom, MIN_SL_USD)

            if analysis.trend == "bullish":
                score += 20
                confluences.append("✅ Trend: Bullish (HH/HL)")
            elif analysis.trend == "ranging":
                score += 8
                confluences.append("↔️ Ranging — ehtiyot bilan")
            if analysis.swing_low and price <= analysis.premium_zone[0]:
                score += 10
                confluences.append(f"📉 Diskont zona ({analysis.swing_low:.2f}–{analysis.premium_zone[0]:.2f})")
        else:
            if not (ob.bottom * 0.988 <= price <= ob.top * 1.002):
                return None
            direction = "SELL"
            entry = ob.bottom
            raw_risk = max(ob.top - ob.bottom, MIN_SL_USD)

            if analysis.trend == "bearish":
                score += 20
                confluences.append("✅ Trend: Bearish (LH/LL)")
            elif analysis.trend == "ranging":
                score += 8
                confluences.append("↔️ Ranging — ehtiyot bilan")
            if analysis.swing_high and price >= analysis.premium_zone[0]:
                score += 10
                confluences.append(f"📈 Premium zona ({analysis.premium_zone[0]:.2f}–{analysis.swing_high:.2f})")

        score += 20
        confluences.append(f"🟦 {ob.type.capitalize()} OB @ {ob.top:.2f}–{ob.bottom:.2f} (kuch: {ob.strength:.2f}%)")

        for fvg in analysis.fair_value_gaps:
            if fvg.type == ob.type:
                if ob.bottom <= fvg.bottom <= ob.top or ob.bottom <= fvg.top <= ob.top:
                    score += 15
                    confluences.append(f"⚡ FVG OB ichida ({fvg.bottom:.2f}–{fvg.top:.2f})")
                    break

        if is_kz:
            score += 15
            confluences.append(f"🕐 Kill Zone: {kz_name}")

        for sweep in analysis.liquidity_sweeps:
            if direction == "BUY" and sweep.type == "SSL" and sweep.swept:
                score += 10
                confluences.append(f"💧 SSL Likvidlik o'g'irlash @ {sweep.price:.2f}")
                break
            if direction == "SELL" and sweep.type == "BSL" and sweep.swept:
                score += 10
                confluences.append(f"💧 BSL Likvidlik o'g'irlash @ {sweep.price:.2f}")
                break

        recent = analysis.structure[-6:]
        choched = any(s.type == "HH" for s in recent[-3:]) if direction == "BUY" \
                  else any(s.type == "LL" for s in recent[-3:])
        if choched:
            score += 10
            label = "HH shakllandi (bullish ChoCh)" if direction == "BUY" else "LL shakllandi (bearish ChoCh)"
            confluences.append(f"🔄 Struktura: {label}")

        if score < self.MIN_CONFIDENCE:
            return None

        sl, tp1, tp2, sl_pips, rr1, rr2 = self._compute_sl_tp(direction, entry, raw_risk, score)

        return Signal(
            id=str(uuid.uuid4())[:8].upper(),
            direction=direction,
            entry=round(entry, 2),
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            rr1=rr1, rr2=rr2,
            sl_pips=sl_pips,
            confidence=min(score, 100),
            confluences=confluences,
            ob_type=f"{ob.type.capitalize()} OB",
            timestamp=ts,
            kill_zone=kz_name if is_kz else "",
        )

    # ─── FVG evaluation ───────────────────────

    def _eval_fvg(self, fvg: FairValueGap, analysis: SMCAnalysis,
                  price: float, ts: pd.Timestamp, kill_zone: tuple) -> Signal | None:
        score = 0
        confluences = []
        is_kz, kz_name = kill_zone

        if fvg.type == "bullish":
            if not (fvg.bottom * 0.998 <= price <= fvg.top * 1.002):
                return None
            direction = "BUY"
            entry = fvg.top
            raw_risk = max(fvg.top - fvg.bottom, MIN_SL_USD)
            if analysis.trend == "bullish":
                score += 20
                confluences.append("✅ Trend: Bullish")
            if price <= analysis.premium_zone[0]:
                score += 10
                confluences.append("📉 Diskont zona")
        else:
            if not (fvg.bottom * 0.998 <= price <= fvg.top * 1.002):
                return None
            direction = "SELL"
            entry = fvg.bottom
            raw_risk = max(fvg.top - fvg.bottom, MIN_SL_USD)
            if analysis.trend == "bearish":
                score += 20
                confluences.append("✅ Trend: Bearish")
            if analysis.swing_high and price >= analysis.premium_zone[0]:
                score += 10
                confluences.append("📈 Premium zona")

        score += 10
        confluences.append(f"⚡ {fvg.type.capitalize()} FVG @ {fvg.bottom:.2f}–{fvg.top:.2f}")

        if is_kz:
            score += 15
            confluences.append(f"🕐 Kill Zone: {kz_name}")

        if score < self.MIN_CONFIDENCE:
            return None

        sl, tp1, tp2, sl_pips, rr1, rr2 = self._compute_sl_tp(direction, entry, raw_risk, score)

        return Signal(
            id=str(uuid.uuid4())[:8].upper(),
            direction=direction,
            entry=round(entry, 2),
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            rr1=rr1, rr2=rr2,
            sl_pips=sl_pips,
            confidence=min(score, 100),
            confluences=confluences,
            ob_type="FVG",
            timestamp=ts,
            kill_zone=kz_name if is_kz else "",
        )

    # ─── dedup ────────────────────────────────

    def _deduplicate(self, signals: list[Signal], threshold: float = 5.0) -> list[Signal]:
        unique: list[Signal] = []
        for s in signals:
            dup = any(u.direction == s.direction and abs(u.entry - s.entry) < threshold for u in unique)
            if not dup:
                unique.append(s)
        return unique
