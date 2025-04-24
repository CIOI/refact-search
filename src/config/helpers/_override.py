from typing import TYPE_CHECKING
from os.path import join, dirname, abspath

if TYPE_CHECKING:
    from src.config import Application


def mock_overrides(application: "Application") -> "Application":

    # 프로젝트 루트 디렉토리의 절대 경로 얻기
    project_root = dirname(dirname(dirname(dirname(abspath(__file__)))))
    credentials_path = join(project_root, "key.json")
    # 기존 Environment 객체 복사
    original_env = application.environment()

    # 필요한 필드만 오버라이드
    overridden_env = original_env.model_copy(
        update={
            "TYPESENSE_HOST": "localhost",
            "QDRANT_HOST": "localhost",
            "GOOGLE_APPLICATION_CREDENTIALS": credentials_path,
        }
    )
    # 오버라이드된 환경 설정
    application.environment.override(overridden_env)
    return application
