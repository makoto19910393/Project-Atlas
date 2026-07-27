#!/usr/bin/env python3
"""Walk-forward parameter selection with a final untouched holdout segment."""

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from backtest.backtest import run, synthetic_bars


FAST = (5, 8, 10, 12, 15, 20, 25, 30)
SLOW = (20, 30, 40, 50, 75, 100, 150, 200)
STOP = (1.0, 1.5, 2.0, 2.5, 3.0)
TARGET = (1.5, 2.0, 3.0, 4.0, 5.0, 6.0)
BREAKOUT = (10, 20, 30, 50, 75, 100, 150, 200)


def optimize() -> dict[str, object]:
    # 18 months of M15 bars: six months for selection and a full untouched year.
    bars = synthetic_bars(52_560, interval_minutes=15)
    development, holdout = bars[:17_520], bars[17_520:]
    candidates = []
    evaluated = 0
    specifications = []
    specifications.extend(("ema", fast, slow, 0, stop, target)
                          for fast, slow, stop, target in product(FAST, SLOW, STOP, TARGET)
                          if fast < slow)
    specifications.extend(("donchian", 0, 0, lookback, stop, target)
                          for lookback, stop, target in product(BREAKOUT, STOP, TARGET))
    for strategy, fast, slow, lookback, stop, target in specifications:
        evaluated += 1
        folds = [run(development[start:start + 4_380], initial_equity=50_000.0,
                     fast_period=fast, slow_period=slow,
                     stop_atr=stop, target_atr=target, strategy=strategy,
                     breakout_period=lookback,trend_ema_period=0)
                 for start in range(0, 17_520, 4_380)]
        returns = [fold["return_percent"] for fold in folds]
        worst_drawdown = max(fold["max_closed_equity_drawdown_percent"] for fold in folds)
        # Higher frequency must not be purchased with uncontrolled account risk.
        if min(returns) <= 0.0 or worst_drawdown > 10.0:
            continue
        score = sum(returns) / len(returns) - 0.5 * worst_drawdown
        candidates.append((score, strategy, fast, slow, lookback, stop, target, folds))

    if not candidates:
        raise RuntimeError("no stable parameter set found")
    score, strategy, fast, slow, lookback, stop, target, folds = max(candidates, key=lambda item: item[0])
    test = run(holdout, initial_equity=50_000.0, fast_period=fast,
               slow_period=slow, stop_atr=stop, target_atr=target,
               strategy=strategy, breakout_period=lookback,trend_ema_period=0)
    baseline = run(holdout, initial_equity=50_000.0, strategy="ema",
                   fast_period=30, slow_period=100, stop_atr=2.0,target_atr=6.0)
    return {
        "data_kind": "deterministic_synthetic_validation_not_market_history",
        "selection_policy": "all four development folds profitable and each drawdown <= 10%; maximize mean return minus 0.5 * worst drawdown",
        "evaluated_parameter_sets": evaluated,
        "stable_parameter_sets": len(candidates),
        "selected": {"strategy": strategy, "fast_ema": fast, "slow_ema": slow,
                     "breakout_period": lookback, "atr_period": 14,
                     "stop_atr": stop, "target_atr": target, "risk_percent": 1.0},
        "development_folds": folds,
        "selection_score": round(score, 3),
        "research_goal": {"annual_return_percent_min": 50.0,
                          "max_closed_equity_drawdown_percent_max": 15.0,
                          "profit_factor_min": 1.30,
                          "minimum_trades": 300},
        "goal_assessment": {
            "return_pass": test["return_percent"] >= 50.0,
            "drawdown_pass": test["max_closed_equity_drawdown_percent"] <= 15.0,
            "profit_factor_pass": test["profit_factor"] is not None and test["profit_factor"] >= 1.30,
            "trade_count_pass": test["trades"] >= 300,
        },
        "previous_ema_baseline_holdout": baseline,
        "untouched_holdout": test,
    }


def main() -> None:
    output = Path("backtest/results/walk-forward-validation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(optimize(), indent=2) + "\n"
    output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
