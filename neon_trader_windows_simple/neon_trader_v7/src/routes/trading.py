"""
مسارات API للتداول
"""

from flask import Blueprint, request, jsonify, current_app
from src.models.auth import require_auth
from src.models.trading_engine import (
    PaperTradingEngine, OrderType, OrderSide, OrderStatus,
    DonchianBreakoutStrategy
)
from datetime import datetime
import json

trading_bp = Blueprint('trading', __name__)


def get_trading_engine(user_id: int) -> PaperTradingEngine:
    """
    الحصول على محرك التداول للمستخدم
    """
    engine_key = f'TRADING_ENGINE_{user_id}'
    
    if engine_key not in current_app.config:
        # إنشاء محرك تداول جديد
        engine = PaperTradingEngine(initial_balance=10000.0)
        engine.start()
        current_app.config[engine_key] = engine
    
    return current_app.config[engine_key]


def get_strategy(user_id: int) -> DonchianBreakoutStrategy:
    """
    الحصول على استراتيجية التداول للمستخدم
    """
    strategy_key = f'STRATEGY_{user_id}'
    
    if strategy_key not in current_app.config:
        strategy = DonchianBreakoutStrategy(period=20, risk_reward_ratio=2.0)
        current_app.config[strategy_key] = strategy
    
    return current_app.config[strategy_key]


