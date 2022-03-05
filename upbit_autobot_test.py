import pyupbit
import time
import pandas as pd
import pprint

#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터5까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!

access = "xTtpMz4mahonsD8xyMvunWxxTDb8HHSmHWlehPaI"          # 본인 값으로 변경
secret = "bVk6m0xSw6z1Bv8Ew3foNqNEXgG0xpwrKHGeXfCx"          # 본인 값으로 변경

#업비트 객체를 만들어요 액세스 키와 시크릿 키를 넣어서요.
upbit = pyupbit.Upbit(access, secret)

#아래 함수안의 내용은 참고로만 보세요! 제가 말씀드렸죠? 검증된 함수니 안의 내용 몰라도 그냥 가져다 쓰기만 하면 끝!
#RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
# 현재 rsi를 14로 잡는데 7로 잡으면 생각보다 기회가 많기 하다. --- 하지만 분할매수시 비중조절을 잘해야한다.
def GetRSI(ohlcv,period,st):
    #이 안의 내용이 어려우시죠? 넘어가셔도 되요. 우리는 이 함수가 RSI지표를 정확히 구해준다는 것만 알면 됩니다.
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
    #이 역시 이동평균선을 제대로 구해줍니다.
    close = ohlcv["close"]
    ma = close.rolling(period).mean()
    return float(ma[st])

# 볼륨이 거래량이다 그러면 close * volume하면 그날의 거래량이 나온다.

# 거래대금이 많은 순으로 코인명 정리하는 함수
# 모든 코인들 목록 가져오기
Tickers = pyupbit.get_tickers("KRW")
print("여기는 잘가져옴???? :::::", Tickers)

dic_coin_money = dict()

for ticker in Tickers:

    try:
        df = pyupbit.get_ohlcv(ticker, interval="day")
        volume_money = (df["close"][-1] * df["volume"][-1]) + (df["close"][-2] * df["volume"][-2]) 

        dic_coin_money[ticker] = volume_money

        print(ticker, dic_coin_money[ticker])

        time.sleep(0.05) # 반드시!!! 좀 쉬어줘야 데이터를 잘가져온다.
        
    except Exception as e:
        print("코인들 목록, 데이터 가져오는 에러", e)























