"""
signal_generator.py
Combines anomaly states into trading signals.

(Anomali durumlarını birleştirerek trading sinyalleri üretir.)

The core "alpha" logic: when multiple indices align in cold/bullish
or warm/bearish direction, confidence increases.
What the Code Does
Reads Weather Data: It takes climate data like NAO, AO, and El Niño from an external detector.
Calculates a Score: It translates these complex climate states into simple mathematical numbers.
Gives Trading Advice: It outputs a directional trading signal like "LONG POWER" or "SHORT POWER".
Measures Confidence: It calculates a specific confidence percentage for the generated signal.
Explains the Reason: It automatically creates a checklist of supporting reasons for the trader.
Highlights Risks: It lists major threat factors that could break the trading signal.
How the Code Works
Step 1: The function generate_signal starts by collecting all current weather data.
Step 2: The private function _vote checks how severe each weather pattern is.
Step 3: Cold and disrupted weather patterns receive positive points like +1 or +2.
Step 4: Warm and windy weather patterns receive negative points like -1 or -2.
Step 5: The engine sums all points together to calculate a total_score.
Step 6: If the total score is high and positive, it triggers a strong buy signal.
Step 7: If the total score is low and negative, it triggers a strong sell signal.
Step 8: Higher total scores automatically increase the confidence percentage up to 95%.
Step 9: Finally, a TradingSignal object is returned to display on a live trading dashboard.

Example:
"If only the NAO index indicates cold weather, the score becomes +2.
The system then gives a 71% confidence level (calculated as 65 + 2 * 3), 
signaling: 'Yes, there could be an upward trend, but I am not entirely certain.'

""However, if the NAO, AO, and La Niña all point to cold weather at the same time, the score jumps to +5 or +6. 
Recognizing that all indicators align in the same direction, 
the system signals: 'Everything is pointing toward the same outcome, this is a great opportunity!' 
and pushes the confidence score to its ceiling limit of 95%."
"""

from __future__ import annotations

from dataclasses import dataclass

from anomaly_detector import IndexState, detect_all


# ─────────────────────────────────────────────────────────────────
# Trading Signal dataclass
# ─────────────────────────────────────────────────────────────────

@dataclass
class TradingSignal:
    """Generated trading signal with rationale.

    (Üretilen trading sinyali ve gerekçesi.)
    """
    direction: str  # "LONG POWER" | "SHORT POWER" | "NEUTRAL"
    strength: str  # "STRONG" | "MODERATE" | "WEAK" | "NONE"
    confidence: int  # 0–100
    horizon: str  # e.g. "2-4 weeks"
    rationale: list[str]  # supporting reasons
    risk_factors: list[str]  # things that could invalidate signal
    color: str

    @property
    def headline(self) -> str:
        """One-line summary for dashboard. (Dashboard için tek satır özet.)"""
        if self.direction == "NEUTRAL":
            return "🔵 NEUTRAL — No high-conviction signal"
        emoji = "🟢" if self.direction.startswith("SHORT") else "🔴"
        return f"{emoji} {self.strength} {self.direction} — {self.confidence}% confidence"


# ─────────────────────────────────────────────────────────────────
# Voting logic
# ─────────────────────────────────────────────────────────────────

def _vote(state: IndexState) -> int:
    """Convert index state to a directional vote.

    Returns:
        +2 = strong bullish for power (cold/disrupted)
        +1 = mild bullish
         0 = neutral
        -1 = mild bearish
        -2 = strong bearish (warm/windy)

    (İndeks durumunu yönsel oya çevirir. Pozitif = power için bullish.)
    """
    if state.severity == "extreme":
        if "NAO-" in state.regime or "AO-" in state.regime or "La Niña" in state.regime:
            return +2
        if "NAO+" in state.regime or "AO+" in state.regime or "El Niño" in state.regime:
            return -2

    if state.severity == "strong":
        if "NAO-" in state.regime or "AO-" in state.regime or "La Niña" in state.regime:
            return +1
        if "NAO+" in state.regime or "AO+" in state.regime or "El Niño" in state.regime:
            return -1

    if state.severity == "moderate":
        if "NAO-" in state.regime or "AO-" in state.regime or "La Niña" in state.regime:
            return +1
        if "NAO+" in state.regime or "AO+" in state.regime or "El Niño" in state.regime:
            return -1

    return 0


# ─────────────────────────────────────────────────────────────────
# Main signal generation
# ─────────────────────────────────────────────────────────────────

