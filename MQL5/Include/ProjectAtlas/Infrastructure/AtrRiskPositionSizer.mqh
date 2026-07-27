#ifndef PROJECT_ATLAS_ATR_RISK_POSITION_SIZER_MQH
#define PROJECT_ATLAS_ATR_RISK_POSITION_SIZER_MQH

#include <ProjectAtlas/Application/Contracts.mqh>

class CAtrRiskPositionSizer : public IPositionSizer
  {
private:
   string m_symbol;
   double m_risk_percent;
   double m_maximum_risk_percent;
   double m_win_multiplier;
   double m_loss_multiplier;
   ulong  m_magic;

   double StreakMultiplier(void)
     {
      if(!HistorySelect(0,TimeCurrent()))
         return 1.0;
      int streak=0;
      int direction=0;
      for(int index=HistoryDealsTotal()-1;index>=0;index--)
        {
         const ulong ticket=HistoryDealGetTicket(index);
         if(ticket==0 || HistoryDealGetString(ticket,DEAL_SYMBOL)!=m_symbol ||
            (ulong)HistoryDealGetInteger(ticket,DEAL_MAGIC)!=m_magic)
            continue;
         const ENUM_DEAL_ENTRY entry=(ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket,DEAL_ENTRY);
         if(entry!=DEAL_ENTRY_OUT && entry!=DEAL_ENTRY_OUT_BY)
            continue;
         const double result=HistoryDealGetDouble(ticket,DEAL_PROFIT)+
                             HistoryDealGetDouble(ticket,DEAL_SWAP)+
                             HistoryDealGetDouble(ticket,DEAL_COMMISSION);
         const int current=(result>0.0 ? 1 : (result<0.0 ? -1 : 0));
         if(current==0)
            continue;
         if(direction==0)
            direction=current;
         if(current!=direction)
            break;
         streak++;
        }
      if(streak==0)
         return 1.0;
      return MathPow(direction>0 ? m_win_multiplier : m_loss_multiplier,streak);
     }

   int VolumeDigits(const double step)
     {
      int digits=0;
      double value=step;
      while(digits<8 && MathAbs(value-MathRound(value))>1e-8)
        {
         value*=10.0;
         digits++;
        }
      return digits;
     }

public:
   CAtrRiskPositionSizer(const string symbol,const double risk_percent,
                         const double maximum_risk_percent,const double win_multiplier,
                         const double loss_multiplier,const ulong magic)
     {
      m_symbol=symbol;
      m_risk_percent=risk_percent;
      m_maximum_risk_percent=maximum_risk_percent;
      m_win_multiplier=win_multiplier;
      m_loss_multiplier=loss_multiplier;
      m_magic=magic;
     }

   virtual double Calculate(const double stop_distance)
     {
      const double tick_size=SymbolInfoDouble(m_symbol,SYMBOL_TRADE_TICK_SIZE);
      const double tick_value=SymbolInfoDouble(m_symbol,SYMBOL_TRADE_TICK_VALUE_LOSS);
      const double volume_min=SymbolInfoDouble(m_symbol,SYMBOL_VOLUME_MIN);
      const double volume_max=SymbolInfoDouble(m_symbol,SYMBOL_VOLUME_MAX);
      const double volume_step=SymbolInfoDouble(m_symbol,SYMBOL_VOLUME_STEP);
      if(stop_distance<=0.0 || tick_size<=0.0 || tick_value<=0.0 || volume_step<=0.0)
         return 0.0;

      const double effective_risk=MathMin(m_risk_percent*StreakMultiplier(),m_maximum_risk_percent);
      const double risk_money=AccountInfoDouble(ACCOUNT_EQUITY)*effective_risk/100.0;
      const double loss_per_lot=(stop_distance/tick_size)*tick_value;
      if(risk_money<=0.0 || loss_per_lot<=0.0)
         return 0.0;

      double volume=MathFloor((risk_money/loss_per_lot)/volume_step)*volume_step;
      volume=MathMin(volume,volume_max);
      if(volume<volume_min)
         return 0.0;
      return NormalizeDouble(volume,VolumeDigits(volume_step));
     }
  };

#endif
