"""
نموذج الخزنة المشفرة (Encrypted Vault Model)
يتولى تشفير وفك تشفير البيانات الحساسة مثل مفاتيح API
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets


class EncryptedVault:
    """
    فئة الخزنة المشفرة لحماية البيانات الحساسة
    """
    
    def __init__(self):
        self.ph = PasswordHasher()
        
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        اشتقاق مفتاح التشفير من كلمة المرور والملح
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    def encrypt_data(self, data: dict, password: str) -> str:
        """
        تشفير البيانات باستخدام AES-256-GCM
        """
        # تحويل البيانات إلى JSON
        json_data = json.dumps(data).encode()
        
        # توليد ملح عشوائي
        salt = os.urandom(16)
        
        # اشتقاق مفتاح التشفير
        key = self.derive_key(password, salt)
        
        # إنشاء مثيل AESGCM
        aesgcm = AESGCM(key)
        
        # توليد nonce عشوائي
        nonce = os.urandom(12)
        
        # تشفير البيانات
        ciphertext = aesgcm.encrypt(nonce, json_data, None)
        
        # دمج الملح والـ nonce والبيانات المشفرة
        encrypted_package = salt + nonce + ciphertext
        
        # تحويل إلى base64 للتخزين
        return base64.b64encode(encrypted_package).decode()
    
    def decrypt_data(self, encrypted_data: str, password: str) -> dict:
        """
        فك تشفير البيانات
        """
        try:
            # فك تشفير base64
            encrypted_package = base64.b64decode(encrypted_data.encode())
            
            # استخراج الملح والـ nonce والبيانات المشفرة
            salt = encrypted_package[:16]
            nonce = encrypted_package[16:28]
            ciphertext = encrypted_package[28:]
            
            # اشتقاق مفتاح التشفير
            key = self.derive_key(password, salt)
            
            # إنشاء مثيل AESGCM
            aesgcm = AESGCM(key)
            
            # فك التشفير
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            
            # تحويل من JSON
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            raise ValueError(f"فشل في فك التشفير: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """
        تجزئة كلمة المرور باستخدام Argon2id
        """
        return self.ph.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        التحقق من كلمة المرور
        """
        try:
            self.ph.verify(hashed, password)
            return True
        except VerifyMismatchError:
            return False
    
    def generate_api_key_id(self) -> str:
        """
        توليد معرف فريد لمفتاح API
        """
        return secrets.token_urlsafe(16)


class VaultManager:
    """
    مدير الخزنة لإدارة مفاتيح API والبيانات الحساسة
    """
    
    def __init__(self, vault_file_path: str = None):
        self.vault = EncryptedVault()
        self.vault_file_path = vault_file_path or "vault.enc"
        self.decrypted_data = None
        self.is_unlocked = False
    
    def create_vault(self, master_password: str, initial_data: dict = None) -> bool:
        """
        إنشاء خزنة جديدة
        """
        try:
            data = initial_data or {
                "api_keys": {},
                "settings": {},
                "created_at": str(os.urandom(8).hex()),
                "version": "1.0"
            }
            
            encrypted_data = self.vault.encrypt_data(data, master_password)
            
            with open(self.vault_file_path, 'w') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"خطأ في إنشاء الخزنة: {str(e)}")
            return False
    
    def unlock_vault(self, master_password: str) -> bool:
        """
        فتح الخزنة باستخدام كلمة المرور الرئيسية
        """
        try:
            if not os.path.exists(self.vault_file_path):
                return False
            
            with open(self.vault_file_path, 'r') as f:
                encrypted_data = f.read()
            
            self.decrypted_data = self.vault.decrypt_data(encrypted_data, master_password)
            self.is_unlocked = True
            return True
            
        except Exception as e:
            print(f"خطأ في فتح الخزنة: {str(e)}")
            self.is_unlocked = False
            return False
    
    def lock_vault(self):
        """
        قفل الخزنة ومسح البيانات من الذاكرة
        """
        self.decrypted_data = None
        self.is_unlocked = False
    
    def save_vault(self, master_password: str) -> bool:
        """
        حفظ الخزنة بعد التعديل
        """
        if not self.is_unlocked or not self.decrypted_data:
            return False
        
        try:
            encrypted_data = self.vault.encrypt_data(self.decrypted_data, master_password)
            
            with open(self.vault_file_path, 'w') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"خطأ في حفظ الخزنة: {str(e)}")
            return False
    
    def add_api_key(self, exchange_name: str, api_key: str, api_secret: str, 
                   api_passphrase: str = None, testnet: bool = True) -> str:
        """
        إضافة مفتاح API جديد
        """
        if not self.is_unlocked:
            raise ValueError("الخزنة مقفلة")
        
        key_id = self.vault.generate_api_key_id()
        
        api_data = {
            "exchange": exchange_name,
            "api_key": api_key,
            "api_secret": api_secret,
            "api_passphrase": api_passphrase,
            "testnet": testnet,
            "trade_only": True,  # دائماً trade-only للأمان
            "created_at": str(os.urandom(8).hex())
        }
        
        self.decrypted_data["api_keys"][key_id] = api_data
        return key_id
    
    def get_api_key(self, key_id: str) -> dict:
        """
        الحصول على مفتاح API
        """
        if not self.is_unlocked:
            raise ValueError("الخزنة مقفلة")
        
        return self.decrypted_data["api_keys"].get(key_id)
    
    def list_api_keys(self) -> dict:
        """
        قائمة جميع مفاتيح API (بدون البيانات الحساسة)
        """
        if not self.is_unlocked:
            raise ValueError("الخزنة مقفلة")
        
        safe_list = {}
        for key_id, data in self.decrypted_data["api_keys"].items():
            safe_list[key_id] = {
                "exchange": data["exchange"],
                "testnet": data["testnet"],
                "trade_only": data["trade_only"],
                "created_at": data["created_at"]
            }
        
        return safe_list
    
    def remove_api_key(self, key_id: str) -> bool:
        """
        حذف مفتاح API
        """
        if not self.is_unlocked:
            raise ValueError("الخزنة مقفلة")
        
        if key_id in self.decrypted_data["api_keys"]:
            del self.decrypted_data["api_keys"][key_id]
            return True
        
        return False
    
    def export_vault(self, export_password: str) -> str:
        """
        تصدير الخزنة بكلمة مرور جديدة
        """
        if not self.is_unlocked:
            raise ValueError("الخزنة مقفلة")
        
        return self.vault.encrypt_data(self.decrypted_data, export_password)
    
    def import_vault(self, encrypted_data: str, import_password: str) -> bool:
        """
        استيراد خزنة من بيانات مشفرة
        """
        try:
            self.decrypted_data = self.vault.decrypt_data(encrypted_data, import_password)
            self.is_unlocked = True
            return True
        except Exception as e:
            print(f"خطأ في استيراد الخزنة: {str(e)}")
            return False

