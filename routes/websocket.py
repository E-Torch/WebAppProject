from util.request import Request
from util.response import Response
from util.router import Router
from util.websockets import *


def add_websocket_routes(router: Router):
    router.add_route("GET", "/websocket", create_handshake, True)
    pass


def create_handshake(request: Request, tcp):

    accept_sec = compute_accept(request.headers["Sec-WebSocket-Key"])
    res = Response("101 Switching Protocols", "", "text/plain")
    res.setHeaders("Connection", "Upgrade")
    res.setHeaders("Upgrade", "websocket")
    res.setHeaders("Sec-WebSocket-Accept", accept_sec)
    tcp.request.sendall(res.makeResponse())
    buffer_socket_response(request, tcp)


def buffer_socket_response(request: Request, tcp):
    extra_bytes = b""
    while True:
        if len(extra_bytes) == 0:
            received_data = tcp.request.recv(2048)
        else:
            received_data = extra_bytes
            extra_bytes = b""
        if len(received_data) == 0:
            break
        # print(tcp.client_address)
        # print("--- received data ---")
        # print(received_data)
        # print("--- end of data ---\n\n")
        payload, extra_bytes = get_payload_from_frames(received_data, tcp)
        print(payload)
    tcp.request.close()


def get_payload_from_frames(received_data, tcp):
    payload = b""
    extra_bytes = b""
    frame_info = parse_ws_frame(received_data)
    if frame_info.fin_bit == 1:
        payload, extra_bytes = _get_rest_bytes(tcp, frame_info)
    else:
        payload, extra_bytes = get_other_frames(tcp, frame_info)
    return [payload, extra_bytes]


def get_other_frames(tcp, frame_info):
    payload = b""
    extra_bytes = b""
    while frame_info.fin_bit != 0:
        p, extra_bytes = _get_rest_bytes(tcp, frame_info)
        payload += p
        if len(extra_bytes) == 0:
            received_data = tcp.request.recv(2048)
            frame_info = parse_ws_frame(received_data)
        else:
            frame_info = parse_ws_frame(extra_bytes)
            extra_bytes = b""

    p, extra_bytes = _get_rest_bytes(tcp, frame_info)
    payload += p

    return payload, extra_bytes


def _get_rest_bytes(tcp, frame_info):
    extra_bytes = b""
    
    while frame_info.payload_length != len(frame_info.payload):
        if frame_info.payload_length < len(frame_info.payload):
            received_data = tcp.request.recv(2048)
            frame_info.payload += received_data
        else:
            extra_bytes = frame_info.payload[frame_info.payload_length :]
            frame_info.payload = frame_info.payload[: frame_info.payload_length]
    return [frame_info.payload, extra_bytes]
