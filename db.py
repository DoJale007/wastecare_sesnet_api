from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

# Connect to Mongo Atlas Cluster
mongo_client = MongoClient(os.getenv("MONGO_URI"))


# Access database
sesnet_db = mongo_client["wastecare_sesnet_db"]


# Access a collection to operate on
users_collection = sesnet_db["users"]
builders_collection = sesnet_db["builders"]
suppliers_collection = sesnet_db["suppliers"]
