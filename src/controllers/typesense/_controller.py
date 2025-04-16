from fastapi import APIRouter, HTTPException
from typing import Optional
from src.services import TypesenseService
from src.config._logger import LoggerService


class TypesenseController:
    """검색 컨트롤러 클래스

    Attributes:
        service (TypesenseService): 검색 서비스
    """

    def __init__(self, service: TypesenseService, logger: LoggerService):
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

        # 자동완성 엔드포인트
        router.add_api_route(
            path="/suggestions",
            endpoint=self.get_suggestions,
            methods=["GET"],
            summary="검색어 자동완성",
            description="검색어에 대한 자동완성 제안을 제공합니다.",
        )

        return router

    def search(
        self,
        query: str,
        mall_id: str,
        page: int = 1,
        per_page: int = 10,
        filter_by: Optional[str] = None,
        sort_by: Optional[str] = None,
    ):
        """상품 검색 API

        Args:
            query (str): 검색어
            mall_id (str): 몰 ID (mall1 또는 mall2)
            page (int): 페이지 번호
            per_page (int): 페이지당 결과 수
            filter_by (Optional[str]): 필터 조건
            sort_by (Optional[str]): 정렬 조건

        Returns:
            Dict: 검색 결과

        Raises:
            HTTPException: 검색 실패 시
        """
        try:
            return self.service.search(
                query=query,
                mall_id=mall_id,
                page=page,
                per_page=per_page,
                filter_by=filter_by,
                sort_by=sort_by,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    def get_suggestions(self, query: str, mall_id: str):
        """검색어 자동완성 API

        Args:
            query (str): 검색어
            mall_id (str): 몰 ID (mall1 또는 mall2)

        Returns:
            List[str]: 자동완성 제안 목록

        Raises:
            HTTPException: 자동완성 실패 시
        """
        try:
            return self.service.get_suggestions(
                query=query,
                mall_id=mall_id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get suggestions: {str(e)}"
            )
