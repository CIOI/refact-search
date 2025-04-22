from pydantic import BaseModel


class ClipModel(BaseModel):
    model_name: str
    tokenizer: str
    max_length: int
    padding: str
    truncation: bool
    vector_size: int


fashion_clip = ClipModel(
    model_name="patrickjohncyh/fashion-clip",
    tokenizer="openai/clip-vit-base-patch32",
    max_length=512,
    padding="max_length",
    truncation=True,
    vector_size=512,
)
