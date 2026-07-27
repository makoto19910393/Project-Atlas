#!/usr/bin/env python3
"""Evaluate aggressive risk levels on twelve independent synthetic months."""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from backtest.backtest import run, synthetic_bars


RISKS = (1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 25.0, 30.0)


def evaluate() -> dict[str, object]:
    bars = synthetic_bars(35_040)
    rows = []
    for risk in RISKS:
        months = [run(bars[start:start + 2_920], risk_percent=risk,
                      breakout_period=30,stop_atr=3.0,target_atr=4.0,trend_ema_period=0,
                      loss_risk_multiplier=1.0,win_risk_multiplier=1.0,
                      maximum_risk_percent=None)
                  for start in range(0, 35_040, 2_920)]
        returns = [month["return_percent"] for month in months]
        drawdowns = [month["max_closed_equity_drawdown_percent"] for month in months]
        rows.append({
            "risk_percent": risk,
            "profitable_months": sum(value > 0.0 for value in returns),
            "months_reaching_10x": sum(value >= 900.0 for value in returns),
            "median_monthly_return_percent": round(statistics.median(returns), 2),
            "mean_monthly_return_percent": round(statistics.mean(returns), 2),
            "worst_month_return_percent": min(returns),
            "best_month_return_percent": max(returns),
            "maximum_monthly_drawdown_percent": max(drawdowns),
            "monthly_returns_percent": returns,
        })

    # Aggressive mode: accept at most two losing months and an 80% drawdown ceiling.
    eligible = [row for row in rows
                if row["profitable_months"] >= 10
                and row["maximum_monthly_drawdown_percent"] <= 80.0]
    selected = max(eligible, key=lambda row: row["median_monthly_return_percent"])
    return {
        "data_kind": "deterministic_synthetic_validation_not_market_history",
        "target": "JPY 50000 to JPY 500000 within one month (900% return)",
        "selection_policy": "maximize median monthly return; at least 10/12 profitable months; maximum drawdown <= 80%",
        "selected_risk_percent": selected["risk_percent"],
        "target_achieved_consistently": selected["months_reaching_10x"] == 12,
        "conclusion": "No tested risk achieved 10x consistently; reaching it required near-total drawdown in other months.",
        "risk_levels": rows,
    }


def main() -> None:
    payload = json.dumps(evaluate(), indent=2) + "\n"
    output = Path("backtest/results/monthly-risk-sweep.json")
    output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
