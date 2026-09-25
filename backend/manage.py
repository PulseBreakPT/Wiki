"""Private account provisioning; no public registration or first-user escalation."""
import asyncio
import argparse
import secrets
import bcrypt
from core import db, uid, now


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('email')
    parser.add_argument('--name', default='Editor do arquivo')
    parser.add_argument('--role', choices=['colaborador', 'investigador', 'jornalista', 'editor', 'moderador', 'administrador'], default='administrador')
    args = parser.parse_args()
    if await db.users.find_one({'email': args.email.lower()}):
        print('Conta já existente. Nenhuma alteração efetuada.')
        return
    password = secrets.token_urlsafe(15)
    await db.users.insert_one({'id': uid(), 'name': args.name, 'email': args.email.lower(), 'role': args.role,
                              'password_hash': bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
                              'active': True, 'created_at': now()})
    print(f'Email: {args.email}\nPalavra-passe: {password}')


if __name__ == '__main__':
    asyncio.run(main())