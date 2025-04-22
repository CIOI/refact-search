# src/services/_service.py
from typing import Dict
from src.managers.qdrant import QdrantManager
from src.config._logger import LoggerService
from src.embedding import ClipEmbeddingModel
from pathlib import Path
import json
from src.databases.schema import get_mall_schema
from src.databases.qdrant import QdrantItem


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

    async def search(
        self,
        query: str,
        mall_id: str,
        limit: int = 10,
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
            results = await self.qdrant_manager.search(
                collection_name=mall_id,
                query_vector=self.embedding_model.get_text_embedding(query)
                .squeeze()
                .tolist(),
                limit=limit,
            )

            self.logger.info(f"Search completed for query: {query} in mall: {mall_id}")
            return results
        except Exception as e:
            self.logger.error(
                f"Search failed for query: {query} in mall: {mall_id}, error: {str(e)}"
            )
            raise

    async def import_documents(self, mall_id: str, batch_size: int = 1000) -> None:
        """문서를 가져옵니다.
        Args:
            mall_id (str): 몰 ID (mall1 또는 mall2)
            batch_size (int): 배치 크기
        """
        mall_schema = get_mall_schema(mall_id)
        db_path = Path(__file__).parent.parent.parent / "databases" / "items"
        fixture_path = db_path / f"{mall_id}.jsonl"
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

        try:
            batch_documents = []
            with open(fixture_path, "r", encoding="utf-8") as jsonl_file:
                for line in jsonl_file:
                    if line.strip():  # 빈 줄 제외
                        document = json.loads(line)  # JSON 파싱
                        batch_documents.append(document)  # JSON 객체 추가
                        if len(batch_documents) >= batch_size:
                            # 배치로 임베딩 생성
                            embeddings = self.embedding_model.get_text_embeddings_batch(
                                [
                                    self._get_document_text(
                                        document, mall_schema.embedding_fields
                                    )
                                    for document in batch_documents
                                ]
                            )
                            qdrant_items = [
                                QdrantItem(
                                    id=int(document[mall_schema.id_field]),
                                    vector=embedding.tolist(),
                                    payload={
                                        field: document[field]
                                        for field in mall_schema.payload_fields
                                    },
                                )
                                for document, embedding in zip(
                                    batch_documents, embeddings
                                )
                            ]
                            await self.qdrant_manager.add_vectors_batch(
                                mall_id,
                                qdrant_items,
                            )
                            batch_documents = []

                # 마지막 배치 처리
                if batch_documents:
                    embeddings = self.embedding_model.get_text_embeddings_batch(
                        [
                            self._get_document_text(
                                document, mall_schema.embedding_fields
                            )
                            for document in batch_documents
                        ]
                    )
                    qdrant_items = [
                        QdrantItem(
                            id=int(document[mall_schema.id_field]),
                            vector=embedding.tolist(),
                            payload={
                                field: document[field]
                                for field in mall_schema.payload_fields
                            },
                        )
                        for document, embedding in zip(batch_documents, embeddings)
                    ]
                    await self.qdrant_manager.add_vectors_batch(
                        mall_id,
                        qdrant_items,
                    )

            self.logger.info(f"{mall_id} collection added to qdrant")
        except Exception as e:
            self.logger.error(
                f"Failed to import documents for mall: {mall_id}, error: {str(e)}"
            )
            raise

    async def create_collection(self, mall_id: str) -> None:
        """컬렉션 생성

        Args:
            mall_id (str): 몰 ID (mall1 또는 mall2)
        """
        await self.qdrant_manager.create_collection(
            mall_id,
            self.embedding_model.vector_size,
        )

    def _get_document_text(self, document: dict, embedding_fields: list[str]) -> str:
        """문서에서 임베딩할 텍스트 필드들을 결합"""
        texts = []
        for field in embedding_fields:
            if field in document:
                texts.append(str(document[field]))
        return " ".join(texts)

    def check_data_count(self) -> list[dict]:
        """데이터 현황 확인"""
        data_counts = []
        for collection in self.qdrant_manager.get_collection_list():
            data_count = {
                "collection_name": collection.name,
                "document_count": self.qdrant_manager.get_document_count(
                    collection.name
                ),
            }
            data_counts.append(data_count)
        return data_counts
