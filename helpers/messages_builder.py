from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from helpers.bot_helpers import normalize_text, create_google_maps_link

FUEL_ICONS = ["🏆", "🥈", "🥉"]

def build_keyboard(open_only=False):
    keyboard = [[InlineKeyboardButton("Buscar otra vez", callback_data='restart')]]
    if not open_only:
        keyboard.append([InlineKeyboardButton("Buscar solo abiertas", callback_data='open_only')])
    return InlineKeyboardMarkup(keyboard)


def build_station_message(stations, fuel_type_key, radius_km, open_only=False, fuel_labels=None):
    fuel_labels = fuel_labels or {}
    message = f'<b>⛽ GASOLINERAS MÁS BARATAS CERCA DE TI ⛽</b>\n\n'
    message += f'<b>🔍 Búsqueda realizada</b>\n'
    message += f'<b>Combustible</b>: <i>{fuel_labels.get(fuel_type_key, "NA")}</i>\n'
    message += f'<b>Distancia</b>: <i>{radius_km} km</i>\n\n'

    if not stations:
        message += "No se han encontrado gasolineras en la distancia indicada"
        if open_only:
            message += " que estén abiertas ahora"
        message += "\n\n"
    else:
        for i, station in enumerate(stations):
            message += f"<b>{FUEL_ICONS[i]} {i+1}. {station.get('brand', 'Desconocido')}</b>\n"
            message += f"💶 <b>Precio</b>: <i>{station.get(fuel_type_key, 'N/A')} €/L</i>\n"
            message += f"📍 <b>Dirección</b>: <i>{normalize_text(station.get('address'))}</i>\n"
            if station.get('is_open') is False:
                message += f"❌ <b>Actualmente cerrada</b>\n"
            coords = station.get('location', {}).get('coordinates', [None, None])
            if coords[1] and coords[0]:
                message += f"🗺️ <a href='{create_google_maps_link(coords[1], coords[0])}'> Ver en Google Maps </a>\n\n"

    message += "☕ <b>¿Te ayudo a ahorrar dinero? <a href='https://paypal.me/dcastrocelard'>¡Invítame a un café! ☕</a></b>\n"
    return message
