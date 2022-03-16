#-*-coding:utf-8 -*-

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

print("access_key: ", simpleEnDecrypt.encrypt(access_key))

print("scret_key: ", simpleEnDecrypt.encrypt(scret_key))

'''

upbit_access = "gAAAAABhHynXP_5VsBAOYlfeao0dflUwcs3tpcTnqpSVpkg0YoNNl2RFvgf5mJKEUQS2VaCyxCdfdBZn4ddKjBI1an0eA2iWxnPiz2ioTmzXfdj1Iq7hbYTOh2dfddddfzXqrNeYNNXM"          # 본인 값으로 변경
upbit_secret = "gAAAAABhHyoC6DsPtHH89Y9icAAWZhEds0DeMLiZrVjyGjqaE4IvVE6d_kZdfdBOcthIshxEb7F-s0_3QiZmlM87BFV7ZmEs9yskevVy5P2BcYypiuVKf64Bxa117nJ9tHhMdfgCWmlcN__"          # 본인 값으로 변경


binance_access = "gAAAAABhJe97xHR99qPag_eHvyUmUo3LY8mfdsfTvM2m1H8xmSFwzxCHpFnSpoyC2S232Uuu4wt4Twmj0Vo3uprf3O_TNzseqJmP0f0wWqvWa_i_8sx7v8Cci8XiN6tj7gdiyVH2v12IacNfgpW_-mJqN6elvIdfg0cCdqNpgQ="          # 본인 값으로 변경
binance_secret = "gAAAAABhJe973Ub7jdfsfg_3Hnord89M_0xzusMHjPXy4fW1dfsdd343AMXuh8R_PbpKl6TSGN03cNNQSqvRv5Yr_FenpyIDq94UuOfyCdCfWs2n6YXHCMRE8szIyy_hv7bcyucvbk3l7-BTeW-tjH867aae6eecJsdffkE="          # 본인 값으로 변경

bybit_access = "gAAAAABhUxuvF-Dexd5xNn5Ll8MHrCawe4JvXd_jrzMyAGqbQ_sXio3zo77DJeUJxwOiIgihE83Q_l0nOg1W7euChn_ZjBPRNubmBtZ_o70iYbgSpg_Vasg="          # 본인 값으로 변경
bybit_secret = "gAAAAABhUxuvYuBGlSim3v48xZ-vAOBUQIGS9__vVOglTnpdHWwkV-TpZrKQjMv0Nm-rVMhSskcVqgPCURlezbvha-yPfmxPS3DhUX5nJ7CTXvAMZeVnump53_RnrYgH9i-tVRyh0gxZ"          # 본인 값으로 변경
