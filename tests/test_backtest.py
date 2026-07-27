import json
from pathlib import Path

from backtest.backtest import Bar, run, synthetic_bars


def test_reference_backtest_is_deterministic():
    result = run(synthetic_bars())
    assert result["bars"] == 3000
    assert result["initial_equity"] == 50000.0
    assert result["final_equity"] == 72050.95
    assert result["trades"] == 43
    assert result["wins"] == 21
    assert result["profit_factor"] == 1.906
    assert result["max_closed_equity_drawdown_percent"] == 11.02
    assert result["cost_bps_per_side"] == 5.0
    assert result == run(synthetic_bars())


def test_rejects_insufficient_history():
    try:
        run(synthetic_bars(10))
    except ValueError as error:
        assert str(error) == "not enough bars"
    else:
        raise AssertionError("short history must be rejected")


def test_bar_model_is_explicit():
    assert tuple(Bar.__dataclass_fields__) == ("time", "open", "high", "low", "close")


def test_execution_cost_reduces_equity():
    bars = synthetic_bars(1000)
    assert run(bars, cost_bps_per_side=5.0)["final_equity"] < run(bars, cost_bps_per_side=0.0)["final_equity"]


def test_walk_forward_result_uses_50000_holdout_and_profitable_folds():
    report = json.loads((Path(__file__).parents[1] / "backtest/results/walk-forward-validation.json").read_text())
    assert report["data_kind"] == "deterministic_synthetic_validation_not_market_history"
    assert all(fold["return_percent"] > 0 for fold in report["development_folds"])
    assert report["selected"] == {
        "strategy": "donchian", "fast_ema": 0, "slow_ema": 0,
        "breakout_period": 30, "atr_period": 14,
        "stop_atr": 3.0, "target_atr": 4.0, "risk_percent": 1.0,
    }
    assert report["untouched_holdout"]["initial_equity"] == 50000.0
    assert report["untouched_holdout"]["final_equity"] == 175205.23
    assert report["untouched_holdout"]["return_percent"] > report["previous_ema_baseline_holdout"]["return_percent"]
    assert all(report["goal_assessment"].values())


def test_monthly_risk_sweep_rejects_10x_claim():
    report = json.loads((Path(__file__).parents[1] / "backtest/results/monthly-risk-sweep.json").read_text())
    assert report["selected_risk_percent"] == 10.0
    assert report["target_achieved_consistently"] is False
    selected = next(row for row in report["risk_levels"] if row["risk_percent"] == 10.0)
    assert selected["profitable_months"] == 11
    assert selected["months_reaching_10x"] == 0
    assert selected["worst_month_return_percent"] == -73.84
    assert selected["maximum_monthly_drawdown_percent"] == 79.81


def test_adaptive_risk_respects_forty_percent_drawdown_ceiling():
    report = json.loads((Path(__file__).parents[1] / "backtest/results/adaptive-risk-validation.json").read_text())
    assert report["evaluated_overlays"] == 276
    assert report["target_achieved_consistently"] is False
    assert report["selected"]["base_risk_percent"] == 3.0
    assert report["selected"]["maximum_risk_percent"] == 3.0
    assert report["selected"]["months_reaching_10x"] == 0
    assert report["selected"]["worst_month_return_percent"] == -28.23
    assert report["selected"]["maximum_monthly_drawdown_percent"] == 32.61


def test_multi_seed_robustness_rejects_monthly_10x_target():
    report = json.loads((Path(__file__).parents[1] / "backtest/results/adaptive-risk-robustness.json").read_text())
    assert report["months"] == 240
    assert report["ten_x_months"] == 0
    assert report["ten_x_month_rate_percent"] == 0.0
    assert report["profitable_month_rate_percent"] == 79.17
    assert report["worst_month_return_percent"] == -31.39
    assert report["maximum_monthly_drawdown_percent"] == 39.23
    assert report["target_validated"] is False


def test_profit_search_respects_dd_ceiling():
    report = json.loads((Path(__file__).parents[1] / "backtest/results/profit-under-dd-validation.json").read_text())
    assert report["evaluated_configurations"] == 108
    assert report["eligible_configurations"] == 38
    assert report["selected"]["trend_ema_period"] == 200
    assert report["selected"]["median_annual_return_percent"] == 2689.8
    assert report["selected"]["maximum_annual_drawdown_percent"] == 35.49
    assert report["selected"]["maximum_annual_drawdown_percent"] <= report["drawdown_ceiling_percent"]


def test_timeframe_comparison_selects_m15_under_dd_ceiling():
    report = json.loads((Path(__file__).parents[1] / "backtest/results/timeframe-comparison.json").read_text())
    assert [row["timeframe"] for row in report["comparison"]] == ["M5", "M15", "M30", "H1", "H4"]
    assert report["selected"]["timeframe"] == "M15"
    assert report["selected"]["maximum_annual_drawdown_percent"] == 30.79
    m5 = report["comparison"][0]
    assert m5["maximum_annual_drawdown_percent"] == 49.03
    assert m5["maximum_annual_drawdown_percent"] > report["drawdown_ceiling_percent"]
