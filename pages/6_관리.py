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


# 데이터 저장 함수
def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# 옵션 데이터를 평탄화하는 함수
def flatten_options(options):
    flat_options = {}
    for category in options.values():
        for opt_key, opt_data in category["options"].items():
            flat_options[opt_key] = opt_data
    return flat_options


# 상품 수정 함수
def edit_product(selected_product, products, options):
    product = products[selected_product]
    new_name = st.text_input("상품명", product["name"])
    new_theme_cost = st.number_input("테마 비용", value=product["theme_cost"])
    new_planning_cost = st.number_input("기획 비용", value=product["planning_cost"])
    new_hosting_cost = st.number_input("호스팅 비용", value=product["hosting_cost"])
    new_discount = st.number_input("할인", value=product["discount"])

    st.subheader("옵션 설정")
    flat_options = flatten_options(options)

    new_options = {}
    for opt, opt_data in product["options"].items():
        option_info = flat_options.get(opt)
        if not option_info:
            st.warning(f"옵션 정보가 없습니다: {opt}")
            continue
        st.write(f"옵션: {option_info['name']} ({opt})")
        enabled = st.checkbox(
            "활성화",
            value=opt_data["enabled"],
            key=f"{selected_product}_{opt}_enabled",
        )
        opt_type = option_info["type"]
        if opt_type == "boolean":
            default = st.checkbox(
                "기본 선택",
                value=opt_data["default"],
                key=f"{selected_product}_{opt}_default",
            )
            price = st.number_input(
                "가격",
                value=opt_data["price"],
                key=f"{selected_product}_{opt}_price",
            )
            new_options[opt] = {
                "enabled": enabled,
                "default": default,
                "price": price,
            }
        elif opt_type == "integer":
            min_value = option_info.get("min", 0)
            max_value = option_info.get("max", 10)
            default = st.number_input(
                "기본 값",
                value=opt_data.get("default", min_value),
                min_value=min_value,
                max_value=max_value,
                key=f"{selected_product}_{opt}_default",
            )
            price_per_unit = st.number_input(
                "단위 당 가격",
                value=opt_data.get("price_per_unit", 0),
                key=f"{selected_product}_{opt}_price_per_unit",
            )
            new_options[opt] = {
                "enabled": enabled,
                "default": default,
                "price_per_unit": price_per_unit,
            }
        else:
            st.error(f"알 수 없는 옵션 타입입니다: {opt_type}")
        st.write("---")

    if st.button("상품 수정"):
        products[selected_product] = {
            "name": new_name,
            "theme_cost": new_theme_cost,
            "planning_cost": new_planning_cost,
            "hosting_cost": new_hosting_cost,
            "discount": new_discount,
            "options": new_options,
        }
        save_data({"options": options, "products": products})
        st.success("상품이 수정되었습니다.")


# 새 상품 추가 함수
def add_new_product(products, options):
    new_product_name = st.text_input("새 상품명")
    new_theme_cost = st.number_input("테마 비용", value=0)
    new_planning_cost = st.number_input("기획 비용", value=0)
    new_hosting_cost = st.number_input("호스팅 비용", value=0)
    new_discount = st.number_input("할인", value=0)

    if st.button("새 상품 추가"):
        if new_product_name and new_product_name not in products:
            flat_options = flatten_options(options)
            new_product_options = {}
            for opt_key, opt_info in flat_options.items():
                if opt_info["type"] == "boolean":
                    new_product_options[opt_key] = {
                        "enabled": False,
                        "default": False,
                        "price": 0,
                    }
                elif opt_info["type"] == "integer":
                    new_product_options[opt_key] = {
                        "enabled": False,
                        "default": opt_info.get("min", 0),
                        "price_per_unit": 0,
                    }
                else:
                    st.error(
                        f"알 수 없는 옵션 타입입니다: {opt_info['type']} (옵션 키: {opt_key})"
                    )
            products[new_product_name] = {
                "name": new_product_name,
                "theme_cost": new_theme_cost,
                "planning_cost": new_planning_cost,
                "hosting_cost": new_hosting_cost,
                "discount": new_discount,
                "options": new_product_options,
            }
            save_data({"options": options, "products": products})
            st.success("새 상품이 추가되었습니다.")
        else:
            st.error("상품명을 입력하거나 중복되지 않은 이름을 사용해주세요.")


