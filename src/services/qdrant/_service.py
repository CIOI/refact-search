# src/services/_service.py
from typing import Dict, List, Optional
from src.managers.qdrant import QdrantManager
from src.config._logger import LoggerService
from src.embedding import ClipEmbeddingModel


class QdrantService:
    """검색 서비스 클래스

    Attributes:
        qdrant_manager (QdrantManager): Qdrant 매니저
        logger (LoggerService): 로깅 서비스
    """

    def __init__(
        self,
        qdrant_manager: QdrantManager,
        embedding_model: ClipEmbeddingModel,
        logger: LoggerService,
    ):
        self.qdrant_manager = qdrant_manager
        self.embedding_model = embedding_model
        self.logger = logger

    def search(
        self,
        query: str,
        mall_id: str,
        page: int = 1,
        per_page: int = 10,
        filter_by: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> Dict:
        """상품 검색

        Args:
            query (str): 검색어
            mall_id (str): 몰 ID (mall1 또는 mall2)
            page (int): 페이지 번호
            per_page (int): 페이지당 결과 수
            filter_by (Optional[str]): 필터 조건
            sort_by (Optional[str]): 정렬 조건

        Returns:
            Dict: 검색 결과
        """
        try:
            search_parameters = {
                "q": query,
                "query_by": "name,description",
                "page": page,
                "per_page": per_page,
            }

            if filter_by:
                search_parameters["filter_by"] = filter_by
            if sort_by:
                search_parameters["sort_by"] = sort_by

            results = self.typesense_manager.client.collections[
                mall_id
            ].documents.search(search_parameters)

            self.logger.info(f"Search completed for query: {query} in mall: {mall_id}")
            return results
        except Exception as e:
            self.logger.error(
                f"Search failed for query: {query} in mall: {mall_id}, error: {str(e)}"
            )
            raise

    def get_suggestions(self, query: str, mall_id: str) -> List[str]:
        """검색어 자동완성

        Args:
            query (str): 검색어
            mall_id (str): 몰 ID (mall1 또는 mall2)

        Returns:
            List[str]: 자동완성 제안 목록
        """
        try:
            results = self.typesense_manager.client.collections[
                mall_id
            ].documents.search(
                {"q": query, "query_by": "name", "per_page": 5, "prefix": True}
            )

            suggestions = [hit["document"]["name"] for hit in results["hits"]]
            self.logger.info(
                f"Suggestions generated for query: {query} in mall: {mall_id}"
            )
            return suggestions
        except Exception as e:
            self.logger.error(
                f"Failed to generate suggestions for query: {query} in mall: {mall_id}, error: {str(e)}"
            )
            raise
