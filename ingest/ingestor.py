from pymongo import MongoClient
from ingestor_helpers import transform
import httpx
import configparser

URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"

# CONFIGURATION
config = configparser.ConfigParser()
config.read("_config.ini")

mongo_uri = config.get("MongoDB", "uri", fallback="mongodb://localhost:27017")
mongo_db_name = config.get("MongoDB", "db_name", fallback="cheap-gas-finder")

# MongoDB connection
client = MongoClient(mongo_uri)
db = client[mongo_db_name]
collection = db["stations"]

def fetch_data():
    """ Download data from the API endpoint """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            response = client.get(URL)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    data = fetch_data()
    records = data.get("ListaEESSPrecio", [])

    # Transform all records using helper
    docs = [transform(r) for r in records]

    # Insert into MongoDB
    collection.delete_many({})  # remove previous records
    collection.insert_many(docs)

    print(f"Inserted {len(docs)} gas stations into MongoDB")

if __name__ == "__main__":
    main()
