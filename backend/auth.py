import hashlib
import secrets
import asyncio
from datetime import datetime, timezone, timedelta
import bcrypt
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from core import db, now
from models import LoginInput, User

router = APIRouter(prefix='/api/v1/auth', tags=['Sessões'])


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


async def session_user(request: Request):
    token = request.cookies.get('vi_session', '')
    session = await db.sessions.find_one({'token_hash': digest(token), 'expires_at': {'$gt': datetime.now(timezone.utc)}}, {'_id': 0})
    if not session:
        raise HTTPException(401, 'A sessão terminou. Inicie sessão novamente.')
    user = await db.users.find_one({'id': session['user_id'], 'active': True}, {'_id': 0, 'password_hash': 0})
    if not user:
        raise HTTPException(401, 'Conta indisponível.')
    if request.method not in ('GET', 'HEAD') and not secrets.compare_digest(request.headers.get('X-CSRF-Token', ''), session['csrf']):
        raise HTTPException(403, 'Pedido de sessão inválido.')
    return {**user, 'csrf': session['csrf']}


def require(*roles):
    async def guard(user=Depends(session_user)):
        if user['role'] not in roles:
            raise HTTPException(403, 'Não tem permissão para esta ação.')
        return user
    return guard


@router.post('/login')
async def login(data: LoginInput, request: Request, response: Response):
    key = digest(data.email.lower())
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    count = await db.login_attempts.count_documents({'key': key, 'created_at': {'$gt': cutoff}})
    if count >= 10:
        raise HTTPException(429, 'Demasiadas tentativas. Aguarde 15 minutos.')
    await db.login_attempts.insert_one({'key': key, 'created_at': datetime.now(timezone.utc)})
    user = await db.users.find_one({'email': data.email.lower(), 'active': True}, {'_id': 0})
    raw = data.password.encode()
    valid = user and len(raw) <= 72 and await asyncio.to_thread(bcrypt.checkpw, raw, user['password_hash'].encode())
    if not valid:
        raise HTTPException(401, 'Email ou palavra-passe incorretos.')
    await db.login_attempts.delete_many({'key': key})
    token, csrf = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
    await db.sessions.insert_one({'token_hash': digest(token), 'csrf': csrf, 'user_id': user['id'],
                                  'expires_at': datetime.now(timezone.utc) + timedelta(hours=8)})
    response.set_cookie('vi_session', token, httponly=True, secure=True, samesite='strict', max_age=28800, path='/api/v1')
    return {'user': User(**user).model_dump(), 'csrf': csrf}


@router.get('/me')
async def me(user=Depends(session_user)):
    return {'user': User(**user).model_dump(), 'csrf': user['csrf']}


@router.post('/logout')
async def logout(request: Request, response: Response, user=Depends(session_user)):
    await db.sessions.delete_one({'token_hash': digest(request.cookies.get('vi_session', ''))})
    response.delete_cookie('vi_session', path='/api/v1', secure=True, httponly=True, samesite='strict')
    return {'message': 'Sessão terminada.'}