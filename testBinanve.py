#-*-coding:utf-8 -*-
import ccxt
import time
import pandas as pd
import pprint
import my_key

simpleEnDecrypt = my_key.SimpleEnDecrypt(b'ycJNAQPaDHt8iGpVJ1756CQ3O9ML_OBa0xdguOKsEs0=')


binance = ccxt.binance(config = {
    'apiKey':  simpleEnDecrypt.decrypt(my_key.binance_access),
    'secret':simpleEnDecrypt.decrypt(my_key.binance_secret),
    'enableRateLimit': True,
    'options' : {
        'defaultType' : 'future'
    }
})

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

#분봉/ 일봉 캔들 정보를 가져오는 함수
def GetOhlcv(binance, Ticker, period):
    btc_ohlcv = binance.fetch_ohlcv(Ticker, period)
    df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df


#이동평균선 수치를 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetMA(ohlcv,period,st):
    close = ohlcv["close"]
    ma = close.rolling(period).mean()
    return float(ma[st])


def GetCoinNowPrice(binance, Ticker):
    coinInfo = binance.fetch_ticker(Ticker)
    coinPrice = coinInfo['last']

    return coinPrice



def GetAmount(usd, coinPrice, rate):
    target = usd * rate
    amount = target/coinPrice

    if amount < 0.001:
        amount = 0.001

    return amount

# 청산을 면하게 하는 함수 스탑로스
def SetStopLoss(binance, Ticker, cutRate):
    time.sleep(0.1)
    # 주문정보를 읽어오는
    orders = binance.fetch_orders(Ticker)

    stopLossOk = False

    for order in orders:

        if order['status'] == "open" and order["type"] == 'stop_market':
            stopLossOk = True
            break

        if stopLossOk == False:

            time.sleep(10.0)
            balance = binance.fetch_balance(params={"type": "future"})
            time.sleep(0.1)

            amt = 0
            entryPrice = 0
            leverage = 0

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

            dangerRate = ((100.0 / leverage) * cutRate) * 1.0

            stopPrice = entryPrice * (1.0 - dangerRate*0.01)

            #숏일 경우의 손절 가격을 정한다.
            if amt < 0:
                stopPrice = entryPrice * (1.0 + dangerRate*0.01)

                
            params = {
            'stopPrice': stopPrice,
            'closePosition' : True
            }

            print("side:",side,"   stopPrice:",stopPrice, "   entryPrice:",entryPrice)
            #스탑 로스 주문을 걸어 놓는다.
            print(binance.create_order(Ticker,'STOP_MARKET',side,abs(amt),stopPrice,params))

            print("####STOPLOSS SETTING DONE ######################")



targetCoinTicker = "BTC/USDT"
targetCoinSymbol = "BTCUSDT"

#캔들 정보를 가져온다.
df1 = GetOhlcv(binance, targetCoinTicker, '1m')
# print("RSI7", GetRSI(df1,7,-1),GetRSI(df1,7,-2),GetRSI(df1,7,-3))
# print("RSI14", GetRSI(df1,14,-1),GetRSI(df1,14,-2),GetRSI(df1,14,-3))
# print("RSI24", GetRSI(df1,24,-1),GetRSI(df1,24,-2),GetRSI(df1,24,-3))

# print("5일선",GetMA(df1, 5,-1), GetMA(df1, 5,-2), GetMA(df1, 5,-3))
# print("20일선",GetMA(df1, 20,-1), GetMA(df1, 20,-2), GetMA(df1, 20,-3))

# print("최근 종가 데이터", df1["close"][-1], df1["close"][-2], df1["close"][-3])

# 내계좌 데이터를 가져온다.
balance = binance.fetch_balance(params={"type":"future"})

time.sleep(0.1)
# print(balance["USDT"])
# print("Total Money:",float(balance['USDT']['total'])) #  내 잔고
# print("Remain Money:",float(balance['USDT']['free'])) # 내가 선물에 쓸수 있는 잔고?


amt = 0 #수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1   #레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0 #미 실현 손익..그냥 참고용 

for posi in balance['info']['positions']:
    if posi['symbol'] == targetCoinSymbol:
        leverage = float(posi['leverage'])
        entryPrice = float(posi['entryPrice'])
        unrealizedProfit = float(posi['unrealizedProfit'])
        amt = float(posi['positionAmt'])


# print("amt:",amt)
# print("entryPrice:",entryPrice) # 평균 매입단가
# print("leverage:",leverage)
# print("unrealizedProfit:",unrealizedProfit)

coinPrice = GetCoinNowPrice(binance, targetCoinTicker)

#현재 내 자산 50%로 구매 가능한 최대 코인 개수
maxAmount = round(GetAmount(float(balance['USDT']['total']), coinPrice, 1),3) * leverage
print("현재 최대 구매 가능 코인 개수 ::: ", maxAmount)


#최대 매수수량의 100%에 해당하는 수량을 구한다.
# 내가 정한 제한 코인 구매개수
onePercentAmount = maxAmount/1.0

