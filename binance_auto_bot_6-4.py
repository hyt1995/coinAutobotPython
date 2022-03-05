import ccxt
import time
import pandas as pd
import pprint


#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터6까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!







#  15분마다 파일을 실행을 시키는 이유 
# 내가 15분봉을 가져오기 때문이다.
#목표가 5분봉이기 때문에 5분마다 실행을 시켜도 될듯하다.


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
target_rate = 0.001 # 0.1%를 말하는 거다 %는 100을 곱해야하니께
#타겟 수익율 0.1% 단타를 친다면 0.1% 만 먹고 떨어지겠다는 뜻
target_revenue_rate = target_rate * 100.0


#0이면 포지션 잡기전
if amt == 0:
    print("-----------------------------No Position---------------------------------")



    #5일선이 20일선 위에 있는데 5일선이 하락추세로 꺾였을때 and RSI지표가 35 이상일때 숏 떨어질거야 를 잡는다.
    if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5 and rsi14 >= 35.0:
        print("sell/short")
        #주문 취소후
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        #해당 코인 가격을 가져온다. 시세 변하기 전에 다시 시장가로 가져와서 여기를 시장가로 변경해서 작성
        coin_price = GetCoinNowPrice(binanceX, Target_Coin_Ticker)

        #숏 포지션을 잡는다
        print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스 설정을 건다.
        SetStopLoss(binanceX,Target_Coin_Ticker,0.5)



### 여기까지 일단 옮겨놓긴는 했다.    testbinanve.py에 여기 밑에서부터 다시 내것으로 옮겨서 작성을 하면 된다. 
### 확실히 코드 작성을 해봐야 머릿속에 들어오는것 같다.





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
        SetStopLoss(binanceX,Target_Coin_Ticker,0.5)


    
#0이 아니라면 포지션 잡은 상태
else:
    print("------------------------------------------------------")

    #현재까지 구매한 퍼센트! 현재 보유 수량을 1%의 수량으로 나누면 된다.
    # 아 이거는 한번 돌려봐야할꺼 같은디???
    buy_percent = abs_amt / one_percent_amount
    print("Buy Percent : ", buy_percent)



    #수익율을 구한다!
    revenue_rate = (coin_price - entryPrice) / entryPrice * 100.0
    #단 숏 포지션일 경우 수익이 나면 마이너스로 표시 되고 손실이 나면 플러스가 표시 되므로 -1을 곱하여 바꿔준다.
    if amt < 0:
        revenue_rate = revenue_rate * -1.0

# 현재 코인 가격을 내가 매입한 단가로 나누고 그걸 내가 매입한 단가로 다시 나누면 현재 수익율이 나오지만
# 여기는 선물 거래기 때문에 레버리지를 곱해야 실제 수익률과 손해율이 나온다. 
    #레버리지를 곱한 실제 수익율
    leverage_revenu_rate = revenue_rate * leverage

    print("Revenue Rate : ", revenue_rate,", Real Revenue Rate : ", leverage_revenu_rate)



    #손절 마이너스 수익율을 셋팅한다.
    # -5%를 뜻한다 
    # 5% 떨어지면 손절을 하겠다는 의미다.
    danger_rate = -5.0
    #레버리지를 곱한 실제 손절 할 마이너스 수익율
    # 실제로 날라가는 금액 - 손해율 * 레버리지  - 5%손해면 레버리지가 10일때 내 원금의 50%가 날라간다고 생각하면 된다. 
    leverage_danger_rate = danger_rate * leverage

    print("Danger Rate : ", danger_rate,", Real Danger Rate : ", leverage_danger_rate)




    '''
    5  + 5
    10  + 10
    20   + 20
    40   + 40
    80  + 20

애매하게 물을 타면 별로 소용이 없다
그래서 물을탈 비중을 좀 늘려줘야 매입단가가 많이 낮아지고 차트가 흔들릴때 
수익을 낼 확률이 높아집니다.




    '''
   #  target_revenue_rate 로 0.1%수익이 나지 않으면 팔지 않고 물을 타겟다는 것다.
    #추격 매수 즉 물 탈 마이너스 수익율을 셋팅한다.


