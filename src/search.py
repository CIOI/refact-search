from src.services import TypesenseService, QdrantService
from src.embedding import ClipEmbeddingModel
from typing import Tuple
from src.config._logger import LoggerService


class SearchService:
    def __init__(
        self,
        typesense_service: TypesenseService,
        embedding_service: ClipEmbeddingModel,
        qdrant_service: QdrantService,
        mall_id: str,
        logger: LoggerService,
    ):
        self.typesense_service = typesense_service
        self.embedding_service = embedding_service
        self.mall_id = mall_id
        self.qdrant_service = qdrant_service
        self.logger: LoggerService = logger

    async def search(self, query: str):
        typesense_results = self._search_typesense(query)
        qdrant_results = await self._search_qdrant(query)
        typesense_ids = [result[0] for result in typesense_results]
        qdrant_ids = [result[0] for result in qdrant_results]
        self.logger.info(f"Number of Typesense results: {len(typesense_results)}")
        self.logger.info(f"Number of Qdrant results: {len(qdrant_results)}")
        self.logger.info(f"Typesense results: {typesense_ids}")
        self.logger.info(f"Qdrant results: {qdrant_ids}")
        results = self._merge_results(typesense_results, qdrant_results)
        self.logger.info(f"Number of merged results: {len(results)}")
        return results

    def _search_typesense(self, query: str) -> list[Tuple[int, dict]]:
        results = self.typesense_service.search(
            query=query,
            mall_id=self.mall_id,
        )
        items = [hit["document"] for hit in results["hits"]]
        return [(item["product_id"], item) for item in items]

    async def _search_qdrant(self, query: str) -> list[Tuple[int, dict]]:
        results = await self.qdrant_service.search(
            query=query,
            mall_id=self.mall_id,
        )
        return [(result.id, result.payload) for result in results]

    def _merge_results(
        self,
        typesense_results: list[tuple[int, dict]],
        qdrant_results: list[tuple[int, dict]],
    ) -> list[dict]:
        """두 검색 결과를 병합하고 중복을 제거합니다.

        Args:
            typesense_results: Typesense 검색 결과 (id, item) 튜플 리스트
            qdrant_results: Qdrant 검색 결과 (id, item) 튜플 리스트

        Returns:
            중복이 제거된 병합된 결과 리스트
        """
        # 결과를 딕셔너리로 변환 (id를 키로 사용)
        merged_dict = {}

        # Typesense 결과 추가
        for item_id, item in typesense_results:
            merged_dict[item_id] = item

        # Qdrant 결과 추가 (이미 있는 ID는 덮어쓰지 않음)
        for item_id, item in qdrant_results:
            if item_id not in merged_dict:
                merged_dict[item_id] = item

        # 딕셔너리를 리스트로 변환하여 반환
        return list(merged_dict.values())
