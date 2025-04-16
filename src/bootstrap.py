from src.config._container import Application
from pathlib import Path
from fastapi import FastAPI, APIRouter
import datetime
from src.databases.schema import get_mall_schema
from typing import List
from src.services.typesense._service import TypesenseService
from src.managers.typesense._manager import TypesenseManager


def create_app() -> FastAPI:
    """기본 FastAPI 앱 생성 및 동기적 설정"""

    return FastAPI(
        title="Search API",
        description="Search API",
        version="1.0.0",
    )


def create_collections(
    typesense_service: TypesenseService,
    mall_list: List[str],
):
    for mall in mall_list:
        mall_schema = get_mall_schema(mall)
        typesense_service.create_collection(mall_schema)


def configure_routes(app: FastAPI, controller) -> FastAPI:

    app.include_router(
        controller.register_routes(APIRouter()),
        prefix="/search",
    )

    @app.get("/", tags=["Root"])
    async def read_root():
        return {"message": "WELCOME TO SEARCH API SERVER", "status": "running"}

    @app.get("/health", tags=["Health Check"])
    async def health_check():
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat(),
            }

    return app


def get_mall_list():
    current_dir = Path(__file__).parent
    malls_dir = Path(current_dir, "databases", "malls")

    # JSON 파일들의 이름을 가져와서 .json 확장자 제거
    mall_list = [path.stem for path in malls_dir.glob("*.json")]
    return mall_list


def import_documents(typesense_manager: TypesenseManager, mall_list: List[str]):
    for mall in mall_list:
        current_dir = Path(__file__).parent
        fixture_path = Path(current_dir, "databases", "items", f"{mall}.jsonl")
        typesense_manager.import_documents(mall, fixture_path)


def bootstrap(application: Application):
    """Typesense 컬렉션을 생성하고 데이터를 import합니다.

    Args:
        application (Application): 애플리케이션 컨테이너
    """
    logger = application.logger()
    mall_list = get_mall_list()
    logger.info(f"Malls: {mall_list}")
    typesense_service = application.services.typesense_service()
    typesense_manager = application.managers.typesense_manager()
    create_collections(typesense_service, mall_list)
    import_documents(typesense_manager, mall_list)
    logger.info(f"Typesense Collections: {typesense_manager.get_collection_list()}")
    app = create_app()
    configure_routes(app, application.controllers().typesense_controller())
    return app
