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
def like_movie():
    user_id, error = decode_token(request)
    if error:
        return jsonify({'error': error}), 401

    data = request.get_json()
    movie_id = data.get('movie_id')

    if not movie_id:
        return jsonify({'error': 'movie_id is required'}), 400
    
    existing = Like.query.filter_by(user_id=user_id, target_type='movie', target_value=movie_id).first()
    if existing:
        return jsonify({'message': 'Movie already liked'}), 200
    
    new_like = Like(user_id=user_id, target_type='movie', target_value=movie_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({'message': 'Movie liked successfully'}), 201

@likes_bp.route('', methods=['DELETE'])
def unlike_movie():
    user_id, error = decode_token(request)
    if error:
        return jsonify({'error': error}), 401
    
    data = request.get_json()
    movie_id = data.get('movie_id')
    if not movie_id:
        return jsonify({'error': 'movie_id is required'}), 400
    
    like = Like.query.filter_by(user_id=user_id, target_type='movie', target_value=movie_id).first()
    if not like:
        return jsonify({'message': 'LKike not found'}), 404
    
    db.session.delete(like)
    db.session.commit()
    return jsonify({'message': 'Like removed successfully'}), 200

@likes_bp.route('', methods=['GET'])
def get_liked_movies():
    user_id, error = decode_token(request)
    if error:
        return jsonify({'error': error}), 401
    
    likes = Like.query.filter_by(user_id=user_id, target_type='movie').all()
    liked_movies = [{'movie_id': like.target_value} for like in likes]
    return jsonify({'liked_movies': liked_movies}), 200