import time
import pyupbit
import pandas as pd
import ende_key
import my_key
import numpy
import datetime as dt



###################################################################################
###업비트 코인 자동매매 함수 작성################################################################################
###################################################################################


# #RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
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

#해당되는 리스트안에 해당 코인이 있는지 여부를 리턴하는 함수
def CheckCoinInList(CoinList,Ticker):
    InCoinOk = False
    for coinTicker in CoinList:
        if coinTicker == Ticker:
            InCoinOk = True
            break

    return InCoinOk

#거래량 top10을 구하는 함수 interval = 기간, top = 몇개까지
def GetTopCoinList(interval, top):

    #모든 원화코인들을 가져온다.
    Tickers = pyupbit.get_tickers("KRW")

    #거래량 순서대로 정렬을 위해서 딕셔너리 생성
    dicCoinMoney = dict()

    for ticker in Tickers:
        try:
            
            temDf = pyupbit.get_ohlcv(ticker, interval)
            # 오늘의 거래량 구하기
            volume_modey = (temDf["close"][-1] * temDf["volume"][-1]) + temDf["close"][-2] * temDf["volume"][-2]
            time.sleep(0.05)

            dicCoinMoney[ticker] = volume_modey

        except Exception as e:
            print("티커 정보 가져오기 에러", e)
        
    #코인 거래량 순서대로 줄세우기 정렬
    dicSortedCoinMoney = sorted(dicCoinMoney.items(), key = lambda x : x[1], reverse=True)
    

    coinList = list()

    for coinData in dicSortedCoinMoney:

    #코인 금액 3000이상, 최소 1달이상코인 

        if pyupbit.get_current_price(coinData[0]) >= 3000 and len(pyupbit.get_ohlcv(coinData[0],count=3, interval="month")) >= 3 and len(coinList) <= top:

            coinList.append(coinData[0])

        elif len(coinList) >= top : 
            break


    return coinList


#티커에 해당하는 코인의 수익율을 구해서 리턴하는 함수.
def GetRevenueRate(balances, Ticker):
    revenue_rate = 0.0

    for value in balances:
        try:
            realTicker = value['unit_currency'] + "-" + value['currency']

            if Ticker == realTicker:
                time.sleep(0.05)
                
                #현재 가격을 가져옵니다.
                nowPrice = pyupbit.get_current_price(realTicker)

                #수익율을 구해서 넣어줍니다
                revenue_rate = (float(nowPrice) - float(value['avg_buy_price'])) * 100.0 / float(value['avg_buy_price'])
                break

        except Exception as e:
            print("GetRevenueRate error:", e)

    return revenue_rate



# 내가 구입한 코인 확인하기
def isHasCoin(balances, Ticker):
    hasCoin = False
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            hasCoin = True
    return hasCoin

#티커에 해당하는 코인의 총 매수금액을 리턴하는 함수
def GetCoinNowMoney(balances,Ticker):
    CoinMoney = 0.0
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            CoinMoney = float(value['avg_buy_price']) * (float(value['balance']) + float(value['locked']))
            break
    return CoinMoney


#총 원금을 구한다!
def GetTotalMoney(balances):
    total = 0.0
    for value in balances:
        try:
            ticker = value['currency']
            if ticker == "KRW": #원화일 때는 평균 매입 단가가 0이므로 구분해서 총 평가금액을 구한다.
                total += (float(value['balance']) + float(value['locked']))
            else:
                avg_buy_price = float(value['avg_buy_price'])

                #매수평균가(avg_buy_price)가 있으면서 잔고가 0이 아닌 코인들의 총 매수가격을 더해줍니다.
                if avg_buy_price != 0 and (float(value['balance']) != 0 or float(value['locked']) != 0):
                    #balance(잔고 수량) + locked(지정가 매도로 걸어둔 수량) 이렇게 해야 제대로 된 값이 구해집니다.
                    #지정가 매도 주문이 없다면 balance에 코인 수량이 100% 있지만 지정가 매도 주문을 걸면 그 수량만큼이 locked로 옮겨지기 때문입니다.
                    total += (avg_buy_price * (float(value['balance']) + float(value['locked'])))
        except Exception as e:
            print("GetTotalMoney error:", e)
    return total

