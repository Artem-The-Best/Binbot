import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from data_fetcher import get_binance_data

scaler = MinMaxScaler()

def prepare_data(symbol="BTCUSDT"):
    df = get_binance_data(symbol)
    df["close_scaled"] = scaler.fit_transform(df["close"].values.reshape(-1, 1))
    seq_len = 50
    X, y = [], []
    for i in range(len(df) - seq_len):
        X.append(df["close_scaled"].values[i:i+seq_len])
        y.append(df["close_scaled"].values[i+seq_len])
    return np.array(X), np.array(y)

def train_model(symbol="BTCUSDT"):
    X, y = prepare_data(symbol)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50, return_sequences=False),
        Dense(25),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=16, verbose=1)
    model.save(f"{symbol}_lstm_model.h5")
    return model

def predict_next(symbol="BTCUSDT"):
    from tensorflow.keras.models import load_model
    model = load_model(f"{symbol}_lstm_model.h5")
    X, _ = prepare_data(symbol)
    return scaler.inverse_transform(model.predict(X[-1].reshape(1, X.shape[1], 1)))

if __name__ == "__main__":
    train_model()
    print("Next price prediction:", predict_next())
