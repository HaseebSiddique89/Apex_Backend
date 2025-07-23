from quart import Blueprint, request, jsonify, g
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.utils.security import hash_password, verify_password, create_access_token, login_required
from backend.models.user import User
from backend.db.mongo import get_db

import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Helper to find user by username or email
async def find_user(db: AsyncIOMotorDatabase, username_or_email: str):
    return await db.users.find_one({
        "$or": [
            {"username": username_or_email},
            {"email": username_or_email}
        ]
    })

@auth_bp.route('/signup', methods=['POST'])
async def signup():
    data = await request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    db = await get_db()
    # Check if user exists
    if await db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({'error': 'Username or email already exists'}), 409

    password_hash = hash_password(password)
    user = User(username=username, email=email, password_hash=password_hash)
    user_dict = user.to_dict()
    user_dict.pop('_id', None)
    await db.users.insert_one(user_dict)
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
async def login():
    data = await request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    db = await get_db()
    user_data = await find_user(db, username_or_email)
    if not user_data or not verify_password(password, user_data['password_hash']):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token({
        'user_id': str(user_data.get('_id')),
        'username': user_data.get('username'),
        'email': user_data.get('email')
    })
    return jsonify({'access_token': access_token}), 200 

@auth_bp.route('/protected', methods=['GET'])
@login_required
async def protected():
    user = g.current_user
    return {'message': f'Hello, {user["username"]}! This is a protected route.'} 