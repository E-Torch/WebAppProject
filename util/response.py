from array import array


class Response:

    def __init__(self, status, body, content_type):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.status_ln = "HTTP/1.1 " + status + "\r\n"
        if isinstance(body, (bytes, bytearray)):
            self.body = body
        else:
            self.body = str.encode(body)
        body_len = str(len(self.body))
        self.headers = {
            "X-Content-Type-Options": "nosniff",
            "Content-Type": content_type,
            "Content-Length": body_len,
        }
        self.cookies = {}

    def setHeaders(self, key, value):
        self.headers[key] = value

    def setCookie(self, key, value):
        self.cookies[key] = value

    def replaceInBody(self, replace, set):
        self.body = self.body.replace(replace, set)
        self.setHeaders("Content-Length", str(len(self.body)))

    def makeResponse(self):
        hrds = ""
        for key in self.headers:
            hrds += key + ": " + self.headers[key] + "\r\n"
        for key in self.cookies:
            hrds = hrds + "Set-Cookie: " + key + "=" + self.cookies[key] + "; "
        hrds = hrds[:-2] + "\r\n\r\n"

        return str.encode(self.status_ln + hrds) + self.body


def test1():
    res = Response("200 OK", b"hello", "plain/text")
    res.setCookie("test", "1")
    res.setCookie("test2", "1")
    res.makeResponse()


if __name__ == "__main__":
    test1()
