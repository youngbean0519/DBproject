from flask import jsonify
from app.models.movie import Movie
from datetime import date
import jwt
import os
import datetime
import requests

def decode_token(request):
    """JWT 토큰을 디코딩하여 user_id를 반환합니다."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, 'Missing token'
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        return payload['user_id'], None
    except Exception as e:
        return None, str(e)

def generate_token(user_id):
    """사용자 ID를 기반으로 JWT 토큰을 생성합니다."""
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, os.getenv('SECRET_KEY'), algorithm='HS256')

def validate_target_type(target_type):
    """좋아요 대상 타입이 유효한지 검증합니다."""
    valid_types = ['movie', 'director', 'genre']
    return target_type in valid_types

def format_error_response(message, status_code=400):
    """에러 응답을 포맷팅합니다."""
    return jsonify({'error': message}), status_code

def format_success_response(message, data=None, status_code=200):
    """성공 응답을 포맷팅합니다."""
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code

def get_date_range(days):
    """현재 날짜로부터 지정된 일수만큼의 날짜 범위를 반환합니다."""
    today = datetime.datetime.now()
    return today.strftime('%Y%m%d'), (today + datetime.timedelta(days=days)).strftime('%Y%m%d')

def validate_required_fields(data, required_fields):
    """필수 필드가 있는지 검증합니다."""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

def check_movie_not_exists(movie_id):
    """영화가 데이터베이스에 존재하지 않는지 확인합니다."""
    movie = Movie.query.filter_by(movie_id=movie_id).first()
    if movie:
        return False, "This movie is already in upcoming movies list"
    return True, None

def get_movie_metadata(movie_id):
    """영화 정보를 가져옵니다."""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {
        'key': os.getenv('KOFIC_API_KEY'),
        'movieCd': movie_id
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie metadata: {str(e)}")
        return None, f'Failed to fetch movie info from KOBIS: {str(e)}'
    
    try:
        data = response.json()
    except ValueError as e:
        print(f"Error parsing JSON response: {str(e)}")
        return None, 'Invalid JSON response from KOBIS'
    
    movie_info = data.get('movieInfoResult', {}).get('movieInfo', {})
    if not movie_info:
        return None, 'No movieInfo in API response'
    
    try:
        return {
            'title': movie_info.get('movieNm'),
            'genre': movie_info.get('genres')[0]['genreNm'] if movie_info.get('genres') else None,
            'director': movie_info.get('directors')[0]['peopleNm'] if movie_info.get('directors') else None,
            'actors': [a['peopleNm'] for a in movie_info.get('actors', [])[:5]],
            'country': movie_info.get('nations')[0]['nationNm'] if movie_info.get('nations') else None,
            'movie_type': movie_info.get('typeNm') if movie_info.get('typeNm') else None,
            'release_date': (
                datetime.datetime.strptime(movie_info.get('openDt'), '%Y%m%d').date()
                if movie_info.get('openDt') else None
            )
        }, None
    except Exception as e:
        print(f"Error parsing movie metadata: {str(e)}")
        return None, f'Failed to parse movie metadata: {str(e)}'