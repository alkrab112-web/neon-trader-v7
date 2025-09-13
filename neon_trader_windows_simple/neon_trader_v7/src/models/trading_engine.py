"""
المحرك الأساسي للتداول (Core Trading Engine)
يتولى تنفيذ الاستراتيجيات، إدارة المخاطر، ومعالجة أوامر التداول
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import uuid
from dataclasses import dataclass, asdict
import threading
import time


class OrderType(Enum):
    """أنواع الأوامر"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    OCO = "oco"  # One-Cancels-the-Other
    TRAIL = "trail"
    BREAK_EVEN = "break_even"


class OrderSide(Enum):
    """جهة الأمر"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """حالة الأمر"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PositionSide(Enum):
    """جهة المركز"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Order:
    """نموذج الأمر"""
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_price: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    exchange_order_id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Position:
    """نموذج المركز"""
    id: str
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Trade:
    """نموذج الصفقة"""
    id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    commission: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class RiskManager:
    """مدير المخاطر"""
    
    def __init__(self, 
                 max_risk_per_trade: float = 0.005,  # 0.5%
                 max_daily_loss: float = 0.02,       # 2%
                 max_positions: int = 10,
                 max_leverage: float = 1.0):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_positions = max_positions
        self.max_leverage = max_leverage
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def calculate_position_size(self, account_balance: float, entry_price: float, 
                              stop_loss_price: float) -> float:
        """
        حساب حجم المركز بناءً على إدارة المخاطر
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            return 0.0
        
        # حساب المخاطرة لكل سهم/عملة
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit <= 0:
            return 0.0
        
        # حساب المبلغ المخاطر به
        risk_amount = account_balance * self.max_risk_per_trade
        
        # حساب حجم المركز
        position_size = risk_amount / risk_per_unit
        
        return position_size
    
    def validate_order(self, order: Order, account_balance: float, 
                      current_positions: List[Position]) -> Tuple[bool, str]:
        """
        التحقق من صحة الأمر قبل التنفيذ
        """
        # التحقق من الخسارة اليومية
        if self.daily_pnl <= -account_balance * self.max_daily_loss:
            return False, "تم الوصول لحد الخسارة اليومي"
        
        # التحقق من عدد المراكز
        if len(current_positions) >= self.max_positions:
            return False, "تم الوصول للحد الأقصى من المراكز"
        
        # التحقق من حجم الأمر
        if order.quantity <= 0:
            return False, "حجم الأمر غير صالح"
        
        # التحقق من السعر
        if order.type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and order.price <= 0:
            return False, "سعر الأمر غير صالح"
        
        return True, "الأمر صالح"
    
    def update_daily_pnl(self, pnl_change: float):
        """
        تحديث الربح والخسارة اليومي
        """
        # إعادة تعيين إذا كان يوم جديد
        current_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if current_day > self.daily_reset_time:
            self.daily_pnl = 0.0
            self.daily_reset_time = current_day
        
        self.daily_pnl += pnl_change


