@echo off
chcp 65001 >nul
echo.
echo 🤖 ===============================================
echo    CRYPTO INVESTMENT BOT - TELEGRAM
echo ===============================================
echo.
echo 📋 Kiểm tra Python...
python --version
if errorlevel 1 (
    echo ❌ Python không được tìm thấy!
    echo 💡 Vui lòng cài đặt Python 3.8+ từ https://python.org
    pause
    exit /b 1
)

echo.
echo 📦 Kiểm tra pip...
pip --version
if errorlevel 1 (
    echo ❌ pip không được tìm thấy!
    pause
    exit /b 1
)

echo.
echo 🔍 Kiểm tra file .env...
if not exist ".env" (
    echo ❌ File .env không tồn tại!
    echo 💡 Đang tạo file .env từ template...
    copy ".env.example" ".env"
    echo ✅ Đã tạo file .env
    echo ⚠️  Vui lòng cấu hình API keys trong file .env trước khi chạy bot
    echo.
    echo 📝 Cần cấu hình:
    echo    - TELEGRAM_BOT_TOKEN (bắt buộc)
    echo    - BINANCE_API_KEY (tùy chọn)
    echo    - NEWS_API_KEY (tùy chọn)
    echo.
    pause
    exit /b 1
)

echo.
echo 📦 Cài đặt dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi cài đặt dependencies!
    pause
    exit /b 1
)

echo.
echo 🚀 Khởi động bot...
echo ⚠️  Nhấn Ctrl+C để dừng bot
echo.
python start_bot.py

echo.
echo 👋 Bot đã dừng
pause