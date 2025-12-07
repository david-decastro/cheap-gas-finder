import re
from datetime import datetime

DAY_MAP = {
    "L": "monday",
    "M": "tuesday",
    "X": "wednesday",
    "J": "thursday",
    "V": "friday",
    "S": "saturday",
    "D": "sunday",
}

def parse_schedule(schedule_str):
    """
    Convert a schedule string like:
      - "L-D: 07:00-23:00"
      - "L-D: 24H"
      - "L-S: 07:00-22:00; D: 08:00-22:00"
    into a structured dict with lists of opening ranges per day
    """
    schedule_str = schedule_str.strip()
    schedule_dict = {day: [] for day in DAY_MAP.values()}

    # Split by ';' in case of multiple ranges
    parts = [p.strip() for p in schedule_str.split(";")]

    for part in parts:
        # 24H case
        if "24H" in part.upper():
            # Determine days
            day_range_match = re.match(r"([LMXJVSD])\-?([LMXJVSD])?", part)
            if day_range_match:
                start_day, end_day = day_range_match.groups()
                days = get_day_range(start_day, end_day)
                for d in days:
                    schedule_dict[DAY_MAP[d]].append({"open": "00:00", "close": "23:59"})
            continue

        # Normal range: "L-D: 07:00-23:00" or "D: 08:00-22:00"
        match = re.match(r"([LMXJVSD])\-?([LMXJVSD])?:\s*(\d{2}:\d{2})-(\d{2}:\d{2})", part)
        if match:
            start_day, end_day, open_time, close_time = match.groups()
            days = get_day_range(start_day, end_day)
            for d in days:
                schedule_dict[DAY_MAP[d]].append({"open": open_time, "close": close_time})
            continue

        # If not matched, store raw string
        for day in schedule_dict:
            schedule_dict[day].append({"raw": part})

    return schedule_dict

def get_day_range(start_day, end_day):
    """
    Returns a list of day letters from start_day to end_day.
    If end_day is None, returns just start_day.
    Handles wrap-around (e.g., D-L)
    """
    day_keys = list(DAY_MAP.keys())
    if end_day is None:
        return [start_day]
    start_idx = day_keys.index(start_day)
    end_idx = day_keys.index(end_day)
    if start_idx <= end_idx:
        return day_keys[start_idx:end_idx+1]
    else:
        return day_keys[start_idx:] + day_keys[:end_idx+1]


def transform(record):
    """
    Clean and transform a single gas station record for MongoDB insertion.
    Includes parsing prices, creating GeoJSON location, and structured schedule
    """
    # Helper to convert price strings like "1,439" into float
    def parse_price(value):
        try:
            return float(value.replace(",", "."))
        except:
            return None

    transformed = {
        "id": record.get("IDEESS"),
        "brand": record.get("Rótulo", "").title().strip(),
        "municipality": record.get("Municipio", "").title().strip(),
        "province": record.get("Provincia", "").title().strip(),
        "address": record.get("Dirección", "").strip(),
        "gasoline_95": parse_price(record.get("Precio Gasolina 95 E5", "")),
        "gasoline_98": parse_price(record.get("Precio Gasolina 98 E5", "")),
        "diesel": parse_price(record.get("Precio Gasoleo A", "")),
        "schedule": parse_schedule(record.get("Horario", "")),
        "location": {
            "type": "Point",
            "coordinates": [
                float(record["Longitud (WGS84)"].replace(",", ".")),
                float(record["Latitud"].replace(",", "."))
            ]
        },
        "ingestion_date": datetime.utcnow()
    }
    return transformed
