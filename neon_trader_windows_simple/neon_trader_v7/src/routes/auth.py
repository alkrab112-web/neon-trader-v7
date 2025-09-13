"""
مسارات API للمصادقة والجلسات
"""

from flask import Blueprint, request, jsonify, current_app
from src.models.auth import AuthManager, require_auth, User
from src.models.vault import VaultManager
from src.models.user import db
import os

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    تسجيل مستخدم جديد
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        username = data.get('username')
        master_password = data.get('master_password')
        enable_2fa = data.get('enable_2fa', False)
        
        if not username or not master_password:
            return jsonify({"error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400
        
        if len(master_password) < 8:
            return jsonify({"error": "كلمة المرور يجب أن تكون 8 أحرف على الأقل"}), 400
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        result = auth_manager.register_user(username, master_password, enable_2fa)
        
        if result["success"]:
            # إنشاء خزنة فارغة للمستخدم الجديد
            vault_path = os.path.join(
                os.path.dirname(current_app.instance_path), 
                'vaults', 
                f"vault_{username}.enc"
            )
            
            # إنشاء مجلد الخزائن إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(vault_path), exist_ok=True)
            
            vault_manager = VaultManager(vault_path)
            vault_created = vault_manager.create_vault(master_password)
            
            if not vault_created:
                return jsonify({"error": "فشل في إنشاء الخزنة"}), 500
            
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    تسجيل الدخول
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        username = data.get('username')
        master_password = data.get('master_password')
        totp_code = data.get('totp_code')
        
        if not username or not master_password:
            return jsonify({"error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400
        
        # الحصول على معلومات الطلب
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent')
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        result = auth_manager.authenticate_user(
            username, master_password, totp_code, ip_address, user_agent
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            status_code = 401 if "requires_2fa" not in result else 200
            return jsonify(result), status_code
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    تسجيل الخروج
    """
    try:
        auth_header = request.headers.get('Authorization')
        session_token = auth_header.split(' ')[1]
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        success = auth_manager.logout_session(session_token)
        
        if success:
            return jsonify({"message": "تم تسجيل الخروج بنجاح"}), 200
        else:
            return jsonify({"error": "فشل في تسجيل الخروج"}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/logout-all', methods=['POST'])
@require_auth
def logout_all():
    """
    تسجيل الخروج من جميع الجلسات
    """
    try:
        user_id = request.current_user["user_id"]
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        success = auth_manager.logout_all_sessions(user_id)
        
        if success:
            return jsonify({"message": "تم تسجيل الخروج من جميع الجلسات"}), 200
        else:
            return jsonify({"error": "فشل في تسجيل الخروج"}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/validate', methods=['GET'])
@require_auth
def validate():
    """
    التحقق من صحة الجلسة
    """
    try:
        return jsonify({
            "valid": True,
            "user": {
                "id": request.current_user["user_id"],
                "username": request.current_user["username"]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/sessions', methods=['GET'])
@require_auth
def get_sessions():
    """
    الحصول على الجلسات النشطة
    """
    try:
        user_id = request.current_user["user_id"]
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        sessions = auth_manager.get_active_sessions(user_id)
        
        return jsonify({"sessions": sessions}), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/extend-session', methods=['POST'])
@require_auth
def extend_session():
    """
    تمديد الجلسة
    """
    try:
        auth_header = request.headers.get('Authorization')
        session_token = auth_header.split(' ')[1]
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        success = auth_manager.extend_session(session_token)
        
        if success:
            return jsonify({"message": "تم تمديد الجلسة"}), 200
        else:
            return jsonify({"error": "فشل في تمديد الجلسة"}), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/enable-2fa', methods=['POST'])
@require_auth
def enable_2fa():
    """
    تفعيل المصادقة الثنائية
    """
    try:
        user_id = request.current_user["user_id"]
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        result = auth_manager.enable_2fa(user_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/disable-2fa', methods=['POST'])
@require_auth
def disable_2fa():
    """
    إلغاء تفعيل المصادقة الثنائية
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        totp_code = data.get('totp_code')
        
        if not totp_code:
            return jsonify({"error": "رمز المصادقة الثنائية مطلوب"}), 400
        
        user_id = request.current_user["user_id"]
        
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        result = auth_manager.disable_2fa(user_id, totp_code)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    تغيير كلمة المرور الرئيسية
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "البيانات مطلوبة"}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({"error": "كلمة المرور الحالية والجديدة مطلوبتان"}), 400
        
        if len(new_password) < 8:
            return jsonify({"error": "كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل"}), 400
        
        user_id = request.current_user["user_id"]
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        
        # التحقق من كلمة المرور الحالية
        vault = VaultManager()
        if not vault.vault.verify_password(current_password, user.master_password_hash):
            return jsonify({"error": "كلمة المرور الحالية غير صحيحة"}), 400
        
        # تحديث كلمة المرور
        user.master_password_hash = vault.vault.hash_password(new_password)
        db.session.commit()
        
        # إعادة تشفير الخزنة بكلمة المرور الجديدة
        vault_path = os.path.join(
            os.path.dirname(current_app.instance_path), 
            'vaults', 
            user.vault_file_path
        )
        
        vault_manager = VaultManager(vault_path)
        if vault_manager.unlock_vault(current_password):
            vault_manager.save_vault(new_password)
            vault_manager.lock_vault()
        
        return jsonify({"message": "تم تغيير كلمة المرور بنجاح"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500


@auth_bp.route('/user-info', methods=['GET'])
@require_auth
def get_user_info():
    """
    الحصول على معلومات المستخدم
    """
    try:
        user_id = request.current_user["user_id"]
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "المستخدم غير موجود"}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "is_2fa_enabled": user.is_2fa_enabled,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"خطأ في الخادم: {str(e)}"}), 500

