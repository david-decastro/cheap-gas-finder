def normalize_text(text: str) -> str:
    """
    Capitalize the first letter of each word in the text.
    Returns 'Desconocido' if text is None or empty.
    """
    return text.lower().title() if text else "Desconocido"


def create_google_maps_link(lat: float, lon: float) -> str:
    """
    Returns a Google Maps URL pointing to the given latitude and longitude.
    """
    return f"https://www.google.com/maps?q={lat},{lon}"
