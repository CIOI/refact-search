from typesense import Client
from src.config._environment import Environment
from src.config._logger import LoggerService
from typing import Optional, Dict, Any
from pathlib import Path


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

    def create_collection(self, schema: Dict[str, Any]) -> None:
        """Collection을 생성합니다. 이미 존재하는 경우 삭제 후 재생성합니다.

        Args:
            schema (Dict[str, Any]): Collection 스키마
        """
        try:
            collections = self.client.collections.retrieve()
            if any(collection["name"] == schema["name"] for collection in collections):
                self.logger.warning(f"Collection {schema['name']} already exists")
                self.delete_collection(schema["name"])

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

    def import_documents(self, collection_name: str, fixture_path: Path) -> None:
        """문서를 일괄적으로 가져옵니다.

        Args:
            collection_name (str): 대상 Collection 이름
            fixture_path (Path): JSONL 파일 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            Exception: 가져오기 실패 시
        """
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

        try:
            # 청크 단위로 처리하여 메모리 사용량 제한
            chunk_size = 1024 * 1024  # 1MB
            with open(fixture_path, "rb") as jsonl_file:
                while chunk := jsonl_file.read(chunk_size):
                    self.client.collections[collection_name].documents.import_(
                        chunk, {"action": "create"}
                    )
            self.logger.info(f"Documents imported successfully to {collection_name}")
        except Exception as e:
            self.logger.error(
                f"Failed to import documents to {collection_name}: {str(e)}"
            )
            raise
