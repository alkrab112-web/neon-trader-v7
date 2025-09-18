from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
import os
import secrets
import pyotp
from motor.motor_asyncio import AsyncIOMotorDatabase

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT settings - should be in .env
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    hashed_password: str
    totp_secret: Optional[str] = None
    is_2fa_enabled: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None

# Password hashing utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="بيانات المصادقة غير صالحة",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(user_id=user_id, username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات المصادقة غير صالحة",
            headers={"WWW-Authenticate": "Bearer"},
        )

# User management utilities
async def get_user_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[User]:
    """Get user by username"""
    user_doc = await db.users.find_one({"username": username})
    if user_doc:
        user_doc.pop('_id', None)
        return User(**user_doc)
    return None

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[User]:
    """Get user by ID"""
    user_doc = await db.users.find_one({"id": user_id})
    if user_doc:
        user_doc.pop('_id', None)
        return User(**user_doc)
    return None

async def create_user(db: AsyncIOMotorDatabase, user_data: UserCreate) -> User:
    """Create new user"""
    import uuid
    
    # Check if username exists
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اسم المستخدم موجود مسبقاً"
        )
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        totp_secret=pyotp.random_base32(),  # For 2FA
        is_2fa_enabled=False,
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    await db.users.insert_one(user.dict())
    return user

async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str, totp_code: Optional[str] = None) -> Optional[User]:
    """Authenticate user with username/password and optional 2FA"""
    user = await get_user_by_username(db, username)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Check 2FA if enabled
    if user.is_2fa_enabled:
        if not totp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="مطلوب رمز التحقق الثنائي"
            )
        
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رمز التحقق غير صحيح"
            )
    
    # Update last login
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return user

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = None
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        user = await get_user_by_id(db, token_data.user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="المستخدم غير موجود"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="الحساب معطل"
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="فشل في المصادقة",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 2FA utilities
def generate_qr_code_url(user: User, app_name: str = "Neon Trader V7") -> str:
    """Generate QR code URL for 2FA setup"""
    totp = pyotp.TOTP(user.totp_secret)
    return totp.provisioning_uri(
        name=user.username,
        issuer_name=app_name
    )

def verify_totp_code(user: User, totp_code: str) -> bool:
    """Verify TOTP code"""
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(totp_code)