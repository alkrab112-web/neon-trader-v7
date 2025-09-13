"""
مسارات API للمساعد الصوتي
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.models.voice_assistant import VoiceAssistant
from src.models.auth import require_auth
from src.models.ai_assistant import AIAssistant
import os
import tempfile
from datetime import datetime
import logging

voice_bp = Blueprint('voice', __name__)
voice_assistant = VoiceAssistant()
ai_assistant = AIAssistant()

# إعداد مجلد الرفع
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac'}

def allowed_file(filename):
    """التحقق من امتداد الملف المسموح"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@voice_bp.route('/text-to-speech', methods=['POST'])
@require_auth
def text_to_speech():
    """تحويل النص إلى كلام"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice_type = data.get('voice_type', 'female_voice')
        language = data.get('language', 'ar')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'النص مطلوب'
            }), 400
        
        if len(text) > 5000:
            return jsonify({
                'success': False,
                'error': 'النص طويل جداً (الحد الأقصى 5000 حرف)'
            }), 400
        
        # تحويل النص إلى كلام
        audio_path = voice_assistant.text_to_speech(text, voice_type, language)
        
        if not audio_path:
            return jsonify({
                'success': False,
                'error': 'فشل في تحويل النص إلى كلام'
            }), 500
        
        return jsonify({
            'success': True,
            'audio_url': f'/api/voice/audio/{os.path.basename(audio_path)}',
            'duration_estimate': len(text) * 0.1,
            'voice_type': voice_type
        })
        
    except Exception as e:
        logging.error(f"خطأ في تحويل النص إلى كلام: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/speech-to-text', methods=['POST'])
@require_auth
def speech_to_text():
    """تحويل الكلام إلى نص"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'ملف الصوت مطلوب'
            }), 400
        
        file = request.files['audio']
        language = request.form.get('language', 'ar')
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'لم يتم اختيار ملف'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'نوع الملف غير مدعوم. الأنواع المدعومة: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # حفظ الملف مؤقتاً
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"upload_{timestamp}_{filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        try:
            # تحويل الكلام إلى نص
            transcribed_text = voice_assistant.speech_to_text(temp_path, language)
            
            if not transcribed_text:
                return jsonify({
                    'success': False,
                    'error': 'فشل في تحويل الكلام إلى نص'
                }), 500
            
            return jsonify({
                'success': True,
                'text': transcribed_text,
                'language': language,
                'confidence': 0.85  # قيمة افتراضية
            })
            
        finally:
            # حذف الملف المؤقت
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logging.error(f"خطأ في تحويل الكلام إلى نص: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/voice-command', methods=['POST'])
@require_auth
def process_voice_command():
    """معالجة أمر صوتي"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'ملف الصوت مطلوب'
            }), 400
        
        file = request.files['audio']
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'نوع الملف غير مدعوم'
            }), 400
        
        # حفظ الملف مؤقتاً
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"command_{timestamp}_{filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        file.save(temp_path)
        
        try:
            # معالجة الأمر الصوتي
            result = voice_assistant.process_voice_command(temp_path)
            
            return jsonify(result)
            
        finally:
            # حذف الملف المؤقت
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logging.error(f"خطأ في معالجة الأمر الصوتي: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/market-summary-audio', methods=['GET'])
@require_auth
def generate_market_summary_audio():
    """توليد ملخص صوتي للسوق"""
    try:
        voice_type = request.args.get('voice_type', 'female_voice')
        
        # الحصول على بيانات السوق (محاكاة)
        market_data = {
            'overall_trend': 'صاعد',
            'volatility': 0.4,
            'volume_trend': 'متزايد',
            'sentiment': 'إيجابي',
            'symbols_analysis': {
                'BTCUSDT': {
                    'price': 45000,
                    'change_24h': 2.5
                },
                'ETHUSDT': {
                    'price': 3200,
                    'change_24h': 1.8
                }
            }
        }
        
        # توليد الملخص الصوتي
        audio_path = voice_assistant.generate_market_summary_audio(market_data, voice_type)
        
        if not audio_path:
            return jsonify({
                'success': False,
                'error': 'فشل في توليد الملخص الصوتي'
            }), 500
        
        return jsonify({
            'success': True,
            'audio_url': f'/api/voice/audio/{os.path.basename(audio_path)}',
            'summary_type': 'market',
            'voice_type': voice_type
        })
        
    except Exception as e:
        logging.error(f"خطأ في توليد الملخص الصوتي: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/daily-plan-audio', methods=['GET'])
@require_auth
def generate_daily_plan_audio():
    """توليد صوت للخطة اليومية"""
    try:
        voice_type = request.args.get('voice_type', 'female_voice')
        
        # الحصول على الخطة اليومية
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            daily_plan = loop.run_until_complete(ai_assistant.generate_daily_plan())
            
            plan_data = {
                'market_outlook': daily_plan.market_outlook,
                'opportunities': daily_plan.opportunities,
                'risks': daily_plan.risks,
                'recommendations': daily_plan.recommendations
            }
            
            # توليد الصوت
            audio_path = voice_assistant.generate_daily_plan_audio(plan_data, voice_type)
            
            if not audio_path:
                return jsonify({
                    'success': False,
                    'error': 'فشل في توليد صوت الخطة'
                }), 500
            
            return jsonify({
                'success': True,
                'audio_url': f'/api/voice/audio/{os.path.basename(audio_path)}',
                'plan_date': daily_plan.date,
                'voice_type': voice_type
            })
            
        finally:
            loop.close()
        
    except Exception as e:
        logging.error(f"خطأ في توليد صوت الخطة اليومية: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/alert-audio', methods=['POST'])
@require_auth
def generate_alert_audio():
    """توليد تنبيه صوتي"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        alert_type = data.get('alert_type', 'info')
        voice_type = data.get('voice_type', 'female_voice')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'رسالة التنبيه مطلوبة'
            }), 400
        
        # توليد التنبيه الصوتي
        audio_path = voice_assistant.generate_alert_audio(message, alert_type, voice_type)
        
        if not audio_path:
            return jsonify({
                'success': False,
                'error': 'فشل في توليد التنبيه الصوتي'
            }), 500
        
        return jsonify({
            'success': True,
            'audio_url': f'/api/voice/audio/{os.path.basename(audio_path)}',
            'alert_type': alert_type,
            'voice_type': voice_type
        })
        
    except Exception as e:
        logging.error(f"خطأ في توليد التنبيه الصوتي: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """تقديم ملفات الصوت"""
    try:
        # التحقق من الأمان
        filename = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'الملف غير موجود'
            }), 404
        
        # التحقق من أن الملف من الملفات المولدة
        if not filename.startswith('speech_'):
            return jsonify({
                'success': False,
                'error': 'غير مسموح بالوصول لهذا الملف'
            }), 403
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logging.error(f"خطأ في تقديم ملف الصوت: {e}")
        return jsonify({
            'success': False,
            'error': 'خطأ في الخادم'
        }), 500

@voice_bp.route('/voices', methods=['GET'])
@require_auth
def get_supported_voices():
    """الحصول على الأصوات المدعومة"""
    try:
        voices = voice_assistant.get_supported_voices()
        
        return jsonify({
            'success': True,
            'voices': voices
        })
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على الأصوات المدعومة: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/stats', methods=['GET'])
@require_auth
def get_voice_stats():
    """إحصائيات المساعد الصوتي"""
    try:
        stats = voice_assistant.get_voice_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logging.error(f"خطأ في الحصول على إحصائيات الصوت: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/cleanup', methods=['POST'])
@require_auth
def cleanup_temp_files():
    """تنظيف الملفات المؤقتة"""
    try:
        max_age_hours = request.json.get('max_age_hours', 24) if request.is_json else 24
        
        voice_assistant.cleanup_temp_files(max_age_hours)
        
        return jsonify({
            'success': True,
            'message': 'تم تنظيف الملفات المؤقتة بنجاح'
        })
        
    except Exception as e:
        logging.error(f"خطأ في تنظيف الملفات المؤقتة: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في الخادم: {str(e)}'
        }), 500

@voice_bp.route('/health', methods=['GET'])
def health_check():
    """فحص صحة المساعد الصوتي"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'text_to_speech',
            'speech_to_text',
            'voice_commands',
            'market_summaries',
            'daily_plan_audio',
            'alerts'
        ],
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

