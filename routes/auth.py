import os
from database.session import delete_session
from database.user import *
from util.auth import *
from util.response import Response
from util.router import Router


def add_auth_routes(router: Router):
    router.add_route("POST", "/register", register_new_account)
    router.add_route("POST", "/login", login_account)
    router.add_route("POST", "/logout", logout_account)
    pass


def register_new_account(request):
    creds = extract_credentials(request)
    password = creds.pop()
    username = creds.pop()
    if validate_password(password):
        user = new_user(username, password)
    r = Response("302 Found", "", "text/plain")
    r.setHeaders("Location", "/")
    return r.makeResponse()


def login_account(request):
    creds = extract_credentials(request)
    password = creds.pop()
    username = creds.pop()
    auth_token = auth_user(username, password)
    r = Response("302 Found", "", "text/plain")
    r.setHeaders("Location", "/")
    if auth_token != None:
        r.setCookie("AUTH_TOKEN", auth_token)
    return r.makeResponse()


def logout_account(request):
    if "AUTH_TOKEN" in request.cookies:
        delete_session(request.cookies["AUTH_TOKEN"])
    r = Response("302 Found", "", "text/plain")
    r.setHeaders("Location", "/")
    r.setCookie("AUTH_TOKEN", "HttpOnly; max-age=0")
    return r.makeResponse()
