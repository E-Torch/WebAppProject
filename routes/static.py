import os
from database.session import get_xsrf_token, validate_session
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
    router.add_route("GET", "/public/functions.js", get_function_js)
    router.add_route("GET", "/public/.", get_static_files)


def get_index(request):
    body = getFile("/public/index.html")
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        xsrf_token = get_xsrf_token(request.cookies["AUTH_TOKEN"])
        body = _change_to_logout_button(body, xsrf_token)
    response = Response("200 OK", body, mimeTypes["html"])
    check_visits_cookie(request, response)
    return response.makeResponse()


def get_static_files(request):
    ext = request.path.split(".").pop()
    mime = mimeTypes[ext]

    body = getFile(request.path)
    if body == None:
        return Response("404 Not Found", "", "text/plain").makeResponse()
    return Response("200 OK", body, mime).makeResponse()


def get_function_js(request):
    ext = request.path.split(".").pop()
    mime = mimeTypes[ext]

    body = getFile(request.path)
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        body = body.replace(
            b'const chatTextBox = document.getElementById("chat-text-box");\n',
            b'const chatTextBox = document.getElementById("chat-text-box");\nconst xsrf_token = document.getElementById("xsfr_token");\n',
        )
        body = body.replace(
            b'const messageJSON = {"message": message};',
            b'const messageJSON = {"message": message, "xsrf-token": xsrf_token.value };',
        )
    if body == None:
        return Response("404 Not Found", "", "text/plain").makeResponse()
    return Response("200 OK", body, mime).makeResponse()


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


def getFile(path):
    path = os.path.join(os.path.dirname(__file__), "../", path[1:])
    if os.path.isfile(path):
        f = open(
            path,
            "rb",
        )
        body = f.read()

        f.close()
        return body
    return None


def _change_to_logout_button(body, xsrf_token):
    start = body.find(b"Register:")
    end = body.find(b"</form>\n\n\n", start) + len(b"</form>")
    logout_button = b"""
    <form action="/logout" method="post">
            <input type="submit" value="Logout">
    </form>
        """
    body = body.replace(body[start:end], logout_button)
    body = body.replace(b"Register:", b"")
    body = body.replace(
        b"Chat:\n",
        b'Chat:\n<input id="xsfr_token" value="' + xsrf_token + b'" hidden>\n',
    )
    return body
