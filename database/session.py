from . import db
import jwt
import datetime
import bcrypt
import random

EXPIRES = 3600
session_collection = db["session"]
session_collection.create_index("Expires", expireAfterSeconds=EXPIRES)


def createSession(user):
    try:
        token = jwt.encode({"user": user}, "cse312", algorithm="HS256").encode()
        xsrf_token = jwt.encode(
            {"value": random.randint(0, 100000)}, "cse312", algorithm="HS256"
        ).encode()
        expires = datetime.datetime.utcnow()
        hashToken = bcrypt.hashpw(token, bcrypt.gensalt())
        session_collection.insert_one(
            {
                "token": hashToken,
                "xsrf-token": xsrf_token,
                "Expires": expires + datetime.timedelta(0, EXPIRES),
                "user": user,
            }
        )
        res = session_collection.find_one({"token": hashToken})
        return (
            token.decode("utf-8")
            + "; HttpOnly; Expires="
            + res["Expires"].strftime("%a, %d %b %Y %H:%M:%S GMT")
        )
    except Exception as e:
        return e


def get_sess(token):
    user = get_decode(token)
    if user == None:
        return None
    return session_collection.find({"user": user})


def get_decode(token):
    decoded = None
    try:
        decoded = jwt.decode(token, "cse312", algorithms=["HS256"])
    except:
        return None
    user = decoded.get("user")
    return user


def delete_session(token):
    collection = get_sess(token)
    if collection == None:
        return

    for item in collection:
        if bcrypt.checkpw(token.encode(), item["token"]):
            session_collection.delete_one({"token": item["token"]})
            return


def get_xsrf_token(token):
    collection = get_sess(token)
    if collection == None:
        return False

    for item in collection:
        if bcrypt.checkpw(token.encode(), item["token"]):
            return item["xsrf-token"]


def validate_session(token):
    collection = get_sess(token)
    if collection == None:
        return False

    for item in collection:
        if bcrypt.checkpw(token.encode(), item["token"]):
            return True
    return False