#총 평가금액을 구한다! 
#위 원금을 구하는 함수와 유사하지만 코인의 매수 평균가가 아니라 현재 평가가격 기준으로 총 평가 금액을 구한다.
def GetTotalRealMoney(balances):
    total = 0.0
    for value in balances:

        try:
            ticker = value['currency']
            if ticker == "KRW": #원화일 때는 평균 매입 단가가 0이므로 구분해서 총 평가금액을 구한다.
                total += (float(value['balance']) + float(value['locked']))
            else:
            
                avg_buy_price = float(value['avg_buy_price'])
                if avg_buy_price != 0 and (float(value['balance']) != 0 or float(value['locked']) != 0): #드랍받은 코인(평균매입단가가 0이다) 제외 하고 현재가격으로 평가금액을 구한다,.
                    realTicker = value['unit_currency'] + "-" + value['currency']

                    time.sleep(0.1)
                    nowPrice = pyupbit.get_current_price(realTicker)
                    total += (float(nowPrice) * (float(value['balance']) + float(value['locked'])))
        except Exception as e:
            print("GetTotalRealMoney error:", e)

    return total
    

#내가 매수한 (가지고 있는) 코인 개수를 리턴하는 함수
def GetHasCoinCnt(balances):
    CoinCnt = 0
    for value in balances:
        avg_buy_price = float(value['avg_buy_price'])
        if avg_buy_price != 0: #원화, 드랍받은 코인(평균매입단가가 0이다) 제외!
            CoinCnt += 1
    return CoinCnt

###################################################################################
###업비트 객체 만드는 부분################################################################################
###################################################################################

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = my_key.SimpleEnDecrypt(ende_key.ende_key)



#### 실서버 운영을 위한
#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

######로컬에서 테스트를 위한
#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
# Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.local_upbit_access)
# Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.local_upbit_secret)

# 업비트 객체 생성
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)



###################################################################################
###여기서 부터 업비트 코인 자동매매 전략 시작!!!!!!################################################################################
###################################################################################


#제외할 코인들을 넣어두세요. 상폐예정이나 유의뜬 코인등등 원하는 코인을 넣어요! 
# DangerCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL']

#만약 나는 내가 원하는 코인만 지정해서 사고 싶다면 여기에 코인 티커를 넣고 아래 for문에서 LovelyCoinList를 활용하시면 되요!
# 비트코인 , 이더리움, 비트코인 캐시, 에이브
LovelyCoinList = ['KRW-BTC','KRW-ETH']
# 이더리움클래식 추가한다.





# 내가 가진 잔고 데이터 가져오기
balances = upbit.get_balances()

# Tickers = pyupbit.get_tickers("KRW")
#거래대금이 많은 탑코인 , 코인 금액 3000이상, 최소 1달이상코인
# TopCoinList = GetTopCoinList("day",5)

#내가 매수할 총 코인 개수
MaxCoinCnt = 3

#처음 매수할 비중(퍼센트) 
FirstRate = 100.0
#추가 매수할 비중 (퍼센트) 
WaterRate = 5.0

TotalMoeny = GetTotalMoney(balances) #총 원금
TotalRealMoney = GetTotalRealMoney(balances) #총 평가금액
#지정 매도가를 위한 1%금액 
selectSale = TotalRealMoney * 0.01

#내 총 수익율
TotalRevenue = (TotalRealMoney - TotalMoeny) * 100.0/ TotalMoeny

#코인당 매수할 최대 매수금액
CoinMaxMoney = TotalMoeny / MaxCoinCnt

#처음에 매수할 금액 
FirstEnterMoney = (CoinMaxMoney / 100.0 * FirstRate) - selectSale

#그 이후 매수할 금액 - 즉 물 탈 금액 
WaterEnterMoeny = CoinMaxMoney / 100.0 * WaterRate

