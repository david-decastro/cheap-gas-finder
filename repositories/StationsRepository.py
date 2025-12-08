from pymongo import GEOSPHERE
from datetime import datetime
from repositories.MongoConnection import MongoConnection

class StationsRepository:
    def __init__(self):
        mongo = MongoConnection()
        self.collection = mongo.db["stations"]

        # Ensure geospatial index exists to improve performance
        self.collection.create_index([("location", GEOSPHERE)])

    def find_nearest_stations(self, fuel_type, latitude, longitude, radius_km=5, limit=3, open_now=False):
        """
        Find the nearest gas stations for a given fuel type and location.
        Optionally filters only stations that are currently open.
        Adds an 'is_open' field to each station regardless of filtering
        """

        # Geo query pipeline
        pipeline = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [longitude, latitude]},
                    "distanceField": "distance",
                    "maxDistance": radius_km * 1000,
                    "spherical": True,
                    "query": {fuel_type: {"$ne": None}}  # only stations with price
                }
            },
            {"$sort": {fuel_type: 1}}
        ]

        stations = list(self.collection.aggregate(pipeline))
        now = datetime.now()

        # Add 'is_open' field to every station
        for s in stations:
            s['is_open'] = self.is_open(s.get("schedule"), now)

        # Filter by open_now if requested
        if open_now:
            stations = [s for s in stations if s['is_open']]

        return stations[:limit]

    @staticmethod
    def is_open(schedule_dict, when):
        """
        Check if a station is open at the given datetime.
        schedule_dict: output of parse_schedule
        """

        if not schedule_dict:
            return False

        weekday = when.strftime("%A").lower()
        ranges = schedule_dict.get(weekday, [])
        current_time = when.time()

        for r in ranges:
            if "open" in r and "close" in r:
                open_time = datetime.strptime(r["open"], "%H:%M").time()
                close_time = datetime.strptime(r["close"], "%H:%M").time()
                if open_time <= current_time <= close_time:
                    return True
        return False
