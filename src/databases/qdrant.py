from pydantic import BaseModel


class QdrantItem(BaseModel):
    id: int
    vector: list[float]
    payload: dict
