#-*-coding:utf-8 -*-
import ccxt
import time
import pandas as pd
import pprint
       
import myBinance
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert #라인 메세지를 보내기 위함!

'''
상승장,하락장 알리미 + 거래량 폭팔 알리미 봇입니다.

상승장을 체크하는 로직은 다양한데 여기서는
5일선이 20일선 위에 있고 현재가가 5일선 위에 있다면 상승장으로 판단합니다.

물론 여기는 선물거래 이기때문에 하락장 알림도 의미가 있으니
하락장의 경우는 반대로 20일선 밑에 5일선 그 밑에 현재가가 있을 때 하락장으로 판단합니다.

여기선 30분봉으로 보지만 일봉을 봐도 되고 그보다 낮은 10분봉을 봐도 됩니다. 이는 여러분의 선택!!
서버에 몇분 마다 돌릴지도 여러분의 선택이지만 60분봉을 본다면 1시간마다 일봉을 본다면 하루에 1번 돌리는게 좋겠죠?

그동안 바이낸스 봇은 비트코인, 이더리움 두개의 티커를 직접 입력해 사용했는데
업비트 봇 처럼 선물거래 마켓에 있는 모든 코인 대상으로도 봇을 만들 수는 있습니다.

만약 흔들 봇을 전체 코인 대상으로 개선하고 싶으신 분은 이 코드가 참고가 되겠네요 :) 


추가적으로 거래량 폭팔 알리미도 추가합니다.
이전 캔들이 그 이전 캔들 5개의 평균 거래금액보다 2배이상 크면 거래량 폭발로 인지하고 알림을 줍니다.
이는 myBinance 모듈 안에 IsVolumePung 함수로 추가했으니 필요하시면 다른 봇에서도 활용하세요!

상승장은 길게 봐도(일봉,60분봉) 거래량 폭발은 짧게(15분,1분봉) 보고 싶으신 분들은
해당 봇을 카피해서 봇을 한개 더 만들어 분리해서 돌리시면 되겠죠?

만약 RSI지표를 본다면 30이하나 70이상 알리미는 여러분이 직접 추가해보세요!!!

현재 코드가 30분봉을 보기에 크론탭에는 일단 아래처럼 30분 마다 동작하게 
등록하면 되지만 어느 캔들(몇분 봉)을 보고 몇 분마다 돌릴지는 여러분 자유입니다

*/30 * * * * python3 /var/autobot/New_Binance_Alert.py


'''

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



#빈 코인 리스트를 생성해둡니다.
UpCoinList = list() #상승장 코인 리스트
DownCoinList = list() #하락장 코인 리스트
VolumePungCoinList = list() #거래량 폭발 코인 담을 리스트 


#선물 마켓에서 거래중인 모든 코인을 가져옵니다.
#Tickers = binanceX.fetch_tickers()

#선물 테더(USDT) 마켓에서 거래중인 코인을 거래대금이 많은 순서로 가져옵니다. 여기선 Top 20
Tickers = myBinance.GetTopCoinList(binanceX,20)



#모든 선물 거래가능한 코인을 가져온다.
for ticker in Tickers:

    try: 
        #아래 주석처리된 부분처럼 선물 거래할 코인을 지정하는 것도 방법입니다.
        #if ticker == "ETH/USDT" or ticker == "BTC/USDT": #이더리움 비트코인만 대상으로..
        
        #하지만 여기서는 USDT 테더로 살수 있는 모든 선물 거래 코인들을 대상으로 돌려봅니다.
        if "/USDT" in ticker:
            print("Coin Ticker: ",ticker)
            
            time.sleep(0.1)

            #캔들 정보 가져온다 30분봉 기준
            df = myBinance.GetOhlcv(binanceX,ticker, '30m')

            ma5 = myBinance.GetMA(df,5,-1)
            ma20 = myBinance.GetMA(df,20,-1)
            now_price = float(df['close'][-1])


            print(ma20 , " < ", ma5 , " < ", now_price)
            #상승장 판단 로직입니다. 20일선 < 5일선 < 현재가
            if ma20 < ma5 and ma5 < now_price:
                print("------------UP COIN-------------")
                #상승장에 해당하는 코인을 리스트에 넣어둡니다.
                #그냥 메세지를 발송하면 메세지가 여러개 가는 스팸이 될 수 있기에 모아서 한번에 보내려고 합니다.
                UpCoinList.append(ticker) 

            print(ma20 , " > ", ma5 , " > ", now_price)
            if now_price < ma5 and ma5 < ma20:
                print("------------DOWN COIN-------------")
                #하락장에 해당하는 코인을 리스트에 넣어둡니다.
                #그냥 메세지를 발송하면 메세지가 여러개 가는 스팸이 될 수 있기에 모아서 한번에 보내려고 합니다.
                DownCoinList.append(ticker) 

            #거래량 폭팔 판단 합니다.
            #여기선 3을 넣었으니 이전 5개의 거래량 평균보다 3배가 높은 거래량을 이전 캔들이 보였다면 거래량 폭발!
            if myBinance.IsVolumePung(df,3) == True:
                print("------------VOLUME PUNG COIN-------------")
                #거래량 폭발 해당하는 코인을 리스트에 넣어둡니다.
                #그냥 메세지를 발송하면 메세지가 여러개 가는 스팸이 될 수 있기에 모아서 한번에 보내려고 합니다.
                VolumePungCoinList.append(ticker)

            
    
    except Exception as e:
        print("---:", e)




#상승장에 해당하는 코인이 1개라도 있으면 메세지를 보냅니다.
if len(UpCoinList) > 0:

    #메세지를 만듭니다. \n은 줄바꿈입니다.
    msg_str = "UP " + str(len(UpCoinList)) + " COINS \n"

    #UpCoinList를 돌면서 위에서 추가한 코인들로 메세지를 만듭니다.
    for coin in UpCoinList:
        msg_str = msg_str + " - " + coin + " - \n"

    #메세지를 보냅니다.
    line_alert.SendMessage(msg_str)


time.sleep(0.5)


#하락장에 해당하는 코인이 1개라도 있으면 메세지를 보냅니다.
if len(DownCoinList) > 0:

    #메세지를 만듭니다. \n은 줄바꿈입니다.
    msg_str = "DOWN " + str(len(DownCoinList)) + " COINS \n"

    #DownCoinList를 돌면서 위에서 추가한 코인들로 메세지를 만듭니다.
    for coin in DownCoinList:
        msg_str = msg_str + " - " + coin + " - \n"

    #메세지를 보냅니다.
    line_alert.SendMessage(msg_str)


time.sleep(0.5)

#거래략 폭발에 해당하는 코인이 1개라도 있으면 메세지를 보냅니다.
if len(VolumePungCoinList) > 0:

    #메세지를 만듭니다. \n은 줄바꿈입니다.
    msg_str = "VolumePung " + str(len(VolumePungCoinList)) + " COINS \n"

    #VolumePungCoinList를 돌면서 위에서 추가한 코인들로 메세지를 만듭니다.
    for coin in VolumePungCoinList:
        msg_str = msg_str + " - " + coin + " - \n"

    #메세지를 보냅니다.
    line_alert.SendMessage(msg_str)





























