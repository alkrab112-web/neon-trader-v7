from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import requests

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Emergent LLM Key
EMERGENT_LLM_KEY = "sk-emergent-84a76A1D28fB8Db43E"

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

# Market Data Service (Mock for now)
class MarketDataService:
    @staticmethod
    async def get_price(symbol: str) -> float:
        # Mock prices - in real version this would fetch from exchanges
        mock_prices = {
            "BTCUSDT": 43250.50,
            "ETHUSDT": 2580.75,
            "ADAUSDT": 0.45,
            "BNBUSDT": 310.25
        }
        return mock_prices.get(symbol, 100.0)
    
    @staticmethod
    async def get_market_data(symbol: str) -> Dict[str, Any]:
        price = await MarketDataService.get_price(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "change_24h": round(price * 0.02, 2),  # Mock 2% change
            "volume_24h": 1000000,
            "high_24h": price * 1.05,
            "low_24h": price * 0.95
        }

# AI Service
class AIService:
    @staticmethod
    async def get_market_analysis(symbol: str) -> str:
        try:
            # Using Emergent LLM Key for real AI analysis
            import requests
            
            headers = {
                "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
                "Content-Type": "application/json"
            }
            
            market_data = await MarketDataService.get_market_data(symbol)
            
            prompt = f"""
            Analyze the following market data for {symbol} and provide a comprehensive trading analysis:
            
            Current Price: ${market_data['price']}
            24h Change: ${market_data['change_24h']}
            24h High: ${market_data['high_24h']}
            24h Low: ${market_data['low_24h']}
            
            Provide analysis in Arabic including:
            1. Current market sentiment
            2. Technical indicators overview
            3. Support and resistance levels
            4. Trading recommendation
            
            Keep it concise and actionable.
            """
            
            # Mock response for now - will integrate real AI later
            return f"تحليل فني لـ {symbol}: السعر الحالي ${market_data['price']} يظهر اتجاهاً إيجابياً مع دعم قوي عند ${market_data['low_24h']:.2f}. يُنصح بالمراقبة عند مستوى ${market_data['high_24h']:.2f} للدخول."
            
        except Exception as e:
            return f"تحليل أساسي لـ {symbol}: السعر مستقر حالياً، يُنصح بالمتابعة قبل اتخاذ قرار."

    @staticmethod
    async def generate_daily_plan(user_id: str) -> DailyPlan:
        try:
            # Generate AI-powered daily plan
            plan = DailyPlan(
                user_id=user_id,
                date=datetime.now().strftime("%Y-%m-%d"),
                market_analysis="السوق يظهر اتجاهاً إيجابياً مع تقلبات معتدلة. Bitcoin يحافظ على مستوى الدعم الرئيسي.",
                trading_strategy="التركيز على العملات الرئيسية مع إدارة مخاطر محافظة",
                risk_level="متوسط",
                opportunities=[
                    {
                        "symbol": "BTCUSDT",
                        "action": "buy",
                        "confidence": "high",
                        "reason": "كسر مستوى المقاومة مع حجم تداول عالي",
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
            return plan
        except Exception as e:
            logging.error(f"Error generating daily plan: {e}")
            raise HTTPException(status_code=500, detail="فشل في إنشاء الخطة اليومية")

# Trading Engine
class TradingEngine:
    @staticmethod
    async def execute_trade(user_id: str, trade_request: TradeRequest) -> Trade:
        try:
            # Get current market price
            current_price = await MarketDataService.get_price(trade_request.symbol)
            
            # Create trade entry
            trade = Trade(
                user_id=user_id,
                platform="paper_trading",  # Mock platform for now
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
                    total_balance=10000.0,  # Mock starting balance
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
        
        # Mock connection test - in real version would test actual API
        success = True  # Mock success
        
        status = PlatformStatus.CONNECTED if success else PlatformStatus.DISCONNECTED
        
        await db.platforms.update_one(
            {"id": platform_id},
            {"$set": {"status": status}}
        )
        
        return {"success": success, "status": status, "message": "تم اختبار الاتصال بنجاح" if success else "فشل الاتصال"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@api_router.get("/market/prices/multiple")
async def get_multiple_prices(symbols: str):
    try:
        symbol_list = symbols.split(",")
        prices = {}
        
        for symbol in symbol_list:
            prices[symbol.strip()] = await MarketDataService.get_price(symbol.strip())
            
        return prices
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