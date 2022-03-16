#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert   


'''
상승장 알리미 + 거래량 폭팔 알리미 봇입니다.

상승장을 체크하는 로직은 다양한데 여기서는
5일선이 20일선 위에 있고 현재가가 5일선 위에 있다면 상승장으로 판단합니다.
다르게 판단하고 싶다면 여러분이 적절히 수정하세요!

여기선 30분봉으로 보지만 일봉을 봐도 되고 그보다 낮은 10분봉을 봐도 됩니다. 이는 여러분의 선택!!
서버에 몇분 마다 돌릴지도 여러분의 선택이지만 60분봉을 본다면 1시간마다 일봉을 본다면 하루에 1번 돌리는게 좋겠죠?

현재 코드는 원화 마켓 코인 전체를 대상으로 찾지만 
나만의 코인만 대상으로 삼아도 되고 거래대금이 많은 코인을 대상으로 삼아도 됩니다.
이는 주석을 적절히 풀면 되지요.


추가적으로 거래량 폭팔 알리미도 추가합니다.
이전 캔들이 그 이전 캔들 5개의 평균 거래금액보다 2배이상 크면 거래량 폭발로 인지하고 알림을 줍니다.
이는 myUpbit모듈 안에 IsVolumePung 함수로 추가했으니 필요하시면 다른 봇에서도 활용하세요!

상승장은 길게 봐도(일봉,60분봉) 거래량 폭발은 짧게(15분,1분봉) 보고 싶으신 분들은
해당 봇을 카피해서 봇을 한개 더 만들어 분리해서 돌리시면 되겠죠?


만약 RSI지표를 본다면 30이하나 70이상 알리미는 여러분이 직접 추가해보세요!!!


현재 코드가 30분봉을 보기에 크론탭에는 일단 아래처럼 30분 마다 동작하게 
등록하면 되지만 어느 캔들(몇분 봉)을 보고 몇 분마다 돌릴지는 여러분 자유입니다,

*/30 * * * * python3 /var/autobot/New_Upbit_Alert.py




'''

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

#거래대금이 많은 탑코인 30개의 리스트 
#이부분 시간이 오래걸리니 사용하지 않는다면 주석처리를 하세요! 이렇게요!
#TopCoinList = myUpbit.GetTopCoinList("day",30)

#구매 제외 코인 리스트
#OutCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL','KRW-BTC']

#나의 코인
#LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-DOT']



#빈 코인 리스트를 생성해둡니다.
UpCoinList = list() #상승장 코인 담을 리스트
VolumePungCoinList = list() #거래량 폭발 코인 담을 리스트 


#원화 마켓 전체를 돕니다.
Tickers = pyupbit.get_tickers("KRW")

for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)
  
        #!!! 업비트 원화마켓 전체를 대상으로 하고싶다면 여기 처럼 아래를 주석처리 하면 됩니다!!!!#

        #거래량 많은 탑코인 리스트안의 코인이 아니라면 스킵! 탑코인에 해당하는 코인만 이후 로직을 수행한다.
        #if myUpbit.CheckCoinInList(TopCoinList,ticker) == False:
        #    continue
        #위험한 코인이라면 스킵!!!
        #if myUpbit.CheckCoinInList(OutCoinList,ticker) == True:
        #    continue
        #나만의 러블리만 사겠다! 그 이외의 코인이라면 스킵!!!
        #if CheckCoinInList(LovelyCoinList,ticker) == False:
        #    continue

            
        time.sleep(0.1)
        df = pyupbit.get_ohlcv(ticker,interval="minute30") #30분봉 데이타를 가져온다.

        df['volume']

        ma5 = myUpbit.GetMA(df,5,-1)
        ma20 = myUpbit.GetMA(df,20,-1)

        now_price = float(df['close'][-1])

        print(ma20 , " < ", ma5 , " < ", now_price)

        #상승장 판단 로직입니다. 20일선 < 5일선 < 현재가
        if ma20 < ma5 and ma5 < now_price:
            print("------------UP COIN-------------")
            #상승장에 해당하는 코인을 리스트에 넣어둡니다.
            #그냥 메세지를 발송하면 메세지가 여러개 가는 스팸이 될 수 있기에 모아서 한번에 보내려고 합니다.
            UpCoinList.append(ticker) 


        #거래량 폭팔 판단 합니다.
        #여기선 3을 넣었으니 이전 5개의 거래량 평균보다 3배가 높은 거래량을 이전 캔들이 보였다면 거래량 폭발!
        if myUpbit.IsVolumePung(df,3) == True:
            print("------------VOLUME PUNG COIN-------------")
            #상승장에 해당하는 코인을 리스트에 넣어둡니다.
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


#거래략 폭발에 해당하는 코인이 1개라도 있으면 메세지를 보냅니다.
if len(VolumePungCoinList) > 0:

    #메세지를 만듭니다. \n은 줄바꿈입니다.
    msg_str = "VolumePung " + str(len(VolumePungCoinList)) + " COINS \n"

    #VolumePungCoinList를 돌면서 위에서 추가한 코인들로 메세지를 만듭니다.
    for coin in VolumePungCoinList:
        msg_str = msg_str + " - " + coin + " - \n"

    #메세지를 보냅니다.
    line_alert.SendMessage(msg_str)



























