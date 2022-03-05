#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

#내가 매수할 총 코인 개수
MaxCoinCnt = 30.0

#처음 매수할 비중(퍼센트)
FirstRate = 10.0
#추가 매수할 비중 (퍼센트)
WaterRate = 5.0

#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()

TotalMoeny = myUpbit.GetTotalMoney(balances) #총 원금
TotalRealMoney = myUpbit.GetTotalRealMoney(balances) #총 평가금액

#내 총 수익율
TotalRevenue = (TotalRealMoney - TotalMoeny) * 100.0/ TotalMoeny


#TotalMoney = TotalMoney / 5.0 이런식으로 총 원금의 1/5만 단타를 치겠다 설정할 수도 있습니다.
#코인당 매수할 최대 매수금액
CoinMaxMoney = TotalMoeny / MaxCoinCnt


#처음에 매수할 금액 
FirstEnterMoney = CoinMaxMoney / 100.0 * FirstRate 

#그 이후 매수할 금액 
WaterEnterMoeny = CoinMaxMoney / 100.0 * WaterRate

print("-----------------------------------------------")
print ("Total Money:", myUpbit.GetTotalMoney(balances))
print ("Total Real Money:", myUpbit.GetTotalRealMoney(balances))
print ("Total Revenue", TotalRevenue)
print("-----------------------------------------------")
print ("CoinMaxMoney : ", CoinMaxMoney)
print ("FirstEnterMoney : ", FirstEnterMoney)
print ("WaterEnterMoeny : ", WaterEnterMoeny)



#거래대금이 많은 탑코인 30개의 리스트
TopCoinList = myUpbit.GetTopCoinList("day",20)

#구매 제외 코인 리스트
OutCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL','KRW-BTC']

#나의 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-"DOT']


Tickers = pyupbit.get_tickers("KRW")


for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)
  
  
        #영상엔 없지만 이부분이 있어야 이미 매수한 코인이라면 단타로 사지 않는다.
        if myUpbit.IsHasCoin(balances,ticker) == True:
            continue


        #거래량 많은 탑코인 리스트안의 코인이 아니라면 스킵! 탑코인에 해당하는 코인만 이후 로직을 수행한다.
        if myUpbit.CheckCoinInList(TopCoinList,ticker) == False:
            continue
        #위험한 코인이라면 스킵!!!
        if myUpbit.CheckCoinInList(OutCoinList,ticker) == True:
            continue
        #나만의 러블리만 사겠다! 그 이외의 코인이라면 스킵!!!
         #if CheckCoinInList(LovelyCoinList,ticker) == False:
        #    continue

        print("!!!!! Target Coin!!! :",ticker)


            
        time.sleep(0.05)
        df_1 = pyupbit.get_ohlcv(ticker,interval="minute1") #1분봉 데이타를 가져온다.


         #1분봉 기준 5일선 값을 구한다.
        ma5_before3 = myUpbit.GetMA(df_1,5,-4)
        ma5_before2 = myUpbit.GetMA(df_1,5,-3)
        ma5 = myUpbit.GetMA(df_1,5,-2)

        #1분봉 기준 20일선 값을 구한다.
        ma20 = myUpbit.GetMA(df_1,20,-2)

        print("ma20 :", ma20)
        print("ma5 :", ma5 , " <- ", ma5_before2, " <- ", ma5_before3)

        rsi1_min = myUpbit.GetRSI(df_1,14,-1)
        print("-rsi1_min:", rsi1_min)

        #5일선이 20일선 밑에 있을 때 5일선이 상승추세로 꺽이면 매수를 진행하자!!
        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt  :
            print("!!!!!!!!!!!!!!!DANTA DANTA First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
            #영상엔 없지만 지정가 주문을 걸기 전에 이전 주문들을 취소해야 된다.
            myUpbit.CancelCoinOrder(upbit,ticker)

            #시장가 매수를 한다.
            balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

            
            #평균매입단가와 매수개수를 구해서 0.5% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
            avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
            coin_volume = upbit.get_balance(ticker)

            #다음 강의에서 나오지만 수익율은 0.2%가 아니라 0.5%로 변경하는 걸 추천드려요! 이렇게요
            avgPrice *= 1.005
            #지정가 매도를 한다.
            myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)



        #1분봉 기준으로 30이하일때 매수를 한다.
        if rsi1_min < 30.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
            print("!!!!!!!!!!!!!!!DANTA DANTA RSI First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
            #영상엔 없지만 지정가 주문을 걸기 전에 이전 주문들을 취소해야 된다.
            myUpbit.CancelCoinOrder(upbit,ticker)
            
            #시장가 매수를 한다.
            balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

            #평균매입단가와 매수개수를 구해서 0.5% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
            avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
            coin_volume = upbit.get_balance(ticker)

            #다음 강의에서 나오지만 수익율은 0.2%가 아니라 0.5%로 변경하는 걸 추천드려요! 이렇게요
            avgPrice *= 1.005

            #지정가 매도를 한다.
            myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)

            

    except Exception as e:
        print("error:", e)



























