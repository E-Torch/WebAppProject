from util.request import Request
from util.router import Router


def add_auth_routes(router: Router):
    router.add_route("POST", "/websocket.", create_handshake)
    pass


def create_handshake(request: Request):
    pass
