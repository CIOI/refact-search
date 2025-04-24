from typing import Dict, List, Optional
from src.managers.typesense import TypesenseManager
from src.config._logger import LoggerService
from src.databases.schema import MallSchema, get_mall_schema
from src.translator.google import GoogleTranslator
from typesense.types.collection import CollectionCreateSchema
from typesense.types.document import RequiredSearchParameters
from pathlib import Path
import json


class TypesenseService:
    """검색 서비스 클래스

    Attributes:
        typesense_manager (TypesenseManager): Typesense 매니저
        logger (LoggerService): 로깅 서비스
        translator (Translator): 번역 서비스
    """

    def __init__(
        self,
        typesense_manager: TypesenseManager,
        logger: LoggerService,
        translator: GoogleTranslator,
    ):
        self.typesense_manager = typesense_manager
        self.logger = logger
        self.translator = translator
        self.mall_id: Optional[str] = None
        self.mall_schema: Optional[MallSchema] = None

    def set_mall(self, mall_id: str):
        self.mall_id = mall_id
        self.mall_schema = get_mall_schema(mall_id)

    def search(
        self,
        query: str,
        mall_id: Optional[str] = None,
        query_by: Optional[str] = "name,description",
        filter_by: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> Dict:
        """상품 검색

        Args:
            query (str): 검색어
            mall_id (str): 몰 ID (mall1 또는 mall2)
            filter_by (Optional[str]): 필터 조건
            sort_by (Optional[str]): 정렬 조건

        Returns:
            Dict: 검색 결과
        """
        try:
            translated_query = self.translator.translate_query(query)
            search_parameters: RequiredSearchParameters = {
                "q": translated_query,
                "query_by": query_by,
            }

            if filter_by:
                search_parameters["filter_by"] = filter_by
            if sort_by:
                search_parameters["sort_by"] = sort_by
            mall_id = mall_id if mall_id else self.mall_id
            results = self.typesense_manager.search(
                mall_id,
                search_parameters,
            )

            self.logger.info(
                f"Search completed for query: {query} "
                f"(translated: {translated_query}) in mall: {mall_id}"
            )
            return results
        except Exception as e:
            self.logger.error(
                f"Search failed for query: {query}"
                + f" in mall: {self.mall_id}, error: {str(e)}"
            )
            raise

    def get_suggestions(self, query: str) -> List[str]:
        """검색어 자동완성

        Args:
            query (str): 검색어

        Returns:
            List[str]: 자동완성 제안 목록
        """
        try:
            suggestions = self.typesense_manager.get_suggestions(self.mall_id, query)
            self.logger.info(
                f"Suggestions generated for query: {query} in mall: {self.mall_id}"
            )
            return suggestions
        except Exception as e:
            self.logger.error(
                f"Failed to generate suggestions for query: {query}"
                + f" in mall: {self.mall_id}, error: {str(e)}"
            )
            raise

    def create_collection(self, mall_id: str) -> None:
        """Typesense 컬렉션 생성"""
        mall_schema = get_mall_schema(mall_id)
        self.typesense_manager.create_collection(
            TypesenseService._schema_builder(mall_schema)
        )

    def import_jsonl_documents(self, collection_name: str) -> None:
        """문서를 일괄적으로 가져옵니다.

        Args:
            collection_name (str): 대상 Collection 이름
            fixture_path (Path): JSONL 파일 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            Exception: 가져오기 실패 시
        """
        db_path = Path(__file__).parent.parent.parent / "databases" / "items"
        fixture_path = db_path / f"{collection_name}.jsonl"
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

        try:
            # 청크 단위로 처리하여 메모리 사용량 제한
            batch_size = 1000  # 1000개씩 처리
            documents = []
            with open(fixture_path, "r", encoding="utf-8") as jsonl_file:
                for line in jsonl_file:
                    if line.strip():  # 빈 줄 제외
                        document = json.loads(line)  # JSON 파싱
                        documents.append(document)  # JSON 객체 추가
                        if len(documents) >= batch_size:
                            self.typesense_manager.upsert_batch(
                                collection_name,
                                documents,
                            )
                            documents = []
            if documents:
                self.typesense_manager.upsert_batch(
                    collection_name,
                    documents,
                )
            self.logger.info(f"{collection_name} collection added to typesense")
        except Exception as e:
            self.logger.error(
                f"Failed to import documents to {collection_name}: {str(e)}"
            )
            raise

    def check_data_count(self) -> list[dict]:
        """데이터 현황 확인"""
        data_counts = []
        for collection in self.typesense_manager.get_collection_list():
            data_count = {
                "collection_name": collection,
                "document_count": self.typesense_manager.get_document_count(collection),
            }
            data_counts.append(data_count)
        return data_counts

    @staticmethod
    def _schema_builder(mall_schema: MallSchema) -> CollectionCreateSchema:
        """Typesense 컬렉션 생성 스키마 빌더"""
        return CollectionCreateSchema(
            name=mall_schema.name,
            fields=TypesenseService._update_fields(mall_schema),
            default_sorting_field=mall_schema.default_sorting_field,
        )

    @staticmethod
    def _update_fields(mall_schema: MallSchema) -> List[dict]:
        fields = mall_schema.fields
        updated_fields = []

        for field in fields:
            field_copy = field.copy()  # 원본 보존을 위한 복사

            if field_copy.get("name") in mall_schema.index_fields:
                field_copy["index"] = True
            if field_copy.get("name") in mall_schema.facet_fields:
                field_copy["facet"] = True

            updated_fields.append(field_copy)

        return updated_fields