#     애매하게 물을 타면 별로 소용이 없다
# 그래서 물을탈 비중을 좀 늘려줘야 매입단가가 많이 낮아지고 차트가 흔들릴때 
# 수익을 낼 확률이 높아집니다.



    water_rate = -1.0

    if buy_percent <= 5.0:
        water_rate = -0.5
    elif buy_percent <= 10.0:
        water_rate = -1.0
    elif buy_percent <= 20.0:
        water_rate = -2.0
    elif buy_percent <= 40.0:
        water_rate = -3.0
    elif buy_percent <= 80.0:  # 내원금의 100%까지 물을 탈려면 추가
        water_rate = -5.0


    #레버리지를 곱한 실제 물 탈 마이너스 수익율
    #여기도 위에처럼 레버리지를 곱해야한다. 1%고 레버리지가 10 일때 내원금의 10%를 잃었을때 물을 타는 구조다.
    leverage_danger_rate = water_rate * leverage

    print("Water Rate : ", water_rate,", Real Water Rate : ", leverage_danger_rate)


#문제가 차트가 마음대로 움직여주지 않기때문에 그걸 대비해서도 생각을 해야하는데
# 5일선이 20일선 위에 있을때 밑으로 꺾였음에도 계속 올라가는것도 대비 
#           - 차트를 보고 RSI를 분석해서 어떤 상황에서 꺾였음에도 위로 올라가는지
#               꺾였음에도 올라갈때 몇%가 손해일때 다시 손절하고 다시 롱을 살건지  
#               아니면 손절하고 사지 말고 기다렸다가 최고 위에 있을때 숏을 다시 잡을지
# 5일선이 20일선 아래에 있을때 위로 꺾였음에도 계속 내려가는 것도 대비 



#### !!!!!!!꺾였을때도 실제로는 가격이 왔다갔다한다.
# #### !!!!!!!  꺾였을대 스케줄 프로그램이 실행되는 시간을 변경해서 실시간으로 확인을 할건지
# #### !!!!!!!   확인 후에 특정 조건일때 롱이나 숏을 잡을 건지 팔지 말고 있다가 봉이 변경 되서 하락인지 상승인지 
# #### !!!!!!!    결정되면 그때 다시 숏이나 롱을 잡을 건지 결정을 해야한다.

## 대부분 RSI가 떨어지지 않으면 다시 위로 올라가는 것 같다.
### RSI지표를 추가한후 RSI지표 후에 물을 타는 로직을 추가하면 될꺼 같다.

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
                # 현재 내 포지션을 반대로 잡기 위해 롱을 잡았으면 숏을 잡을때 내가 산 코인(abs_amt) + 내가 설정한 코인 수량(first_amount)
                # 으로 포지션을 반대로 잡는다.
                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs_amt + first_amount, coin_price))

                #스탑 로스 설정을 건다.
                SetStopLoss(binanceX,Target_Coin_Ticker,0.5)
            



# 물탈 라인도 너무 넓게 잡으면 5일선과 20일선이 왔다갔다해도 전혀 판매를 하지 않는다.

        #영상에서 빠져있는 중요한 부분!!! 숏인 상태에서는 숏을 잡을 만한 상황에서 물을 타야 겠죠?
        #즉 5일 선이 20일 선 위에 있고 하락추세로 꺾였을 때 물을 탑니다.
        #숏 포지션을 잡을만한 상황!!!!
        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:
            #물탈 수량  - 이 로직땜시 내 원금의 80%이상 물을 타는게 안된다.
            water_amount = abs_amt
# 내가 80%만큼 물을 탔고 하지만 20만큼 더 물을 탈거라는 로직이다.
#100(Max_Amount)에서 80(abs_amt)을 빼면 20이다 20만큼 물을 타겠다는 거다
#그러면 이제 100%까지 물을 타게 되는거다.
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
                SetStopLoss(binanceX,Target_Coin_Ticker,0.5)

           

#내가 물을 100%까지 타면 여기서 손절을 하지 않는다.
# 그래서 100%까지 다 물을 타면 그때 이로직에 따라 절반을 손절을 하게 된다.
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
            SetStopLoss(binanceX,Target_Coin_Ticker,0.5)


        


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
                SetStopLoss(binanceX,Target_Coin_Ticker,0.5)
            


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
                SetStopLoss(binanceX,Target_Coin_Ticker,0.5)

           


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
            SetStopLoss(binanceX,Target_Coin_Ticker,0.5)



#지정가 주문만 있기 때문에 혹시나 스탑로스가 안걸릴 수 있어서 마지막에 한번 더 건다
#해당 봇이 서버에서 주기적으로 실행되기 때문에 실행 될때마다 체크해서 걸어 줄 수 있다.
#스탑 로스 설정을 건다.
SetStopLoss(binanceX,Target_Coin_Ticker,0.5)







