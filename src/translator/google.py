import re
from typing import Dict
from google.cloud import translate_v2 as translate
from .model import Translator


class GoogleTranslator(Translator):
    """한국어를 영어로 번역하는 클래스 (Google Cloud Translate 사용)"""

    def __init__(self, credentials_path: str = None):
        """Translator 초기화

        Args:
            credentials_path (str, optional): Google Cloud 서비스 계정 키 파일 경로
        """
        if credentials_path:
            self.translate_client = translate.Client.from_service_account_json(
                credentials_path
            )
        else:
            self.translate_client = translate.Client()
        self.pre_translation_glossary = None
        self.domain_glossary = None

    def set_pre_translation_glossary(self, glossary: Dict[str, str]):
        self.pre_translation_glossary = glossary

    def set_domain_glossary(self, glossary: Dict[str, str]):
        self.domain_glossary = glossary

    def translate(
        self,
        text: str,
        target_language: str = "en",
    ) -> str:
        """Google Cloud Translate를 사용하여 텍스트를 영어로 번역

        Args:
            text (str): 번역할 텍스트
            target_language (str): 목표 언어 (기본값: "en")

        Returns:
            str: 번역된 텍스트
        """
        if not text or not text.strip():
            return text
        result = self.translate_client.translate(
            text,
            target_language=target_language,
        )
        return result.get("translatedText", text)

    def _contains_korean(self, text: str) -> bool:
        """텍스트에 한국어 문자가 포함되어 있는지 확인

        Args:
            text (str): 확인할 텍스트

        Returns:
            bool: 한국어 포함 여부
        """
        return re.search("[\uac00-\ud7a3]", text) is not None

    def _apply_pre_translation_glossary(self, text: str) -> str:
        """번역 전 용어집을 적용

        Args:
            text (str): 적용할 텍스트

        Returns:
            str: 용어집이 적용된 텍스트
        """
        if not self.pre_translation_glossary:
            return text
        for term, desired in self.pre_translation_glossary.items():
            text = text.replace(term, desired)
        return text

    def _apply_domain_glossary(self, translation: str) -> str:
        """번역된 텍스트에 도메인 용어집을 적용

        Args:
            translation (str): 번역된 텍스트

        Returns:
            str: 용어집이 적용된 텍스트
        """
        if not self.domain_glossary:
            return translation
        for term, desired in self.domain_glossary.items():
            translation = translation.replace(term, desired)
        return translation

    def translate_query(
        self,
        text: str,
    ) -> str:
        """쿼리 텍스트를 처리하고 필요한 경우 번역

        Args:
            text (str): 처리할 쿼리 텍스트

        Returns:
            str: 처리된 쿼리 텍스트
        """
        text = text.strip()
        if len(text) == 0:
            return "generic fashion item"

        if self._contains_korean(text):
            # Apply pre-translation glossary
            translated_text = self._apply_pre_translation_glossary(text)
            # Translate using Google Cloud Translate
            translated_text = self.translate(
                translated_text,
                target_language="en",
            )
            # Apply domain-specific glossary
            corrected_text = self._apply_domain_glossary(translated_text)
        else:
            corrected_text = text

        return corrected_text
