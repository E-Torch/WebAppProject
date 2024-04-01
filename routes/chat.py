from database.chat import *
from database.session import get_decode, get_xsrf_token, validate_session
from util.request import Request
from util.response import Response


def add_chat_routes(router):
    router.add_route("GET", "/chat-messages$", get_chat_log)
    router.add_route("POST", "/chat-messages$", post_chat_message)
    router.add_route("GET", "/chat-messages/.", get_single_chat_message)
    router.add_route("PUT", "/chat-messages/.", put_chat_message)
    router.add_route("DELETE", "/chat-messages/.", delete_chat_message)


def get_chat_log(request):
    return Response("200 OK", get_all_chat_messages(), "text/plain").makeResponse()


def get_single_chat_message(request):
    path_id = request.path.split("/").pop()
    message = get_chat_message(path_id)
    if "id" in message:
        return Response("200 OK", message, "application/json").makeResponse()

    else:
        return Response("404 Not Found", "No chat found", "text/plain").makeResponse()


def delete_chat_message(request):
    path_id = request.path.split("/").pop()
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        user = get_decode(request.cookies["AUTH_TOKEN"])
        if has_remove_chat_message(path_id, user):
            return Response("204 No Content", "", "text/plain").makeResponse()

    return Response("403 Forbidden", "user not logged in", "text/plain").makeResponse()


def post_chat_message(request: Request):
    request.html_escape_body()
    json_req = json.loads(request.body)
    message = json_req["message"]
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        user = get_decode(request.cookies["AUTH_TOKEN"])
        xsrf_token = get_xsrf_token(request.cookies["AUTH_TOKEN"])
        if json_req["xsrf-token"] == xsrf_token.decode("utf-8"):
            return Response(
                "201 Created", add_new_chat(message, user), "application/json"
            ).makeResponse()
        else:
            return Response("403 Forbidden", "auth error", "text/plain").makeResponse()

    return Response(
        "201 Created", add_new_chat(message, "Guest"), "application/json"
    ).makeResponse()


def put_chat_message(request):
    path_id = request.path.split("/").pop()
    request.html_escape_body()
    if has_update_chat(path_id, json.loads(request.body)):
        return Response(
            "200 okay", get_chat_message(path_id), "application/json"
        ).makeResponse()
    else:
        return Response(
            "404 Not Found", "no record exist to modify", "text/plain"
        ).makeResponse()
