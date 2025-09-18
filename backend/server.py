from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import requests
from passlib.context import CryptContext
from jose import JWTError, jwt
import hashlib

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security settings
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key')
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Emergent LLM Key from environment
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app
app = FastAPI(title="Neon Trader V7", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Enums
class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class PlatformStatus(str, Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    two_factor_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Portfolio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    total_balance: float
    available_balance: float
    invested_balance: float
    daily_pnl: float
    total_pnl: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Trade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    platform: str
    symbol: str
    trade_type: TradeType
    order_type: OrderType
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: TradeStatus
    pnl: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

class Platform(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    platform_type: str  # binance, bybit, etc
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    is_testnet: bool = True
    status: PlatformStatus = PlatformStatus.DISCONNECTED
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    symbol: str
    action: str  # buy, sell, hold
    confidence: str  # high, medium, low
    reason: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DailyPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    date: str
    market_analysis: str
    trading_strategy: str
    risk_level: str
    opportunities: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    username: str

class TradeRequest(BaseModel):
    symbol: str
    trade_type: TradeType
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PlatformRequest(BaseModel):
    name: str
    platform_type: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    is_testnet: bool = True

class AIAnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"

# Authentication Utilities
class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get user from JWT token"""
        token = credentials.credentials
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise credentials_exception
        
        user.pop('_id', None)
        return User(**user)
    
    @staticmethod
    async def get_current_active_user(current_user: User = Depends(lambda: AuthService.get_user_from_token)):
        """Get current active user"""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

# Enhanced Market Data Service with multiple asset types
class MarketDataService:
    # Asset type definitions
    ASSET_TYPES = {
        'crypto': {
            'name': 'العملات الرقمية',
            'symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'AVAXUSDT']
        },
        'forex': {
            'name': 'الفوركس',
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'EURJPY']
        },
        'stocks': {
            'name': 'الأسهم',
            'symbols': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        },
        'commodities': {
            'name': 'السلع',
            'symbols': ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'WHEAT', 'CORN']
        },
        'indices': {
            'name': 'المؤشرات',
            'symbols': ['SPX500', 'NAS100', 'DJ30', 'GER40', 'UK100', 'JPN225', 'AUS200', 'HK50']
        }
    }

    @staticmethod
    async def get_all_asset_types():
        """Get all supported asset types"""
        return MarketDataService.ASSET_TYPES

    @staticmethod
    async def get_symbols_by_type(asset_type: str):
        """Get symbols for specific asset type"""
        return MarketDataService.ASSET_TYPES.get(asset_type, {}).get('symbols', [])

    @staticmethod
    async def get_price_from_binance(symbol: str) -> float:
        """Get real price from Binance API (for crypto)"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
        except Exception as e:
            logging.error(f"Error fetching price from Binance: {e}")
        return None

    @staticmethod
    async def get_price_from_alpha_vantage(symbol: str, asset_type: str) -> float:
        """Get price from Alpha Vantage for stocks/forex"""
        try:
            import aiohttp
            # This would require Alpha Vantage API key in production
            # For now, return mock data based on asset type
            mock_prices = {
                'forex': {
                    'EURUSD': 1.0950, 'GBPUSD': 1.2750, 'USDJPY': 149.50,
                    'AUDUSD': 0.6650, 'USDCHF': 0.8950, 'USDCAD': 1.3550,
                    'NZDUSD': 0.6150, 'EURJPY': 163.20
                },
                'stocks': {
                    'AAPL': 195.50, 'GOOGL': 142.80, 'MSFT': 415.25,
                    'AMZN': 155.75, 'TSLA': 248.50, 'META': 325.80,
                    'NVDA': 875.25, 'NFLX': 485.60
                },
                'commodities': {
                    'XAUUSD': 2015.50, 'XAGUSD': 24.85, 'USOIL': 78.25,
                    'UKOIL': 82.15, 'NATGAS': 2.65, 'COPPER': 8.45,
                    'WHEAT': 5.85, 'CORN': 4.75
                },
                'indices': {
                    'SPX500': 4515.25, 'NAS100': 15850.75, 'DJ30': 35650.80,
                    'GER40': 16250.45, 'UK100': 7485.60, 'JPN225': 32850.90,
                    'AUS200': 7125.35, 'HK50': 17850.25
                }
            }
            
            return mock_prices.get(asset_type, {}).get(symbol, 100.0)
            
        except Exception as e:
            logging.error(f"Error fetching price from Alpha Vantage: {e}")
        return None

    @staticmethod
    async def detect_asset_type(symbol: str) -> str:
        """Detect asset type based on symbol"""
        for asset_type, data in MarketDataService.ASSET_TYPES.items():
            if symbol in data['symbols']:
                return asset_type
        return 'crypto'  # Default to crypto

    @staticmethod
    async def get_price(symbol: str) -> float:
        """Get price with support for multiple asset types"""
        asset_type = await MarketDataService.detect_asset_type(symbol)
        
        if asset_type == 'crypto':
            # Try Binance first for crypto
            price = await MarketDataService.get_price_from_binance(symbol)
            if price is not None:
                return price
        
        # Try Alpha Vantage for other asset types
        price = await MarketDataService.get_price_from_alpha_vantage(symbol, asset_type)
        if price is not None:
            return price
        
        # Ultimate fallback to mock prices
        mock_prices = {
            "BTCUSDT": 43250.50, "ETHUSDT": 2580.75, "ADAUSDT": 0.45, "BNBUSDT": 310.25,
            "EURUSD": 1.0950, "GBPUSD": 1.2750, "USDJPY": 149.50,
            "AAPL": 195.50, "GOOGL": 142.80, "MSFT": 415.25,
            "XAUUSD": 2015.50, "XAGUSD": 24.85, "USOIL": 78.25,
            "SPX500": 4515.25, "NAS100": 15850.75
        }
        price = mock_prices.get(symbol, 100.0)
        logging.warning(f"Using mock price for {symbol} ({asset_type}): {price}")
        
        return price
    
    @staticmethod
    async def get_market_data(symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data for any asset type"""
        asset_type = await MarketDataService.detect_asset_type(symbol)
        
        try:
            if asset_type == 'crypto':
                # Try to get real data from Binance for crypto
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "symbol": symbol,
                                "asset_type": asset_type,
                                "price": float(data['lastPrice']),
                                "change_24h": float(data['priceChange']),
                                "change_24h_percent": float(data['priceChangePercent']),
                                "volume_24h": float(data['volume']),
                                "high_24h": float(data['highPrice']),
                                "low_24h": float(data['lowPrice']),
                                "open_price": float(data['openPrice']),
                                "timestamp": datetime.utcnow()
                            }
        except Exception as e:
            logging.error(f"Error fetching real market data: {e}")
        
        # Fallback to constructed data
        price = await MarketDataService.get_price(symbol)
        
        # Different volatility for different asset types
        volatility_multipliers = {
            'crypto': 0.05,    # 5% volatility
            'forex': 0.01,     # 1% volatility  
            'stocks': 0.03,    # 3% volatility
            'commodities': 0.04, # 4% volatility
            'indices': 0.02    # 2% volatility
        }
        
        volatility = volatility_multipliers.get(asset_type, 0.03)
        change_24h = round(price * volatility * (1 if hash(symbol) % 2 else -1), 4)
        
        return {
            "symbol": symbol,
            "asset_type": asset_type,
            "asset_type_name": MarketDataService.ASSET_TYPES[asset_type]['name'],
            "price": price,
            "change_24h": change_24h,
            "change_24h_percent": round((change_24h / price) * 100, 2),
            "volume_24h": 1000000 * (1 + hash(symbol) % 10),
            "high_24h": price * (1 + volatility),
            "low_24h": price * (1 - volatility),
            "open_price": price * (1 - change_24h / price),
            "timestamp": datetime.utcnow()
        }

# AI Service
class AIService:
    @staticmethod
    async def get_market_analysis(symbol: str) -> str:
        try:
            # Using Emergent LLM Key for real AI analysis
            from emergentintegrations import EmergentLLM
            
            market_data = await MarketDataService.get_market_data(symbol)
            
            prompt = f"""
            أنت خبير تحليل مالي متخصص في العملات المشفرة. قم بتحليل البيانات التالية لـ {symbol}:
            
            السعر الحالي: ${market_data['price']}
            التغيير خلال 24 ساعة: ${market_data['change_24h']}
            أعلى سعر خلال 24 ساعة: ${market_data['high_24h']}
            أدنى سعر خلال 24 ساعة: ${market_data['low_24h']}
            
            قدم تحليلاً تقنياً شاملاً يتضمن:
            1. تحليل الاتجاه الحالي (صاعد/هابط/جانبي)
            2. مستويات الدعم والمقاومة المهمة
            3. توصية التداول (شراء/بيع/انتظار)
            4. إدارة المخاطر المقترحة
            
            اجعل التحليل مختصراً وقابلاً للتطبيق باللغة العربية.
            """
            
            # Initialize Emergent LLM
            llm = EmergentLLM(api_key=EMERGENT_LLM_KEY)
            
            # Get AI analysis
            analysis = llm.generate_text(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o-mini",
                max_tokens=300
            )
            
            return analysis.get('content', f"تحليل أساسي لـ {symbol}: السعر مستقر حالياً، يُنصح بالمتابعة قبل اتخاذ قرار.")
            
        except Exception as e:
            logging.error(f"Error in AI analysis: {e}")
            market_data = await MarketDataService.get_market_data(symbol)
            return f"تحليل فني لـ {symbol}: السعر الحالي ${market_data['price']} يظهر اتجاهاً مستقراً. المستوى الداعم عند ${market_data['low_24h']:.2f} والمقاومة عند ${market_data['high_24h']:.2f}."

    @staticmethod
    async def generate_daily_plan(user_id: str) -> DailyPlan:
        try:
            from emergentintegrations import EmergentLLM
            
            # Get current market data for major cryptocurrencies
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT']
            market_summary = []
            
            for symbol in symbols:
                data = await MarketDataService.get_market_data(symbol)
                market_summary.append(f"{symbol}: ${data['price']} ({data['change_24h']:+.2f})")
            
            prompt = f"""
            أنت مساعد تداول ذكي متخصص في العملات المشفرة. قم بإعداد خطة تداول يومية باللغة العربية تتضمن:

            بيانات السوق الحالية:
            {' | '.join(market_summary)}

            أعد خطة تداول يومية شاملة تتضمن:
            1. تحليل وضع السوق العام (50-80 كلمة)
            2. استراتيجية التداول المقترحة (30-50 كلمة)  
            3. تقييم مستوى المخاطرة (منخفض/متوسط/عالي)
            4. 2-3 فرص تداول محددة مع التفسير

            يجب أن تكون التوصيات عملية ومناسبة للتداول اليومي مع إدارة مخاطر محافظة.
            """
            
            llm = EmergentLLM(api_key=EMERGENT_LLM_KEY)
            ai_response = llm.generate_text(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o-mini",
                max_tokens=400
            )
            
            ai_content = ai_response.get('content', '')
            
            # Parse AI response or use fallback
            if ai_content:
                plan = DailyPlan(
                    user_id=user_id,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    market_analysis=ai_content[:200] + "..." if len(ai_content) > 200 else ai_content,
                    trading_strategy="استراتيجية محافظة مع التركيز على الفرص عالية الاحتمالية",
                    risk_level="متوسط",
                    opportunities=[
                        {
                            "symbol": "BTCUSDT",
                            "action": "buy" if "شراء" in ai_content or "buy" in ai_content.lower() else "hold",
                            "confidence": "high",
                            "reason": "تحليل AI يشير لفرصة إيجابية",
                            "target": 45000,
                            "stop_loss": 42000
                        },
                        {
                            "symbol": "ETHUSDT", 
                            "action": "hold",
                            "confidence": "medium",
                            "reason": "انتظار إشارة اختراق واضحة",
                            "target": 2700,
                            "stop_loss": 2400
                        }
                    ]
                )
            else:
                # Fallback plan
                plan = DailyPlan(
                    user_id=user_id,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    market_analysis="السوق يظهر استقراراً نسبياً مع تقلبات معتدلة. Bitcoin يحافظ على مستويات دعم مهمة.",
                    trading_strategy="التركيز على العملات الرئيسية مع إدارة مخاطر محافظة",
                    risk_level="متوسط",
                    opportunities=[
                        {
                            "symbol": "BTCUSDT",
                            "action": "buy",
                            "confidence": "high",
                            "reason": "مستوى دعم قوي مع حجم تداول جيد",
                            "target": 45000,
                            "stop_loss": 42000
                        },
                        {
                            "symbol": "ETHUSDT", 
                            "action": "hold",
                            "confidence": "medium",
                            "reason": "انتظار كسر مستوى المقاومة",
                            "target": 2700,
                            "stop_loss": 2400
                        }
                    ]
                )
            
            return plan
            
        except Exception as e:
            logging.error(f"Error generating daily plan: {e}")
            # Return fallback plan
            plan = DailyPlan(
                user_id=user_id,
                date=datetime.now().strftime("%Y-%m-%d"),
                market_analysis="السوق يظهر استقراراً مع فرص محدودة اليوم",
                trading_strategy="نهج محافظ مع التركيز على إدارة المخاطر",
                risk_level="منخفض",
                opportunities=[
                    {
                        "symbol": "BTCUSDT",
                        "action": "hold",
                        "confidence": "medium",
                        "reason": "انتظار إشارات السوق",
                        "target": 44000,
                        "stop_loss": 41000
                    }
                ]
            )
            return plan

# Real Trading Engine with multiple exchange support
class RealTradingEngine:
    @staticmethod
    async def get_exchange_client(platform_type: str, api_key: str, secret_key: str, is_testnet: bool = True):
        """Initialize exchange client using CCXT"""
        try:
            import ccxt
            
            exchange_class = getattr(ccxt, platform_type.lower())
            
            # Configure exchange
            config = {
                'apiKey': api_key,
                'secret': secret_key,
                'timeout': 30000,
                'enableRateLimit': True,
            }
            
            # Set sandbox mode for supported exchanges
            if is_testnet:
                if platform_type.lower() in ['binance', 'bybit']:
                    config['sandbox'] = True
                elif platform_type.lower() == 'binance':
                    config['urls'] = {'api': 'https://testnet.binance.vision'}
            
            exchange = exchange_class(config)
            return exchange
            
        except Exception as e:
            logging.error(f"Error initializing exchange client: {e}")
            return None

    @staticmethod
    async def test_connection(platform_type: str, api_key: str, secret_key: str, is_testnet: bool = True) -> bool:
        """Test connection to exchange"""
        try:
            exchange = await RealTradingEngine.get_exchange_client(platform_type, api_key, secret_key, is_testnet)
            if exchange is None:
                return False
            
            # Test API connection
            balance = await exchange.fetch_balance()
            return True
            
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            return False

    @staticmethod
    async def execute_real_trade(platform: Platform, trade_request: TradeRequest) -> Dict[str, Any]:
        """Execute real trade on exchange"""
        try:
            exchange = await RealTradingEngine.get_exchange_client(
                platform.platform_type, 
                platform.api_key, 
                platform.secret_key, 
                platform.is_testnet
            )
            
            if exchange is None:
                raise Exception("Failed to initialize exchange client")
            
            # Prepare order parameters
            order_type = 'market' if trade_request.order_type == OrderType.MARKET else 'limit'
            side = 'buy' if trade_request.trade_type == TradeType.BUY else 'sell'
            
            # Execute order
            order = await exchange.create_order(
                symbol=trade_request.symbol,
                type=order_type,
                side=side,
                amount=trade_request.quantity,
                price=trade_request.price if order_type == 'limit' else None
            )
            
            return {
                'success': True,
                'order': order,
                'exchange': platform.platform_type
            }
            
        except Exception as e:
            logging.error(f"Real trade execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'exchange': platform.platform_type
            }

# Enhanced Trading Engine with real trading support
class TradingEngine:
    @staticmethod
    async def execute_trade(user_id: str, trade_request: TradeRequest, use_real_trading: bool = False) -> Trade:
        try:
            current_price = await MarketDataService.get_price(trade_request.symbol)
            
            # Determine platform to use
            platform_name = "paper_trading"
            
            if use_real_trading:
                # Get user's connected platforms
                platforms = await db.platforms.find({
                    "user_id": user_id, 
                    "status": PlatformStatus.CONNECTED
                }).to_list(10)
                
                if platforms:
                    # Use first connected platform
                    platform = platforms[0]
                    platform_obj = Platform(**platform)
                    
                    # Execute real trade
                    real_trade_result = await RealTradingEngine.execute_real_trade(platform_obj, trade_request)
                    
                    if real_trade_result['success']:
                        platform_name = f"{platform['platform_type']}_{'testnet' if platform['is_testnet'] else 'live'}"
                        current_price = real_trade_result['order'].get('price', current_price)
                    else:
                        logging.warning(f"Real trade failed, falling back to paper trading: {real_trade_result['error']}")
            
            # Create trade entry
            trade = Trade(
                user_id=user_id,
                platform=platform_name,
                symbol=trade_request.symbol,
                trade_type=trade_request.trade_type,
                order_type=trade_request.order_type,
                quantity=trade_request.quantity,
                entry_price=trade_request.price or current_price,
                stop_loss=trade_request.stop_loss,
                take_profit=trade_request.take_profit,
                status=TradeStatus.OPEN
            )
            
            # Save to database
            await db.trades.insert_one(trade.dict())
            
            # Update portfolio
            await TradingEngine.update_portfolio(user_id, trade)
            
            return trade
            
        except Exception as e:
            logging.error(f"Error executing trade: {e}")
            raise HTTPException(status_code=500, detail="فشل في تنفيذ الصفقة")
    
    @staticmethod
    async def update_portfolio(user_id: str, trade: Trade):
        try:
            portfolio = await db.portfolios.find_one({"user_id": user_id})
            
            if not portfolio:
                # Create new portfolio
                portfolio = Portfolio(
                    user_id=user_id,
                    total_balance=10000.0,  # Starting balance
                    available_balance=10000.0,
                    invested_balance=0.0,
                    daily_pnl=0.0,
                    total_pnl=0.0
                )
                await db.portfolios.insert_one(portfolio.dict())
            
            # Calculate trade value
            trade_value = trade.quantity * trade.entry_price
            
            # Update balances
            if trade.status == TradeStatus.OPEN:
                new_available = portfolio["available_balance"] - trade_value
                new_invested = portfolio["invested_balance"] + trade_value
                
                await db.portfolios.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "available_balance": new_available,
                            "invested_balance": new_invested,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
        except Exception as e:
            logging.error(f"Error updating portfolio: {e}")

# API Routes

@api_router.get("/")
async def root():
    return {"message": "Neon Trader V7 API", "status": "active", "version": "1.0.0"}

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register_user(user_data: UserRegister):
    try:
        # Validate password confirmation
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="كلمات المرور غير متطابقة")
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم بالفعل")
        
        existing_username = await db.users.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(status_code=400, detail="اسم المستخدم غير متاح")
        
        # Hash password
        hashed_password = AuthService.get_password_hash(user_data.password)
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        # Save to database
        await db.users.insert_one(user.dict())
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        # Create default portfolio for user
        portfolio = Portfolio(
            user_id=user.id,
            total_balance=10000.0,
            available_balance=10000.0,
            invested_balance=0.0,
            daily_pnl=0.0,
            total_pnl=0.0
        )
        await db.portfolios.insert_one(portfolio.dict())
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="خطأ في إنشاء الحساب")

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    try:
        # Find user
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")
        
        # Verify password
        if not AuthService.verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")
        
        # Check if account is active
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="الحساب غير نشط")
        
        # TODO: Handle 2FA if enabled
        if user.get("two_factor_enabled", False) and not user_data.two_factor_code:
            raise HTTPException(status_code=422, detail="مطلوب رمز التحقق الثنائي")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user["id"]}, expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user["id"],
            email=user["email"],
            username=user["username"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="خطأ في تسجيل الدخول")

@api_router.get("/auth/me")
async def get_current_user(current_user: User = Depends(AuthService.get_user_from_token)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_active": current_user.is_active,
        "two_factor_enabled": current_user.two_factor_enabled,
        "created_at": current_user.created_at
    }

# Portfolio Routes
@api_router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    try:
        portfolio = await db.portfolios.find_one({"user_id": user_id})
        if not portfolio:
            # Create default portfolio
            portfolio = Portfolio(
                user_id=user_id,
                total_balance=10000.0,
                available_balance=10000.0,
                invested_balance=0.0,
                daily_pnl=0.0,
                total_pnl=0.0
            )
            await db.portfolios.insert_one(portfolio.dict())
            return portfolio.dict()
        
        # Remove _id field for JSON serialization
        portfolio.pop('_id', None)
        return portfolio
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trades Routes
@api_router.post("/trades/{user_id}")
async def create_trade(user_id: str, trade_request: TradeRequest):
    try:
        trade = await TradingEngine.execute_trade(user_id, trade_request)
        return {"message": "تم تنفيذ الصفقة بنجاح", "trade": trade.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trades/{user_id}")
async def get_trades(user_id: str):
    try:
        trades = await db.trades.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        # Remove _id fields
        for trade in trades:
            trade.pop('_id', None)
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/trades/{trade_id}/close")
async def close_trade(trade_id: str):
    try:
        trade = await db.trades.find_one({"id": trade_id})
        if not trade:
            raise HTTPException(status_code=404, detail="الصفقة غير موجودة")
        
        # Get current price for closing
        current_price = await MarketDataService.get_price(trade["symbol"])
        
        # Calculate PnL
        if trade["trade_type"] == "buy":
            pnl = (current_price - trade["entry_price"]) * trade["quantity"]
        else:
            pnl = (trade["entry_price"] - current_price) * trade["quantity"]
        
        # Update trade
        await db.trades.update_one(
            {"id": trade_id},
            {
                "$set": {
                    "status": TradeStatus.CLOSED,
                    "exit_price": current_price,
                    "pnl": pnl,
                    "closed_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "تم إغلاق الصفقة بنجاح", "pnl": pnl}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Platforms Routes
@api_router.post("/platforms/{user_id}")
async def add_platform(user_id: str, platform_request: PlatformRequest):
    try:
        platform = Platform(
            user_id=user_id,
            name=platform_request.name,
            platform_type=platform_request.platform_type,
            api_key=platform_request.api_key,
            secret_key=platform_request.secret_key,
            is_testnet=platform_request.is_testnet,
            status=PlatformStatus.DISCONNECTED
        )
        
        await db.platforms.insert_one(platform.dict())
        return {"message": "تم إضافة المنصة بنجاح", "platform": platform.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/platforms/{user_id}")
async def get_platforms(user_id: str):
    try:
        platforms = await db.platforms.find({"user_id": user_id}).to_list(100)
        # Remove _id and sensitive fields
        for platform in platforms:
            platform.pop('_id', None)
            platform.pop('secret_key', None)  # Don't expose secret keys
        return platforms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/platforms/{platform_id}/test")
async def test_platform_connection(platform_id: str):
    try:
        platform = await db.platforms.find_one({"id": platform_id})
        if not platform:
            raise HTTPException(status_code=404, detail="المنصة غير موجودة")
        
        # Real connection test if API keys are provided
        success = False
        message = ""
        
        if platform.get('api_key') and platform.get('secret_key'):
            # Test real connection
            success = await RealTradingEngine.test_connection(
                platform['platform_type'],
                platform['api_key'],
                platform['secret_key'],
                platform['is_testnet']
            )
            message = "تم اختبار الاتصال بنجاح - المنصة متصلة!" if success else "فشل الاتصال - تحقق من صحة مفاتيح API"
        else:
            # Mock connection for platforms without API keys
            success = True
            message = "اختبار وهمي - أضف مفاتيح API للاتصال الحقيقي"
        
        status = PlatformStatus.CONNECTED if success else PlatformStatus.DISCONNECTED
        
        await db.platforms.update_one(
            {"id": platform_id},
            {"$set": {"status": status}}
        )
        
        return {"success": success, "status": status, "message": message}
        
    except Exception as e:
        logging.error(f"Platform connection test error: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في اختبار الاتصال: {str(e)}")

# AI Assistant Routes
@api_router.get("/ai/daily-plan/{user_id}")
async def get_daily_plan(user_id: str):
    try:
        # Check if plan exists for today
        today = datetime.now().strftime("%Y-%m-%d")
        existing_plan = await db.daily_plans.find_one({"user_id": user_id, "date": today})
        
        if existing_plan:
            existing_plan.pop('_id', None)
            return existing_plan
        
        # Generate new plan
        plan = await AIService.generate_daily_plan(user_id)
        await db.daily_plans.insert_one(plan.dict())
        
        return plan.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ai/analyze")
async def analyze_market(analysis_request: AIAnalysisRequest):
    try:
        analysis = await AIService.get_market_analysis(analysis_request.symbol)
        market_data = await MarketDataService.get_market_data(analysis_request.symbol)
        
        return {
            "symbol": analysis_request.symbol,
            "analysis": analysis,
            "market_data": market_data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Market Data Routes
@api_router.get("/market/{symbol}")
async def get_market_data(symbol: str):
    try:
        data = await MarketDataService.get_market_data(symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/types/all")
async def get_all_asset_types():
    try:
        types = await MarketDataService.get_all_asset_types()
        return types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/symbols/{asset_type}")
async def get_symbols_by_asset_type(asset_type: str):
    try:
        symbols = await MarketDataService.get_symbols_by_type(asset_type)
        if not symbols:
            raise HTTPException(status_code=404, detail="نوع الأصل غير موجود")
        return {"asset_type": asset_type, "symbols": symbols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/prices/multiple")
async def get_multiple_prices(symbols: str):
    try:
        symbol_list = symbols.split(",")
        prices = {}
        
        for symbol in symbol_list:
            symbol = symbol.strip()
            market_data = await MarketDataService.get_market_data(symbol)
            prices[symbol] = {
                "price": market_data["price"],
                "change_24h_percent": market_data["change_24h_percent"],
                "asset_type": market_data.get("asset_type", "unknown")
            }
            
        return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Smart Notifications System
class SmartNotificationService:
    @staticmethod
    async def generate_market_analysis() -> str:
        """Generate AI-powered market analysis"""
        try:
            from emergentintegrations import EmergentLLM
            
            # Get current market data for analysis
            symbols = ['BTCUSDT', 'ETHUSDT', 'XAUUSD', 'EURUSD', 'AAPL']
            market_data = []
            
            for symbol in symbols:
                data = await MarketDataService.get_market_data(symbol)
                market_data.append({
                    'symbol': symbol,
                    'price': data['price'],
                    'change_24h_percent': data['change_24h_percent'],
                    'asset_type': data.get('asset_type', 'unknown')
                })
            
            prompt = f"""
            أنت خبير تحليل أسواق مالية متخصص. قم بتحليل البيانات التالية وقدم توصيات ذكية:

            بيانات السوق الحالية:
            {market_data}

            قدم تحليلاً يتضمن:
            1. تحليل الاتجاه العام للأسواق
            2. أفضل 2-3 فرص استثمارية حالياً 
            3. تحذيرات مخاطر محتملة
            4. توصيات للمدى القصير والطويل
            5. نصائح لإدارة المحفظة

            اجعل التحليل مفيداً وقابلاً للتطبيق باللغة العربية.
            """
            
            llm = EmergentLLM(api_key=EMERGENT_LLM_KEY)
            analysis = llm.generate_text(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o-mini",
                max_tokens=500
            )
            
            return analysis.get('content', 'تحليل السوق غير متاح حالياً')
            
        except Exception as e:
            logging.error(f"Error generating market analysis: {e}")
            return "تحليل السوق العام: الأسواق تشهد حركة طبيعية مع فرص متنوعة للاستثمار."

    @staticmethod
    async def detect_trading_opportunities(user_id: str) -> List[Dict[str, Any]]:
        """Detect trading opportunities using AI"""
        try:
            opportunities = []
            
            # Mock opportunities - في الإنتاج ستكون تحليل حقيقي
            mock_opportunities = [
                {
                    'symbol': 'BTCUSDT',
                    'type': 'breakout',
                    'confidence': 85,
                    'timeframe': 'متوسط المدى',
                    'description': 'كسر مستوى المقاومة مع حجم تداول عالي',
                    'target_price': 47000,
                    'stop_loss': 41000,
                    'risk_reward': 2.5
                },
                {
                    'symbol': 'XAUUSD', 
                    'type': 'news_driven',
                    'confidence': 78,
                    'timeframe': 'طويل المدى',
                    'description': 'قرارات البنوك المركزية تدعم ارتفاع الذهب',
                    'target_price': 2100,
                    'stop_loss': 1980,
                    'risk_reward': 3.0
                }
            ]
            
            return mock_opportunities
            
        except Exception as e:
            logging.error(f"Error detecting opportunities: {e}")
            return []

    @staticmethod
    async def create_smart_notification(user_id: str, notification_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a smart notification"""
        try:
            notification = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'type': notification_type,
                'title': data.get('title', 'إشعار جديد'),
                'message': data.get('message', ''),
                'symbol': data.get('symbol'),
                'confidence': data.get('confidence'),
                'timeframe': data.get('timeframe'),
                'priority': data.get('priority', 'medium'),
                'created_at': datetime.utcnow(),
                'read': False
            }
            
            await db.notifications.insert_one(notification)
            return notification
            
        except Exception as e:
            logging.error(f"Error creating notification: {e}")
            return None

# Smart Notifications Routes
@api_router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str):
    try:
        notifications = await db.notifications.find({"user_id": user_id}).sort("created_at", -1).to_list(50)
        # Remove _id fields
        for notification in notifications:
            notification.pop('_id', None)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/{user_id}/smart-alert")
async def create_smart_alert(user_id: str):
    try:
        # Generate AI-powered market analysis
        analysis = await SmartNotificationService.generate_market_analysis()
        
        # Detect opportunities
        opportunities = await SmartNotificationService.detect_trading_opportunities(user_id)
        
        # Create notification with analysis
        notification_data = {
            'title': 'تحليل ذكي جديد للأسواق',
            'message': analysis[:200] + "...",  # Truncate for notification
            'type': 'ai_analysis',
            'priority': 'high',
            'timeframe': 'تحليل شامل'
        }
        
        notification = await SmartNotificationService.create_smart_notification(
            user_id, 'opportunity', notification_data
        )
        
        return {
            'notification': notification,
            'analysis': analysis,
            'opportunities': opportunities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/{user_id}/opportunities")
async def get_trading_opportunities(user_id: str):
    try:
        opportunities = await SmartNotificationService.detect_trading_opportunities(user_id)
        return {'opportunities': opportunities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    try:
        result = await db.notifications.update_one(
            {"id": notification_id},
            {"$set": {"read": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="الإشعار غير موجود")
            
        return {"message": "تم تحديد الإشعار كمقروء"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background Tasks
async def update_market_prices():
    """Background task to update market prices periodically"""
    while True:
        try:
            # This would update real market prices in production
            await asyncio.sleep(60)  # Update every minute
        except Exception as e:
            logger.error(f"Error updating market prices: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Neon Trader V7 API Started")
    # Start background tasks
    # asyncio.create_task(update_market_prices())

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")