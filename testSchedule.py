

init = 0.0010871549866824505


first = str(init).split("0")
print("~~~~~~~~~~~",first,"나눈 값  split :::", str(init).split("0"))

splitRe = ""

for int in first:
    print("하나하나 출력", int)
    if int and int != ".":
        sec = str(init).split(int)
        print(sec)

        thir = sec[0] + int
        print(thir)

        first = float(thir)
        print("~~~~~~~~~~~",first)

        break


print("결국에는 뭐가 드어옴???????::::::", first)