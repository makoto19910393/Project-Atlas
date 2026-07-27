# Strategy experiment log

This log records decision questions and observable answers without treating synthetic output as market evidence.

## 1. Was parameter tuning alone enough?

- **Question:** Can the original EMA crossover be improved without changing the method family?
- **Experiment:** Search 1,800 EMA/ATR combinations across four development folds.
- **Observation:** The stable EMA 30/100, 2 ATR stop, 6 ATR target baseline returned 12.02% on the later holdout, with profit factor 1.492 and 4.96% closed-equity drawdown.
- **Decision:** Keep it as the explicit baseline, but test a different trend-entry mechanism.

## 2. Does a price breakout capture persistent moves better?

- **Question:** Does a Donchian close breakout avoid the lag of waiting for two moving averages to cross?
- **Experiment:** Add 240 Donchian/ATR combinations (eight channel periods, five stops, six targets) to the same four-fold selection process. No holdout result participates in selection.
- **Observation:** Donchian 50, 1.5 ATR stop, and 5 ATR target had the highest development score among candidates profitable in every fold. On the untouched holdout it returned 24.71%, versus 12.02% for the recorded EMA baseline.
- **Decision:** Replace the EA entry module with the selected Donchian implementation while retaining ATR sizing and the 1% risk cap.

## 3. Should risk be increased to amplify profit?

- **Question:** Would raising per-trade risk create a larger headline profit?
- **Observation:** Profit and drawdown would both be mechanically amplified. The selected method already reached 16.11% closed-equity drawdown at 1% risk on the synthetic holdout.
- **Decision:** Do not increase the 1% risk default. Improve signal quality before leverage.

## Next evidence required

The next acceptable promotion gate is native MT5 testing on broker BTCUSD ticks with spread, volume steps, commissions, swap, and slippage, followed by a genuinely unseen date range. Until that passes, the Donchian result is a research hypothesis rather than evidence of expected live profit.

## 4. Does moving from H1 to M15 physically increase opportunities?

- **Question:** Can the EA enter more often without opening simultaneous positions or increasing per-trade risk?
- **Experiment:** Change signal generation to M15, expand validation to 52,560 M15 bars, reserve the final 35,040 bars (one full 365-day year) as holdout, and rerun both method families.
- **Observation:** The selected Donchian 10 / 2.5 ATR stop / 3 ATR target configuration produced 1,416 closed trades in the synthetic annual holdout, compared with 90 trades in the earlier 4,000-bar H1-style holdout. It met the 15% development-fold drawdown ceiling; annual holdout closed-equity drawdown was 14.43%.
- **Decision:** Adopt M15 and the newly selected parameters. Keep one position and 1% risk constraints. The very large compounded synthetic return is not used as a live target because transaction costs and real BTCUSD microstructure are absent.

The explicit research gate is now annual return at least 50%, profit factor at least 1.30, at least 300 closed trades, and maximum closed-equity drawdown no greater than 15%. It is a rejection gate, not a promise: a result can fail in native MT5 even after passing here.

## 5. Does the high-frequency result survive modeled execution costs?

- **Question:** Is the previous result still attractive after charging every entry and exit rather than assuming free execution?
- **Experiment:** Charge 5 basis points per side (10 bps round trip), include those costs in risk sizing and net P/L, tighten every development fold to a 10% drawdown ceiling, and rerun all 2,040 configurations.
- **Observation:** Only three configurations passed. Donchian 30 / 3 ATR stop / 4 ATR target was selected. On the untouched synthetic year it produced 826 trades, 250.41% net return, profit factor 1.357, and 13.71% maximum closed-equity drawdown after modeled costs.
- **Decision:** Replace the earlier cost-free Donchian 10 configuration. A smaller cost-aware result is better evidence than a larger frictionless result.

## 6. Can JPY 50,000 become JPY 500,000 every month by relaxing risk?

