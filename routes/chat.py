from database.chat import *
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
    if has_remove_chat_message(path_id):
        return Response("204 No Content", "", "text/plain").makeResponse()

    else:
        return Response(
            "404 Not Found", "no record exist to delete", "text/plain"
        ).makeResponse()


def post_chat_message(request):
    request.html_escape_body()
    message = json.loads(request.body)["message"]

    return Response(
        "201 Created", add_new_chat(message), "application/json"
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
