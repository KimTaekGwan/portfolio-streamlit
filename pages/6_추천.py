import streamlit as st
import json
import os

# 데이터 경로 상수 정의
DATA_PATH = "data/product_data.json"


# 데이터 로드 함수
def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    else:
        st.error(
            f"{DATA_PATH} 파일을 찾을 수 없습니다. 관리 페이지에서 데이터를 먼저 생성해주세요."
        )
        return {"options": {}, "products": {}}


# 가격 계산 함수들
def calculate_base_price(product):
    # 기본 가격 계산: 테마 비용 + 기획 비용 + 웹호스팅 비용
    return product["theme_cost"] + product["planning_cost"] + product["hosting_cost"]


def calculate_final_base_price(product):
    # 최종 기본 가격 계산: 기본 가격 - 할인
    return calculate_base_price(product) - product["discount"]


def calculate_selection_price(product, selections):
    # 추가 옵션 가격 계산
    selection_price = 0
    for option, value in selections.items():
        option_data = product["options"].get(option, {})
        default_value = option_data.get("default", False)

        if isinstance(value, bool):
            # 옵션이 boolean 타입인 경우
            if value and not default_value:
                # 기본값이 False인데 선택한 경우 가격 추가
                selection_price += option_data.get("price", 0)
        elif isinstance(value, int):
            # 옵션이 integer 타입인 경우
            if value > default_value:
                # 선택한 값이 기본값보다 큰 경우에만 추가 가격 계산
                price_per_unit = option_data.get(
                    "price_per_unit", option_data.get("price", 0)
                )
                selection_price += (value - default_value) * price_per_unit
    return selection_price


def calculate_total_price(product, selections):
    # 총 가격 계산
    total_price = calculate_final_base_price(product)
    total_price += calculate_selection_price(product, selections)
    return total_price


# 옵션 선택 위젯 생성 함수
def render_option_widgets(selected_product, options):
    selections = {}
    sorted_categories = sorted(options.items(), key=lambda x: x[1]["order"])

    for category, category_info in sorted_categories:
        if category_info["options"] != {}:

            st.subheader(category)
            sorted_options = sorted(
                category_info["options"].items(), key=lambda x: x[1]["order"]
            )

            for option_key, option_value in sorted_options:
                product_option = selected_product["options"].get(option_key)
                if product_option and product_option["enabled"]:
                    option_name = option_value["name"]
                    if option_value["type"] == "boolean":
                        price = product_option["price"]
                        default_value = product_option.get("default", False)
                        # 기본값이 True인 경우 체크박스를 비활성화하여 변경 불가능하게 함
                        value = st.checkbox(
                            (
                                f"{option_name} (+{price:,}원)"
                                if not default_value
                                else f"{option_name} (기본 포함)"
                            ),
                            value=default_value,
                            disabled=default_value,
                        )
                        selections[option_key] = value
                    elif option_value["type"] == "integer":
                        price_per_unit = product_option.get("price_per_unit", 0)
                        min_value = option_value.get("min", 0)
                        max_value = option_value.get("max", 10)
                        default_value = product_option.get("default", min_value)
                        # 최소값을 기본값으로 설정하여 감소 불가능하게 함
                        min_value = max(min_value, default_value)
                        value = st.number_input(
                            f"{option_name} (개당 +{price_per_unit:,}원)",
                            min_value=min_value,
                            max_value=max_value,
                            value=default_value,
                        )
                        selections[option_key] = value
    return selections


# 선택한 옵션 표시 함수
def display_selected_options(selections, selected_product, options):
    st.header("선택한 옵션")
    sorted_categories = sorted(options.items(), key=lambda x: x[1]["order"])

    for category, category_info in sorted_categories:
        selected_options_in_category = [
            (option_key, selections[option_key])
            for option_key in category_info["options"]
            if option_key in selections
        ]

        if selected_options_in_category:
            st.subheader(category)
            for option_key, value in selected_options_in_category:
                option_info = category_info["options"][option_key]
                product_option = selected_product["options"][option_key]
                default_value = product_option.get("default", False)

                if option_info["type"] == "boolean":
                    if value and not default_value:
                        # 기본값이 False인데 선택된 경우
                        st.write(
                            f"{option_info['name']}: 선택됨 (+{product_option['price']:,}원)"
                        )
                    elif value and default_value:
                        # 기본 포함된 옵션인 경우
                        st.write(f"{option_info['name']}: 기본 포함")
                elif option_info["type"] == "integer":
                    if value > default_value:
                        # 추가된 개수가 있는 경우
                        extra_units = value - default_value
                        price_per_unit = product_option.get("price_per_unit", 0)
                        total_price = extra_units * price_per_unit
                        st.write(
                            f"{option_info['name']}: 기본 {default_value}개 + 추가 {extra_units}개 (+{total_price:,}원)"
                        )
                    else:
                        # 기본값만 선택된 경우
                        st.write(f"{option_info['name']}: 기본 {default_value}개")


# 메인 함수
def main():
    st.set_page_config(layout="wide")
    data = load_data()
    options = data.get("options", {})
    products = data.get("products", {})

    st.title("웹사이트 제작 서비스 가격 계산기")

    col1, col2 = st.columns(2)

    with col1:
        # 상품 선택
        selected_product_key = st.selectbox(
            "상품 선택",
            list(products.keys()),
            format_func=lambda x: products[x]["name"],
        )
        selected_product = products[selected_product_key]

        # 기본 가격 정보 표시
        st.header(f"선택된 상품: {selected_product['name']}")
        st.write(f"테마 비용: {selected_product['theme_cost']:,}원")
        st.write(f"기획 비용: {selected_product['planning_cost']:,}원")
        st.write(f"웹호스팅 비용: {selected_product['hosting_cost']:,}원")
        base_price = calculate_base_price(selected_product)
        st.write(f"**기본 가격: {base_price:,}원**")
        st.write(f"할인: {selected_product['discount']:,}원")
        final_base_price = calculate_final_base_price(selected_product)
        st.write(f"**최종 기본 가격: {final_base_price:,}원**")

    with col2:
        # 옵션 표시 및 선택
        st.header("추가 옵션")
        selections = render_option_widgets(selected_product, options)

    with col1:
        # 가격 정보 표시
        st.header("가격 정보")
        total_price = calculate_total_price(selected_product, selections)
        selection_price = calculate_selection_price(selected_product, selections)
        st.write(f"**총 가격: {total_price:,}원**")
        st.write(f"기본 가격: {final_base_price:,}원")
        st.write(f"추가 옵션 가격: {selection_price:,}원")

        # 선택한 옵션 표시
        display_selected_options(selections, selected_product, options)


if __name__ == "__main__":
    main()
