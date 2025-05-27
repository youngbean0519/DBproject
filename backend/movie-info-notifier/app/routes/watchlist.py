from flask import Blueprint, request
from app import db
from app.models.watchlist import Watchlist
from app.models.movie import Movie
from app.utils import (
    decode_token, format_error_response, format_success_response, validate_required_fields
)

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/watchlist')

@watchlist_bp.route('', methods=['POST'])
def add_to_watchlist():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    data = request.get_json()
    is_valid, error = validate_required_fields(data, ['movie_id'])
    if not is_valid:
        return format_error_response(error)
    
    movie_id = data['movie_id']
    movie = Movie.query.filter_by(movie_id=movie_id).first()
    if not movie:
        return format_error_response('Movie not found', 404)
    
    existing = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing:
        return format_error_response('Movie already in watchlist', 400)
    
    entry = Watchlist(
        user_id=user_id,
        movie_id=movie.movie_id,
        movie_title=movie.title,
        director=movie.director,
        genre=movie.genre,
        actors=movie.actors,
        country=movie.country,
        movie_type=movie.movie_type,
        release_date=movie.release_date
    )
    db.session.add(entry)
    db.session.commit()
    
    return format_success_response('Movie added to watchlist')

@watchlist_bp.route('', methods=['GET'])
def get_watchlist():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    watchlist = Watchlist.query.filter_by(user_id=user_id).all()
    result = [{
        'movie_id': item.movie_id,
        'title': item.movie_title,
        'director': item.director,
        'genre': item.genre,
        'actors': item.actors.split(',') if item.actors else [],
        'country': item.country,
        'movie_type': item.movie_type,
        'release_date': item.release_date.isoformat() if item.release_date else None
    } for item in watchlist]

    return format_success_response('Watchlist retrieved', {'watchlist': result})

@watchlist_bp.route('/<movie_id>', methods=['DELETE'])
def remove_from_watchlist(movie_id):
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    item = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not item:
        return format_error_response('Movie not found in watchlist', 404)
    
    db.session.delete(item)
    db.session.commit()

    return format_success_response('Movie removed from watchlist')