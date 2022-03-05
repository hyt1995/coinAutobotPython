import pyupbit
import pandas as pd


access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경

upbit = pyupbit.Upbit(access, secret) #업비트 객체를 만듭니다.

#RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetRSI(ohlcv,period,st):
    ohlcv["close"] = ohlcv["close"]
    delta = ohlcv["close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    RS = _gain / _loss
    return float(pd.Series(100 - (100 / (1 + RS)), name="RSI").iloc[st])

#이동평균선 수치를 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetMA(ohlcv,period,st):
    close = ohlcv["close"]
    ma = close.rolling(period).mean()
    return float(ma[st])


#비트코인의 일봉(캔들) 정보를 가져온다.  
df = pyupbit.get_ohlcv("KRW-BTC",interval="minute240")

#RSI지표를 가져와 봅니다.
rsi14_yesterday = GetRSI(df,14,-2)
rsi14_today = GetRSI(df,14,-1)

print("BTC_BOT_WORKING")
print("YESTERDAY RSI:", rsi14_yesterday , "NOW RSI:", rsi14_today)

#20일 이동평균선을 가져와 봅니다.
ma20_before2 = GetMA(df,20,-3)
ma20_before = GetMA(df,20,-2)
ma20_now = GetMA(df,20,-1)

print("-------------MA CHECK---------------")
print(ma20_before2, ma20_before, ma20_now)
print("------------------------------------")

#RSI지표가 30이하라면
if rsi14_today <= 30:
    #비트코인을 5천원씩 시장가로 매수합니다!
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!IN")
    print(upbit.buy_market_order("KRW-BTC",5000))