# 옵션 수정 함수
def edit_option(products, options):
    selected_category = st.selectbox("카테고리 선택", list(options.keys()))
    if selected_category:
        selected_option = st.selectbox(
            "수정할 옵션 선택", list(options[selected_category]["options"].keys())
        )
        if selected_option:
            option = options[selected_category]["options"][selected_option]
            new_name = st.text_input("옵션명", option["name"])
            new_type = st.selectbox(
                "타입",
                ["boolean", "integer"],
                index=0 if option["type"] == "boolean" else 1,
            )
            new_order = st.number_input("순서", value=option["order"])

            if new_type == "integer":
                new_min = st.number_input("최소값", value=option.get("min", 0))
                new_max = st.number_input("최대값", value=option.get("max", 10))

            if st.button("옵션 수정"):
                options[selected_category]["options"][selected_option] = {
                    "name": new_name,
                    "type": new_type,
                    "order": new_order,
                }
                if new_type == "integer":
                    options[selected_category]["options"][selected_option][
                        "min"
                    ] = new_min
                    options[selected_category]["options"][selected_option][
                        "max"
                    ] = new_max
                save_data({"options": options, "products": products})
                st.success("옵션이 수정되었습니다.")


# 새 옵션 추가 함수
def add_new_option(products, options):
    new_category = st.text_input(
        "새 카테고리 (기존 카테고리를 사용하려면 입력하지 마세요)"
    )
    if not new_category:
        new_category = st.selectbox("기존 카테고리 선택", list(options.keys()))
    new_option_name = st.text_input("새 옵션명")
    new_type = st.selectbox("타입", ["boolean", "integer"])
    new_order = st.number_input("순서", min_value=1, value=1)

    if new_type == "integer":
        new_min = st.number_input("최소값", value=0)
        new_max = st.number_input("최대값", value=10)

    if st.button("새 옵션 추가"):
        if new_category and new_option_name:
            if new_category not in options:
                options[new_category] = {"order": len(options) + 1, "options": {}}

            options[new_category]["options"][new_option_name] = {
                "name": new_option_name,
                "type": new_type,
                "order": new_order,
            }
            if new_type == "integer":
                options[new_category]["options"][new_option_name]["min"] = new_min
                options[new_category]["options"][new_option_name]["max"] = new_max

            save_data({"options": options, "products": products})
            st.success("새 옵션이 추가되었습니다.")
        else:
            st.error("카테고리와 옵션명을 모두 입력해주세요.")


# 메인 함수
def main():
    data = load_data()
    options = data.get("options", {})
    products = data.get("products", {})

    st.title("상품 및 옵션 관리")

    # 탭 생성
    tab1, tab2 = st.tabs(["상품 관리", "옵션 관리"])

    with tab1:
        st.header("상품 관리")

        # 상품 선택 또는 새 상품 추가
        product_action = st.radio("작업 선택", ["기존 상품 수정", "새 상품 추가"])

        if product_action == "기존 상품 수정":
            selected_product = st.selectbox("수정할 상품 선택", list(products.keys()))
            if selected_product:
                edit_product(selected_product, products, options)
        else:
            add_new_product(products, options)

    with tab2:
        st.header("옵션 관리")

        # 옵션 선택 또는 새 옵션 추가
        option_action = st.radio("작업 선택", ["기존 옵션 수정", "새 옵션 추가"])

        if option_action == "기존 옵션 수정":
            edit_option(products, options)
        else:
            add_new_option(products, options)

    # 현재 데이터 표시
    st.header("현재 데이터")
    st.json({"options": options, "products": products})


if __name__ == "__main__":
    main()
