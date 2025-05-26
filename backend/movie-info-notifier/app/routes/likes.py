from flask import Blueprint, request
from app import db
from app.models.like import Like
from app.models.movie import Movie
from app.utils import (
    decode_token, validate_target_type, format_error_response,
    format_success_response, validate_required_fields, check_movie_not_exists, get_movie_metadata
)

likes_bp = Blueprint('likes', __name__, url_prefix='/likes')

@likes_bp.route('', methods=['POST'])
def like_item():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)

    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['target_type', 'target_value'])
    if not is_valid:
        return format_error_response(error_message)
    
    reasons = data.get('reasons', [])
    if data['target_type'] == 'movie' and not isinstance(reasons, list):
        return format_error_response("Reasons must be a list when liking a movie")

    if not validate_target_type(data['target_type']):
        return format_error_response('Invalid target_type. Must be one of: movie, director, genre')
    
    if data['target_type'] == 'movie':
        not_exists, movie_error = check_movie_not_exists(data['target_value'])
        if not not_exists:
            return format_error_response(movie_error, 400)
        
        enriched_reasons = []
        if reasons:
            metadata, error = get_movie_metadata(data['target_value'])
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
        
    else:
        enriched_reasons = None
    
    existing = Like.query.filter_by(
        user_id=user_id,
        target_type=data['target_type'],
        target_value=data['target_value']
    ).first()
    
    if existing:
        return format_success_response(f"{data['target_type'].capitalize()} already liked")
    
    new_like = Like(
        user_id=user_id,
        target_type=data['target_type'],
        target_value=data['target_value'],
        reasons=enriched_reasons
    )
    db.session.add(new_like)
    db.session.commit()

    return format_success_response(
        f"{data['target_type'].capitalize()} liked successfully",
        status_code=201
    )

@likes_bp.route('', methods=['DELETE'])
def unlike_item():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    data = request.get_json()
    is_valid, error_message = validate_required_fields(data, ['target_type', 'target_value'])
    if not is_valid:
        return format_error_response(error_message)
    
    if not validate_target_type(data['target_type']):
        return format_error_response('Invalid target_type. Must be one of: movie, director, genre')
    
    like = Like.query.filter_by(
        user_id=user_id,
        target_type=data['target_type'],
        target_value=data['target_value']
    ).first()
    
    if not like:
        return format_error_response('Like not found', 404)
    
    db.session.delete(like)
    db.session.commit()
    
    return format_success_response(f"{data['target_type'].capitalize()} unliked successfully")

@likes_bp.route('', methods=['GET'])
def get_liked_items():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    target_type = request.args.get('target_type')
    
    if target_type and not validate_target_type(target_type):
        return format_error_response('Invalid target_type. Must be one of: movie, director, genre')
    
    query = Like.query.filter_by(user_id=user_id)
    if target_type:
        query = query.filter_by(target_type=target_type)
    
    likes = query.all()
    liked_items = [{'target_type': like.target_type, 'target_value': like.target_value} for like in likes]
    
    return format_success_response('Liked items retrieved successfully', {'liked_items': liked_items})