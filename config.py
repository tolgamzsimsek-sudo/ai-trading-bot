import os
from dotenv import load_dotenv

load_dotenv()

# Binance Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Trading Configuration
TRADING_SYMBOL = os.getenv('TRADING_SYMBOL', 'BTCUSDT')
TRADING_TIMEFRAME = os.getenv('TRADING_TIMEFRAME', '5m')
TRADING_AMOUNT = float(os.getenv('TRADING_AMOUNT', '0.001'))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '2.0'))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '1.0'))

# Bot Settings
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Technical Analysis Settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD_DEV = 2

# ML Model Settings
ML_LOOKBACK_PERIOD = 100
ML_TRAIN_SIZE = 0.8
ML_TEST_SIZE = 0.2
ML_EPOCHS = 50
ML_BATCH_SIZE = 32

# Timeframe Mapping
TIMEFRAME_MAP = {
    '1m': 1,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
    '4h': 240,
    '1d': 1440
}

print("✅ Configuration loaded successfully")
