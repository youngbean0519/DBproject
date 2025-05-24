from flask import Blueprint, request
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import (
    generate_token, format_error_response,
    format_success_response, validate_required_fields
)

import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['email', 'password'])
    if not is_valid:
        return format_error_response(error_message)
    
    email = data['email']
    password = data['password']
    notify = data.get('notify_by_email', True)
    
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