import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN
from states import WeatherStates
from keyboards import main_menu_keyboard
from weather_handler import analyze_weather, process_city, process_analysis_year, process_month

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация обработчиков
dp.register_message_handler(analyze_weather, commands=['m_menu'])
dp.register_message_handler(process_city, state=WeatherStates.waiting_for_city)
dp.register_message_handler(process_analysis_year, state=WeatherStates.waiting_for_year)
dp.register_message_handler(process_month, state=WeatherStates.waiting_for_month)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
