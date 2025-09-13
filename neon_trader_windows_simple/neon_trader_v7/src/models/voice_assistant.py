"""
نموذج المساعد الصوتي لـ Neon Trader V7
يوفر تحويل النص إلى كلام والكلام إلى نص
"""

import os
import tempfile
import subprocess
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import json

class VoiceAssistant:
    """المساعد الصوتي للتداول"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.gettempdir()
        
    def text_to_speech(self, text: str, voice_type: str = 'female_voice', 
                      language: str = 'ar') -> Optional[str]:
        """تحويل النص إلى كلام"""
        try:
            # تنظيف النص
            cleaned_text = self._clean_text_for_speech(text)
            
            # إنشاء ملف مؤقت للصوت
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_filename = f"speech_{timestamp}.wav"
            audio_path = os.path.join(self.temp_dir, audio_filename)
            
            # محاكاة تحويل النص إلى كلام
            # في التطبيق الحقيقي، يمكن استخدام خدمات مثل Google TTS أو Azure Speech
            self._generate_mock_audio(cleaned_text, audio_path, voice_type)
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"خطأ في تحويل النص إلى كلام: {e}")
            return None
    
    def speech_to_text(self, audio_file_path: str, language: str = 'ar') -> Optional[str]:
        """تحويل الكلام إلى نص"""
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"ملف الصوت غير موجود: {audio_file_path}")
            
            # محاكاة تحويل الكلام إلى نص
            # في التطبيق الحقيقي، يمكن استخدام خدمات مثل Google Speech-to-Text
            transcribed_text = self._mock_speech_recognition(audio_file_path)
            
            return transcribed_text
            
        except Exception as e:
            self.logger.error(f"خطأ في تحويل الكلام إلى نص: {e}")
            return None
    
    def generate_market_summary_audio(self, market_data: Dict[str, Any], 
                                    voice_type: str = 'female_voice') -> Optional[str]:
        """توليد ملخص صوتي للسوق"""
        try:
            # إنشاء نص الملخص
            summary_text = self._create_market_summary_text(market_data)
            
            # تحويل إلى كلام
            audio_path = self.text_to_speech(summary_text, voice_type)
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد الملخص الصوتي: {e}")
            return None
    
    def generate_daily_plan_audio(self, daily_plan: Dict[str, Any], 
                                voice_type: str = 'female_voice') -> Optional[str]:
        """توليد صوت للخطة اليومية"""
        try:
            # إنشاء نص الخطة
            plan_text = self._create_daily_plan_text(daily_plan)
            
            # تحويل إلى كلام
            audio_path = self.text_to_speech(plan_text, voice_type)
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد صوت الخطة اليومية: {e}")
            return None
    
    def generate_alert_audio(self, alert_message: str, alert_type: str = 'info',
                           voice_type: str = 'female_voice') -> Optional[str]:
        """توليد تنبيه صوتي"""
        try:
            # تنسيق رسالة التنبيه
            formatted_message = self._format_alert_message(alert_message, alert_type)
            
            # تحويل إلى كلام
            audio_path = self.text_to_speech(formatted_message, voice_type)
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد التنبيه الصوتي: {e}")
            return None
    
    def process_voice_command(self, audio_file_path: str) -> Dict[str, Any]:
        """معالجة أمر صوتي"""
        try:
            # تحويل الصوت إلى نص
            text = self.speech_to_text(audio_file_path)
            
            if not text:
                return {
                    'success': False,
                    'error': 'فشل في تحويل الصوت إلى نص'
                }
            
            # تحليل الأمر
            command_analysis = self._analyze_voice_command(text)
            
            return {
                'success': True,
                'transcribed_text': text,
                'command': command_analysis['command'],
                'parameters': command_analysis['parameters'],
                'confidence': command_analysis['confidence']
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة الأمر الصوتي: {e}")
            return {
                'success': False,
                'error': f'خطأ في معالجة الأمر: {str(e)}'
            }
    
    def _clean_text_for_speech(self, text: str) -> str:
        """تنظيف النص للكلام"""
        # إزالة الرموز الخاصة
        cleaned = text.replace('$', 'دولار ')
        cleaned = cleaned.replace('%', ' بالمئة')
        cleaned = cleaned.replace('&', ' و ')
        cleaned = cleaned.replace('@', ' في ')
        
        # تحويل الأرقام الإنجليزية إلى عربية للنطق الأفضل
        english_to_arabic = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
        cleaned = cleaned.translate(english_to_arabic)
        
        # إزالة المسافات الزائدة
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _generate_mock_audio(self, text: str, output_path: str, voice_type: str):
        """توليد صوت وهمي للاختبار"""
        # إنشاء ملف صوتي فارغ للاختبار
        # في التطبيق الحقيقي، هنا سيتم استدعاء خدمة TTS
        
        # إنشاء ملف WAV بسيط
        duration = max(len(text) * 0.1, 1.0)  # تقدير المدة بناءً على طول النص
        
        # استخدام أداة مدمجة لإنشاء صوت بسيط
        try:
            # إنشاء ملف صوتي صامت بالمدة المحسوبة
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=duration={duration}:sample_rate=44100:channel_layout=mono',
                '-y', output_path
            ], check=True, capture_output=True)
            
            self.logger.info(f"تم إنشاء ملف صوتي وهمي: {output_path}")
            
        except subprocess.CalledProcessError:
            # إذا لم يكن ffmpeg متاحاً، إنشاء ملف نصي بدلاً من ذلك
            with open(output_path.replace('.wav', '.txt'), 'w', encoding='utf-8') as f:
                f.write(f"نص للتحويل الصوتي: {text}\nنوع الصوت: {voice_type}")
            
            self.logger.warning("تم إنشاء ملف نصي بدلاً من الصوت")
    
    def _mock_speech_recognition(self, audio_file_path: str) -> str:
        """محاكاة تحويل الكلام إلى نص"""
        # في التطبيق الحقيقي، هنا سيتم استدعاء خدمة STT
        
        # أوامر صوتية محتملة للاختبار
        mock_commands = [
            "ما هو سعر البيتكوين الحالي؟",
            "أظهر لي الخطة اليومية",
            "ما هي التوصيات الحالية؟",
            "كيف أداء محفظتي اليوم؟",
            "أريد شراء بيتكوين",
            "ما هي المخاطر في السوق؟",
            "أغلق جميع المراكز",
            "أظهر لي الأرباح والخسائر"
        ]
        
        # اختيار أمر عشوائي للاختبار
        import random
        return random.choice(mock_commands)
    
    def _create_market_summary_text(self, market_data: Dict[str, Any]) -> str:
        """إنشاء نص ملخص السوق"""
        summary_parts = []
        
        # مقدمة
        summary_parts.append("ملخص السوق الحالي.")
        
        # معلومات عامة
        if 'overall_trend' in market_data:
            summary_parts.append(f"الاتجاه العام للسوق {market_data['overall_trend']}.")
        
        if 'volatility' in market_data:
            volatility_level = "عالية" if market_data['volatility'] > 0.6 else "متوسطة" if market_data['volatility'] > 0.3 else "منخفضة"
            summary_parts.append(f"مستوى التقلبات {volatility_level}.")
        
        # أسعار العملات الرئيسية
        if 'symbols_analysis' in market_data:
            summary_parts.append("أسعار العملات الرئيسية:")
            
            for symbol, data in market_data['symbols_analysis'].items():
                price = data.get('price', 0)
                change = data.get('change_24h', 0)
                change_text = "ارتفع" if change > 0 else "انخفض" if change < 0 else "استقر"
                
                summary_parts.append(f"{symbol} يتداول عند {price:.0f} دولار، وقد {change_text} بنسبة {abs(change):.1f} بالمئة خلال آخر 24 ساعة.")
        
        return " ".join(summary_parts)
    
    def _create_daily_plan_text(self, daily_plan: Dict[str, Any]) -> str:
        """إنشاء نص الخطة اليومية"""
        plan_parts = []
        
        # مقدمة
        plan_parts.append("الخطة اليومية للتداول.")
        
        # نظرة عامة على السوق
        if 'market_outlook' in daily_plan:
            plan_parts.append(f"نظرة عامة على السوق: {daily_plan['market_outlook']}.")
        
        # الفرص المتاحة
        if 'opportunities' in daily_plan and daily_plan['opportunities']:
            plan_parts.append("الفرص المتاحة اليوم:")
            
            for opportunity in daily_plan['opportunities']:
                symbol = opportunity.get('symbol', 'غير محدد')
                description = opportunity.get('description', '')
                probability = opportunity.get('probability', 0) * 100
                
                plan_parts.append(f"{symbol}: {description}. احتمالية النجاح {probability:.0f} بالمئة.")
        
        # المخاطر
        if 'risks' in daily_plan and daily_plan['risks']:
            plan_parts.append("المخاطر المحتملة:")
            for risk in daily_plan['risks']:
                plan_parts.append(f"{risk}.")
        
        # التوصيات
        if 'recommendations' in daily_plan and daily_plan['recommendations']:
            plan_parts.append("التوصيات العامة:")
            for recommendation in daily_plan['recommendations']:
                plan_parts.append(f"{recommendation}.")
        
        return " ".join(plan_parts)
    
    def _format_alert_message(self, message: str, alert_type: str) -> str:
        """تنسيق رسالة التنبيه"""
        alert_prefixes = {
            'success': 'تنبيه إيجابي:',
            'error': 'تنبيه خطأ:',
            'warning': 'تحذير:',
            'info': 'معلومة:'
        }
        
        prefix = alert_prefixes.get(alert_type, 'تنبيه:')
        return f"{prefix} {message}"
    
    def _analyze_voice_command(self, text: str) -> Dict[str, Any]:
        """تحليل الأمر الصوتي"""
        text_lower = text.lower()
        
        # تحليل بسيط للأوامر الشائعة
        if any(word in text_lower for word in ['سعر', 'كم', 'قيمة']):
            if 'بتكوين' in text_lower or 'bitcoin' in text_lower:
                return {
                    'command': 'get_price',
                    'parameters': {'symbol': 'BTCUSDT'},
                    'confidence': 0.9
                }
            elif 'إيثريوم' in text_lower or 'ethereum' in text_lower:
                return {
                    'command': 'get_price',
                    'parameters': {'symbol': 'ETHUSDT'},
                    'confidence': 0.9
                }
        
        elif any(word in text_lower for word in ['خطة', 'تخطيط', 'برنامج']):
            return {
                'command': 'show_daily_plan',
                'parameters': {},
                'confidence': 0.8
            }
        
        elif any(word in text_lower for word in ['توصية', 'نصيحة', 'اقتراح']):
            return {
                'command': 'show_recommendations',
                'parameters': {},
                'confidence': 0.8
            }
        
        elif any(word in text_lower for word in ['محفظة', 'أداء', 'ربح', 'خسارة']):
            return {
                'command': 'show_portfolio',
                'parameters': {},
                'confidence': 0.8
            }
        
        elif any(word in text_lower for word in ['شراء', 'اشتري']):
            # محاولة استخراج اسم العملة
            symbol = 'BTCUSDT'  # افتراضي
            if 'إيثريوم' in text_lower:
                symbol = 'ETHUSDT'
            elif 'كاردانو' in text_lower:
                symbol = 'ADAUSDT'
            
            return {
                'command': 'place_buy_order',
                'parameters': {'symbol': symbol},
                'confidence': 0.7
            }
        
        elif any(word in text_lower for word in ['بيع', 'بع']):
            return {
                'command': 'place_sell_order',
                'parameters': {},
                'confidence': 0.7
            }
        
        elif any(word in text_lower for word in ['إغلاق', 'أغلق']):
            return {
                'command': 'close_positions',
                'parameters': {},
                'confidence': 0.8
            }
        
        else:
            return {
                'command': 'unknown',
                'parameters': {},
                'confidence': 0.3
            }
    
    def get_supported_voices(self) -> Dict[str, Dict[str, str]]:
        """الحصول على الأصوات المدعومة"""
        return {
            'female_voice': {
                'name': 'صوت أنثوي',
                'language': 'ar',
                'description': 'صوت أنثوي عربي طبيعي'
            },
            'male_voice': {
                'name': 'صوت ذكوري',
                'language': 'ar',
                'description': 'صوت ذكوري عربي طبيعي'
            }
        }
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """تنظيف الملفات المؤقتة"""
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.temp_dir):
                if filename.startswith('speech_') and filename.endswith('.wav'):
                    file_path = os.path.join(self.temp_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                        os.remove(file_path)
                        self.logger.info(f"تم حذف الملف المؤقت: {filename}")
                        
        except Exception as e:
            self.logger.error(f"خطأ في تنظيف الملفات المؤقتة: {e}")
    
    def get_voice_stats(self) -> Dict[str, Any]:
        """إحصائيات المساعد الصوتي"""
        try:
            temp_files = [f for f in os.listdir(self.temp_dir) 
                         if f.startswith('speech_') and f.endswith('.wav')]
            
            return {
                'temp_files_count': len(temp_files),
                'supported_voices': len(self.get_supported_voices()),
                'temp_directory': self.temp_dir,
                'last_cleanup': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على إحصائيات الصوت: {e}")
            return {}

