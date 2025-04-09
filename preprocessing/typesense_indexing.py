from typesense import Client
from os.path import join, dirname
from src.config._environment import Environment
from findup import glob


def typesense_indexing(env: Environment):
    client = Client(
        {
            "api_key": env.typesense_api_key,
            "nodes": [
                {
                    "host": "localhost",  # For Typesense Cloud use xxx.a1.typesense.net
                    "port": "8108",  # For Typesense Cloud use 443
                    "protocol": "http",  # For Typesense Cloud use https
                }
            ],
            "connection_timeout_seconds": 2,
        }
    )
    fixture_path = join(
        dirname(glob(".env")),
        "preprocessing",
        "fixtures",
        "consolidated_products_normalized.jsonl",
    )
    products_schema = {
        "name": "products",
        "fields": [
            {"name": "serial_number", "type": "int32"},
            {"name": "description", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "product_id", "type": "int32", "index": True},
            {"name": "brand", "type": "string", "facet": True},
            {"name": "category", "type": "string", "facet": True},
            {"name": "price", "type": "float", "facet": True},
            {"name": "subcategory", "type": "string", "facet": True},
            {"name": "gender", "type": "string", "facet": True},
            {"name": "pose", "type": "string"},
            {"name": "image_path", "type": "string"},
        ],
        "default_sorting_field": "product_id",
    }
    collections = client.collections.retrieve()
    if not any(
        collection["name"] == products_schema["name"] for collection in collections
    ):
        try:
            client.collections.create(products_schema)
        except Exception as e:
            print(e)
    with open(fixture_path) as jsonl_file:
        client.collections["products"].documents.import_(
            jsonl_file.read().encode("utf-8")
        )
