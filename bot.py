import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from model import predict_next

TOKEN = "ТВОЙ_TELEGRAM_BOT_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer("Привет! Отправь мне валютную пару (например, BTCUSDT), и я предскажу цену.")

@dp.message_handler()
async def get_prediction(message: Message):
    try:
        prediction = predict_next(message.text)
        await message.answer(f"Прогнозируемая цена {message.text}: {prediction[0][0]:.2f}")
    except Exception as e:
        await message.answer("Ошибка: " + str(e))

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
