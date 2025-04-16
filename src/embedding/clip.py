from typing import Optional, Union
import torch
from transformers import AutoProcessor
from PIL import Image
from src.utils.embedding_utils import get_combined_text
from src.config._logger import LoggerService
from .schma import ClipModel
from transformers import CLIPProcessor, CLIPModel
from transformers import CLIPTokenizerFast


class ClipEmbeddingModel:
    def __init__(
        self,
        clip_model: ClipModel,
        device: Optional[str] = None,
        logger: Optional[LoggerService] = None,
    ):
        """
        임베딩 모델을 초기화합니다.

        Args:
            model_name: 모델 이름 또는 경로
            model_class: 모델 클래스 (예: CLIPModel)
            tokenizer_class: 토크나이저 클래스 (예: CLIPTokenizerFast)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.clip_model = clip_model
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.logger = logger

    def model_load(self, image_usage: bool = False):
        self.model = CLIPModel.from_pretrained(self.clip_model.model_name).to(
            self.device
        )
        self.tokenizer = CLIPTokenizerFast.from_pretrained(self.clip_model.tokenizer)
        if image_usage:
            self.processor = CLIPProcessor.from_pretrained(self.clip_model.model_name)

    def get_text_embedding(
        self,
        product: dict,
        max_length: int = 77,
        return_tensors: str = "pt",
    ) -> torch.Tensor:
        """
        텍스트 임베딩을 생성합니다.

        Args:
            text: 입력 텍스트 또는 텍스트 리스트
            max_length: 최대 시퀀스 길이
            return_tensors: 반환 텐서 타입

        Returns:
            텍스트 임베딩 텐서
        """
        # 텍스트 토큰화
        text = get_combined_text(product)
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors=return_tensors,
        ).to(self.device)

        # 임베딩 생성
        with torch.no_grad():
            text_embeddings = self.model.get_text_features(**inputs)

        return text_embeddings

    def get_image_embedding(
        self, image: Union[Image.Image, list[Image.Image]], return_tensors: str = "pt"
    ) -> torch.Tensor:
        """
        이미지 임베딩을 생성합니다.

        Args:
            image: PIL 이미지 또는 이미지 리스트
            return_tensors: 반환 텐서 타입

        Returns:
            이미지 임베딩 텐서

        """
        if self.processor is None:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
        # 이미지 전처리
        inputs = self.processor(images=image, return_tensors=return_tensors).to(
            self.device
        )

        # 임베딩 생성
        with torch.no_grad():
            image_embeddings = self.model.get_image_features(**inputs)

        return image_embeddings

    def get_query_embedding(self, text):
        tokenized_text = self.tokenizer(
            text, truncation=True, max_length=75, return_tensors="pt"
        )
        tokens = tokenized_text["input_ids"].to(self.device)

        with torch.no_grad():
            query_embedding = self.model.get_text_features(tokens)
        return query_embedding.cpu().numpy()
