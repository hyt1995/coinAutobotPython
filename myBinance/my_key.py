#-*-coding:utf-8 -*-


# 그전에 pip3 install Fernet 로 인스톨을 진행을 해야한다.

from cryptography.fernet import Fernet


class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou


simpleEnDecrypt = SimpleEnDecrypt(b'ycJNAQPaDHt8iGpVJ1756CQ3O9ML_OBa0xdguOKsEs0=')

binance_access = "gAAAAABiIb4sNWJsbZDVmQK5dNtnL5xLPCDS6mPSn7LYxmuJo9WafT8EeU8HbD04xAlBG7b6_x0FYclAtdMyQN2dObI-dP2OJBoD62FNu34oSBy6JMHPjiXBNGZq9a5-VVuyiDRWsoPNITOAwZ4frWFdc35H3RLkMuVJ_z6Zvt8cmZU1JRenkI0="          # 이미 변경한 값이다.
binance_secret = "gAAAAABiIb4sDY84lmb-XniHYk_9RzLX_GVjYYdxRGEnjtVpaA6BLq0erQL4jlfCLjAayLM0Z2nyKOuy-uhPVyte9MopKyRpFp7JTD6fJAa6uJzPGG0OCTQFp7HAzB1Ocay-H9OvxzY8opiIaNlTAKwxLRhaucbQi-da0nFGblAZn1CgGDXA1sk="          # 이미 변경한 값이다.


# print("바이낸스 에섹스 : ", simpleEnDecrypt.encrypt(binance_access))
# print("바이낸스 시크릿 : ", simpleEnDecrypt.encrypt(binance_secret))



















'''
여러분의 시크릿 키와 엑세스 키를 
ende_key.py에 있는 키를 활용해서 암호화한 값을 넣으세요

마찬가지 방법으로 아래 로직을 실행하시면 됩니다.. (ende_key.py 참조)

from cryptography.fernet import Fernet

class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou

         

simpleEnDecrypt = SimpleEnDecrypt(b'NcUgge50agCYGXpJmpcxsE5_0do84kKNdI6DsG-iwm8=') #ende_key.py 에 있는 키를 넣으세요

access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경


print("access_key: ", simpleEnDecrypt.encrypt(access))

print("scret_key: ", simpleEnDecrypt.encrypt(secret))

'''