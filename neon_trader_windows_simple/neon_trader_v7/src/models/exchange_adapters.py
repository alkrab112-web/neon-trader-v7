"""
محولات المنصات لـ Neon Trader V7
يوفر تكامل مع منصات التداول المختلفة
"""

import os
import json
import hmac
import hashlib
import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class OrderResult:
    """نتيجة الأمر"""
    success: bool
    order_id: Optional[str] = None
    error_message: Optional[str] = None
    filled_quantity: float = 0
    average_price: float = 0
    status: str = 'unknown'

@dataclass
class Balance:
    """رصيد العملة"""
    asset: str
    free: float
    locked: float
    total: float

@dataclass
class Position:
    """المركز"""
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float
    pnl: float
    pnl_percentage: float

class ExchangeAdapter(ABC):
    """الفئة الأساسية لمحولات المنصات"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def get_account_balance(self) -> List[Balance]:
        """الحصول على رصيد الحساب"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """الحصول على المراكز المفتوحة"""
        pass
    
    @abstractmethod
    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """وضع أمر سوق"""
        pass
    
    @abstractmethod
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> OrderResult:
        """وضع أمر محدد"""
        pass
    
    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        pass
    
    @abstractmethod
    def get_ticker_price(self, symbol: str) -> float:
        """الحصول على سعر الرمز"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """اختبار الاتصال"""
        pass

class BybitAdapter(ExchangeAdapter):
    """محول منصة Bybit"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-BAPI-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, timestamp: str, params: str) -> str:
        """توليد التوقيع"""
        param_str = timestamp + self.api_key + "5000" + params
        return hmac.new(
            bytes(self.api_secret, "utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """إجراء طلب HTTP"""
        try:
            timestamp = str(int(time.time() * 1000))
            params_str = json.dumps(params) if params else ""
            
            signature = self._generate_signature(timestamp, params_str)
            
            headers = {
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-SIGN': signature,
                'X-BAPI-RECV-WINDOW': '5000'
            }
            
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            else:
                response = self.session.post(url, json=params, headers=headers)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"خطأ في طلب Bybit: {e}")
            return {'retCode': -1, 'retMsg': str(e)}
    
    def test_connection(self) -> bool:
        """اختبار الاتصال"""
        try:
            result = self._make_request('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
            return result.get('retCode') == 0
        except:
            return False
    
    def get_account_balance(self) -> List[Balance]:
        """الحصول على رصيد الحساب"""
        try:
            result = self._make_request('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
            
            if result.get('retCode') != 0:
                self.logger.error(f"خطأ في الحصول على الرصيد: {result.get('retMsg')}")
                return []
            
            balances = []
            wallet_data = result.get('result', {}).get('list', [])
            
            if wallet_data:
                coins = wallet_data[0].get('coin', [])
                for coin in coins:
                    balance = Balance(
                        asset=coin.get('coin', ''),
                        free=float(coin.get('availableToWithdraw', 0)),
                        locked=float(coin.get('locked', 0)),
                        total=float(coin.get('walletBalance', 0))
                    )
                    balances.append(balance)
            
            return balances
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على رصيد Bybit: {e}")
            return []
    
    def get_positions(self) -> List[Position]:
        """الحصول على المراكز المفتوحة"""
        try:
            result = self._make_request('GET', '/v5/position/list', {'category': 'linear'})
            
            if result.get('retCode') != 0:
                self.logger.error(f"خطأ في الحصول على المراكز: {result.get('retMsg')}")
                return []
            
            positions = []
            position_data = result.get('result', {}).get('list', [])
            
            for pos in position_data:
                if float(pos.get('size', 0)) > 0:  # فقط المراكز المفتوحة
                    position = Position(
                        symbol=pos.get('symbol', ''),
                        side=pos.get('side', ''),
                        size=float(pos.get('size', 0)),
                        entry_price=float(pos.get('avgPrice', 0)),
                        mark_price=float(pos.get('markPrice', 0)),
                        pnl=float(pos.get('unrealisedPnl', 0)),
                        pnl_percentage=float(pos.get('unrealisedPnl', 0)) / float(pos.get('positionValue', 1)) * 100
                    )
                    positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على مراكز Bybit: {e}")
            return []
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """وضع أمر سوق"""
        try:
            params = {
                'category': 'linear',
                'symbol': symbol,
                'side': side.capitalize(),
                'orderType': 'Market',
                'qty': str(quantity)
            }
            
            result = self._make_request('POST', '/v5/order/create', params)
            
            if result.get('retCode') == 0:
                order_data = result.get('result', {})
                return OrderResult(
                    success=True,
                    order_id=order_data.get('orderId'),
                    status='submitted'
                )
            else:
                return OrderResult(
                    success=False,
                    error_message=result.get('retMsg', 'خطأ غير معروف')
                )
                
        except Exception as e:
            self.logger.error(f"خطأ في وضع أمر السوق: {e}")
            return OrderResult(success=False, error_message=str(e))
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> OrderResult:
        """وضع أمر محدد"""
        try:
            params = {
                'category': 'linear',
                'symbol': symbol,
                'side': side.capitalize(),
                'orderType': 'Limit',
                'qty': str(quantity),
                'price': str(price)
            }
            
            result = self._make_request('POST', '/v5/order/create', params)
            
            if result.get('retCode') == 0:
                order_data = result.get('result', {})
                return OrderResult(
                    success=True,
                    order_id=order_data.get('orderId'),
                    status='submitted'
                )
            else:
                return OrderResult(
                    success=False,
                    error_message=result.get('retMsg', 'خطأ غير معروف')
                )
                
        except Exception as e:
            self.logger.error(f"خطأ في وضع الأمر المحدد: {e}")
            return OrderResult(success=False, error_message=str(e))
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        try:
            params = {
                'category': 'linear',
                'symbol': symbol,
                'orderId': order_id
            }
            
            result = self._make_request('POST', '/v5/order/cancel', params)
            return result.get('retCode') == 0
            
        except Exception as e:
            self.logger.error(f"خطأ في إلغاء الأمر: {e}")
            return False
    
    def get_ticker_price(self, symbol: str) -> float:
        """الحصول على سعر الرمز"""
        try:
            result = self._make_request('GET', '/v5/market/tickers', {
                'category': 'linear',
                'symbol': symbol
            })
            
            if result.get('retCode') == 0:
                ticker_data = result.get('result', {}).get('list', [])
                if ticker_data:
                    return float(ticker_data[0].get('lastPrice', 0))
            
            return 0
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على السعر: {e}")
            return 0

class BinanceAdapter(ExchangeAdapter):
    """محول منصة Binance (للمستقبل)"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
    
    def test_connection(self) -> bool:
        """اختبار الاتصال"""
        # تنفيذ مؤقت
        return False
    
    def get_account_balance(self) -> List[Balance]:
        """الحصول على رصيد الحساب"""
        # تنفيذ مؤقت
        return []
    
    def get_positions(self) -> List[Position]:
        """الحصول على المراكز المفتوحة"""
        # تنفيذ مؤقت
        return []
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """وضع أمر سوق"""
        # تنفيذ مؤقت
        return OrderResult(success=False, error_message="غير مدعوم حالياً")
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> OrderResult:
        """وضع أمر محدد"""
        # تنفيذ مؤقت
        return OrderResult(success=False, error_message="غير مدعوم حالياً")
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        # تنفيذ مؤقت
        return False
    
    def get_ticker_price(self, symbol: str) -> float:
        """الحصول على سعر الرمز"""
        # تنفيذ مؤقت
        return 0

class ForexAdapter(ExchangeAdapter):
    """محول تداول الفوركس (للمستقبل)"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.base_url = "https://api.forex.com"  # مثال
    
    def test_connection(self) -> bool:
        """اختبار الاتصال"""
        # تنفيذ مؤقت
        return False
    
    def get_account_balance(self) -> List[Balance]:
        """الحصول على رصيد الحساب"""
        # تنفيذ مؤقت
        return []
    
    def get_positions(self) -> List[Position]:
        """الحصول على المراكز المفتوحة"""
        # تنفيذ مؤقت
        return []
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """وضع أمر سوق"""
        # تنفيذ مؤقت
        return OrderResult(success=False, error_message="غير مدعوم حالياً")
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> OrderResult:
        """وضع أمر محدد"""
        # تنفيذ مؤقت
        return OrderResult(success=False, error_message="غير مدعوم حالياً")
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        # تنفيذ مؤقت
        return False
    
    def get_ticker_price(self, symbol: str) -> float:
        """الحصول على سعر الرمز"""
        # تنفيذ مؤقت
        return 0

class StocksAdapter(ExchangeAdapter):
    """محول تداول الأسهم (للمستقبل)"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.base_url = "https://api.alpaca.markets"  # مثال
    
    def test_connection(self) -> bool:
        """اختبار الاتصال"""
        # تنفيذ مؤقت
        return False
    
    def get_account_balance(self) -> List[Balance]:
        """الحصول على رصيد الحساب"""
        # تنفيذ مؤقت
        return []
    
    def get_positions(self) -> List[Position]:
        """الحصول على المراكز المفتوحة"""
        # تنفيذ مؤقت
        return []
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """وضع أمر سوق"""
        # تنفيذ مؤقت
        return OrderResult(success=False, error_message="غير مدعوم حالياً")
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> OrderResult:
        """وضع أمر محدد"""
        # تنفيذ مؤقت
        return OrderResult(success=False, error_message="غير مدعوم حالياً")
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """إلغاء أمر"""
        # تنفيذ مؤقت
        return False
    
    def get_ticker_price(self, symbol: str) -> float:
        """الحصول على سعر الرمز"""
        # تنفيذ مؤقت
        return 0

class ExchangeManager:
    """مدير المنصات"""
    
    def __init__(self):
        self.adapters: Dict[str, ExchangeAdapter] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_exchange(self, name: str, exchange_type: str, api_key: str, 
                    api_secret: str, testnet: bool = True) -> bool:
        """إضافة منصة جديدة"""
        try:
            if exchange_type.lower() == 'bybit':
                adapter = BybitAdapter(api_key, api_secret, testnet)
            elif exchange_type.lower() == 'binance':
                adapter = BinanceAdapter(api_key, api_secret, testnet)
            elif exchange_type.lower() == 'forex':
                adapter = ForexAdapter(api_key, api_secret, testnet)
            elif exchange_type.lower() == 'stocks':
                adapter = StocksAdapter(api_key, api_secret, testnet)
            else:
                self.logger.error(f"نوع المنصة غير مدعوم: {exchange_type}")
                return False
            
            # اختبار الاتصال
            if adapter.test_connection():
                self.adapters[name] = adapter
                self.logger.info(f"تم إضافة المنصة بنجاح: {name}")
                return True
            else:
                self.logger.error(f"فشل في الاتصال بالمنصة: {name}")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في إضافة المنصة {name}: {e}")
            return False
    
    def remove_exchange(self, name: str) -> bool:
        """إزالة منصة"""
        if name in self.adapters:
            del self.adapters[name]
            self.logger.info(f"تم إزالة المنصة: {name}")
            return True
        return False
    
    def get_exchange(self, name: str) -> Optional[ExchangeAdapter]:
        """الحصول على محول المنصة"""
        return self.adapters.get(name)
    
    def list_exchanges(self) -> List[str]:
        """قائمة المنصات المتاحة"""
        return list(self.adapters.keys())
    
    def test_all_connections(self) -> Dict[str, bool]:
        """اختبار جميع الاتصالات"""
        results = {}
        for name, adapter in self.adapters.items():
            results[name] = adapter.test_connection()
        return results
    
    def get_all_balances(self) -> Dict[str, List[Balance]]:
        """الحصول على جميع الأرصدة"""
        balances = {}
        for name, adapter in self.adapters.items():
            try:
                balances[name] = adapter.get_account_balance()
            except Exception as e:
                self.logger.error(f"خطأ في الحصول على رصيد {name}: {e}")
                balances[name] = []
        return balances
    
    def get_all_positions(self) -> Dict[str, List[Position]]:
        """الحصول على جميع المراكز"""
        positions = {}
        for name, adapter in self.adapters.items():
            try:
                positions[name] = adapter.get_positions()
            except Exception as e:
                self.logger.error(f"خطأ في الحصول على مراكز {name}: {e}")
                positions[name] = []
        return positions
    
    def place_order_on_exchange(self, exchange_name: str, symbol: str, side: str, 
                               order_type: str, quantity: float, price: float = None) -> OrderResult:
        """وضع أمر على منصة محددة"""
        adapter = self.get_exchange(exchange_name)
        if not adapter:
            return OrderResult(success=False, error_message=f"المنصة غير موجودة: {exchange_name}")
        
        try:
            if order_type.lower() == 'market':
                return adapter.place_market_order(symbol, side, quantity)
            elif order_type.lower() == 'limit':
                if price is None:
                    return OrderResult(success=False, error_message="السعر مطلوب للأمر المحدد")
                return adapter.place_limit_order(symbol, side, quantity, price)
            else:
                return OrderResult(success=False, error_message=f"نوع الأمر غير مدعوم: {order_type}")
                
        except Exception as e:
            self.logger.error(f"خطأ في وضع الأمر على {exchange_name}: {e}")
            return OrderResult(success=False, error_message=str(e))
    
    def get_supported_exchanges(self) -> List[Dict[str, str]]:
        """الحصول على المنصات المدعومة"""
        return [
            {
                'type': 'bybit',
                'name': 'Bybit',
                'description': 'منصة تداول العملات المشفرة',
                'supported': True
            },
            {
                'type': 'binance',
                'name': 'Binance',
                'description': 'منصة تداول العملات المشفرة',
                'supported': False  # قيد التطوير
            },
            {
                'type': 'forex',
                'name': 'Forex',
                'description': 'تداول العملات الأجنبية',
                'supported': False  # قيد التطوير
            },
            {
                'type': 'stocks',
                'name': 'Stocks',
                'description': 'تداول الأسهم',
                'supported': False  # قيد التطوير
            }
        ]

