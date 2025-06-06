from flask import Blueprint, request
from app import db
from app.models.like import Like
from app.models.movie import Movie
from app.utils import (
    decode_token, format_error_response,
    format_success_response, validate_required_fields, get_movie_metadata
)

likes_bp = Blueprint('likes', __name__, url_prefix='/likes')

@likes_bp.route('', methods=['POST'])
def like_movie():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)

    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['movie_id'])
    if not is_valid:
        return format_error_response(error_message)

    reasons = data.get('reasons', [])
    if not isinstance(reasons, list):
        return format_error_response("Reasons must be a list")

    enriched_reasons = []
    if reasons:
        metadata, error = get_movie_metadata(data['movie_id'])
        if error:
            return format_error_response(error)
        for r in reasons:
            if r == 'director' and metadata.get('director'):
                enriched_reasons.append({"type": "director", "value": metadata['director']})
            elif r == 'genre' and metadata.get('genre'):
                enriched_reasons.append({"type": "genre", "value": metadata['genre']})
            elif r == 'type' and metadata.get('movie_type'):
                enriched_reasons.append({"type": "type", "value": metadata['movie_type']})
            elif r == 'country' and metadata.get('country'):
                enriched_reasons.append({"type": "country", "value": metadata['country']})
            elif r == 'actor' and metadata.get('actors'):
                for actor in metadata['actors']:
                    enriched_reasons.append({"type": "actor", "value": actor})

    # 중복 체크
    existing = Like.query.filter_by(user_id=user_id, movie_id=data['movie_id']).first()
    if existing:
        return format_success_response("Movie already liked")

    new_like = Like(
        user_id=user_id,
        movie_id=data['movie_id'],
        reasons=enriched_reasons
    )
    db.session.add(new_like)
    db.session.commit()

    return format_success_response("Movie liked successfully", status_code=201)

@likes_bp.route('/delete', methods=['POST'])
def unlike_movie():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['movie_id'])
    if not is_valid:
        return format_error_response(error_message)
    
    like = Like.query.filter_by(user_id=user_id, movie_id=data['movie_id']).first()
    if not like:
        return format_error_response('Like not found', 404)
    
    db.session.delete(like)
    db.session.commit()
    
    return format_success_response("Movie unliked successfully")

@likes_bp.route('', methods=['GET'])
def get_liked_movies():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    likes = Like.query.filter_by(user_id=user_id).all()
    liked_items = []
    for like in likes:
        metadata, error = get_movie_metadata(like.movie_id)
        if error:
            liked_items.append({
                'movie_id': like.movie_id,
                'reasons': like.reasons,
                'title': '제목 없음'
            })
        else:
            liked_items.append({
                'movie_id': like.movie_id,
                'reasons': like.reasons,
                'title': metadata.get('title', '제목 없음')
            })
    return format_success_response('Liked movies retrieved successfully', {'liked_items': liked_items})