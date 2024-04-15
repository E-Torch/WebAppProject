import os
from database.chat import add_new_chat
from database.session import get_decode, validate_session
from util.response import Response
from util.router import Router
from util.multipart import *

import uuid


def add_upload_routes(router: Router):
    router.add_route("POST", "/upload", save_file_to_disk)


def save_file_to_disk(request):
    mp = parse_multipart(request)
    for part in mp.parts:
        if part.name == "file_upload":
            create_file_message(request, part)
            r = Response("302 Found", "", "text/plain")
            r.setHeaders("Location", "/")
            return r.makeResponse()
    return Response("404 Not Found", "", "text/plain").makeResponse()


def create_file_message(request, part):
    ext = part.get_file_ext()
    if ext == "jpg":
        _create_file_message(request, part)
    elif ext == "mp4":
        _create_video_message(request, part)


def _create_file_message(request, part):
    user = _get_user_info(request)
    img_html = '<img src="public/image/{}" width="250" height="250"/>'
    file_name = uuid.uuid4().hex + ".jpg"
    save_to_public_disk(part, user, img_html, file_name)


def _create_video_message(request, part):
    user = _get_user_info(request)
    video_html = '<video width="400" controls autoplay muted> <source src="public/image/{}" type="video/mp4"></video>'
    file_name = uuid.uuid4().hex + ".mp4"
    save_to_public_disk(part, user, video_html, file_name)


def _get_user_info(request):
    user = "Guest"
    if "AUTH_TOKEN" in request.cookies and validate_session(
        request.cookies["AUTH_TOKEN"]
    ):
        user = get_decode(request.cookies["AUTH_TOKEN"])
    return user


def save_to_public_disk(part, user, html, file_name):
    file_path = os.path.join(os.path.dirname(__file__), "../public/image/", file_name)
    file_wb = open(file_path, "w+b")
    file_wb.write(part.content)
    file_wb.close()
    html = html.format(file_name)
    add_new_chat(html, user)
