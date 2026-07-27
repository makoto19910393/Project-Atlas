#!/usr/bin/env python3
"""Maximize multi-path annual return while enforcing a 40% drawdown ceiling."""

import json
import statistics
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parents[1]))
from backtest.backtest import run,synthetic_bars


def evaluate() -> dict[str,object]:
    paths=[synthetic_bars(35_040,seed=seed) for seed in range(26_072_026,26_072_046)]
    candidates=[]
    for lookback,target,trend,risk in product((10,20,30),(4.0,5.0,6.0),(0,100,200),(1.5,2.0,2.5,3.0)):
        results=[run(path,breakout_period=lookback,stop_atr=3.0,target_atr=target,
                     trend_ema_period=trend,risk_percent=risk,maximum_risk_percent=risk,
                     loss_risk_multiplier=0.7) for path in paths]
        returns=[item["return_percent"] for item in results]
        maximum_dd=max(item["max_closed_equity_drawdown_percent"] for item in results)
        candidates.append({"breakout_period":lookback,"trend_ema_period":trend,
                           "stop_atr":3.0,"target_atr":target,"risk_percent":risk,
                           "loss_risk_multiplier":0.7,"minimum_annual_return_percent":min(returns),
                           "median_annual_return_percent":round(statistics.median(returns),2),
                           "maximum_annual_drawdown_percent":maximum_dd,
                           "minimum_profit_factor":min(item["profit_factor"] for item in results)})
    eligible=[item for item in candidates if item["minimum_annual_return_percent"]>0.0 and
              item["maximum_annual_drawdown_percent"]<=40.0]
    selected=max(eligible,key=lambda item:item["median_annual_return_percent"])
    return {"data_kind":"twenty_deterministic_synthetic_annual_paths_not_market_history",
            "evaluated_configurations":len(candidates),"drawdown_ceiling_percent":40.0,
            "eligible_configurations":len(eligible),"selected":selected}


def main() -> None:
    payload=json.dumps(evaluate(),indent=2)+"\n"
    Path("backtest/results/profit-under-dd-validation.json").write_text(payload,encoding="utf-8")
    print(payload,end="")


if __name__=="__main__":main()
