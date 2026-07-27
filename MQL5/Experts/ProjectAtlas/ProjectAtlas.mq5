#property copyright "Project Atlas"
#property version   "1.00"
#property strict
#property description "BTCUSD Donchian breakout EA with ATR-based risk management"

#include <ProjectAtlas/Domain/AtlasConfig.mqh>
#include <ProjectAtlas/Infrastructure/DonchianAtrSignalStrategy.mqh>
#include <ProjectAtlas/Infrastructure/AtrRiskPositionSizer.mqh>
#include <ProjectAtlas/Infrastructure/MqlTradeGateway.mqh>
#include <ProjectAtlas/Application/TradingEngine.mqh>

input string          InpSymbol="BTCUSD";
input ENUM_TIMEFRAMES InpTimeframe=PERIOD_M15;
input int             InpBreakoutPeriod=10;
input int             InpAtrPeriod=14;
input int             InpTrendEmaPeriod=200;
input double          InpStopAtrMultiple=3.0;
input double          InpTakeProfitAtrMultiple=6.0;
input double          InpRiskPercent=2.5;
input double          InpMaximumRiskPercent=2.5;
input double          InpWinRiskMultiplier=1.0;
input double          InpLossRiskMultiplier=0.7;
input int             InpMaxSpreadPoints=5000;
input ulong           InpMagicNumber=26072026;
input int             InpSlippagePoints=100;

CAtlasConfig          g_config;
CDonchianAtrSignalStrategy *g_strategy=NULL;
CAtrRiskPositionSizer *g_sizer=NULL;
CMqlTradeGateway      *g_gateway=NULL;
CTradingEngine        *g_engine=NULL;

bool LoadAndValidateConfig(void)
  {
   g_config.Symbol=InpSymbol;
   g_config.Timeframe=InpTimeframe;
   g_config.BreakoutPeriod=InpBreakoutPeriod;
   g_config.AtrPeriod=InpAtrPeriod;
   g_config.TrendEmaPeriod=InpTrendEmaPeriod;
   g_config.StopAtrMultiple=InpStopAtrMultiple;
   g_config.TakeProfitAtrMultiple=InpTakeProfitAtrMultiple;
   g_config.RiskPercent=InpRiskPercent;
   g_config.MaximumRiskPercent=InpMaximumRiskPercent;
   g_config.WinRiskMultiplier=InpWinRiskMultiplier;
   g_config.LossRiskMultiplier=InpLossRiskMultiplier;
   g_config.MaxSpreadPoints=InpMaxSpreadPoints;
   g_config.MagicNumber=InpMagicNumber;
   g_config.SlippagePoints=InpSlippagePoints;

   if(g_config.Symbol!="BTCUSD")
     {
      Print("Project Atlas: this EA is restricted to BTCUSD.");
      return false;
     }
   if(_Symbol!=g_config.Symbol)
     {
      PrintFormat("Project Atlas: attach the EA to %s (current chart: %s).",g_config.Symbol,_Symbol);
      return false;
     }
   if(g_config.BreakoutPeriod<2 || g_config.AtrPeriod<2 || g_config.TrendEmaPeriod<2 ||
      g_config.StopAtrMultiple<=0.0 ||
      g_config.TakeProfitAtrMultiple<=0.0 || g_config.RiskPercent<=0.0 ||
      g_config.RiskPercent>100.0 || g_config.MaximumRiskPercent<g_config.RiskPercent ||
      g_config.MaximumRiskPercent>100.0 || g_config.WinRiskMultiplier<1.0 ||
      g_config.LossRiskMultiplier<=0.0 || g_config.LossRiskMultiplier>1.0 ||
      g_config.MaxSpreadPoints<0)
     {
      Print("Project Atlas: invalid input parameters.");
      return false;
     }
   return true;
  }

int OnInit(void)
  {
   if(!LoadAndValidateConfig())
      return INIT_PARAMETERS_INCORRECT;
   if(!SymbolSelect(g_config.Symbol,true))
      return INIT_FAILED;

   g_strategy=new CDonchianAtrSignalStrategy(g_config.Symbol,g_config.Timeframe,
                                             g_config.BreakoutPeriod,g_config.AtrPeriod,
                                             g_config.TrendEmaPeriod);
   g_sizer=new CAtrRiskPositionSizer(g_config.Symbol,g_config.RiskPercent,
                                     g_config.MaximumRiskPercent,g_config.WinRiskMultiplier,
                                     g_config.LossRiskMultiplier,g_config.MagicNumber);
   g_gateway=new CMqlTradeGateway(g_config.Symbol,g_config.MagicNumber,
                                  g_config.MaxSpreadPoints,g_config.SlippagePoints);
   g_engine=new CTradingEngine(g_strategy,g_sizer,g_gateway,
                               g_config.StopAtrMultiple,g_config.TakeProfitAtrMultiple);
   if(g_engine==NULL || !g_engine.Initialize())
     {
      OnDeinit(REASON_INITFAILED);
      return INIT_FAILED;
     }
   Print("Project Atlas initialized.");
   return INIT_SUCCEEDED;
  }

void OnTick(void)
  {
   if(g_engine!=NULL)
      g_engine.OnTick();
  }

void OnDeinit(const int reason)
  {
   if(g_engine!=NULL)
     {
      g_engine.Shutdown();
      delete g_engine;
      g_engine=NULL;
     }
   if(g_gateway!=NULL) { delete g_gateway; g_gateway=NULL; }
   if(g_sizer!=NULL)   { delete g_sizer;   g_sizer=NULL; }
   if(g_strategy!=NULL){ delete g_strategy;g_strategy=NULL; }
  }
