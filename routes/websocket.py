import json
import os
from database.chat import add_new_chat
from database.session import get_decode, validate_session
from util.request import Request
from util.response import Response
from util.router import Router
from util.websockets import *

socket_users = {}


def add_websocket_routes(router: Router):
    router.add_route("GET", "/websocket", create_handshake, True)
    pass


def create_handshake(request: Request, tcp):
    user = "Guest"
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        user = get_decode(request.cookies["AUTH_TOKEN"])
    accept_sec = compute_accept(request.headers["Sec-WebSocket-Key"])
    res = Response("101 Switching Protocols", "", "text/plain")
    res.setHeaders("Connection", "Upgrade")
    res.setHeaders("Upgrade", "websocket")
    res.setHeaders("Sec-WebSocket-Accept", accept_sec)
    tcp.request.sendall(res.makeResponse())
    socket_users[accept_sec] = [user, tcp]
    buffer_socket_response(request, tcp, user, accept_sec)


def buffer_socket_response(request: Request, tcp, user, accept_sec):
    extra_bytes = b""
    payload = b""
    frame = None
    if user != "Guest":
        handleMessage(request, {"messageType": "updateList"})
    while True:
        if len(extra_bytes) == 0:
            received_data = tcp.request.recv(2048)
        else:
            received_data = extra_bytes
            extra_bytes = b""
        if len(received_data) == 0:
            socket_users.pop(accept_sec)
            handleMessage(request, {"messageType": "updateList"})
            break
        frame = parse_ws_frame(received_data)
        while frame.payload_length > len(frame.payload):
            print(frame.payload_length, len(frame.payload))
            received_data += tcp.request.recv(2048)
            frame = parse_ws_frame(received_data)
        if frame.opcode == 8:
            handleMessage(request, {"messageType": "updateList"})
            socket_users.pop(accept_sec)
            break
        extra_bytes = frame.extra
        payload += frame.payload

        if frame.fin_bit == 0:
            print("still grabbing")
        else:
            data = json.loads(payload)
            handleMessage(request, data)
            payload = b""

    print("exit")
    tcp.request.close()


def html_escape(body):
    body = body.replace("&", "&amp")
    body = body.replace("<", "&lt")
    body = body.replace(">", "&gt")
    return body


def handleMessage(request, data):
    user = "Guest"
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        user = get_decode(request.cookies["AUTH_TOKEN"])
    if data["messageType"] == "chatMessage":
        handleChat(data, user)
    if data["messageType"] == "updateList":
        userList = []
        for i in socket_users:
            user = socket_users[i][0]
            if user != "Guest":
                userList.append(user)
        list_to_send = {"messageType": "updateList", "list": userList}
        msg = json.dumps(list_to_send).encode()
        for i in socket_users:
            socket_users[i][1].request.sendall(generate_ws_frame(msg))


def handleChat(data, user):
    msg = html_escape(data["message"])
    res = json.loads(add_new_chat(msg, user))
    chat_to_send = {
        "messageType": "chatMessage",
        "username": user,
        "message": msg,
        "id": res["id"],
    }
    for i in socket_users:
        socket_users[i][1].request.sendall(
            generate_ws_frame(json.dumps(chat_to_send).encode())
        )
