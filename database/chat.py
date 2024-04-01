import json
from . import db

chat_collection = db["chat"]


def get_all_chat_messages():
    array = []
    result = chat_collection.find({})
    for collection in result:
        message = {}
        message["message"] = collection["message"]
        message["username"] = collection["username"]
        message["id"] = collection["id"]
        array.append(message)
    array = json.dumps(array)
    return array


def get_chat_message(id):
    message = {}
    result = chat_collection.find({"id": id})
    for collection in result:
        message["message"] = collection["message"]
        message["username"] = collection["username"]
        message["id"] = collection["id"]
    return json.dumps(message)


def has_remove_chat_message(id, user):
    result = chat_collection.delete_one({"id": id, "username": user})
    return result.deleted_count != 0


def add_new_chat(message, user):
    result = chat_collection.insert_one(
        {
            "username": user,
            "message": message,
            "id": str(get_count(chat_collection) + 1),
        }
    )

    result = chat_collection.find({"_id": result.inserted_id})
    message = {}
    for collection in result:
        message["message"] = collection["message"]
        message["username"] = collection["username"]
        message["id"] = collection["id"]
    return json.dumps(message)


def has_update_chat(id, message, user):
    query = {"id": id}
    update = {
        "message": message,
        "username": user,
    }
    result = chat_collection.update_one(query, update)
    return result.modified_count != 0


def get_count(chat_collection):
    chat_count = 0
    for l in chat_collection.find({}):
        chat_count += 1
    return chat_count