- **Question:** What happens when per-trade risk is swept from 1% through 30% over twelve independent 2,920-bar M15 months?
- **Experiment:** Keep the cost-aware Donchian 30 strategy fixed and require an aggressive candidate to have at least 10 profitable months and no monthly drawdown above 80%.
- **Observation:** 10% risk maximized median monthly return within that boundary: median +111.62%, 11/12 profitable months, worst month -73.84%, and maximum drawdown 79.81%. It reached +900% in 0/12 months. Risks of 15% through 30% reached +900% in only 2/12 months while worst-month losses ranged from -90.34% to -99.88%.
- **Decision:** Expose 10% as the aggressive research default requested, but record that the 10x monthly target was not achieved. Higher tested risk is rejected because it behaves like account ruin rather than repeatable growth.

## 7. Can anti-martingale risk make 10x months more frequent?

- **Question:** Instead of using constant risk, can risk be raised only during winning streaks and reduced after losses?
- **Experiment:** Evaluate 180 overlays combining 3–10% base risk, 1.25–2.0 win multipliers, 0.35–0.7 loss multipliers, and 10–30% caps over the same twelve months with modeled costs.
- **Observation:** The selected 8% base / 2.0 win multiplier / 0.7 loss multiplier / 20% cap produced 3/12 10x months versus 0/12 for fixed 10% risk. It had 11/12 profitable months and +123.35% median return, but its worst month was -90.11% and maximum drawdown was 92.11%.
- **Decision:** Implement the overlay as an explicitly aggressive research mode. The target remains unproven because nine of twelve months did not reach 10x and one month almost destroyed the account.

## 8. Does the adaptive result survive alternate price paths?

- **Question:** Was the 3/12 result dependent on one favorable synthetic seed?
- **Experiment:** Run the selected overlay over 20 seeds, totaling 240 independent synthetic months.
- **Observation:** Only 41/240 months (17.08%) reached 10x; 179/240 (74.58%) were profitable; the worst month was -90.88%. Some synthetic years had only six profitable months.
- **Decision:** Reject “monthly 10x” as a validated expectation. The overlay increases upside frequency, but the logic still needs genuinely independent alpha sources—not more leverage—to approach consistency.

## 9. Can adaptive risk stay below 40% drawdown?

- **Question:** What is the strongest overlay when maximum monthly drawdown is a hard 40% ceiling?
- **Experiment:** Expand the search to 276 lower-risk overlays and enforce a 35% development ceiling, reserving five percentage points for path variation.
- **Observation:** The selected 3% base / 1.0 win multiplier / 0.7 loss multiplier / 3% cap returned a +28.85% monthly median across the selection path, with -28.23% worst month and 32.61% maximum drawdown. Across 20 seeds and 240 months it produced 79.17% profitable months, +25.08% median-of-medians, -31.39% worst month, 39.23% maximum drawdown, and zero 10x months.
- **Decision:** Adopt the 40%-bounded overlay. Monthly 10x is incompatible with the requested drawdown ceiling in the tested strategy family.

## 10. Can signal quality increase profit without breaking 40% DD?

- **Question:** Can a long-term trend filter improve profit more safely than raising risk?
- **Experiment:** Jointly test 108 Donchian/EMA/ATR/risk configurations over 20 full-year paths and reject any configuration above 40% annual drawdown.
- **Observation:** 38 configurations qualified. Donchian 10 with EMA(200), 3 ATR stop, 6 ATR target, 2.5% base/max risk, and 0.7 loss multiplier produced +2,689.80% median annual return, +283.27% minimum annual return, 35.49% maximum annual drawdown, and 1.309 minimum profit factor across the synthetic paths.
- **Decision:** Adopt the trend-filtered configuration. The improvement comes from filtering counter-trend breakouts rather than relaxing the drawdown ceiling.

## 11. Is M15 actually the best timeframe under 40% DD?

- **Question:** Does M15 outperform M5, M30, H1, and H4 when every timeframe sees the same underlying price paths and elapsed year?
- **Experiment:** Generate 20 annual M5 paths, aggregate the identical OHLC stream into every timeframe, and rescale Donchian/EMA periods to approximately 150/3,000 minutes. Keep costs and risk logic equal.
- **Observation:** M5 had the highest headline return but failed the 40% boundary at 49.03% DD. M15 passed at 30.79% and had the highest median return among eligible timeframes. M30, H1, and H4 reduced DD further but also reduced trade frequency and return.
- **Decision:** Retain M15. It is now selected by a cross-timeframe test rather than assumed from entry frequency alone.
