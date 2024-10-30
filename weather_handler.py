import aiohttp
from datetime import datetime, timedelta
from aiogram.dispatcher import FSMContext

from config import API_WEATHER_TOKEN
from states import WeatherStates


async def analyze_weather(message):
    await WeatherStates.waiting_for_city.set()
    await message.answer("Введите название города на кириллице, в котором вы хотите проанализировать погоду:")


async def process_city(message, state: FSMContext):
    city = message.text.strip()
    await state.update_data(city=city)

    if message.text == "Погода сегодня":
        weather_info = await get_current_weather(city)
        await message.answer(weather_info)
        await state.finish()

    elif message.text == "Прогноз погоды":
        weather_forecast = await get_weather_forecast(city)
        await message.answer(weather_forecast)
        await state.finish()

    else:
        await WeatherStates.waiting_for_year.set()
        await message.answer("В каком году вы хотите проанализировать погоду? (не ранее 1980 и не позже 2024)")


async def get_current_weather(city: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_WEATHER_TOKEN}&units=metric"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temp = data['main']['temp']
                weather_desc = data['weather'][0]['description']
                return f"Текущая погода в городе {city}:\nТемпература: {temp}°C\nОписание: {weather_desc}"
            else:
                return "Не удалось получить данные о погоде."


async def get_weather_forecast(city: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_WEATHER_TOKEN}&units=metric"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                forecast = "Прогноз погоды на следующие 3 дня:\n"
                for i in range(0, 24 * 3, 8):  # Каждые 8 часов
                    date = datetime.utcfromtimestamp(data['list'][i]['dt']).strftime('%Y-%m-%d %H:%M')
                    temp = data['list'][i]['main']['temp']
                    weather_desc = data['list'][i]['weather'][0]['description']
                    forecast += f"{date}: Температура: {temp}°C, Описание: {weather_desc}\n"
                return forecast
            else:
                return "Не удалось получить данные о прогнозе погоды."
