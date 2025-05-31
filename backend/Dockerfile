FROM python:3.12.3-slim

WORKDIR /app

# 비root 사용자 생성 (보안 목적)
RUN useradd -m -u 1000 appuser

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 권한 설정
RUN chown -R appuser:appuser /app

# 비root 사용자로 실행
USER appuser

#환경변수 설정 (운영 환경)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

EXPOSE 5000

# 운영 환경에서는 Gunicorn 사용 (run.py 안에 app 객체가 있어야 함)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]