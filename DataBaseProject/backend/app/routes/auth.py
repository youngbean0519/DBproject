# filepath: /home/bean/Programming/DataBaseProject/backend/app/routes/auth.py
from flask import Blueprint, request
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from app.utils import (
    generate_token, format_error_response,
    format_success_response, validate_required_fields, decode_token
)

import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """회원가입 기능"""
    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['email', 'password'])
    if not is_valid:
        return format_error_response(error_message)
    
    email = data['email']
    password = data['password']
    notify = data.get('notify_by_email', False)
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return format_error_response('User already exists', 409)
    
    hashed_password = generate_password_hash(password)
    user = User(email=email, hashed_password=hashed_password, notify_by_email=notify)
    db.session.add(user)
    db.session.commit()

    return format_success_response('User registered successfully', status_code=201)

@auth_bp.route('/login', methods=['POST'])
def login():
    """로그인 기능"""
    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['email', 'password'])
    if not is_valid:
        return format_error_response(error_message)
    
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.hashed_password, password):
        return format_error_response('Invalid credentials', 401)
    
    token = generate_token(user.user_id)
    return format_success_response('Login successful', {'token': token})

@auth_bp.route('/withdraw', methods=['DELETE'])
def withdraw():
    """회원 탈퇴 기능"""
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    try:
        user = User.query.get(user_id)
        if not user:
            return format_error_response('User not found', 404)
        
        # 관련된 모든 데이터 삭제
        # likes 테이블에서 삭제
        db.session.execute(
            text('DELETE FROM likes WHERE user_id = :user_id'),
            {'user_id': user_id}
        )
        
        # watchlist 테이블에서 삭제
        db.session.execute(
            text('DELETE FROM watchlist WHERE user_id = :user_id'),
            {'user_id': user_id}
        )
        
        # recommendations 테이블에서 삭제
        db.session.execute(
            text('DELETE FROM recommendations WHERE user_id = :user_id'),
            {'user_id': user_id}
        )
        db.session.delete(user)
        db.session.commit()

        return format_success_response('User account deleted successfully')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to delete user account: {str(e)}', 500)

@auth_bp.route('/update', methods=['PUT'])
def update_user():
    """회원 정보 수정 기능"""
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    data = request.get_json()
    if not data:
        return format_error_response('No data provided', 400)
    
    try:
        user = User.query.get(user_id)
        if not user:
            return format_error_response('User not found', 404)
        
        #이메일 변경
        if 'email' in data:
            new_email = data['email']
            if not new_email:
                return format_error_response('Email cannot be empty', 400)
            
            # 이메일 중복 체크
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.user_id != user_id:
                return format_error_response('Email already exists', 409)
            
            user.email = new_email
        
        # 비밀번호 변경
        if 'password' in data:
            if not data['password']:
                return format_error_response('Password cannot be empty', 400)
            user.hashed_password = generate_password_hash(data['password'])
        
        # 이메일 수신 동의 여부 변경
        if 'notify_by_email' in data:
            user.notify_by_email = bool(data['notify_by_email'])
        
        db.session.commit()

        return format_success_response('User information updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to update user information: {str(e)}', 500)