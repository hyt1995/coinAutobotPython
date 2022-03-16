import ccxt
import time
import pandas as pd
import pprint
import numpy


from cryptography.fernet import Fernet


'''
여기에 바이비트 봇에 사용될 함수들을 추가하세요!!
'''

#암호화 복호화 클래스
class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou


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

#볼린저 밴드를 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
#차트와 다소 오차가 있을 수 있습니다.
def GetBB(ohlcv,period,st):
    dic_bb = dict()

    ohlcv = ohlcv[::-1]
    ohlcv = ohlcv.shift(st + 1)
    close = ohlcv["close"].iloc[::-1]

    unit = 2.0
    bb_center=numpy.mean(close[len(close)-period:len(close)])
    band1=unit*numpy.std(close[len(close)-period:len(close)])

    dic_bb['ma'] = float(bb_center)
    dic_bb['upper'] = float(bb_center + band1)
    dic_bb['lower'] = float(bb_center - band1)

    return dic_bb




#일목 균형표의 각 데이타를 리턴한다 첫번째: 분봉/일봉 정보, 두번째: 기준 날짜
def GetIC(ohlcv,st):

    high_prices = ohlcv['high']
    close_prices = ohlcv['close']
    low_prices = ohlcv['low']


    nine_period_high =  ohlcv['high'].shift(-2-st).rolling(window=9).max()
    nine_period_low = ohlcv['low'].shift(-2-st).rolling(window=9).min()
    ohlcv['conversion'] = (nine_period_high + nine_period_low) /2
    
    period26_high = high_prices.shift(-2-st).rolling(window=26).max()
    period26_low = low_prices.shift(-2-st).rolling(window=26).min()
    ohlcv['base'] = (period26_high + period26_low) / 2
    
    ohlcv['sunhang_span_a'] = ((ohlcv['conversion'] + ohlcv['base']) / 2).shift(26)
    
    
    period52_high = high_prices.shift(-2-st).rolling(window=52).max()
    period52_low = low_prices.shift(-2-st).rolling(window=52).min()
    ohlcv['sunhang_span_b'] = ((period52_high + period52_low) / 2).shift(26)
    
    
    ohlcv['huhang_span'] = close_prices.shift(-26)


    nine_period_high_real =  ohlcv['high'].rolling(window=9).max()
    nine_period_low_real = ohlcv['low'].rolling(window=9).min()
    ohlcv['conversion'] = (nine_period_high_real + nine_period_low_real) /2
    
    period26_high_real = high_prices.rolling(window=26).max()
    period26_low_real = low_prices.rolling(window=26).min()
    ohlcv['base'] = (period26_high_real + period26_low_real) / 2
    


    
    dic_ic = dict()

    dic_ic['conversion'] = ohlcv['conversion'].iloc[st]
    dic_ic['base'] = ohlcv['base'].iloc[st]
    dic_ic['huhang_span'] = ohlcv['huhang_span'].iloc[-27]
    dic_ic['sunhang_span_a'] = ohlcv['sunhang_span_a'].iloc[-1]
    dic_ic['sunhang_span_b'] = ohlcv['sunhang_span_b'].iloc[-1]


  

    return dic_ic




#MACD의 12,26,9 각 데이타를 리턴한다 첫번째: 분봉/일봉 정보, 두번째: 기준 날짜
def GetMACD(ohlcv,st):
    macd_short, macd_long, macd_signal=12,26,9

    ohlcv["MACD_short"]=ohlcv["close"].ewm(span=macd_short).mean()
    ohlcv["MACD_long"]=ohlcv["close"].ewm(span=macd_long).mean()
    ohlcv["MACD"]=ohlcv["MACD_short"] - ohlcv["MACD_long"]
    ohlcv["MACD_signal"]=ohlcv["MACD"].ewm(span=macd_signal).mean() 

    dic_macd = dict()
    
    dic_macd['macd'] = ohlcv["MACD"].iloc[st]
    dic_macd['macd_siginal'] = ohlcv["MACD_signal"].iloc[st]
    dic_macd['ocl'] = dic_macd['macd'] - dic_macd['macd_siginal']

    return dic_macd




