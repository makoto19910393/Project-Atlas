#ifndef PROJECT_ATLAS_DONCHIAN_ATR_SIGNAL_STRATEGY_MQH
#define PROJECT_ATLAS_DONCHIAN_ATR_SIGNAL_STRATEGY_MQH

#include <ProjectAtlas/Application/Contracts.mqh>

class CDonchianAtrSignalStrategy : public ISignalStrategy
  {
private:
   string           m_symbol;
   ENUM_TIMEFRAMES  m_timeframe;
   int              m_breakout_period;
   int              m_atr_period;
   int              m_trend_period;
   int              m_atr_handle;
   int              m_trend_handle;
   datetime         m_last_bar_time;

public:
   CDonchianAtrSignalStrategy(const string symbol,const ENUM_TIMEFRAMES timeframe,
                              const int breakout_period,const int atr_period,const int trend_period)
     {
      m_symbol=symbol;
      m_timeframe=timeframe;
      m_breakout_period=breakout_period;
      m_atr_period=atr_period;
      m_trend_period=trend_period;
      m_atr_handle=INVALID_HANDLE;
      m_trend_handle=INVALID_HANDLE;
      m_last_bar_time=0;
     }

   virtual bool Initialize(void)
     {
      m_atr_handle=iATR(m_symbol,m_timeframe,m_atr_period);
      m_trend_handle=iMA(m_symbol,m_timeframe,m_trend_period,0,MODE_EMA,PRICE_CLOSE);
      if(m_atr_handle==INVALID_HANDLE || m_trend_handle==INVALID_HANDLE)
        {
         PrintFormat("Project Atlas: ATR initialization failed (%d).",GetLastError());
         return false;
        }
      return true;
     }

   virtual void Shutdown(void)
     {
      if(m_atr_handle!=INVALID_HANDLE)
         IndicatorRelease(m_atr_handle);
      if(m_trend_handle!=INVALID_HANDLE)
         IndicatorRelease(m_trend_handle);
      m_atr_handle=INVALID_HANDLE;
      m_trend_handle=INVALID_HANDLE;
     }

   virtual ENUM_ATLAS_SIGNAL Evaluate(double &atr)
     {
      atr=0.0;
      const datetime current_bar=iTime(m_symbol,m_timeframe,0);
      if(current_bar<=0 || current_bar==m_last_bar_time)
         return ATLAS_SIGNAL_NONE;
      m_last_bar_time=current_bar;
      if(Bars(m_symbol,m_timeframe)<MathMax(m_breakout_period+m_atr_period,m_trend_period)+2)
         return ATLAS_SIGNAL_NONE;

      double atr_buffer[1],trend_buffer[1];
      if(CopyBuffer(m_atr_handle,0,1,1,atr_buffer)!=1 ||
         CopyBuffer(m_trend_handle,0,1,1,trend_buffer)!=1)
         return ATLAS_SIGNAL_NONE;
      const int highest=iHighest(m_symbol,m_timeframe,MODE_HIGH,m_breakout_period,2);
      const int lowest=iLowest(m_symbol,m_timeframe,MODE_LOW,m_breakout_period,2);
      if(highest<0 || lowest<0)
         return ATLAS_SIGNAL_NONE;

      atr=atr_buffer[0];
      const double close=iClose(m_symbol,m_timeframe,1);
      if(close>iHigh(m_symbol,m_timeframe,highest) && close>trend_buffer[0])
         return ATLAS_SIGNAL_BUY;
      if(close<iLow(m_symbol,m_timeframe,lowest) && close<trend_buffer[0])
         return ATLAS_SIGNAL_SELL;
      return ATLAS_SIGNAL_NONE;
     }
  };

#endif
