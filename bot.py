import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from model import predict_next, get_recommendation
from data_fetcher import get_binance_data

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Кнопки для выбора интервала
interval_buttons = [
    "1 мин", "5 мин", "10 мин", "15 мин", "30 мин",
    "1 час", "2 часа", "4 часа", "1 день", "2 дня", "3 дня", "1 неделя"
]
interval_markup = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=btn)] for btn in interval_buttons],
    resize_keyboard=True
)

# Хранение состояния
user_state = {}

@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer("Привет! Отправь мне валютную пару, и я предскажу её цену.", reply_markup=interval_markup)

@dp.message_handler(lambda message: message.text not in interval_buttons)
async def handle_symbol(message: Message):
    symbol = message.text.upper()
    try:
        # Запоминаем валютную пару
        user_state[message.chat.id] = {"symbol": symbol}
        await message.answer(
            f"Ты выбрал валютную пару {symbol}. Теперь выбери временной интервал для прогноза.",
            reply_markup=interval_markup
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@dp.message_handler(lambda message: message.text in interval_buttons)
async def handle_interval(message: Message):
    interval = message.text
    chat_id = message.chat.id

    # Проверяем, была ли выбрана валютная пара
    if chat_id not in user_state or "symbol" not in user_state[chat_id]:
        await message.answer("Пожалуйста, сначала отправь валютную пару.")
        return

    symbol = user_state[chat_id]["symbol"]

    # Преобразуем интервал в формат Binance
    interval_map = {
        "1 мин": "1m", "5 мин": "5m", "10 мин": "10m", "15 мин": "15m", "30 мин": "30m",
        "1 час": "1h", "2 часа": "2h", "4 часа": "4h", "1 день": "1d", "2 дня": "2d", "3 дня": "3d", "1 неделя": "1w"
    }
    binance_interval = interval_map.get(interval)

    if not binance_interval:
        await message.answer("Ошибка интервала. Попробуйте еще раз.")
        return

    # Получаем прогноз и рекомендацию
    try:
        predicted_price = predict_next(symbol, binance_interval)
        current_price = get_binance_data(symbol, binance_interval).iloc[-1]["close"]
        recommendation = get_recommendation(predicted_price, current_price)

        await message.answer(
            f"Прогнозируемая цена {symbol} на {interval}: {predicted_price:.2f}\n"
            f"Текущая цена: {current_price:.2f}\n"
            f"Рекомендация: {recommendation}"
        )
    except Exception as e:
        await message.answer(f"Ошибка при расчете: {e}")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
