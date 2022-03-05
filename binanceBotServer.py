#-*-coding:utf-8 -*-
import ccxt
import time
import pandas as pd
import pprint
import my_key

simpleEnDecrypt = my_key.SimpleEnDecrypt(b'ycJNAQPaDHt8iGpVJ1756CQ3O9ML_OBa0xdguOKsEs0=')

BinanceAccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
BinanceSecretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

binanceCon = ccxt.binance(config = {
    'apiKey': BinanceAccessKey,
    'secret': BinanceSecretKey,
    'enableRateLimit': True,
    'options' : {
        'defaultType' : 'future'
    }
})

#거래할 코인 티커와 심볼
TargetCoinTicker = "BTC/USDT"
TargetCoinSymbol = "BTCUSDT"



#시장가 taker 0.04, 지정가 maker 0.02

#시장가 숏 포지션 잡기 
#print(binance.create_market_sell_order(Target_Coin_Ticker, 0.002))

#시장가 롱 포지션 잡기 
#print(binance.create_market_buy_order(Target_Coin_Ticker, 0.001))


#지정가 숏 포지션 잡기 
#print(binance.create_limit_sell_order(Target_Coin_Ticker, abs_amt, entryPrice))

#지정가 롱 포지션 잡기 
#print(binance.create_limit_buy_order(Target_Coin_Ticker, abs_amt, btc_price))




#rsi 지표 가져오는 함수
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
def GetBB(ohlcv,period,st):
    dic_bb = dict()

    close = ohlcv["close"]

    ma = close.rolling(period).mean()
    sdddev = close.rolling(period).std()

    dic_bb['ma'] = float(ma[st])
    dic_bb['upper'] = float(ma[st]) + 2.0*float(sdddev[st])
    dic_bb['lower'] = float(ma[st]) - 2.0*float(sdddev[st])

    return dic_bb





#분봉/일봉 캔들 정보를 가져온다 첫번째: 바이낸스 객체, 두번째: 코인 티커, 세번째: 기간 (1d,4h,1h,15m,10m,1m ...)
def GetOhlcv(binance, Ticker, period):
    btc_ohlcv = binance.fetch_ohlcv(Ticker, period)
    df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df



#스탑로스를 걸어놓는다. 해당 가격에 해당되면 바로 손절한다. 첫번째: 바이낸스 객체, 두번째: 코인 티커, 세번째: 손절 수익율 (1.0:마이너스100% 청산, 0.9:마이너스 90%, 0.5: 마이너스 50%)
def SetStopLoss(binance, Ticker, cut_rate):
    time.sleep(0.1)
    #주문 정보를 읽어온다.
    orders = binance.fetch_orders(Ticker)

    StopLossOk = False
    for order in orders:

        if order['status'] == "open" and order['type'] == 'stop_market':
            #print(order)
            StopLossOk = True
            break

    #스탑로스 주문이 없다면 주문을 건다!
    if StopLossOk == False:

        time.sleep(10.0)

        #잔고 데이타를 가지고 온다.
        balance = binance.fetch_balance(params={"type": "future"})
        time.sleep(0.1)
                                
        amt = 0
        entryPrice = 0
        leverage = 0
        #평균 매입단가와 수량을 가지고 온다.
        for posi in balance['info']['positions']:
            if posi['symbol'] == Ticker.replace("/", ""):
                entryPrice = float(posi['entryPrice'])
                amt = float(posi['positionAmt'])
                leverage = float(posi['leverage'])


        #롱일땐 숏을 잡아야 되고
        side = "sell"
        #숏일땐 롱을 잡아야 한다.
        if amt < 0:
            side = "buy"

        danger_rate = ((100.0 / leverage) * cut_rate) * 1.0

        #롱일 경우의 손절 가격을 정한다.
        stopPrice = entryPrice * (1.0 - danger_rate*0.01)

        #숏일 경우의 손절 가격을 정한다.
        if amt < 0:
            stopPrice = entryPrice * (1.0 + danger_rate*0.01)

        params = {
            'stopPrice': stopPrice,
            'closePosition' : True
        }

        print("side:",side,"   stopPrice:",stopPrice, "   entryPrice:",entryPrice)
        #스탑 로스 주문을 걸어 놓는다.
        print(binance.create_order(Ticker,'STOP_MARKET',side,abs(amt),stopPrice,params))

        print("####STOPLOSS SETTING DONE ######################")




