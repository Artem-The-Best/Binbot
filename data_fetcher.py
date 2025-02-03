from binance.client import Client
import pandas as pd

# API-ключи (лучше хранить в переменных окружения)
API_KEY = "ТВОЙ_API_KEY"
API_SECRET = "ТВОЙ_API_SECRET"

client = Client(API_KEY, API_SECRET)

def get_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].astype(float)
    return df

if __name__ == "__main__":
    print(get_binance_data().head())
