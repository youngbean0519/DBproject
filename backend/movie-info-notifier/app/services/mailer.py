import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.watchlist import Watchlist
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MovieMailer:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    def get_upcoming_movies_for_user(self, user_id: int) -> List[Dict]:
        """사용자의 watchlist에서 다음 7일 내 개봉 예정인 영화들을 반환합니다."""
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        upcoming_movies = Watchlist.query.filter(
            Watchlist.user_id == user_id,
            Watchlist.release_date >= today,
            Watchlist.release_date <= next_week
        ).all()
        
        return [{
            'title': movie.movie_title,
            'release_date': movie.release_date.strftime('%Y-%m-%d'),
            'director': movie.director,
            'genre': movie.genre
        } for movie in upcoming_movies]

    def create_email_content(self, movies: List[Dict]) -> str:
        """이메일 내용을 생성합니다."""
        if not movies:
            return "다음 7일 내에 개봉 예정인 영화가 없습니다."
        
        content = "다음 7일 내에 개봉 예정인 영화 목록입니다:\n\n"
        for movie in movies:
            content += f"제목: {movie['title']}\n"
            content += f"개봉일: {movie['release_date']}\n"
            content += f"감독: {movie['director']}\n"
            content += f"장르: {movie['genre']}\n"
            content += "-" * 50 + "\n"
        
        return content

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """이메일을 전송합니다."""
        try:
            if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
                logger.error("SMTP 설정이 완료되지 않았습니다.")
                return False
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'plain'))
            
            # SMTP 서버 연결 및 이메일 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            logger.error(f"이메일 전송 중 오류 발생: {str(e)}")
            return False

    def send_weekly_notifications(self) -> Dict[str, int]:
        """모든 수신 동의 사용자에게 주간 알림을 전송합니다."""
        # 이메일 수신 동의한 사용자 조회
        users = User.query.filter_by(notify_by_email=True).all()
        
        results = {
            'total_users': len(users),
            'successful_sends': 0,
            'failed_sends': 0
        }
        
        for user in users:
            # 사용자의 watchlist에서 다음 7일 내 개봉 예정 영화 조회
            upcoming_movies = self.get_upcoming_movies_for_user(user.user_id)
            
            if not upcoming_movies:
                continue
            
            # 이메일 내용 생성
            content = self.create_email_content(upcoming_movies)
            
            # 이메일 전송
            if self.send_email(
                to_email=user.email,
                subject="다음 주 개봉 예정 영화 알림",
                content=content
            ):
                results['successful_sends'] += 1
            else:
                results['failed_sends'] += 1
        
        return results
