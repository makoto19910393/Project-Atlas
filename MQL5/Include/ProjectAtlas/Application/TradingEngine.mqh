#ifndef PROJECT_ATLAS_TRADING_ENGINE_MQH
#define PROJECT_ATLAS_TRADING_ENGINE_MQH

#include <ProjectAtlas/Application/Contracts.mqh>

class CTradingEngine
  {
private:
   ISignalStrategy  *m_strategy;
   IPositionSizer   *m_sizer;
   ITradeGateway    *m_gateway;
   double            m_stop_atr_multiple;
   double            m_take_profit_atr_multiple;

public:
                     CTradingEngine(ISignalStrategy *strategy,
                                    IPositionSizer *sizer,
                                    ITradeGateway *gateway,
                                    const double stop_atr_multiple,
                                    const double take_profit_atr_multiple)
     {
      m_strategy= strategy;
      m_sizer= sizer;
      m_gateway= gateway;
      m_stop_atr_multiple= stop_atr_multiple;
      m_take_profit_atr_multiple= take_profit_atr_multiple;
     }

   bool              Initialize(void)
     {
      return m_strategy!=NULL && m_sizer!=NULL && m_gateway!=NULL && m_strategy.Initialize();
     }

   void              Shutdown(void)
     {
      if(m_strategy!=NULL)
         m_strategy.Shutdown();
     }

   void              OnTick(void)
     {
      double atr=0.0;
      const ENUM_ATLAS_SIGNAL signal=m_strategy.Evaluate(atr);
      if(signal==ATLAS_SIGNAL_NONE || atr<=0.0)
         return;
      if(m_gateway.HasOpenPosition() || !m_gateway.IsSpreadAllowed())
         return;

      const double stop_distance=atr*m_stop_atr_multiple;
      const double volume=m_sizer.Calculate(stop_distance);
      if(volume<=0.0)
        {
         Print("Project Atlas: calculated volume is invalid.");
         return;
        }

      m_gateway.Open(signal,volume,stop_distance,atr*m_take_profit_atr_multiple);
     }
  };

#endif
