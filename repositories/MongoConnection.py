import configparser
from pymongo import MongoClient

class MongoConnection:
    _instance = None

    def __new__(cls, config_file="_config.ini"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            config = configparser.ConfigParser()
            config.read(config_file)

            uri = config.get("MongoDB", "uri", fallback="mongodb://localhost:27017")
            db_name = config.get("MongoDB", "db_name", fallback="cheap-gas-finder")

            cls._instance.client = MongoClient(uri)
            cls._instance.db = cls._instance.client[db_name]

        return cls._instance
