#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script để test các chức năng của Crypto Investment Bot
Chạy script này để kiểm tra bot hoạt động mà không cần Telegram
"""

import asyncio
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

async def test_binance_client():
    """Test Binance client"""
    print("\n🔗 Testing Binance Client...")
    print("=" * 50)
    
    try:
        from binance_client import BinanceClient
        client = BinanceClient()
        
        # Test current price
        print("📊 Lấy giá hiện tại...")
        price = await client.get_current_price('BTCUSDT')
        if price:
            print(f"✅ BTC/USDT: ${price:,.2f}")
        
        # Test 24h ticker
        print("\n📈 Lấy thông tin 24h...")
        ticker = await client.get_24h_ticker('BTCUSDT')
        if ticker:
            print(f"✅ Giá: ${ticker['price']:,.2f}")
            print(f"✅ Thay đổi: {ticker['change_percent']:+.2f}%")
            print(f"✅ Volume: {ticker['volume']:,.0f}")
        
        # Test historical data
        print("\n📊 Lấy dữ liệu lịch sử...")
        df = await client.get_historical_data('BTCUSDT', limit=10)
        if df is not None:
            print(f"✅ Đã lấy {len(df)} data points")
            print(f"✅ Giá gần nhất: ${df['close'].iloc[-1]:,.2f}")
        
        # Test top gainers/losers
        print("\n🏆 Top gainers/losers...")
        top_data = await client.get_top_gainers_losers(limit=3)
        if top_data:
            print("📈 Top Gainers:")
            for coin in top_data['gainers'][:3]:
                print(f"   {coin['symbol']}: +{coin['change_percent']:.2f}%")
            
            print("📉 Top Losers:")
            for coin in top_data['losers'][:3]:
                print(f"   {coin['symbol']}: {coin['change_percent']:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi Binance Client: {e}")
        return False

async def test_crypto_predictor():
    """Test Crypto Predictor"""
    print("\n🔮 Testing Crypto Predictor...")
    print("=" * 50)
    
    try:
        from crypto_predictor import CryptoPredictor
        predictor = CryptoPredictor()
        
        # Test prediction
        print("📈 Dự đoán giá BTC...")
        prediction = await predictor.predict_price('BTCUSDT')
        
        if prediction:
            print(f"✅ Giá hiện tại: ${prediction['current_price']:,.2f}")
            print(f"✅ Giá dự đoán: ${prediction['predicted_price']:,.2f}")
            print(f"✅ Thay đổi: {prediction['price_change_percent']:+.2f}%")
            print(f"✅ Độ tin cậy: {prediction['confidence']:.1f}%")
            print(f"✅ Khuyến nghị: {prediction['recommendation']}")
        
        # Test technical analysis
        print("\n📊 Phân tích kỹ thuật...")
        analysis = await predictor.get_technical_analysis('BTCUSDT')
        
        if analysis:
            print(f"✅ RSI: {analysis['rsi']:.2f}")
            print(f"✅ MACD: {analysis['macd']:.6f}")
            print(f"✅ Trend: {analysis['trend']}")
            print(f"✅ BB Position: {analysis['bb_position']}")
            print(f"✅ Signals: {', '.join(analysis['signals'])}")
        
        # Test market sentiment
        print("\n💭 Sentiment thị trường...")
        sentiment = await predictor.get_market_sentiment()
        
        if sentiment:
            print(f"✅ Sentiment: {sentiment['sentiment']}")
            print(f"✅ Thay đổi TB: {sentiment['avg_change_percent']:+.2f}%")
            print(f"✅ Số coins phân tích: {len(sentiment['predictions'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi Crypto Predictor: {e}")
        return False

async def test_news_service():
    """Test News Service"""
    print("\n📰 Testing News Service...")
    print("=" * 50)
    
    try:
        from news_service import NewsService
        news_service = NewsService()
        
        # Test general crypto news
        print("📰 Lấy tin tức crypto...")
        news = await news_service.get_crypto_news(limit=3)
        
        if news:
            print(f"✅ Đã lấy {len(news)} bài báo")
            for i, article in enumerate(news[:2], 1):
                print(f"   {i}. {article['title'][:60]}...")
                print(f"      Nguồn: {article['source']} | Sentiment: {article['sentiment']}")
        
        # Test coin-specific news
        print("\n📰 Tin tức Bitcoin...")
        btc_news = await news_service.get_coin_news('BTC', limit=2)
        
        if btc_news:
            print(f"✅ Đã lấy {len(btc_news)} bài báo về Bitcoin")
            for i, article in enumerate(btc_news, 1):
                print(f"   {i}. {article['title'][:60]}...")
        
        # Test market news summary
        print("\n📊 Tóm tắt tin tức thị trường...")
        summary = await news_service.get_market_news_summary()
        
        if summary:
            print(f"✅ Sentiment tổng thể: {summary['overall_sentiment']}")
            print(f"✅ Tích cực: {summary['positive_count']} | Tiêu cực: {summary['negative_count']} | Trung tính: {summary['neutral_count']}")
            print(f"✅ Tổng bài báo: {summary['total_articles']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi News Service: {e}")
        return False

async def test_utils():
    """Test utility functions"""
    print("\n🛠️ Testing Utilities...")
    print("=" * 50)
    
    try:
        from utils import (
            format_price, format_percentage, format_volume,
            format_market_cap, calculate_rsi, get_trend_direction
        )
        
        # Test formatting functions
        print("💰 Format functions:")
        print(f"   Price: {format_price(45678.123)}")
        print(f"   Percentage: {format_percentage(5.67)}")
        print(f"   Volume: {format_volume(1234567890)}")
        print(f"   Market Cap: {format_market_cap(987654321000)}")
        
        # Test technical calculations
        print("\n📊 Technical calculations:")
        sample_prices = [100, 102, 98, 105, 103, 107, 104, 109, 106, 111, 108, 115, 112, 118, 115]
        rsi = calculate_rsi(sample_prices)
        trend = get_trend_direction(sample_prices)
        
        print(f"   RSI: {rsi:.2f}")
        print(f"   Trend: {trend}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi Utils: {e}")
        return False

async def run_comprehensive_demo():
    """Chạy demo tổng hợp"""
    print("\n🚀 Comprehensive Demo...")
    print("=" * 50)
    
    try:
        # Import all modules
        from binance_client import BinanceClient
        from crypto_predictor import CryptoPredictor
        from news_service import NewsService
        from utils import format_price, format_percentage
        
        # Initialize services
        binance = BinanceClient()
        predictor = CryptoPredictor()
        news = NewsService()
        
        # Comprehensive analysis for BTC
        print("📊 Phân tích tổng hợp BTC/USDT:")
        print("-" * 30)
        
        # Current price
        price = await binance.get_current_price('BTCUSDT')
        ticker = await binance.get_24h_ticker('BTCUSDT')
        
        if price and ticker:
            print(f"💰 Giá hiện tại: ${format_price(price)}")
            print(f"📈 24h thay đổi: {format_percentage(ticker['change_percent'])}")
            print(f"📊 Volume 24h: {ticker['volume']:,.0f} BTC")
        
        # Prediction
        prediction = await predictor.predict_price('BTCUSDT')
        if prediction:
            print(f"🔮 Dự đoán 24h: ${format_price(prediction['predicted_price'])}")
            print(f"🎯 Khuyến nghị: {prediction['recommendation']}")
            print(f"📊 Độ tin cậy: {prediction['confidence']:.1f}%")
        
        # Technical analysis
        analysis = await predictor.get_technical_analysis('BTCUSDT')
        if analysis:
            print(f"📈 RSI: {analysis['rsi']:.1f}")
            print(f"📊 Trend: {analysis['trend']}")
        
        # News
        btc_news = await news.get_coin_news('BTC', limit=1)
        if btc_news:
            print(f"📰 Tin mới nhất: {btc_news[0]['title'][:50]}...")
        
        # Market sentiment
        sentiment = await predictor.get_market_sentiment()
        if sentiment:
            print(f"💭 Sentiment thị trường: {sentiment['sentiment']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi comprehensive demo: {e}")
        return False

async def main():
    """Main demo function"""
    print("""
🤖 ===============================================
   CRYPTO INVESTMENT BOT - DEMO
===============================================

🧪 Đang test các chức năng chính của bot...
    """)
    
    results = []
    
    # Run all tests
    tests = [
        ("Binance Client", test_binance_client),
        ("Crypto Predictor", test_crypto_predictor),
        ("News Service", test_news_service),
        ("Utilities", test_utils),
        ("Comprehensive Demo", run_comprehensive_demo)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Testing {test_name}...")
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DEMO SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20}: {status}")
    
    print(f"\n🎯 Kết quả: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Tất cả tests đều PASSED! Bot sẵn sàng hoạt động.")
        print("\n🚀 Để chạy bot Telegram:")
        print("   python start_bot.py")
        print("   hoặc")
        print("   run_bot.bat")
    else:
        print("\n⚠️ Một số tests FAILED. Kiểm tra cấu hình và dependencies.")
        print("\n💡 Gợi ý:")
        print("   - Kiểm tra file .env")
        print("   - Kiểm tra kết nối internet")
        print("   - Chạy: pip install -r requirements.txt")
    
    print("\n👋 Demo hoàn thành!")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo bị dừng bởi người dùng")
    except Exception as e:
        print(f"\n💥 Lỗi nghiêm trọng: {e}")