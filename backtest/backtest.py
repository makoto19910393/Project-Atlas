#!/usr/bin/env python3
"""Deterministic bar-by-bar reference backtest for the Project Atlas rules."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class Bar:
    time: datetime
    open: float
    high: float
    low: float
    close: float


@dataclass
class Position:
    side: int
    entry: float
    stop: float
    target: float
    quantity: float
    risk: float
    entry_cost: float


def ema(values: list[float], period: int) -> list[float]:
    result = [math.nan] * len(values)
    if len(values) < period:
        return result
    result[period - 1] = sum(values[:period]) / period
    alpha = 2.0 / (period + 1.0)
    for index in range(period, len(values)):
        result[index] = alpha * values[index] + (1.0 - alpha) * result[index - 1]
    return result


def atr(bars: list[Bar], period: int) -> list[float]:
    ranges = [bars[0].high - bars[0].low]
    for previous, current in zip(bars, bars[1:]):
        ranges.append(max(current.high - current.low,
                          abs(current.high - previous.close),
                          abs(current.low - previous.close)))
    result = [math.nan] * len(bars)
    if len(bars) < period:
        return result
    result[period - 1] = sum(ranges[:period]) / period
    for index in range(period, len(bars)):
        result[index] = ((period - 1) * result[index - 1] + ranges[index]) / period
    return result


def synthetic_bars(count: int = 3000, seed: int = 26072026,
                   interval_minutes: int = 15,regime_bars: int = 1000) -> list[Bar]:
    """Repeatable regime-changing data for execution-path validation only."""
    randomizer = random.Random(seed)
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    price = 42_000.0
    bars = []
    for index in range(count):
        regime = (index // regime_bars) % 4
        drift = (18.0, -14.0, 3.0, -2.0)[regime]
        change = drift + randomizer.gauss(0.0, 180.0)
        opening = price
        closing = max(1_000.0, opening + change)
        excursion = abs(randomizer.gauss(90.0, 55.0))
        high = max(opening, closing) + excursion
        low = min(opening, closing) - excursion
        bars.append(Bar(timestamp, opening, high, low, closing))
        timestamp += timedelta(minutes=interval_minutes)
        price = closing
    return bars


def load_csv(path: Path) -> list[Bar]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = csv.DictReader(source)
        return [Bar(datetime.fromisoformat(row["time"].replace("Z", "+00:00")),
                    float(row["open"]), float(row["high"]),
                    float(row["low"]), float(row["close"])) for row in rows]


def run(bars: list[Bar], initial_equity: float = 50_000.0,
        fast_period: int = 30, slow_period: int = 100, atr_period: int = 14,
        stop_atr: float = 3.0, target_atr: float = 6.0,
        risk_percent: float = 2.5, strategy: str = "donchian",
        breakout_period: int = 10, cost_bps_per_side: float = 5.0,
        win_risk_multiplier: float = 1.0, loss_risk_multiplier: float = 0.7,
        maximum_risk_percent: float | None = None,
        trend_ema_period: int = 200) -> dict[str, object]:
    warmup = (max(fast_period, slow_period, atr_period) if strategy == "ema"
              else max(breakout_period, atr_period, trend_ema_period))
    if strategy not in {"ema", "donchian"}:
        raise ValueError("unknown strategy")
    if len(bars) <= warmup + 1:
        raise ValueError("not enough bars")
    closes = [bar.close for bar in bars]
    fast = ema(closes, fast_period) if strategy == "ema" else []
    slow = ema(closes, slow_period) if strategy == "ema" else []
    trend = ema(closes, trend_ema_period) if trend_ema_period > 0 else []
    ranges = atr(bars, atr_period)
    equity = peak = initial_equity
    max_drawdown = 0.0
    position = None
    profits: list[float] = []
    consecutive_wins = consecutive_losses = 0

    # A signal confirmed at bar i-1 is entered at bar i open, matching EA new-bar execution.
    for index in range(warmup + 1, len(bars)):
        bar = bars[index]
        if position is not None:
            exit_price = None
            if position.side == 1:
                # Conservative rule when both levels occur in one bar: stop is evaluated first.
                if bar.low <= position.stop:
                    exit_price = position.stop
                elif bar.high >= position.target:
                    exit_price = position.target
            else:
                if bar.high >= position.stop:
                    exit_price = position.stop
                elif bar.low <= position.target:
                    exit_price = position.target
            if exit_price is not None:
                exit_cost=exit_price*position.quantity*cost_bps_per_side/10_000.0
                profit = (position.side * (exit_price - position.entry) * position.quantity
                          -position.entry_cost-exit_cost)
                equity += position.side*(exit_price-position.entry)*position.quantity-exit_cost
                profits.append(profit)
                if profit > 0.0:
                    consecutive_wins += 1
                    consecutive_losses = 0
                else:
                    consecutive_losses += 1
                    consecutive_wins = 0
                peak = max(peak, equity)
                max_drawdown = max(max_drawdown, (peak - equity) / peak * 100.0)
                position = None

        if position is not None:
            continue
        previous, older = index - 1, index - 2
        signal = 0
        if strategy == "ema":
            if fast[older] <= slow[older] and fast[previous] > slow[previous]:
                signal = 1
            elif fast[older] >= slow[older] and fast[previous] < slow[previous]:
                signal = -1
        else:
            channel = bars[previous - breakout_period:previous]
            if bars[previous].close > max(item.high for item in channel):
                signal = 1
            elif bars[previous].close < min(item.low for item in channel):
                signal = -1
            if trend_ema_period>0 and ((signal==1 and bars[previous].close<=trend[previous]) or
                                      (signal==-1 and bars[previous].close>=trend[previous])):
                signal=0
        distance = ranges[previous] * stop_atr
        if signal and math.isfinite(distance) and distance > 0.0:
            effective_risk = (risk_percent * win_risk_multiplier ** consecutive_wins
                              * loss_risk_multiplier ** consecutive_losses)
            if maximum_risk_percent is not None:
                effective_risk = min(effective_risk, maximum_risk_percent)
            risk = equity * effective_risk / 100.0
            stop_price=bar.open-signal*distance
            estimated_cost_per_unit=(bar.open+stop_price)*cost_bps_per_side/10_000.0
            quantity = risk / (distance+estimated_cost_per_unit)
            entry_cost=bar.open*quantity*cost_bps_per_side/10_000.0
            equity-=entry_cost
            position = Position(signal, bar.open, bar.open - signal * distance,
                                bar.open + signal * ranges[previous] * target_atr,
                                quantity, risk, entry_cost)

    if position is not None:
        exit_cost=bars[-1].close*position.quantity*cost_bps_per_side/10_000.0
        profit = (position.side * (bars[-1].close-position.entry)*position.quantity
                  -position.entry_cost-exit_cost)
        equity += position.side*(bars[-1].close-position.entry)*position.quantity-exit_cost
        profits.append(profit)
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak * 100.0)

    wins = [profit for profit in profits if profit > 0.0]
    losses = [profit for profit in profits if profit < 0.0]
    gross_profit, gross_loss = sum(wins), -sum(losses)
    return {
        "bars": len(bars),
        "from": bars[0].time.isoformat(),
        "to": bars[-1].time.isoformat(),
        "initial_equity": round(initial_equity, 2),
        "final_equity": round(equity, 2),
        "net_profit": round(equity - initial_equity, 2),
        "return_percent": round((equity / initial_equity - 1.0) * 100.0, 2),
        "trades": len(profits),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_percent": round(len(wins) / len(profits) * 100.0, 2) if profits else 0.0,
        "profit_factor": round(gross_profit / gross_loss, 3) if gross_loss else None,
        "max_closed_equity_drawdown_percent": round(max_drawdown, 2),
        "cost_bps_per_side": cost_bps_per_side,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, help="CSV with time,open,high,low,close columns")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--synthetic-bars", type=int, default=3000)
    args = parser.parse_args()
    bars = load_csv(args.csv) if args.csv else synthetic_bars(args.synthetic_bars)
    report = run(bars)
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
