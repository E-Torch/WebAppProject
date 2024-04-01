from .session import createSession
from . import db
import bcrypt

user_collection = db["user"]


def new_user(username, password):
    account = user_collection.find_one({"username": username})

    if account != None:
        return None
    hashpw = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
    user_collection.insert_one({"username": username, "password": hashpw})
    return username


def auth_user(username, password):
    account = user_collection.find_one({"username": username})

    if account == None:
        return None
    if bcrypt.checkpw(str.encode(password), account["password"]):
        return createSession(username)
    return None
