from util.request import Request
from util.response import Response
from util.router import Router
from util.websockets import *


def add_auth_routes(router: Router):
    router.add_route("GET", "/websocket", create_handshake, True)
    pass


def create_handshake(request: Request):

    accept_sec = compute_accept(request.headers["Sec-WebSocket-Key"])
    res = Response("101 Switching Protocols", "", "text/plain")
    res.setHeaders("Connection", "Upgrade")
    res.setHeaders("Upgrade", "websocket")
    res.setHeaders("Sec-WebSocket-Accept", accept_sec)
    pass
