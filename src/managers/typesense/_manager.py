from typesense import Client
from src.config._environment import Environment
from src.config._logger import LoggerService
from typing import Optional, List
from typesense.types.collection import CollectionCreateSchema
from typesense.types.document import SearchParameters, SearchResponse


class TypesenseManager:
    """Typesense 클라이언트를 관리하는 매니저 클래스

    Attributes:
        environment (Environment): 환경 설정
        logger (LoggerService): 로깅 서비스
    """

    def __init__(self, environment: Environment, logger: LoggerService):
        self._client: Optional[Client] = None
        self.api_key = environment.TYPESENSE_API_KEY
        self.nodes = [
            {
                "host": environment.TYPESENSE_HOST,
                "port": environment.TYPESENSE_PORT,
                "protocol": environment.TYPESENSE_PROTOCOL,
            }
        ]
        self.logger = logger

    @property
    def client(self) -> Client:
        """Typesense 클라이언트를 싱글톤으로 관리

        Returns:
            Client: Typesense 클라이언트 인스턴스
        """
        if self._client is None:
            self._client = Client(
                {
                    "api_key": self.api_key,
                    "nodes": self.nodes,
                    "connection_timeout_seconds": 2,
                }
            )
        return self._client

    def create_collection(self, schema: CollectionCreateSchema) -> None:
        """Collection을 생성합니다. 이미 존재하는 경우 삭제 후 재생성합니다.

        Args:
            schema (Dict[str, Any]): Collection 스키마
        """
        try:
            collections = self.get_collection_list()
            if schema["name"] in collections:
                self.logger.warning(
                    f"Collection {schema['name']} already exists in Typesense"
                )
                return

            self.client.collections.create(schema)
            self.logger.info(f"Collection {schema['name']} created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create collection {schema['name']}: {str(e)}")
            raise

    def delete_collection(self, collection_name: str) -> None:
        """Collection을 삭제합니다.

        Args:
            collection_name (str): 삭제할 Collection 이름
        """
        try:
            self.client.collections[collection_name].delete()
            self.logger.info(f"Collection {collection_name} deleted successfully")
        except Exception as e:
            self.logger.error(
                f"Failed to delete collection {collection_name}: {str(e)}"
            )
            raise

    def upsert(self, collection_name: str, document: dict) -> None:
        """문서를 추가합니다.

        Args:
            collection_name (str): 대상 Collection 이름
            document (dict): 문서
        """
        self.client.collections[collection_name].documents.upsert(document)

    def upsert_batch(self, collection_name: str, documents: list[dict]) -> None:
        """문서를 일괄적으로추가합니다..

        Args:
            collection_name (str): 대상 Collection 이름
            documents (list[dict]): 문서 리스트
        """
        self.client.collections[collection_name].documents.import_(
            documents, {"action": "create"}
        )

    def get_collection_list(self) -> List[str]:
        """Collection 목록을 가져옵니다.

        Returns:
            List[str]: Collection 목록
        """
        return [collection["name"] for collection in self.client.collections.retrieve()]

    def get_document_count(self, collection_name: str) -> int:
        """Collection 내 문서 수를 가져옵니다.

        Args:
            collection_name (str): Collection 이름
        """
        return self.client.collections[collection_name].retrieve()["num_documents"]

    def search(
        self,
        collection_name: str,
        search_parameters: SearchParameters,
    ) -> SearchResponse:
        """검색 쿼리를 실행하고 결과를 반환합니다.

        Args:
            search_parameters (SearchParameters): 검색 쿼리
            collection_name (str): 검색할 Collection 이름

        Returns:
            List[dict]: 검색 결과
        """
        return self.client.collections[collection_name].documents.search(
            search_parameters
        )

    def get_suggestions(self, collection_name: str, query: str) -> List[str]:
        """검색어 자동완성을 위한 제안을 가져옵니다.

        Args:
            collection_name (str): 검색할 Collection 이름
            query (str): 검색어

        Returns:
            List[str]: 검색어 자동완성 제안 목록
        """
        response = self.client.collections[collection_name].documents.search(
            {"q": query, "query_by": "name", "per_page": 5, "prefix": True}
        )
        return [hit["document"]["name"] for hit in response["hits"]]
