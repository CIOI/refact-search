import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel


class MallSchema(BaseModel):
    """쇼핑몰별 검색 설정"""

    mall_id: str
    name: str
    description: Optional[str] = None

    # Typesense 관련 설정
    fields: List[dict] = []
    index_fields: List[str] = []
    facet_fields: List[str] = []
    default_sorting_field: str = "product_id"

    # embedding 관련 설정
    embedding_fields: List[str] = ["name", "description"]

    # Qdrant 관련 설정
    id_field: str = "product_id"

    # 검색 결과에 포함할 필드
    payload_fields: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "mall_id": "mall1",
                "name": "패션몰1",
                "description": "의류 전문몰",
                "index_fields": ["product_id"],
                "facet_fields": ["brand", "category", "price"],
                "default_sorting_field": "product_id",
                "id_field": "product_id",
                "payload_fields": ["product_id", "name", "brand", "image_path"],
            }
        }


def get_mall_schema(mall_id: str) -> MallSchema:
    """
    JSON 파일에서 몰 스키마를 생성합니다.

    Args:
        json_path (str): 몰 설정이 저장된 JSON 파일 경로

    Returns:
        MallSchema: 생성된 몰 스키마 객체

    Raises:
        FileNotFoundError: JSON 파일이 존재하지 않는 경우
        ValueError: JSON 형식이 잘못된 경우
    """
    app_dir = Path(__file__).parent.parent  # src 디렉토리
    try:
        json_path = Path(app_dir, "databases", "malls", f"{mall_id}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return MallSchema(**data)
    except FileNotFoundError:
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"잘못된 JSON 형식입니다: {json_path}")
    except Exception as e:
        raise ValueError(f"스키마 생성 중 오류 발생: {str(e)}")


def create_mall_document(
    mall_id: str,
    name: str,
    description: Optional[str] = None,
    index_fields: List[str] = None,
    facet_fields: List[str] = None,
    default_sorting_field: str = "product_id",
    payload_fields: List[str] = None,
) -> str:
    """
    몰 설정 JSON 문서를 생성합니다.

    Args:
        mall_id (str): 몰 ID
        name (str): 몰 이름
        description (Optional[str]): 몰 설명
        index_fields (List[str]): 검색 가능한 필드 목록
        facet_fields (List[str]): 필터링 가능한 필드 목록
        default_sorting_field (str): 기본 정렬 필드
        payload_fields (List[str]): Qdrant 페이로드 필드 목록

    Returns:
        str: 생성된 JSON 파일의 경로

    Raises:
        OSError: 디렉토리 생성 실패 시
    """
    # app.py 위치 찾기
    app_path = Path(__file__).parent.parent

    # databases/models 디렉토리 경로 생성
    output_dir = Path(app_path).parent / "databases" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 설정 데이터 생성
    mall_config = {
        "mall_id": mall_id,
        "name": name,
        "description": description,
        "index_fields": index_fields or [],
        "facet_fields": facet_fields or [],
        "default_sorting_field": default_sorting_field,
        "payload_fields": payload_fields or [],
    }

    # JSON 파일 경로 (name.json 형식)
    json_path = output_dir / f"{name}.json"

    # JSON 파일 저장
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(mall_config, f, ensure_ascii=False, indent=2)
        return str(json_path)
    except Exception as e:
        raise OSError(f"JSON 파일 생성 중 오류 발생: {str(e)}")


def get_mall_list():
    current_dir = Path(__file__).parent
    malls_dir = Path(current_dir, "malls")

    # JSON 파일들의 이름을 가져와서 .json 확장자 제거
    mall_list = [path.stem for path in malls_dir.glob("*.json")]
    return mall_list
