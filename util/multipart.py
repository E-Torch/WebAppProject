class Multipart:
    def __init__(self, boundary, parts):
        self.boundary = boundary
        self.parts = parts


class Part:
    def __init__(self, h, n, c):
        self.headers = h
        self.name = n
        self.content = c

    def get_file_ext(self):
        return (
            self.headers["Content-Disposition"]
            .split(" filename=")
            .pop(1)
            .split(".")
            .pop()
            .strip('"')
        )


def parse_multipart(request):
    boundary = request.headers["Content-Type"].split("boundary=").pop()
    delimeter = b"--" + str.encode(boundary)

    parts = []
    multi = request.body.lstrip(delimeter).split(b"\r\n" + delimeter)
    multi.pop()
    for item in multi:
        parts.append(create_part(item))

    return Multipart(boundary, parts)


def create_part(item: bytes):
    item = item.lstrip(b"\r\n")
    item = item.split(b"\r\n\r\n", 1)
    content = item.pop()
    headers = {}
    item = item.pop().decode("utf-8")
    for line in item.split("\r\n"):
        key, value = line.split(":")
        headers[key] = value.strip(" ")

    name = headers["Content-Disposition"].split(" name=").pop(1)
    if name.find(";") != -1:
        name = name.split(";").pop(0)
    name = name.strip('"')
    return Part(headers, name, content)
