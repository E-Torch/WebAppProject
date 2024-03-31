class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        hrds = request.split(b"\r\n\r\n")
        self.body = hrds.pop()

        hrds = hrds.pop().decode("utf-8").split("\r\n")
        self.method, self.path, self.http_version = hrds.pop(0).split(" ")

        self.headers = {}
        self.cookies = {}
        for line in hrds:
            key, value = line.split(":", 1)
            key = key.strip()
            self.headers[key] = value.strip()

        if "Cookie" in self.headers:
            self.cookies = _cookie_parse(self.headers["Cookie"])

    def html_escape_body(self):
        body = self.body
        body = body.replace(b"&", b"&amp")
        body = body.replace(b"<", b"&lt")
        body = body.replace(b">", b"&gt")
        self.body = body


def _cookie_parse(value):
    cookies = {}
    cookie_list = value.split(";")

    for c in cookie_list:

        k, v = c.split("=")
        cookies[k.strip()] = v.strip()
    return cookies


def test_simple_get_request():
    request = Request(
        b"GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n"
    )
    assert request.method == "GET"
    assert request.path == "/"
    assert request.http_version == "HTTP/1.1"
    assert "Host" in request.headers
    assert "Connection" in request.headers
    assert request.headers["Host"] == "localhost:8080"
    assert request.headers["Connection"] == "keep-alive"
    assert request.body == b""


def test_cookie_get_request():
    request = Request(
        b"GET /host/test HTTP/1.1\r\nHost: localhost:8000\r\nConnection: keep-alive\r\n Cookie: id=X6kAw pgW29M; visits=4\r\n\r\n"
    )
    assert request.method == "GET"
    assert request.path == "/host/test"
    assert request.http_version == "HTTP/1.1"
    assert "Host" in request.headers
    assert "Connection" in request.headers
    assert "id" in request.cookies
    assert "visits" in request.cookies
    assert request.headers["Host"] == "localhost:8000"
    assert request.headers["Connection"] == "keep-alive"
    assert request.cookies["id"] == "X6kAw pgW29M"
    assert request.cookies["visits"] == "4"
    assert request.body == b""
    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct


def test_body_get_request():
    request = Request(
        b"GET /body HTTP/1.1\r\nHost: localhost:5000\r\nConnection: keep-alive\r\nCookie: id=X645a6AST; visits=3; =15\r\n\r\nHello World!"
    )
    assert request.method == "GET"
    assert request.path == "/body"
    assert request.http_version == "HTTP/1.1"
    assert "Host" in request.headers
    assert "Connection" in request.headers
    assert "id" in request.cookies
    assert "visits" in request.cookies
    assert "" in request.cookies
    assert request.headers["Host"] == "localhost:5000"
    assert request.headers["Connection"] == "keep-alive"
    assert request.cookies["id"] == "X645a6AST"
    assert request.cookies["visits"] == "3"
    assert request.cookies[""] == "15"
    assert request.body == b"Hello World!"


def test_simple_post_request():
    request = Request(
        b"POST /path HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 5\r\nCookie: Expires=Wed, 7 Feb 2024 16:35:00 GMT\r\n\r\nhello"
    )
    assert request.method == "POST"
    assert request.path == "/path"
    assert request.http_version == "HTTP/1.1"
    assert "Content-Type" in request.headers
    assert "Content-Length" in request.headers
    assert "Expires" in request.cookies
    assert request.cookies["Expires"] == "Wed, 7 Feb 2024 16:35:00 GMT"
    assert request.headers["Content-Type"] == "text/plain"
    assert request.headers["Content-Length"] == "5"
    assert request.body == b"hello"


if __name__ == "__main__":
    test_simple_get_request()
    test_cookie_get_request()
    test_body_get_request()
    test_simple_post_request()
    print("all test passed")
