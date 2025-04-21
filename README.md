# keyword-search
Typesense와 Qdrant를 활용한 하이브리드 검색 시스템을 제공합니다.

## 구조
- **Manager**: 외부 서비스(Typesense, Qdrant)와의 연결 관리
- **Service**: 비즈니스 로직 구현
- **Controller**: HTTP 요청을 처리하는 API 엔드포인트 계층

## 시스템 구성
### 1. FastAPI 서버 (port: 8100)
검색 기능 테스트와 실시간 데이터 추가를 위한 API를 제공합니다.
- Typesense 키워드 검색 API
- Qdrant 벡터 검색 API
- 데이터 동기화 및 관리 API

### 2. Streamlit 대시보드
서비스 테스트를 위한 웹 인터페이스를 제공합니다.
- 통합 검색 인터페이스
- 실시간 검색 결과 시각화
- 이미지 및 텍스트 검색 지원

### 3. 검색 엔진
- **Typesense** (port: 8108): 키워드 기반 검색
- **Qdrant** (port: 6333, 6334): 벡터 기반 검색

## 실행 방법

### 1. 환경 설정
.env 파일을 root directory에 위치시켜주세요
없다면 rhkr9693@gmail.com 으로 요청주세요

### 2. Docker 실행
```bash
# 모든 서비스 실행
docker-compose up -d
```

### 3. FastAPI 서버 실행
```bash
# 직접 실행
python -m src.app

# 또는 Docker로 실행
docker-compose up -d api
```
- API 문서: http://localhost:8100/docs

### 4. Streamlit 대시보드 실행
```bash
streamlit run src/streamlit.py
```

### company_a를 8501 포트에서 실행
```bash
streamlit run src/streamlit.py --server.port 8501 --mall_id company_a
```

### 다른 터미널에서 company_b를 8502 포트에서 실행
```
streamlit run src/streamlit.py --server.port 8502 --mall_id company_b
```
- 대시보드: http://localhost:8501

## 서비스 포트
- FastAPI: 8100
- Typesense: 8108
- Qdrant: 6333(API), 6334(Web)
- Streamlit: 8501
