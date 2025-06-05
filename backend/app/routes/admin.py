from flask import Blueprint, request
from app.utils import decode_token, format_error_response, format_success_response
from app.services.mailer import MovieMailer
from app.models.user import User
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin(user_id: int) -> bool:
    """사용자가 관리자인지 확인합니다."""
    admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    return user_id in admin_ids

@admin_bp.route('/send-notifications', methods=['POST'])
def send_notifications():
    # 관리자 권한 확인
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    
    if not is_admin(user_id):
        return format_error_response('관리자 권한이 필요합니다', 403)
    
    # 주간 알림 전송
    mailer = MovieMailer()
    results = mailer.send_weekly_notifications()
    
    return format_success_response(
        '알림 전송 완료',
        {
            'total_users': results['total_users'],
            'successful_sends': results['successful_sends'],
            'failed_sends': results['failed_sends']
        }
    )

@admin_bp.route('/check', methods=['GET'])
def check_admin():
    user_id, error = decode_token(request)
    if error:
        return format_error_response(error, 401)
    return format_success_response('ok', {'is_admin': is_admin(user_id)})