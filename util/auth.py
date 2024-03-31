from request import Request


def extract_credentials(request):
    fields = request.body.decode("utf-8").split("&")
    username = fields[0].split("=").pop()
    password = fields[1].split("=").pop()
    return [url_decode(username), url_decode(password)]


def validate_password(password):
    return False


def url_decode(value: str) -> str:
    while value.find("%") != -1:
        start = value.find("%")
        end = start + 3
        url = value[start:end]
        decoded_hex = int("0x" + url[1:], 16)

        value = value.replace(url, chr(decoded_hex))
    print(value)
    return value


if __name__ == "__main__":
    r = Request(
        b"POST /path HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 51\r\nCookie: Expires=Wed, 7 Feb 2024 16:35:00 GMT\r\n\r\nusername_reg=etestest%40gmail.com&password_reg=test"
    )
    test = extract_credentials(r)
    assert "etestest@gmail.com" == test[0]
    assert "test" == test[1]
