import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import ta
import joblib
import os
from datetime import datetime, timedelta
import logging
import asyncio

from binance_client import BinanceClient

logger = logging.getLogger(__name__)

class CryptoPredictor:
    def __init__(self):
        self.binance_client = BinanceClient()
        self.models = {}
        self.scalers = {}
        self.model_dir = 'models'
        
        # Tạo thư mục models nếu chưa có
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def calculate_technical_indicators(self, df):
        """Tính toán các chỉ báo kỹ thuật"""
        try:
            # Moving Averages
            df['sma_7'] = ta.trend.sma_indicator(df['close'], window=7)
            df['sma_25'] = ta.trend.sma_indicator(df['close'], window=25)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['close'])
            df['macd_signal'] = ta.trend.macd_signal(df['close'])
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Stochastic
            df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
            
            # Williams %R
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['vwap'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'])
            
            # Price features
            df['price_change'] = df['close'].pct_change()
            df['high_low_ratio'] = df['high'] / df['low']
            df['close_open_ratio'] = df['close'] / df['open']
            
            # Volatility
            df['volatility'] = df['close'].rolling(window=20).std()
            
            # Support and Resistance levels
            df['support'] = df['low'].rolling(window=20).min()
            df['resistance'] = df['high'].rolling(window=20).max()
            
            return df
            
        except Exception as e:
            logger.error(f"Lỗi tính toán chỉ báo kỹ thuật: {e}")
            return df
    
    def prepare_features(self, df):
        """Chuẩn bị features cho model"""
        feature_columns = [
            'open', 'high', 'low', 'volume',
            'sma_7', 'sma_25', 'ema_12', 'ema_26',
            'macd', 'macd_signal', 'rsi',
            'bb_upper', 'bb_lower', 'bb_middle', 'bb_width',
            'stoch_k', 'stoch_d', 'williams_r',
            'volume_sma', 'vwap',
            'price_change', 'high_low_ratio', 'close_open_ratio',
            'volatility', 'support', 'resistance'
        ]
        
        # Lọc các cột có sẵn
        available_features = [col for col in feature_columns if col in df.columns]
        
        # Tạo target (giá sau 1 giờ)
        df['target'] = df['close'].shift(-1)
        
        # Loại bỏ NaN
        df_clean = df[available_features + ['target']].dropna()
        
        if len(df_clean) < 50:
            logger.warning("Không đủ dữ liệu để training")
            return None, None
        
        X = df_clean[available_features]
        y = df_clean['target']
        
        return X, y
    
    async def train_model(self, symbol, retrain=False):
        """Training model cho một symbol"""
        try:
            model_path = os.path.join(self.model_dir, f'{symbol}_model.pkl')
            scaler_path = os.path.join(self.model_dir, f'{symbol}_scaler.pkl')
            
            # Kiểm tra nếu model đã tồn tại và không cần retrain
            if not retrain and os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[symbol] = joblib.load(model_path)
                self.scalers[symbol] = joblib.load(scaler_path)
                logger.info(f"Đã load model cho {symbol}")
                return True
            
            # Lấy dữ liệu lịch sử
            logger.info(f"Đang lấy dữ liệu training cho {symbol}...")
            df = await self.binance_client.get_historical_data(symbol, interval='1h', limit=500)
            
            if df is None or len(df) < 100:
                logger.error(f"Không đủ dữ liệu cho {symbol}")
                return False
            
            # Tính toán chỉ báo kỹ thuật
            df = self.calculate_technical_indicators(df)
            
            # Chuẩn bị features
            X, y = self.prepare_features(df)
            
            if X is None or len(X) < 50:
                logger.error(f"Không đủ features cho {symbol}")
                return False
            
            # Chia dữ liệu
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Chuẩn hóa dữ liệu
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Training ensemble model
            models = {
                'rf': RandomForestRegressor(n_estimators=100, random_state=42),
                'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'lr': LinearRegression()
            }
            
            best_model = None
            best_score = float('inf')
            
            for name, model in models.items():
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                
                if mse < best_score:
                    best_score = mse
                    best_model = model
            
            # Lưu model và scaler
            self.models[symbol] = best_model
            self.scalers[symbol] = scaler
            
            joblib.dump(best_model, model_path)
            joblib.dump(scaler, scaler_path)
            
            # Tính accuracy
            y_pred = best_model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            
            logger.info(f"Model {symbol} trained - MAE: {mae:.4f}, MAPE: {mape:.2f}%")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi training model cho {symbol}: {e}")
            return False
    
    async def predict_price(self, symbol, hours_ahead=24):
        """Dự đoán giá cho symbol"""
        try:
            # Kiểm tra và load model
            if symbol not in self.models:
                success = await self.train_model(symbol)
                if not success:
                    return None
            
            # Lấy dữ liệu mới nhất
            df = await self.binance_client.get_historical_data(symbol, interval='1h', limit=100)
            
            if df is None or len(df) < 50:
                return None
            
            # Tính toán chỉ báo kỹ thuật
            df = self.calculate_technical_indicators(df)
            
            # Chuẩn bị features
            X, _ = self.prepare_features(df)
            
            if X is None:
                return None
            
            # Lấy dữ liệu mới nhất
            latest_features = X.iloc[-1:]
            
            # Chuẩn hóa
            latest_features_scaled = self.scalers[symbol].transform(latest_features)
            
            # Dự đoán
            predicted_price = self.models[symbol].predict(latest_features_scaled)[0]
            current_price = df['close'].iloc[-1]
            
            # Tính toán confidence và recommendation
            price_change_percent = ((predicted_price - current_price) / current_price) * 100
            
            # Confidence dựa trên volatility gần đây
            recent_volatility = df['close'].pct_change().tail(24).std() * 100
            confidence = max(50, min(95, 90 - recent_volatility * 10))
            
            # Recommendation
            if price_change_percent > 5:
                recommendation = "STRONG BUY 🚀"
            elif price_change_percent > 2:
                recommendation = "BUY 📈"
            elif price_change_percent > -2:
                recommendation = "HOLD ⏸️"
            elif price_change_percent > -5:
                recommendation = "SELL 📉"
            else:
                recommendation = "STRONG SELL ⚠️"
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'predicted_price': predicted_price,
                'price_change_percent': price_change_percent,
                'confidence': confidence,
                'recommendation': recommendation,
                'prediction_time': datetime.now(),
                'target_time': datetime.now() + timedelta(hours=hours_ahead)
            }
            
        except Exception as e:
            logger.error(f"Lỗi dự đoán giá cho {symbol}: {e}")
            return None
    
    async def get_market_sentiment(self, symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT']):
        """Phân tích sentiment thị trường"""
        try:
            predictions = []
            
            for symbol in symbols:
                prediction = await self.predict_price(symbol)
                if prediction:
                    predictions.append(prediction)
            
            if not predictions:
                return None
            
            # Tính sentiment tổng thể
            avg_change = np.mean([p['price_change_percent'] for p in predictions])
            
            if avg_change > 3:
                sentiment = "Rất tích cực 🚀"
            elif avg_change > 1:
                sentiment = "Tích cực 📈"
            elif avg_change > -1:
                sentiment = "Trung tính ⚖️"
            elif avg_change > -3:
                sentiment = "Tiêu cực 📉"
            else:
                sentiment = "Rất tiêu cực ⚠️"
            
            return {
                'sentiment': sentiment,
                'avg_change_percent': avg_change,
                'predictions': predictions,
                'analysis_time': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Lỗi phân tích market sentiment: {e}")
            return None
    
    async def get_technical_analysis(self, symbol):
        """Phân tích kỹ thuật chi tiết"""
        try:
            df = await self.binance_client.get_historical_data(symbol, interval='1h', limit=100)
            
            if df is None:
                return None
            
            df = self.calculate_technical_indicators(df)
            latest = df.iloc[-1]
            
            analysis = {
                'symbol': symbol,
                'current_price': latest['close'],
                'rsi': latest.get('rsi', 0),
                'macd': latest.get('macd', 0),
                'bb_position': 'N/A',
                'trend': 'N/A',
                'support': latest.get('support', 0),
                'resistance': latest.get('resistance', 0),
                'signals': []
            }
            
            # RSI signals
            if latest.get('rsi', 50) > 70:
                analysis['signals'].append("RSI quá mua - có thể giảm")
            elif latest.get('rsi', 50) < 30:
                analysis['signals'].append("RSI quá bán - có thể tăng")
            
            # Bollinger Bands position
            if 'bb_upper' in latest and 'bb_lower' in latest:
                if latest['close'] > latest['bb_upper']:
                    analysis['bb_position'] = "Trên dải trên - quá mua"
                elif latest['close'] < latest['bb_lower']:
                    analysis['bb_position'] = "Dưới dải dưới - quá bán"
                else:
                    analysis['bb_position'] = "Trong dải - bình thường"
            
            # Trend analysis
            if 'sma_7' in latest and 'sma_25' in latest:
                if latest['sma_7'] > latest['sma_25']:
                    analysis['trend'] = "Xu hướng tăng 📈"
                else:
                    analysis['trend'] = "Xu hướng giảm 📉"
            
            # MACD signals
            if latest.get('macd', 0) > 0:
                analysis['signals'].append("MACD tích cực")
            else:
                analysis['signals'].append("MACD tiêu cực")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Lỗi phân tích kỹ thuật cho {symbol}: {e}")
            return None