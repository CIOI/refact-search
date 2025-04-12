# keyword-search
Typesense를 활용한 keyword-search api 를 제공합니다.
# Structure
Manager : 외부 서비스(예: Typesense, Redis)와의 연결

Service : 비즈니스 로직을 구현

Controlloer : HTTP 요청을 처리하는 API 엔드포인트 계층
