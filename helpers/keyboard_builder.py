from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def build_keyboard(phase: str, show_only_open_btn: bool = False):
    """
    Return the appropriate keyboard for each phase of the bot.
    """
    if phase == "select_fuel":
        # Inline keyboard to select fuel type
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Gasoleo A", callback_data='diesel')],
            [InlineKeyboardButton("Gasolina 95", callback_data='gasoline_95')],
            [InlineKeyboardButton("Gasolina 98", callback_data='gasoline_98')],
        ])
    elif phase == "select_radius":
        # Inline keyboard to select search radius
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("1 km", callback_data='1km')],
            [InlineKeyboardButton("2 km", callback_data='2km')],
            [InlineKeyboardButton("5 km", callback_data='5km')],
            [InlineKeyboardButton("10 km", callback_data='10km')],
            [InlineKeyboardButton("20 km", callback_data='20km')],
            [InlineKeyboardButton("60 km", callback_data='60km')],
        ])
    elif phase == "restart_options":
        # Inline keyboard after search results
        buttons = [
            [InlineKeyboardButton("Nueva búsqueda", callback_data='restart')],
            [InlineKeyboardButton("Repetir búsqueda", callback_data='repeat_search')]
        ]
        if show_only_open_btn:
            buttons.insert(1, [InlineKeyboardButton("Buscar solo abiertas", callback_data='open_only')])
        return InlineKeyboardMarkup(buttons)
    elif phase == "restart_options_without_open":
        # Inline keyboard after search results
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Nueva búsqueda", callback_data='restart')],
            [InlineKeyboardButton("Repetir búsqueda", callback_data='repeat_search')],
        ])
    elif phase == "request_location":
        # Reply keyboard to request user location
        return ReplyKeyboardMarkup(
            [[KeyboardButton("Enviar mi ubicación", request_location=True)]],
            one_time_keyboard=True
        )
    elif phase == "remove":
        # Remove keyboard
        return ReplyKeyboardRemove()
    else:
        # Default: empty keyboard
        return None
