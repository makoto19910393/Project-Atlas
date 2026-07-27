# Project Atlas

Project Atlas is a modular MetaTrader 5 Expert Advisor restricted to `BTCUSD`.

## Trading rules

- Timeframe: M15 by default to increase the number of independently confirmed entry opportunities.
- Entry: 10-bar Donchian breakout confirmed on a closed candle and aligned with EMA(200).
- Stop loss: 3 ATR(14).
- Take profit: 6 ATR(14).
- Position size: drawdown-controlled mode risks 2.5% after wins and multiplies risk by 0.7 after each consecutive loss; risk never exceeds 2.5%.
- Exposure: at most one position opened by this EA (symbol + magic number).
- Guardrails: closed-bar evaluation, spread limit, input validation, and BTCUSD-only startup validation.

All values are EA inputs. The implementation is split into Domain, Application, and Infrastructure modules beneath `MQL5/Include/ProjectAtlas`.

The research gate is intentionally above 20%: at least 50% annual return, profit factor 1.30, 300 trades, and no more than 15% closed-equity drawdown on a full one-year holdout. Passing this gate on synthetic data is not a performance forecast; native broker-tick validation with costs is required before deployment.

## Install

Copy `MQL5/Experts/ProjectAtlas` and `MQL5/Include/ProjectAtlas` into the matching directories in the MetaTrader 5 data folder, then compile `ProjectAtlas.mq5` in MetaEditor.

## Backtesting

The repository contains two complementary backtest paths:

1. `python backtest/backtest.py --csv BTCUSD_H1.csv` runs the deterministic, bar-by-bar reference model. The CSV columns must be `time,open,high,low,close`.
2. `terminal64.exe /config:backtest/mt5/ProjectAtlas.ini` runs the EA in the native MT5 Strategy Tester after compiling the EA and adjusting the broker symbol/date range if required.

Run `python backtest/backtest.py --output backtest/results/synthetic-validation.json` for the bundled deterministic execution-path validation. The synthetic report is deliberately labelled as such: it verifies signal timing, sizing, stop/target handling, and metric generation, but must **not** be interpreted as historical BTCUSD performance. Native MT5 results depend on broker-specific BTCUSD ticks, contract size, spread, and trading conditions and are therefore not fabricated or substituted with the synthetic result.
