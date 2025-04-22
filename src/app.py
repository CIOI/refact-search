import logging
from .bootstrap import bootstrap
from src.config._container import Application


def create_app():
    application = Application()
    # 로거 설정
    logger = application.logger()
    environment = Application.environment()
    # 환경변수 로드
    logger.info(f"Current settings: {environment}")

    # 모든 로거의 기본 레벨을 INFO로 설정
    logging.getLogger().setLevel(logging.INFO)

    # 특정 라이브러리 로거의 레벨도 INFO로 설정
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)
    logging.getLogger("selenium").setLevel(logging.INFO)

    # 애플리케이션 컨테이너 생성 및 앱 부트스트랩
    return bootstrap(application)


# 앱 인스턴스 생성
app = create_app()