print("최대 매수수량의 100%에 해당하는 수량은???? ::: ",  onePercentAmount)

# 구매가능한 전체 코인개수의  50%로에 해당하는 코인을 구매한다.
firtstAmount = onePercentAmount * 5.0


if firtstAmount < 0.001:
    firtstAmount = 0.001

print("첫매수 비중을 위한 :::",  firtstAmount)


# 숏일때는 음수로 들어오기 때문에 절대값으로 변경
absAmt = abs(amt)
# 나의 전략에 필요한 정보를 가져오는 곳
ma5Before3 = GetMA(df1, 5, -4)
ma5Before2 = GetMA(df1, 5, -3)
ma5 = GetMA(df1, 5, -2)
ma20 = GetMA(df1, 20, -2)
rsiSeven = GetRSI(df1, 7, -1)

## 함수부분은 종료

## 이제 실제 전략이 들어가는 부분

targetRate = 0.001 # 0.1%를 말하는 것이다
# 0.1%만 먹고 떨어지겠다는 뜻
targetRevenueRate = targetRate * 100.0




if amt == 0:
    print("아직 코인 구매를 하지 않았을 경우 ---------------------------------------------")

    if ma5 > ma20:
        if ma5Before3 < ma5Before2 and ma5Before2 > ma5 and rsiSeven >= 40:
            # 5일선이 20일선 밑으로 꺽이면서 rsi가 40이하면 매수를 해야한다.
            print("우선 기존에 있던 주문을 취소한다.")
            binance.cancel_all_orders(targetCoinTicker)
            time.sleep(0.1)

            # 현재 코인가격을 가져온다.
            coinPriceCurr = GetCoinNowPrice(binance, targetCoinTicker)
            #숏포지션을 잡는다.
            print(binance, binance.create_market_sell_order(targetCoinTicker, firtstAmount,  coinPriceCurr))

            # 청산을 면하게 하는 스탑로스 설정을 한다.
            SetStopLoss(binance, targetCoinTicker, 0.5)

            #현재 내가 봤을때 요즘 트렌드가 따로 있다.
            # 올라갈때 특징 내려갈때 특징을 잘파악을 해서 수정한 후 돌려야한다.

    if ma5 < ma20:
        if ma5Before3 > ma5Before2 and ma5Before2 < ma5 and rsiSeven <= 65.0:
            print("5일선이 20일선 아래에 있는데 5일선이 상승추세가  됐을때 rsi가 65 이하일대 롱포지션을 잡는다.")
            # 우선 연례행사 기존 주문 취소
            binance.cancel_all_orders(targetCoinTicker)

            #해당 코인 가격을 가져온다.
            coinPriceCurr = GetCoinNowPrice(binance, targetCoinTicker)

            # 현재 5일선이 20일선 밑에 있기 때문에 롱 포지션을 잡아야한다.
            print(binance.create_market_buy_order(targetCoinTicker, firtstAmount, coinPriceCurr))

            # 또 연례행사중 하나인 파산을 막아주는 스탑로스 설정을 거는 것이다.
            SetStopLoss(binance, targetCoinTicker, 0.5)

#물을 타기 위한 코드를 작성하는 곳
else:
    print("0이 아니라 이미 기존 주문이 있는 상태이다.")

    # 현재까지 구매한 퍼센트 현재 보유 수량을 1%의 수량으로 나누면 된다
    buyPercent = absAmt / onePercentAmount
    print("현재까지 구매한 퍼센트를 구하는 곳",   buyPercent)


    #수익율을 구하는 코드를 작성하는 곳 coinPrice-코인가격    entryPrice - 평균매입단가
    revenueRate = (coinPrice - entryPrice)/entryPrice*100.0

    if amt < 0:
        revenueRate = revenueRate * -1.0

# 마진거래기때무에 실질적인 수익율
    leverageRevenueRate = revenueRate*leverage

    print("실질적인 나의 수익율", leverageRevenueRate)

    #나의 손절 수익율 셋팅
    dangerRate = -5.0
    #실제로 날라가는 나의 금액
    leverageDangerRate = dangerRate * leverage
    print("선물거래에서 실제로 날라가는 나의 금액", leverageDangerRate)


    # targetRevenueRate에서 설정한 0.1%수익이 나지 않으면 팔지 않고 물을 타겠다는 뜻이다.
    waterRate = -1.0

    if buyPercent <= 5.0:
        waterRate = -0.5
    elif buyPercent <= 10.0:
        waterRate = -1.0
    elif buyPercent <= 20.0:
        waterRate = -2.0
    elif buyPercent <= 40.0:
        waterRate = -3.0
    elif buyPercent <= 80.0:  # 내원금의 100%까지 물을 탈려면 추가
        waterRate = -5.0

    
    leverageDangerRate = waterRate * leverage
    print("물을 탄 후 내 위험 손절 수익율", leverageDangerRate)

    if amt < 0:
        print("숏포지션을 잡을때 ")