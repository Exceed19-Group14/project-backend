from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

load_dotenv()

MONGO_HOST = getenv('MONGO_HOST')
MONGO_DB = getenv('MONGO_DB')

client = MongoClient(MONGO_HOST)

try:
    conn = client.server_info()
    print("Connected to MongoDB")
except:
    print("Unable to connect MongoDB")

db = client.get_database(MONGO_DB)
