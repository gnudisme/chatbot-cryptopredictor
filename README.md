# 🤖 Crypto Investment Bot - Telegram

Bot Telegram thông minh dự đoán giá cryptocurrency, cung cấp phân tích kỹ thuật và tin tức thị trường crypto.

## ✨ Tính năng chính

### 📈 Dự đoán giá
- Dự đoán giá cryptocurrency trong 24h tới
- Sử dụng Machine Learning với Random Forest, Gradient Boosting
- Phân tích các chỉ báo kỹ thuật: RSI, MACD, Bollinger Bands, SMA, EMA
- Đánh giá độ tin cậy và đưa ra khuyến nghị đầu tư

### 💰 Thông tin thị trường Real-time
- Giá hiện tại từ Binance API
- Thông tin 24h: thay đổi giá, volume, high/low
- Top gainers/losers
- Market cap và supply info

### 📊 Phân tích kỹ thuật
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
- Support/Resistance levels
- Volatility analysis

### 📰 Tin tức Crypto
- Tin tức tổng quát về thị trường crypto
- Tin tức cụ thể cho từng coin
- Phân tích sentiment từ tin tức
- Trending topics

### 💡 Gợi ý đầu tư
- Phân tích sentiment thị trường
- Tín hiệu mua/bán dựa trên technical analysis
- Risk assessment
- Portfolio suggestions

## 🚀 Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.8+
- pip

### 2. Clone repository
```bash
git clone <repository-url>
cd crypto-investment-bot
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

#### Tạo file .env từ template:
```bash
cp .env.example .env
```

#### Cấu hình các API keys trong file .env:

**Telegram Bot Token:**
1. Tạo bot mới với @BotFather trên Telegram
2. Copy token vào `TELEGRAM_BOT_TOKEN`

**Binance API (Tùy chọn):**
1. Đăng ký tài khoản Binance
2. Tạo API key tại Binance API Management
3. Copy API key và Secret key vào file .env

**News API (Tùy chọn):**
1. Đăng ký tại https://newsapi.org/
2. Copy API key vào `NEWS_API_KEY`

### 5. Chạy bot
```bash
python main.py
```

## 📱 Cách sử dụng

### Khởi động bot
- Gửi `/start` để bắt đầu
- Chọn chức năng từ menu inline keyboard

### Các lệnh chính
- **📈 Dự đoán giá**: Chọn coin để dự đoán giá 24h
- **💰 Giá hiện tại**: Xem giá real-time
- **📊 Phân tích kỹ thuật**: Phân tích technical indicators
- **📰 Tin tức crypto**: Đọc tin tức mới nhất
- **💡 Gợi ý đầu tư**: Nhận khuyến nghị đầu tư
- **ℹ️ Thông tin coin**: Xem thông tin chi tiết coin

### Nhập trực tiếp tên coin
Bạn có thể nhập trực tiếp tên coin (VD: BTC, ETH, BNB) để nhận phân tích nhanh.

## 🔧 Cấu hình nâng cao

### Supported Coins
Bot hỗ trợ tất cả các cặp trading trên Binance, đặc biệt tối ưu cho:
- BTC/USDT
- ETH/USDT
- BNB/USDT
- ADA/USDT
- SOL/USDT
- DOGE/USDT
- XRP/USDT
- DOT/USDT
- AVAX/USDT
- MATIC/USDT

### Model Training
Bot tự động train model cho mỗi coin khi lần đầu dự đoán. Model được lưu trong thư mục `models/` và có thể retrain khi cần.

### Caching
Dữ liệu được cache trong 5 phút để tối ưu performance và giảm API calls.

## 📊 Technical Indicators

### Trend Indicators
- **SMA (Simple Moving Average)**: 7, 25 periods
- **EMA (Exponential Moving Average)**: 12, 26 periods
- **MACD**: 12, 26, 9 periods

### Momentum Indicators
- **RSI**: 14 periods
- **Stochastic**: %K, %D
- **Williams %R**: 14 periods

### Volatility Indicators
- **Bollinger Bands**: 20 periods, 2 std dev
- **Volatility**: 20 periods rolling standard deviation

### Volume Indicators
- **Volume SMA**: 20 periods
- **VWAP**: Volume Weighted Average Price

## 🔒 Bảo mật

- Không bao giờ commit file .env vào git
- API keys được mã hóa trong môi trường production
- Bot chỉ sử dụng quyền đọc dữ liệu, không thực hiện giao dịch
- Logs không chứa thông tin nhạy cảm

## 🐛 Troubleshooting

### Bot không phản hồi
- Kiểm tra Telegram Bot Token
- Kiểm tra kết nối internet
- Xem logs để debug

### Lỗi API
- Kiểm tra API keys trong file .env
- Kiểm tra rate limits của các API
- Binance API có thể hoạt động mà không cần API key (chế độ public)

### Lỗi dự đoán
- Kiểm tra dữ liệu lịch sử có đủ không (tối thiểu 100 data points)
- Retrain model nếu cần: xóa file trong thư mục `models/`

## 📈 Performance

### Model Accuracy
- MAPE (Mean Absolute Percentage Error): ~5-15% tùy coin
- Confidence score: 50-95% tùy volatility
- Update model hàng ngày để duy trì accuracy

### API Limits
- Binance: 1200 requests/minute
- NewsAPI: 1000 requests/day (free tier)
- CoinGecko: 50 calls/minute

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## ⚠️ Disclaimer

**QUAN TRỌNG**: Bot này chỉ mang tính chất tham khảo và giáo dục. Không phải lời khuyên đầu tư tài chính. Luôn thực hiện nghiên cứu riêng và cân nhắc rủi ro trước khi đầu tư. Cryptocurrency là thị trường có độ rủi ro cao.

## 📞 Hỗ trợ

Nếu gặp vấn đề hoặc có câu hỏi, vui lòng tạo issue trên GitHub repository.

---

**Happy Trading! 🚀📈**