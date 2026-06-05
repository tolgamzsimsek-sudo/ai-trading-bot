import pandas as pd
import numpy as np
import ta
import logging
import config

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.signals = {}
    
    def calculate_rsi(self, period=config.RSI_PERIOD):
        """
        Calculate Relative Strength Index
        """
        self.df['rsi'] = ta.momentum.rsi(self.df['close'], window=period)
        return self.df['rsi'].iloc[-1]
    
    def calculate_macd(self):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        try:
            macd_line = ta.trend.macd(self.df['close'], window_fast=config.MACD_FAST, 
                                       window_slow=config.MACD_SLOW)
            macd_signal = ta.trend.macd_signal(self.df['close'], 
                                               window_fast=config.MACD_FAST,
                                               window_slow=config.MACD_SLOW, 
                                               window_sign=config.MACD_SIGNAL)
            self.df['macd'] = macd_line
            self.df['macd_signal'] = macd_signal
            self.df['macd_diff'] = self.df['macd'] - self.df['macd_signal']
            return self.df['macd'].iloc[-1], self.df['macd_signal'].iloc[-1]
        except:
            # Fallback if MACD fails
            return 0, 0
    
    def calculate_bollinger_bands(self, period=config.BB_PERIOD, std_dev=config.BB_STD_DEV):
        """
        Calculate Bollinger Bands
        """
        bb = ta.volatility.BollingerBands(self.df['close'], window=period, window_dev=std_dev)
        self.df['bb_high'] = bb.bollinger_hband()
        self.df['bb_mid'] = bb.bollinger_mavg()
        self.df['bb_low'] = bb.bollinger_lband()
        return self.df['bb_high'].iloc[-1], self.df['bb_mid'].iloc[-1], self.df['bb_low'].iloc[-1]
    
    def calculate_moving_averages(self):
        """
        Calculate SMA (Simple Moving Average)
        """
        self.df['sma_20'] = ta.trend.sma_indicator(self.df['close'], window=20)
        self.df['sma_50'] = ta.trend.sma_indicator(self.df['close'], window=50)
        self.df['sma_200'] = ta.trend.sma_indicator(self.df['close'], window=200)
        return self.df['sma_20'].iloc[-1], self.df['sma_50'].iloc[-1], self.df['sma_200'].iloc[-1]
    
    def get_technical_signals(self):
        """
        Generate signals from technical analysis
        """
        signals = {'buy': 0, 'sell': 0, 'neutral': 0}
        
        # RSI Signals
        rsi = self.calculate_rsi()
        if rsi < config.RSI_OVERSOLD:
            signals['buy'] += 2
        elif rsi > config.RSI_OVERBOUGHT:
            signals['sell'] += 2
        
        # MACD Signals
        macd, signal = self.calculate_macd()
        if macd > signal:
            signals['buy'] += 1
        else:
            signals['sell'] += 1
        
        # Bollinger Bands Signals
        bb_high, bb_mid, bb_low = self.calculate_bollinger_bands()
        current_price = self.df['close'].iloc[-1]
        if current_price < bb_low:
            signals['buy'] += 1
        elif current_price > bb_high:
            signals['sell'] += 1
        
        # Moving Averages Signals
        sma_20, sma_50, sma_200 = self.calculate_moving_averages()
        if sma_20 > sma_50 > sma_200:
            signals['buy'] += 1
        elif sma_20 < sma_50 < sma_200:
            signals['sell'] += 1
        
        return signals
    
    def get_dataframe(self):
        return self.df