#분봉/일봉 캔들 정보를 가져온다 첫번째: 바이비트 객체, 두번째: 코인 티커, 세번째: 기간 (1d,4h,1h,15m,10m,1m ...)
def GetOhlcv(bybit, Ticker, period):
    #바이비트는 리미트를 반드시 걸어줘야 된다.
    btc_ohlcv = bybit.fetch_ohlcv(Ticker, period,since=None, limit=200)
    df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df


#스탑로스를 걸어놓는다. 해당 가격에 해당되면 바로 손절한다. 첫번째: 바이낸스 객체, 두번째: 코인 티커, 세번째: 손절 수익율 (1.0:마이너스100% 청산, 0.9:마이너스 90%, 0.5: 마이너스 50%)
#네번째 웹훅 알림에서 사용할때는 마지막 파라미터를 False로 넘겨서 사용한다. 트레이딩뷰 웹훅 강의 참조..
def SetStopLoss(bybit, Ticker, cut_rate, Rest = True):
    if Rest == True:
        time.sleep(0.1)
    #주문 정보를 읽어온다.
    orders = bybit.fetch_orders(Ticker,None,None,{'stop_order_status': 'Untriggered'})

    StopLossOk = False
    for order in orders:
        if order['status'].strip() == "open" :

            StopLossOk = True
            break

    #스탑로스 주문이 없다면 주문을 건다!
    if StopLossOk == False:
        if Rest == True:
            time.sleep(10.0)

        #잔고 데이타를 가지고 온다.
        balance = bybit.private_linear_get_position_list()['result']
        if Rest == True:
            time.sleep(0.1)
                                
        amt = 0
        entryPrice = 0
        leverage = 0

        #평균 매입단가와 수량을 가지고 온다.
        #숏포지션을 잡았는지 여부 
        Already_Short = False

        #실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
        for posi in balance:
            if posi['data']['symbol'] == Ticker.replace("/", "") and posi['data']['side'] == "Sell":
                amt = float(posi['data']['size']) * -1

                #사이즈가 0미만이라면 포지션을 잡은거다 숏 포지션 잡았다!
                if amt < 0:
                    Already_Short = True

                entryPrice = float(posi['data']['entry_price'])
                leverage = float(posi['data']['leverage'])
                break

        #숏포지션을 안잡았다면 롱 포지션을 뒤져주자!
        if Already_Short == False:
            for posi in balance:
                if posi['data']['symbol'] == Ticker.replace("/", "") and posi['data']['side'] == "Buy":

                    amt = float(posi['data']['size'])

                    entryPrice = float(posi['data']['entry_price'])
                    leverage = float(posi['data']['leverage'])
                    break
            

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

 
        print("side:",side,"   stopPrice:",stopPrice, "   entryPrice:",entryPrice)

        params = {
            'base_price' : entryPrice,
            'stop_px' : stopPrice,
            'trigger_by' : 'LastPrice',
            'reduce_only': True,
            'close_on_trigger': True
        }

        #스탑 로스 주문을 걸어 놓는다.
        print(bybit.create_order(Ticker,'market',side,abs(amt),entryPrice,params))

        print("####STOPLOSS SETTING DONE ######################")


#구매할 수량을 구한다.  첫번째: 돈(USDT), 두번째:코인 가격, 세번째: 비율 1.0이면 100%, 0.5면 50%
def GetAmount(usd, coin_price, rate):

    target = usd * rate 

    amout = target/coin_price

    if amout < 0.001:
        amout = 0.001

    #print("amout", amout)
    return amout

#거래할 코인의 현재가를 가져온다. 첫번째: 바이비트 객체, 두번째: 코인 티커
def GetCoinNowPrice(bybit,Ticker):
    coin_info = bybit.fetch_ticker(Ticker)
    coin_price = coin_info['last'] # coin_info['close'] == coin_info['last'] 

    return coin_price


        
#거래대금 폭발 여부 첫번째: 캔들 정보, 두번째: 이전 5개의 평균 거래량보다 몇 배 이상 큰지
#이전 캔들이 그 이전 캔들 5개의 평균 거래금액보다 몇 배이상 크면 거래량 폭발로 인지하고 True를 리턴해줍니다
#현재 캔들[-1]은 막 시작했으므로 이전 캔들[-2]을 보는게 맞다!
def IsVolumePung(ohlcv,st):

    Result = False
    try:
        avg_volume = (float(ohlcv['volume'][-3]) + float(ohlcv['volume'][-4]) + float(ohlcv['volume'][-5]) + float(ohlcv['volume'][-6]) + float(ohlcv['volume'][-7])) / 5.0
        if avg_volume * st < float(ohlcv['volume'][-2]):
            Result = True
    except Exception as e:
        print("IsVolumePung ---:", e)

    
    return Result



