from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import threading
import logging
from bot import HybridTradingBot
import config

app = Flask(__name__)
CORS(app)

# Global bot instance
bot_instance = None
bot_thread = None

# Store latest analysis
latest_data = {
    'signal': 'HOLD',
    'price': 0,
    'timestamp': None,
    'entry': 0,
    'stoploss': 0,
    'target1': 0,
    'target2': 0,
    'tech_buy': 0,
    'tech_sell': 0,
    'ml_signal': 0.5,
    'history': []
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get bot status and latest data"""
    return jsonify({
        'status': 'running',
        'symbol': config.TRADING_SYMBOL,
        'dry_run': config.DRY_RUN,
        'trading_amount': config.TRADING_AMOUNT,
        'latest': latest_data
    })

@app.route('/api/latest')
def get_latest():
    """Get latest signal data"""
    return jsonify(latest_data)

@app.route('/api/history')
def get_history():
    """Get trading history"""
    return jsonify({'history': latest_data['history']})

@app.route('/api/config')
def get_config():
    """Get configuration"""
    return jsonify({
        'symbol': config.TRADING_SYMBOL,
        'timeframe': config.TRADING_TIMEFRAME,
        'take_profit': config.TAKE_PROFIT_PERCENT,
        'stop_loss': config.STOP_LOSS_PERCENT,
        'dry_run': config.DRY_RUN
    })

def update_latest_data(analysis, signal):
    """Update global latest_data with new analysis"""
    global latest_data
    
    if analysis:
        targets = bot_instance.calculate_price_targets(analysis['price'], signal)
        
        latest_data.update({
            'signal': signal,
            'price': round(analysis['price'], 2),
            'timestamp': datetime.now().isoformat(),
            'entry': round(targets['entry_price'], 2) if targets else 0,
            'stoploss': round(targets['stop_loss'], 2) if targets else 0,
            'target1': round(targets['target_1'], 2) if targets else 0,
            'target2': round(targets['target_2'], 2) if targets else 0,
            'tech_buy': analysis['tech_signals']['buy'],
            'tech_sell': analysis['tech_signals']['sell'],
            'ml_signal': round(analysis['ml_signal'], 4)
        })
        
        # Add to history
        latest_data['history'].append({
            'timestamp': latest_data['timestamp'],
            'signal': signal,
            'price': latest_data['price'],
            'entry': latest_data['entry'],
            'target1': latest_data['target1'],
            'target2': latest_data['target2']
        })
        
        # Keep only last 100 records
        if len(latest_data['history']) > 100:
            latest_data['history'] = latest_data['history'][-100:]

def run_bot_loop():
    """Run bot in background thread with shorter interval for dashboard"""
    global bot_instance
    
    bot_instance = HybridTradingBot()
    
    iteration = 0
    while True:
        try:
            iteration += 1
            logger.info(f"Bot iteration #{iteration}")
            
            analysis = bot_instance.analyze_market()
            if analysis:
                signal = analysis['final_signal']
                update_latest_data(analysis, signal)
                logger.info(f"Signal: {signal}, Price: {analysis['price']}")
            
            # 2 dakika aralık (test için kısa tuttum)
            import time
            time.sleep(120)
        
        except Exception as e:
            logger.error(f"Bot error: {str(e)}")
            import time
            time.sleep(60)

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
    bot_thread.start()
    
    # Run Flask app
    app.run(debug=False, host='0.0.0.0', port=5000)
