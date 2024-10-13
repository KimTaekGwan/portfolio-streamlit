import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 상품 선택")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)
