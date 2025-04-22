from src.config._container import Application
from typing import List
from src.services import TypesenseService, QdrantService
from src.databases.schema import get_mall_list
from src.config.helpers._override import mock_overrides
import asyncio


async def import_documents(
    typesense_service: TypesenseService,
    qdrant_service: QdrantService,
    mall_list: List[str],
):
    for mall in mall_list:
        typesense_service.import_jsonl_documents(mall)
        await qdrant_service.import_documents(mall)


async def create_collections(
    mall_list: List[str],
    typesense_service: TypesenseService,
    qdrant_service: QdrantService,
):
    for mall in mall_list:
        typesense_service.create_collection(mall)
        await qdrant_service.create_collection(mall)


if __name__ == "__main__":
    application = Application()
    application = mock_overrides(application)
    mall_list = get_mall_list()
    asyncio.run(
        create_collections(
            typesense_service=application.services.typesense_service(),
            qdrant_service=application.services.qdrant_service(),
            mall_list=mall_list,
        )
    )
    asyncio.run(
        import_documents(
            typesense_service=application.services.typesense_service(),
            qdrant_service=application.services.qdrant_service(),
            mall_list=mall_list,
        )
    )
