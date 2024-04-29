from pymongo import MongoClient

mongo_client = MongoClient(
    "mongodb+srv://eddieturcios112:Balamc12@cluster0.3jelkgt.mongodb.net/"
)
# mongo_client = MongoClient("database")
db = mongo_client["cse312"]
