import hashlib
import random
from datetime import datetime, timezone
from telegram import Update
from typing import Optional

def anonymize_user(user_id: int) -> str:
    """Return a SHA256 hash of the user_id as an anonymous identifier"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()

def anonymize_coord(lat, lon, precision=2, max_noise=0.01):
    """Adds noise to the position to prevent geolocation tracking"""
    lat = round(lat, precision) + random.uniform(-max_noise, max_noise)
    lon = round(lon, precision) + random.uniform(-max_noise, max_noise)
    return lat, lon


def _build_log(operation: str, update: Update):
    data = update.to_dict()
    user_id = (
            data.get("message", {}).get("from", {}).get("id")
            or data.get("callback_query", {}).get("from", {}).get("id")
    )

    log_entry = {
        "user_id": anonymize_user(user_id),
        "timestamp": datetime.now(timezone.utc),
        "operation": operation
    }

    return log_entry

def build_error_log(update: Update):
    """
    Builds a log entry for update response errors

    Params:
        update: telegram.Update
    """
    log_entry = _build_log("ERROR", update)

    log_entry["data"] = update.to_dict()

def build_log(operation: str, update: Update, context: Optional[any] = None):
    """
    Builds a log entry for the perform_search request

    Params:
        operation: str
        update: telegram.Update
        context: telegram.ext.CallbackContext
    """
    log_entry = _build_log(operation, update)

    if context is not None:
        lat, lon = anonymize_coord(context.user_data.get("latitude"), context.user_data.get("longitude"))
        log_entry["data"] = {
            "fuel_type": context.user_data.get("fuel_type"),
            "radius_km": context.user_data.get("radius"),
            "open_only": context.user_data.get("open_only", False),
            "location": {
                "latitude": lat,
                "longitude": lon
            }
        }

    return log_entry
