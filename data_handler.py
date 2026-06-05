import pandas as pd
import numpy as np
from binance.client import Client
import logging
from datetime import datetime, timedelta
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class DataHandler:
    def __init__(self):
        self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        self.symbol = config.TRADING_SYMBOL
        self.interval = config.TRADING_TIMEFRAME
    
    def get_historical_data(self, limit=500):
        """
        Get historical OHLCV data from Binance
        """
        try:
            klines = self.client.get_historical_klines(
                self.symbol,
                self.interval,
                f"{limit * config.TIMEFRAME_MAP[self.interval]} minutes ago UTC"
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert to numeric
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            logger.info(f"📊 Retrieved {len(df)} candles for {self.symbol}")
            return df
        
        except Exception as e:
            logger.error(f"❌ Error fetching data: {str(e)}")
            return None
    
    def get_latest_price(self):
        """
        Get the latest price of the trading symbol
        """
        try:
            ticker = self.client.get_symbol_info(self.symbol)
            price = self.client.get_average_price(symbol=self.symbol)
            return float(price['price'])
        except Exception as e:
            logger.error(f"❌ Error getting price: {str(e)}")
            return None
    
    def get_account_balance(self):
        """
        Get account balance information
        """
        try:
            account = self.client.get_account()
            balances = {}
            for asset in account['balances']:
                free = float(asset['free'])
                locked = float(asset['locked'])
                if free > 0 or locked > 0:
                    balances[asset['asset']] = {'free': free, 'locked': locked}
            return balances
        except Exception as e:
            logger.error(f"❌ Error getting balance: {str(e)}")
            return None
