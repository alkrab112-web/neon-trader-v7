"""
مسارات API للمساعد الذكي
"""

from flask import Blueprint, request, jsonify
from src.models.ai_assistant import AIAssistant, MarketSignal, DailyPlan
from src.models.auth import require_auth
import asyncio
import json
from datetime import datetime

ai_bp = Blueprint('ai', __name__)
assistant = AIAssistant()

@ai_bp.route('/daily-plan', methods=['GET'])
@require_auth
def get_daily_plan():
    """الحصول على الخطة اليومية"""
    try:
        symbols = request.args.getlist('symbols')
        if not symbols:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
        
        # تشغيل الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            plan = loop.run_until_complete(assistant.generate_daily_plan(symbols))
            
            return jsonify({
                'success': True,
                'plan': {
                    'date': plan.date,
                    'market_outlook': plan.market_outlook,
                    'key_levels': plan.key_levels,
                    'opportunities': plan.opportunities,
                    'risks': plan.risks,
                    'recommendations': plan.recommendations
                }
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في توليد الخطة اليومية: {str(e)}'
        }), 500

@ai_bp.route('/analyze-opportunity', methods=['POST'])
@require_auth
def analyze_opportunity():
    """تحليل فرصة التداول"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'رمز العملة مطلوب'
            }), 400
        
        # تشغيل الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            signal = loop.run_until_complete(
                assistant.analyze_trading_opportunity(symbol, timeframe)
            )
            
            return jsonify({
                'success': True,
                'signal': {
                    'symbol': signal.symbol,
                    'action': signal.action,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'reasoning': signal.reasoning,
                    'timestamp': signal.timestamp.isoformat()
                }
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في تحليل الفرصة: {str(e)}'
        }), 500

@ai_bp.route('/market-insights', methods=['GET'])
@require_auth
def get_market_insights():
    """الحصول على رؤى السوق"""
    try:
        symbols = request.args.getlist('symbols')
        if not symbols:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        # تشغيل الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            insights = loop.run_until_complete(assistant.get_market_insights(symbols))
            
            return jsonify({
                'success': True,
                'insights': insights
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الحصول على رؤى السوق: {str(e)}'
        }), 500

@ai_bp.route('/portfolio-risk', methods=['POST'])
@require_auth
def evaluate_portfolio_risk():
    """تقييم مخاطر المحفظة"""
    try:
        data = request.get_json()
        positions = data.get('positions', [])
        
        # تشغيل الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            risk_analysis = loop.run_until_complete(
                assistant.evaluate_portfolio_risk(positions)
            )
            
            return jsonify({
                'success': True,
                'risk_analysis': risk_analysis
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في تقييم مخاطر المحفظة: {str(e)}'
        }), 500

@ai_bp.route('/recommendations', methods=['GET'])
@require_auth
def get_recommendations():
    """الحصول على التوصيات الحالية"""
    try:
        # الحصول على التوصيات للرموز الرئيسية
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
        recommendations = []
        
        # تشغيل الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for symbol in symbols:
                signal = loop.run_until_complete(
                    assistant.analyze_trading_opportunity(symbol)
                )
                
                if signal.action != 'hold' and signal.confidence > 0.6:
                    recommendations.append({
                        'symbol': signal.symbol,
                        'action': signal.action,
                        'confidence': signal.confidence,
                        'entry_price': signal.entry_price,
                        'reasoning': signal.reasoning,
                        'timestamp': signal.timestamp.isoformat()
                    })
            
            return jsonify({
                'success': True,
                'recommendations': recommendations
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الحصول على التوصيات: {str(e)}'
        }), 500

@ai_bp.route('/chat', methods=['POST'])
@require_auth
def chat_with_assistant():
    """الدردشة مع المساعد الذكي"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'الرسالة مطلوبة'
            }), 400
        
        # معالجة الرسالة وإرجاع رد
        response = process_chat_message(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في معالجة الرسالة: {str(e)}'
        }), 500

@ai_bp.route('/strategy/signals', methods=['GET'])
@require_auth
def get_strategy_signals():
    """الحصول على إشارات الاستراتيجية"""
    try:
        strategy = request.args.get('strategy', 'donchian_breakout')
        symbols = request.args.getlist('symbols')
        
        if not symbols:
            symbols = ['BTCUSDT', 'ETHUSDT']
        
        signals = []
        
        # تشغيل الدالة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for symbol in symbols:
                signal = loop.run_until_complete(
                    assistant.analyze_trading_opportunity(symbol)
                )
                
                signals.append({
                    'symbol': signal.symbol,
                    'action': signal.action,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'reasoning': signal.reasoning,
                    'strategy': strategy,
                    'timestamp': signal.timestamp.isoformat()
                })
            
            return jsonify({
                'success': True,
                'strategy': strategy,
                'signals': signals
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطأ في الحصول على إشارات الاستراتيجية: {str(e)}'
        }), 500

def process_chat_message(message: str) -> str:
    """معالجة رسالة الدردشة"""
    message_lower = message.lower()
    
    # ردود بسيطة للأسئلة الشائعة
    if 'سعر' in message_lower and 'بتكوين' in message_lower:
        return "سعر البيتكوين الحالي حوالي $45,000. يمكنك مراقبة الأسعار في الوقت الفعلي من خلال لوحة التحكم."
    
    elif 'توصية' in message_lower or 'نصيحة' in message_lower:
        return "أنصحك بمراجعة الخطة اليومية والتوصيات الحالية. تذكر دائماً استخدام إدارة المخاطر المناسبة."
    
    elif 'مخاطر' in message_lower:
        return "إدارة المخاطر أهم من الأرباح. استخدم دائماً وقف الخسارة ولا تخاطر بأكثر من 2% من رأس المال في صفقة واحدة."
    
    elif 'استراتيجية' in message_lower:
        return "نستخدم استراتيجية Donchian Breakout مع تحليل الذكاء الاصطناعي. يمكنك مراجعة الإشارات في قسم المساعد الذكي."
    
    elif 'مساعدة' in message_lower or 'help' in message_lower:
        return """يمكنني مساعدتك في:
        
• تحليل الأسواق والأسعار
• تقديم توصيات التداول
• إدارة المخاطر
• شرح الاستراتيجيات
• الإجابة على أسئلة التداول

ما الذي تريد معرفته؟"""
    
    else:
        return "شكراً لرسالتك. يمكنني مساعدتك في أمور التداول والتحليل. اكتب 'مساعدة' لمعرفة ما يمكنني فعله."

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """فحص صحة المساعد الذكي"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'daily_plan',
            'market_analysis',
            'trading_signals',
            'risk_assessment',
            'chat_support'
        ]
    })

