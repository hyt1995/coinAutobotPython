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
바이낸스에 전체 선물 거래 코인 리스트를 돌면서
매매하는 봇은 무한매수법 변형 봇밖에 없는데
참고하시라고 볼린저 밴드를 활용한 봇도 만들었습니다.

볼린저 밴드 상단을 뚫으면 숏을 잡고
하단을 뚫으면 롱을 잡습니다.

10개의 코인을 최대치로 잡고
원금 1/10씩 나눈 걸 코인당 최대 매수 금액으로 잡습니다.

레버는 3배로 잡습니다.

여러가지로 변형을 해놨으니 한줄 한줄 살펴보세요!

15분봉을 보고 15분마다 돕니다.


*/15 * * * * python3 /var/autobot/New_Binance_All_BB.py

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
#pprint.pprint(balances)


print(balances['USDT'])
print("Total Money:",float(balances['USDT']['total']))
print("Remain Money:",float(balances['USDT']['free']))

TotalMoney = float(balances['USDT']['total'])

#내가 매수할 총 코인 개수
MaxCoinCnt = 10.0
print("MaxCoinCnt : ", MaxCoinCnt)


#선물 마켓에서 거래중인 모든 코인을 가져옵니다.
Tickers = binanceX.fetch_tickers()

#선물 테더(USDT) 마켓에서 거래중인 코인을 거래대금이 많은 순서로 가져옵니다. 여기선 Top 25
TopCoinList = myBinance.GetTopCoinList(binanceX,25)


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


            print("--------0--------", ticker)
            time.sleep(0.05)
            #최소 주문 수량을 가져온다 
            minimun_amount = binanceX.markets[Target_Coin_Ticker]['limits']['market']['min']

            print("minimun_amount : ", minimun_amount)


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

            print("---------2-------", ticker)

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

                    
            print("---------3-------", ticker)

            print("amt:",amt)
            print("entryPrice:",entryPrice)
            print("leverage:",leverage)
            print("unrealizedProfit:",unrealizedProfit)

            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)


            #레버리지에 따른 최대 매수 가능 수량
            Max_Amount = round(myBinance.GetAmount(float(balances['USDT']['total']),coin_price,1.0 / MaxCoinCnt),3) * leverage 

            #최대 매수수량의 1%에 해당하는 수량을 구한다.
            one_percent_amount = Max_Amount / 100.0

            print("one_percent_amount : ", one_percent_amount) 

            #첫 매수 비중을 구한다.. 여기서는 20%!
            first_amount = one_percent_amount * 20.0

            if first_amount < minimun_amount:
                first_amount = minimun_amount

            print("first_amount : ", first_amount) 


            #매수할 수량을 구합니다.
            water_amount = one_percent_amount * 10.0

            if water_amount < minimun_amount:
                water_amount = minimun_amount

            print("water_amount : ", water_amount) 

            #음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
            abs_amt = abs(amt)

            #타겟 레이트 0.01 즉 1%를 의미한다
            target_rate = 0.01 
            target_revenue_rate = target_rate * 100.0


            #스탑로스
            stop_loass_rate = 0.5

            print("---------4-------", ticker)

            time.sleep(0.1)
            #캔들 정보 가져온다 여기서는 15분봉을 보지만 자유롭게 조절 하세요!!!
            df = myBinance.GetOhlcv(binanceX,Target_Coin_Ticker, '15m')

            time.sleep(0.1)
            #상위 캔들 정보 가져온다 여기서는 4시간 봉을 보지만 자유롭게 조절 하세요!!!
            df_up = myBinance.GetOhlcv(binanceX,Target_Coin_Ticker, '4h')


            
            print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
            ################################새로 추가된 지표 참고용으로 필요하시면 봇에 활용해 보세요!##############################################################

            #---------------------------------------------#
            #아래 지표들 구할때 제가 현재 캔들을 -1 이 아니라 -2로 
            #이전 캔들을 -2가 아니라 -3으로 수정했습니다. 이유는 https://blog.naver.com/zacra/222567868086 참고하세요!
            #---------------------------------------------#


            #볼린저 밴드 구하는 함수는 실제 차트와 다소 오차가 존재하지만 활용하는데는 무리가 없습니다!
            #볼린저 밴드 함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 upper가 상단, ma는 기준이 되는 이동평균선(여기선 20일선),lower가 하단이 됩니다.
            print("-----------------------------------------------")
            #이전 캔들의 볼린저 밴드 상하단
            BB_dic_before = myBinance.GetBB(df,20,-3)
            print("before - MA:",BB_dic_before['ma'],", Upper:", BB_dic_before['upper'] ,", Lower:" ,BB_dic_before['lower'])

            print("-----------------------------------------------")
            #현재 볼린저 밴드 상하단
            BB_dic_now = myBinance.GetBB(df,20,-2)
            print("now - MA:",BB_dic_now['ma'],", Upper:", BB_dic_now['upper'] ,", Lower:" ,BB_dic_now['lower'])



            #MACD값을 구해줍니다!
            #MACD함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 macd는 MACD값, macd_siginal값이 시그널값, ocl이 오실레이터 값이 됩니다
            print("-----------------------------------------------")
            macd_before = myBinance.GetMACD(df,-3) #이전캔들의 MACD
            print("before - MACD:",macd_before['macd'], ", MACD_SIGNAL:", macd_before['macd_siginal'],", ocl:", macd_before['ocl'])
            print("-----------------------------------------------")
            macd = myBinance.GetMACD(df,-2) #현재캔들의 MACD
            print("now - MACD:",macd['macd'], ", MACD_SIGNAL:", macd['macd_siginal'],", ocl:", macd['ocl'])




            #일목균형표(일목구름) 구해줍니다!
            #일목균형표(일목구름)함수는 아래와 같이 딕셔너리 형식으로 값을 리턴하며 conversion는 전환선, base는 기준선
            #huhang_span은 후행스팬, sunhang_span_a는 선행스팬1, sunhang_span_b는 선행스판2 입니다.
            print("-----------------------------------------------")
            ic_before = myBinance.GetIC(df,-3) #이전캔들의 일목균형표
            print("before - Conversion:",ic_before['conversion'], ", Base:", ic_before['base'],", HuHang_Span:", ic_before['huhang_span'],", SunHang_Span_a:", ic_before['sunhang_span_a'],", SunHang_Span_b:", ic_before['sunhang_span_b'])

            print("-----------------------------------------------")
            ic = myBinance.GetIC(df,-2) #현재캔들의 일목균형표
            print("now - Conversion:",ic['conversion'], ", Base:", ic['base'],", HuHang_Span:", ic['huhang_span'],", SunHang_Span_a:", ic['sunhang_span_a'],", SunHang_Span_b:", ic['sunhang_span_b'])




            print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")





            #이전 캔들의 종가 
            price_before = df['close'][-2]
            #현재가
            price_now = df['close'][-1]


            #################################################################################################################
            #################################################################################################################
            #################################################################################################################
            #################################################################################################################
            #################################################################################################################

            #반드시 이 글을 읽고 수정하세요 https://blog.naver.com/zacra/222567868086
            # 지표를 활용할 때 현재 캔들 -1 과 이전 캔들 -2는 값이 같아지는 경우가 생길 수 있습니다. 
            # (봇이 캔들이 변경되는 시점에 주로 실행되기에 이 경우 현재 캔들 기준으로 구한 지표 값과 이전 캔들 기준으로 구한 지표 값이 동일해 지는 상황압니다,)
            # 따라서 이전 캔들 -2, 이이전 캔들 -3으로 조합해야 원하는 결과를 얻을 수 있습니다.
            # 쉽게 이야기해서 현재 캔들을 -2, 이전 캔들을 -3으로 보는게 좋다는 거죠. 어자피 진짜 현재 캔들 -1과 이전 캔들 -2의 값이 보통 같을테니까요. 
            # (이전 캔들의 종가와 현재 캔들의 시가가 거의 같은 경우가 많으니까요!)

            #################################################################################################################
            #################################################################################################################
            #################################################################################################################
            #################################################################################################################
            #################################################################################################################


            #0이면 포지션 잡기전
            if amt == 0:
                print("-----------------------------No Position---------------------------------")


                #탑 코인 리스트에 있는 코인만 포지션을 잡을 수 있습니다!
                if myBinance.CheckCoinInList(TopCoinList,ticker) == True and NowCoinCnt < MaxCoinCnt:
                    print("this coin is TOP!!")

        
                    #현재 캔들이 볼린저 밴드 상단을 뚫었다.
                    if float(price_now) > float(BB_dic_now['upper']):
                        print("-----------------------sell/short")
                        #주문 취소후
                        binanceX.cancel_all_orders(Target_Coin_Ticker)
                        time.sleep(0.1)

                        #상위 캔들이 상승하고 있다면 롱을 잡아준다 (추세추종)
                        if df_up['close'][-2] < df_up['close'][-1]:

                            #롱 포지션을 잡는다 시장가로 포지션을 잡는다.
                            print(binanceX.create_market_buy_order(Target_Coin_Ticker, first_amount))

                            #숏 포지션을 걸어 수익화 라인을 그어준다 
                            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price * (1.0 + target_rate)))

                        #아니라면 숏을 잡아주자 (추세전환)
                        else:

                            #숏 포지션을 잡는다 시장가로 포지션을 잡는다.
                            print(binanceX.create_market_sell_order(Target_Coin_Ticker, first_amount))

                            
                            #롱 포지션을 걸어 수익화 라인을 그어준다 
                            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price * (1.0 - target_rate)))



                        NowCoinCnt = myBinance.GetHasCoinCnt(binanceX)

                    #현재 캔들이 볼린저 밴드 하단을 뚫었다.
                    if float(price_now) < float(BB_dic_now['lower']):
                        print("-----------------------buy/long")
                        #주문 취소후
                        binanceX.cancel_all_orders(Target_Coin_Ticker)
                        time.sleep(0.1)

                        #상위 캔들이 하락하고 있다면 숏을 잡아준다 (추세추종)
                        if df_up['close'][-2] > df_up['close'][-1]:

                            #숏 포지션을 잡는다 시장가로 포지션을 잡는다.
                            print(binanceX.create_market_sell_order(Target_Coin_Ticker, first_amount))

                            #롱 포지션을 걸어 수익화 라인을 그어준다 
                            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price * (1.0 - target_rate)))
                            
                        #아니라면 롱을 잡아주자 (추세전환)
                        else:
                        
                            #롱 포지션을 잡는다 노리기에 시장가로 포지션을 잡는다.
                            print(binanceX.create_market_buy_order(Target_Coin_Ticker, first_amount))
                            
                            #숏 포지션을 걸어 수익화 라인을 그어준다 
                            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price * (1.0 + target_rate)))

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


                #현재까지 구매한 퍼센트! 즉 비중!! 현재 보유 수량을 1%의 수량으로 나누면 된다.
                buy_percent = abs_amt / one_percent_amount
                print("Buy Percent : ", buy_percent)

                #비중에 따라 스탑로스를 정하자
                #비중이 늘어날수록 스탑로스는 0.5까지 커진다.
                stop_loass_rate = (100 - (buy_percent / 2.0))/100.0
              

                water_rate = -5.0
                if buy_percent < 40.0:
                    water_rate = -5.0
                elif buy_percent < 60:
                    water_rate = -10.0
                elif buy_percent < 80:
                    water_rate = -20.0



                
                #레버리지 반영한 수익율이 water_rate보다 작을때만 물을 탄다.
                if leverage_revenu_rate < water_rate:
        

                    #음수면 숏 포지션 상태
                    if amt < 0:
                        print("##################################-----Short Position")

                        #숏인데 이전 캔들이 상단을 또 뚫었고 레버 수익율이 water_rate 이하 일때 물을 타자!
                        if (float(price_before) > float(BB_dic_before['upper']) and leverage_revenu_rate < water_rate) and Max_Amount >= abs_amt + water_amount:

                            #주문 취소후
                            binanceX.cancel_all_orders(Target_Coin_Ticker)
                            time.sleep(0.1)
                                
                            #해당 코인 가격을 가져온다.
                            #coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                            #숏 포지션을 잡는다
                            print(binanceX.create_market_sell_order(Target_Coin_Ticker, water_amount))

                            #스탑 로스 설정을 건다.
                            #myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)


                            #잔고 데이타를 다시 가져온다
                            time.sleep(0.1)
                            balances = binanceX.fetch_balance(params={"type": "future"})


                            amt = 0
                            entryPrice = 0


                            for posi in balances['info']['positions']:
                                if posi['symbol'] == Target_Coin_Symbol:
                                    entryPrice = float(posi['entryPrice'])
                                    amt = float(posi['positionAmt'])


                            #롱 포지션을 잡아 수익화 라인을 그어준다
                            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs(amt), entryPrice * (1.0 - target_rate)))


                    #양수면 롱 포지션 상태
                    else:
                        print("##################################------Long Position")

                        #롱인데 이전 캔들이 하단을 또 뚫었고 레버 수익율이 water_rate 이하 일때 물을 타자!
                        if (float(price_before) < float(BB_dic_before['lower']) and leverage_revenu_rate < water_rate) and Max_Amount >= abs_amt + water_amount:

                            #주문 취소후
                            binanceX.cancel_all_orders(Target_Coin_Ticker)
                            time.sleep(0.1)
                                
                            #해당 코인 가격을 가져온다.
                            #coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

                            #롱 포지션을 잡는다
                            print(binanceX.create_market_buy_order(Target_Coin_Ticker, water_amount))

                            #스탑 로스 설정을 건다.
                            #myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)



                            #잔고 데이타를 다시 가져온다
                            time.sleep(0.1)
                            balances = binanceX.fetch_balance(params={"type": "future"})


                            amt = 0
                            entryPrice = 0


                            for posi in balances['info']['positions']:
                                if posi['symbol'] == Target_Coin_Symbol:
                                    entryPrice = float(posi['entryPrice'])
                                    amt = float(posi['positionAmt'])


                            #숏 포지션을 잡아 수익화 라인을 그어준다
                            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs(amt), entryPrice * (1.0 + target_rate)))


            if amt != 0:
                myBinance.SetStopLoss(binanceX,Target_Coin_Ticker,stop_loass_rate)




    except Exception as e:
        print("---:", e)



