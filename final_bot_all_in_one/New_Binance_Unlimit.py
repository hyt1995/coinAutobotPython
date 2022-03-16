import ccxt
import time
import pandas as pd
import pprint

import myBinance
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

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


'''
라오어 미국주식 무한매수법을 변형한 코인 무한매수봇
지표 안보고 그냥 비중조절만 하는 약간 무식한 방법??

즉 매일 매일 조금씩 모아가서 물타기 효과! 코스트에버리징 효과를 극대화화는 전략으로
많은 분들이 미국주식 ETF 으로 높은 수익율을 기록하고 있다는 매매전략입니다!

무엇보다 스탑로스를 주석처리해서 걸지 않는 리스크한 봇입니다.
필요하시다면 주석을 풀어서 거세요 ^^ 

저는 잘게 쪼개서 분할매수하는 거고 저 레버 3을 쓸꺼라 스탑로스 안걸고 한번 가봅니다 ㅎ

이번 바이낸스 봇은 강의에서와는 다르게
선물거래되는 모든 코인을 대상으로 for문을 돌면서 포지션을 잡아볼것입니다.

거래량이 많은 탑코인 구하는 함수를 추가해서 사용했습니다.

레버는 모든 코인 3배로 고정하고
가장 비싼 비트코인의 최고 매수수량인 0.001을 레버 3배썼을 때 $15 정도가 드니깐
넉넉잡아 20$를 1/40으로 잡으면 $800가 1코인 당 할당 금액이 됩니다.

즉 원금이 300만원 정도면 3개 정도 살수 있겠네요~~

이래서 제가 비트코인,이더리움만 봇을 만들었고
반복문을 돌면서 모든 코인을 포지션 잡지 않았던 겁니다.

또 다른 코인들은 레버3배를 써도 순식간에 20%오르거나 내리는 코인도 있어서
따라서 특정 코인만 거래하게 제약을 두는 방식을 추천드리지만 

일단 여기서는 거래대금이 많은 코인 대상으로 한번 해보겠습니다.
1코인당 최대 매수금액은 $800이라는 제한을 두구요.
따라서 최대매수코인 개수가 존재합니다. (아래 코드에 나옵니다)

측 최대 매수 코인이 2개일 경우 2개를 포지션 잡으면 그 이 후는 신규 매수하지 않습니다.


일단 원금을 40으로 나눈다.

1/40을 산다. 이를 첫 매수 금액이라고 칭하자
바이낸스 선물이므로 포지션을 잡아야 하는데.

해당 봇은 1시간마다 돕니다.

하지만 매일 9시에만 추가매수를 합니다

그런데 왜 1시간마다 도느냐?
그날 장 중에 매도를 하면 최대 매수코인 개수에 미달하게 되고
신규 매수 기회가 생깁니다. 그때 매수(포지션 잡기)를 하기 위함입니다.
즉 현재 매수 코인 개수가 최대 매수 코인 개수보다 작은 상황이라면
1시간 마다 도는 봇이 첫 매수에 들어가게 되는 구조입니다.

첫 매수(포지션)일 경우
RSI지표가 40이하면 롱을 잡고
RSI지표가 60이상이면 솟을 잡도록 합니다. - 그냥 제가 정한 기준.

그리고 현재 평단의 마이너스 5%이상 손실이 난다면 - 그냥 제가 정한 기준입니다. 맘대로 바꾸세요

첫 매수 금액 만큼을 추가 포지션을 잡고

그 밖의 경우는 첫 매수 금액의 절반을 추가 포지션을 잡습니다.
(물론 최소 수량보다 작아지면 최소 수량으로 포지션을 잡습니다.
비트코인의 경우 0.001개)

레버리지는 일봉을 보고 장기 분할매수이므로 레버는 라오어 미국주식 무한매수법처럼 3배를 추천합니다.
레버리지 반영한 수익이 10% 이상일때 지정가 매도를 걸어 팔아버립니다.

다 팔았다면
다시 처음으로 돌아가 1/40을 삽니다.


크론탭에 매 1시간마다 실행되게 등록합니다.

0 */1 * * * python3 /var/autobot/New_Binance_Unlimit.py

이런 식으로 등록하면 되지만 마음대로 바꾸세요!


'''



#시장가 taker 0.04, 지정가 maker 0.02

