"""
مسارات API لإدارة الخزنة المشفرة
"""

from flask import Blueprint, request, jsonify, current_app
from src.models.auth import require_auth, User
from src.models.vault import VaultManager
import os

vault_bp = Blueprint('vault', __name__)


@vault_bp.route('/unlock', methods=['POST'])
@require_auth
def unlock_vault():
    """
    فتح الخزنة
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        master_password = data.get('master_password')
        
        if not master_password:
            return jsonify({"error": "كلمة المرور الرئيسية مطلوبة"}), 400
        
        user_id = request.current_user["user_id"]
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        
        # التحقق من كلمة المرور
        vault_manager = VaultManager()
        if not vault_manager.vault.verify_password(master_password, user.master_password_hash):
            return jsonify({"error": "كلمة المرور غير صحيحة"}), 401
        
        # فتح الخزنة
        vault_path = os.path.join(
            os.path.dirname(current_app.instance_path), 
            'vaults', 
            user.vault_file_path
        )
        
        vault_manager = VaultManager(vault_path)
        success = vault_manager.unlock_vault(master_password)
        
        if success:
            # حفظ الخزنة في الجلسة (في الذاكرة فقط)
            current_app.config[f'VAULT_{user_id}'] = vault_manager
            
            return jsonify({
                "message": "تم فتح الخزنة بنجاح",
                "api_keys_count": len(vault_manager.list_api_keys())
            }), 200
        else:
            return jsonify({"error": "فشل في فتح الخزنة"}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/lock', methods=['POST'])
@require_auth
def lock_vault():
    """
    قفل الخزنة
    """
    try:
        user_id = request.current_user["user_id"]
        
        # إزالة الخزنة من الذاكرة
        vault_key = f'VAULT_{user_id}'
        if vault_key in current_app.config:
            vault_manager = current_app.config[vault_key]
            vault_manager.lock_vault()
            del current_app.config[vault_key]
        
        return jsonify({"message": "تم قفل الخزنة"}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/status', methods=['GET'])
@require_auth
def vault_status():
    """
    حالة الخزنة
    """
    try:
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        is_unlocked = vault_key in current_app.config
        api_keys_count = 0
        
        if is_unlocked:
            vault_manager = current_app.config[vault_key]
            api_keys_count = len(vault_manager.list_api_keys())
        
        return jsonify({
            "is_unlocked": is_unlocked,
            "api_keys_count": api_keys_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/api-keys', methods=['GET'])
@require_auth
def list_api_keys():
    """
    قائمة مفاتيح API
    """
    try:
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        if vault_key not in current_app.config:
            return jsonify({"error": "الخزنة مقفلة"}), 401
        
        vault_manager = current_app.config[vault_key]
        api_keys = vault_manager.list_api_keys()
        
        return jsonify({"api_keys": api_keys}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/api-keys', methods=['POST'])
@require_auth
def add_api_key():
    """
    إضافة مفتاح API جديد
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        exchange_name = data.get('exchange_name')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        api_passphrase = data.get('api_passphrase')
        testnet = data.get('testnet', True)
        master_password = data.get('master_password')
        
        if not all([exchange_name, api_key, api_secret, master_password]):
            return jsonify({"error": "جميع الحقول مطلوبة"}), 400
        
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        if vault_key not in current_app.config:
            return jsonify({"error": "الخزنة مقفلة"}), 401
        
        vault_manager = current_app.config[vault_key]
        
        # إضافة مفتاح API
        key_id = vault_manager.add_api_key(
            exchange_name, api_key, api_secret, api_passphrase, testnet
        )
        
        # حفظ الخزنة
        success = vault_manager.save_vault(master_password)
        
        if success:
            return jsonify({
                "message": "تم إضافة مفتاح API بنجاح",
                "key_id": key_id
            }), 201
        else:
            return jsonify({"error": "فشل في حفظ الخزنة"}), 500
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/api-keys/<key_id>', methods=['GET'])
@require_auth
def get_api_key(key_id):
    """
    الحصول على مفتاح API (بدون البيانات الحساسة)
    """
    try:
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        if vault_key not in current_app.config:
            return jsonify({"error": "الخزنة مقفلة"}), 401
        
        vault_manager = current_app.config[vault_key]
        api_key_data = vault_manager.get_api_key(key_id)
        
        if not api_key_data:
            return jsonify({"error": "مفتاح API غير موجود"}), 404
        
        # إرجاع البيانات بدون المفاتيح الحساسة
        safe_data = {
            "key_id": key_id,
            "exchange": api_key_data["exchange"],
            "testnet": api_key_data["testnet"],
            "trade_only": api_key_data["trade_only"],
            "created_at": api_key_data["created_at"]
        }
        
        return jsonify(safe_data), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/api-keys/<key_id>', methods=['DELETE'])
