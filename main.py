import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import asyncio

from crypto_predictor import CryptoPredictor
from binance_client import BinanceClient
from news_service import NewsService
from utils import format_price, format_percentage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CryptoBotTelegram:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.predictor = CryptoPredictor()
        self.binance_client = BinanceClient()
        self.news_service = NewsService()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Khởi động bot và hiển thị menu chính"""
        keyboard = [
            [InlineKeyboardButton("📈 Dự đoán giá", callback_data='predict')],
            [InlineKeyboardButton("💰 Giá hiện tại", callback_data='current_price')],
            [InlineKeyboardButton("📊 Phân tích kỹ thuật", callback_data='technical_analysis')],
            [InlineKeyboardButton("📰 Tin tức crypto", callback_data='news')],
            [InlineKeyboardButton("💡 Gợi ý đầu tư", callback_data='investment_advice')],
            [InlineKeyboardButton("ℹ️ Thông tin coin", callback_data='coin_info')],
            [InlineKeyboardButton("⚙️ Cài đặt", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🤖 *Chào mừng đến với Crypto Investment Bot!*\n\n"
            "Tôi có thể giúp bạn:\n"
            "• Dự đoán giá cryptocurrency\n"
            "• Cung cấp thông tin thị trường real-time\n"
            "• Phân tích kỹ thuật\n"
            "• Tin tức và xu hướng thị trường\n"
            "• Gợi ý đầu tư thông minh\n\n"
            "Chọn một tùy chọn bên dưới để bắt đầu:"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý các nút bấm"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'predict':
            await self.show_prediction_menu(query)
        elif query.data.startswith('predict_'):
            symbol = query.data.replace('predict_', '')
            await self.show_prediction_result(query, symbol)
        elif query.data == 'current_price':
            await self.show_price_menu(query)
        elif query.data.startswith('price_'):
            symbol = query.data.replace('price_', '')
            await self.show_current_price(query, symbol)
        elif query.data == 'technical_analysis':
            await self.show_analysis_menu(query)
        elif query.data.startswith('analysis_'):
            symbol = query.data.replace('analysis_', '')
            await self.show_technical_analysis(query, symbol)
        elif query.data == 'news':
            await self.show_news(query)
        elif query.data == 'investment_advice':
            await self.show_investment_advice(query)
        elif query.data == 'coin_info':
            await self.show_coin_info_menu(query)
        elif query.data == 'back_to_main':
            await self.show_main_menu(query)
    
    async def show_prediction_menu(self, query):
        """Hiển thị menu dự đoán giá"""
        keyboard = [
            [InlineKeyboardButton("BTC/USDT", callback_data='predict_BTCUSDT')],
            [InlineKeyboardButton("ETH/USDT", callback_data='predict_ETHUSDT')],
            [InlineKeyboardButton("BNB/USDT", callback_data='predict_BNBUSDT')],
            [InlineKeyboardButton("ADA/USDT", callback_data='predict_ADAUSDT')],
            [InlineKeyboardButton("SOL/USDT", callback_data='predict_SOLUSDT')],
            [InlineKeyboardButton("🔙 Quay lại", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "📈 *Chọn cặp coin để dự đoán giá:*\n\nTôi sẽ phân tích dữ liệu lịch sử và đưa ra dự đoán giá trong 24h tới."
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_prediction_result(self, query, symbol):
        """Hiển thị kết quả dự đoán giá cho symbol"""
        try:
            await query.edit_message_text("🔄 Đang phân tích và dự đoán giá...")
            
            # Lấy dự đoán giá
            prediction = await self.predictor.predict_price(symbol)
            
            if prediction:
                text = f"📈 *Dự đoán giá {symbol}*\n\n"
                text += f"💰 Giá hiện tại: ${format_price(prediction['current_price'])}\n"
                text += f"🎯 Giá dự đoán (24h): ${format_price(prediction['predicted_price'])}\n"
                text += f"📊 Thay đổi dự kiến: {prediction['price_change_percent']:+.2f}%\n"
                text += f"🔮 Độ tin cậy: {prediction['confidence']:.1f}%\n"
                text += f"💡 Khuyến nghị: {prediction['recommendation']}\n\n"
                text += f"⏰ Thời gian phân tích: {prediction['prediction_time'].strftime('%H:%M:%S')}"
            else:
                text = f"❌ Không thể dự đoán giá cho {symbol}. Vui lòng thử lại sau."
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='predict')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in prediction result: {e}")
            await query.edit_message_text("❌ Có lỗi xảy ra khi dự đoán. Vui lòng thử lại sau.")
    
    async def show_current_price(self, query, symbol):
        """Hiển thị giá hiện tại cho symbol"""
        try:
            await query.edit_message_text("🔄 Đang lấy thông tin giá...")
            
            # Lấy thông tin giá 24h
            ticker = await self.binance_client.get_24h_ticker(symbol)
            
            if ticker:
                text = f"💰 *Giá hiện tại {symbol}*\n\n"
                text += f"💵 Giá: ${format_price(ticker['price'])}\n"
                text += f"📈 Thay đổi 24h: {format_percentage(ticker['change_percent'])}\n"
                text += f"📊 Volume 24h: {ticker['volume']:,.0f}\n"
                text += f"🔝 Cao nhất 24h: ${format_price(ticker['high'])}\n"
                text += f"🔻 Thấp nhất 24h: ${format_price(ticker['low'])}\n"
            else:
                text = f"❌ Không thể lấy thông tin giá cho {symbol}. Vui lòng thử lại sau."
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='current_price')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in current price: {e}")
            await query.edit_message_text("❌ Có lỗi xảy ra khi lấy giá. Vui lòng thử lại sau.")
    
    async def show_technical_analysis(self, query, symbol):
        """Hiển thị phân tích kỹ thuật cho symbol"""
        try:
            await query.edit_message_text("🔄 Đang phân tích kỹ thuật...")
            
            # Lấy phân tích kỹ thuật
            analysis = await self.predictor.get_technical_analysis(symbol)
            
            if analysis:
                text = f"📊 *Phân tích kỹ thuật {symbol}*\n\n"
                text += f"💰 Giá hiện tại: ${format_price(analysis['current_price'])}\n"
                text += f"📈 RSI: {analysis['rsi']:.2f}\n"
                text += f"📉 MACD: {analysis['macd']:.6f}\n"
                text += f"🎯 Xu hướng: {analysis['trend']}\n"
                text += f"📍 Bollinger Bands: {analysis['bb_position']}\n"
                text += f"🛡️ Hỗ trợ: ${format_price(analysis['support'])}\n"
                text += f"⚡ Kháng cự: ${format_price(analysis['resistance'])}\n\n"
                
                if analysis['signals']:
                    text += "🔔 *Tín hiệu:*\n"
                    for signal in analysis['signals']:
                        text += f"• {signal}\n"
            else:
                text = f"❌ Không thể phân tích kỹ thuật cho {symbol}. Vui lòng thử lại sau."
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='technical_analysis')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            await query.edit_message_text("❌ Có lỗi xảy ra khi phân tích. Vui lòng thử lại sau.")

    async def show_price_menu(self, query):
        """Hiển thị menu giá hiện tại"""
        keyboard = [
            [InlineKeyboardButton("BTC/USDT", callback_data='price_BTCUSDT')],
            [InlineKeyboardButton("ETH/USDT", callback_data='price_ETHUSDT')],
            [InlineKeyboardButton("BNB/USDT", callback_data='price_BNBUSDT')],
            [InlineKeyboardButton("ADA/USDT", callback_data='price_ADAUSDT')],
            [InlineKeyboardButton("SOL/USDT", callback_data='price_SOLUSDT')],
            [InlineKeyboardButton("🔙 Quay lại", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "💰 *Chọn cặp coin để xem giá hiện tại:*\n\nTôi sẽ cung cấp thông tin giá real-time và thống kê 24h."
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_analysis_menu(self, query):
        """Hiển thị menu phân tích kỹ thuật"""
        keyboard = [
            [InlineKeyboardButton("BTC/USDT", callback_data='analysis_BTCUSDT')],
            [InlineKeyboardButton("ETH/USDT", callback_data='analysis_ETHUSDT')],
            [InlineKeyboardButton("BNB/USDT", callback_data='analysis_BNBUSDT')],
            [InlineKeyboardButton("ADA/USDT", callback_data='analysis_ADAUSDT')],
            [InlineKeyboardButton("SOL/USDT", callback_data='analysis_SOLUSDT')],
            [InlineKeyboardButton("🔙 Quay lại", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "📊 *Chọn cặp coin để phân tích kỹ thuật:*\n\nTôi sẽ phân tích các chỉ báo kỹ thuật như RSI, MACD, Bollinger Bands."
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_main_menu(self, query):
        """Hiển thị menu chính"""
        keyboard = [
            [InlineKeyboardButton("📈 Dự đoán giá", callback_data='predict')],
            [InlineKeyboardButton("💰 Giá hiện tại", callback_data='current_price')],
            [InlineKeyboardButton("📊 Phân tích kỹ thuật", callback_data='technical_analysis')],
            [InlineKeyboardButton("📰 Tin tức crypto", callback_data='news')],
            [InlineKeyboardButton("💡 Gợi ý đầu tư", callback_data='investment_advice')],
            [InlineKeyboardButton("ℹ️ Thông tin coin", callback_data='coin_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "🤖 *Crypto Investment Bot*\n\nChọn chức năng bạn muốn sử dụng:"
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý tin nhắn văn bản"""
        text = update.message.text.upper()
        
        # Kiểm tra nếu user nhập symbol coin
        if any(symbol in text for symbol in ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOGE', 'XRP']):
            symbol = text.replace('USDT', '').replace('/', '')
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            await self.get_coin_analysis(update, symbol)
        else:
            await update.message.reply_text(
                "Vui lòng sử dụng menu hoặc nhập tên coin (VD: BTC, ETH, BNB...)"
            )
    
    async def get_coin_analysis(self, update, symbol):
        """Phân tích tổng quan một coin"""
        try:
            # Lấy giá hiện tại
            current_price = await self.binance_client.get_current_price(symbol)
            
            # Dự đoán giá
            prediction = await self.predictor.predict_price(symbol)
            
            # Tin tức liên quan
            news = await self.news_service.get_coin_news(symbol.replace('USDT', ''))
            
            response = f"📊 *Phân tích {symbol}*\n\n"
            response += f"💰 Giá hiện tại: ${format_price(current_price)}\n"
            
            if prediction:
                response += f"📈 Dự đoán 24h: ${format_price(prediction['predicted_price'])}\n"
                response += f"📊 Độ tin cậy: {prediction['confidence']:.1f}%\n"
                response += f"🎯 Khuyến nghị: {prediction['recommendation']}\n\n"
            
            if news:
                response += "📰 *Tin tức mới nhất:*\n"
                for article in news[:2]:
                    response += f"• {article['title'][:50]}...\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in coin analysis: {e}")
            await update.message.reply_text("❌ Có lỗi xảy ra khi phân tích. Vui lòng thử lại sau.")
    
    async def run_async(self):
        """Khởi động bot async"""
        application = None
        try:
            # Tạo application
            application = Application.builder().token(self.token).build()
            
            # Thêm handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CallbackQueryHandler(self.button_handler))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
            
            # Khởi tạo và chạy bot
            logger.info("Bot đang khởi động...")
            
            # Khởi tạo application
            await application.initialize()
            await application.start()
            
            # Bắt đầu polling
            await application.updater.start_polling()
            
            # Chờ vô hạn
            try:
                import signal
                stop_event = asyncio.Event()
                
                def signal_handler():
                    stop_event.set()
                
                # Đăng ký signal handlers nếu có thể
                try:
                    loop = asyncio.get_running_loop()
                    for sig in [signal.SIGTERM, signal.SIGINT]:
                        loop.add_signal_handler(sig, signal_handler)
                except (NotImplementedError, AttributeError):
                    # Windows không hỗ trợ signal handlers trong asyncio
                    pass
                
                await stop_event.wait()
                
            except KeyboardInterrupt:
                logger.info("Nhận được tín hiệu dừng...")
            
        except Exception as e:
            logger.error(f"💥 Lỗi nghiêm trọng: {e}")
            raise
        finally:
            # Cleanup
            if application:
                try:
                    await application.updater.stop()
                    await application.stop()
                    await application.shutdown()
                except Exception as e:
                    logger.error(f"Lỗi cleanup: {e}")
    
    def run(self):
        """Khởi động bot (deprecated - sử dụng run_async thay thế)"""
        try:
            asyncio.run(self.run_async())
        except Exception as e:
            logger.error(f"💥 Lỗi nghiêm trọng: {e}")
            raise

if __name__ == '__main__':
    bot = CryptoBotTelegram()
    bot.run()