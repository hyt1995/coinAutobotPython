#-*-coding:utf-8 -*-
import pyupbit
import time
import pandas as pd
import numpy

from cryptography.fernet import Fernet

'''
여기에 업비트 봇에 사용될 함수들을 추가하세요!!
'''

#암호화 복호화 클래스
class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou


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

#볼린저 밴드를 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
#차트와 다소 오차가 있을 수 있습니다.
def GetBB(ohlcv,period,st):
    dic_bb = dict()

    ohlcv = ohlcv[::-1]
    ohlcv = ohlcv.shift(st + 1)
    close = ohlcv["close"].iloc[::-1]

    unit = 2.0
    bb_center=numpy.mean(close[len(close)-period:len(close)])
    band1=unit*numpy.std(close[len(close)-period:len(close)])

    dic_bb['ma'] = float(bb_center)
    dic_bb['upper'] = float(bb_center + band1)
    dic_bb['lower'] = float(bb_center - band1)

    return dic_bb


#일목 균형표의 각 데이타를 리턴한다 첫번째: 분봉/일봉 정보, 두번째: 기준 날짜
def GetIC(ohlcv,st):

    high_prices = ohlcv['high']
    close_prices = ohlcv['close']
    low_prices = ohlcv['low']


    nine_period_high =  ohlcv['high'].shift(-2-st).rolling(window=9).max()
    nine_period_low = ohlcv['low'].shift(-2-st).rolling(window=9).min()
    ohlcv['conversion'] = (nine_period_high + nine_period_low) /2
    
    period26_high = high_prices.shift(-2-st).rolling(window=26).max()
    period26_low = low_prices.shift(-2-st).rolling(window=26).min()
    ohlcv['base'] = (period26_high + period26_low) / 2
    
    ohlcv['sunhang_span_a'] = ((ohlcv['conversion'] + ohlcv['base']) / 2).shift(26)
    
    
    period52_high = high_prices.shift(-2-st).rolling(window=52).max()
    period52_low = low_prices.shift(-2-st).rolling(window=52).min()
    ohlcv['sunhang_span_b'] = ((period52_high + period52_low) / 2).shift(26)
    
    
    ohlcv['huhang_span'] = close_prices.shift(-26)


    nine_period_high_real =  ohlcv['high'].rolling(window=9).max()
    nine_period_low_real = ohlcv['low'].rolling(window=9).min()
    ohlcv['conversion'] = (nine_period_high_real + nine_period_low_real) /2
    
    period26_high_real = high_prices.rolling(window=26).max()
    period26_low_real = low_prices.rolling(window=26).min()
    ohlcv['base'] = (period26_high_real + period26_low_real) / 2
    


    
    dic_ic = dict()

    dic_ic['conversion'] = ohlcv['conversion'].iloc[st]
    dic_ic['base'] = ohlcv['base'].iloc[st]
    dic_ic['huhang_span'] = ohlcv['huhang_span'].iloc[-27]
    dic_ic['sunhang_span_a'] = ohlcv['sunhang_span_a'].iloc[-1]
    dic_ic['sunhang_span_b'] = ohlcv['sunhang_span_b'].iloc[-1]


  

    return dic_ic




#MACD의 12,26,9 각 데이타를 리턴한다 첫번째: 분봉/일봉 정보, 두번째: 기준 날짜
def GetMACD(ohlcv,st):
    macd_short, macd_long, macd_signal=12,26,9

    ohlcv["MACD_short"]=ohlcv["close"].ewm(span=macd_short).mean()
    ohlcv["MACD_long"]=ohlcv["close"].ewm(span=macd_long).mean()
    ohlcv["MACD"]=ohlcv["MACD_short"] - ohlcv["MACD_long"]
    ohlcv["MACD_signal"]=ohlcv["MACD"].ewm(span=macd_signal).mean() 

    dic_macd = dict()
    
    dic_macd['macd'] = ohlcv["MACD"].iloc[st]
    dic_macd['macd_siginal'] = ohlcv["MACD_signal"].iloc[st]
    dic_macd['ocl'] = dic_macd['macd'] - dic_macd['macd_siginal']

    return dic_macd




