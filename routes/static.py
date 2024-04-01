import os
from util.response import Response

mimeTypes = {
    "js": "text/javascript",
    "css": "text/css",
    "ico": "image/x-icon",
    "jpg": "image/jpg",
    "html": "text/html; charset=UTF-8",
}


def add_static_routes(router):
    router.add_route("GET", "/$", get_index)
    router.add_route("GET", "/public/.", get_static_files)


def get_index(request):
    response = getFiles("/public/index.html")
    check_visits_cookie(request, response)
    return response.makeResponse()


def get_static_files(request):
    return getFiles(request.path).makeResponse()


def check_visits_cookie(request, response):
    if "visits" in request.cookies:
        response.setCookie("visits", str(int(request.cookies["visits"]) + 1))
        response.setCookie("Max-Age", "3600")
        response.replaceInBody(b"{{visits}}", str.encode(response.cookies["visits"]))
        response.setHeaders("Content-Length", str(len(response.body)))
    else:
        response.setCookie("visits", "1")
        response.setCookie("Max-Age", "3600")
        response.replaceInBody(b"{{visits}}", str.encode(response.cookies["visits"]))
        response.setHeaders("Content-Length", str(len(response.body)))


def setPublicResponse(filepath, mime):
    f = open(
        filepath,
        "rb",
    )
    body = f.read()

    f.close()
    response = Response("200 OK", body, mime)
    return response


def getFiles(path):
    path = os.path.join(os.path.dirname(__file__), "../", path[1:])
    if os.path.isfile(path):
        ext = path.split(".").pop()
        mime = mimeTypes[ext]
        response = setPublicResponse(path, mime)
    return response
