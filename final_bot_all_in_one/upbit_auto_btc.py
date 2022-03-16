import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import pyupbit
import time
import pandas as pd

import line_alert

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

'''
그냥 단순히 5천원씩 매일 9시 비트코인을 사는 봇입니다.
라인 메세지를 보내기에 서버가 잘 동작하는지 체크용으로 돌리고 있습니다.

서버 크론탭에는 

0 0 * * * python3 /var/autobot/upbit_auto_btc.py

이렇게 설정하면 매일 아침 9시에 실행됩니다. 


'''

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)


upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

#시간 정보를 보여 줍니다.
time_info = time.gmtime()
print(time_info)
print(time_info.tm_hour)

#해당 봇이 매일 아침 9시에 돌기에 9시마다 메세지가 옵니다 이로써 우리는 서버가 살아있는지 체크할 수 있습니다.
line_alert.SendMessage("SERVER IS OK!!!")

#단순히 비트코인을 5천원씩 매수합니다.
print(upbit.buy_market_order("KRW-BTC",5000))

