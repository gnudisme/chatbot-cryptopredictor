import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.newsapi = None
        
        if self.news_api_key:
            try:
                self.newsapi = NewsApiClient(api_key=self.news_api_key)
            except Exception as e:
                logger.warning(f"Không thể khởi tạo NewsAPI: {e}")
        
        # Các nguồn tin tức crypto miễn phí
        self.crypto_sources = {
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'cointelegraph': 'https://cointelegraph.com/rss',
            'decrypt': 'https://decrypt.co/feed',
            'bitcoinist': 'https://bitcoinist.com/feed/'
        }
        
        # Keywords cho từng coin
        self.coin_keywords = {
            'BTC': ['bitcoin', 'btc', 'Bitcoin'],
            'ETH': ['ethereum', 'eth', 'Ethereum', 'ether'],
            'BNB': ['binance', 'bnb', 'Binance Coin'],
            'ADA': ['cardano', 'ada', 'Cardano'],
            'SOL': ['solana', 'sol', 'Solana'],
            'DOGE': ['dogecoin', 'doge', 'Dogecoin'],
            'XRP': ['ripple', 'xrp', 'XRP', 'Ripple'],
            'DOT': ['polkadot', 'dot', 'Polkadot'],
            'AVAX': ['avalanche', 'avax', 'Avalanche'],
            'MATIC': ['polygon', 'matic', 'Polygon']
        }
    
    async def get_crypto_news(self, limit=10):
        """Lấy tin tức crypto tổng quát"""
        try:
            news_articles = []
            
            # Sử dụng NewsAPI nếu có
            if self.newsapi:
                try:
                    articles = self.newsapi.get_everything(
                        q='cryptocurrency OR bitcoin OR ethereum',
                        language='en',
                        sort_by='publishedAt',
                        page_size=limit
                    )
                    
                    for article in articles['articles']:
                        news_articles.append({
                            'title': article['title'],
                            'description': article['description'],
                            'url': article['url'],
                            'source': article['source']['name'],
                            'published_at': article['publishedAt'],
                            'sentiment': self.analyze_sentiment(article['title'] + ' ' + (article['description'] or ''))
                        })
                except Exception as e:
                    logger.error(f"Lỗi NewsAPI: {e}")
            
            # Lấy từ CoinGecko API (miễn phí)
            try:
                async with aiohttp.ClientSession() as session:
                    url = "https://api.coingecko.com/api/v3/news"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get('data', [])[:limit]:
                                news_articles.append({
                                    'title': item.get('title', ''),
                                    'description': item.get('description', ''),
                                    'url': item.get('url', ''),
                                    'source': item.get('news_site', 'CoinGecko'),
                                    'published_at': item.get('published_at', ''),
                                    'sentiment': self.analyze_sentiment(item.get('title', '') + ' ' + item.get('description', ''))
                                })
            except Exception as e:
                logger.error(f"Lỗi CoinGecko News: {e}")
            
            # Lấy từ CryptoPanic API (miễn phí)
            try:
                async with aiohttp.ClientSession() as session:
                    url = "https://cryptopanic.com/api/v1/posts/?auth_token=free&kind=news"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get('results', [])[:limit]:
                                news_articles.append({
                                    'title': item.get('title', ''),
                                    'description': '',
                                    'url': item.get('url', ''),
                                    'source': item.get('source', {}).get('title', 'CryptoPanic'),
                                    'published_at': item.get('published_at', ''),
                                    'sentiment': self.analyze_sentiment(item.get('title', ''))
                                })
            except Exception as e:
                logger.error(f"Lỗi CryptoPanic: {e}")
            
            # Sắp xếp theo thời gian và loại bỏ trùng lặp
            unique_articles = self.remove_duplicates(news_articles)
            return sorted(unique_articles, key=lambda x: x.get('published_at', ''), reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Lỗi lấy tin tức crypto: {e}")
            return []
    
    async def get_general_crypto_news(self, limit=10):
        """Alias cho get_crypto_news để tương thích"""
        return await self.get_crypto_news(limit)
    
    async def get_coin_news(self, coin_symbol, limit=5):
        """Lấy tin tức cho một coin cụ thể"""
        try:
            coin_symbol = coin_symbol.upper().replace('USDT', '')
            keywords = self.coin_keywords.get(coin_symbol, [coin_symbol.lower()])
            
            news_articles = []
            
            # Sử dụng NewsAPI nếu có
            if self.newsapi:
                try:
                    query = ' OR '.join(keywords)
                    articles = self.newsapi.get_everything(
                        q=query,
                        language='en',
                        sort_by='publishedAt',
                        page_size=limit * 2  # Lấy nhiều hơn để filter
                    )
                    
                    for article in articles['articles']:
                        if any(keyword.lower() in (article['title'] + ' ' + (article['description'] or '')).lower() 
                              for keyword in keywords):
                            news_articles.append({
                                'title': article['title'],
                                'description': article['description'],
                                'url': article['url'],
                                'source': article['source']['name'],
                                'published_at': article['publishedAt'],
                                'sentiment': self.analyze_sentiment(article['title'] + ' ' + (article['description'] or '')),
                                'relevance': self.calculate_relevance(article['title'] + ' ' + (article['description'] or ''), keywords)
                            })
                except Exception as e:
                    logger.error(f"Lỗi NewsAPI cho {coin_symbol}: {e}")
            
            # Lấy từ CryptoPanic với filter coin
            try:
                async with aiohttp.ClientSession() as session:
                    # Tìm currency ID
                    currency_map = {
                        'BTC': 'BTC', 'ETH': 'ETH', 'BNB': 'BNB',
                        'ADA': 'ADA', 'SOL': 'SOL', 'DOGE': 'DOGE',
                        'XRP': 'XRP', 'DOT': 'DOT', 'AVAX': 'AVAX', 'MATIC': 'MATIC'
                    }
                    
                    currency_id = currency_map.get(coin_symbol, coin_symbol)
                    url = f"https://cryptopanic.com/api/v1/posts/?auth_token=free&currencies={currency_id}&kind=news"
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get('results', [])[:limit]:
                                news_articles.append({
                                    'title': item.get('title', ''),
                                    'description': '',
                                    'url': item.get('url', ''),
                                    'source': item.get('source', {}).get('title', 'CryptoPanic'),
                                    'published_at': item.get('published_at', ''),
                                    'sentiment': self.analyze_sentiment(item.get('title', '')),
                                    'relevance': 0.9  # High relevance vì đã filter theo coin
                                })
            except Exception as e:
                logger.error(f"Lỗi CryptoPanic cho {coin_symbol}: {e}")
            
            # Sắp xếp theo relevance và thời gian
            unique_articles = self.remove_duplicates(news_articles)
            return sorted(unique_articles, 
                         key=lambda x: (x.get('relevance', 0), x.get('published_at', '')), 
                         reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Lỗi lấy tin tức cho {coin_symbol}: {e}")
            return []
    
    def analyze_sentiment(self, text):
        """Phân tích sentiment đơn giản dựa trên keywords"""
        if not text:
            return 'neutral'
        
        text = text.lower()
        
        positive_words = [
            'bullish', 'bull', 'surge', 'pump', 'moon', 'rocket', 'gain', 'profit',
            'rise', 'increase', 'up', 'high', 'breakthrough', 'adoption', 'partnership',
            'upgrade', 'positive', 'optimistic', 'rally', 'boom', 'soar'
        ]
        
        negative_words = [
            'bearish', 'bear', 'crash', 'dump', 'fall', 'drop', 'decline', 'loss',
            'down', 'low', 'hack', 'scam', 'ban', 'regulation', 'negative', 'pessimistic',
            'sell-off', 'correction', 'plunge', 'collapse'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_relevance(self, text, keywords):
        """Tính độ liên quan của bài báo với coin"""
        if not text:
            return 0
        
        text = text.lower()
        relevance_score = 0
        
        for keyword in keywords:
            count = text.count(keyword.lower())
            relevance_score += count * 0.3
        
        return min(1.0, relevance_score)
    
    def remove_duplicates(self, articles):
        """Loại bỏ bài báo trùng lặp"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles
    
    async def get_market_news_summary(self):
        """Tóm tắt tin tức thị trường"""
        try:
            news = await self.get_crypto_news(20)
            
            if not news:
                return None
            
            # Phân tích sentiment tổng thể
            sentiments = [article.get('sentiment', 'neutral') for article in news]
            positive_count = sentiments.count('positive')
            negative_count = sentiments.count('negative')
            neutral_count = sentiments.count('neutral')
            
            total = len(sentiments)
            if total == 0:
                return None
            
            # Tính sentiment score
            sentiment_score = (positive_count - negative_count) / total
            
            if sentiment_score > 0.3:
                overall_sentiment = "Tích cực 📈"
            elif sentiment_score < -0.3:
                overall_sentiment = "Tiêu cực 📉"
            else:
                overall_sentiment = "Trung tính ⚖️"
            
            # Top headlines
            top_headlines = [article['title'] for article in news[:5]]
            
            return {
                'overall_sentiment': overall_sentiment,
                'sentiment_score': sentiment_score,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'top_headlines': top_headlines,
                'total_articles': total,
                'analysis_time': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Lỗi tóm tắt tin tức thị trường: {e}")
            return None
    
    async def get_trending_topics(self):
        """Lấy các chủ đề trending"""
        try:
            news = await self.get_crypto_news(50)
            
            if not news:
                return []
            
            # Đếm từ khóa trong tiêu đề
            word_count = {}
            
            for article in news:
                title = article.get('title', '').lower()
                words = re.findall(r'\b[a-z]{3,}\b', title)
                
                for word in words:
                    if word not in ['the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 'have', 'been']:
                        word_count[word] = word_count.get(word, 0) + 1
            
            # Sắp xếp và lấy top trending
            trending = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return [{'topic': word, 'count': count} for word, count in trending]
            
        except Exception as e:
            logger.error(f"Lỗi lấy trending topics: {e}")
            return []