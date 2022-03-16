#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert   


'''
변동성 돌파 전략의 변형 버전입니다.
기본적인 룰은 같습니다.

변동성 돌파를 잘 모르신다면 검색 한번 하고 오심을 추천드려요 

전일 고가와 저가를 빼서 변동폭을 구한뒤 
변동폭 * 0.5 이상 상승하는 시점에 매수를 진행하고

다음날 매도하는 전략입니다.

일단 이 봇은 15분마다 서버에서 돌게 설정할 예정입니다.
응용해서 5분마다 돌리셔도 되고 30분마다 돌리셔도 됩니다.
이는 자유~

시간 정보를 읽어서 아침 9시라면 (서버시간 기준으로는 0시.. 9시간 차이가 나니깐)
가지고 있는 코인 모두를 매도하되 분할 매도 합니다.

그리고 장중에 15분마다 체크하면서
변동성 돌파하는 시점에 코인당 할당된 금액의 30%의 비중으로 첫 매수를 합니다. 
(뭐 사실 그날 추가 매수 계획이 없다면 그냥 100%들어가도 됩니다 이는 알아서 수정하세요)

그 이후 RSI지표가 40이하면서 수익율이 마이너스 3%이상 되면서 아직 비중이 남았다면 물을 타줍니다
(사실 물타는 이 로직은 빼도 됩니다. 제가 변형 한거죠)

TopCoinList를 주석처리 했는데 이부분을 풀어서 거래량이 많은 코인만 대상으로 삼을 수도 있습니다.
현재는 모든 코인 대상으로 체크를 합니다.

최대 코인 개수는 5개로 설정했는데 이 역시 여러분이 바꾸세요

이상 변동성 돌파 전략 봇이었습니다!


현재 코드가 15분봉을 보기에 크론탭에는 일단 아래처럼 15분 마다 동작하게 
등록하면 되지만 어느 캔들(몇분 봉)을 보고 몇 분마다 돌릴지는 여러분 자유입니다.

*/15 * * * * python3 /var/autobot/New_Upbit_DolPa.py

코드를 잘보면 매일 아침 9시에 변동성 돌파 전략에 맞게 모두 분할매도하는 부분이 있으니
따로 9시에 매도 하는 봇을 만들지 않아도 됩니다.
15분마다 도는건 변동성 돌파하는 시점을 잡기 위함입니다.



'''


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
#30이라는 비중으로 들어갑니다. 처음에 100%들어가고 물타는 로직을 빼셔도 무관합니다.
FirstRate = 30.0
#추가 매수할 비중 (퍼센트)
WaterRate = 10.0


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




#시간 정보를 가져옵니다. 봇이 15분마다 돌다가 아침 9시 즉 hour변수가 0이 된다면 매도합니다.
time_info = time.gmtime()
hour = time_info.tm_hour
print(hour)




#거래대금이 많은 탑코인 30개의 리스트
#TopCoinList = myUpbit.GetTopCoinList("day",30)


Tickers = pyupbit.get_tickers("KRW")

for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)

        

        #이미 매수된 코인이다. 
        if myUpbit.IsHasCoin(balances,ticker) == True:
            
            #현재 코인의 총 매수금액
            NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)


            #현재 9시라면 변동성 돌파 전략에 의해 모두 매도 하되 분할 매도 한다. 
            if hour == 0:

                #최대코인매수금액의 1/4보다 작다면 전체 시장가 매도 
                if NowCoinTotalMoney < (CoinMaxMoney / 4.0):
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))
                #최대코인매수금액의 1/4보다 크다면 절반씩 시장가 매도 
                else:
                    #시장가 매도를 한다.
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker) / 2.0)

            #그밖의 경우는 15분봉을 보면서 물을 탑니다 (다음날 아침 9시에 매도가 진행되기에 물타는 로직은 원래 변동성 돌파 전략에는 없지만 그냥 제가 넣은 로직)
            else:
            
                time.sleep(0.05)
                df = pyupbit.get_ohlcv(ticker,interval="minute15") #15분봉 데이타를 가져온다.

                #RSI지표를 구한다.
                rsi_min = myUpbit.GetRSI(df,14,-1)

                #수익율을 구한다.
                revenu_rate = myUpbit.GetRevenueRate(balances,ticker)


                #할당된 최대코인매수금액 대비 매수된 코인 비율
                Total_Rate = NowCoinTotalMoney / CoinMaxMoney * 100.0

                #RSI지표가 40이하면서 수익율이 마이너스 3%이상 나왔고 아직 풀매수가 아니라면 물을 타준다.
                if rsi_min < 40 and revenu_rate < -3.0 and Total_Rate < 100.0:
                    #물탈 돈 만큼 시장가 매수를 한다.
                    balances = myUpbit.BuyCoinMarket(upbit,ticker,WaterEnterMoeny)



        #아직 매수안한 코인
        else:

            #거래량 많은 탑코인 리스트안의 코인이 아니라면 스킵! 탑코인에 해당하는 코인만 이후 로직을 수행한다.
        #    if myUpbit.CheckCoinInList(TopCoinList,ticker) == False:
         #       continue

            print("!!!!! Target Coin!!! :",ticker)
            
            time.sleep(0.05)
            df = pyupbit.get_ohlcv(ticker,interval="day") #일봉 데이타를 가져온다.
            
            #이전 종가가 오늘의 시가..
            #어제의 고가와 저가의 변동폭에 0.5를 곱해서
            #오늘의 시가와 더해주면 목표 가격이 나온다!
            target_price = float(df['close'][-2]) + (float(df['high'][-2]) - float(df['low'][-2])) * 0.5
            
            #현재가
            now_price = float(df['close'][-1])

            print(now_price , " > ", target_price)
            #이를 돌파했다면 변동성 돌파 성공!!
            if now_price >  target_price and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt:
                print("!!!!!!!!!!!!!!!First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
                 #시장가 매수를 한다.
                balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)
                #이렇게 매수했다고 메세지를 보낼수도 있다
                line_alert.SendMessage("BUY Done DolPa Coin : " + ticker)



    except Exception as e:
        print("---:", e)








