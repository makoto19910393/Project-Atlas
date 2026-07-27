#ifndef PROJECT_ATLAS_CONFIG_MQH
#define PROJECT_ATLAS_CONFIG_MQH

class CAtlasConfig
  {
public:
   string            Symbol;
   ENUM_TIMEFRAMES   Timeframe;
   int               FastEmaPeriod;
   int               SlowEmaPeriod;
   int               AtrPeriod;
   int               BreakoutPeriod;
   int               TrendEmaPeriod;
   double            StopAtrMultiple;
   double            TakeProfitAtrMultiple;
   double            RiskPercent;
   double            MaximumRiskPercent;
   double            WinRiskMultiplier;
   double            LossRiskMultiplier;
   int               MaxSpreadPoints;
   ulong             MagicNumber;
   int               SlippagePoints;

                     CAtlasConfig(void)
     {
      Symbol                   = "BTCUSD";
      Timeframe                = PERIOD_M15;
      FastEmaPeriod            = 30;
      SlowEmaPeriod            = 100;
      AtrPeriod                = 14;
      BreakoutPeriod           = 10;
      TrendEmaPeriod           = 200;
      StopAtrMultiple          = 3.0;
      TakeProfitAtrMultiple    = 6.0;
      RiskPercent              = 2.5;
      MaximumRiskPercent       = 2.5;
      WinRiskMultiplier        = 1.0;
      LossRiskMultiplier       = 0.7;
      MaxSpreadPoints          = 5000;
      MagicNumber              = 26072026;
      SlippagePoints           = 100;
     }
  };

#endif
