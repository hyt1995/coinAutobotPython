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

#레버리지에 따른 최대 매수 가능 수량
Max_Amount = round(GetAmount(float(balance['USDT']['total']),coin_price,0.5),3) * leverage 

#최대 매수수량의 1%에 해당하는 수량을 구한다.
one_percent_amount = Max_Amount / 100.0

print("one_percent_amount : ", one_percent_amount) 

#첫 매수 비중을 구한다.. 여기서는 5%!
first_amount = one_percent_amount * 5.0

if first_amount < 0.001:
    first_amount = 0.001

print("first_amount : ", first_amount) 




#음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
abs_amt = abs(amt)

#타겟 레이트 0.001 
target_rate = 0.001
#타겟 수익율 0.1%
target_revenue_rate = target_rate * 100.0


#########################미션 수행#################################
#스탑로스 비율설정 0.5는 원금의 마이너스 50%를 의미한다. 0.1은 마이너스 10%
#맨 처음에는 적은 비중이 들어가므로 스탑로스를 0.9로 셋팅하는 것도 나쁘지 않으 듯 합니다.
stop_loass_rate = 0.5


#0이면 포지션 잡기전
if amt == 0:
    print("-----------------------------No Position---------------------------------")



    #5일선이 20일선 위에 있는데 5일선이 하락추세로 꺾였을때 and RSI지표가 35 이상일때 숏 떨어질거야 를 잡는다.
    if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5 and rsi14 >= 35.0:
        print("sell/short")
        #주문 취소후
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        #해당 코인 가격을 가져온다.
        coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

        #숏 포지션을 잡는다
        print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스 설정을 건다.
        SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행




    #5일선이 20일선 아래에 있는데 5일선이 상승추세로 꺾였을때 and RSI지표가 65 이하일때  롱 오를거야 를 잡는다.
    if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and rsi14 <= 65.0:
        print("buy/long")
        #주문 취소후
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)
        
        #해당 코인 가격을 가져온다.
        coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

        #롱 포지션을 잡는다
        print(binanceX.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스 설정을 건다.
        SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행


    
#0이 아니라면 포지션 잡은 상태
else:
    print("------------------------------------------------------")

    #현재까지 구매한 퍼센트! 현재 보유 수량을 1%의 수량으로 나누면 된다.
    buy_percent = abs_amt / one_percent_amount
    print("Buy Percent : ", buy_percent)



    #수익율을 구한다!
    revenue_rate = (coin_price - entryPrice) / entryPrice * 100.0
    #단 숏 포지션일 경우 수익이 나면 마이너스로 표시 되고 손실이 나면 플러스가 표시 되므로 -1을 곱하여 바꿔준다.
    if amt < 0:
        revenue_rate = revenue_rate * -1.0

    #레버리지를 곱한 실제 수익율
    leverage_revenu_rate = revenue_rate * leverage

    print("Revenue Rate : ", revenue_rate,", Real Revenue Rate : ", leverage_revenu_rate)



    #손절 마이너스 수익율을 셋팅한다.
    danger_rate = -5.0
    #레버리지를 곱한 실제 손절 할 마이너스 수익율
    leverage_danger_rate = danger_rate * leverage

    print("Danger Rate : ", danger_rate,", Real Danger Rate : ", leverage_danger_rate)




    '''
    5  + 5
    10  + 10
    20   + 20
    40   + 40
    80  + 20

    '''

    #추격 매수 즉 물 탈 마이너스 수익율을 셋팅한다.
    water_rate = -1.0

    ###########미션응용??###############
    #보유 비중에 따라 스탑로스를 다르게 걸 수도 있겠죠?
    #적은 비중이라면 스탑로스를 멀게 (0.9, 90%) 많은 비중이라면 스탑로스를 가깝게 (0.1, 10%) 하는 것도 하나의 전략이 됩니다.
    if buy_percent <= 5.0:
        water_rate = -0.5 
        stop_loass_rate = 0.9 #미션 응용
    elif buy_percent <= 10.0:
        water_rate = -1.0 
        stop_loass_rate = 0.7 #미션 응용
    elif buy_percent <= 20.0:
        water_rate = -2.0 
        stop_loass_rate = 0.5  #미션 응용
    elif buy_percent <= 40.0:
        water_rate = -3.0 
        stop_loass_rate = 0.2  #미션 응용
    elif buy_percent <= 80.0:
        water_rate = -5.0 
        stop_loass_rate = 0.1  #미션 응용


    #레버리지를 곱한 실제 물 탈 마이너스 수익율
    leverage_danger_rate = water_rate * leverage

    print("Water Rate : ", water_rate,", Real Water Rate : ", leverage_danger_rate)




    #음수면 숏 포지션 상태
    if amt < 0:
        print("-----Short Position")

        #롱 포지션을 잡을만한 상황!!!!
        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:
            #수익이 났다!!! 숏 포지션 종료하고 롱 포지션도 잡아주자!
            if revenue_rate >= target_revenue_rate:

                #주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                
                #해당 코인 가격을 가져온다.
                coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #롱 포지션을 잡는다
                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs_amt + first_amount, coin_price))

                #스탑 로스 설정을 건다.
                SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행
            



        #영상에서 빠져있는 중요한 부분!!! 숏인 상태에서는 숏을 잡을 만한 상황에서 물을 타야 겠죠?
        #즉 5일 선이 20일 선 위에 있고 하락추세로 꺾였을 때 물을 탑니다.
        #숏 포지션을 잡을만한 상황!!!!
        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:
            #물탈 수량 
            water_amount = abs_amt

            if Max_Amount < abs_amt + water_amount:
                water_amount = Max_Amount - abs_amt

            #물탈 마이너스 수익율 보다 내 수익율이 작다면 물을 타자!!
            if revenue_rate <= water_rate and Max_Amount >= abs_amt + water_amount:

                #주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                
                #해당 코인 가격을 가져온다.
                coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #숏 포지션을 잡는다
                print(binanceX.create_limit_sell_order(Target_Coin_Ticker, water_amount, coin_price))

                #스탑 로스 설정을 건다.
                SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행

           


        #내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:

            #주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
                
            #해당 코인 가격을 가져온다.
            coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

            #롱 포지션을 잡는다
            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))

            #스탑 로스 설정을 건다.
            SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행


        


    #양수면 롱 포지션 상태
    else:
        print("-----Long Position")


        #숏 포지션을 잡을만한 상황!!!!
        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:
            #수익이 났다!!! 롱 포지션 종료하고 숏 포지션도 잡아주자!
            if revenue_rate >= target_revenue_rate:

                #주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                
                #해당 코인 가격을 가져온다.
                coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #숏 포지션을 잡는다
                print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs_amt + first_amount, coin_price))

                #스탑 로스 설정을 건다.
                SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행
            


        #영상에서 빠져있는 중요한 부분!!! 롱인 상태에서는 롱을 잡을 만한 상황에서 물을 타야 겠죠?
        #즉 5일 선이 20일 선 아래에 있고 상승추세로 꺾였을 때 물을 탑니다.
        #롱 포지션을 잡을만한 상황!!!!
        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:
            #물탈 수량 
            water_amount = abs_amt

            if Max_Amount < abs_amt + water_amount:
                water_amount = Max_Amount - abs_amt

            #물탈 마이너스 수익율 보다 내 수익율이 작다면 물을 타자!!
            if revenue_rate <= water_rate and Max_Amount >= abs_amt + water_amount:

                #주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                
                #해당 코인 가격을 가져온다.
                coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #롱 포지션을 잡는다
                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, water_amount, coin_price))

                #스탑 로스 설정을 건다.
                SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행

           


        #내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:

            #주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
                
            #해당 코인 가격을 가져온다.
            coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

            #숏 포지션을 잡는다
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))

            #스탑 로스 설정을 건다.
            SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행



#지정가 주문만 있기 때문에 혹시나 스탑로스가 안걸릴 수 있어서 마지막에 한번 더 건다
#해당 봇이 서버에서 주기적으로 실행되기 때문에 실행 될때마다 체크해서 걸어 줄 수 있다.
#스탑 로스 설정을 건다.
if amt != 0: #포지션이 있을때만 스탑로스를 건다
    SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate) #미션 수행







