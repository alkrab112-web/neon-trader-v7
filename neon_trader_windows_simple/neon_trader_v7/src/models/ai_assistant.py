"""
نموذج المساعد الذكي لـ Neon Trader V7
يوفر تحليل السوق والتوصيات والخطط اليومية
"""

import os
import json
import openai
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import logging

# إعداد OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')

@dataclass
class MarketSignal:
    """إشارة السوق"""
    symbol: str
    action: str  # buy, sell, hold
    confidence: float  # 0-1
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timestamp: datetime

@dataclass
class DailyPlan:
    """الخطة اليومية"""
    date: str
    market_outlook: str
    key_levels: Dict[str, Dict[str, float]]
    opportunities: List[Dict]
    risks: List[str]
    recommendations: List[str]

class AIAssistant:
    """المساعد الذكي للتداول"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_data = {}
        self.user_preferences = {}
        self.trading_history = []
        
    async def generate_daily_plan(self, symbols: List[str] = None) -> DailyPlan:
        """توليد الخطة اليومية"""
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
        
        try:
            # جمع بيانات السوق
            market_analysis = await self._analyze_market_conditions(symbols)
            
            # توليد الخطة باستخدام GPT
            plan_prompt = self._create_daily_plan_prompt(market_analysis, symbols)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": plan_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            plan_data = self._parse_daily_plan_response(response.choices[0].message.content)
            
            return DailyPlan(
                date=datetime.now().strftime('%Y-%m-%d'),
                market_outlook=plan_data.get('market_outlook', 'محايد'),
                key_levels=plan_data.get('key_levels', {}),
                opportunities=plan_data.get('opportunities', []),
                risks=plan_data.get('risks', []),
                recommendations=plan_data.get('recommendations', [])
            )
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد الخطة اليومية: {e}")
            return self._get_fallback_daily_plan()
    
    async def analyze_trading_opportunity(self, symbol: str, timeframe: str = '1h') -> MarketSignal:
        """تحليل فرصة التداول"""
        try:
            # جمع البيانات التقنية
            technical_data = await self._get_technical_analysis(symbol, timeframe)
            
            # تحليل المشاعر
            sentiment_data = await self._analyze_market_sentiment(symbol)
            
            # توليد الإشارة باستخدام الذكاء الاصطناعي
            signal_prompt = self._create_signal_analysis_prompt(
                symbol, technical_data, sentiment_data
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_trading_system_prompt()},
                    {"role": "user", "content": signal_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            signal_data = self._parse_signal_response(response.choices[0].message.content)
            
            return MarketSignal(
                symbol=symbol,
                action=signal_data.get('action', 'hold'),
                confidence=signal_data.get('confidence', 0.5),
                entry_price=signal_data.get('entry_price', 0),
                stop_loss=signal_data.get('stop_loss', 0),
                take_profit=signal_data.get('take_profit', 0),
                reasoning=signal_data.get('reasoning', 'تحليل تلقائي'),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"خطأ في تحليل فرصة التداول لـ {symbol}: {e}")
            return self._get_fallback_signal(symbol)
    
    async def get_market_insights(self, symbols: List[str]) -> Dict:
        """الحصول على رؤى السوق"""
        try:
            insights = {}
            
            for symbol in symbols:
                # تحليل الاتجاه
                trend_analysis = await self._analyze_trend(symbol)
                
                # تحليل الدعم والمقاومة
                support_resistance = await self._find_support_resistance(symbol)
                
                # تحليل الحجم
                volume_analysis = await self._analyze_volume(symbol)
                
                insights[symbol] = {
                    'trend': trend_analysis,
                    'support_resistance': support_resistance,
                    'volume': volume_analysis,
                    'recommendation': await self._get_symbol_recommendation(symbol)
                }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على رؤى السوق: {e}")
            return {}
    
    async def evaluate_portfolio_risk(self, positions: List[Dict]) -> Dict:
        """تقييم مخاطر المحفظة"""
        try:
            if not positions:
                return {
                    'risk_level': 'منخفض',
                    'diversification_score': 1.0,
                    'recommendations': ['لا توجد مراكز مفتوحة']
                }
            
            # حساب التنويع
            diversification_score = self._calculate_diversification(positions)
            
            # حساب التعرض للمخاطر
            risk_exposure = self._calculate_risk_exposure(positions)
            
            # تحليل الارتباط
            correlation_analysis = await self._analyze_correlations(positions)
            
            # توليد التوصيات
            risk_prompt = self._create_risk_analysis_prompt(
                positions, diversification_score, risk_exposure, correlation_analysis
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_risk_system_prompt()},
                    {"role": "user", "content": risk_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            risk_data = self._parse_risk_response(response.choices[0].message.content)
            
            return {
                'risk_level': risk_data.get('risk_level', 'متوسط'),
                'diversification_score': diversification_score,
                'risk_exposure': risk_exposure,
                'correlation_analysis': correlation_analysis,
                'recommendations': risk_data.get('recommendations', []),
                'suggested_actions': risk_data.get('suggested_actions', [])
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تقييم مخاطر المحفظة: {e}")
            return {'risk_level': 'غير محدد', 'recommendations': ['خطأ في التحليل']}
    
    def _get_system_prompt(self) -> str:
        """النص التوجيهي للنظام"""
        return """أنت مساعد ذكي متخصص في التداول والتحليل المالي. مهمتك هي:

