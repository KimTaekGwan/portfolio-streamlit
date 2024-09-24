# 📄 Document question answering template

A simple Streamlit app that answers questions about an uploaded document via OpenAI's GPT-3.5.

## 1. Python Setting

- python 가상환경 생성 (python 3.11.9 기준)

  ```zsh
  python -m venv .venv
  ```

- activate 파일 생성

  - mac 기준

    ```zsh
    touch activate
    ```

  - windows 기준

    ```zsh
    type nul > activate
    ```

- activate 파일 내에 내용 추가

  - mac 기준

    ```zsh
    source .venv/bin/activate
    ```

  - windows 기준

    ```zsh
    .venv/Scripts/activate
    ```

- 가상한경 실행

  - mac 기준

    ```zsh
    source activate
    ```

  - windows 기준

    ```zsh
    activate
    ```

## 2. Install the requirements

```
$ pip install -r requirements.txt
```

## 3. Run the app

```
$ streamlit run streamlit_app.py
```