class PaperTradingEngine:
    """
    محرك التداول الورقي (Paper Trading)
    محاكاة عمليات التداول دون استخدام أموال حقيقية
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.market_data: Dict[str, Dict] = {}
        self.risk_manager = RiskManager()
        self.is_running = False
        self._lock = threading.Lock()
    
    def start(self):
        """بدء محرك التداول"""
        self.is_running = True
    
    def stop(self):
        """إيقاف محرك التداول"""
        self.is_running = False
    
    def update_market_price(self, symbol: str, price: float, timestamp: datetime = None):
        """
        تحديث سعر السوق
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        with self._lock:
            if symbol not in self.market_data:
                self.market_data[symbol] = {}
            
            self.market_data[symbol].update({
                'price': price,
                'timestamp': timestamp
            })
            
            # تحديث المراكز المفتوحة
            self._update_positions(symbol, price)
            
            # فحص الأوامر المعلقة
            self._check_pending_orders(symbol, price)
    
    def place_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                   quantity: float, price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Tuple[bool, str, Optional[str]]:
        """
        وضع أمر جديد
        """
        if not self.is_running:
            return False, "محرك التداول متوقف", None
        
        # إنشاء الأمر
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        # التحقق من صحة الأمر
        is_valid, error_msg = self.risk_manager.validate_order(
            order, self.current_balance, list(self.positions.values())
        )
        
        if not is_valid:
            return False, error_msg, None
        
        with self._lock:
            self.orders[order.id] = order
            
            # تنفيذ الأمر إذا كان من نوع السوق
            if order_type == OrderType.MARKET:
                self._execute_market_order(order)
            
            return True, "تم وضع الأمر بنجاح", order.id
    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """
        إلغاء أمر
        """
        with self._lock:
            if order_id not in self.orders:
                return False, "الأمر غير موجود"
            
            order = self.orders[order_id]
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                return False, "لا يمكن إلغاء الأمر"
            
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.utcnow()
            
            return True, "تم إلغاء الأمر"
    
    def close_position(self, position_id: str, quantity: Optional[float] = None) -> Tuple[bool, str]:
        """
        إغلاق مركز (كلي أو جزئي)
        """
        with self._lock:
            if position_id not in self.positions:
                return False, "المركز غير موجود"
            
            position = self.positions[position_id]
            close_quantity = quantity or position.quantity
            
            if close_quantity > position.quantity:
                return False, "الكمية المطلوب إغلاقها أكبر من المركز"
            
            # تحديد جهة أمر الإغلاق
            close_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
            
            # وضع أمر إغلاق
            success, message, order_id = self.place_order(
                position.symbol, close_side, OrderType.MARKET, close_quantity
            )
            
            return success, message
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        ملخص الحساب
        """
        with self._lock:
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            total_realized_pnl = sum(trade.price * trade.quantity for trade in self.trades)
            
            return {
                "initial_balance": self.initial_balance,
                "current_balance": self.current_balance,
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_realized_pnl": total_realized_pnl,
                "total_equity": self.current_balance + total_unrealized_pnl,
                "open_positions": len(self.positions),
                "pending_orders": len([o for o in self.orders.values() if o.status == OrderStatus.PENDING]),
                "total_trades": len(self.trades)
            }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        الحصول على المراكز المفتوحة
        """
        with self._lock:
            return [asdict(pos) for pos in self.positions.values()]
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Dict[str, Any]]:
        """
        الحصول على الأوامر
        """
        with self._lock:
            orders = list(self.orders.values())
            
            if status:
                orders = [o for o in orders if o.status == status]
            
            return [asdict(order) for order in orders]
    
    def get_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        الحصول على الصفقات
        """
        with self._lock:
            trades = self.trades
            
            if symbol:
                trades = [t for t in trades if t.symbol == symbol]
            
            # ترتيب حسب التاريخ (الأحدث أولاً)
            trades = sorted(trades, key=lambda x: x.timestamp, reverse=True)
            
            return [asdict(trade) for trade in trades[:limit]]
    
    def _execute_market_order(self, order: Order):
        """
        تنفيذ أمر السوق
        """
        if order.symbol not in self.market_data:
            order.status = OrderStatus.REJECTED
            return
        
        current_price = self.market_data[order.symbol]['price']
        
        # تنفيذ الأمر
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_price = current_price
        order.updated_at = datetime.utcnow()
        
        # إنشاء صفقة
        trade = Trade(
            id=str(uuid.uuid4()),
            order_id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=current_price
        )
        
        self.trades.append(trade)
        
        # تحديث المراكز
        self._update_position_from_trade(trade)
        
        # تحديث الرصيد
        trade_value = trade.quantity * trade.price
        if trade.side == OrderSide.BUY:
            self.current_balance -= trade_value
        else:
            self.current_balance += trade_value
    
    def _update_position_from_trade(self, trade: Trade):
        """
        تحديث المراكز من الصفقة
        """
        symbol = trade.symbol
        
        # البحث عن مركز موجود
        existing_position = None
        for pos in self.positions.values():
            if pos.symbol == symbol:
                existing_position = pos
                break
        
        if existing_position is None:
            # إنشاء مركز جديد
            position_side = PositionSide.LONG if trade.side == OrderSide.BUY else PositionSide.SHORT
            
            position = Position(
                id=str(uuid.uuid4()),
                symbol=symbol,
                side=position_side,
                quantity=trade.quantity,
                entry_price=trade.price,
                current_price=trade.price
            )
            
            self.positions[position.id] = position
        else:
            # تحديث المركز الموجود
            if ((existing_position.side == PositionSide.LONG and trade.side == OrderSide.BUY) or
                (existing_position.side == PositionSide.SHORT and trade.side == OrderSide.SELL)):
                # زيادة المركز
                total_value = (existing_position.quantity * existing_position.entry_price + 
                              trade.quantity * trade.price)
                total_quantity = existing_position.quantity + trade.quantity
                existing_position.entry_price = total_value / total_quantity
                existing_position.quantity = total_quantity
            else:
                # تقليل المركز أو إغلاقه
                if trade.quantity >= existing_position.quantity:
                    # إغلاق المركز
                    del self.positions[existing_position.id]
                else:
                    # تقليل المركز
                    existing_position.quantity -= trade.quantity
            
            existing_position.updated_at = datetime.utcnow()
    
    def _update_positions(self, symbol: str, current_price: float):
        """
        تحديث المراكز بالأسعار الحالية
        """
        for position in self.positions.values():
            if position.symbol == symbol:
                position.current_price = current_price
                
                # حساب الربح/الخسارة غير المحققة
                if position.side == PositionSide.LONG:
                    position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
                else:
                    position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
                
                position.updated_at = datetime.utcnow()
    
    def _check_pending_orders(self, symbol: str, current_price: float):
        """
        فحص الأوامر المعلقة وتنفيذها إذا لزم الأمر
        """
        for order in self.orders.values():
            if (order.symbol == symbol and 
                order.status == OrderStatus.PENDING):
                
                should_execute = False
                
                if order.type == OrderType.LIMIT:
                    if ((order.side == OrderSide.BUY and current_price <= order.price) or
                        (order.side == OrderSide.SELL and current_price >= order.price)):
                        should_execute = True
                
                elif order.type == OrderType.STOP:
                    if ((order.side == OrderSide.BUY and current_price >= order.stop_price) or
                        (order.side == OrderSide.SELL and current_price <= order.stop_price)):
                        should_execute = True
                
                if should_execute:
                    self._execute_market_order(order)


class DonchianBreakoutStrategy:
    """
    استراتيجية Donchian Breakout
    """
    
    def __init__(self, period: int = 20, risk_reward_ratio: float = 2.0):
        self.period = period
        self.risk_reward_ratio = risk_reward_ratio
        self.price_history: Dict[str, List[float]] = {}
    
    def update_price(self, symbol: str, price: float):
        """
        تحديث تاريخ الأسعار
        """
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        
        # الاحتفاظ بالفترة المطلوبة فقط
        if len(self.price_history[symbol]) > self.period:
            self.price_history[symbol] = self.price_history[symbol][-self.period:]
    
    def get_signal(self, symbol: str, current_price: float) -> Optional[Dict[str, Any]]:
        """
        الحصول على إشارة التداول
        """
        if (symbol not in self.price_history or 
            len(self.price_history[symbol]) < self.period):
            return None
        
        prices = self.price_history[symbol]
        
        # حساب أعلى وأقل سعر في الفترة
        highest_high = max(prices)
        lowest_low = min(prices)
        
        signal = None
        
        # إشارة شراء - كسر أعلى سعر
        if current_price > highest_high:
            stop_loss = lowest_low
            take_profit = current_price + (current_price - stop_loss) * self.risk_reward_ratio
            
            signal = {
                "action": "buy",
                "entry_price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "confidence": self._calculate_confidence(prices, current_price, "buy")
            }
        
        # إشارة بيع - كسر أقل سعر
        elif current_price < lowest_low:
            stop_loss = highest_high
            take_profit = current_price - (stop_loss - current_price) * self.risk_reward_ratio
            
            signal = {
                "action": "sell",
                "entry_price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "confidence": self._calculate_confidence(prices, current_price, "sell")
            }
        
        return signal
    
    def _calculate_confidence(self, prices: List[float], current_price: float, action: str) -> float:
        """
        حساب مستوى الثقة في الإشارة
        """
        # حساب بسيط لمستوى الثقة بناءً على قوة الكسر
        if action == "buy":
            highest = max(prices)
            breakout_strength = (current_price - highest) / highest
        else:
            lowest = min(prices)
            breakout_strength = (lowest - current_price) / lowest
        
        # تحويل إلى نسبة مئوية وتحديد مستوى الثقة
        confidence = min(max(breakout_strength * 100, 0.3), 0.9)
        
        return confidence