1. تحليل أسواق العملات المشفرة والفوركس والأسهم
2. تقديم توصيات تداول مدروسة ومبررة
3. إنشاء خطط يومية شاملة للتداول
4. تقييم المخاطر وإدارة المحفظة
5. تقديم رؤى تقنية وأساسية

يجب أن تكون إجاباتك:
- دقيقة ومبنية على التحليل
- واضحة ومفهومة
- تتضمن مستويات المخاطرة
- تراعي إدارة رأس المال
- باللغة العربية

تذكر: التداول ينطوي على مخاطر، وجميع التوصيات هي لأغراض تعليمية."""
    
    def _get_trading_system_prompt(self) -> str:
        """النص التوجيهي لتحليل التداول"""
        return """أنت محلل تقني متخصص في إشارات التداول. عند تحليل الفرص:

1. استخدم التحليل التقني والأساسي
2. حدد نقاط الدخول والخروج بدقة
3. احسب نسبة المخاطرة إلى العائد
4. قدم مبررات واضحة للتوصية
5. حدد مستوى الثقة في الإشارة

تنسيق الإجابة:
- الإجراء: شراء/بيع/انتظار
- مستوى الثقة: 0-100%
- سعر الدخول: [السعر]
- وقف الخسارة: [السعر]
- جني الأرباح: [السعر]
- المبرر: [التفسير]"""
    
    def _get_risk_system_prompt(self) -> str:
        """النص التوجيهي لتحليل المخاطر"""
        return """أنت خبير في إدارة المخاطر المالية. عند تقييم المحفظة:

1. حلل مستوى التنويع
2. قيم التعرض للمخاطر
3. احسب الارتباطات بين الأصول
4. قدم توصيات لتحسين المحفظة
5. حدد المخاطر المحتملة

ركز على:
- الحفاظ على رأس المال
- تحسين نسبة المخاطرة/العائد
- التنويع الفعال
- إدارة الحجم المناسب"""
    
    async def _analyze_market_conditions(self, symbols: List[str]) -> Dict:
        """تحليل ظروف السوق"""
        # محاكاة تحليل السوق
        market_conditions = {
            'overall_trend': 'صاعد' if np.random.random() > 0.5 else 'هابط',
            'volatility': np.random.uniform(0.1, 0.8),
            'volume_trend': 'متزايد' if np.random.random() > 0.5 else 'متناقص',
            'sentiment': np.random.choice(['إيجابي', 'محايد', 'سلبي']),
            'symbols_analysis': {}
        }
        
        for symbol in symbols:
            market_conditions['symbols_analysis'][symbol] = {
                'price': np.random.uniform(20000, 50000) if 'BTC' in symbol else np.random.uniform(1000, 4000),
                'change_24h': np.random.uniform(-10, 10),
                'volume_24h': np.random.uniform(1000000, 10000000),
                'rsi': np.random.uniform(20, 80),
                'macd_signal': np.random.choice(['صاعد', 'هابط', 'محايد'])
            }
        
        return market_conditions
    
    async def _get_technical_analysis(self, symbol: str, timeframe: str) -> Dict:
        """الحصول على التحليل التقني"""
        # محاكاة البيانات التقنية
        return {
            'rsi': np.random.uniform(20, 80),
            'macd': {
                'macd': np.random.uniform(-100, 100),
                'signal': np.random.uniform(-100, 100),
                'histogram': np.random.uniform(-50, 50)
            },
            'bollinger_bands': {
                'upper': np.random.uniform(45000, 50000),
                'middle': np.random.uniform(40000, 45000),
                'lower': np.random.uniform(35000, 40000)
            },
            'moving_averages': {
                'sma_20': np.random.uniform(40000, 45000),
                'sma_50': np.random.uniform(38000, 43000),
                'ema_12': np.random.uniform(41000, 46000),
                'ema_26': np.random.uniform(39000, 44000)
            },
            'support_resistance': {
                'support': np.random.uniform(35000, 40000),
                'resistance': np.random.uniform(45000, 50000)
            }
        }
    
    async def _analyze_market_sentiment(self, symbol: str) -> Dict:
        """تحليل مشاعر السوق"""
        return {
            'fear_greed_index': np.random.uniform(0, 100),
            'social_sentiment': np.random.choice(['إيجابي', 'محايد', 'سلبي']),
            'news_sentiment': np.random.choice(['إيجابي', 'محايد', 'سلبي']),
            'whale_activity': np.random.choice(['شراء', 'بيع', 'محايد']),
            'funding_rate': np.random.uniform(-0.01, 0.01)
        }
    
    def _create_daily_plan_prompt(self, market_analysis: Dict, symbols: List[str]) -> str:
        """إنشاء نص الطلب للخطة اليومية"""
        return f"""
