import streamlit as st
from src.config._container import Application
from src.search import SearchService

# 컨테이너 초기화
container = Application()

# 명령줄 인자 설정
st.set_page_config(page_title="패션 검색엔진")
mall_id = st.get_option("mall_id")

if not mall_id:
    mall_id = "company_a"  # 기본값


# 서비스 초기화
@st.cache_resource
def get_search_service(mall_id: str):
    return SearchService(
        typesense_client=container.typesense_client(),
        embedding_service=container.embedding_service(),
        qrant_manager=container.qrant_manager(),
        mall_id=mall_id,
    )


def main():
    st.title("🔍 패션 검색엔진")
    st.write("찾고계신 패션 아이템을 입력해 주세요.")

    # 서비스 가져오기
    search_service = get_search_service()

    query = st.text_input("검색 입력창:")

    if query:
        st.write(f"Searching for: **{query}**")

        # 검색 실행
        results = search_service.search(query)

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
    main()
