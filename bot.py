import os
import time
import logging
import numpy as np
from pybit.unified_trading import HTTP
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import requests

# Конфигурация
API_KEY = "eEswxhyhPeTP292Hsq"
API_SECRET = "UEnSj2eL1HKVGFEnJr5Icp9CpxKVvb6LiAli"
TELEGRAM_TOKEN = "7964441740:AAEQH_N-Alj9SEDTfbpjrsfxF4QflNPJCH4"
CHAT_ID = "1771266956"
SYMBOL = "BTCUSDT"
TIMEFRAME = "15"
TRADING_MODE = True  # True = testnet

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

class TradingBot:
    def __init__(self):
        self.session = HTTP(
            api_key=API_KEY,
            api_secret=API_SECRET,
            testnet=TRADING_MODE
        )
        self.model = self.build_model()
        self.balance = self.get_balance()
        
    def build_model(self):
        model = Sequential([
            LSTM(64, input_shape=(60, 1)),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
        
    def get_balance(self):
        res = self.session.get_wallet_balance(accountType="SPOT")
        return float(res["result"]["list"][0]["coin"][0]["walletBalance"])
    
    def preprocess_data(self, data):
        prices = np.array([float(d[4]) for d in data])
        normalized = (prices - np.mean(prices)) / np.std(prices)
        
        X, y = [], []
        for i in range(len(normalized)-60):
            X.append(normalized[i:i+60])
            y.append(normalized[i+60])
            
        return np.array(X), np.array(y)
    
    def predict_price(self, X):
        return self.model.predict(np.array([X]))[0][0]
    
    def calculate_position(self, price):
        risk = 2  # 2% от баланса
        return round((self.balance * risk/100) / price, 4)
    
    def send_alert(self, message):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, params=params)
    
    def trade_cycle(self):
        try:
            # Получение данных
            klines = self.session.get_kline(
                category="spot",
                symbol=SYMBOL,
                interval=TIMEFRAME,
                limit=200
            )["result"]["list"]
            
            # Обучение модели
            X, y = self.preprocess_data(klines)
            self.model.fit(X, y, epochs=30, verbose=0)
            
            # Прогноз
            last_data = X[-1]
            predicted = self.predict_price(last_data)
            current_price = float(klines[-1][4])
            
            # Расчет позиции
            qty = self.calculate_position(current_price)
            
            # Логика
            if predicted > current_price * 1.002:
                self.session.place_order(
                    category="spot",
                    symbol=SYMBOL,
                    side="Buy",
                    orderType="Market",
                    qty=qty
                )
                msg = f"🟢 BUY {qty} {SYMBOL} @ {current_price}"
                logging.info(msg)
                self.send_alert(msg)
                
            elif predicted < current_price * 0.998:
                self.session.place_order(
                    category="spot",
                    symbol=SYMBOL,
                    side="Sell",
                    orderType="Market",
                    qty=qty
                )
                msg = f"🔴 SELL {qty} {SYMBOL} @ {current_price}"
                logging.info(msg)
                self.send_alert(msg)
                
        except Exception as e:
            error_msg = f"🚨 Error: {str(e)}"
            logging.error(error_msg)
            self.send_alert(error_msg)

if __name__ == "__main__":
    bot = TradingBot()
    logging.info("Bot started successfully!")
    bot.send_alert("🤖 Trading bot activated!")
    
    while True:
        bot.trade_cycle()
        time.sleep(60 * int(TIMEFRAME))
