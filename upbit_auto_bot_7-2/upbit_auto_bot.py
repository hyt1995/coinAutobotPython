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
MaxCoinCnt = 5.0

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



#거래대금이 많은 탑코인 10개의 리스트
TopCoinList = myUpbit.GetTopCoinList("week",30)

#구매 제외 코인 리스트
OutCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL','KRW-BTC']

#나의 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-"DOT']


Tickers = pyupbit.get_tickers("KRW")


for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)
  

        #이미 매수된 코인이다. 물타기!!
        if myUpbit.IsHasCoin(balances,ticker) == True:
            

            #제외할 코인이라면 스킵!!!
            if myUpbit.CheckCoinInList(OutCoinList,ticker) == True:
                continue

            print("!!!!! Target Coin!!! :",ticker)
            
            time.sleep(0.05)
            df_60 = pyupbit.get_ohlcv(ticker,interval="minute60") #60분봉 데이타를 가져온다.

            #RSI지표를 구한다.
            #제가 현재 캔들을 -1 이 아니라 -2로 
            #이전 캔들을 -2가 아니라 -3으로 수정했습니다. 이유는 https://blog.naver.com/zacra/222567868086 참고하세요!
            rsi60_min_before = myUpbit.GetRSI(df_60,14,-3)
            rsi60_min = myUpbit.GetRSI(df_60,14,-2)

            #수익율을 구한다.
            revenu_rate = myUpbit.GetRevenueRate(balances,ticker)


            time.sleep(0.05)
            #원화 잔고를 가져온다
            won = float(upbit.get_balance("KRW"))
            print("# Remain Won :", won)

            print("------------------------------------")
            print("Coin ticker :",ticker)
            print("- Recently RSI :", rsi60_min_before, " -> ", rsi60_min)
            print("- Now Revenue : ",revenu_rate)
        

            #현재 코인의 총 매수금액
            NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)

            #60분봉 기준 RSI지표 70 이상이면서 수익권일때 분할 매도를 한다.
            if rsi60_min >= 70.0 and revenu_rate >= 1.0:
                print("!!!!!!!!!!!!!!!Revenue Success Sell Coin!!!!!!!!!!!!!!!!!!!!")

                #현재 걸려있는 지정가 주문을 취소한다. 왜? 아래 매수매도 로직이 있으니깐 
                myUpbit.CancelCoinOrder(upbit,ticker)

                #최대코인매수금액의 1/4보다 작다면 전체 시장가 매도 
                if NowCoinTotalMoney < (CoinMaxMoney / 4.0):
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))
                #최대코인매수금액의 1/4보다 크다면 절반씩 시장가 매도 
                else:
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker) / 2.0)

                #팔았으면 원화를 다시 가져올 필요가 있다.
                won = float(upbit.get_balance("KRW"))
               



            #내가 가진 원화가 물탈 돈보다 적다..(원금 바닥) 그런데 수익율이 - 10% 이하다? 그럼 절반 팔아서 물탈돈을 마련하자!
            if won < WaterEnterMoeny and revenu_rate <= -10.0:
                print("!!!!!!!!!!!!!!!No Money Sell Coin Half !!!!!!!!!!!!!!!!!!!!")
                #현재 걸려있는 지정가 주문을 취소한다. 왜? 아래 매수매도 로직이 있으니깐 
                myUpbit.CancelCoinOrder(upbit,ticker)
                #시장가 매도를 한다.
                balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker) / 2.0)



            #할당된 최대코인매수금액 대비 매수된 코인 비율
            Total_Rate = NowCoinTotalMoney / CoinMaxMoney * 100.0

            #60분봉 기준 RSI지표 30 이하에서 빠져나왔을 때
            if rsi60_min_before <= 30.0 and rsi60_min > 30.0:
                #할당된 최대코인매수금액 대비 매수된 코인 비중이 50%이하일때..
                if Total_Rate <= 50.0:
                    print("!!!!!!!!!!!!!!!Water GoGo!!!!!!!!!!!!!!!!!!!!!!")
                    #현재 걸려있는 지정가 주문을 취소한다. 왜? 아래 매수매도 로직이 있으니깐 
                    myUpbit.CancelCoinOrder(upbit,ticker)

                     #시장가 매수를 한다.
                    balances = myUpbit.BuyCoinMarket(upbit,ticker,WaterEnterMoeny)


                #50%를 초과하면
                else:
                    print("!!!!!!!!!!!!!!! Water GoGo But if ",revenu_rate," Under !!!!!!!!!!!!!!!!!!!!!")
                    #수익율이 마이너스 5% 이하 일때만 매수를 진행하여 원금 소진을 늦춘다.
                    if revenu_rate <= -5.0:
                        print("!!!!!!!!!!!!!!!Water GoGo!!!!!!!!!!!!!!!!!!!!!")
                        #현재 걸려있는 지정가 주문을 취소한다. 왜? 아래 매수매도 로직이 있으니깐 
                        myUpbit.CancelCoinOrder(upbit,ticker)

                         #시장가 매수를 한다.
                        balances = myUpbit.BuyCoinMarket(upbit,ticker,WaterEnterMoeny)





        #아직 매수안한 코인
        else:

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
            df_60 = pyupbit.get_ohlcv(ticker,interval="minute60") #60분봉 데이타를 가져온다.


            #RSI지표를 구한다.
            #제가 현재 캔들을 -1 이 아니라 -2로 
            #이전 캔들을 -2가 아니라 -3으로 수정했습니다. 이유는 https://blog.naver.com/zacra/222567868086 참고하세요!
            rsi60_min_before = myUpbit.GetRSI(df_60,14,-3)
            rsi60_min = myUpbit.GetRSI(df_60,14,-2)



            print("------------------------------------")
            print("Coin ticker :",ticker)
            print("- Recently RSI :", rsi60_min_before, " -> ", rsi60_min)


            #60분봉 기준 RSI지표 30 이하에서 빠져나오면서 아직 매수한 코인이 MaxCoinCnt보다 작다면 매수 진행!
            if rsi60_min_before <= 30.0 and rsi60_min > 30.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!!!First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
                 #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)


            time.sleep(0.05)
            df_15 = pyupbit.get_ohlcv(ticker,interval="minute15") #15분봉 데이타를 가져온다.

            #15분봉 기준 5일선 값을 구한다.
            ma5_before3 = myUpbit.GetMA(df_15,5,-4)
            ma5_before2 = myUpbit.GetMA(df_15,5,-3)
            ma5 = myUpbit.GetMA(df_15,5,-2)

            #15분봉 기준 20일선 값을 구한다.
            ma20 = myUpbit.GetMA(df_15,20,-2)

            print("ma20 :", ma20)
            print("ma5 :", ma5 , " <- ", ma5_before2, " <- ", ma5_before3)


            #5일선이 20일선 밑에 있을 때 5일선이 상승추세로 꺽이면 매수를 진행하자!!
            if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!!!DANTA DANTA First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
                #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

                #평균매입단가와 매수개수를 구해서 1% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
                avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
                coin_volume = upbit.get_balance(ticker)

                avgPrice *= 1.01
                #지정가 매도를 한다.
                myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)




            #이부분이 이번 강의에서 추가 되었지만 사실 해당 봇이 1분마다 돌지 않는 한 15분씩 도는 봇에 1분봉을 보는 것은 큰 의미가 없습니다. 이는 이후 강의에서 수정(분리)되니 참고하세요!
            time.sleep(0.05)
            df_1 = pyupbit.get_ohlcv(ticker,interval="minute1") #1분봉 데이타를 가져온다.

            rsi1_min = myUpbit.GetRSI(df_1,14,-1)
            print("-rsi1_min:", rsi1_min)

            #1분봉 기준으로 30이하일때 매수를 한다.
            if rsi1_min < 30.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt:
                print("!!!!!!!!!!!!!!!DANTA DANTA RSI First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
                #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

                #평균매입단가와 매수개수를 구해서 1% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
                avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
                coin_volume = upbit.get_balance(ticker)

                avgPrice *= 1.01

                #지정가 매도를 한다.
                myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)

            

    except Exception as e:
        print("error:", e)



























