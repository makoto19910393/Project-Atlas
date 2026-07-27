#ifndef PROJECT_ATLAS_EMA_ATR_SIGNAL_STRATEGY_MQH
#define PROJECT_ATLAS_EMA_ATR_SIGNAL_STRATEGY_MQH

#include <ProjectAtlas/Application/Contracts.mqh>

class CEmaAtrSignalStrategy : public ISignalStrategy
  {
private:
   string            m_symbol;
   ENUM_TIMEFRAMES   m_timeframe;
   int               m_fast_period;
   int               m_slow_period;
   int               m_atr_period;
   int               m_fast_handle;
   int               m_slow_handle;
   int               m_atr_handle;
   datetime          m_last_bar_time;

public:
                     CEmaAtrSignalStrategy(const string symbol,
                                           const ENUM_TIMEFRAMES timeframe,
                                           const int fast_period,
                                           const int slow_period,
                                           const int atr_period)
     {
      m_symbol=symbol;
      m_timeframe=timeframe;
      m_fast_period=fast_period;
      m_slow_period=slow_period;
      m_atr_period=atr_period;
      m_fast_handle=INVALID_HANDLE;
      m_slow_handle=INVALID_HANDLE;
      m_atr_handle=INVALID_HANDLE;
      m_last_bar_time=0;
     }

   virtual bool Initialize(void)
     {
      m_fast_handle=iMA(m_symbol,m_timeframe,m_fast_period,0,MODE_EMA,PRICE_CLOSE);
      m_slow_handle=iMA(m_symbol,m_timeframe,m_slow_period,0,MODE_EMA,PRICE_CLOSE);
      m_atr_handle=iATR(m_symbol,m_timeframe,m_atr_period);
      if(m_fast_handle==INVALID_HANDLE || m_slow_handle==INVALID_HANDLE || m_atr_handle==INVALID_HANDLE)
        {
         PrintFormat("Project Atlas: indicator initialization failed (%d).",GetLastError());
         Shutdown();
         return false;
        }
      return true;
     }

   virtual void Shutdown(void)
     {
      if(m_fast_handle!=INVALID_HANDLE) IndicatorRelease(m_fast_handle);
      if(m_slow_handle!=INVALID_HANDLE) IndicatorRelease(m_slow_handle);
      if(m_atr_handle!=INVALID_HANDLE)  IndicatorRelease(m_atr_handle);
      m_fast_handle=INVALID_HANDLE;
      m_slow_handle=INVALID_HANDLE;
      m_atr_handle=INVALID_HANDLE;
     }

   virtual ENUM_ATLAS_SIGNAL Evaluate(double &atr)
     {
      atr=0.0;
      const datetime current_bar=iTime(m_symbol,m_timeframe,0);
      if(current_bar<=0 || current_bar==m_last_bar_time)
         return ATLAS_SIGNAL_NONE;
      m_last_bar_time=current_bar;

      double fast[2],slow[2],atr_buffer[1];
      if(CopyBuffer(m_fast_handle,0,1,2,fast)!=2 ||
         CopyBuffer(m_slow_handle,0,1,2,slow)!=2 ||
         CopyBuffer(m_atr_handle,0,1,1,atr_buffer)!=1)
        {
         PrintFormat("Project Atlas: indicator data unavailable (%d).",GetLastError());
         return ATLAS_SIGNAL_NONE;
        }

      atr=atr_buffer[0];
      // CopyBuffer stores the oldest requested value first: [0]=bar 2, [1]=bar 1.
      if(fast[0]<=slow[0] && fast[1]>slow[1])
         return ATLAS_SIGNAL_BUY;
      if(fast[0]>=slow[0] && fast[1]<slow[1])
         return ATLAS_SIGNAL_SELL;
      return ATLAS_SIGNAL_NONE;
     }
  };

#endif
