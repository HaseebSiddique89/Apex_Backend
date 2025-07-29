from quart import Blueprint, request, jsonify, g
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.utils.security import hash_password, verify_password, create_access_token, login_required
from backend.models.user import User
from backend.db.mongo import get_db
from backend.utils.email_utils import generate_verification_token, send_verification_email

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

    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'error': 'Invalid email format'}), 400

    db = await get_db()
    
    # Check if user already exists in verified users
    if await db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({'error': 'Username or email already exists'}), 409
    
    # Check if user exists in pending verification
    if await db.pending_users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({'error': 'Username or email already exists in pending verification'}), 409

    # Generate verification token
    verification_token = generate_verification_token()
    
    password_hash = hash_password(password)
    user = User(
        username=username, 
        email=email, 
        password_hash=password_hash,
        is_email_verified=False,
        email_verification_token=verification_token
    )
    user_dict = user.to_dict()
    user_dict.pop('_id', None)
    
    # Store in pending_users collection (not verified yet)
    result = await db.pending_users.insert_one(user_dict)
    
    # Send verification email
    email_sent = await send_verification_email(email, username, verification_token)
    
    if email_sent:
        return jsonify({
            'message': 'Registration initiated. Please check your email to verify your account and complete registration.'
        }), 201
    else:
        # If email fails, remove from pending and inform user
        await db.pending_users.delete_one({"_id": result.inserted_id})
        return jsonify({
            'error': 'Failed to send verification email. Please try again.'
        }), 500

@auth_bp.route('/verify-email', methods=['POST'])
async def verify_email():
    data = await request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Verification token is required'}), 400
    
    db = await get_db()
    
    # Find user in pending_users collection
    user_data = await db.pending_users.find_one({"email_verification_token": token})
    
    if not user_data:
        return jsonify({'error': 'Invalid or expired verification token'}), 400
    
    # Check if email is already verified in main users collection
    existing_user = await db.users.find_one({"email": user_data['email']})
    if existing_user:
        return jsonify({'error': 'Email is already verified'}), 400
    
    # Move user from pending_users to users collection
    user_dict = user_data.copy()
    user_dict.pop('_id', None)  # Remove the old _id
    user_dict['is_email_verified'] = True
    user_dict['email_verification_token'] = None
    
    # Insert into verified users collection
    await db.users.insert_one(user_dict)
    
    # Remove from pending users collection
    await db.pending_users.delete_one({"_id": user_data['_id']})
    
    return jsonify({'message': 'Email verified successfully. You can now login.'}), 200

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
    
    # Check if email is verified (users in main collection are already verified)
    if not user_data.get('is_email_verified', False):
        return jsonify({
            'error': 'Please verify your email address before logging in. Check your email for verification link.'
        }), 401

    access_token = create_access_token({
        'user_id': str(user_data.get('_id')),
        'username': user_data.get('username'),
        'email': user_data.get('email')
    })
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/resend-verification', methods=['POST'])
async def resend_verification():
    data = await request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    db = await get_db()
    
    # Check in pending_users collection
    user_data = await db.pending_users.find_one({"email": email})
    
    if not user_data:
        # Check if already verified
        verified_user = await db.users.find_one({"email": email})
        if verified_user:
            return jsonify({'error': 'Email is already verified'}), 400
        return jsonify({'error': 'User not found'}), 404
    
    # Generate new verification token
    new_token = generate_verification_token()
    
    # Update user with new token
    await db.pending_users.update_one(
        {"_id": user_data['_id']},
        {"$set": {"email_verification_token": new_token}}
    )
    
    # Send new verification email
    email_sent = await send_verification_email(email, user_data['username'], new_token)
    
    if email_sent:
        return jsonify({'message': 'Verification email sent successfully'}), 200
    else:
        return jsonify({'error': 'Failed to send verification email'}), 500

@auth_bp.route('/protected', methods=['GET'])
@login_required
async def protected():
    user = g.current_user
    return {'message': f'Hello, {user["username"]}! This is a protected route.'} 