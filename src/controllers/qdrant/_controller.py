from fastapi import APIRouter, HTTPException
from src.services import QdrantService
from src.config._logger import LoggerService


class QdrantController:
    """검색 컨트롤러 클래스

    Attributes:
        service (QdrantService): 검색 서비스
    """

    def __init__(self, service: QdrantService, logger: LoggerService):
        self.service = service
        self.logger = logger

    def register_routes(self, router: APIRouter) -> APIRouter:
        """FastAPI 라우터에 엔드포인트 등록

        Args:
            router (APIRouter): FastAPI 라우터

        Returns:
            APIRouter: 등록된 라우터
        """
        # 검색 엔드포인트
        router.add_api_route(
            path="/search",
            endpoint=self.search,
            methods=["GET"],
            summary="상품 검색",
            description="상품을 검색합니다.",
        )
        router.add_api_route(
            path="/data-count",
            endpoint=self.check_data_count,
            methods=["GET"],
            summary="데이터 현황",
            description="데이터 현황을 확인합니다.",
        )

        return router

    async def search(
        self,
        query: str,
        mall_id: str,
    ):
        """상품 검색 API

        Args:
            query (str): 검색어
            mall_id (str): 몰 ID (mall1 또는 mall2)


        Returns:
            Dict: 검색 결과

        Raises:
            HTTPException: 검색 실패 시
        """
        try:
            return await self.service.search(
                query=query,
                mall_id=mall_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    def check_data_count(self):
        """데이터 현황 확인"""
        return self.service.check_data_count()
