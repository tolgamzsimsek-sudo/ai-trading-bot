import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import logging
import config
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MLPredictor:
    def __init__(self, df):
        self.df = df.copy()
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.rf_model = None
    
    def prepare_data(self, lookback=config.ML_LOOKBACK_PERIOD):
        """
        Prepare data for ML model
        """
        data = self.df['close'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(len(scaled_data) - lookback):
            X.append(scaled_data[i:(i + lookback)])
            # 1 if price goes up, 0 if down
            y.append(1 if scaled_data[i + lookback] > scaled_data[i + lookback - 1] else 0)
        
        X, y = np.array(X), np.array(y)
        train_size = int(len(X) * config.ML_TRAIN_SIZE)
        
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        return X_train, X_test, y_train, y_test
    
    def build_lstm_model(self, lookback=config.ML_LOOKBACK_PERIOD):
        """
        Build LSTM neural network model
        """
        try:
            self.model = Sequential([
                LSTM(128, activation='relu', input_shape=(lookback, 1), return_sequences=True),
                Dropout(0.2),
                LSTM(64, activation='relu', return_sequences=False),
                Dropout(0.2),
                Dense(32, activation='relu'),
                Dense(1, activation='sigmoid')
            ])
            
            self.model.compile(optimizer=Adam(learning_rate=0.001), 
                             loss='binary_crossentropy', 
                             metrics=['accuracy'])
            logger.info("✅ LSTM model built successfully")
            return self.model
        except Exception as e:
            logger.error(f"❌ Error building LSTM model: {str(e)}")
            return None
    
    def train_lstm_model(self, X_train, y_train, epochs=config.ML_EPOCHS):
        """
        Train LSTM model
        """
        try:
            self.model.fit(X_train, y_train, 
                          epochs=epochs, 
                          batch_size=config.ML_BATCH_SIZE,
                          verbose=0)
            logger.info(f"✅ LSTM model trained for {epochs} epochs")
        except Exception as e:
            logger.error(f"❌ Error training LSTM: {str(e)}")
    
    def build_random_forest_model(self):
        """
        Build Random Forest model
        """
        try:
            self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            logger.info("✅ Random Forest model built successfully")
            return self.rf_model
        except Exception as e:
            logger.error(f"❌ Error building RF model: {str(e)}")
            return None
    
    def train_random_forest(self, X_train, y_train):
        """
        Train Random Forest model
        """
        try:
            # Reshape for Random Forest
            X_train_2d = X_train.reshape(X_train.shape[0], -1)
            self.rf_model.fit(X_train_2d, y_train)
            logger.info("✅ Random Forest model trained successfully")
        except Exception as e:
            logger.error(f"❌ Error training RF: {str(e)}")
    
    def predict_lstm(self, X_test):
        """
        Make predictions with LSTM
        """
        try:
            predictions = self.model.predict(X_test, verbose=0)
            return predictions
        except Exception as e:
            logger.error(f"❌ Error predicting with LSTM: {str(e)}")
            return None
    
    def predict_random_forest(self, X_test):
        """
        Make predictions with Random Forest
        """
        try:
            X_test_2d = X_test.reshape(X_test.shape[0], -1)
            predictions = self.rf_model.predict_proba(X_test_2d)[:, 1]
            return predictions
        except Exception as e:
            logger.error(f"❌ Error predicting with RF: {str(e)}")
            return None
    
    def get_ensemble_prediction(self, X_test):
        """
        Get ensemble prediction (average of LSTM and RF)
        """
        lstm_pred = self.predict_lstm(X_test)
        rf_pred = self.predict_random_forest(X_test)
        
        if lstm_pred is not None and rf_pred is not None:
            ensemble_pred = (lstm_pred.flatten() + rf_pred) / 2
            return ensemble_pred
        return None