def generate_signal(states: dict[str, IndexState] | None = None) -> TradingSignal:
    """Generate a trading signal from current anomaly states.

    (Mevcut anomali durumlarından trading sinyali üretir.)
    """
    if states is None:
        states = detect_all()

    if not states:
        return TradingSignal(
            direction="NEUTRAL",
            strength="NONE",
            confidence=0,
            horizon="N/A",
            rationale=["No data available — run data_fetcher first"],
            risk_factors=[],
            color="#6B7280",
        )

    # Collect votes
    votes = {name: _vote(state) for name, state in states.items()}
    total_score = sum(votes.values())
    rationale = []
    risk_factors = []

    # Build rationale (Gerekçe oluştur)
    for name, state in states.items():
    # =================================================================
    # FUTURE WORK: MARKET EXPECTATION INTEGRATION (PHASE 2)
    # =================================================================
    # PURPOSE: To fulfill the core thesis of calculating the "divergence"
    # between atmospheric reality (weather_score) and market pricing.
    # By ingesting public data (EIA, AGSI+, ENTSO-E, yfinance), the engine
    # will penalize priced-in consensus and amplify true alpha signals.
    #
    # @dataclass
    # class MarketExpectationContext:
    #     storage_deviation_vs_5y: float = 0.0  # e.g., AGSI+ gas storage buffer %
    #     front_month_price_trend: str = "FLAT"  # e.g., yfinance front-month futures trend
    #     market_sentiment: str = "NEUTRAL"     # "PRICED_FOR_COLD" | "PRICED_FOR_WARM"
    #
    # # Step 1: Fetch live baseline from public endpoints
    # market_context = _fetch_public_market_data()
    #
    # # Step 2: Calculate Divergence and Adjust Signal Metrics
    # # Case A: Atmosphere is bullish (cold), but market already priced it in.
    # if total_score > 0 and market_context.market_sentiment == "PRICED_FOR_COLD":
    #     confidence -= 15  # Alpha decays because the market already expects the cold.
    #     rationale.append("Warning: Atmospheric cold is heavily priced-in by the market.")
    #
    # # Case B: True Alpha Divergence (Atmosphere is cold, but market prices warm/flat)
    # elif total_score > 0 and market_context.market_sentiment == "PRICED_FOR_WARM":
    #     confidence = min(confidence + 10, 98)  # High conviction alpha expansion.
    #     rationale.append("ALPHA DIVERGENCE: Market expects warm/neutral, but atmospheric reality is COLD.")
    # =================================================================

        
        if state.severity != "neutral":
            rationale.append(f"{state.name}: {state.regime} ({state.current_value:+.2f}) → {state.market_impact}")
        else:
            risk_factors.append(f"{state.name} is neutral — no confirmation")

    # Determine direction & strength (Yön ve güç belirle)
    if total_score >= 4:
        direction = "LONG POWER"
        strength = "STRONG"
        confidence = min(85 + total_score * 2, 95)
        horizon = "2-4 weeks"
        color = "#DC2626"
    elif total_score >= 2:
        direction = "LONG POWER"
        strength = "MODERATE"
        confidence = 65 + total_score * 3
        horizon = "2-6 weeks"
        color = "#F87171"
    elif total_score >= 1:
        direction = "LONG POWER"
        strength = "WEAK"
        confidence = 55
        horizon = "Watch closely"
        color = "#FCA5A5"
    elif total_score <= -4:
        direction = "SHORT POWER"
        strength = "STRONG"
        confidence = min(85 + abs(total_score) * 2, 95)
        horizon = "2-4 weeks"
        color = "#10B981"
    elif total_score <= -2:
        direction = "SHORT POWER"
        strength = "MODERATE"
        confidence = 65 + abs(total_score) * 3
        horizon = "2-6 weeks"
        color = "#34D399"
    elif total_score <= -1:
        direction = "SHORT POWER"
        strength = "WEAK"
        confidence = 55
        horizon = "Watch closely"
        color = "#6EE7B7"
    else:
        direction = "NEUTRAL"
        strength = "NONE"
        confidence = 50
        horizon = "N/A"
        color = "#6B7280"
        if not rationale:
            rationale.append("All indices in neutral regime — market base case applies")

    # Always add risk warning (Risk uyarısı her zaman ekle)
    if direction != "NEUTRAL":
        risk_factors.append("Cross-check with ECMWF ensemble before sizing position")
        risk_factors.append("Monitor for regime shifts daily — climate signals can flip")

    return TradingSignal(
        direction=direction,
        strength=strength,
        confidence=confidence,
        horizon=horizon,
        rationale=rationale,
        risk_factors=risk_factors,
        color=color,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("📡 ALPHA SCANNER — Signal Generation")
    print("=" * 60)
    print()

    signal = generate_signal()

    print(f"  {signal.headline}")
    print(f"  Horizon: {signal.horizon}")
    print()
    print("  📋 Rationale:")
    for r in signal.rationale:
        print(f"     • {r}")
    print()
    if signal.risk_factors:
        print("  ⚠️  Risk Factors:")
        for r in signal.risk_factors:
            print(f"     • {r}")
    print()
