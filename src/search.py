from src.managers import QdrantManager
from src.embedding import ClipEmbeddingModel
from typesense import Client


class SearchService:
    def __init__(
        self,
        typesense_client: Client,
        embedding_service: ClipEmbeddingModel,
        qrant_manager: QdrantManager,
        mall_id: str,
    ):
        self.typesense_client = typesense_client
        self.embedding_service = embedding_service
        self.qrant_manager = qrant_manager
        self.mall_id = mall_id

    def search(self, query: str):
        typesense_results = self._search_typesense(query)
        qdrant_results = self._search_qdrant(query)
        return typesense_results + qdrant_results

    def _search_typesense(self, query: str):
        pass

    def _search_qdrant(self, query: str):
        pass
