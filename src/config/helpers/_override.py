from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import Application


def mock_overrides(application: "Application") -> "Application":

    # 기존 Environment 객체 복사
    original_env = application.environment()

    # 필요한 필드만 오버라이드
    overridden_env = original_env.model_copy(
        update={
            "TYPESENSE_HOST": "localhost",
            "QDRANT_HOST": "localhost",
        }
    )
    # 오버라이드된 환경 설정
    application.environment.override(overridden_env)
    return application
