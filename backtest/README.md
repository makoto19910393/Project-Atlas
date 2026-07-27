# Backtest evidence

## Deterministic validation executed in this repository

Command:

```bash
python backtest/backtest.py --output backtest/results/synthetic-validation.json
```

The committed JSON is the direct output of that run. The generator uses a fixed seed and changing trend regimes, so the run is reproducible in CI. It is intended to exercise the complete rule path rather than claim market profitability.

`python backtest/optimize.py` compares EMA crossover and Donchian breakout method families on M15 bars, performs automatic parameter selection on four separate development regimes, and evaluates the selected configuration once on an untouched one-year holdout. A candidate must be profitable in every development fold and keep each development drawdown at or below 10% before it can be selected. This reduces, but cannot eliminate, synthetic-data overfitting. The resulting `walk-forward-validation.json` remains functional evidence—not a profit promise or historical BTCUSD evidence.

`python backtest/risk_sweep.py` evaluates the separate aggressive-risk question over twelve synthetic months. It records both upside and near-ruin outcomes; it does not optimize the entry strategy on those months.

`python backtest/adaptive_risk.py` searches anti-martingale overlays that increase risk during winning streaks and reduce it during losing streaks. This is deliberately extreme target research, not a safe-money-management recommendation.

`python backtest/robustness.py` reruns the selected overlay across 20 deterministic seeds (240 independent synthetic months) to expose seed sensitivity and prevent a single favorable path from being presented as repeatable performance.

`python backtest/profit_under_dd.py` jointly searches Donchian periods, EMA trend filters, ATR targets, and risk over 20 full-year paths, rejecting any configuration whose annual-path drawdown exceeds 40%.

`python backtest/timeframe_compare.py` aggregates identical underlying M5 paths into M5, M15, M30, H1, and H4 bars. Donchian and EMA horizons are rescaled to approximately 150 minutes and 3,000 minutes so the timeframe comparison does not silently change the intended observation windows.

Execution assumptions:

- a crossover on closed bar `i-1` enters at the open of bar `i`;
- only one position may be open;
- stop loss is checked before take profit when both occur in the same OHLC bar (conservative ambiguity handling);
- position risk is 1% of current closed equity;
- an open final position is marked to the final close;
- a configurable execution-cost proxy is charged at entry and exit (5 basis points per side by default); swap, latency, and broker volume constraints remain unmodeled.

## Native MT5 test

`mt5/ProjectAtlas.ini` defines a native Strategy Tester run for BTCUSD M15 from 2024-01-01 through 2025-12-31 with a JPY 50,000 initial deposit. Native execution requires MetaTrader 5, a broker connection that exposes BTCUSD, and downloaded tick history. It can be launched on Windows from the terminal directory with:

```powershell
terminal64.exe /config:C:\absolute\path\to\backtest\mt5\ProjectAtlas.ini
```

The generated `ProjectAtlas-report.html` is authoritative for broker-history performance. Do not compare the synthetic validation result with a native MT5 report as though they used the same market input or execution model.
