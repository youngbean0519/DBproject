from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import os
import requests

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

@movies_bp.route('/search', methods=['GET'])
def search_movies():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'Missing "title" query parameter'}), 400
    
    api_key = os.getenv('KOFIC_API_KEY')
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {
        'key': api_key,
        'movieNm': title
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from KOFIC'}), 500
    
    data = response.json()
    movie_list = data.get('movieListResult', {}).get('movieList', [])
    results = []
    for movie in movie_list:
        results.append({
            'movie_code': movie.get('movieCd'),
            'title': movie.get('movieNm'),
            'open_date': movie.get('openDt'),
            'director': movie.get('directors'),
            'genre': movie.get('repGenreNm')
        })
    
    return jsonify({'results': results}), 200

@movies_bp.route('/now_showing', methods=['GET'])
def now_showing():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    api_key = os.getenv('KOFIC_API_KEY')
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        'key': api_key,
        'targetDt': yesterday
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch boxoffice data'}), 500
    
    data = response.json()
    box_office_list = data.get('boxOfficeResult', {}).get('dailyBoxOfficeList', [])
    results = []
    for entry in box_office_list:
        results.append({
            'rank': entry.get('rank'),
            'title': entry.get('movieNm'),
            'open_date': entry.get('openDt'),
            'audience': entry.get('audiAcc')
        })
    
    return jsonify({'now_showing': results}), 200

@movies_bp.route('/upcoming', methods=['GET'])
def upcoming():
    today = datetime.now()
    today_str = today.strftime('%Y%m%d')
    two_months_later = (today + timedelta(days=60)).strftime('%Y%m%d')  # 2개월 후
    
    api_key = os.getenv('KOFIC_API_KEY')
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    
    all_movies = []
    total_pages = 10  # 10페이지까지 검색
    
    for page in range(1, total_pages + 1):
        params = {
            'key': api_key,
            'itemPerPage': 100,
            'curPage': page
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            continue  # 한 페이지 실패해도 계속 진행
        
        data = response.json()
        movie_list = data.get('movieListResult', {}).get('movieList', [])
        all_movies.extend(movie_list)
    
    results = []
    for movie in all_movies:
        open_date = movie.get('openDt')
        if open_date and today_str < open_date <= two_months_later:  # 오늘부터 2개월 이내 개봉 영화만 포함
            results.append({
                'movie_code': movie.get('movieCd'),
                'title': movie.get('movieNm'),
                'open_date': open_date,
                'director': movie.get('directors'),
                'genre': movie.get('repGenreNm')
            })
    
    # 개봉일 순으로 정렬
    results.sort(key=lambda x: x['open_date'])
    
    return jsonify({'upcoming_movies': results}), 200
    