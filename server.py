import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import configparser

from helpers.log_helper import build_log, build_error_log
from repositories.LogsRepository import LogsRepository
from repositories.StationsRepository import StationsRepository
from helpers.messages_builder import build_station_message
from helpers.keyboard_builder import build_keyboard

# Fuel type mapping
FUEL_TYPE = {
    'gasoline_95': 'Gasolina 95',
    'gasoline_98': 'Gasolina 98',
    'diesel': 'Gasoleo A'
}

# CONFIGURATION FILE
config = configparser.ConfigParser()
config.read('_config.ini')

# LOGGER
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize repositories
stations_repo = StationsRepository()
logs_repo = LogsRepository()

# HANDLERS
async def start(update: Update, context) -> None:
    reply_markup = build_keyboard("select_fuel")
    if update.message:
        await update.message.reply_text("⛽ Selecciona el tipo de combustible", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("⛽ Selecciona el tipo de combustible", reply_markup=reply_markup)

    logs_repo.save(build_log("START", update))  # Log


async def select_fuel(update: Update, context) -> None:
    query = update.callback_query
    context.user_data['fuel_type'] = query.data

    reply_markup = build_keyboard("request_location")
    await query.message.reply_text(
        "Por favor, envía tu ubicación usando el botón de abajo",
        reply_markup=reply_markup
    )


async def location_handler(update: Update, context) -> None:
    user_location = update.message.location
    context.user_data['latitude'] = user_location.latitude
    context.user_data['longitude'] = user_location.longitude

    reply_markup = build_keyboard("select_radius")
    await update.message.reply_text("¡Ubicación recibida!", reply_markup=build_keyboard("remove"))
    await update.message.reply_text("Selecciona un radio de búsqueda", reply_markup=reply_markup)


async def perform_search(update: Update, context) -> None:
    query = update.callback_query

    # Initializing variables to perform the search
    open_only = False
    radius_km = context.user_data.get('radius', None)

    if query.data == 'open_only':
        open_only = True
    elif query.data != 'repeat_search':
        radius_km = float(query.data.replace("km", "").strip())
        context.user_data['radius'] = radius_km

    if context.user_data.get('fuel_type') is None:
        await query.message.reply_text("Ups! 🙈 Faltan datos, vamos a empezar de nuevo")
        await start(update, context)
        return
    if context.user_data.get('latitude') is None or context.user_data.get('longitude') is None:
        await query.message.reply_text("⛽ ¿Qué tipo de combustible quieres buscar?")
        await select_fuel(update, context)
        return

    await query.message.reply_text("Buscando...... 🤔")

    lat = context.user_data['latitude']
    lon = context.user_data['longitude']
    fuel_type_repo = context.user_data['fuel_type']

    nearest_stations = stations_repo.find_nearest_stations(
        fuel_type=fuel_type_repo,
        latitude=lat,
        longitude=lon,
        radius_km=radius_km,
        limit=3,
        open_now=open_only
    )

    message = build_station_message(
        nearest_stations,
        fuel_type_repo,
        radius_km,
        open_only=open_only,
        fuel_labels=FUEL_TYPE
    )

    if open_only:
        reply_markup = build_keyboard("restart_options_without_open")
    else:
        # Shows the "Buscar solo abiertas" button if at least one of the three gas stations is closed
        open_gas_stations_count = sum(1 for station in nearest_stations if station.get("is_open", True))
        reply_markup = build_keyboard("restart_options", open_gas_stations_count < 3)

    await query.message.reply_text(
        message, parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup
    )

    logs_repo.save(build_log("SEARCH", update, context)) # Log


async def restart_handler(update: Update, context) -> None:
    context.user_data.clear()
    await start(update, context)


async def generic_response(update: Update, context) -> None:
    logs_repo.save(build_log("GENERIC", update)) # Log

    reply_markup = build_keyboard("remove")
    await update.message.reply_text("Lo siento, no entiendo ese comando", reply_markup=reply_markup)


async def error_handler(update: object, context) -> None:
    """Log any errors caused by updates"""
    logger.error("Exception while handling update:", exc_info=context.error)

    reply_markup = build_keyboard("remove")
    await update.message.reply_text(
        "😢 Lo siento mucho!\n\n"
        "El bot ha encontrado un error y algo ha fallado.\n"
        "Por favor, inténtalo de nuevo.",
        reply_markup=reply_markup
    )

    if isinstance(update, Update):
        logger.info("Update that failed: %s", update.to_dict())
        logs_repo.save(build_error_log(update))

# MAIN
def main() -> None:
    application = Application.builder().token(config['TELEGRAM']['bot_token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(select_fuel, pattern='^(diesel|gasoline_95|gasoline_98)$'))
    application.add_handler(MessageHandler(filters.LOCATION, location_handler))
    application.add_handler(CallbackQueryHandler(perform_search, pattern='^.*km$'))
    application.add_handler(CallbackQueryHandler(perform_search, pattern='^open_only$'))
    application.add_handler(CallbackQueryHandler(perform_search, pattern='^repeat_search$'))
    application.add_handler(CallbackQueryHandler(restart_handler, pattern='^restart$'))
    application.add_handler(MessageHandler(filters.ALL, generic_response))
    application.add_error_handler(error_handler)

    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=config['TELEGRAM']['bot_token'],
        webhook_url=f"{config['TELEGRAM']['webhook_url']}/{config['TELEGRAM']['bot_token']}"
    )

if __name__ == '__main__':
    main()
