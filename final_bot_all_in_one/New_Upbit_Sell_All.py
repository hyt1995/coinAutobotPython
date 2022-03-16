#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import pyupbit
import time
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키


'''
가끔 전략상 봇을 새로 돌리기 위해서
업비트에 매수된 모든 코인을 다 시장가 매도하고 싶을 때가 있습니다.
그때 이 봇을 비주얼 스튜디오 코드나 서버에 올려놓고 실행 해주면
업비트의 모든 코인이 매도처리 됩니다.


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

#원화 마켓에서 거래중인 코인을 가져온다.
Tickers = pyupbit.get_tickers("KRW")

for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)

        #이미 매수한 코인일 경우
        if myUpbit.IsHasCoin(balances,ticker) == True:
            #이전 주문들을 취소해야 된다.
            myUpbit.CancelCoinOrder(upbit,ticker)
            time.sleep(0.1)

            #수익율을 구한다.
            revenu_rate = myUpbit.GetRevenueRate(balances,ticker)
            print("----------------------------------HAS_COIN!!!!", ticker, " -> " ,revenu_rate)
            
            
            #시장가 매도를 한다.
            balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))


    except Exception as e:
        print("---:", e)



























