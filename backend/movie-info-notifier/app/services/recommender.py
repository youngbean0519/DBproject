from app.models.movie import Movie
from app.models.recommendation import Recommendation
from app.models.like import Like
from app.utils import get_movie_metadata
from app import db
from datetime import date

def extract_user_preferences(user_id):
    """사용자의 좋아요 기반 취향을 집계"""
    likes = Like.query.filter_by(user_id=user_id).all()
    preferences = {
        'genres': set(),
        'directors': set(),
        'actors': set(),
        'countries': set(),
        'types': set()
    }

    for like in likes:
        if like.target_type == 'genre':
            preferences['genres'].add(like.target_value)

        elif like.target_type == 'director':
            preferences['directors'].add(like.target_value)

        elif like.target_type == 'movie':
            if not like.reasons:
                continue
            
            metadata, error = get_movie_metadata(like.target_value)
            if error or not metadata:
                continue;
            
            for reason in like.reasons:
                reason_type = reason.get("type")
                value = reason.get("value")

                if reason_type == "genre" and metadata.get("genre") == value:
                    preferences['genres'].add(value)

                elif reason_type == "director" and metadata.get("director") == value:
                    preferences['directors'].add(value)

                elif reason_type == "actor" and value in metadata.get("actors", []):
                    preferences['actors'].add(value)

                elif reason_type == "country" and metadata.get("country") == value:
                    preferences['countries'].add(value)

                elif reason_type == "type" and metadata.get("movie_type") == value:
                    preferences['types'].add(value)
    
    return preferences

def calculate_score(movie, preferences):
    score = 0
    reasons = []

    if movie.genre in preferences['genres']:
        score += 3
        reasons.append(f"genre: {movie.genre}")
    
    if movie.director in preferences['directors']:
        score += 2
        reasons.append(f"director: {movie.director}")
    
    if movie.country in preferences['countries']:
        score += 1
        reasons.append(f"country: {movie.country}")
    
    if movie.movie_type in preferences['types']:
        score += 1
        reasons.append(f"type: {movie.movie_type}")
    
    if movie.actors in preferences['actors']:
        for actor in movie.actors.split(','):
            if actor.strip() in preferences['actors']:
                score += 2
                reasons.append(f"actor: {actor.strip()}")
                break
    
    return score, "; ".join(reasons)

def generate_recommendations(user_id):
    Recommendation.query.filter_by(user_id=user_id).delete()

    preferences = extract_user_preferences(user_id)

    liked_movies = Like.query.filter_by(user_id=user_id, target_type='movie').with_entities(Like.target_value).all()
    liked_movies_ids = {movie_id for (movie_id, ) in liked_movies}
    candidates = Movie.query.all()

    for movie in candidates:
        if str(movie.movie_id) in liked_movies_ids:
            continue
        
        score, reason = calculate_score(movie, preferences)
        if score > 0:
            print(f"Adding recommendation: {movie.title}, score: {score}, reason: {reason}")
            rec = Recommendation(
                user_id=user_id,
                movie_id=movie.movie_id,
                reason=reason
            )
            db.session.add(rec)
    
    db.session.commit()
    print("Recommendations generated successfully")