#구매할 수량을 구한다.  첫번째: 돈(USDT), 두번째:코인 가격, 세번째: 비율 1.0이면 100%, 0.5면 50%
def GetAmount(usd, coin_price, rate):

    target = usd * rate 

    amout = target/coin_price

    if amout < 0.001:
        amout = 0.001

    #print("amout", amout)
    return amout




#거래할 코인의 현재가를 가져온다. 첫번째: 바이낸스 객체, 두번째: 코인 티커
def GetCoinNowPrice(binance,Ticker):
    coin_info = binance.fetch_ticker(Ticker)
    coin_price = coin_info['last'] # coin_info['close'] == coin_info['last'] 

    return coin_price






def ExistOrderSide(binance,Ticker,Side):
    #주문 정보를 읽어온다.
    orders = binance.fetch_orders(Ticker)

    ExistFlag = False
    for order in orders:
        if order['status'] == "open" and order['side'] == Side:
            ExistFlag = True

    return ExistFlag





#3분을 기준으로 한 캔들 정보 가져온다
df3 = GetOhlcv(binanceCon,TargetCoinTicker, '3m')

#최근 3분의 종가 데이터
#최근 3개의 종가 데이터
print("Price: ",df3['close'][-3], "->",df3['close'][-2], "->",df3['close'][-1] )

#최근 3개의 5일선 데이터
print("5ma: ",GetMA(df3, 5, -3), "->",GetMA(df3, 5, -2), "->",GetMA(df3, 5, -1))

#최근 3개의 20일선 데이터
print("20ma: ",GetMA(df3, 20, -3), "->",GetMA(df3, 20, -2), "->",GetMA(df3, 20, -1))


#최근 3개의 RSI7 데이터
print("RSI7: ",GetMA(df3, 7, -3), "->",GetMA(df3, 7, -2), "->",GetMA(df3, 7, -1))

#최근 3개의 RSI14 데이터
print("RSI14: ",GetMA(df3, 14, -3), "->",GetMA(df3, 14, -2), "->",GetMA(df3, 14, -1))

#최근 3개의 RSI24 데이터
print("RSI24: ",GetMA(df3, 24, -3), "->",GetMA(df3, 24, -2), "->",GetMA(df3, 24, -1))


#최근 5일선 3개를 가지고 와서 변수에 넣어준다.
ma5Before3 = GetMA(df3, 5, -4)
ma5Before2 = GetMA(df3, 5, -3)
ma5 = GetMA(df3, 5, -2)

#20일선을 가지고 와서 변수에 넣어준다.
ma20 = GetMA(df3, 20, -2)

#RSI7 정보를 가지고 온다.
rsi7 = GetRSI(df3, 7, -1)
#RSI14 정보를 가지고 온다.
rsi14 = GetRSI(df3, 14, -1)
#RSI24 정보를 가지고 온다.
rsi24 = GetRSI(df3, 24, -1)

#잔고 데이타 가져오기 
balance = binanceCon.fetch_balance(params={"type": "future"})
time.sleep(0.1)

print(balance['USDT'])
print("현재 내 총 자산:",float(balance['USDT']['total']))
print("이거는 뭘 뜻함?:",float(balance['USDT']['free']))


##레버리지를 건드는것은 사이트에서 정해서 건들기###############################################################################################################
# 혹시 모르니 일단 
# 영상엔 없지만 레버리지를 3으로 셋팅합니다! 필요없다면 주석처리 하세요!
# try:
#     print(binanceCon.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': 3}))
# except Exception as e:
#     print("error:", e)
#앱이나 웹에서 레버리지를 바뀌면 바뀌니깐 주의하세요!!
#################################################################################################################



amt = 0 #수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1   #레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0 #미 실현 손익..그냥 참고용

isolated = True #격리모드인지 


