from binance.client import Client
import pandas as pd
import os

# Подставь свои API-ключи
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

# Словарь интервалов Binance
INTERVALS = {
    "1m": Client.KLINE_INTERVAL_1MINUTE,
    "5m": Client.KLINE_INTERVAL_5MINUTE,
    "10m": Client.KLINE_INTERVAL_5MINUTE,  # Нет точного 10m, берём 5m и удваиваем
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "30m": Client.KLINE_INTERVAL_30MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR,
    "2h": Client.KLINE_INTERVAL_2HOUR,
    "4h": Client.KLINE_INTERVAL_4HOUR,
    "1d": Client.KLINE_INTERVAL_1DAY,
    "2d": Client.KLINE_INTERVAL_1DAY,  # Нет 2d, берём 1d и удваиваем
    "3d": Client.KLINE_INTERVAL_1DAY,  # Нет 3d, берём 1d и утраиваем
    "1w": Client.KLINE_INTERVAL_1WEEK,
}

def get_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    """Получает исторические данные по валютной паре и интервалу"""
    if interval not in INTERVALS:
        raise ValueError("Неподдерживаемый интервал")
    
    klines = client.get_klines(symbol=symbol, interval=INTERVALS[interval], limit=limit)
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].astype(float)
    
    # Агрегация, если нужно (для 10m, 2d, 3d)
    if interval == "10m":
        df = df.resample("10T", on="timestamp").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna().reset_index()
    elif interval in ["2d", "3d"]:
        days = int(interval[0])
        df = df.resample(f"{days}D", on="timestamp").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna().reset_index()
    
    return df

if __name__ == "__main__":
    print(get_binance_data("BTCUSDT", "1h").head())