#시장가 숏 포지션 잡기 
#print(binance.create_market_sell_order(Target_Coin_Ticker, 0.002))

#시장가 롱 포지션 잡기 
#print(binance.create_market_buy_order(Target_Coin_Ticker, 0.001))


#지정가 숏 포지션 잡기 
#print(binance.create_limit_sell_order(Target_Coin_Ticker, abs_amt, entryPrice))

#지정가 롱 포지션 잡기 
#print(binance.create_limit_buy_order(Target_Coin_Ticker, abs_amt, btc_price))





#잔고 데이타 가져오기 
balances = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)
pprint.pprint(balances)


print(balances['USDT'])
print("Total Money:",float(balances['USDT']['total']))
print("Remain Money:",float(balances['USDT']['free']))

TotalMoney = float(balances['USDT']['total'])






#시간 정보를 가져옵니다. 
#아침 9시에만 코인을 매수(포지션 잡기)를 하기 위해 시간 체크가 필요합니다.
#매일 9시에 한번만 실행되게 봇을 설정해도 되지만 1시간마다 봇을 돌게 해놨습니다.
#이유는 장중에 수익화가 되어 코인이 매도되면 자리가 남기에 코인을 추가 매수하기 위함입니다.
#즉 9시가 아닌 시간에는 추가 매수만 되고(자리가 남았으면) 물타기(기존 매수된 코인을 추가매수)는 막아야 하기에 필요한 시간 정보입니다
time_info = time.gmtime()
hour = time_info.tm_hour
print("HOUR:",hour)





#내가 매수할 총 코인 개수
#원금이 $2400이라 가정하면 최대 3개까지 가능합니다. 한 코인당 $800..이를 40분할하면 한번에 $20씩!
#따라서 내 원금을 $800로 나누면 가능한 코인 개수가 나옵니다.
MaxCoinCnt = int(TotalMoney / 800.0)
print("MaxCoinCnt : ", MaxCoinCnt)


#선물 마켓에서 거래중인 모든 코인을 가져옵니다.
Tickers = binanceX.fetch_tickers()

#선물 테더(USDT) 마켓에서 거래중인 코인을 거래대금이 많은 순서로 가져옵니다. 여기선 Top 10
TopCoinList = myBinance.GetTopCoinList(binanceX,10)


#현재 포지션 잡은 코인개수를 구하는 함수를 myBinance에 만들었습니다.
NowCoinCnt = myBinance.GetHasCoinCnt(binanceX)


