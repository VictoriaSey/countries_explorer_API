from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# connect to mongo atlas cluster
mongo_client = MongoClient(os.getenv("MONGO_URI"))


# Access database
countries_explorer_api_db = mongo_client["countries_explorer_api_db"]

# The collection is our specific "scrapbook" for saved articles
favourites_collection = countries_explorer_api_db["favourites"]