بناءً على تحليل السوق التالي، أنشئ خطة تداول يومية شاملة:

تحليل السوق:
- الاتجاه العام: {market_analysis['overall_trend']}
- التقلبات: {market_analysis['volatility']:.2f}
- اتجاه الحجم: {market_analysis['volume_trend']}
- المشاعر العامة: {market_analysis['sentiment']}

الرموز المراقبة: {', '.join(symbols)}

يرجى تقديم:
1. نظرة عامة على السوق
2. المستويات المهمة لكل رمز
3. الفرص المتاحة
4. المخاطر المحتملة
5. التوصيات العامة

تنسيق الإجابة بـ JSON:
{{
    "market_outlook": "...",
    "key_levels": {{"BTCUSDT": {{"support": 0, "resistance": 0}}}},
    "opportunities": [{{"symbol": "...", "description": "...", "probability": 0}}],
    "risks": ["..."],
    "recommendations": ["..."]
}}
"""
    
    def _create_signal_analysis_prompt(self, symbol: str, technical_data: Dict, sentiment_data: Dict) -> str:
        """إنشاء نص الطلب لتحليل الإشارة"""
        return f"""
حلل فرصة التداول لـ {symbol} بناءً على البيانات التالية:

التحليل التقني:
- RSI: {technical_data['rsi']:.2f}
- MACD: {technical_data['macd']['macd']:.2f}
- إشارة MACD: {technical_data['macd']['signal']:.2f}
- الدعم: {technical_data['support_resistance']['support']:.2f}
- المقاومة: {technical_data['support_resistance']['resistance']:.2f}

تحليل المشاعر:
- مؤشر الخوف والطمع: {sentiment_data['fear_greed_index']:.2f}
- المشاعر الاجتماعية: {sentiment_data['social_sentiment']}
- نشاط الحيتان: {sentiment_data['whale_activity']}

قدم توصية تداول مع:
- الإجراء المطلوب
- مستوى الثقة
- نقاط الدخول والخروج
- المبررات

تنسيق JSON:
{{
    "action": "buy/sell/hold",
    "confidence": 0.0-1.0,
    "entry_price": 0,
    "stop_loss": 0,
    "take_profit": 0,
    "reasoning": "..."
}}
"""
    
    def _create_risk_analysis_prompt(self, positions: List[Dict], diversification: float, 
                                   risk_exposure: float, correlations: Dict) -> str:
        """إنشاء نص الطلب لتحليل المخاطر"""
        positions_summary = []
        for pos in positions:
            positions_summary.append(f"- {pos['symbol']}: {pos['side']} {pos['quantity']} @ {pos['entry_price']}")
        
        return f"""
قيم مخاطر المحفظة التالية:

المراكز المفتوحة:
{chr(10).join(positions_summary)}

مقاييس المخاطر:
- نقاط التنويع: {diversification:.2f}
- التعرض للمخاطر: {risk_exposure:.2f}%
- الارتباطات: {correlations}

قدم تقييماً شاملاً يتضمن:
- مستوى المخاطر العام
- نقاط القوة والضعف
- توصيات التحسين
- إجراءات مقترحة

