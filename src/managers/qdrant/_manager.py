from qdrant_client import AsyncQdrantClient, QdrantClient, models
from qdrant_client.models import (
    VectorParams,
    PointStruct,
    Filter,
)
from qdrant_client.http.models import UpdateResult
from src.config._logger import LoggerService
from src.config._environment import Environment
from src.databases.qdrant import QdrantItem


class QdrantManager:
    """Qdrant 클라이언트를 관리하는 매니저 클래스

    Attributes:
        environment (Environment): 환경 설정
        logger (LoggerService): 로깅 서비스
    """

    def __init__(
        self,
        environment: Environment,
        logger: LoggerService,
    ):
        self.sync_client = QdrantClient(
            url=f"http://{environment.QDRANT_HOST}:{environment.QDRANT_PORT}",
        )
        self.client = AsyncQdrantClient(
            url=f"http://{environment.QDRANT_HOST}:{environment.QDRANT_PORT}",
        )
        self.vector_size = environment.VECTOR_SIZE
        self.logger = logger

    async def create_collection(self, collection_name: str, vector_size: int):
        if await self.client.collection_exists(collection_name):
            self.logger.warning(
                f"Collection {collection_name} already exists in Qdrant"
            )
            return

        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    async def add_vector(
        self,
        collection_name: str,
        item: QdrantItem,
    ) -> UpdateResult:
        response = await self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=item.id,
                    vector=item.vector,
                    payload=item.payload,
                ),
            ],
        )
        return response

    async def add_vectors_batch(
        self,
        collection_name: str,
        items: list[QdrantItem],
    ) -> UpdateResult:
        points = [
            PointStruct(
                id=item.id,
                vector=item.vector,
                payload=item.payload,
            )
            for item in items
        ]

        response = await self.client.upsert(
            collection_name=collection_name,
            points=points,
        )
        return response

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        payload: bool = True,
        limit: int = 10,
    ):
        response = await self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            with_payload=payload,
            limit=limit,
        )
        return response

    async def search_with_filter(
        self,
        collection_name: str,
        query_vector: list[float],
        filter: Filter,
        limit: int = 10,
    ):
        # TODO: 필터 조건 추가
        pass

    def get_collection_list(self) -> list[str]:
        return self.sync_client.get_collections().collections

    async def collection_exists(self, collection_name: str):
        return await self.client.collection_exists(collection_name)

    async def delete_collection(self, collection_name: str):
        await self.client.delete_collection(collection_name=collection_name)

    def get_document_count(self, collection_name: str) -> int:
        return self.sync_client.get_collection(collection_name).points_count
