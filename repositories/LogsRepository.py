from repositories.MongoConnection import MongoConnection

class LogsRepository:
    def __init__(self):
        mongo = MongoConnection()
        self.collection = mongo.db["logs"]

    def save(self, log_entry):
        """Save log into MongoDB"""
        self.collection.insert_one(log_entry)