#모든 선물 거래가능한 코인을 가져온다.
for ticker in Tickers:

    try: 

        print("######## NowCoinCnt : ", NowCoinCnt)

   
        #하지만 여기서는 USDT 테더로 살수 있는 모든 선물 거래 코인들을 대상으로 돌려봅니다.
        if "/USDT" in ticker:
            Target_Coin_Ticker = ticker
            Target_Coin_Symbol = ticker.replace("/", "")


            print("----------------", ticker)


            #레버리지를 3으로 셋팅합니다
            #앱이나 웹에서 레버리지를 바뀌면 바뀌니깐 주의하세요!!
            try:
                print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': 3}))
            except Exception as e:
                print("---:", e)

            #아직 맥스 코인만큼 사지 않았다!
            if NowCoinCnt < MaxCoinCnt:
                #위 레버리지를 반영하려면 잔고 데이타를 다시 가져와야한다 그런데 시간이 오래걸리므로 코인을 지정된 수량만큼 사기 전에만 호출하자! 
                balances = binanceX.fetch_balance(params={"type": "future"})
                time.sleep(0.1)


            amt = 0 #수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
            entryPrice = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
            leverage = 3   #레버리지, 앱이나 웹에서 설정된 값을 가져온다.
            unrealizedProfit = 0 #미 실현 손익..그냥 참고용 
            isolated = True #격리모드인지 

            #실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
            for posi in balances['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol:
                    amt = float(posi['positionAmt'])
                    entryPrice = float(posi['entryPrice'])
                    leverage = float(posi['leverage'])
                    unrealizedProfit = float(posi['unrealizedProfit'])
                    isolated = posi['isolated']
                    break

            #격리모드로 셋팅합니다.
            if isolated == False:
                try:
                    print(binanceX.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                except Exception as e:
                    print("---:", e)

                    

            print("amt:",amt)
            print("entryPrice:",entryPrice)
            print("leverage:",leverage)
            print("unrealizedProfit:",unrealizedProfit)


            #최소 주문 수량을 가져온다 
            minimun_amount = binanceX.markets[Target_Coin_Ticker]['limits']['market']['min']

            print("minimun_amount : ", minimun_amount)


            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

            #레버리지에 따른 최대 매수 가능 수량 - 한 코인당 설정된 $800에 해당하는 수량 
            Max_Amount = round(myBinance.GetAmount(TotalMoney,coin_price, 800.0 / TotalMoney ),3) * leverage 

            #매수할 수량을 구합니다.
            buy_amount = Max_Amount / 40.0

            print("buy_amount : ", buy_amount) 

            #코인별 최소 매수 수량보다 작다면 최소매수수량으로 바꿔준다
            if minimun_amount > buy_amount:
                buy_amount = minimun_amount

    

            #음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
            abs_amt = abs(amt)

            #타겟 레이트 0.1 즉 10%를 의미하는데 레버리지를 나눠서 실제 레버리지를 곱한 수익이 10%가 되도록 만든다.
            target_rate = 0.1 / leverage
            #타겟 수익율 10%
            target_revenue_rate = target_rate * 100.0


   
            #제 무한매수법에는 스탑로스는 없습니다. 필요하다면 거세요. 저는 리스크 지고 가즈아!!!
            #stop_loass_rate = 0.5


            #0이면 포지션 잡기전
            if amt == 0:
                print("-----------------------------No Position---------------------------------")

                #############################################################################
                #아래 주석처리된 부분처럼 선물거래할 코인을 지정하는 것도 방법입니다.
                #초보자 분껜 이 방법을 추천합니다. 변동성이 심한 코인은 포지션 잘못 잡으면 청산당할 확율이 높습니다.
                #if ticker == "ETH/USDT" or ticker == "BTC/USDT" and NowCoinCnt < MaxCoinCnt: #이더리움 비트코인만 대상으로..
                ##############################################################################
                

                #탑 코인 리스트에 있는 코인만 포지션을 잡을 수 있습니다!
                if myBinance.CheckCoinInList(TopCoinList,ticker) == True and NowCoinCnt < MaxCoinCnt:
                    print("this coin is TOP!!")

                    time.sleep(0.1)
                    df = myBinance.GetOhlcv(binanceX,Target_Coin_Ticker, '1h')

                    #RSI14 정보를 가지고 온다.
                    rsi14 = myBinance.GetRSI(df, 14, -1)


                    #RSI가 60 이상라면 숏 포지션을 잡아줍니다.
                    #저는 RSI지표를 봤는데 당연히 다른 지표를 봐도 됩니다!
                    if rsi14 >= 60 :
                        print("-----------------------sell/short")
                        #주문 취소후
                        binanceX.cancel_all_orders(Target_Coin_Ticker)
                        time.sleep(0.1)

                        #해당 코인 가격을 가져온다.
                        coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                        #숏 포지션을 잡는다 10%의 수익을 노리기에 시장가로 포지션을 잡는다.
                        print(binanceX.create_market_sell_order(Target_Coin_Ticker, buy_amount))

                        #스탑 로스 설정을 건다.
                        #myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)

                        
                        #롱 포지션을 걸어 수익화 라인을 그어준다 
                        print(binanceX.create_limit_buy_order(Target_Coin_Ticker, buy_amount, coin_price * (1.0 - target_rate)))

                        NowCoinCnt = myBinance.GetHasCoinCnt(binanceX)


                    # RSI가 40 이하라면 롱 포지션을 잡아줍니다.
                    #저는 RSI지표를 봤는데 당연히 다른 지표를 봐도 됩니다!
                    if rsi14 <= 40 :
                        print("-----------------------buy/long")
                        #주문 취소후
                        binanceX.cancel_all_orders(Target_Coin_Ticker)
                        time.sleep(0.1)
                        
                        #해당 코인 가격을 가져온다.
                        coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                        #롱 포지션을 잡는다 10%의 수익을 노리기에 시장가로 포지션을 잡는다.
                        print(binanceX.create_market_buy_order(Target_Coin_Ticker, buy_amount))

                        #스탑 로스 설정을 건다.
                        #myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)

                        
                        
                        #숏 포지션을 걸어 수익화 라인을 그어준다 
                        print(binanceX.create_limit_sell_order(Target_Coin_Ticker, buy_amount, coin_price * (1.0 + target_rate)))

                        NowCoinCnt = myBinance.GetHasCoinCnt(binanceX)


            #0이 아니라면 포지션 잡은 상태
            else:
                print("------------------HAS COIN------------------------")

                #수익율을 구한다!
                revenue_rate = (coin_price - entryPrice) / entryPrice * 100.0
                #단 숏 포지션일 경우 수익이 나면 마이너스로 표시 되고 손실이 나면 플러스가 표시 되므로 -1을 곱하여 바꿔준다.
                if amt < 0:
                    revenue_rate = revenue_rate * -1.0

                #레버리지를 곱한 실제 수익율
                leverage_revenu_rate = revenue_rate * leverage

                print("Revenue Rate : ", revenue_rate,", Real Revenue Rate : ", leverage_revenu_rate)

                #물탈 돈의 1/2를 실제로 물탈돈으로 셋팅하지만 
                water_buy_amount = buy_amount * 0.5

                #수익율이 레버리지 반영한 마이너스 10%보다 작다면 물탈 돈을 온전히 탄다.
                if leverage_revenu_rate < -10.0:
                    water_buy_amount = buy_amount


                #코인별 최소 매수 수량보다 작다면 최소매수수량으로 바꿔준다
                if minimun_amount > water_buy_amount:
                    water_buy_amount = minimun_amount


                #위험 마이너스 수익율을 셋팅한다. 단 레버리지를 나눠서 실제 원금의 손실율을 직관적으로..
                danger_rate = -50.0 / leverage
                #레버리지를 곱한 실제 손절 할 마이너스 수익율
                leverage_danger_rate = danger_rate * leverage

                print("Danger Rate : ", danger_rate,", Real Danger Rate : ", leverage_danger_rate)


                ########### 추가 매수(물타기)는 9시에만 탑니다. 
                #혹은 손실율이 마이너스 50%까지 왔을 경우 청산을 막기 위해 물을 탑니다. ###########
                if hour == 0 or danger_rate > revenue_rate:
        
  


                    #음수면 숏 포지션 상태
                    if amt < 0:
                        print("##################################-----Short Position")

                        
                        if Max_Amount >= abs_amt + water_buy_amount:

                            #주문 취소후
                            binanceX.cancel_all_orders(Target_Coin_Ticker)
                            time.sleep(0.1)
                                
                            #해당 코인 가격을 가져온다.
                            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                            #숏 포지션을 잡는다
                            print(binanceX.create_market_sell_order(Target_Coin_Ticker, water_buy_amount))

                            #스탑 로스 설정을 건다.
                            #myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)


                            #잔고 데이타를 다시 가져온다
                            time.sleep(0.1)
                            balance = binanceX.fetch_balance(params={"type": "future"})


                            amt = 0
                            entryPrice = 0


                            for posi in balance['info']['positions']:
                                if posi['symbol'] == Target_Coin_Symbol:
                                    entryPrice = float(posi['entryPrice'])
                                    amt = float(posi['positionAmt'])


                            #롱 포지션을 잡아 수익화 라인을 그어준다
                            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs(amt), entryPrice * (1.0 - target_rate)))


                    #양수면 롱 포지션 상태
                    else:
                        print("##################################------Long Position")


                        if Max_Amount >= abs_amt + water_buy_amount:

                            #주문 취소후
                            binanceX.cancel_all_orders(Target_Coin_Ticker)
                            time.sleep(0.1)
                                
                            #해당 코인 가격을 가져온다.
                            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                            #롱 포지션을 잡는다
                            print(binanceX.create_market_buy_order(Target_Coin_Ticker, water_buy_amount))

                            #스탑 로스 설정을 건다.
                            #myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)



                            #잔고 데이타를 다시 가져온다
                            time.sleep(0.1)
                            balance = binanceX.fetch_balance(params={"type": "future"})


                            amt = 0
                            entryPrice = 0


                            for posi in balance['info']['positions']:
                                if posi['symbol'] == Target_Coin_Symbol:
                                    entryPrice = float(posi['entryPrice'])
                                    amt = float(posi['positionAmt'])


                            #숏 포지션을 잡아 수익화 라인을 그어준다
                            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs(amt), entryPrice * (1.0 + target_rate)))


            #if amt != 0:
            #    myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)




    except Exception as e:
        print("---:", e)



