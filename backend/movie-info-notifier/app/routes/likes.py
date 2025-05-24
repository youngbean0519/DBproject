from flask import Blueprint, request, jsonify
from app import db
from app.models.like import Like
from app.models.user import User
import jwt
import os

likes_bp = Blueprint('likes', __name__, url_prefix='/likes')

def decode_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, 'Missing token'
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        return payload['user_id'], None
    except Exception as e:
        return None, str(e)

@likes_bp.route('', methods=['POST'])
def like_item():
    user_id, error = decode_token(request)
    if error:
        return jsonify({'error': error}), 401

    data = request.get_json()
    target_type = data.get('target_type')  # 'movie', 'director', 'genre'
    target_value = data.get('target_value')

    if not target_type or not target_value:
        return jsonify({'error': 'target_type and target_value are required'}), 400
    
    if target_type not in ['movie', 'director', 'genre']:
        return jsonify({'error': 'Invalid target_type. Must be one of: movie, director, genre'}), 400
    
    existing = Like.query.filter_by(user_id=user_id, target_type=target_type, target_value=target_value).first()
    if existing:
        return jsonify({'message': f'{target_type.capitalize()} already liked'}), 200
    
    new_like = Like(user_id=user_id, target_type=target_type, target_value=target_value)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({'message': f'{target_type.capitalize()} liked successfully'}), 201

@likes_bp.route('', methods=['DELETE'])
def unlike_item():
    user_id, error = decode_token(request)
    if error:
        return jsonify({'error': error}), 401
    
    data = request.get_json()
    target_type = data.get('target_type')
    target_value = data.get('target_value')
    
    if not target_type or not target_value:
        return jsonify({'error': 'target_type and target_value are required'}), 400
    
    if target_type not in ['movie', 'director', 'genre']:
        return jsonify({'error': 'Invalid target_type. Must be one of: movie, director, genre'}), 400
    
    like = Like.query.filter_by(user_id=user_id, target_type=target_type, target_value=target_value).first()
    if not like:
        return jsonify({'message': 'Like not found'}), 404
    
    db.session.delete(like)
    db.session.commit()
    return jsonify({'message': f'{target_type.capitalize()} unliked successfully'}), 200

@likes_bp.route('', methods=['GET'])
def get_liked_items():
    user_id, error = decode_token(request)
    if error:
        return jsonify({'error': error}), 401
    
    target_type = request.args.get('target_type')  # Optional filter by type
    
    if target_type and target_type not in ['movie', 'director', 'genre']:
        return jsonify({'error': 'Invalid target_type. Must be one of: movie, director, genre'}), 400
    
    query = Like.query.filter_by(user_id=user_id)
    if target_type:
        query = query.filter_by(target_type=target_type)
    
    likes = query.all()
    liked_items = [{'target_type': like.target_type, 'target_value': like.target_value} for like in likes]
    return jsonify({'liked_items': liked_items}), 200