تنسيق JSON:
{{
    "risk_level": "منخفض/متوسط/عالي",
    "recommendations": ["..."],
    "suggested_actions": ["..."]
}}
"""
    
    def _parse_daily_plan_response(self, response: str) -> Dict:
        """تحليل استجابة الخطة اليومية"""
        try:
            # محاولة تحليل JSON
            return json.loads(response)
        except:
            # في حالة فشل التحليل، إرجاع بيانات افتراضية
            return {
                'market_outlook': 'تحليل السوق غير متاح',
                'key_levels': {},
                'opportunities': [],
                'risks': ['خطأ في تحليل البيانات'],
                'recommendations': ['يرجى المحاولة مرة أخرى']
            }
    
    def _parse_signal_response(self, response: str) -> Dict:
        """تحليل استجابة الإشارة"""
        try:
            return json.loads(response)
        except:
            return {
                'action': 'hold',
                'confidence': 0.5,
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0,
                'reasoning': 'خطأ في تحليل الإشارة'
            }
    
    def _parse_risk_response(self, response: str) -> Dict:
        """تحليل استجابة المخاطر"""
        try:
            return json.loads(response)
        except:
            return {
                'risk_level': 'متوسط',
                'recommendations': ['خطأ في تحليل المخاطر'],
                'suggested_actions': ['يرجى المحاولة مرة أخرى']
            }
    
    def _get_fallback_daily_plan(self) -> DailyPlan:
        """خطة يومية احتياطية"""
        return DailyPlan(
            date=datetime.now().strftime('%Y-%m-%d'),
            market_outlook='السوق في حالة تذبذب، يُنصح بالحذر',
            key_levels={
                'BTCUSDT': {'support': 42000, 'resistance': 48000},
                'ETHUSDT': {'support': 2800, 'resistance': 3200}
            },
            opportunities=[
                {
                    'symbol': 'BTCUSDT',
                    'description': 'فرصة شراء عند كسر مستوى 45000',
                    'probability': 0.6
                }
            ],
            risks=['تقلبات عالية في السوق', 'أخبار اقتصادية مهمة'],
            recommendations=[
                'استخدم إدارة مخاطر صارمة',
                'راقب الأخبار الاقتصادية',
                'لا تتداول بأكثر من 2% من رأس المال'
            ]
        )
    
    def _get_fallback_signal(self, symbol: str) -> MarketSignal:
        """إشارة احتياطية"""
        return MarketSignal(
            symbol=symbol,
            action='hold',
            confidence=0.5,
            entry_price=0,
            stop_loss=0,
            take_profit=0,
            reasoning='تحليل غير متاح حالياً',
            timestamp=datetime.now()
        )
    
    async def _analyze_trend(self, symbol: str) -> str:
        """تحليل الاتجاه"""
        return np.random.choice(['صاعد قوي', 'صاعد', 'محايد', 'هابط', 'هابط قوي'])
    
    async def _find_support_resistance(self, symbol: str) -> Dict:
        """العثور على الدعم والمقاومة"""
        base_price = 45000 if 'BTC' in symbol else 3000
        return {
            'support': base_price * 0.9,
            'resistance': base_price * 1.1,
            'pivot': base_price
        }
    
    async def _analyze_volume(self, symbol: str) -> Dict:
        """تحليل الحجم"""
        return {
            'trend': np.random.choice(['متزايد', 'متناقص', 'مستقر']),
            'strength': np.random.uniform(0.3, 1.0),
            'anomaly': np.random.random() > 0.8
        }
    
    async def _get_symbol_recommendation(self, symbol: str) -> str:
        """الحصول على توصية للرمز"""
        return np.random.choice(['شراء قوي', 'شراء', 'احتفاظ', 'بيع', 'بيع قوي'])
    
    def _calculate_diversification(self, positions: List[Dict]) -> float:
        """حساب التنويع"""
        if not positions:
            return 1.0
        
        # حساب بسيط للتنويع بناءً على عدد الأصول المختلفة
        unique_symbols = len(set(pos['symbol'] for pos in positions))
        total_positions = len(positions)
        
        return min(unique_symbols / max(total_positions, 1), 1.0)
    
    def _calculate_risk_exposure(self, positions: List[Dict]) -> float:
        """حساب التعرض للمخاطر"""
        if not positions:
            return 0.0
        
        # حساب إجمالي قيمة المراكز كنسبة من رأس المال
        total_exposure = sum(
            abs(pos.get('quantity', 0) * pos.get('entry_price', 0)) 
            for pos in positions
        )
        
        # افتراض رأس مال قدره 10000
        account_balance = 10000
        return min((total_exposure / account_balance) * 100, 100)
    
    async def _analyze_correlations(self, positions: List[Dict]) -> Dict:
        """تحليل الارتباطات"""
        symbols = [pos['symbol'] for pos in positions]
        correlations = {}
        
        # محاكاة ارتباطات بين الأصول
        for i, symbol1 in enumerate(symbols):
            for symbol2 in symbols[i+1:]:
                correlation = np.random.uniform(-0.5, 0.9)
                correlations[f"{symbol1}-{symbol2}"] = correlation
        
        return correlations

