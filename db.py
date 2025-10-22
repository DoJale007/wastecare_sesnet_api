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
enterprises_collection = sesnet_db["enterprises"]
products_collection = sesnet_db["products"]
applications_collection = sesnet_db["applications"]
contacts_collection = sesnet_db["contacts"]
