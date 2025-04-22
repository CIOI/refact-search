import streamlit as st
from src.config._container import Application
from src.search import SearchService
from src.config.helpers._override import mock_overrides
from argparse import ArgumentParser
import sys
import asyncio

parser = ArgumentParser()
parser.add_argument("--mall_id", default="company_a", help="Mall ID to search")
args = parser.parse_args(sys.argv[1:])  # streamlit 관련 인자는 제외하고 파싱
mall_id = args.mall_id or "company_a"  # 기본값 설정
# 전역 범위에서 한 번만 초기화
application = Application()
application = mock_overrides(application)
# 페이지 설정
st.set_page_config(page_title="패션 검색엔진")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--mall_id", default="company_a", help="Mall ID to search")
    # streamlit의 인자는 무시하고 스크립트의 인자만 파싱
    return parser.parse_args(sys.argv[1:])


# 서비스 초기화
@st.cache_resource
def get_search_service():
    return SearchService(
        typesense_service=application.services.typesense_service(),
        embedding_service=application.embedding_model(),
        qdrant_service=application.services.qdrant_service(),
        mall_id=mall_id,
        logger=application.logger(),
    )


async def main():
    st.title("🔍 패션 검색엔진")
    st.write("찾고계신 패션 아이템을 입력해 주세요.")
    # 서비스 가져오기
    search_service = get_search_service()

    query = st.text_input("검색 입력창:")

    if query:
        st.write(f"Searching for: **{query}**")

        # 검색 실행
        results = await search_service.search(query)
        print(results)
        st.write("### 🎯 검색결과:")

        # 결과 표시
        for i in range(0, len(results), 2):
            cols = st.columns(2)

            # 왼쪽 열
            if i < len(results):
                product = results[i]
                display_product(cols[0], product)

            # 오른쪽 열
            if i + 1 < len(results):
                product = results[i + 1]
                display_product(cols[1], product)


def display_product(column, product):
    image_path = product.get("image_path", "default.jpg")
    column.image(image_path, caption=product.get("name", ""), width=300)
    column.write(f"🛍️ **{product.get('name', 'Unknown')}**")
    column.write(f"📖 {product.get('description', 'No description available.')}")


if __name__ == "__main__":
    asyncio.run(main())
