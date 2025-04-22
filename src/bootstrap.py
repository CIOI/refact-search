from src.config._container import Application
from fastapi import FastAPI, APIRouter
import datetime
from src.databases.schema import get_mall_list
from src.controllers import TypesenseController, QdrantController


def create_app() -> FastAPI:
    """기본 FastAPI 앱 생성 및 동기적 설정"""

    return FastAPI(
        title="Search API",
        description="Search API",
        version="1.0.0",
    )


def configure_routes(
    app: FastAPI,
    typesense_controller: TypesenseController,
    qdrant_controller: QdrantController,
) -> FastAPI:

    typesense_router = APIRouter(prefix="/typesense", tags=["Typesense"])
    typesense_controller.register_routes(typesense_router)
    app.include_router(typesense_router)

    qdrant_router = APIRouter(prefix="/qdrant", tags=["Qdrant"])
    qdrant_controller.register_routes(qdrant_router)
    app.include_router(qdrant_router)

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
    logger = application.logger()
    controller = application.controllers()
    typesense_manager = application.managers.typesense_manager()
    qdrant_manager = application.managers.qdrant_manager()
    typesense_collections = typesense_manager.get_collection_list()
    qdrant_collections = qdrant_manager.get_collection_list()
    mall_list = get_mall_list()
    logger.info(f"Malls: {mall_list}")
    logger.info(f"Typesense Collections: {typesense_collections}")
    logger.info(f"Qdrant Collections: {qdrant_collections}")
    if any(mall not in typesense_collections for mall in mall_list):
        logger.warning(f"index.py 를 통해 {mall_list} 컬렉션을 추가해 주세요")
    app = create_app()
    configure_routes(
        app,
        controller.typesense_controller(),
        controller.qdrant_controller(),
    )
    return app
