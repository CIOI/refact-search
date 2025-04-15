from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
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
        self.client = QdrantClient(url=environment.QDRANT_URL)
        self.vector_size = environment.VECTOR_SIZE
        self.logger = logger

    def create_collection(self, collection_name: str):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.DOT),
        )

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name=collection_name)

    def add_vector(
        self,
        id: str,
        collection_name: str,
        vector: list[float],
        payload: dict,
    ) -> UpdateResult:
        response = self.client.upsert(
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

    def query(
        self,
        collection_name: str,
        query: list[float],
        payload: bool = True,
        limit: int = 10,
    ):
        response = self.client.query_points(
            collection_name=collection_name,
            query_vector=query,
            with_payload=payload,
            limit=limit,
        )
        return response

    def filter_query(
        self, collection_name: str, query: list[float], filter: Filter, limit: int = 10
    ):
        search_result = self.client.query_points(
            collection_name=collection_name,
            query=query,
            query_filter=filter,
            with_payload=True,
            limit=limit,
        ).points
        return search_result