#내가 포지션 잡은 (가지고 있는) 코인 개수를 리턴하는 함수
def GetHasCoinCnt(bybit):

    #잔고 데이타 가져오기 
    balances = bybit.private_linear_get_position_list()['result']
    
    time.sleep(0.1)

    #선물 마켓에서 거래중인 코인을 가져옵니다.
    Tickers = bybit.fetch_tickers().keys()
    print("-------------------")
    #선물 마켓에서 거래중인 코인을 가져옵니다.
        
    CoinCnt = 0
        #모든 선물 거래가능한 코인을 가져온다.
    for ticker in Tickers:

        if "/USDT" in ticker:
            Target_Coin_Symbol = ticker.replace("/", "")

            amt = 0

            #숏포지션을 잡았는지 여부 
            Already_Short = False

            #실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
            for posi in balances:
                if posi['data']['symbol'] == Target_Coin_Symbol and posi['data']['side'] == "Sell":
                    amt = float(posi['data']['size']) * -1

                    #사이즈가 0미만이라면 포지션을 잡은거다 숏 포지션 잡았다!
                    if amt < 0:
                        Already_Short = True


                    break

            #숏포지션을 안잡았다면 롱 포지션을 뒤져주자!
            if Already_Short == False:
                for posi in balances:
                    if posi['data']['symbol'] == Target_Coin_Symbol and posi['data']['side'] == "Buy":

                        amt = float(posi['data']['size'])
                
                        break


            if amt != 0:
                CoinCnt += 1


    return CoinCnt


#바이비트 선물 거래에서 거래량이 많은 코인 순위 (테더 선물 마켓)
def GetTopCoinList(bybit, top):
    print("--------------GetTopCoinList Start-------------------")

    #선물 마켓에서 거래중인 코인을 가져옵니다.
    Tickers = bybit.fetch_tickers()
    pprint.pprint(Tickers)

    dic_coin_money = dict()
    #모든 선물 거래가능한 코인을 가져온다.
    for ticker in Tickers:

        try: 

            if "/USDT" in ticker:
                print(ticker,"----- \n",Tickers[ticker]['baseVolume'] * Tickers[ticker]['close'])

                dic_coin_money[ticker] = Tickers[ticker]['baseVolume'] * Tickers[ticker]['close']

        except Exception as e:
            print("---:", e)


    dic_sorted_coin_money = sorted(dic_coin_money.items(), key = lambda x : x[1], reverse= True)


    coin_list = list()
    cnt = 0
    for coin_data in dic_sorted_coin_money:
        print("####-------------", coin_data[0], coin_data[1])
        cnt += 1
        if cnt <= top:
            coin_list.append(coin_data[0])
        else:
            break

    print("--------------GetTopCoinList End-------------------")

    return coin_list


#해당되는 리스트안에 해당 코인이 있는지 여부를 리턴하는 함수
def CheckCoinInList(CoinList,Ticker):
    InCoinOk = False
    for coinTicker in CoinList:
        if coinTicker == Ticker:
            InCoinOk = True
            break

    return InCoinOk
    
#최소 포지션 수량을 리턴합니다! 비트코인 0.001 이더리움 0.01 등..
def GetMinimumAmount(bybit,ticker):
    min_amount = 0.01
    Tickers = bybit.fetch_markets()
    for coin_info in Tickers:
        if coin_info['id'] == ticker.replace("/", ""): #BTCUSDT로 넘어와야 되는데 실수로 BTC/USDT 티커를 넘길경우를 대비해 / 를 없애주는 로직!
            min_amount = coin_info['limits']['amount']['min']
            break
    return min_amount

#해당 티커의 모든 주문(스탑로스 리미트 주문 포함)을 취소한다!
def CancelAllOrder(bybit,ticker):
    bybit.cancel_all_orders(ticker)

    orders = bybit.fetch_orders(ticker,None,None,{'stop_order_status': 'Untriggered'})

    for order in orders:
        if order['status'].strip() == "open" :
            print(bybit.cancel_order(order['id'],ticker,{'stop_order_id' : order['id']}))
