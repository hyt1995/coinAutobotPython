import ccxt
import time
import pandas as pd
import pprint


access = "6SRa2x8VAxUxBEw7qc7pbPm14ptazXpMBbIWg3qVzX1cGEP835xvPtQyjzoWrJDe"
secret = "JChJP2OIWEPVCBlTBVA9ohLQ3erUkC5ZWPWkWzGfo9e53rBdJmqs9rNB8UX9Qy0K"


binance = ccxt.binance(config = {
    'apiKey':access,
    'secret':secret,
    'enableRateLimit': True,
    'options' : {
        'defaultType' : 'future'
    }
})



targetCoinTicker = "BTC/USDT"
targetCoinSymbol = "BTCUSDT"

# orders = binance.fetch_orders(targetCoinTicker)

# for order in orders:
#     print("스탑로스에서 필요한 정보를 가져오는중 :::: ", order['status'],"코인 이름", order['info']['symbol'])

abs_amt = 0.3

one_percent_amount = 0.15

# 내가 산 코인을 1%로 나누면 현재 까지 구매한 %가 나온다는디 뭔말인지 모르겠다.
buy_percent = abs_amt / one_percent_amount
print("Buy Percent : ", buy_percent)








