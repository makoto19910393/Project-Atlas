from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_expected_modules_exist():
    expected = [
        "MQL5/Experts/ProjectAtlas/ProjectAtlas.mq5",
        "MQL5/Include/ProjectAtlas/Domain/TradeSignal.mqh",
        "MQL5/Include/ProjectAtlas/Domain/AtlasConfig.mqh",
        "MQL5/Include/ProjectAtlas/Application/Contracts.mqh",
        "MQL5/Include/ProjectAtlas/Application/TradingEngine.mqh",
        "MQL5/Include/ProjectAtlas/Infrastructure/EmaAtrSignalStrategy.mqh",
        "MQL5/Include/ProjectAtlas/Infrastructure/DonchianAtrSignalStrategy.mqh",
        "MQL5/Include/ProjectAtlas/Infrastructure/AtrRiskPositionSizer.mqh",
        "MQL5/Include/ProjectAtlas/Infrastructure/MqlTradeGateway.mqh",
    ]
    assert all((ROOT / path).is_file() for path in expected)


def test_entrypoint_uses_modules_and_required_callbacks():
    source = (ROOT / "MQL5/Experts/ProjectAtlas/ProjectAtlas.mq5").read_text()
    assert "int OnInit(void)" in source
    assert "void OnTick(void)" in source
    assert "void OnDeinit(const int reason)" in source
    assert source.count("#include <ProjectAtlas/") == 5
    assert "InpTimeframe=PERIOD_M15" in source
    assert "InpRiskPercent=2.5" in source
    assert "InpMaximumRiskPercent=2.5" in source
    assert "InpWinRiskMultiplier=1.0" in source
    assert "InpLossRiskMultiplier=0.7" in source
    assert "InpTrendEmaPeriod=200" in source


def test_strategy_uses_closed_candles_and_atr():
    source = (ROOT / "MQL5/Include/ProjectAtlas/Infrastructure/DonchianAtrSignalStrategy.mqh").read_text()
    assert "iClose(m_symbol,m_timeframe,1)" in source
    assert "m_breakout_period,2" in source
    assert "CopyBuffer(m_atr_handle,0,1,1,atr_buffer)" in source
    assert "current_bar==m_last_bar_time" in source


def test_no_placeholder_markers():
    sources = [*ROOT.glob("MQL5/**/*.mq5"), *ROOT.glob("MQL5/**/*.mqh")]
    joined = "\n".join(path.read_text() for path in sources)
    assert "TODO" not in joined


def test_project_includes_resolve_and_braces_are_balanced():
    sources = [*ROOT.glob("MQL5/**/*.mq5"), *ROOT.glob("MQL5/**/*.mqh")]
    include_root = ROOT / "MQL5/Include"
    for path in sources:
        source = path.read_text()
        assert source.count("{") == source.count("}"), path
        for line in source.splitlines():
            prefix = "#include <ProjectAtlas/"
            if line.startswith(prefix):
                include = line.removeprefix("#include <").removesuffix(">")
                assert (include_root / include).is_file(), (path, include)
