#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키


'''
라오어 미국주식 무한매수법을 변형한 코인 무한매수봇
지표 안보고 그냥 비중조절만 하는 약간 무식한 방법??

즉 매일 매일 조금씩 모아가서 물타기 효과! 코스트에버리징 효과를 극대화화는 전략으로
많은 분들이 미국주식 ETF 으로 높은 수익율을 기록하고 있다는 매매전략입니다!



원금을 40으로 나눈다.

1/40을 그냥 산다. 이를 첫 매수 금액이라고 칭하자

해당 봇은 1시간마다 돕니다.

하지만 매일 9시에만 추가매수를 합니다

그런데 왜 1시간마다 도느냐?
그날 장 중에 매도를 하면 최대 매수코인 개수에 미달하게 되고
신규 매수 기회가 생깁니다. 그때 매수(포지션 잡기)를 하기 위함입니다.
즉 현재 매수 코인 개수가 최대 매수 코인 개수보다 작은 상황이라면
1시간 마다 도는 봇이 첫 매수에 들어가게 되는 구조입니다.




평단의 마이너스 5%이상 손실이 난다면 - 그냥 제가 정한 기준입니다. 맘대로 바꾸세요

첫 매수 금액 만큼을 추가 매수한다.

그 밖의 경우는 첫 매수 금액의 절반을 추가 매수한다.

업비트에선 레버리지를 못쓰므로
수익이 3% 이상에 지정가 매도를 걸어 팔아버린다.

다시 처음으로 돌아가 1/40을 산다!


중요한건 업비트 최소 매수금액이 5천원이기에 
최소 1만원 * 40 = 40만원
최소 한 코인당 40만원 이상 할당되어야 이 무한매수법을 실행할 수 있습니다.
따라서 내 원금이 120만원이라면 3개의 코인을 돌릴 수 있다는 점 참고하세요!!

코인 할당금액이 40만원일때
이는 제가 평단 마이너스 5% 이하 일때는 1/40 즉 1만원을 사지만
평단 마이너스 5%보다 위에 있는 경우에는 1/80 즉 5천원을 사야하기 때문입니다.

이게 맘에 들지 않으시다면 평단 마이너스 5%체크하는 로직을 빼시면 됩니다! 
혹은 1%나 10%로 조절도 되겠죠?
혹은 평단 마이너스 20%가 되었다 치면 1/20인 2만원을 매수하게 하는 것도 나쁘지 않을 것 같습니다.


크론탭에 매 1시간마다 실행되게 등록합니다.

0 */1 * * * python3 /var/autobot/New_Binance_Unlimit.py

이런 식으로 등록하면 되지만 마음대로 바꾸세요!

'''


#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)


#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()

TotalMoeny = myUpbit.GetTotalMoney(balances) #총 원금
TotalRealMoney = myUpbit.GetTotalRealMoney(balances) #총 평가금액

#내 총 수익율
TotalRevenue = (TotalRealMoney - TotalMoeny) * 100.0/ TotalMoeny


#내가 매수할 총 코인 개수
#원금이 1백이라 가정하면 최대 2개까지 가능합니다. 한 코인당 40만원..이를 40분할하면 한번에 1만원씩!
#따라서 내 원금을 40만원으로 나누면 가능한 코인 개수가 나옵니다.
MaxCoinCnt = int(TotalMoeny / 400000.0)
print("MaxCoinCnt : ", MaxCoinCnt)

#원금의 1/40은 곧 2.5%를 의미합니다.
#따라서 처음 매수할 비중과 추가매수할 비중 모두 2.5로 셋팅합니다.
#처음 매수할 비중(퍼센트)
FirstRate = 2.5
#추가 매수할 비중 (퍼센트)
WaterRate = 2.5


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





#시간 정보를 가져옵니다. 
#아침 9시에만 코인을 매수(포지션 잡기)를 하기 위해 시간 체크가 필요합니다.
#매일 9시에 한번만 실행되게 봇을 설정해도 되지만 1시간마다 봇을 돌게 해놨습니다.
#이유는 장중에 수익화가 되어 코인이 매도되면 자리가 남기에 코인을 추가 매수하기 위함입니다.
#즉 9시가 아닌 시간에는 추가 매수만 되고(자리가 남았으면) 물타기(기존 매수된 코인을 추가매수)는 막아야 하기에 필요한 시간 정보입니다
time_info = time.gmtime()
hour = time_info.tm_hour
print("HOUR:",hour)




