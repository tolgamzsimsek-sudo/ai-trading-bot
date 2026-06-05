import logging
import time
from datetime import datetime
import config
from data_handler import DataHandler
from technical_analysis import TechnicalAnalyzer
from ml_model import MLPredictor
from colorama import Fore, Style, init
import numpy as np
import pandas as pd

init(autoreset=True)

logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HybridTradingBot:
    def __init__(self):
        self.running = False
        self.trade_log = []
        self.positions = {}
        
        # Test modunda Binance'e bağlanmayı atla
        if config.BINANCE_API_KEY == "test":
            self.data_handler = None
            logger.info(f"{Fore.YELLOW}⚠️  Test modu - Binance bağlantısı atlanıyor")
        else:
            try:
                self.data_handler = DataHandler()
            except Exception as e:
                logger.warning(f"{Fore.YELLOW}⚠️  Binance bağlantı hatası, test modu kullanılıyor: {str(e)}")
                self.data_handler = None
        
        logger.info(f"{Fore.GREEN}🤖 Hibrit Trading Bot Başlatıldı")
        logger.info(f"{Fore.CYAN}📊 Symbol: {config.TRADING_SYMBOL}")
        logger.info(f"{Fore.CYAN}⏱️  Timeframe: {config.TRADING_TIMEFRAME}")
        logger.info(f"{Fore.CYAN}💰 Amount: {config.TRADING_AMOUNT}")
        logger.info(f"{Fore.YELLOW}{('🔄 DRY RUN MODE' if config.DRY_RUN else '💵 LIVE TRADING MODE')}")
    
    def generate_test_data(self):
        """
        Test modu için sahte veri üret
        """
        np.random.seed(42)
        dates = pd.date_range(end=datetime.now(), periods=500, freq='5min')
        
        # Gerçekçi fiyat hareketi oluştur
        price = 45000
        prices = [price]
        for _ in range(499):
            change = np.random.normal(0, 50)
            price += change
            prices.append(max(price, 1000))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + np.random.uniform(0, 100) for p in prices],
            'low': [max(p - np.random.uniform(0, 100), 1000) for p in prices],
            'close': [p + np.random.normal(0, 30) for p in prices],
            'volume': np.random.uniform(100, 10000, 500)
        })
        
        return df
    
    def calculate_price_targets(self, entry_price, signal):
        """
        Calculate Stop Loss, Target 1, and Target 2 based on signal
        """
        if signal == 'BUY':
            stop_loss = entry_price * (1 - config.STOP_LOSS_PERCENT / 100)
            target_1 = entry_price * (1 + config.TAKE_PROFIT_PERCENT / 100)
            target_2 = entry_price * (1 + (config.TAKE_PROFIT_PERCENT * 2) / 100)
        elif signal == 'SELL':
            stop_loss = entry_price * (1 + config.STOP_LOSS_PERCENT / 100)
            target_1 = entry_price * (1 - config.TAKE_PROFIT_PERCENT / 100)
            target_2 = entry_price * (1 - (config.TAKE_PROFIT_PERCENT * 2) / 100)
        else:
            return None
        
        return {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_1': target_1,
            'target_2': target_2,
            'risk_reward_1': (target_1 - entry_price) / (entry_price - stop_loss) if entry_price != stop_loss else 0,
            'risk_reward_2': (target_2 - entry_price) / (entry_price - stop_loss) if entry_price != stop_loss else 0
        }
    
    def analyze_market(self):
        """
        Analyze market using hybrid approach (Technical + ML)
        """
        logger.info(f"{Fore.BLUE}📈 Pazar analizi başlanıyor...")
        
        # Test modu veri kullan
        if self.data_handler is None or config.BINANCE_API_KEY == "test":
            df = self.generate_test_data()
            logger.info(f"{Fore.YELLOW}📡 Test veri kullanılıyor")
        else:
            df = self.data_handler.get_historical_data(limit=500)
        
        if df is None or len(df) < 100:
            logger.error(f"{Fore.RED}❌ Yeterli veri yok")
            return None
        
        # Technical Analysis
        logger.info(f"{Fore.BLUE}🔧 Teknik analiz yapılıyor...")
        ta = TechnicalAnalyzer(df)
        tech_signals = ta.get_technical_signals()
        logger.info(f"{Fore.CYAN}📊 Teknik Sinyaller - Buy: {tech_signals['buy']}, Sell: {tech_signals['sell']}")
        
        # Machine Learning Analysis
        logger.info(f"{Fore.BLUE}🧠 ML modeli çalıştırılıyor...")
        try:
            ml = MLPredictor(df)
            X_train, X_test, y_train, y_test = ml.prepare_data()
            
            # Build and train models
            ml.build_lstm_model()
            ml.train_lstm_model(X_train, y_train, epochs=20)
            ml.build_random_forest_model()
            ml.train_random_forest(X_train, y_train)
            
            # Get ensemble prediction
            ensemble_pred = ml.get_ensemble_prediction(X_test[-10:])
            ml_signal = np.mean(ensemble_pred) if ensemble_pred is not None else 0.5
            logger.info(f"{Fore.CYAN}🎯 ML Tahmini: {ml_signal:.4f} (>0.5=BUY, <0.5=SELL)")
        except Exception as e:
            logger.error(f"{Fore.RED}❌ ML hatası: {str(e)}")
            ml_signal = 0.5
        
        # Combine signals
        final_signal = self.combine_signals(tech_signals, ml_signal)
        
        return {
            'tech_signals': tech_signals,
            'ml_signal': ml_signal,
            'final_signal': final_signal,
            'price': df['close'].iloc[-1],
            'df': df
        }
    
    def combine_signals(self, tech_signals, ml_signal):
        """
        Combine technical and ML signals
        """
        tech_score = (tech_signals['buy'] - tech_signals['sell']) / 10
        ml_score = ml_signal - 0.5
        
        # Weighted combination (60% technical, 40% ML)
        final_score = (tech_score * 0.6) + (ml_score * 0.4)
        
        if final_score > 0.3:
            return 'BUY'
        elif final_score < -0.3:
            return 'SELL'
        else:
            return 'HOLD'
    
    def display_trade_setup(self, signal, price):
        """
        Display detailed trade setup with entry, SL, and targets
        """
        if signal == 'HOLD':
            logger.info(f"{Fore.YELLOW}⭕ HOLD - Bekleniyor...\n")
            return
        
        targets = self.calculate_price_targets(price, signal)
        
        if signal == 'BUY':
            logger.info(f"\n{Fore.GREEN}{'='*70}")
            logger.info(f"{Fore.GREEN}🟢 BUY SİNYALİ ALINDI")
            logger.info(f"{Fore.GREEN}{'='*70}")
        else:
            logger.info(f"\n{Fore.RED}{'='*70}")
            logger.info(f"{Fore.RED}🔴 SELL SİNYALİ ALINDI")
            logger.info(f"{Fore.RED}{'='*70}")
        
        # Display trade setup
        logger.info(f"\n{Fore.CYAN}📍 GİRİŞ FİYATI (Entry): {Fore.YELLOW}{targets['entry_price']:.2f}")
        logger.info(f"{Fore.CYAN}🛑 STOPLOSS: {Fore.RED}{targets['stop_loss']:.2f}")
        logger.info(f"{Fore.CYAN}🎯 TARGET 1: {Fore.GREEN}{targets['target_1']:.2f} {Fore.WHITE}(Risk/Reward: {targets['risk_reward_1']:.2f}:1)")
        logger.info(f"{Fore.CYAN}🎯 TARGET 2: {Fore.GREEN}{targets['target_2']:.2f} {Fore.WHITE}(Risk/Reward: {targets['risk_reward_2']:.2f}:1)")
        
        if signal == 'BUY':
            profit_range = targets['target_2'] - targets['entry_price']
            loss_range = targets['entry_price'] - targets['stop_loss']
            logger.info(f"{Fore.CYAN}📊 Maksimum Kar Potansiyeli: {Fore.GREEN}{profit_range:.2f} ({(profit_range/targets['entry_price']*100):.2f}%)")
            logger.info(f"{Fore.CYAN}📊 Maksimum Zarar Riski: {Fore.RED}{loss_range:.2f} ({(loss_range/targets['entry_price']*100):.2f}%)")
        else:
            profit_range = targets['entry_price'] - targets['target_2']
            loss_range = targets['stop_loss'] - targets['entry_price']
            logger.info(f"{Fore.CYAN}📊 Maksimum Kar Potansiyeli: {Fore.GREEN}{profit_range:.2f} ({(profit_range/targets['entry_price']*100):.2f}%)")
            logger.info(f"{Fore.CYAN}📊 Maksimum Zarar Riski: {Fore.RED}{loss_range:.2f} ({(loss_range/targets['entry_price']*100):.2f}%)")
        
        logger.info(f"{Fore.CYAN}{'─'*70}\n")
        
        if config.DRY_RUN:
            logger.info(f"{Fore.YELLOW}[DRY RUN] {config.TRADING_AMOUNT} {config.TRADING_SYMBOL} işlemi simüle edildi")
            self.positions['entry_price'] = price
            self.positions['entry_time'] = datetime.now()
    
    def execute_trade(self, signal, price):
        """
        Execute trade based on signal
        """
        if signal == 'BUY':
            if config.DRY_RUN:
                self.display_trade_setup('BUY', price)
            else:
                logger.info(f"{Fore.GREEN}💰 GERÇEK İŞLEM: {config.TRADING_AMOUNT} {config.TRADING_SYMBOL} alınıyor...")
                self.display_trade_setup('BUY', price)
        
        elif signal == 'SELL':
            if config.DRY_RUN:
                self.display_trade_setup('SELL', price)
            else:
                logger.info(f"{Fore.RED}💰 GERÇEK İŞLEM: {config.TRADING_AMOUNT} {config.TRADING_SYMBOL} satılıyor...")
                self.display_trade_setup('SELL', price)
        
        else:
            logger.info(f"{Fore.YELLOW}⭕ HOLD - Bekleniyor...\n")
    
    def run(self, interval=300):
        """
        Run the bot continuously
        """
        self.running = True
        logger.info(f"{Fore.GREEN}✅ Bot çalışmaya başladı!")
        logger.info(f"{Fore.CYAN}⏰ Analiz aralığı: {interval} saniye ({interval//60} dakika)")
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                logger.info(f"\n{Fore.MAGENTA}{'='*70}")
                logger.info(f"{Fore.MAGENTA}📋 İterasyon #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{Fore.MAGENTA}{'='*70}")
                
                analysis = self.analyze_market()
                
                if analysis:
                    logger.info(f"\n{Fore.CYAN}{'─'*70}")
                    logger.info(f"{Fore.CYAN}📊 FINAL SINYAL: {Fore.YELLOW}{analysis['final_signal']}{Fore.CYAN}")
                    logger.info(f"{Fore.CYAN}💹 MEVCUT FİYAT: {Fore.YELLOW}{analysis['price']:.2f}")
                    logger.info(f"{Fore.CYAN}{'─'*70}")
                    
                    self.execute_trade(analysis['final_signal'], analysis['price'])
                
                logger.info(f"{Fore.BLUE}💤 Sonraki kontrol: {interval} saniye sonra...\n")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info(f"\n{Fore.RED}⛔ Bot durduruldu (Ctrl+C)")
            self.running = False
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Hata: {str(e)}")
            self.running = False

if __name__ == "__main__":
    bot = HybridTradingBot()
    # 5 dakika = 300 saniye
    bot.run(interval=300)