print("-----------------------------------------------")
print ("Total Money:", GetTotalMoney(balances))
print ("Total Real Money:", GetTotalRealMoney(balances))
print ("Total Revenue", TotalRevenue)
print("-----------------------------------------------")
print ("CoinMaxMoney : ", CoinMaxMoney)
print ("FirstEnterMoney : ", FirstEnterMoney)
print ("WaterEnterMoeny : ", WaterEnterMoeny)
print ("지정 매도가를 위한 1% 금액 : ", selectSale)

TopCoinList = GetTopCoinList("day",15)

booleanFor = True

if booleanFor == True:

    #이 두개는 항상 추가하고 돌린다. - 그나마 정상적인 기회가 많다.
    TopCoinList.append("KRW-BTC")
    TopCoinList.append("KRW-ETH")
    TopCoinList.append("KRW-ETC")

    print("매수/매도 돌릴 코인 리스트 ::::::: ", TopCoinList)


    for ticker in TopCoinList:
        try:

            #보유하고 있는 코인들 즉 매수 상태인 코인들
            if isHasCoin(balances,ticker) == True:

                print("---------------------코인 매수 상태--------------------------------------------------------------")

                balances = upbit.get_balances()

                for value in balances:
                    
                    if ticker == value['unit_currency'] + "-" + value['currency']:

                        print("내가 매입한 코인가격에서 -1%밑으로 떨어지면 매도 하고 다시 기회를 노린다. !!!!!!!!!!!!!!!!!")
                        if pyupbit.get_current_price(ticker) <= float(value["avg_buy_price"])*0.99:

                            revenu_rate = GetRevenueRate(balances, ticker)
                            print("현재 내 수익율 가져오기 :::: ", revenu_rate)
                            print("1% 보다 떨어져 매도 :::",upbit.sell_market_order(ticker,upbit.get_balance(ticker)))
                            time.sleep(0.5)




                # 5분봉을 가져온다.
                df_5 = pyupbit.get_ohlcv(ticker, interval="minute5")
                ma3_2 = GetMA(df_5, 3, -2)
                ma3_3 = GetMA(df_5, 3, -3)
                ma10_2 = GetMA(df_5, 10, -2)
                
                if  ma3_3 > ma3_2 and ma3_3 >= ma10_2  and ma10_2 > ma3_2: 
                    print("여기서 매도를 통해 기회를 더 늘린다.")
                    print("1% 보다 떨어져 매도 :::",upbit.sell_market_order(ticker,upbit.get_balance(ticker)))
                    time.sleep(0.5)

                # rsi7이 70이상이면 매도를 진행한다.######################################
                rsi7_1 = GetRSI(df_5, 7, -2)


                #5분봉 기준 RSI지표 70이상일때 매도
                # if rsi14_2 >= 70 and rsi14_2 > rsi14_1 :
                if rsi7_1>= 70.0:
                    print("바로 전 rsi7이 70이상 매도 진행 ::::", upbit.sell_market_order(ticker,upbit.get_balance(ticker)))
                    break

            else:
                print("-----------------------------------현재 매수된 코인이 없을 경우---------------------------------------------------------------------")
                #분봉을 가져온다.
                df5 = pyupbit.get_ohlcv(ticker, interval="minute5")
                rsi7_1 = GetRSI(df5, 7, -2)
                rsi7_2 = GetRSI(df5, 7, -3)
                
                if rsi7_2 <= 30 and rsi7_2 < rsi7_1:
                    
                    print(upbit.buy_market_order(ticker,FirstEnterMoney))
                    print("현재 rsi지수가 30보다 같거나 작을때 코인 :", ticker, "매수",FirstEnterMoney,"가격으로 매수")

                    time.sleep(0.5)

                    break


        #예외 즉 에러가 발생하면 여기서 프린트 해줍니다.
        except Exception as e:
            print("error:", e)


print("마지막에 매수함? ::: ", upbit.get_balances())