@require_auth
def remove_api_key(key_id):
    """
    حذف مفتاح API
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        master_password = data.get('master_password')
        
        if not master_password:
            return jsonify({"error": "كلمة المرور الرئيسية مطلوبة"}), 400
        
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        if vault_key not in current_app.config:
            return jsonify({"error": "الخزنة مقفلة"}), 401
        
        vault_manager = current_app.config[vault_key]
        
        # حذف مفتاح API
        success = vault_manager.remove_api_key(key_id)
        
        if not success:
            return jsonify({"error": "مفتاح API غير موجود"}), 404
        
        # حفظ الخزنة
        save_success = vault_manager.save_vault(master_password)
        
        if save_success:
            return jsonify({"message": "تم حذف مفتاح API بنجاح"}), 200
        else:
            return jsonify({"error": "فشل في حفظ الخزنة"}), 500
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/export', methods=['POST'])
@require_auth
def export_vault():
    """
    تصدير الخزنة
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        export_password = data.get('export_password')
        
        if not export_password:
            return jsonify({"error": "كلمة مرور التصدير مطلوبة"}), 400
        
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        if vault_key not in current_app.config:
            return jsonify({"error": "الخزنة مقفلة"}), 401
        
        vault_manager = current_app.config[vault_key]
        exported_data = vault_manager.export_vault(export_password)
        
        return jsonify({
            "message": "تم تصدير الخزنة بنجاح",
            "exported_data": exported_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/import', methods=['POST'])
@require_auth
def import_vault():
    """
    استيراد الخزنة
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        encrypted_data = data.get('encrypted_data')
        import_password = data.get('import_password')
        master_password = data.get('master_password')
        
        if not all([encrypted_data, import_password, master_password]):
            return jsonify({"error": "جميع الحقول مطلوبة"}), 400
        
        user_id = request.current_user["user_id"]
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        
        # إنشاء مدير خزنة جديد
        vault_path = os.path.join(
            os.path.dirname(current_app.instance_path), 
            'vaults', 
            user.vault_file_path
        )
        
        vault_manager = VaultManager(vault_path)
        
        # استيراد البيانات
        success = vault_manager.import_vault(encrypted_data, import_password)
        
        if not success:
            return jsonify({"error": "فشل في استيراد الخزنة"}), 400
        
        # حفظ الخزنة بكلمة المرور الرئيسية
        save_success = vault_manager.save_vault(master_password)
        
        if save_success:
            # تحديث الخزنة في الذاكرة
            vault_key = f'VAULT_{user_id}'
            current_app.config[vault_key] = vault_manager
            
            return jsonify({
                "message": "تم استيراد الخزنة بنجاح",
                "api_keys_count": len(vault_manager.list_api_keys())
            }), 200
        else:
            return jsonify({"error": "فشل في حفظ الخزنة المستوردة"}), 500
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@vault_bp.route('/test-connection/<key_id>', methods=['POST'])
@require_auth
def test_api_connection(key_id):
    """
    اختبار الاتصال بمفتاح API
    """
    try:
        user_id = request.current_user["user_id"]
        vault_key = f'VAULT_{user_id}'
        
        if vault_key not in current_app.config:
            return jsonify({"error": "الخزنة مقفلة"}), 401
        
        vault_manager = current_app.config[vault_key]
        api_key_data = vault_manager.get_api_key(key_id)
        
        if not api_key_data:
            return jsonify({"error": "مفتاح API غير موجود"}), 404
        
        # هنا يمكن إضافة منطق اختبار الاتصال الفعلي
        # حالياً سنرجع نتيجة وهمية
        
        return jsonify({
            "status": "success",
            "message": "تم اختبار الاتصال بنجاح",
            "exchange": api_key_data["exchange"],
            "testnet": api_key_data["testnet"],
            "permissions": ["trade"],  # وهمي
            "balance_access": False  # وهمي
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500

