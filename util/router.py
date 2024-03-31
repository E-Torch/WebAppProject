import re
from request import Request
from response import Response


class Router:
    def __init__(self):
        self.routes = []
        self.NotFound = Response(
            "404 Not Found", "no route exist", "text/plain"
        ).makeResponse()
        pass

        # A method named "add_route" that takes 3 parameters: The HTTP method (str), the path (str), a function that takes a Request object (from your util/request.py file) and returns a byte array (bytes) that will be the bytes of the response that will be sent to the client. The add_route method itself does not return anything. The function that is the third parameter does return bytes

    def add_route(self, http_method: str, path: str, on_route):
        regex = r"{}".format(path)
        for item in self.routes:
            if item["pattern"] == regex:
                item[http_method] = on_route
                return
        self.routes.append({"pattern": path, http_method: on_route})

    def route_request(self, request: Request) -> bytes:
        for item in self.routes:
            if (
                re.match(item["pattern"], request.path) != None
                and request.method in item
            ):
                return item[request.method]()
        return self.NotFound


def index():
    return Response("200 OK", "hello world", "text/html").makeResponse()


if __name__ == "__main__":
    request = Request(
        b"GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n"
    )
    r = Router()
    res = index()
    r.add_route("GET", "/$", index)

    assert res == r.route_request(request)
    request = Request(
        b"DELETE / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n"
    )
    assert r.NotFound == r.route_request(request)
