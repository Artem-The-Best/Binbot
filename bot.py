import os
import asyncio
import ccxt.async_support as ccxt
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# API-ключи
BYBIT_API_KEY = Hmhbm9aXfTlT5l7hAQ
BYBIT_SECRET_KEY = HJLTwcdjPyhJiOKMuzUCmERf0R8EORlkjQLc

# Подключение к Bybit
exchange = ccxt.bybit({
    'apiKey': BYBIT_API_KEY,
    'secret': BYBIT_SECRET_KEY,
})

# Список валютных пар для анализа (спот и фьючерсы)
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "MATIC/USDT",
    "LTC/USDT", "TRX/USDT", "LINK/USDT", "ATOM/USDT", "XLM/USDT",
    "NEAR/USDT", "FIL/USDT", "ALGO/USDT", "VET/USDT", "ICP/USDT"
]

# Порог арбитража (например, 0.5% разница)
ARBITRAGE_THRESHOLD = 0.005  

async def fetch_prices(symbol):
    """Получает цены для спотового и фьючерсного рынков."""
    try:
        # Спотовая цена
        exchange.options['defaultType'] = 'spot'
        spot_ticker = await exchange.fetch_ticker(symbol)
        spot_price = spot_ticker['last']

        # Фьючерсная цена
        exchange.options['defaultType'] = 'future'
        future_ticker = await exchange.fetch_ticker(symbol)
        future_price = future_ticker['last']

        return symbol, spot_price, future_price
    except Exception as e:
        print(f"Ошибка получения цен для {symbol}: {e}")
        return symbol, None, None

async def check_arbitrage():
    """Проверяет арбитраж для всех валют."""
    while True:
        tasks = [fetch_prices(symbol) for symbol in SYMBOLS]
        results = await asyncio.gather(*tasks)

        for symbol, spot_price, future_price in results:
            if spot_price and future_price:
                spread = (future_price - spot_price) / spot_price
                print(f"{symbol}: Спот {spot_price}, Фьючерс {future_price}, Спред {spread:.4f}")

                if spread > ARBITRAGE_THRESHOLD:
                    print(f"[АРБИТРАЖ] Выгодная возможность на {symbol}!")

        await asyncio.sleep(1)  # Минимальная задержка

async def main():
    await check_arbitrage()

if __name__ == "__main__":
    asyncio.run(main())
