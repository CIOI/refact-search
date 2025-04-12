# Python 3.11 slim 기반 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 의존성 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 소스 코드 복사
COPY . .

# 환경 변수 파일 복사
COPY .env .env

# 포트 노출
EXPOSE 8100

# 실행 명령
CMD ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8100"]