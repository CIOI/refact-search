from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import (
    VectorParams,
    PointStruct,
    Filter,
)
from qdrant_client.http.models import UpdateResult
from src.config._logger import LoggerService
from src.config._environment import Environment


class QdrantManager:
    """Qdrant 클라이언트를 관리하는 매니저 클래스

    Attributes:
        qdrant_url (str): Qdrant 서버 URL
        logger (LoggerService): 로깅 서비스
    """

    def __init__(
        self,
        environment: Environment,
        logger: LoggerService,
    ):
        self.client = AsyncQdrantClient(url=environment.QDRANT_URL)
        self.vector_size = environment.VECTOR_SIZE
        self.logger = logger

    async def create_collection(self, collection_name: str):
        if not await self.client.collection_exists(collection_name):
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )

    async def add_vector(
        self,
        id: str,
        collection_name: str,
        vector: list[float],
        payload: dict,
    ) -> UpdateResult:
        response = await self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=id,
                    vector=vector,
                    payload=payload,
                ),
            ],
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

    async def get_collection_list(self):
        return await self.client.get_collections()

    async def collection_exists(self, collection_name: str):
        return await self.client.collection_exists(collection_name)

    async def delete_collection(self, collection_name: str):
        await self.client.delete_collection(collection_name=collection_name)
