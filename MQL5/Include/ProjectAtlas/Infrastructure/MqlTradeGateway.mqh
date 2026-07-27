#ifndef PROJECT_ATLAS_MQL_TRADE_GATEWAY_MQH
#define PROJECT_ATLAS_MQL_TRADE_GATEWAY_MQH

#include <Trade/Trade.mqh>
#include <ProjectAtlas/Application/Contracts.mqh>

class CMqlTradeGateway : public ITradeGateway
  {
private:
   string m_symbol;
   ulong  m_magic;
   int    m_max_spread_points;
   CTrade m_trade;

public:
   CMqlTradeGateway(const string symbol,const ulong magic,const int max_spread_points,const int slippage_points)
     {
      m_symbol=symbol;
      m_magic=magic;
      m_max_spread_points=max_spread_points;
      m_trade.SetExpertMagicNumber(magic);
      m_trade.SetDeviationInPoints(slippage_points);
      m_trade.SetTypeFillingBySymbol(symbol);
     }

   virtual bool HasOpenPosition(void)
     {
      for(int index=PositionsTotal()-1;index>=0;index--)
        {
         const ulong ticket=PositionGetTicket(index);
         if(ticket>0 && PositionGetString(POSITION_SYMBOL)==m_symbol &&
            (ulong)PositionGetInteger(POSITION_MAGIC)==m_magic)
            return true;
        }
      return false;
     }

   virtual bool IsSpreadAllowed(void)
     {
      MqlTick tick;
      const double point=SymbolInfoDouble(m_symbol,SYMBOL_POINT);
      if(point<=0.0 || !SymbolInfoTick(m_symbol,tick))
         return false;
      return ((tick.ask-tick.bid)/point)<=m_max_spread_points;
     }

   virtual bool Open(const ENUM_ATLAS_SIGNAL signal,const double volume,
                     const double stop_distance,const double take_profit_distance)
     {
      MqlTick tick;
      if(!SymbolInfoTick(m_symbol,tick))
         return false;
      const int digits=(int)SymbolInfoInteger(m_symbol,SYMBOL_DIGITS);
      bool result=false;
      if(signal==ATLAS_SIGNAL_BUY)
        {
         const double sl=NormalizeDouble(tick.ask-stop_distance,digits);
         const double tp=NormalizeDouble(tick.ask+take_profit_distance,digits);
         result=m_trade.Buy(volume,m_symbol,0.0,sl,tp,"Project Atlas breakout");
        }
      else if(signal==ATLAS_SIGNAL_SELL)
        {
         const double sl=NormalizeDouble(tick.bid+stop_distance,digits);
         const double tp=NormalizeDouble(tick.bid-take_profit_distance,digits);
         result=m_trade.Sell(volume,m_symbol,0.0,sl,tp,"Project Atlas breakout");
        }
      if(!result)
         PrintFormat("Project Atlas: order failed. Retcode=%u, %s",
                     m_trade.ResultRetcode(),m_trade.ResultRetcodeDescription());
      return result;
     }
  };

#endif
