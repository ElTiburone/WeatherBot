from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import State

class WeatherStates:
    waiting_for_city = State()
    waiting_for_year = State()
    waiting_for_month = State()
