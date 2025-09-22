import re
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def format_price(price: float, decimals: int = None) -> str:
    """Format giá tiền với số thập phân phù hợp"""
    try:
        if price is None:
            return "N/A"
        
        if decimals is None:
            # Tự động xác định số thập phân
            if price >= 1000:
                decimals = 2
            elif price >= 1:
                decimals = 4
            elif price >= 0.01:
                decimals = 6
            else:
                decimals = 8
        
        formatted = f"{price:,.{decimals}f}"
        
        # Loại bỏ số 0 thừa ở cuối
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        
        return formatted
        
    except Exception as e:
        logger.error(f"Lỗi format price: {e}")
        return str(price)

def format_percentage(percentage: float, decimals: int = 2) -> str:
    """Format phần trăm với màu sắc emoji"""
    try:
        if percentage is None:
            return "N/A"
        
        formatted = f"{percentage:+.{decimals}f}%"
        
        # Thêm emoji
        if percentage > 0:
            return f"🟢 {formatted}"
        elif percentage < 0:
            return f"🔴 {formatted}"
        else:
            return f"⚪ {formatted}"
            
    except Exception as e:
        logger.error(f"Lỗi format percentage: {e}")
        return str(percentage)

def format_volume(volume: float) -> str:
    """Format volume với đơn vị phù hợp"""
    try:
        if volume is None:
            return "N/A"
        
        if volume >= 1_000_000_000:
            return f"{volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.2f}K"
        else:
            return f"{volume:.2f}"
            
    except Exception as e:
        logger.error(f"Lỗi format volume: {e}")
        return str(volume)

def format_market_cap(market_cap: float) -> str:
    """Format market cap"""
    try:
        if market_cap is None:
            return "N/A"
        
        if market_cap >= 1_000_000_000_000:
            return f"${market_cap/1_000_000_000_000:.2f}T"
        elif market_cap >= 1_000_000_000:
            return f"${market_cap/1_000_000_000:.2f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap/1_000_000:.2f}M"
        else:
            return f"${market_cap:,.0f}"
            
    except Exception as e:
        logger.error(f"Lỗi format market cap: {e}")
        return str(market_cap)

def format_time_ago(timestamp: str) -> str:
    """Format thời gian thành 'x phút/giờ/ngày trước'"""
    try:
        if not timestamp:
            return "N/A"
        
        # Parse timestamp
        if isinstance(timestamp, str):
            # Xử lý các format timestamp khác nhau
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        else:
            dt = timestamp
        
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} ngày trước"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} giờ trước"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} phút trước"
        else:
            return "Vừa xong"
            
    except Exception as e:
        logger.error(f"Lỗi format time ago: {e}")
        return "N/A"

