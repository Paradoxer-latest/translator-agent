import os
from dotenv import load_dotenv
from mongoengine import connect

load_dotenv()

url = os.getenv("DB_URL")

# Function to connect to MongoDB using MongoEngine (mapped from Mongoose)
def connectUsingMongoose():
    try:
        if not url:
            raise ValueError("DB_URL is not set in environment variables")
        connect(host=url, alias="default")
        print("Mongodb connected using mongoengine")
    except Exception as err:
        print("Error while connecting to db")
        print(err)
