#ifndef PROJECT_ATLAS_CONTRACTS_MQH
#define PROJECT_ATLAS_CONTRACTS_MQH

#include <ProjectAtlas/Domain/TradeSignal.mqh>

class ISignalStrategy
  {
public:
   virtual bool              Initialize(void)=0;
   virtual void              Shutdown(void)=0;
   virtual ENUM_ATLAS_SIGNAL Evaluate(double &atr)=0;
  };

class IPositionSizer
  {
public:
   virtual double Calculate(const double stop_distance)=0;
  };

class ITradeGateway
  {
public:
   virtual bool HasOpenPosition(void)=0;
   virtual bool IsSpreadAllowed(void)=0;
   virtual bool Open(const ENUM_ATLAS_SIGNAL signal,
                     const double volume,
                     const double stop_distance,
                     const double take_profit_distance)=0;
  };

#endif
