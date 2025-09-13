"""
نموذج المصادقة وإدارة الجلسات (Authentication & Session Management)
يتولى تسجيل الدخول، المصادقة الثنائية، وإدارة الجلسات
"""

import os
import jwt
import time
import secrets
import pyotp
import qrcode
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from src.models.vault import EncryptedVault


class User(db.Model):
    """
    نموذج المستخدم في قاعدة البيانات
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    master_password_hash = db.Column(db.String(255), nullable=False)
    totp_secret = db.Column(db.String(32), nullable=True)  # للمصادقة الثنائية
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    vault_file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Session(db.Model):
    """
    نموذج الجلسات النشطة
    """
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def __repr__(self):
        return f'<Session {self.session_token[:8]}...>'


class AuthManager:
    """
    مدير المصادقة والجلسات
    """
    
    def __init__(self, secret_key: str, session_timeout_minutes: int = 5):
        self.vault = EncryptedVault()
        self.secret_key = secret_key
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def register_user(self, username: str, master_password: str, enable_2fa: bool = False) -> Dict[str, Any]:
        """
        تسجيل مستخدم جديد
        """
        try:
            # التحقق من عدم وجود المستخدم
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return {"success": False, "error": "اسم المستخدم موجود بالفعل"}
            
            # تجزئة كلمة المرور الرئيسية
            password_hash = self.vault.hash_password(master_password)
            
            # إنشاء مفتاح TOTP للمصادقة الثنائية
            totp_secret = None
            qr_code_data = None
            
            if enable_2fa:
                totp_secret = pyotp.random_base32()
                totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                    name=username,
                    issuer_name="Neon Trader V7"
                )
                
                # إنشاء QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp_uri)
                qr.make(fit=True)
                qr_code_data = totp_uri
            
            # إنشاء المستخدم
            user = User(
                username=username,
                master_password_hash=password_hash,
                totp_secret=totp_secret,
                is_2fa_enabled=enable_2fa,
                vault_file_path=f"vault_{username}.enc"
            )
            
            db.session.add(user)
            db.session.commit()
            
            result = {
                "success": True,
                "user_id": user.id,
                "username": username,
                "2fa_enabled": enable_2fa
            }
            
            if qr_code_data:
                result["qr_code_uri"] = qr_code_data
                result["totp_secret"] = totp_secret
            
            return result
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"خطأ في التسجيل: {str(e)}"}
    
    def authenticate_user(self, username: str, master_password: str, 
                         totp_code: str = None, ip_address: str = None, 
                         user_agent: str = None) -> Dict[str, Any]:
        """
        مصادقة المستخدم وإنشاء جلسة
        """
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return {"success": False, "error": "اسم المستخدم أو كلمة المرور غير صحيحة"}
            
            # التحقق من القفل
            if user.locked_until and datetime.utcnow() < user.locked_until:
                return {"success": False, "error": "الحساب مقفل مؤقتاً"}
            
            # التحقق من كلمة المرور
            if not self.vault.verify_password(master_password, user.master_password_hash):
                user.failed_login_attempts += 1
                
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.locked_until = datetime.utcnow() + self.lockout_duration
                
                db.session.commit()
                return {"success": False, "error": "اسم المستخدم أو كلمة المرور غير صحيحة"}
            
            # التحقق من المصادقة الثنائية
            if user.is_2fa_enabled:
                if not totp_code:
                    return {"success": False, "error": "مطلوب رمز المصادقة الثنائية", "requires_2fa": True}
                
                totp = pyotp.TOTP(user.totp_secret)
                if not totp.verify(totp_code):
                    return {"success": False, "error": "رمز المصادقة الثنائية غير صحيح"}
            
            # إعادة تعيين محاولات الدخول الفاشلة
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # إنشاء جلسة جديدة
            session_token = self.create_session(user.id, ip_address, user_agent)
            
            db.session.commit()
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "session_token": session_token,
                "vault_file_path": user.vault_file_path
            }
            
        except Exception as e:
            return {"success": False, "error": f"خطأ في المصادقة: {str(e)}"}
    
    def create_session(self, user_id: int, ip_address: str = None, 
                      user_agent: str = None) -> str:
        """
        إنشاء جلسة جديدة
        """
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + self.session_timeout
        
        session = Session(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session_token
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """
        التحقق من صحة الجلسة
        """
        try:
            session = Session.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not session:
                return {"valid": False, "error": "جلسة غير صالحة"}
            
            # التحقق من انتهاء الصلاحية
            if datetime.utcnow() > session.expires_at:
                session.is_active = False
                db.session.commit()
                return {"valid": False, "error": "انتهت صلاحية الجلسة"}
            
            # تحديث آخر نشاط
            session.last_activity = datetime.utcnow()
            db.session.commit()
            
            return {
                "valid": True,
                "user_id": session.user_id,
                "username": session.user.username,
                "session_id": session.id
            }
            
        except Exception as e:
            return {"valid": False, "error": f"خطأ في التحقق من الجلسة: {str(e)}"}
    
    def extend_session(self, session_token: str) -> bool:
        """
        تمديد الجلسة
        """
        try:
            session = Session.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if session and datetime.utcnow() <= session.expires_at:
                session.expires_at = datetime.utcnow() + self.session_timeout
                session.last_activity = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"خطأ في تمديد الجلسة: {str(e)}")
            return False
    
    def logout_session(self, session_token: str) -> bool:
        """
        تسجيل الخروج وإنهاء الجلسة
        """
        try:
            session = Session.query.filter_by(session_token=session_token).first()
            
            if session:
                session.is_active = False
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"خطأ في تسجيل الخروج: {str(e)}")
            return False
    
    def logout_all_sessions(self, user_id: int) -> bool:
        """
        تسجيل الخروج من جميع الجلسات
        """
        try:
            sessions = Session.query.filter_by(user_id=user_id, is_active=True).all()
            
            for session in sessions:
                session.is_active = False
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"خطأ في تسجيل الخروج من جميع الجلسات: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self):
        """
        تنظيف الجلسات المنتهية الصلاحية
        """
        try:
            expired_sessions = Session.query.filter(
                Session.expires_at < datetime.utcnow(),
                Session.is_active == True
            ).all()
            
            for session in expired_sessions:
                session.is_active = False
            
            db.session.commit()
            
        except Exception as e:
            print(f"خطأ في تنظيف الجلسات: {str(e)}")
    
    def get_active_sessions(self, user_id: int) -> list:
        """
        الحصول على الجلسات النشطة للمستخدم
        """
        try:
            sessions = Session.query.filter_by(
                user_id=user_id,
                is_active=True
            ).filter(
                Session.expires_at > datetime.utcnow()
            ).all()
            
            return [{
                "id": session.id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "ip_address": session.ip_address,
                "user_agent": session.user_agent
            } for session in sessions]
            
        except Exception as e:
            print(f"خطأ في الحصول على الجلسات النشطة: {str(e)}")
            return []
    
    def enable_2fa(self, user_id: int) -> Dict[str, Any]:
        """
        تفعيل المصادقة الثنائية
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "المستخدم غير موجود"}
            
            if user.is_2fa_enabled:
                return {"success": False, "error": "المصادقة الثنائية مفعلة بالفعل"}
            
            # إنشاء مفتاح TOTP جديد
            totp_secret = pyotp.random_base32()
            totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                name=user.username,
                issuer_name="Neon Trader V7"
            )
            
            user.totp_secret = totp_secret
            user.is_2fa_enabled = True
            db.session.commit()
            
            return {
                "success": True,
                "qr_code_uri": totp_uri,
                "totp_secret": totp_secret
            }
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"خطأ في تفعيل المصادقة الثنائية: {str(e)}"}
    
    def disable_2fa(self, user_id: int, totp_code: str) -> Dict[str, Any]:
        """
        إلغاء تفعيل المصادقة الثنائية
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "المستخدم غير موجود"}
            
            if not user.is_2fa_enabled:
                return {"success": False, "error": "المصادقة الثنائية غير مفعلة"}
            
            # التحقق من رمز TOTP
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(totp_code):
                return {"success": False, "error": "رمز المصادقة الثنائية غير صحيح"}
            
            user.totp_secret = None
            user.is_2fa_enabled = False
            db.session.commit()
            
            return {"success": True}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"خطأ في إلغاء المصادقة الثنائية: {str(e)}"}


def require_auth(f):
    """
    ديكوريتر للتحقق من المصادقة
    """
    from functools import wraps
    from flask import request, jsonify, current_app
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "مطلوب رمز المصادقة"}), 401
        
        session_token = auth_header.split(' ')[1]
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        
        validation_result = auth_manager.validate_session(session_token)
        
        if not validation_result["valid"]:
            return jsonify({"error": validation_result["error"]}), 401
        
        # إضافة معلومات المستخدم إلى الطلب
        request.current_user = validation_result
        
        return f(*args, **kwargs)
    
    return decorated_function

