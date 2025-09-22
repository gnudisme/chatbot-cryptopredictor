#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Bot - Test các chức năng mà không cần Telegram Token
"""

import asyncio
import logging
from crypto_predictor import CryptoPredictor
from binance_client import BinanceClient
from news_service import NewsService
from utils import format_price, format_percentage

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DemoCryptoBot:
    """Demo bot để test chức năng"""
    
    def __init__(self):
        self.predictor = CryptoPredictor()
        self.binance = BinanceClient()
        self.news = NewsService()
        
    async def demo_price_analysis(self, symbol='BTCUSDT'):
        """Demo phân tích giá"""
        print(f"\n🔍 Phân tích {symbol}...")
        
        try:
            # Lấy giá hiện tại
            price_data = await self.binance.get_24h_ticker(symbol)
            if price_data:
                print(f"💰 Giá hiện tại: {format_price(price_data['price'])}")
                print(f"📈 Thay đổi 24h: {format_percentage(price_data['change_percent'])}")
            
            # Dự đoán giá
            prediction = await self.predictor.predict_price(symbol)
            if prediction:
                print(f"🎯 Dự đoán giá: {format_price(prediction['predicted_price'])}")
                print(f"📊 Độ tin cậy: {prediction['confidence']:.1%}")
                print(f"💡 Khuyến nghị: {prediction['recommendation']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    async def demo_technical_analysis(self, symbol='ETHUSDT'):
        """Demo phân tích kỹ thuật"""
        print(f"\n📊 Phân tích kỹ thuật {symbol}...")
        
        try:
            analysis = await self.predictor.get_technical_analysis(symbol)
            if analysis:
                print(f"📈 RSI: {analysis.get('rsi', 'N/A')}")
                print(f"📉 MACD: {analysis.get('macd_signal', 'N/A')}")
                print(f"🎯 Tín hiệu: {analysis.get('signal', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    async def demo_market_overview(self):
        """Demo tổng quan thị trường"""
        print("\n🌍 Tổng quan thị trường...")
        
        try:
            # Top gainers
            gainers = await self.binance.get_top_gainers(limit=3)
            if gainers:
                print("\n🚀 Top Gainers:")
                for coin in gainers:
                    print(f"  • {coin['symbol']}: {format_percentage(coin['change_percent'])}")
            
            # Top losers
            losers = await self.binance.get_top_losers(limit=3)
            if losers:
                print("\n📉 Top Losers:")
                for coin in losers:
                    print(f"  • {coin['symbol']}: {format_percentage(coin['change_percent'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    async def demo_news(self):
        """Demo tin tức"""
        print("\n📰 Tin tức crypto...")
        
        try:
            news = await self.news.get_general_crypto_news(limit=3)
            if news:
                for i, article in enumerate(news, 1):
                    print(f"\n{i}. {article['title'][:60]}...")
                    print(f"   📅 {article.get('publishedAt', 'N/A')}")
                    if 'sentiment' in article:
                        print(f"   😊 Sentiment: {article['sentiment']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    async def run_demo(self):
        """Chạy demo đầy đủ"""
        print("🤖 " + "="*50)
        print("   CRYPTO BOT DEMO - TEST CHỨC NĂNG")
        print("="*52)
        
        # Test các chức năng
        tests = [
            ("Phân tích giá BTC", self.demo_price_analysis, 'BTCUSDT'),
            ("Phân tích kỹ thuật ETH", self.demo_technical_analysis, 'ETHUSDT'),
            ("Tổng quan thị trường", self.demo_market_overview,),
            ("Tin tức crypto", self.demo_news,)
        ]
        
        results = []
        
        for test_name, test_func, *args in tests:
            print(f"\n🧪 Test: {test_name}")
            try:
                if args:
                    result = await test_func(*args)
                else:
                    result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Lỗi trong {test_name}: {e}")
                results.append((test_name, False))
        
        # Tổng kết
        print("\n" + "="*52)
        print("📋 KẾT QUẢ TEST:")
        print("="*52)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n📊 Tổng kết: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 Tất cả chức năng hoạt động tốt!")
            print("💡 Bạn có thể cấu hình Telegram token và chạy bot thực")
        else:
            print("\n⚠️ Một số chức năng có vấn đề")
            print("💡 Kiểm tra kết nối mạng và API keys")
        
        print("\n🔧 Để chạy bot Telegram:")
        print("1. Cấu hình TELEGRAM_BOT_TOKEN trong file .env")
        print("2. Chạy: python test_token.py (để kiểm tra token)")
        print("3. Chạy: python start_bot.py (để khởi động bot)")

async def main():
    """Main function"""
    bot = DemoCryptoBot()
    await bot.run_demo()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo đã được dừng")
    except Exception as e:
        print(f"\n💥 Lỗi: {e}")