import os
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        # Khởi tạo client (có thể hoạt động mà không cần API key cho dữ liệu công khai)
        try:
            if self.api_key and self.secret_key:
                self.client = Client(self.api_key, self.secret_key)
            else:
                self.client = Client()  # Client công khai
                logger.warning("Sử dụng Binance client công khai - một số tính năng có thể bị hạn chế")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo Binance client: {e}")
            self.client = None
    
    async def get_current_price(self, symbol):
        """Lấy giá hiện tại của một symbol"""
        try:
            if self.client:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                return float(ticker['price'])
            else:
                # Sử dụng API công khai
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                    async with session.get(url) as response:
                        data = await response.json()
                        return float(data['price'])
        except Exception as e:
            logger.error(f"Lỗi lấy giá hiện tại cho {symbol}: {e}")
            return None
    
    async def get_24h_ticker(self, symbol):
        """Lấy thông tin ticker 24h"""
        try:
            if self.client:
                ticker = self.client.get_ticker(symbol=symbol)
                return {
                    'symbol': ticker['symbol'],
                    'price': float(ticker['lastPrice']),
                    'change': float(ticker['priceChange']),
                    'change_percent': float(ticker['priceChangePercent']),
                    'high': float(ticker['highPrice']),
                    'low': float(ticker['lowPrice']),
                    'volume': float(ticker['volume']),
                    'quote_volume': float(ticker['quoteVolume'])
                }
            else:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                    async with session.get(url) as response:
                        data = await response.json()
                        return {
                            'symbol': data['symbol'],
                            'price': float(data['lastPrice']),
                            'change': float(data['priceChange']),
                            'change_percent': float(data['priceChangePercent']),
                            'high': float(data['highPrice']),
                            'low': float(data['lowPrice']),
                            'volume': float(data['volume']),
                            'quote_volume': float(data['quoteVolume'])
                        }
        except Exception as e:
            logger.error(f"Lỗi lấy ticker 24h cho {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol, interval='1h', limit=100):
        """Lấy dữ liệu lịch sử"""
        try:
            if self.client:
                klines = self.client.get_historical_klines(symbol, interval, f"{limit} hours ago UTC")
            else:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
                    async with session.get(url) as response:
                        klines = await response.json()
            
            # Chuyển đổi thành DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Chuyển đổi kiểu dữ liệu
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df[numeric_columns]
            
        except Exception as e:
            logger.error(f"Lỗi lấy dữ liệu lịch sử cho {symbol}: {e}")
            return None
    
    async def get_top_gainers_losers(self, limit=10):
        """Lấy danh sách top tăng/giảm"""
        try:
            if self.client:
                tickers = self.client.get_ticker()
            else:
                async with aiohttp.ClientSession() as session:
                    url = "https://api.binance.com/api/v3/ticker/24hr"
                    async with session.get(url) as response:
                        tickers = await response.json()
            
            # Lọc các cặp USDT
            usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT') and float(t['quoteVolume']) > 1000000]
            
            # Sắp xếp theo % thay đổi
            gainers = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)[:limit]
            losers = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']))[:limit]
            
            return {
                'gainers': [{
                    'symbol': t['symbol'],
                    'price': float(t['lastPrice']),
                    'change_percent': float(t['priceChangePercent'])
                } for t in gainers],
                'losers': [{
                    'symbol': t['symbol'],
                    'price': float(t['lastPrice']),
                    'change_percent': float(t['priceChangePercent'])
                } for t in losers]
            }
            
        except Exception as e:
            logger.error(f"Lỗi lấy top gainers/losers: {e}")
            return None
    
    async def get_market_cap_info(self, symbol):
        """Lấy thông tin market cap (sử dụng API bên thứ 3)"""
        try:
            coin_id = symbol.replace('USDT', '').lower()
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'market_cap': data['market_data']['market_cap']['usd'],
                            'total_supply': data['market_data']['total_supply'],
                            'circulating_supply': data['market_data']['circulating_supply'],
                            'max_supply': data['market_data']['max_supply']
                        }
        except Exception as e:
            logger.error(f"Lỗi lấy thông tin market cap cho {symbol}: {e}")
            return None
    
    async def get_order_book(self, symbol, limit=10):
        """Lấy order book"""
        try:
            if self.client:
                order_book = self.client.get_order_book(symbol=symbol, limit=limit)
            else:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}"
                    async with session.get(url) as response:
                        order_book = await response.json()
            
            return {
                'bids': [[float(price), float(qty)] for price, qty in order_book['bids']],
                'asks': [[float(price), float(qty)] for price, qty in order_book['asks']]
            }
            
        except Exception as e:
            logger.error(f"Lỗi lấy order book cho {symbol}: {e}")
            return None
    
    async def search_symbols(self, query):
        """Tìm kiếm symbols"""
        try:
            if self.client:
                exchange_info = self.client.get_exchange_info()
                symbols = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']
            else:
                async with aiohttp.ClientSession() as session:
                    url = "https://api.binance.com/api/v3/exchangeInfo"
                    async with session.get(url) as response:
                        data = await response.json()
                        symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
            
            # Tìm kiếm symbols phù hợp
            query = query.upper()
            matching_symbols = [s for s in symbols if query in s and s.endswith('USDT')]
            
            return matching_symbols[:20]  # Giới hạn 20 kết quả
            
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm symbols: {e}")
            return []
    
    async def get_top_gainers(self, limit=10):
        """Lấy top gainers"""
        try:
            data = await self.get_top_gainers_losers(limit * 2)  # Lấy nhiều hơn để filter
            if data and 'gainers' in data:
                return data['gainers'][:limit]
            return []
        except Exception as e:
            logger.error(f"Lỗi lấy top gainers: {e}")
            return []
    
    async def get_top_losers(self, limit=10):
        """Lấy top losers"""
        try:
            data = await self.get_top_gainers_losers(limit * 2)  # Lấy nhiều hơn để filter
            if data and 'losers' in data:
                return data['losers'][:limit]
            return []
        except Exception as e:
            logger.error(f"Lỗi lấy top losers: {e}")
            return []
    
    def is_connected(self):
        """Kiểm tra kết nối"""
        try:
            if self.client:
                self.client.get_server_time()
                return True
            return False
        except:
            return False