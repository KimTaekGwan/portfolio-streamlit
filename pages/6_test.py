import streamlit as st
import openai
import json

# OpenAI API 키 설정
openai.api_key = 'YOUR_OPENAI_API_KEY'

st.title("OpenAI Structured Output with Streamlit")

st.sidebar.header("Function Definition")

# 함수 이름 입력
function_name = st.sidebar.text_input("Function Name", value="get_info")

# 함수 설명 입력
function_description = st.sidebar.text_area("Function Description", value="Retrieve information based on the user's request.")

# 함수 파라미터 입력 (JSON 형식)
parameters_json = st.sidebar.text_area(
    "Function Parameters (in JSON Schema format)",
    value=json.dumps({
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic to retrieve information about"
            },
            "details": {
                "type": "boolean",
                "description": "Whether to include detailed information"
            }
        },
        "required": ["topic"]
    }, indent=4)
)

# 사용자 프롬프트 입력
user_prompt = st.text_area("Enter your prompt", value="Tell me about the Eiffel Tower.")

if st.button("Generate Response"):
    try:
        # JSON 파싱
        parameters = json.loads(parameters_json)

        # 함수 정의 생성
        functions = [
            {
                "name": function_name,
                "description": function_description,
                "parameters": parameters
            }
        ]

        # 메시지 구성
        messages = [
            {"role": "user", "content": user_prompt}
        ]

        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",  # 또는 사용 가능한 다른 모델
            messages=messages,
            functions=functions,
            function_call="auto"
        )

        # 응답 출력
        response_message = response['choices'][0]['message']

        st.subheader("Assistant's Response:")
        st.write(response_message['content'])

        if 'function_call' in response_message:
            st.subheader("Function Call:")
            st.json(response_message['function_call'])

    except json.JSONDecodeError:
        st.error("Invalid JSON in function parameters.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