def validate_symbol(symbol: str) -> str:
    """Validate và chuẩn hóa symbol"""
    try:
        if not symbol:
            return None
        
        symbol = symbol.upper().strip()
        
        # Loại bỏ ký tự đặc biệt
        symbol = re.sub(r'[^A-Z0-9]', '', symbol)
        
        # Thêm USDT nếu chưa có
        if not symbol.endswith('USDT') and len(symbol) <= 10:
            symbol += 'USDT'
        
        return symbol
        
    except Exception as e:
        logger.error(f"Lỗi validate symbol: {e}")
        return None

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Tính RSI"""
    try:
        if len(prices) < period + 1:
            return 50  # Giá trị mặc định
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    except Exception as e:
        logger.error(f"Lỗi tính RSI: {e}")
        return 50

def calculate_sma(prices: List[float], period: int) -> float:
    """Tính Simple Moving Average"""
    try:
        if len(prices) < period:
            return np.mean(prices) if prices else 0
        
        return np.mean(prices[-period:])
        
    except Exception as e:
        logger.error(f"Lỗi tính SMA: {e}")
        return 0

def calculate_ema(prices: List[float], period: int) -> float:
    """Tính Exponential Moving Average"""
    try:
        if len(prices) < period:
            return np.mean(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
        
    except Exception as e:
        logger.error(f"Lỗi tính EMA: {e}")
        return 0

def get_support_resistance(prices: List[float], window: int = 20) -> Dict[str, float]:
    """Tính support và resistance levels"""
    try:
        if len(prices) < window:
            return {'support': min(prices), 'resistance': max(prices)}
        
        recent_prices = prices[-window:]
        support = min(recent_prices)
        resistance = max(recent_prices)
        
        return {'support': support, 'resistance': resistance}
        
    except Exception as e:
        logger.error(f"Lỗi tính support/resistance: {e}")
        return {'support': 0, 'resistance': 0}

def calculate_volatility(prices: List[float], period: int = 20) -> float:
    """Tính volatility (độ biến động)"""
    try:
        if len(prices) < period:
            return 0
        
        recent_prices = prices[-period:]
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns) * 100  # Chuyển thành %
        
        return volatility
        
    except Exception as e:
        logger.error(f"Lỗi tính volatility: {e}")
        return 0

def get_trend_direction(prices: List[float], short_period: int = 7, long_period: int = 25) -> str:
    """Xác định hướng trend"""
    try:
        if len(prices) < long_period:
            return "Không đủ dữ liệu"
        
        short_sma = calculate_sma(prices, short_period)
        long_sma = calculate_sma(prices, long_period)
        
        if short_sma > long_sma:
            return "Tăng 📈"
        elif short_sma < long_sma:
            return "Giảm 📉"
        else:
            return "Sideway ➡️"
            
    except Exception as e:
        logger.error(f"Lỗi xác định trend: {e}")
        return "N/A"

def generate_trading_signal(rsi: float, macd: float, price: float, sma: float) -> Dict[str, Any]:
    """Tạo tín hiệu trading"""
    try:
        signals = []
        overall_signal = "HOLD"
        confidence = 50
        
        # RSI signals
        if rsi > 70:
            signals.append("RSI quá mua")
            confidence -= 10
        elif rsi < 30:
            signals.append("RSI quá bán")
            confidence += 10
        
        # MACD signals
        if macd > 0:
            signals.append("MACD tích cực")
            confidence += 5
        else:
            signals.append("MACD tiêu cực")
            confidence -= 5
        
        # Price vs SMA
        if price > sma:
            signals.append("Giá trên SMA")
            confidence += 5
        else:
            signals.append("Giá dưới SMA")
            confidence -= 5
        
        # Tổng hợp signal
        if confidence > 70:
            overall_signal = "BUY"
        elif confidence < 30:
            overall_signal = "SELL"
        
        return {
            'signal': overall_signal,
            'confidence': max(0, min(100, confidence)),
            'signals': signals
        }
        
    except Exception as e:
        logger.error(f"Lỗi tạo trading signal: {e}")
        return {'signal': 'HOLD', 'confidence': 50, 'signals': []}

def clean_text(text: str) -> str:
    """Làm sạch text cho Telegram"""
    try:
        if not text:
            return ""
        
        # Loại bỏ HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Loại bỏ ký tự đặc biệt của Markdown
        text = text.replace('*', '\\*')
        text = text.replace('_', '\\_')
        text = text.replace('[', '\\[')
        text = text.replace(']', '\\]')
        text = text.replace('(', '\\(')
        text = text.replace(')', '\\)')
        text = text.replace('`', '\\`')
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Lỗi clean text: {e}")
        return str(text)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Cắt ngắn text"""
    try:
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
        
    except Exception as e:
        logger.error(f"Lỗi truncate text: {e}")
        return str(text)

def save_user_preferences(user_id: int, preferences: Dict[str, Any]) -> bool:
    """Lưu preferences của user"""
    try:
        filename = f"user_preferences_{user_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, ensure_ascii=False, indent=2)
        return True
        
    except Exception as e:
        logger.error(f"Lỗi lưu user preferences: {e}")
        return False

def load_user_preferences(user_id: int) -> Dict[str, Any]:
    """Load preferences của user"""
    try:
        filename = f"user_preferences_{user_id}.json"
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except FileNotFoundError:
        # Trả về preferences mặc định
        return {
            'favorite_coins': ['BTCUSDT', 'ETHUSDT'],
            'notifications': True,
            'language': 'vi',
            'timezone': 'Asia/Ho_Chi_Minh'
        }
    except Exception as e:
        logger.error(f"Lỗi load user preferences: {e}")
        return {}

def format_coin_info(coin_data: Dict[str, Any]) -> str:
    """Format thông tin coin thành text đẹp"""
    try:
        text = f"📊 *{coin_data.get('symbol', 'N/A')}*\n\n"
        
        if 'price' in coin_data:
            text += f"💰 Giá: ${format_price(coin_data['price'])}\n"
        
        if 'change_percent' in coin_data:
            text += f"📈 24h: {format_percentage(coin_data['change_percent'])}\n"
        
        if 'volume' in coin_data:
            text += f"📊 Volume: {format_volume(coin_data['volume'])}\n"
        
        if 'market_cap' in coin_data:
            text += f"🏦 Market Cap: {format_market_cap(coin_data['market_cap'])}\n"
        
        if 'high' in coin_data and 'low' in coin_data:
            text += f"📊 24h High/Low: ${format_price(coin_data['high'])} / ${format_price(coin_data['low'])}\n"
        
        return text
        
    except Exception as e:
        logger.error(f"Lỗi format coin info: {e}")
        return "Lỗi hiển thị thông tin"

def get_emoji_for_change(change_percent: float) -> str:
    """Lấy emoji phù hợp cho % thay đổi"""
    try:
        if change_percent > 10:
            return "🚀"
        elif change_percent > 5:
            return "📈"
        elif change_percent > 0:
            return "🟢"
        elif change_percent == 0:
            return "⚪"
        elif change_percent > -5:
            return "🔴"
        elif change_percent > -10:
            return "📉"
        else:
            return "💥"
            
    except Exception as e:
        logger.error(f"Lỗi get emoji: {e}")
        return "⚪"