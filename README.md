python3 파일경로/파일이름


python3 testSchedule.py 




스탑로스 확인하는 곳
Position -> TP/SL for position
연필을 누르면 관련 설정이 나온다.
Last Price가 얼마일때 손절을 하겠다는 뜻이다.


Open Orders를 보면 
type - Stop Market로 스탑로스 주문이 들어간것을 확인이 가능하다.


/home/gksdudxkr/.vscode/extensions/python3

/home/gksdudxkr/coinauto/pythonCoin/testSchedule.py 



autoServer 접속 방법 - 

chmod 400 botServerKey001.pem

ssh -i "botServerKey001.pem" ec2-user@ec2-54-226-206-18.compute-1.amazonaws.com



각 봇에 대한 설명

*/5 * * * * python3 /home/ec2-user/server/coinAutobotPython/myBinance/multipleBinanceBotServer.py

/home/ec2-user/server/coinAutobotPython/myBinance

*/5 0-05 * * * python3 /home/ec2-user/server/coinAutobotPython/myUpbit/upbitbot.py
*/5 10-23 * * * python3 /home/ec2-user/server/coinAutobotPython/myUpbit/upbitbot.py





/home/ec2-user/server/coinAutobotPython/myBinance/multipleBinanceBotServer.py
/home/ec2-user/server/coinAutobotPython/myUpbit/upbitbot.py