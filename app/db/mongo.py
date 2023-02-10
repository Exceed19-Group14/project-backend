from pymongo import MongoClient
import pymongo
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

board_collection = db.get_collection('boards')
board_collection.create_index('board_id', unique=True)
plant_collection = db.get_collection('plants')
plant_collection.create_index('plant_id', unique=True)
