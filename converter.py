from pathlib import Path
import json


def split_data_by_serial_number(input_file: Path, output_odd: Path, output_even: Path):
    """serial_number의 홀수/짝수에 따라 데이터를 분리합니다.

    Args:
        input_file (Path): 입력 JSONL 파일 경로
        output_odd (Path): 홀수 데이터를 저장할 파일 경로
        output_even (Path): 짝수 데이터를 저장할 파일 경로
    """
    with (
        open(input_file, "r", encoding="utf-8") as f_in,
        open(output_odd, "w", encoding="utf-8") as f_odd,
        open(output_even, "w", encoding="utf-8") as f_even,
    ):

        for line in f_in:
            # JSONL 파일의 각 라인을 파싱
            data = json.loads(line.strip())

            # serial_number가 홀수인지 짝수인지 확인
            if data["serial_number"] % 2 == 0:
                # 짝수인 경우
                f_even.write(json.dumps(data, ensure_ascii=False) + "\n")
            else:
                # 홀수인 경우
                f_odd.write(json.dumps(data, ensure_ascii=False) + "\n")


# 사용 예시
if __name__ == "__main__":
    input_file = Path("preprocessing/fixtures/consolidated_products_normalized.jsonl")
    output_odd = Path("preprocessing/fixtures/consolidated_products_odd.jsonl")
    output_even = Path("preprocessing/fixtures/consolidated_products_even.jsonl")

    split_data_by_serial_number(input_file, output_odd, output_even)
