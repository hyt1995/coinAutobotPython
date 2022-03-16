import line_alert
import json
import sys

import pyupbit
import ccxt

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
## 이 중에 안쓰는 모듈이 있다면 주석처리 하세요!
## 예로 바이비트를 사용 안한다면 아래 import myBybit를 주석처리 합니다!!!
import myBinance
import myUpbit
import myBybit 
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

import ende_key  #암복호화키
import my_key    # 시크릿 액세스키

#######################################################################
#######################################################################

# https://youtu.be/GmR4-AiJjPE 여기를 참고하세요 트레이딩뷰 웹훅 관련 코드입니다!

#######################################################################
#######################################################################

data = json.loads(sys.argv[1])

print(data)

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)




#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#-- 아래 부터는 업비트, 바이낸스, 바이비트 순으로 넘겨받은 데이터(메시지) data를 해석해서 적당한 기능을 하는 로직입니다.
#-- 만약 사용안하는 거래소가 있다면 과감히 삭제하고 사용하세요! 안그러면 에러가 납니다!!
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------





#업비트 Json파일 구성 예

# dist -> 무조건 "upbit" 로 입력 
# ticker -> "KRW-BTC" ,"KRW-ETH" 등의 원화마켓 티커를 입력
# type -> "limit" 지정가매매, "market" 시장가매매, "cancel" 지정가주문 취소로 정의
# side -> "buy"는 매수, "sell"은 매도
# price_money -> 지정가 매매"limit"의 경우엔 !!!매매할 가격!!!, 시장가"market" 매매할 경우 !!!매수금액!!!
# amt -> 지정가 매매에 사용할 수량
# etc_num -> 추가 필요한 정보 있으면 넣을 넘버형 데이타 (현재 사용 안함 필요하면 쓰세용!) 
# etc_str -> 추가 필요한 정보 있으면 넣을 스트링형 데이타 (현재 사용 안함 필요하면 쓰세용!) 


if data['dist'] == "upbit":
        
    Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
    Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

    #업비트 객체를 만든다
    upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

    #내가 가진 업비트 잔고 데이터를 다 가져온다.
    balances = upbit.get_balances()

    if data['type'] == "market":
        if data['side'] == "buy":
            balances = myUpbit.BuyCoinMarket(upbit,data['ticker'],data['price_money'])
        elif data['side'] == "sell":

            balances = myUpbit.SellCoinMarket(upbit,data['ticker'],data['amt'])

    elif data['type'] == "limit":
        if data['side'] == "buy":
            myUpbit.BuyCoinLimit(upbit,data['ticker'],data['price_money'],data['amt'])
        elif data['side'] == "sell":

            myUpbit.SellCoinLimit(upbit,data['ticker'],data['price_money'],data['amt'])

    elif data['type'] == 'cancel':
        
  
        myUpbit.CancelCoinOrder(upbit,data['ticker'])




#바이낸스 Json파일 구성 예

# dist -> 무조건 "binance" 로 입력 
# ticker -> "BTC/USDT" ,"ETH/USDT" 등의 선물마켓 티커를 입력 
# type -> "limit" 지정가매매, "market" 시장가매매, "cancel" 지정가주문 취소, 'stop' 스탑로스로 정의
# side -> "long"는 롱포지션, "short"은 숏포지션
# price_money -> 지정가 매매"limit"의 경우엔 진입 가격 혹은 청산 가격!
# amt -> 포지션 잡을 수량
# etc_num -> 스탑 로스의 경우 스탑로스 비중 (ex 0.2면 마이너스 20%에 스탑로스 )
# etc_str -> 추가 필요한 정보 있으면 넣을 스트링형 데이타 (현재 사용 안함 필요하면 쓰세용!) 


elif data['dist'] == 'binance':



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


    if data['type'] == "market":
        if data['side'] == "long":
            print(binanceX.create_market_buy_order(data['ticker'], data['amt']))

        elif data['side'] == "short":
            print(binanceX.create_market_sell_order(data['ticker'], data['amt']))

    elif data['type'] == "limit":
        if data['side'] == "long":
            print(binanceX.create_limit_buy_order(data['ticker'], data['amt'], data['price_money']))
        elif data['side'] == "short":
            print(binanceX.create_limit_sell_order(data['ticker'], data['amt'], data['price_money']))

    elif data['type'] == 'cancel':
        
        binanceX.cancel_all_orders(data['ticker'])

    elif data['type'] == 'stop':

        #스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binanceX,data['ticker'],data['etc_num'],False)


#바이비트 Json파일 구성 예

# dist -> 무조건 "bybit" 로 입력 
# ticker -> "BTC/USDT" ,"ETH/USDT" 등의 선물마켓 티커를 입력 
# type -> "limit" 지정가매매, "market" 시장가매매, "cancel" 지정가주문 취소, 'stop' 스탑로스로 정의
# side -> "long"는 롱포지션, "short"은 숏포지션
# price_money -> 지정가 매매"limit"의 경우엔 진입 가격 혹은 청산 가격!
# amt -> 포지션 잡을 수량
# etc_num -> 스탑 로스의 경우 스탑로스 비중 (ex 0.2면 마이너스 20%에 스탑로스 )
# etc_str -> 'open'의 경우 포지션 오픈, 'close'의 경우 포지선 종료 이걸 구분 안하면 양방향 포지션 매매가 됨(롱과 숏이 공존)



elif data['dist'] == 'bybit':



    #암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
    simpleEnDecrypt = myBybit.SimpleEnDecrypt(ende_key.ende_key)


    #암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
    Bybit_AccessKey = simpleEnDecrypt.decrypt(my_key.bybit_access)
    Bybit_ScretKey = simpleEnDecrypt.decrypt(my_key.bybit_secret)

    # bybit 객체 생성
    bybitX = ccxt.bybit(config={
        'apiKey': Bybit_AccessKey, 
        'secret': Bybit_ScretKey,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        }
    })



    if data['type'] == "market":

        if data['etc_str'] == "open":

            if data['side'] == "long":
                print(bybitX.create_market_buy_order(data['ticker'], data['amt']))
            elif data['side'] == "short":
                print(bybitX.create_market_sell_order(data['ticker'], data['amt']))

        elif data['etc_str'] == "close":
            
            if data['side'] == "long":
                print(bybitX.create_market_buy_order(data['ticker'], data['amt'],{'reduce_only': True,'close_on_trigger':True}))
            elif data['side'] == "short":
                print(bybitX.create_market_sell_order(data['ticker'], data['amt'],{'reduce_only': True,'close_on_trigger':True}))


    elif data['type'] == "limit":

        if data['etc_str'] == "open":


            if data['side'] == "long":
                print(bybitX.create_limit_buy_order(data['ticker'], data['amt'], data['price_money']))
            elif data['side'] == "short":
                print(bybitX.create_limit_sell_order(data['ticker'], data['amt'], data['price_money']))


        elif data['etc_str'] == "close":

            if data['side'] == "long":
                print(bybitX.create_limit_buy_order(data['ticker'], data['amt'], data['price_money'],{'reduce_only': True,'close_on_trigger':True}))
            elif data['side'] == "short":
                print(bybitX.create_limit_sell_order(data['ticker'], data['amt'], data['price_money'],{'reduce_only': True,'close_on_trigger':True}))


    elif data['type'] == 'cancel':

        myBybit.CancelAllOrder(bybitX,data['ticker'])


    elif data['type'] == 'stop':

        #스탑 로스 설정을 건다.
        myBybit.SetStopLoss(bybitX,data['ticker'],data['etc_num'],False)
       
         



line_alert.SendMessage("MsgTest: " + str(data))







