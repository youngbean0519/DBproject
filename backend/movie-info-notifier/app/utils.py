from flask import jsonify
import jwt
import os
import datetime

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
