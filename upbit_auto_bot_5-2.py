import pyupbit
import time
import pandas as pd

#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터5까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!

access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경

#업비트 객체를 만들어요 액세스 키와 시크릿 키를 넣어서요.
upbit = pyupbit.Upbit(access, secret)

#아래 함수안의 내용은 참고로만 보세요! 제가 말씀드렸죠? 검증된 함수니 안의 내용 몰라도 그냥 가져다 쓰기만 하면 끝!
#RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetRSI(ohlcv,period,st):
    #이 안의 내용이 어려우시죠? 넘어가셔도 되요. 우리는 이 함수가 RSI지표를 정확히 구해준다는 것만 알면 됩니다.
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
    #이 역시 이동평균선을 제대로 구해줍니다.
    close = ohlcv["close"]
    ma = close.rolling(period).mean()
    return float(ma[st])

#거래대금이 많은 순으로 코인 리스트를 얻는다. 첫번째 : Interval기간(day,week,minute15 ....), 두번째 : 몇개까지 
def GetTopCoinList(interval,top):
    print("--------------GetTopCoinList Start-------------------")
    #원화 마켓의 코인 티커를 리스트로 담아요.
    Tickers = pyupbit.get_tickers("KRW")

    #딕셔너리를 하나 만듭니다.
    dic_coin_money = dict()

    #for문을 돌면서 모든 코인들을 순회합니다.
    for ticker in Tickers:
        try:
            #캔들 정보를 가져와서 
            df = pyupbit.get_ohlcv(ticker,interval)
            #최근 2개 캔들의 종가와 거래량을 곱하여 대략의 거래대금을 구합니다.
            volume_money = (df['close'][-1] * df['volume'][-1]) + (df['close'][-2] * df['volume'][-2])
            #volume_money = float(df['value'][-1]) + float(df['value'][-2]) #거래대금! value가 거래대금이었네요.. 이걸 이제야 알다니 ㅎ
            #이걸 위에서 만든 딕셔너리에 넣어줍니다. Key는 코인의 티커, Value는 위에서 구한 거래대금 
            dic_coin_money[ticker] = volume_money
            #출력해 봅니다.
            print(ticker, dic_coin_money[ticker])
            #반드시 이렇게 쉬어줘야 합니다. 안그럼 에러가.. 시간조절을 해보시며 최적의 시간을 찾아보세요 전 일단 0.1로 수정했어요!
            time.sleep(0.1)

        except Exception as e:
            print("exception:",e)

    #딕셔너리를 값으로 정렬하되 숫자가 큰 순서대로 정렬합니다.
    dic_sorted_coin_money = sorted(dic_coin_money.items(), key = lambda x : x[1], reverse= True)

    #빈 리스트를 만듭니다.
    coin_list = list()

    #코인을 셀 변수를 만들어요.
    cnt = 0

    #티커와 거래대금 많은 순으로 정렬된 딕셔너리를 순회하면서 
    for coin_data in dic_sorted_coin_money:
        #코인 개수를 증가시켜주는데..
        cnt += 1

        #파라메타로 넘어온 top의 수보다 작으면 코인 리스트에 코인 티커를 넣어줍니다.
        #즉 top에 10이 들어갔다면 결과적으로 top 10에 해당하는 코인 티커가 coin_list에 들어갑니다.
        if cnt <= top:
            coin_list.append(coin_data[0])
        else:
            break

    print("--------------GetTopCoinList End-------------------")

    #코인 리스트를 리턴해 줍니다.
    return coin_list

#해당되는 리스트안에 해당 코인이 있는지 여부를 리턴하는 함수
def CheckCoinInList(CoinList,Ticker):
    InCoinOk = False

    #리스트안에 해당 코인이 있는지 체크합니다.
    for coinTicker in CoinList:
        #있으면 True로!!
        if coinTicker == Ticker:
            InCoinOk = True
            break

    return InCoinOk

#티커에 해당하는 코인의 수익율을 구해서 리턴하는 함수.
def GetRevenueRate(balances,Ticker):
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



#티커에 해당하는 코인이 매수된 상태면 참을 리턴하는함수
def IsHasCoin(balances,Ticker):
    HasCoin = False
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            HasCoin = True
    return HasCoin




#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()


#거래대금이 많은 탑코인 10개의 리스트
#여러분의 전략대로 마음껏 바꾸세요. 
#첫번째 파라메타에 넣을 수 있는 값 day/minute1/minute3/minute5/minute10/minute15/minute30/minute60/minute240/week/month
#ex) TopCoinList = GetTopCoinList("minute10",30) <- 최근 10여분 동안 거래대금이 많은 코인 30개를 리스트로 리턴
TopCoinList = GetTopCoinList("week",10)

#제외할 코인들을 넣어두세요. 상폐예정이나 유의뜬 코인등등 원하는 코인을 넣어요! 
DangerCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL']

#만약 나는 내가 원하는 코인만 지정해서 사고 싶다면 여기에 코인 티커를 넣고 아래 for문에서 LovelyCoinList를 활용하시면 되요!
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-DOT']

Tickers = pyupbit.get_tickers("KRW")

for ticker in Tickers:
    try:
        #거래량 많은 탑코인 리스트안의 코인이 아니라면 스킵! 탑코인에 해당하는 코인만 이후 로직을 수행한다.
        if CheckCoinInList(TopCoinList,ticker) == False:
            continue
        #위험한 코인이라면 스킵!!!
        if CheckCoinInList(DangerCoinList,ticker) == True:
            continue
        #나만의 러블리만 사겠다면 여기 주석을 풀고 위의 2부분을 주석처리 한다 
        #if CheckCoinInList(LovelyCoinList,ticker) == False:
        #    continue

        #이렇게 쉬어주는거 잊지 마세요!
        time.sleep(0.1)

        #60분봉 1시간봉 기준의 캔들 정보를 가져온다 
        df_60 = pyupbit.get_ohlcv(ticker,interval="minute60")

        #RSI지표를 구한다
        rsi60_min_before = GetRSI(df_60,14,-2) #이전 캔들 RSI지표
        rsi60_min = GetRSI(df_60,14,-1) #현재 캔들 RSI지표
        # RSA를 7로 하게되면 더 기회가 많아지고 공격적이된다.

        #수익율을 구해준다
        revenu_rate = GetRevenueRate(balances,ticker)
        print(ticker , ", RSI :", rsi60_min_before, " -> ", rsi60_min)
        print("revenu_rate : ",revenu_rate)

        #보유하고 있는 코인들 즉 매수 상태인 코인들
        if IsHasCoin(balances,ticker) == True:
            print("HasCoin")
        #아직 매수하기 전인 코인들 즉 매수 대상
        else:
            print("No have")
            
        #if rsi60_min <= 30.0 and revenu_rate < -5.0:
            #분할 매수를 진행한다.




    except Exception as e:
        print("error:", e)



























