from pymongo import MongoClient

mongo_client = MongoClient("database")
db = mongo_client["cse312"]
