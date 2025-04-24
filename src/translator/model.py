from abc import ABC, abstractmethod
from typing import Optional


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, target_language: Optional[str] = "en") -> str:
        pass

    @abstractmethod
    def translate_query(self, query: str) -> str:
        pass
