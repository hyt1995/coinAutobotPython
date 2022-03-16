import requests

#메세지를 보냅니다.
def SendMessage(msg):
    try:

        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = 'sTt1DUNOOeYtabies1N1xxsKhev1p70X7AbruTnuy9K' #여러분의 값으로 변경

        response = requests.post(
            TARGET_URL,
            headers={
                'Authorization': 'Bearer ' + TOKEN
            },
            data={
                'message': msg
            }
        )

    except Exception as ex:
        print(ex)