# from request import Request


import re


def extract_credentials(request):
    fields = request.body.decode("utf-8").split("&")
    username = fields[0].split("=").pop()
    password = fields[1].split("=").pop()
    return [url_decode(username), url_decode(password)]


def validate_password(password):
    pattern = r"^(?=\S*[a-z])(?=\S*[A-Z])(?=\S*[0-9])(?=\S*[!@#$%^&()\-_=])[a-zA-Z0-9!@#$%^&()\-_=]{8,}$"
    return re.match(pattern, password) != None


def url_decode(value: str) -> str:
    start = 0
    v = value.split("%")
    if v[0] != "%":
        start = 1
    for i in range(start, len(v)):
        item: str = v[i]
        str_hex = item[:2]
        decoded_hex = int("0x" + str_hex, 16)
        item = item.replace(str_hex, chr(decoded_hex))
        v[i] = item

    return "".join(v)


if __name__ == "__main__":
    assert validate_password("Password!@1234")
    assert validate_password("!@Google2024")
    assert validate_password("9#oGGGSD")
    assert validate_password("#9oGGGSD!@#$%^&()-_=")
    assert validate_password("!@#$%^&()-_=9oGGGSD")
    assert validate_password("P1g!@#$#")
    assert validate_password("1)AASDASDASDSDAs")
    assert not validate_password("#9o GGG SD asd 98")
    assert not validate_password("1532415648964789")
    assert not validate_password("1532415648964789")
    assert not validate_password("!@#$%^&()-_=")
    assert not validate_password("ADWQEQREFSDGAFDHUJDS")
    assert not validate_password("aashgdjksadhjkhaksjsa")
    assert not validate_password("!@#@ERE@%$RTSDRT34532 343214 32asfdasdferwe")
    assert not validate_password("P1g!@#$t+")
    assert not validate_password("+P1g!\n\t@#$t+")
    assert not validate_password(" !@1Password")
    assert not validate_password("!@1Password ")
#     r = Request(
#         b"POST /path HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 51\r\nCookie: Expires=Wed, 7 Feb 2024 16:35:00 GMT\r\n\r\nusername_reg=etestest%40gmail.com&password_reg=test"
#     )
#     test = extract_credentials(r)
#     assert "etestest@gmail.com" == test[0]
#     assert "test" == test[1]
