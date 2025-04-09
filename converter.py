import json

# 입력 및 출력 파일 경로
input_file = "preprocessing/fixtures/consolidated_products_normalized.json"
output_file = "preprocessing/fixtures/consolidated_products_normalized.jsonl"

# JSON 파일 읽기
with open(input_file, "r") as f:
    data = json.load(f)

# JSONL 파일로 변환하여 쓰기
with open(output_file, "w") as f:
    for item in data:
        # 각 객체를 JSON 문자열로 변환하고 줄바꿈 추가
        f.write(json.dumps(item) + "\n")

print(f"변환 완료: {input_file} → {output_file}")
