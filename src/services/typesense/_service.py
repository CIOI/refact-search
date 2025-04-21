# src/services/_service.py
from typing import Dict, List, Optional
from src.managers.typesense import TypesenseManager
from src.config._logger import LoggerService
from src.databases.schema import MallSchema, get_mall_schema
from typesense.types.collection import CollectionCreateSchema
from typesense.types.document import RequiredSearchParameters


class TypesenseService:
    """검색 서비스 클래스

    Attributes:
        typesense_manager (TypesenseManager): Typesense 매니저
        logger (LoggerService): 로깅 서비스
    """

    def __init__(
        self,
        typesense_manager: TypesenseManager,
        logger: LoggerService,
    ):
        self.typesense_manager = typesense_manager
        self.logger = logger
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
            search_parameters: RequiredSearchParameters = {
                "q": query,
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

            self.logger.info(f"Search completed for query: {query} in mall: {mall_id}")
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

    def create_collection(self, mall_schema: MallSchema) -> None:
        """Typesense 컬렉션 생성"""
        self.typesense_manager.create_collection(
            TypesenseService._schema_builder(mall_schema)
        )

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