#스토캐스틱 %K %D 값을 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetStoch(ohlcv,period,st):

    dic_stoch = dict()

    ndays_high = ohlcv['high'].rolling(window=period, min_periods=1).max()
    ndays_low = ohlcv['low'].rolling(window=period, min_periods=1).min()
    fast_k = (ohlcv['close'] - ndays_low)/(ndays_high - ndays_low)*100
    slow_d = fast_k.rolling(window=3, min_periods=1).mean()

    dic_stoch['fast_k'] = fast_k.iloc[st]
    dic_stoch['slow_d'] = slow_d.iloc[st]

    return dic_stoch


#거래대금이 많은 순으로 코인 리스트를 얻는다. 첫번째 : Interval기간(day,week,minute15 ....), 두번째 : 몇개까지 
def GetTopCoinList(interval,top):
    print("--------------GetTopCoinList Start-------------------")
    Tickers = pyupbit.get_tickers("KRW")
    time.sleep(0.1)
    dic_coin_money = dict()

    for ticker in Tickers:
        print("--------------------------", ticker)
        try:
            time.sleep(0.1)
            df = pyupbit.get_ohlcv(ticker,interval)
            volume_money = (df['close'][-1] * df['volume'][-1]) + (df['close'][-2] * df['volume'][-2])
            #volume_money = float(df['value'][-1]) + float(df['value'][-2]) #거래대금!
            dic_coin_money[ticker] = volume_money
            print(ticker, dic_coin_money[ticker])
           # time.sleep(0.1)

        except Exception as e:
            print("---:",e)

    dic_sorted_coin_money = sorted(dic_coin_money.items(), key = lambda x : x[1], reverse= True)

    coin_list = list()
    cnt = 0
    for coin_data in dic_sorted_coin_money:
        cnt += 1
        if cnt <= top:
            coin_list.append(coin_data[0])
        else:
            break

    print("--------------GetTopCoinList End-------------------")

    return coin_list

#해당되는 리스트안에 해당 코인이 있는지 여부를 리턴하는 함수
def CheckCoinInList(CoinList,Ticker):
    InCoinOk = False
    for coinTicker in CoinList:
        if coinTicker == Ticker:
            InCoinOk = True
            break

    return InCoinOk

#티커에 해당하는 코인의 수익율을 구해서 리턴하는 함수.
def GetRevenueRate(balances,Ticker):
    revenue_rate = 0.0
    for value in balances:
        try:
            realTicker = value['unit_currency'] + "-" + value['currency']
            if Ticker == realTicker:
                time.sleep(0.05)
                nowPrice = pyupbit.get_current_price(realTicker)
                revenue_rate = (float(nowPrice)- float(value['avg_buy_price'])) * 100.0 / float(value['avg_buy_price'])
                break

        except Exception as e:
            print("---:", e)

    return revenue_rate

#티커에 해당하는 코인의 총 매수금액을 리턴하는 함수
def GetCoinNowMoney(balances,Ticker):
    CoinMoney = 0.0
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            CoinMoney = float(value['avg_buy_price']) * (float(value['balance']) + float(value['locked']))
            break
    return CoinMoney

#티커에 해당하는 코인이 매수된 상태면 참을 리턴하는함수
def IsHasCoin(balances,Ticker):
    HasCoin = False
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            HasCoin = True
    return HasCoin

#내가 매수한 (가지고 있는) 코인 개수를 리턴하는 함수
def GetHasCoinCnt(balances):
    CoinCnt = 0
    for value in balances:
        avg_buy_price = float(value['avg_buy_price'])
        if avg_buy_price != 0: #원화, 드랍받은 코인(평균매입단가가 0이다) 제외!
            CoinCnt += 1
    return CoinCnt



#티커에 해당하는 코인의 평균 매입단가를 리턴한다.
def GetAvgBuyPrice(balances, Ticker):
    avg_buy_price = 0
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            avg_buy_price = float(value['avg_buy_price'])
    return avg_buy_price
    
