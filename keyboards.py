from aiogram import types


def main_menu_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Погода сегодня"),
                 types.KeyboardButton("Прогноз погоды"))
    keyboard.add(types.KeyboardButton("Аналитика погоды"))

    return keyboard
