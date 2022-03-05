import ccxt
import time
import pandas as pd
import pprint


#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터6까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!


access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경

# binance 객체 생성
binanceX = ccxt.binance(config={
    'apiKey': access, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})


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

#분봉/일봉 캔들 정보를 가져온다 첫번째: 바이낸스 객체, 두번째: 코인 티커, 세번째: 기간 (1d,4h,1h,15m,10m,1m ...)
def GetOhlcv(binance, Ticker, period):
    btc_ohlcv = binance.fetch_ohlcv(Ticker, period)
    df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df


#스탑로스를 걸어놓는다. 해당 가격에 해당되면 바로 손절한다. 첫번째: 바이낸스 객체, 두번째: 코인 티커, 세번째: 손절 수익율 (1.0:마이너스100% 청산, 0.9:마이너스 90%, 0.5: 마이너스 50%)
def SetStopLoss(binance, Ticker, cut_rate):
    # 
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



#시장가 taker 0.04, 지정가 maker 0.02

#시장가 숏 포지션 잡기 
#print(binance.create_market_sell_order(Target_Coin_Ticker, 0.002))

#시장가 롱 포지션 잡기 
#print(binance.create_market_buy_order(Target_Coin_Ticker, 0.001))


#지정가 숏 포지션 잡기 
#print(binance.create_limit_sell_order(Target_Coin_Ticker, abs_amt, entryPrice))

#지정가 롱 포지션 잡기 
#print(binance.create_limit_buy_order(Target_Coin_Ticker, abs_amt, btc_price))


#거래할 코인 티커와 심볼
Target_Coin_Ticker = "BTC/USDT"
Target_Coin_Symbol = "BTCUSDT"



#캔들 정보 가져온다
df_15 = GetOhlcv(binanceX,Target_Coin_Ticker, '15m')

#최근 3개의 종가 데이터
print("Price: ",df_15['close'][-3], "->",df_15['close'][-2], "->",df_15['close'][-1] )
#최근 3개의 5일선 데이터
print("5ma: ",GetMA(df_15, 5, -3), "->",GetMA(df_15, 5, -2), "->",GetMA(df_15, 5, -1))
#최근 3개의 RSI14 데이터
print("RSI14: ",GetRSI(df_15, 14, -3), "->",GetRSI(df_15, 14, -2), "->",GetRSI(df_15, 14, -1))


#최근 5일선 3개를 가지고 와서 변수에 넣어준다.
ma5_before3 = GetMA(df_15, 5, -4)
ma5_before2 = GetMA(df_15, 5, -3)
ma5 = GetMA(df_15, 5, -2)

#20일선을 가지고 와서 변수에 넣어준다.
ma20 = GetMA(df_15, 20, -2)

#RSI14 정보를 가지고 온다.
rsi14 = GetRSI(df_15, 14, -1)



#잔고 데이타 가져오기 
balance = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)
#pprint.pprint(balance)


print(balance['USDT'])
print("Total Money:",float(balance['USDT']['total']))
print("Remain Money:",float(balance['USDT']['free']))



#################################################################################################################
#영상엔 없지만 레버리지를 3으로 셋팅합니다! 필요없다면 주석처리 하세요!
try:
    print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': 3}))
except Exception as e:
    print("error:", e)
#앱이나 웹에서 레버리지를 바뀌면 바뀌니깐 주의하세요!!
#################################################################################################################



amt = 0 #수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1   #레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0 #미 실현 손익..그냥 참고용 

isolated = True #격리모드인지 

#실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
for posi in balance['info']['positions']:
    if posi['symbol'] == Target_Coin_Symbol:
        amt = float(posi['positionAmt'])
        entryPrice = float(posi['entryPrice'])
        leverage = float(posi['leverage'])
        unrealizedProfit = float(posi['unrealizedProfit'])
        isolated = posi['isolated']
        break
        

#################################################################################################################
#영상엔 없지만 격리모드가 아니라면 격리모드로 처음 포지션 잡기 전에 셋팅해 줍니다,.
if isolated == False:
    try:
        print(binanceX.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
    except Exception as e:
        print("error:", e)
#################################################################################################################       

print("amt:",amt)
print("entryPrice:",entryPrice)
print("leverage:",leverage)
print("unrealizedProfit:",unrealizedProfit)

#해당 코인 가격을 가져온다.
coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

#레버리지에 따른 최대 매수 가능 수량  0.5가 50%다 내 총자산의 50%로 비트코인을 얼마나 살수 있는지 알려주는 함수이다.
# round는 반올림 함수이다.
Max_Amount = round(GetAmount(float(balance['USDT']['total']),coin_price,0.5),3) * leverage 

#최대 매수수량의 1%에 해당하는 수량을 구한다.
one_percent_amount = Max_Amount / 100.0

print("one_percent_amount : ", one_percent_amount) 

#첫 매수 비중을 구한다.. 여기서는 5%!
first_amount = one_percent_amount * 5.0

if first_amount < 0.001:
    first_amount = 0.001

print("first_amount : ", first_amount) 


'''
5  + 5
10  + 10
20   + 20
40   + 40
80

'''



#음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
abs_amt = abs(amt)


#0이면 포지션 잡기전
if amt == 0:
    print("-----No Position")

    #5일선이 20일선 위에 있는데 5일선이 하락추세로 꺾였을때 
    if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5 and rsi14 >= 35.0:
        print("sell/shot")

        #모든 주문을 취소합니다. 개별 주문을 취소하는 방법도 있지만 복잡해 지므로 여기서는 심플한 방법을 선택합니다
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        #포지션을 잡습니다! 즉 코인을 매수한다는 이야기입니다.
        print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스를 걸어줍니다.
        SetStopLoss(binanceX,Target_Coin_Ticker,0.5)

    #5일선이 20일선 아래에 있는데 5일선이 상승추세로 꺾였을때 
    if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and rsi14 <= 65.0:
        print("buy/long")

        #모든 주문을 취소합니다. 개별 주문을 취소하는 방법도 있지만 복잡해 지므로 여기서는 심플한 방법을 선택합니다
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        #포지션을 잡습니다! 즉 코인을 매수한다는 이야기입니다.
        print(binanceX.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스를 걸어줍니다.
        SetStopLoss(binanceX,Target_Coin_Ticker,0.5)


    
#0이 아니라면 포지션 잡은 상태
else:

    #음수면 숏 포지션 상태
    if amt < 0:
        print("-----Short Position")

    #양수면 롱 포지션 상태
    else:
        print("-----Long Position")


#지정가 주문이므로 스탑로스가 안걸릴 수도 있다. 다음번 봇이 실행될 때 를 기다리며 스탑로스를 걸어준다!
#맨 마지막에 호출 되며 스탑로스가 걸려있다면 추가 주문이 들어가지 않으니 안심하고 사용하면 된다
SetStopLoss(binanceX,Target_Coin_Ticker,0.5)







