import ccxt
import time
import pandas as pd
import pprint

import myBinance
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)


#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)


# binance 객체 생성
binanceX = ccxt.binance(config={
    'apiKey': Binance_AccessKey, 
    'secret': Binance_ScretKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})




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
Target_Coin_Ticker = "ETH/USDT"
Target_Coin_Symbol = "ETHUSDT"



#캔들 정보 가져온다
df_1 = myBinance.GetOhlcv(binanceX,Target_Coin_Ticker, '1m')

#최근 3개의 종가 데이터
print("Price: ",df_1['close'][-3], "->",df_1['close'][-2], "->",df_1['close'][-1] )
#최근 3개의 5일선 데이터
print("5ma: ",myBinance.GetMA(df_1, 5, -3), "->",myBinance.GetMA(df_1, 5, -2), "->",myBinance.GetMA(df_1, 5, -1))
#최근 3개의 RSI14 데이터
print("RSI14: ",myBinance.GetRSI(df_1, 14, -3), "->",myBinance.GetRSI(df_1, 14, -2), "->",myBinance.GetRSI(df_1, 14, -1))


#최근 5일선 3개를 가지고 와서 변수에 넣어준다.
ma5_before3 = myBinance.GetMA(df_1, 5, -4)
ma5_before2 = myBinance.GetMA(df_1, 5, -3)
ma5 = myBinance.GetMA(df_1, 5, -2)

#20일선을 가지고 와서 변수에 넣어준다.
ma20 = myBinance.GetMA(df_1, 20, -2)

#RSI14 정보를 가지고 온다.
rsi14 = myBinance.GetRSI(df_1, 14, -1)



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
coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

#레버리지에 따른 최대 매수 가능 수량
#  이렇게 50%만 설정을 해놓는 이유는 이더리움반 비트코인 반 등 나눠서 매매를 하기 위한것이다.
Max_Amount = round(myBinance.GetAmount(float(balance['USDT']['total']),coin_price,0.5),3) * leverage 

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

#다음 강의에서 나오지만 수익율은 0.05%가 아니라 0.1%로 변경하는 걸 추천드려요! 이렇게요
#타겟 레이트 0.001 
target_rate = 0.001
#타겟 수익율 0.1%
target_revenue_rate = target_rate * 100.0


#스탑로스 비율을 설정합니다. 0.5면 50% 0.1이면 10%입니다.
#이 것도 물타기 비율 처럼 매수 비중에 따라 조절할 수도 있겠죠?
StopLossRate = 0.5



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
        coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

        #숏 포지션을 잡는다
        print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

        
        #롱 포지션을 잡는다
        print(binanceX.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price * (1.0 - target_rate)))



    #5일선이 20일선 아래에 있는데 5일선이 상승추세로 꺾였을때 and RSI지표가 65 이하일때  롱 오를거야 를 잡는다.
    if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and rsi14 <= 65.0:
        print("buy/long")
        #주문 취소후
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)
        
        #해당 코인 가격을 가져온다.
        coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

        #롱 포지션을 잡는다
        print(binanceX.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price))

        #스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

        
        
        #숏 포지션을 잡는다
        print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price * (1.0 + target_rate)))



    
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

    if buy_percent <= 5.0:
        water_rate = -0.5
    elif buy_percent <= 10.0:
        water_rate = -1.0
    elif buy_percent <= 20.0:
        water_rate = -2.0
    elif buy_percent <= 40.0:
        water_rate = -3.0
    elif buy_percent <= 80.0:
        water_rate = -5.0


    #레버리지를 곱한 실제 물 탈 마이너스 수익율
    leverage_danger_rate = water_rate * leverage

    print("Water Rate : ", water_rate,", Real Water Rate : ", leverage_danger_rate)



    #음수면 숏 포지션 상태
    if amt < 0:
        print("-----Short Position")

        SetPosition = False

        #롱 포지션을 잡을만한 상황!!!!
        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:
            #수익이 났다!!! 숏 포지션 종료하고 롱 포지션도 잡아주자!
            if revenue_rate >= target_revenue_rate:

                #주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                
                #해당 코인 가격을 가져온다.
                coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #롱 포지션을 잡는다
                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs_amt + first_amount, coin_price))

                #스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

                SetPosition = True
            
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
                coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #숏 포지션을 잡는다
                print(binanceX.create_limit_sell_order(Target_Coin_Ticker, water_amount, coin_price))

                #스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

                SetPosition = True

           


        #내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:

            #주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
                
            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

            #롱 포지션을 잡는다
            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))

            #스탑 로스 설정을 건다.
            myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

            SetPosition = True



        if SetPosition == False:
            #주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)

            #잔고 데이타를 다시 가져온다
            time.sleep(0.1)
            balance = binanceX.fetch_balance(params={"type": "future"})


            amt = 0
            entryPrice = 0


            for posi in balance['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol:
                    entryPrice = float(posi['entryPrice'])
                    amt = float(posi['positionAmt'])


            #롱 포지션을 잡는다
            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs(amt), entryPrice * (1.0 - target_rate)))


    #양수면 롱 포지션 상태
    else:
        print("-----Long Position")

        SetPosition = False

        #숏 포지션을 잡을만한 상황!!!!
        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:
            #수익이 났다!!! 롱 포지션 종료하고 숏 포지션도 잡아주자!
            if revenue_rate >= target_revenue_rate:

                #주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                
                #해당 코인 가격을 가져온다.
                coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #숏 포지션을 잡는다
                print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs_amt + first_amount, coin_price))

                #스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

                SetPosition = True
            

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
                coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                #롱 포지션을 잡는다
                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, water_amount, coin_price))

                #스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)

                SetPosition = True

           


        #내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:

            #주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
                
            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

            #숏 포지션을 잡는다
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))

            #스탑 로스 설정을 건다.
            myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)


            SetPosition = True

        if SetPosition == False:
            #주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)

            #잔고 데이타를 다시 가져온다
            time.sleep(0.1)
            balance = binanceX.fetch_balance(params={"type": "future"})


            amt = 0
            entryPrice = 0


            for posi in balance['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol:
                    entryPrice = float(posi['entryPrice'])
                    amt = float(posi['positionAmt'])


            #숏 포지션을 잡는다
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs(amt), entryPrice * (1.0 + target_rate)))





#지정가 주문만 있기 때문에 혹시나 스탑로스가 안걸릴 수 있어서 마지막에 한번 더 건다
#해당 봇이 서버에서 주기적으로 실행되기 때문에 실행 될때마다 체크해서 걸어 줄 수 있다.
#스탑 로스 설정을 건다.
if amt != 0: #포지션이 있을때만 스탑로스를 건다
    myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,StopLossRate)







