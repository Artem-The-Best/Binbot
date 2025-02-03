import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import os
from data_fetcher import get_binance_data

scaler = MinMaxScaler()

def prepare_data(symbol="BTCUSDT", interval="1h"):
    """Подготавливает данные для обучения LSTM"""
    df = get_binance_data(symbol, interval)
    df["close_scaled"] = scaler.fit_transform(df["close"].values.reshape(-1, 1))
    
    seq_len = 50  # Длина последовательности
    X, y = [], []
    
    for i in range(len(df) - seq_len):
        X.append(df["close_scaled"].values[i:i+seq_len])
        y.append(df["close_scaled"].values[i+seq_len])
    
    return np.array(X), np.array(y)

def train_model(symbol="BTCUSDT", interval="1h"):
    """Обучает модель LSTM"""
    X, y = prepare_data(symbol, interval)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50, return_sequences=False),
        Dense(25),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=16, verbose=1)

    model_path = f"models/{symbol}_{interval}_lstm.h5"
    os.makedirs("models", exist_ok=True)
    model.save(model_path)

    return model

def predict_next(symbol="BTCUSDT", interval="1h"):
    """Делает предсказание с использованием обученной модели"""
    model_path = f"models/{symbol}_{interval}_lstm.h5"

    if not os.path.exists(model_path):
        train_model(symbol, interval)

    model = load_model(model_path)
    X, _ = prepare_data(symbol, interval)
    
    prediction = model.predict(X[-1].reshape(1, X.shape[1], 1))
    return scaler.inverse_transform(prediction)[0][0]

def get_recommendation(predicted_price, current_price):
    """Выдаёт рекомендацию на основе предсказания"""
    change = (predicted_price - current_price) / current_price * 100

    if change > 0.5:
        return "🔼 Покупать"
    elif change < -0.5:
        return "🔽 Продавать"
    else:
        return "⏳ Ждать"

if __name__ == "__main__":
    symbol = "BTCUSDT"
    interval = "1h"
    prediction = predict_next(symbol, interval)
    current_price = get_binance_data(symbol, interval).iloc[-1]["close"]
    recommendation = get_recommendation(prediction, current_price)

    print(f"Прогнозируемая цена: {prediction:.2f}")
    print(f"Текущая цена: {current_price:.2f}")
    print(f"Рекомендация: {recommendation}")