#거래대금이 많은 탑코인 30개의 리스트
TopCoinList = myUpbit.GetTopCoinList("day",30)

#구매 제외 코인 리스트
OutCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL','KRW-BTC']

#나의 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-DOT']


Tickers = pyupbit.get_tickers("KRW")


for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)

          

        ############이미 매수한 코인이다.
        if myUpbit.IsHasCoin(balances,ticker) == True:

            #수익율을 구한다.
            revenu_rate = myUpbit.GetRevenueRate(balances,ticker)
            print("revenu_rate", revenu_rate)

            #물탈 돈의 1/2를 실제로 물탈돈으로 셋팅하지만 
            WaterMoney = WaterEnterMoeny * 0.5

            #수익율이 마이너스 5%보다 작다면 물탈 돈을 온전히 탄다.
            if revenu_rate < -5.0:
                WaterMoney = WaterEnterMoeny

            #최소 주문금액 5천원보다 작으면 5천원으로 맞춰줍니다.
            if WaterMoney < 5000:
                WaterMoney = 5000

                            
            #현재 코인의 총 매수금액
            NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)
            print(CoinMaxMoney, " >", NowCoinTotalMoney)

            #9시에만 추가 매수를 합니다! 1시간마다 봇이 돌기 때문에 이 조건문이 필요!!
            if hour == 0:

                #매수 비중이 남았다면
                if CoinMaxMoney > NowCoinTotalMoney:
                    #이전 지정가 매도 주문을 취소하고 왜냐하면 평단이 변할테니깐 
                    myUpbit.CancelCoinOrder(upbit,ticker)

                    #위에서 구한 물탈 돈으로 시장가 매수를 한다.
                    balances = myUpbit.BuyCoinMarket(upbit,ticker,WaterMoney)

                    #평균매입단가와 매수개수를 구해서 3% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
                    avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
                    coin_volume = upbit.get_balance(ticker)

                    avgPrice *= 1.03
                    #+3%에 지정가 매도를 걸어준다.
                    myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)

                #40여번 매수에 풀매수가 되서 돈이 부족한 경우 손절 로직이 필요하다.
                else:

                    time.sleep(0.05)
                    #원화 잔고를 가져온다
                    won = float(upbit.get_balance("KRW"))
                                
                    #내가 가진 원화가 물탈 돈보다 적다..(원금 바닥) 그런데 수익율이 - 10% 이하다? 그럼 절반 팔아서 물탈돈을 마련하자!
                    if won < WaterEnterMoeny and revenu_rate <= -10.0:
                        print("!!!!!!!!!!!!!!!No Money Sell Coin Half !!!!!!!!!!!!!!!!!!!!")
                        #현재 걸려있는 지정가 주문을 취소한다. 왜? 아래 매수매도 로직이 있으니깐 
                        myUpbit.CancelCoinOrder(upbit,ticker)
                        #시장가 매도를 한다.
                        balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker) / 2.0)



            #continue로 다음 코인으로 넘어가기에 매수한 코인은 아래 로직을 타지 않는다.
            continue

  
        ############################# 여기서 부터는 매수 아직 안한 매수 대상 코인들이다. ############################
  
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
        df = pyupbit.get_ohlcv(ticker,interval="minute60") #1시간봉 데이타를 가져온다.

        rsi_min = myUpbit.GetRSI(df,14,-1)
        print("-rsi_min:", rsi_min)



        #일봉 기준으로 40이하일때 매수를 한다. 그냥 매수해도 됩니다. 그럼 아래처럼 if문을 만들면 되지만 
        #if myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
        
        #그래도 RSI지표가 40이하가 되는 코인들을 매수 대상을 삼아봤습니다.
        if rsi_min < 40.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
            print("!!!!!!!!!!!!!!!First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
            #지정가 주문을 걸기 전에 이전 주문들을 취소해야 된다.
            myUpbit.CancelCoinOrder(upbit,ticker)
            
            #시장가 매수를 한다.
            balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

            #평균매입단가와 매수개수를 구해서 3% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
            avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
            coin_volume = upbit.get_balance(ticker)

            avgPrice *= 1.03

            #지정가 매도를 한다.
            myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)

            

    except Exception as e:
        print("---:", e)



