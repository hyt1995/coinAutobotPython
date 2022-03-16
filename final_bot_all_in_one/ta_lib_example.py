#-*-coding:utf-8 -*-
import pyupbit
import talib

import numpy as np
import tulipy as ti

#####################################
#####################################
# TA-Lib를 설치하고 사용한 예제입니다!!!
# 자세한건 유튜브 영상을 참고하세요 ^^
# https://youtu.be/Jqw8jijbF0E
#####################################
#####################################

ticker = 'KRW-BTC'

df = pyupbit.get_ohlcv(ticker,interval="day") #일봉 데이타를 가져온다.


integer = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
print(integer[-1],integer[-2]) #현재 캔들 기준의 값과 이전 캔들 기준의 값
print(integer.to_string())



#볼린저 밴드 값을 가져온다.
upperband, middleband, lowerband = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

print("--------------------BBANDS-------------------------")
#이전 캔들의 값
print(upperband[-2],middleband[-2],lowerband[-2])

#현재 캔들의 값(변동 중...)
print(upperband[-1],middleband[-1],lowerband[-1])
print("---------------------------------------------------")




print("-------------------CCI-------------------------")
real = talib.CCI(df['high'],df['low'],df['close'], timeperiod=20)
print(real[-1], real[-2]) #현재 캔들 기준의 값과 이전 캔들 기준의 값





print("-------------------STOCHRSI--------------------------")



fastk, fastd = talib.STOCHRSI(df['close'], timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0)
print(fastk[-2],fastd[-2])
print(fastk[-1],fastd[-1])



rsi = talib.RSI(df['close'], timeperiod=14)
rsinp = rsi.values
rsinp = rsinp[np.logical_not(np.isnan(rsinp))]
fastk, fastd = ti.stoch(rsinp, rsinp, rsinp, 14, 3, 3)

print("--", fastk[-2],fastd[-2])
print("--", fastk[-1],fastd[-1])


print("---------------------------------------------------")

