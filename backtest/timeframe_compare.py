#!/usr/bin/env python3
"""Compare timeframes on identical underlying M5 paths and elapsed time."""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parents[1]))
from backtest.backtest import Bar,run,synthetic_bars


TIMEFRAMES={
    "M5":{"factor":1,"breakout":30,"trend":600},
    "M15":{"factor":3,"breakout":10,"trend":200},
    "M30":{"factor":6,"breakout":5,"trend":100},
    "H1":{"factor":12,"breakout":3,"trend":50},
    "H4":{"factor":48,"breakout":2,"trend":13},
}


def aggregate(bars:list[Bar],factor:int)->list[Bar]:
    result=[]
    for start in range(0,len(bars)-factor+1,factor):
        group=bars[start:start+factor]
        result.append(Bar(group[0].time,group[0].open,max(item.high for item in group),
                          min(item.low for item in group),group[-1].close))
    return result


def evaluate()->dict[str,object]:
    rows=[]
    for name,config in TIMEFRAMES.items():
        results=[]
        for seed in range(26_072_026,26_072_046):
            base=synthetic_bars(105_120,seed=seed,interval_minutes=5,regime_bars=3000)
            bars=aggregate(base,config["factor"])
            results.append(run(bars,breakout_period=config["breakout"],trend_ema_period=config["trend"],
                               stop_atr=3.0,target_atr=6.0,risk_percent=2.5,
                               maximum_risk_percent=2.5,loss_risk_multiplier=0.7))
        returns=[item["return_percent"] for item in results]
        rows.append({"timeframe":name,"bars_per_year":len(aggregate(
                         synthetic_bars(105_120,interval_minutes=5,regime_bars=3000),config["factor"])),
                     "breakout_period":config["breakout"],"trend_ema_period":config["trend"],
                     "median_annual_return_percent":round(statistics.median(returns),2),
                     "minimum_annual_return_percent":min(returns),
                     "maximum_annual_drawdown_percent":max(
                         item["max_closed_equity_drawdown_percent"] for item in results),
                     "median_trades":statistics.median(item["trades"] for item in results),
                     "minimum_profit_factor":min(item["profit_factor"] for item in results)})
    eligible=[row for row in rows if row["maximum_annual_drawdown_percent"]<=40.0 and
              row["minimum_annual_return_percent"]>0.0]
    selected=max(eligible,key=lambda row:row["median_annual_return_percent"])
    return {"data_kind":"identical_underlying_synthetic_m5_paths_not_market_history",
            "years_per_timeframe":20,"drawdown_ceiling_percent":40.0,
            "comparison":rows,"selected":selected}


def main()->None:
    payload=json.dumps(evaluate(),indent=2)+"\n"
    Path("backtest/results/timeframe-comparison.json").write_text(payload,encoding="utf-8")
    print(payload,end="")


if __name__=="__main__":main()
