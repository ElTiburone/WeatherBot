import aiohttp
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from aiogram import Router, F, html
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from config import API_WEATHER_TOKEN
from states import WeatherStates
from keyboards import main_menu_keyboard


weather_router = Router()


@weather_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(WeatherStates.city)
    await message.answer(
        text=''.join(['Привет, ', message.from_user.first_name,
                      '!\n Я Бот, который поможет тебе узнать погоду в любом городе планеты!',
                      '\n В каком городе ты хочешь узнать погоду?'
                      ]),
        reply_markup=ReplyKeyboardRemove()
    )


@weather_router.message(WeatherStates.city)
async def process_city(message: Message, state: FSMContext) -> None:
    city = message.text.strip()
    await state.update_data(city=city)
    await state.set_state(WeatherStates.days)
    await message.answer(
        text='Отлично! Хочешь узнать прогноз погоды на сегодняшний день или на неделю?',
        reply_markup=main_menu_keyboard()
    )


@weather_router.message(WeatherStates.days, F.text.casefold() == "погода сегодня")
async def get_today_weather(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    city = data.get("city")
    weather_data = await fetch_weather(city)

    if weather_data:
        await message.answer(
            text=f"Погода в городе {html.quote(city)} сегодня:\n"
                 f"Температура: {weather_data['temp']}°C\n"
                 f"Описание: {weather_data['description']}\n"
                 f"Влажность: {weather_data['humidity']}%\n"
                 f"Скорость ветра: {weather_data['wind_speed']} м/с"
        )
    else:
        await message.answer("Не удалось получить данные о погоде.")

    await state.clear()


@weather_router.message(WeatherStates.days, F.text.casefold() == "прогноз погоды")
async def get_forecast_weather(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    city = data.get("city")
    forecast_data = await fetch_forecast(city)

    if forecast_data:
        forecast_message = f"Прогноз погоды в городе {html.quote(city)} на неделю:\n"
        for day in forecast_data:
            forecast_message += (
                f"{day['date']}: Температура: {day['temp']}°C, "
                f"Описание: {day['description']}\n"
            )
        await message.answer(forecast_message)
    else:
        await message.answer("Не удалось получить данные о прогнозе погоды.")

    await state.clear()


async def fetch_weather(city: str) -> Optional[dict[str, Any]]:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={API_WEATHER_TOKEN}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "temp": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"]
                }
            else:
                return None


async def fetch_forecast(city: str) -> Any:
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=ru&appid={API_WEATHER_TOKEN}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                forecast = []
                for item in data['list'][:7]:  # Количество дней
                    forecast.append({
                        "date": item["dt_txt"].split(" ")[0],
                        "temp": item["main"]["temp"],
                        "description": item["weather"][0]["description"],
                    })
                return forecast
            else:
                return None
