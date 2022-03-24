import requests


# data = {
#     "name" : "korpc",
#     "password" : "Korpcdream21!"
# }

# response = requests.post("http://localhost:5001/coinServer/userInfo/account",json=data)


data = {
    "storeName" : "upbit",
}

response = requests.post("http://localhost:5001/coinServer/userInfo/getStore",json=data)


# data = {
#     "storeName" : "binance",
# }

# response = requests.post("http://localhost:5001/coinServer/userInfo/getUserInfo",json=data)






print("접속 후 결과값을 확인을 위해 ::::::", response)