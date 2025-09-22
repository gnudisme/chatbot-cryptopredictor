#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script khởi động Crypto Investment Bot
Kiểm tra cấu hình và khởi động bot
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Kiểm tra cấu hình môi trường"""
    logger.info("🔍 Kiểm tra cấu hình môi trường...")
    
    # Load environment variables
    env_file = Path('.env')
    if not env_file.exists():
        logger.error("❌ File .env không tồn tại!")
        logger.info("💡 Hãy copy .env.example thành .env và cấu hình các API keys")
        return False
    
    load_dotenv()
    
    # Check required variables
    required_vars = ['TELEGRAM_BOT_TOKEN']
    optional_vars = ['BINANCE_API_KEY', 'BINANCE_SECRET_KEY', 'NEWS_API_KEY']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            logger.info(f"✅ {var}: Đã cấu hình")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            logger.info(f"✅ {var}: Đã cấu hình")
    
    if missing_required:
        logger.error(f"❌ Thiếu các biến môi trường bắt buộc: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        logger.warning(f"⚠️ Thiếu các biến môi trường tùy chọn: {', '.join(missing_optional)}")
        logger.info("💡 Bot vẫn có thể hoạt động với chức năng hạn chế")
    
    return True

def check_dependencies():
    """Kiểm tra dependencies"""
    logger.info("📦 Kiểm tra dependencies...")
    
    # Map package names to import names
    package_map = {
        'telegram': 'telegram',
        'binance': 'binance',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scikit-learn': 'sklearn',
        'requests': 'requests',
        'matplotlib': 'matplotlib',
        'python-dotenv': 'dotenv',
        'ta': 'ta',
        'aiohttp': 'aiohttp'
    }
    
    missing_packages = []
    
    for package, import_name in package_map.items():
        try:
            __import__(import_name)
            logger.info(f"✅ {package}: Đã cài đặt")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package}: Chưa cài đặt")
    
    if missing_packages:
        logger.error(f"❌ Thiếu các package: {', '.join(missing_packages)}")
        logger.info("💡 Chạy: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Tạo các thư mục cần thiết"""
    logger.info("📁 Tạo thư mục cần thiết...")
    
    directories = ['models', 'logs', 'data', 'cache']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✅ Thư mục {directory}: OK")

async def test_connections():
    """Test kết nối các API"""
    logger.info("🌐 Kiểm tra kết nối API...")
    
    # Test Binance connection
    try:
        from binance_client import BinanceClient
        binance_client = BinanceClient()
        
        # Test public API
        price = await binance_client.get_current_price('BTCUSDT')
        if price:
            logger.info(f"✅ Binance API: OK (BTC price: ${price:,.2f})")
        else:
            logger.warning("⚠️ Binance API: Có vấn đề")
    except Exception as e:
        logger.error(f"❌ Binance API: {e}")
    
    # Test News API
    try:
        from news_service import NewsService
        news_service = NewsService()
        news = await news_service.get_crypto_news(limit=1)
        
        if news:
            logger.info(f"✅ News Service: OK ({len(news)} articles)")
        else:
            logger.warning("⚠️ News Service: Không có dữ liệu")
    except Exception as e:
        logger.error(f"❌ News Service: {e}")

def print_startup_info():
    """In thông tin khởi động"""
    print("""
🤖 ===============================================
   CRYPTO INVESTMENT BOT - TELEGRAM
===============================================

📈 Tính năng:
   • Dự đoán giá cryptocurrency
   • Phân tích kỹ thuật real-time
   • Tin tức và sentiment analysis
   • Gợi ý đầu tư thông minh

🚀 Bot đang khởi động...
    """)

def print_success_info():
    """In thông tin thành công"""
    print("""
✅ ===============================================
   BOT ĐÃ KHỞI ĐỘNG THÀNH CÔNG!
===============================================

📱 Cách sử dụng:
   1. Mở Telegram
   2. Tìm bot của bạn
   3. Gửi /start để bắt đầu
   4. Chọn chức năng từ menu

💡 Lệnh hữu ích:
   • Nhập tên coin (VD: BTC, ETH) để phân tích nhanh
   • Sử dụng menu để truy cập đầy đủ tính năng

⚠️  Lưu ý: Đây chỉ là công cụ hỗ trợ, không phải lời khuyên đầu tư!

🔄 Để dừng bot: Nhấn Ctrl+C
    """)

async def main():
    """Hàm chính"""
    try:
        print_startup_info()
        
        # Kiểm tra môi trường
        if not check_environment():
            logger.error("❌ Cấu hình môi trường không hợp lệ")
            return False
        
        # Kiểm tra dependencies
        if not check_dependencies():
            logger.error("❌ Dependencies không đầy đủ")
            return False
        
        # Tạo thư mục
        create_directories()
        
        # Test connections
        await test_connections()
        
        logger.info("✅ Tất cả kiểm tra đã hoàn thành")
        
        # Import và khởi động bot
        logger.info("🚀 Khởi động Telegram Bot...")
        
        from main import CryptoBotTelegram
        
        bot = CryptoBotTelegram()
        
        print_success_info()
        
        return bot
        
    except KeyboardInterrupt:
        logger.info("\n👋 Bot đã được dừng bởi người dùng")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động bot: {e}")
        return False

async def run_bot():
    """Chạy bot với async context"""
    try:
        # Kiểm tra môi trường
        if not check_environment():
            return False
            
        if not check_dependencies():
            return False
            
        create_directories()
        
        # Test connections
        await test_connections()
        
        print_startup_info()
        
        # Import và chạy bot
        from main import CryptoBotTelegram
        bot = CryptoBotTelegram()
        await bot.run_async()
        
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động bot: {e}")
        return False

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"\n💥 Lỗi nghiêm trọng: {e}")
        sys.exit(1)