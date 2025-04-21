from abc import ABC, abstractmethod


class EmbeddingModel(ABC):

    @abstractmethod
    def get_text_embedding(self, product: dict):
        pass

    @abstractmethod
    def model_load(self):
        pass

    @abstractmethod
    def get_image_embedding(self):
        pass

    @abstractmethod
    def get_query_embedding(self, query: str):
        pass
