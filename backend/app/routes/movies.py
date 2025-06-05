from flask import Blueprint, request
from app import db
from app.models.movie import Movie
from datetime import datetime, timedelta
import os
import requests
from app.utils import (
    format_error_response, format_success_response,
    validate_required_fields, get_date_range, get_movie_metadata
)

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

KOBIS_API_BASE_URL = "https://www.kobis.or.kr/kobisopenapi/webservice/rest"

def get_kobis_api_key():
    """KOBIS API 키를 가져옵니다."""
    api_key = os.getenv('KOFIC_API_KEY')
    if not api_key:
        raise RuntimeError("KOFIC_API_KEY is not set")
    return api_key

@movies_bp.route('/search', methods=['GET'])
def search_movies():
    title = request.args.get('title')
    if not title:
        return format_error_response('Missing "title" query parameter')
    
    api_key = get_kobis_api_key()
    url = f"{KOBIS_API_BASE_URL}/movie/searchMovieList.json"
    params = {
        'key': api_key,
        'movieNm': title,
        'itemPerPage': 10
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return format_error_response('Failed to fetch data from KOBIS API', 500)
    
    try:
        data = response.json()
    except ValueError:
        return format_error_response('Invalid response from KOBIS API', 500)
    
    movie_list = data.get('movieListResult', {}).get('movieList', [])
    
    if not movie_list:
        return format_success_response('No movies found', {'results': []})
    
    results = []
    for movie in movie_list:
        movie_code = movie.get('movieCd')
        if not movie_code:
            continue
            
        # 영화 상세 정보 가져오기
        metadata, error = get_movie_metadata(movie_code)
        if error:
            print(f"Error fetching metadata for movie {movie_code}: {error}")
            continue
            
        movie_data = {
            'movie_code': movie_code,
            'title': movie.get('movieNm'),
            'director': metadata.get('director', '미상'),
            'actors': metadata.get('actors', []),
            'genre': metadata.get('genre', '기타'),
            'movie_type': metadata.get('movie_type', '장편'),
            'country': metadata.get('country', '미상'),
            'open_date': movie.get('openDt')
        }
        results.append(movie_data)
    
    if not results:
        return format_success_response('No movies found', {'results': []})
        
    return format_success_response('Movies found', {'results': results})

@movies_bp.route('/now_showing', methods=['GET'])
def now_showing():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    api_key = get_kobis_api_key()
    url = f"{KOBIS_API_BASE_URL}/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        'key': api_key,
        'targetDt': yesterday
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching boxoffice data: {str(e)}")
        return format_error_response('Failed to fetch boxoffice data', 500)
    
    data = response.json()
    box_office_list = data.get('boxOfficeResult', {}).get('dailyBoxOfficeList', [])
    results = []
    
    for entry in box_office_list:
        movie_code = entry.get('movieCd')
        metadata, error = get_movie_metadata(movie_code)
        if error or not metadata:
            continue

        results.append({
            'rank': entry.get('rank'),
            'movie_code': movie_code,
            'title': metadata['title'],
            'director': metadata['director'],
            'actors': metadata['actors'][:5],
            'genre': metadata['genre'],
            'movie_type': metadata['movie_type'],
            'country': metadata['country'],
            'open_date': entry.get('openDt'),
            'audience': entry.get('audiAcc')
        })
    
    return format_success_response('Now showing movies retrieved', {'now_showing': results})

@movies_bp.route('/upcoming', methods=['GET'])
def upcoming():
    today = datetime.now().date()
    three_months_later = today + timedelta(days=90)

    Movie.query.filter(Movie.release_date < today).delete()

    api_key = get_kobis_api_key()
    url = f"{KOBIS_API_BASE_URL}/movie/searchMovieList.json"
    
    all_movies = []
    total_pages = 10  # 10페이지까지 검색
    
    for page in range(1, total_pages + 1):
        params = {
            'key': api_key,
            'itemPerPage': 100,
            'curPage': page
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            continue

    
        data = response.json()
        movie_list = data.get('movieListResult', {}).get('movieList', [])
        all_movies.extend(movie_list)
    
    results = []
    for movie in all_movies:
        try:
            open_date = datetime.strptime(movie.get('openDt'), '%Y%m%d').date()
        except (ValueError, TypeError):
            continue
        
        if not (today <= open_date <= three_months_later):
            continue
        
        movie_code = movie.get('movieCd')
        metadata, error = get_movie_metadata(movie_code)
        if error or not metadata:
            continue

        # DB 저장
        existing = Movie.query.filter_by(movie_id=movie_code).first()
        if existing:
            # 기존 영화 정보 업데이트
            existing.title = metadata['title']
            existing.genre = metadata['genre']
            existing.director = metadata['director']
            existing.release_date = metadata['release_date']
            existing.actors = ','.join(metadata['actors'])
            existing.country = metadata['country']
            existing.movie_type = metadata['movie_type']
            
        else:    
            new_movie = Movie(
                movie_id=movie_code,
                title=metadata['title'],
                genre=metadata['genre'],
                director=metadata['director'],
                release_date=metadata['release_date'],
                actors=','.join(metadata['actors']),
                country=metadata['country'],
                movie_type=metadata['movie_type']
            )
            db.session.add(new_movie)

        results.append({
            'movie_code': movie_code,
            'title': metadata['title'],
            'director': metadata['director'],
            'actors': metadata['actors'][:5],
            'genre': metadata['genre'],
            'movie_type': metadata['movie_type'],
            'country': metadata['country'],
            'open_date': open_date.strftime('%Y-%m-%d')
        })
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # 롤백 추가
        if 'duplicate key value violates unique constraint' in str(e):
            # 중복 에러는 무시하고 진행
            pass
        else:
            return format_error_response(f'Database error: {str(e)}', 500)
    
    # 개봉일 순으로 정렬
    results.sort(key=lambda x: x['open_date'])
    return format_success_response('Upcoming movies retrieved', {'upcoming_movies': results})

