#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra Telegram Bot Token
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import InvalidToken, NetworkError

# Load environment variables
load_dotenv()

async def test_telegram_token():
    """Test Telegram Bot Token"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token or token == 'your_telegram_bot_token_here':
        print("❌ TELEGRAM_BOT_TOKEN chưa được cấu hình!")
        print("\n📋 Hướng dẫn lấy Telegram Bot Token:")
        print("1. Mở Telegram và tìm @BotFather")
        print("2. Gửi lệnh /newbot")
        print("3. Đặt tên cho bot (VD: My Crypto Bot)")
        print("4. Đặt username cho bot (phải kết thúc bằng 'bot', VD: mycryptobot)")
        print("5. Copy token và paste vào file .env")
        print("\n📝 Ví dụ trong file .env:")
        print("TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False
    
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print(f"✅ Token hợp lệ!")
        print(f"🤖 Bot name: {me.first_name}")
        print(f"📱 Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        return True
        
    except InvalidToken:
        print("❌ Token không hợp lệ!")
        print("💡 Kiểm tra lại token trong file .env")
        return False
        
    except NetworkError as e:
        print(f"❌ Lỗi kết nối mạng: {e}")
        print("💡 Kiểm tra kết nối internet")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Kiểm tra Telegram Bot Token...\n")
    
    try:
        result = asyncio.run(test_telegram_token())
        
        if result:
            print("\n🚀 Token OK! Bạn có thể chạy bot bằng: python start_bot.py")
        else:
            print("\n❌ Vui lòng cấu hình token trước khi chạy bot")
            
    except KeyboardInterrupt:
        print("\n👋 Đã hủy kiểm tra")
    except Exception as e:
        print(f"\n💥 Lỗi: {e}")