#실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
for posi in balance['info']['positions']:
    if posi['symbol'] == TargetCoinSymbol:
        amt = float(posi['positionAmt'])
        entryPrice = float(posi['entryPrice'])
        leverage = float(posi['leverage'])
        unrealizedProfit = float(posi['unrealizedProfit'])
        isolated = posi['isolated']
        break
        

# #################################################################################################################
# #영상엔 없지만 격리모드가 아니라면 격리모드로 처음 포지션 잡기 전에 셋팅해 줍니다,.
# if isolated == False:
#     try:
#         print(binanceCon.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
#     except Exception as e:
#         print("error:", e)
# #################################################################################################################    


print("amt:",amt)
print("entryPrice:",entryPrice)
print("leverage:",leverage)
print("unrealizedProfit:",unrealizedProfit)

#해당 코인 가격을 가져온다.
coinPrice = GetCoinNowPrice(binanceCon, TargetCoinTicker)



#레버리지에 따른 최대 매수 가능 수량
#  이렇게 40%만 설정을 해놓는 이유는 이더리움반 비트코인 반 등 나눠서 매매를 하기 위한것이다.
Max_Amount = round(GetAmount(float(balance['USDT']['total']),coinPrice,1.0),3) * leverage 

#최대 매수수량의 1%에 해당하는 수량을 구한다.
one_percent_amount = Max_Amount / 100.0

print("최대 매수 가능 수량의 1% :  ", one_percent_amount) 

#첫 매수 비중을 구한다..
# 근데 나는 첫 매수를 100%로 할꺼다 시드 머니가 작으니까
firstAmount = one_percent_amount * 100.0

if firstAmount < 0.001:
    firstAmount = 0.001

print("첫 매수할 양 : ", firstAmount) 


#음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
absAmt = abs(amt)
print("현재 내가 매수한 양 : ", absAmt)

#타겟 레이트 0.001 
target_rate = 0.001
#타겟 수익율 0.1%
target_revenue_rate = target_rate * 100.0

#스탑로스 비율을 설정합니다. 0.5면 50% 0.1이면 10%입니다.
#이 것도 물타기 비율 처럼 매수 비중에 따라 조절할 수도 있겠죠?
StopLossRate = 0.1

# 0이면 포지션 잡기전
# 포지션을 잡아 수익을 만들 로직
# if amt == 0:
#     print("포지션을 잡아 수익을 만들겠습니다.")

# 우선 밑에서 사서 올랐을때 파는 전략부터 구현을 하도록 하겠습니다.
if ma5 < ma20:
    print("20일선 밑에서 진행")
    if rsi7 <= 35.0 and rsi14 <= 35.0 and rsi24 <= 40.0 and rsi7 < rsi14 and rsi14 < rsi24:
        print("매수 진행")

        #주문 취소후
        binanceCon.cancel_all_orders(TargetCoinTicker)
        time.sleep(0.1)

        #해당 코인 가격을 가져온다.- 지정 가격 주문에만 필요하다.
        coin_price = GetCoinNowPrice(binanceCon, TargetCoinTicker)

        print("매수 진행",binanceCon.create_market_buy_order(TargetCoinTicker, firstAmount))

        #스탑 로스 설정을 건다.
        SetStopLoss(binanceCon,TargetCoinTicker,StopLossRate)

elif ma5 > ma20:
    print("20일선 위에서 진행")
    if rsi7 > rsi14 and rsi14 > rsi24 and rsi7 >= 60.0 and rsi14 >= 60.0:
        print("매도 진행")

        #주문 취소후
        binanceCon.cancel_all_orders(TargetCoinTicker)
        time.sleep(0.1)

        #해당 코인 가격을 가져온다.
        coin_price = GetCoinNowPrice(binanceCon, TargetCoinTicker)

        #시장가 숏 포지션 잡기 - 매도가 곧 숏 포지션 잡는 것
        print("매도 진행",binanceCon.create_market_sell_order(TargetCoinTicker, absAmt))

        #스탑 로스 설정을 건다.
        SetStopLoss(binanceCon,TargetCoinTicker,StopLossRate)



