#총 원금을 구한다!
def GetTotalMoney(balances):
    total = 0.0
    for value in balances:
        try:
            ticker = value['currency']
            if ticker == "KRW": #원화일 때는 평균 매입 단가가 0이므로 구분해서 총 평가금액을 구한다.
                total += (float(value['balance']) + float(value['locked']))
            else:
                avg_buy_price = float(value['avg_buy_price'])
                if avg_buy_price != 0 and (float(value['balance']) != 0 or float(value['locked']) != 0):
                    total += (avg_buy_price * (float(value['balance']) + float(value['locked'])))
        except Exception as e:
            print("GetTotalMoney ---:", e)
    return total

#총 평가금액을 구한다!
def GetTotalRealMoney(balances):
    total = 0.0
    for value in balances:

        try:
            ticker = value['currency']
            if ticker == "KRW": #원화일 때는 평균 매입 단가가 0이므로 구분해서 총 평가금액을 구한다.
                total += (float(value['balance']) + float(value['locked']))
            else:
            
                avg_buy_price = float(value['avg_buy_price'])
                if avg_buy_price != 0 and (float(value['balance']) != 0 or float(value['locked']) != 0): #드랍받은 코인(평균매입단가가 0이다) 제외 하고 현재가격으로 평가금액을 구한다,.
                    realTicker = value['unit_currency'] + "-" + value['currency']
                    time.sleep(0.1)
                    nowPrice = pyupbit.get_current_price(realTicker)
                    total += (float(nowPrice) * (float(value['balance']) + float(value['locked'])))
        except Exception as e:
            print("GetTotalRealMoney ---:", e)


    return total



#시장가 매수한다. 2초뒤 잔고 데이타 리스트를 리턴한다.
def BuyCoinMarket(upbit,Ticker,Money):
    time.sleep(0.05)
    print(upbit.buy_market_order(Ticker,Money))

    time.sleep(2.0)
    #내가 가진 잔고 데이터를 다 가져온다.
    balances = upbit.get_balances()
    return balances

#시장가 매도한다. 2초뒤 잔고 데이타 리스트를 리턴한다.
def SellCoinMarket(upbit,Ticker,Volume):
    time.sleep(0.05)
    print(upbit.sell_market_order(Ticker,Volume))

    time.sleep(2.0)
    #내가 가진 잔고 데이터를 다 가져온다.
    balances = upbit.get_balances()
    return balances

#넘겨받은 가격과 수량으로 지정가 매수한다.
def BuyCoinLimit(upbit,Ticker,Price,Volume):
    time.sleep(0.05)
    print(upbit.buy_limit_order(Ticker,pyupbit.get_tick_size(Price),Volume))

#넘겨받은 가격과 수량으로 지정가 매도한다.
def SellCoinLimit(upbit,Ticker,Price,Volume):
    time.sleep(0.05)
    print(upbit.sell_limit_order(Ticker,pyupbit.get_tick_size(Price),Volume))

#해당 코인에 걸어진 매수매도주문 모두를 취소한다.
def CancelCoinOrder(upbit,Ticker):
    orders_data = upbit.get_order(Ticker)
    if len(orders_data) > 0:
        for order in orders_data:
            time.sleep(0.1)
            print(upbit.cancel_order(order['uuid']))

#거래대금 폭발 여부 첫번째: 캔들 정보, 두번째: 이전 5개의 평균 거래량보다 몇 배 이상 큰지
#이전 캔들이 그 이전 캔들 5개의 평균 거래금액보다 몇 배이상 크면 거래량 폭발로 인지하고 True를 리턴해줍니다
#현재 캔들[-1]은 막 시작했으므로 이전 캔들[-2]을 보는게 맞다!
def IsVolumePung(ohlcv,st):

    Result = False
    try:
        avg_volume = (float(ohlcv['volume'][-3]) + float(ohlcv['volume'][-4]) + float(ohlcv['volume'][-5]) + float(ohlcv['volume'][-6]) + float(ohlcv['volume'][-7])) / 5.0
        if avg_volume * st < float(ohlcv['volume'][-2]):
            Result = True
    except Exception as e:
        print("IsVolumePung ---:", e)

    
    return Result
