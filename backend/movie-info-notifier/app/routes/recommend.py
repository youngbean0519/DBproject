from flask import Blueprint, request
from app.utils import (
    decode_token, format_error_response, format_success_response
)
from app.models.recommendation import Recommendation
from app.models.movie import Movie
from app.services.recommender import generate_recommendations
from datetime import date

recommend_bp = Blueprint('recommend', __name__, url_prefix='/recommend')

@recommend_bp.route('', methods=['GET'])
def get_recommendations():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    generate_recommendations(user_id)
    recommendations = Recommendation.query.filter_by(user_id=user_id).all()
    results = []
    for rec in recommendations:
        movie = Movie.query.filter_by(movie_id=rec.movie_id).first()
        if not movie:
            continue
    
        tag = " [개봉 예정]" if movie.release_date > date.today() else ""
        results.append({
            'movie_id': movie.movie_id,
            'title': f"{movie.title}{tag}",
            'release_date': movie.release_date.strftime('%Y-%m-%d'),
            'reason': rec.reason
        })
    
    return format_success_response("Recommendations retrieved", {'recommendations': results})
