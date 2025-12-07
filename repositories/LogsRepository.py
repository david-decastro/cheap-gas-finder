import configparser
import hashlib
from pymongo import MongoClient
from datetime import datetime

class LogsRepository:
    def __init__(self, config_file="_config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.uri = config.get("MongoDB", "uri", fallback="mongodb://localhost:27017")
        self.db_name = config.get("MongoDB", "db_name", fallback="cheap-gas-finder")

        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db["logs"]

    @staticmethod
    def anonymize_user(user_id: int) -> str:
        """Return a SHA256 hash of the user_id as an anonymous identifier"""
        return hashlib.sha256(str(user_id).encode()).hexdigest()

    def build_log(self, update):
        """Convert a Telegram Update into a privacy-friendly log dict"""
        data = update.to_dict()
        user_id = (
            data.get("message", {}).get("from", {}).get("id")
            or data.get("callback_query", {}).get("from", {}).get("id")
        )

        log_entry = {
            "user_hash": self.anonymize_user(user_id) if user_id else None,
            "message_type": None,
            "text_category": None,
            "location": None,
            "timestamp": datetime.utcnow()
        }

        if "message" in data:
            msg = data["message"]
            if "text" in msg:
                log_entry["message_type"] = "text"
                log_entry["text_category"] = (
                    "command" if msg["text"].startswith("/") else "free_text"
                )
            elif "location" in msg:
                log_entry["message_type"] = "location"
                loc = msg["location"]
                log_entry["location"] = {
                    "latitude": round(loc["latitude"], 2),   # 2 decimals ≈ 1km precision
                    "longitude": round(loc["longitude"], 2)
                }
        elif "callback_query" in data:
            log_entry["message_type"] = "callback_query"
            log_entry["text_category"] = "button_click"

        return log_entry

    def save(self, update):
        """Save anonymized update log into MongoDB"""
        log_entry = self.build_log(update)
        self.collection.insert_one(log_entry)
