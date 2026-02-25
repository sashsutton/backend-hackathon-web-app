
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

import os
from dotenv import load_dotenv

load_dotenv("key.env")


uri = os.getenv("MONGODB_URI")

def mongodb_connection():

    client = MongoClient(uri, tlsAllowInvalidCertificates=True)
    return client

def check_mongodb_connection():

    try:
        client = mongodb_connection()
        client.admin.command('ismaster')
        return True, "Successfully connected to MongoDB"
    except ConnectionFailure as e:
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

