import streamlit as st
import json
import pandas as pd
import os

# 데이터 경로 상수 정의
DATA_PATH = "data/product_data.json"


# 데이터 로드 함수
def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        st.error(
            f"{DATA_PATH} 파일을 찾을 수 없습니다. 관리 페이지에서 데이터를 먼저 생성해주세요."
        )
        return {"options": {}, "products": {}}


# 옵션 이름 매핑 생성 함수
def get_option_name_mapping(options):
    mapping = {}
    for category in options.values():
        for opt_key, opt_data in category["options"].items():
            mapping[opt_key] = opt_data["name"]
    return mapping


def main():
    st.title("상품 비교표")

    data = load_data()
    options = data.get("options", {})
    products = data.get("products", {})

    if not products:
        st.warning("상품 데이터가 없습니다.")
        return

    option_name_mapping = get_option_name_mapping(options)

    # 표시할 옵션 선택
    st.sidebar.header("옵션 카테고리 선택")
    selected_categories = st.sidebar.multiselect(
        "카테고리 선택", options.keys(), default=list(options.keys())
    )

    selected_options = []
    for category in selected_categories:
        category_options = options[category]["options"]
        selected_options.extend(category_options.keys())

    # 상품별 데이터프레임 생성
    product_list = []
    for product_key, product in products.items():
        product_info = {
            "상품명": product["name"],
            "테마 비용": product["theme_cost"],
            "기획 비용": product["planning_cost"],
            "호스팅 비용": product["hosting_cost"],
            "할인": product["discount"],
            "기본 가격": product["theme_cost"]
            + product["planning_cost"]
            + product["hosting_cost"]
            - product["discount"],
        }

        # 옵션 정보 추가
        for opt_key, opt_data in product["options"].items():
            if opt_key in selected_options:
                option_name = option_name_mapping.get(opt_key, opt_key)
                if opt_data["enabled"]:
                    if "price" in opt_data:
                        product_info[option_name] = f"가능 (+{opt_data['price']:,}원)"
                    elif "price_per_unit" in opt_data:
                        product_info[option_name] = (
                            f"가능 (단위당 +{opt_data['price_per_unit']:,}원)"
                        )
                    else:
                        product_info[option_name] = "가능"
                else:
                    product_info[option_name] = "불가능"

        product_list.append(product_info)

    # 데이터프레임 생성
    df = pd.DataFrame(product_list)
    df = df.set_index("상품명")

    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
    styled_df = df.style.format({col: "{:,}" for col in numeric_columns})

    st.dataframe(df.select_dtypes(include=["float64", "int64"]))
    st.dataframe(styled_df.data.T)


if __name__ == "__main__":
    main()