@trading_bp.route('/account', methods=['GET'])
@require_auth
def get_account():
    """
    الحصول على ملخص الحساب
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        account_summary = engine.get_account_summary()
        
        return jsonify(account_summary), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/positions', methods=['GET'])
@require_auth
def get_positions():
    """
    الحصول على المراكز المفتوحة
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        positions = engine.get_positions()
        
        return jsonify({"positions": positions}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/orders', methods=['GET'])
@require_auth
def get_orders():
    """
    الحصول على الأوامر
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        status_param = request.args.get('status')
        status = None
        
        if status_param:
            try:
                status = OrderStatus(status_param)
            except ValueError:
                return jsonify({"error": "حالة الأمر غير صالحة"}), 400
        
        orders = engine.get_orders(status)
        
        return jsonify({"orders": orders}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/trades', methods=['GET'])
@require_auth
def get_trades():
    """
    الحصول على الصفقات
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 100))
        
        trades = engine.get_trades(symbol, limit)
        
        return jsonify({"trades": trades}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/place-order', methods=['POST'])
@require_auth
def place_order():
    """
    وضع أمر جديد
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        symbol = data.get('symbol')
        side = data.get('side')
        order_type = data.get('type')
        quantity = data.get('quantity')
        price = data.get('price')
        stop_price = data.get('stop_price')
        
        if not all([symbol, side, order_type, quantity]):
            return jsonify({"error": "الحقول المطلوبة: symbol, side, type, quantity"}), 400
        
        try:
            side_enum = OrderSide(side)
            type_enum = OrderType(order_type)
            quantity = float(quantity)
            price = float(price) if price else None
            stop_price = float(stop_price) if stop_price else None
        except (ValueError, TypeError):
            return jsonify({"error": "قيم الحقول غير صالحة"}), 400
        
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        success, message, order_id = engine.place_order(
            symbol, side_enum, type_enum, quantity, price, stop_price
        )
        
        if success:
            return jsonify({
                "message": message,
                "order_id": order_id
            }), 201
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/cancel-order/<order_id>', methods=['POST'])
@require_auth
def cancel_order(order_id):
    """
    إلغاء أمر
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        success, message = engine.cancel_order(order_id)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/close-position/<position_id>', methods=['POST'])
@require_auth
def close_position(position_id):
    """
    إغلاق مركز
    """
    try:
        data = request.get_json() or {}
        quantity = data.get('quantity')
        
        if quantity:
            try:
                quantity = float(quantity)
            except (ValueError, TypeError):
                return jsonify({"error": "كمية الإغلاق غير صالحة"}), 400
        
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        success, message = engine.close_position(position_id, quantity)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/update-price', methods=['POST'])
@require_auth
def update_market_price():
    """
    تحديث سعر السوق (للاختبار)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        symbol = data.get('symbol')
        price = data.get('price')
        
        if not symbol or not price:
            return jsonify({"error": "الرمز والسعر مطلوبان"}), 400
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            return jsonify({"error": "السعر غير صالح"}), 400
        
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        strategy = get_strategy(user_id)
        
        # تحديث السعر في المحرك
        engine.update_market_price(symbol, price)
        
        # تحديث السعر في الاستراتيجية
        strategy.update_price(symbol, price)
        
        return jsonify({"message": "تم تحديث السعر"}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/strategy/signal/<symbol>', methods=['GET'])
@require_auth
def get_strategy_signal(symbol):
    """
    الحصول على إشارة الاستراتيجية
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        strategy = get_strategy(user_id)
        
        # الحصول على السعر الحالي
        if symbol not in engine.market_data:
            return jsonify({"error": "لا توجد بيانات سوق لهذا الرمز"}), 404
        
        current_price = engine.market_data[symbol]['price']
        
        # الحصول على الإشارة
        signal = strategy.get_signal(symbol, current_price)
        
        if signal:
            return jsonify({"signal": signal}), 200
        else:
            return jsonify({"signal": None, "message": "لا توجد إشارة حالياً"}), 200
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/strategy/execute-signal', methods=['POST'])
@require_auth
def execute_strategy_signal():
    """
    تنفيذ إشارة الاستراتيجية
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({"error": "الرمز مطلوب"}), 400
        
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        strategy = get_strategy(user_id)
        
        # الحصول على السعر الحالي
        if symbol not in engine.market_data:
            return jsonify({"error": "لا توجد بيانات سوق لهذا الرمز"}), 404
        
        current_price = engine.market_data[symbol]['price']
        
        # الحصول على الإشارة
        signal = strategy.get_signal(symbol, current_price)
        
        if not signal:
            return jsonify({"error": "لا توجد إشارة للتنفيذ"}), 400
        
        # حساب حجم المركز
        account_summary = engine.get_account_summary()
        position_size = engine.risk_manager.calculate_position_size(
            account_summary["current_balance"],
            signal["entry_price"],
            signal["stop_loss"]
        )
        
        if position_size <= 0:
            return jsonify({"error": "لا يمكن حساب حجم مركز صالح"}), 400
        
        # تنفيذ الأمر
        side = OrderSide.BUY if signal["action"] == "buy" else OrderSide.SELL
        
        success, message, order_id = engine.place_order(
            symbol, side, OrderType.MARKET, position_size
        )
        
        if success:
            # وضع أوامر إيقاف الخسارة وجني الأرباح
            stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
            
            # أمر إيقاف الخسارة
            engine.place_order(
                symbol, stop_side, OrderType.STOP, position_size, 
                stop_price=signal["stop_loss"]
            )
            
            # أمر جني الأرباح
            engine.place_order(
                symbol, stop_side, OrderType.LIMIT, position_size,
                price=signal["take_profit"]
            )
            
            return jsonify({
                "message": "تم تنفيذ الإشارة بنجاح",
                "order_id": order_id,
                "signal": signal,
                "position_size": position_size
            }), 201
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/reset-account', methods=['POST'])
@require_auth
def reset_account():
    """
    إعادة تعيين الحساب (للاختبار)
    """
    try:
        user_id = request.current_user["user_id"]
        
        # إنشاء محرك تداول جديد
        engine = PaperTradingEngine(initial_balance=10000.0)
        engine.start()
        
        engine_key = f'TRADING_ENGINE_{user_id}'
        current_app.config[engine_key] = engine
        
        # إعادة تعيين الاستراتيجية
        strategy = DonchianBreakoutStrategy(period=20, risk_reward_ratio=2.0)
        strategy_key = f'STRATEGY_{user_id}'
        current_app.config[strategy_key] = strategy
        
        return jsonify({"message": "تم إعادة تعيين الحساب"}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/market-data/<symbol>', methods=['GET'])
@require_auth
def get_market_data(symbol):
    """
    الحصول على بيانات السوق
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        if symbol not in engine.market_data:
            return jsonify({"error": "لا توجد بيانات لهذا الرمز"}), 404
        
        market_data = engine.market_data[symbol]
        
        return jsonify({
            "symbol": symbol,
            "price": market_data["price"],
            "timestamp": market_data["timestamp"].isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@trading_bp.route('/performance', methods=['GET'])
@require_auth
def get_performance():
    """
    الحصول على إحصائيات الأداء
    """
    try:
        user_id = request.current_user["user_id"]
        engine = get_trading_engine(user_id)
        
        account_summary = engine.get_account_summary()
        trades = engine.get_trades(limit=1000)
        
        # حساب إحصائيات الأداء
        total_trades = len(trades)
        winning_trades = len([t for t in trades if float(t['price']) > 0])  # تبسيط
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_return = ((account_summary["total_equity"] - account_summary["initial_balance"]) / 
                       account_summary["initial_balance"] * 100)
        
        performance = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": round(win_rate, 2),
            "total_return": round(total_return, 2),
            "current_equity": account_summary["total_equity"],
            "max_drawdown": 0.0,  # يحتاج حساب أكثر تعقيداً
            "sharpe_ratio": 0.0   # يحتاج بيانات تاريخية
        }
        
        return jsonify({"performance": performance}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500

