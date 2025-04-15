from src.config._container import Application
from pathlib import Path
import json
from fastapi import FastAPI, APIRouter
import datetime


def create_app() -> FastAPI:
    """기본 FastAPI 앱 생성 및 동기적 설정"""

    app = FastAPI(
        title="Search API",
        description="Search API",
        version="1.0.0",
    )
    return app


def create_collections(manager):
    # 스키마 파일 로드
    schema_path = Path("src/mall/schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schemas = json.load(f)
    typesense_manager = manager.typesense_manager()
    # mall1 (even) 생성 및 데이터 import
    mall1_schema = next(schema for schema in schemas if schema["name"] == "mall1")
    typesense_manager.create_collection(mall1_schema)
    typesense_manager.import_documents(
        collection_name="mall1",
        fixture_path=Path("preprocessing/fixtures/consolidated_products_even.jsonl"),
    )

    # mall2 (odd) 생성 및 데이터 import
    mall2_schema = next(schema for schema in schemas if schema["name"] == "mall2")
    typesense_manager.create_collection(mall2_schema)
    typesense_manager.import_documents(
        collection_name="mall2",
        fixture_path=Path("preprocessing/fixtures/consolidated_products_odd.jsonl"),
    )


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


def bootstrap(application: Application):
    """Typesense 컬렉션을 생성하고 데이터를 import합니다.

    Args:
        application (Application): 애플리케이션 컨테이너
    """
    manager = application.managers()
    create_collections(manager)
    app = create_app()
    configure_routes(app, application.search_controller())
    return app
