from pymongo import MongoClient
from typesense import Client
import json
from typing import Dict, Any
import time
from src.config._logger import LoggerService


class MongoTypesenseSync:
    def __init__(
        self, mongo_uri: str, typesense_config: Dict[str, Any], logger: LoggerService
    ):
        # MongoDB 설정
        self.mongo_client = MongoClient(mongo_uri)

        # Typesense 설정
        self.typesense_client = Client(typesense_config)
        self.logger = logger

    def create_schema(self, schema: Dict[str, Any]) -> None:
        """Typesense 컬렉션 스키마 생성"""
        try:
            collections = self.typesense_client.collections.retrieve()
            if any(collection["name"] == schema["name"] for collection in collections):
                self.logger.warning(f"Collection {schema['name']} already exists")
                self.typesense_client.collections[schema["name"]].delete()

            self.typesense_client.collections.create(schema)
            self.logger.info(f"Schema created for collection: {schema['name']}")
        except Exception as e:
            self.logger.error(f"Failed to create schema: {str(e)}")
            raise

    def handle_change(self, change: Dict[str, Any]) -> None:
        """MongoDB 변경사항 처리"""
        try:
            collection_name = "books"  # 또는 변경사항에서 가져올 수 있음

            if change["operationType"] == "delete":
                # 문서 삭제
                doc_id = str(change["documentKey"]["_id"])
                self.typesense_client.collections[collection_name].documents[
                    doc_id
                ].delete()
                self.logger.info(f"Deleted document: {doc_id}")

            elif change["operationType"] == "update":
                # 문서 업데이트
                doc_id = str(change["documentKey"]["_id"])
                updated_fields = change["updateDescription"]["updatedFields"]
                self.typesense_client.collections[collection_name].documents[
                    doc_id
                ].update(json.dumps(updated_fields))
                self.logger.info(f"Updated document: {doc_id}")

            elif change["operationType"] in ["insert", "replace"]:
                # 문서 생성/대체
                document = change["fullDocument"]
                document["id"] = str(document.pop("_id"))  # _id를 id로 변환
                self.typesense_client.collections[collection_name].documents.upsert(
                    json.dumps(document)
                )
                self.logger.info(f"Upserted document: {document['id']}")

        except Exception as e:
            self.logger.error(f"Failed to handle change: {str(e)}")
            raise

    def initial_sync(self, database: str, collection: str) -> None:
        """기존 MongoDB 데이터 초기 동기화"""
        try:
            mongo_collection = self.mongo_client[database][collection]
            collection_name = "books"

            # 전체 문서 가져오기
            total_docs = mongo_collection.count_documents({})
            self.logger.info(f"Starting initial sync of {total_docs} documents")

            # 배치 처리로 효율적인 동기화
            batch_size = 1000
            for i in range(0, total_docs, batch_size):
                documents = []
                for doc in mongo_collection.find().skip(i).limit(batch_size):
                    # _id를 id로 변환
                    doc["id"] = str(doc.pop("_id"))
                    documents.append(doc)

                if documents:
                    # 배치로 문서 import
                    self.typesense_client.collections[
                        collection_name
                    ].documents.import_(documents, {"action": "create"})

                self.logger.info(
                    f"Synced {min(i + batch_size, total_docs)}/{total_docs} documents"
                )

            self.logger.info("Initial sync completed")

        except Exception as e:
            self.logger.error(f"Failed to perform initial sync: {str(e)}")
            raise

    def start_sync(self, database: str, collection: str) -> None:
        """MongoDB Change Stream 시작 (초기 동기화 포함)"""
        try:
            # 1. 초기 동기화 수행
            self.initial_sync(database, collection)

            # 2. Change Stream 시작
            mongo_collection = self.mongo_client[database][collection]
            with mongo_collection.watch() as stream:
                self.logger.info(
                    f"Started watching collection: {database}.{collection}"
                )
                for change in stream:
                    self.handle_change(change)

        except Exception as e:
            self.logger.error(f"Failed to start sync: {str(e)}")
            raise


def main():
    # 환경 설정
    mongo_uri = "mongodb://localhost:27017"
    typesense_config = {
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "api_key": "xyz",
        "connection_timeout_seconds": 2,
    }

    # 스키마 정의
    schema = {
        "name": "books",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "author", "type": "string"},
            {"name": "year", "type": "int32", "facet": True},
        ],
        "default_sorting_field": "year",
    }

    # 동기화 시작
    syncer = MongoTypesenseSync(mongo_uri, typesense_config)
    syncer.create_schema(schema)
    syncer.start_sync("sample", "books")


if __name__ == "__main__":
    main()
