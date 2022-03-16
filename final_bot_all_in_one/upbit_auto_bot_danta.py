#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키


'''
영상에서는 1분봉을 보지만 거래대금 탑 코인을 구하는 로직 때문에 봇이 도는 시간이 1분이상 걸리는 경우가 생기기에
이 코드 처럼 5분봉 이상을 보는 것을 추천드립니다.

단독으로 쓸 경우를 대비해 물타는 로직도 추가했으니 제거하시거나 적절히 수정하셔서 사용해보세요!

하락장 대비하는 것이 전략이라면
단타시 많은 코인을 많은 비중으로 매수하는건 위험하니 조절해 보시면서 테스트 해보세요!


현재 코드가 5분봉을 보기에 크론탭에는 일단 아래처럼 5분 마다 동작하게 
등록하면 되지만 어느 캔들(몇분 봉)을 보고 몇 분마다 돌릴지는 여러분 자유입니다.

*/5 * * * * python3 /var/autobot/upbit_auto_bot_danta.py


'''
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
TopCoinList = myUpbit.GetTopCoinList("minute10",30)

#구매 제외 코인 리스트
OutCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL','KRW-BTC']

#나의 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-DOT']


Tickers = pyupbit.get_tickers("KRW")


for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)

        #제외할 코인이라면 스킵!!!
        if myUpbit.CheckCoinInList(OutCoinList,ticker) == True:
            continue
  
        ############영상엔 없지만 여기서 물을 타줄 수도 있다.
        if myUpbit.IsHasCoin(balances,ticker) == True:

            #예로 수익율이 마이너스 5% 미만이라면 물탈 비중만큼 물을 탄다.
            #수익율을 구한다.
            revenu_rate = myUpbit.GetRevenueRate(balances,ticker)

            #수익율이 마이너스 5%이면서 
            if revenu_rate < -5.0:
                            
                #현재 코인의 총 매수금액
                NowCoinTotalMoney = myUpbit.GetCoinNowMoney(balances,ticker)
                print("CHEK WATER")
                print(CoinMaxMoney, " >", NowCoinTotalMoney)

                #매수 비중이 남았다면
                if CoinMaxMoney > NowCoinTotalMoney:
                    #이전 주문들을 취소하고
                    myUpbit.CancelCoinOrder(upbit,ticker)

                    #시장가 매수를 한다.
                    balances = myUpbit.BuyCoinMarket(upbit,ticker,WaterEnterMoeny)

                    #평균매입단가와 매수개수를 구해서 0.5% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
                    avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
                    coin_volume = upbit.get_balance(ticker)

                    avgPrice *= 1.005
                    #지정가 매도를 한다.
                    myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)


            continue

  
  
        #거래량 많은 탑코인 리스트안의 코인이 아니라면 스킵! 탑코인에 해당하는 코인만 이후 로직을 수행한다.
        if myUpbit.CheckCoinInList(TopCoinList,ticker) == False:
            continue
 
        #나만의 러블리만 사겠다! 그 이외의 코인이라면 스킵!!!
         #if CheckCoinInList(LovelyCoinList,ticker) == False:
        #    continue

        print("!!!!! Target Coin!!! :",ticker)


            
        time.sleep(0.05)
        #영상에선 1분봉으로 만들었지만 최종적으로 5분으로 변경해 봅니다
        df = pyupbit.get_ohlcv(ticker,interval="minute5") #5분봉 데이타를 가져온다.


        #5일선 값을 구한다.
        ma5_before3 = myUpbit.GetMA(df,5,-4)
        ma5_before2 = myUpbit.GetMA(df,5,-3)
        ma5 = myUpbit.GetMA(df,5,-2)

        #20일선 값을 구한다.
        ma20 = myUpbit.GetMA(df,20,-2)

        print("ma20 :", ma20)
        print("ma5 :", ma5 , " <- ", ma5_before2, " <- ", ma5_before3)

        rsi_min = myUpbit.GetRSI(df,14,-1)
        print("-rsi_min:", rsi_min)




        print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        ################################새로 추가된 지표 참고용으로 필요하시면 봇에 활용해 보세요!##############################################################

        #---------------------------------------------#
        #아래 지표들 구할때 제가 현재 캔들을 -1 이 아니라 -2로 
        #이전 캔들을 -2가 아니라 -3으로 수정했습니다. 이유는 https://blog.naver.com/zacra/222567868086 참고하세요!
        #---------------------------------------------#



        #볼린저 밴드 구하는 함수는 실제 차트와 다소 오차가 존재하지만 활용하는데는 무리가 없습니다!
        #볼린저 밴드 함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 upper가 상단, ma는 기준이 되는 이동평균선(여기선 20일선),lower가 하단이 됩니다.
        print("-----------------------------------------------")
        #이전 캔들의 볼린저 밴드 상하단
        BB_dic_before = myUpbit.GetBB(df,20,-3)
        print("before - MA:",BB_dic_before['ma'],", Upper:", BB_dic_before['upper'] ,", Lower:" ,BB_dic_before['lower'])

        print("-----------------------------------------------")
        #현재 볼린저 밴드 상하단
        BB_dic_now = myUpbit.GetBB(df,20,-2)
        print("now - MA:",BB_dic_now['ma'],", Upper:", BB_dic_now['upper'] ,", Lower:" ,BB_dic_now['lower'])



        #MACD값을 구해줍니다!
        #MACD함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 macd는 MACD값, macd_siginal값이 시그널값, ocl이 오실레이터 값이 됩니다
        print("-----------------------------------------------")
        macd_before = myUpbit.GetMACD(df,-3) #이전캔들의 MACD
        print("before - MACD:",macd_before['macd'], ", MACD_SIGNAL:", macd_before['macd_siginal'],", ocl:", macd_before['ocl'])
        print("-----------------------------------------------")
        macd = myUpbit.GetMACD(df,-2) #현재캔들의 MACD
        print("now - MACD:",macd['macd'], ", MACD_SIGNAL:", macd['macd_siginal'],", ocl:", macd['ocl'])




        #일목균형표(일목구름) 구해줍니다! 다소 오차는 있을 수 있으나 활용하는데 무리는 없습니다.
        #일목균형표(일목구름)함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 conversion는 전환선, base는 기준선
        #huhang_span은 후행스팬, sunhang_span_a는 선행스팬1, sunhang_span_b는 선행스팬2 입니다.
        print("-----------------------------------------------")
        ic_before = myUpbit.GetIC(df,-3) #이전캔들의 일목균형표
        print("before - Conversion:",ic_before['conversion'], ", Base:", ic_before['base'],", HuHang_Span:", ic_before['huhang_span'],", SunHang_Span_a:", ic_before['sunhang_span_a'],", SunHang_Span_b:", ic_before['sunhang_span_b'])

        print("-----------------------------------------------")
        ic = myUpbit.GetIC(df,-2) #현재캔들의 일목균형표
        print("now - Conversion:",ic['conversion'], ", Base:", ic['base'],", HuHang_Span:", ic['huhang_span'],", SunHang_Span_a:", ic['sunhang_span_a'],", SunHang_Span_b:", ic['sunhang_span_b'])




        print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")



        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################

        #반드시 이 글을 읽고 수정하세요 https://blog.naver.com/zacra/222567868086
        # 지표를 활용할 때 현재 캔들 -1 과 이전 캔들 -2는 값이 같아지는 경우가 생길 수 있습니다. 
        # (봇이 캔들이 변경되는 시점에 주로 실행되기에 이 경우 현재 캔들 기준으로 구한 지표 값과 이전 캔들 기준으로 구한 지표 값이 동일해 지는 상황압니다,)
        # 따라서 이전 캔들 -2, 이이전 캔들 -3으로 조합해야 원하는 결과를 얻을 수 있습니다.
        # 쉽게 이야기해서 현재 캔들을 -2, 이전 캔들을 -3으로 보는게 좋다는 거죠. 어자피 진짜 현재 캔들 -1과 이전 캔들 -2의 값이 보통 같을테니까요. 
        # (이전 캔들의 종가와 현재 캔들의 시가가 거의 같은 경우가 많으니까요!)

        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################


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

            avgPrice *= 1.005
            #지정가 매도를 한다.
            myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)



        #1분봉 기준으로 30이하일때 매수를 한다.
        if rsi_min < 30.0 and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt :
            print("!!!!!!!!!!!!!!!DANTA DANTA RSI First Buy GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
            #영상엔 없지만 지정가 주문을 걸기 전에 이전 주문들을 취소해야 된다.
            myUpbit.CancelCoinOrder(upbit,ticker)
            
            #시장가 매수를 한다.
            balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

            #평균매입단가와 매수개수를 구해서 0.5% 상승한 가격으로 지정가 매도주문을 걸어놓는다.
            avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
            coin_volume = upbit.get_balance(ticker)

            avgPrice *= 1.005

            #지정가 매도를 한다.
            myUpbit.SellCoinLimit(upbit,ticker,avgPrice,coin_volume)

            

    except Exception as e:
        print("---:", e)



























