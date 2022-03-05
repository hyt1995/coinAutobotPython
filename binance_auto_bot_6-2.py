import ccxt
import time
import pandas as pd
import pprint


#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터6까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!


access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': access, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future' # 선물거래이기 때문에
    }
})

#포지션 잡을 코인을 설정합니다.
Target_Coin_Ticker = "BTC/USDT"
Target_Coin_Symbol = "BTCUSDT"

#해당 코인의 정보를 가져옵니다
btc = binance.fetch_ticker(Target_Coin_Ticker)
#현재 종가 즉 현재가를 읽어옵니다.
btc_price = btc['close']

print(btc['close'])


#시장가 taker 0.04, 지정가 maker 0.02

#시장가 숏 포지션 잡기 
#print(binance.create_market_sell_order(Target_Coin_Ticker, 0.002))

#시장가 롱 포지션 잡기 
#print(binance.create_market_buy_order(Target_Coin_Ticker, 0.001))

# 선물거래에서는 매수 매도라는 개념이 없다 

time.sleep(0.1)

#잔고 데이타 가져오기 
balance = binance.fetch_balance(params={"type": "future"})
#pprint.pprint(balance) # 그냥 출력하면 모든 코인 잔고가 나와서 USDT코인만 가져온다

print(balance['USDT'])


amt = 0 #수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1   #레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0 #미 실현 손익..그냥 참고용 

#실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
for posi in balance['info']['positions']:
    if posi['symbol'] == Target_Coin_Symbol:
        leverage = float(posi['leverage'])
        entryPrice = float(posi['entryPrice'])
        unrealizedProfit = float(posi['unrealizedProfit']) # 아직 정해지지 않은 금액으로 지금 팔면 나오는 수익률 PNL부분이다.
        amt = float(posi['positionAmt'])

print("amt:",amt)
print("entryPrice:",entryPrice) # 평균 매입단가
print("leverage:",leverage)
print("unrealizedProfit:",unrealizedProfit)

#음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다. 숏포지션은 음수로 나오기 때문
abs_amt = abs(amt)

#0.1%증가한 금액을 의미합니다  그냥 팔면 손해기 때문에 평균매입단가에서 조금 올린 가격으로 판다. 왜냐 시장가는 수수료가 0.04이다 매수 매도 합쳐서 0.08이다 0.001은 먹어야 수익이난다.
entryPrice = entryPrice * 1.001
# 숏포지션일 경우 0.999를 곱해야한다.

#지정가 숏 포지션 잡기 
#print(binance.create_limit_sell_order(Target_Coin_Ticker, abs_amt, entryPrice))

#지정가 롱 포지션 잡기 
#print(binance.create_limit_buy_order(Target_Coin_Ticker, abs_amt, entryPriceㄴ))








