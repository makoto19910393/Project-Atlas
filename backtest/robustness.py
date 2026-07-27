#!/usr/bin/env python3
"""Multi-seed robustness check for the selected adaptive-risk overlay."""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parents[1]))

from backtest.backtest import run,synthetic_bars


def evaluate() -> dict[str,object]:
    yearly=[]
    for seed in range(26_072_026,26_072_046):
        bars=synthetic_bars(35_040,seed=seed)
        months=[run(bars[start:start+2_920],risk_percent=3.0,
                    win_risk_multiplier=1.0,loss_risk_multiplier=0.7,
                    maximum_risk_percent=3.0,breakout_period=30,
                    stop_atr=3.0,target_atr=4.0,trend_ema_period=0)
                for start in range(0,35_040,2_920)]
        returns=[month["return_percent"] for month in months]
        yearly.append({"seed":seed,"profitable_months":sum(value>0 for value in returns),
                       "months_reaching_10x":sum(value>=900 for value in returns),
                       "median_monthly_return_percent":round(statistics.median(returns),2),
                       "worst_month_return_percent":min(returns),
                       "maximum_monthly_drawdown_percent":max(
                           month["max_closed_equity_drawdown_percent"] for month in months)})
    total_months=len(yearly)*12
    hits=sum(row["months_reaching_10x"] for row in yearly)
    profitable=sum(row["profitable_months"] for row in yearly)
    return {
        "data_kind":"twenty_deterministic_synthetic_seeds_not_market_history",
        "years":len(yearly),"months":total_months,
        "ten_x_months":hits,"ten_x_month_rate_percent":round(hits/total_months*100,2),
        "profitable_months":profitable,
        "profitable_month_rate_percent":round(profitable/total_months*100,2),
        "median_of_yearly_median_returns_percent":round(statistics.median(
            row["median_monthly_return_percent"] for row in yearly),2),
        "worst_month_return_percent":min(row["worst_month_return_percent"] for row in yearly),
        "maximum_monthly_drawdown_percent":max(
            row["maximum_monthly_drawdown_percent"] for row in yearly),
        "target_validated":hits==total_months,
        "yearly_results":yearly,
    }


def main() -> None:
    payload=json.dumps(evaluate(),indent=2)+"\n"
    Path("backtest/results/adaptive-risk-robustness.json").write_text(payload,encoding="utf-8")
    print(payload,end="")


if __name__=="__main__":
    main()
