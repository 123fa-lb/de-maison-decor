"""Single-client session authentication for De Maison Decor. No signup route."""
import hashlib
import hmac
import os
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

router = APIRouter(prefix='/api/auth', tags=['Authentication'])
_cookie_name = 'maison_session'
_client = None
_lock = threading.Lock()
_attempts = {}


def database():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                uri = os.environ.get('MONGODB_URI')
                if not uri:
                    raise RuntimeError('MONGODB_URI is missing from .env')
                _client = MongoClient(uri, serverSelectionTimeoutMS=7000)
    return _client[os.getenv('MONGODB_DB_NAME', 'de_maison_decor')]


def secret():
    key = os.getenv('JWT_SECRET', '')
    if len(key) < 32:
        raise RuntimeError('JWT_SECRET must be set to a private random string of at least 32 characters')
    return key


def allowed_origins():
    defaults = ['http://localhost:5173', 'http://127.0.0.1:5173']
    extras = [s.strip().rstrip('/') for s in os.getenv('FRONTEND_ORIGINS', '').split(',') if s.strip()]
    return list(dict.fromkeys(defaults + extras))


def cookie_options():
    same_site = os.getenv('AUTH_COOKIE_SAMESITE', 'lax').lower()
    if same_site not in ('lax', 'strict', 'none'):
        raise RuntimeError('AUTH_COOKIE_SAMESITE must be lax, strict, or none')
    secure = os.getenv('AUTH_COOKIE_SECURE', 'false').lower() == 'true'
    if same_site == 'none' and not secure:
        raise RuntimeError('SameSite=None requires AUTH_COOKIE_SECURE=true (HTTPS)')
    return {'httponly': True, 'secure': secure, 'samesite': same_site, 'path': '/'}


def current_user(request: Request):
    token = request.cookies.get(_cookie_name)
    if not token:
        return None
    try:
        payload = jwt.decode(token, secret(), algorithms=['HS256'], options={'require': ['sub', 'exp', 'iat', 'jti']})
        jti_hash = hashlib.sha256(payload['jti'].encode()).hexdigest()
        session = database().sessions.find_one({'_id': jti_hash, 'username': payload['sub']})
        if not session:
            return None
        expiry = session.get('expires_at')
        if not isinstance(expiry, datetime):
            return None
        if expiry.tzinfo is None:  # PyMongo returns naive UTC datetimes by default.
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry <= datetime.now(timezone.utc):
            return None
        user = database().users.find_one({'username': payload['sub'], 'active': True, 'role': 'client'})
        return user
    except (jwt.PyJWTError, PyMongoError, ValueError, TypeError):
        return None


def response_error(code, message):
    return JSONResponse({'detail': message}, status_code=code, headers={'Cache-Control': 'no-store'})


@router.post('/login')
async def login(request: Request):
    origin = request.headers.get('origin')
    if origin and origin.rstrip('/') not in allowed_origins():
        return response_error(403, 'Origin not allowed')
    ip = request.client.host if request.client else 'unknown'
    now = time.monotonic()
    with _lock:
        # Basic per-process brute-force protection; use shared rate limiting for multiple workers.
        recent = [t for t in _attempts.get(ip, []) if now - t < 900]
        if len(recent) >= 5:
            return response_error(429, 'Too many attempts. Try again in 15 minutes.')
        recent.append(now)
        _attempts[ip] = recent
    try:
        data = await request.json()
        username = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))
        if not username or not password:
            return response_error(400, 'Username and password are required')
        user = database().users.find_one({'username': username, 'active': True, 'role': 'client'})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return response_error(401, 'Invalid username or password')
        now_utc = datetime.now(timezone.utc)
        expires = now_utc + timedelta(days=7)
        jti = secrets.token_urlsafe(32)
        database().sessions.create_index('expires_at', expireAfterSeconds=0)
        database().sessions.insert_one({'_id': hashlib.sha256(jti.encode()).hexdigest(), 'username': username, 'expires_at': expires})
        token = jwt.encode({'sub': username, 'iat': now_utc, 'exp': expires, 'jti': jti}, secret(), algorithm='HS256')
        response = JSONResponse({'authenticated': True, 'username': username}, headers={'Cache-Control': 'no-store'})
        response.set_cookie(_cookie_name, token, max_age=7*86400, **cookie_options())
        with _lock:
            _attempts.pop(ip, None)
        return response
    except (ValueError, TypeError, KeyError, UnicodeError):
        return response_error(401, 'Invalid username or password')
    except (PyMongoError, RuntimeError):
        return response_error(503, 'Authentication service unavailable')


@router.get('/me')
async def me(request: Request):
    user = current_user(request)
    if not user:
        return response_error(401, 'Not authenticated')
    return JSONResponse({'authenticated': True, 'username': user['username']}, headers={'Cache-Control': 'no-store'})


@router.post('/logout')
async def logout(request: Request):
    origin = request.headers.get('origin')
    if origin and origin.rstrip('/') not in allowed_origins():
        return response_error(403, 'Origin not allowed')
    token = request.cookies.get(_cookie_name)
    if token:
        try:
            payload = jwt.decode(token, secret(), algorithms=['HS256'])
            database().sessions.delete_one({'_id': hashlib.sha256(payload['jti'].encode()).hexdigest()})
        except (jwt.PyJWTError, PyMongoError, KeyError, RuntimeError):
            pass
    response = JSONResponse({'success': True}, headers={'Cache-Control': 'no-store'})
    response.delete_cookie(_cookie_name, path='/', secure=cookie_options()['secure'], samesite=cookie_options()['samesite'])
    return response


async def protect_api(request: Request, call_next):
    path = request.url.path
    if request.method == 'OPTIONS' or not path.startswith('/api/'):
        return await call_next(request)
    if path in ('/api/health', '/api/auth/login', '/api/auth/me', '/api/auth/logout'):
        return await call_next(request)
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        origin = request.headers.get('origin', '').rstrip('/')
        if origin not in allowed_origins():
            return response_error(403, 'Request origin not allowed')
    if not current_user(request):
        return response_error(401, 'Login required')
    return await call_next(request)
