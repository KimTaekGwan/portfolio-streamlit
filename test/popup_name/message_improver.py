import pandas as pd
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
import os
import json

load_dotenv()

BASE_PATH = "/Users/ktg/Desktop/project/portfolio-streamlit/test/popup_name"
FINAL_RESULT_PATH = f"{BASE_PATH}/result.csv"
MERGED_BATCH_PATH = f"{BASE_PATH}/merged_batch_results.csv"

client = OpenAI()


class ResponseModel(BaseModel):
    modified_text: str
    score: int


def improve_phrase(phrase):
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": template},
                {"role": "user", "content": phrase},
            ],
            response_format=ResponseModel,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return type("ErrorResponse", (), {"modified_text": "Error", "score": 0})()


origin_df = pd.read_csv(f"{BASE_PATH}/message.csv")

result_example = f"""input: 현재 비밀번호를 입력해주세요.
output: 현재 사용 중인 비밀번호를 입력해 주세요.

input: 이메일형식이 올바르지 않습니다.
output: 이메일 형식이 올바르지 않습니다. 다시 확인해 주세요.

input: 한글이름을 입력해주세요.
output: 이름을 한글로 입력해 주세요.

input: 웹용 썸네일 이미지는 3MB를 넘을 수 없습니다.
output: 웹용 썸네일 이미지는 3MB 이하로 등록해 주세요.

input: 서비스 준비중입니다.
output: 현재 서비스 준비 중입니다. 잠시만 기다려 주세요."""

template = f"""You are tasked with improving a given Korean phrase to make it more user-friendly and natural. Your goal is to follow the instructions carefully and provide an improved version of the phrase along with a self-evaluation score.

To improve the phrase:
1. 존댓말 사용
2. 명확한 안내
3. 부드러운 어조
4. 필요한 경우 추가 설명

After improving the phrase, evaluate your own work by assigning a score from 0 to 9, where 0 is the lowest and 9 is the highest. Consider how well you've addressed each of the given criteria in your improvement.

Example:
{result_example}"""


def get_processed_messages():
    """이미 처리된 메시지들을 가져오는 함수"""
    processed_messages = set()
    result_files = [
        f
        for f in os.listdir(BASE_PATH)
        if f.startswith("result_batch_") and f.endswith(".csv")
    ]

    for file in result_files:
        df = pd.read_csv(f"{BASE_PATH}/{file}")
        processed_messages.update(df["original_message"].tolist())

    return processed_messages


# 유니크한 메시지 추출
unique_messages = origin_df["Message"].unique()

# 이미 처리된 메시지 확인
processed_messages = get_processed_messages()

# 아직 처리되지 않은 메시지만 필터링
remaining_messages = [msg for msg in unique_messages if msg not in processed_messages]
print(f"전체 메시지 수: {len(unique_messages)}")
print(f"이미 처리된 메시지 수: {len(processed_messages)}")
print(f"남은 메시지 수: {len(remaining_messages)}")

batch_size = 100
improved_results = []

for i in range(0, len(remaining_messages), batch_size):
    batch_messages = remaining_messages[i : i + batch_size]

    for message in tqdm(
        batch_messages,
        desc=f"배치 {i//batch_size + 1} 처리 중",
        total=len(batch_messages),
        position=0,
    ):
        try:
            result = improve_phrase(message)
            improved_results.append(
                {
                    "original_message": message,
                    "modified_text": result.modified_text,
                    "score": result.score,
                }
            )
        except Exception as e:
            print(f"Error in batch processing: {str(e)}")
            improved_results.append(
                {
                    "original_message": message,
                    "modified_text": "Error",
                    "score": 0,
                }
            )

    # 100개 처리할 때마다 중간 저장
    batch_num = (
        len([f for f in os.listdir(BASE_PATH) if f.startswith("result_batch_")]) + 1
    )

    temp_df = pd.DataFrame(improved_results)
    temp_df.to_csv(
        f"{BASE_PATH}/result_batch_{batch_num}.csv",
        index=False,
        encoding="utf-8",
    )
    improved_results = []  # 메모리 관리를 위해 저장 후 리스트 초기화


# 모든 배치 결과 파일 합치기
result_files = [
    f
    for f in os.listdir(BASE_PATH)
    if f.startswith("result_batch_") and f.endswith(".csv")
]

improved_df = pd.DataFrame()
for file in result_files:
    temp_df = pd.read_csv(f"{BASE_PATH}/{file}")
    improved_df = pd.concat([improved_df, temp_df], ignore_index=True)

# 중복 제거 (혹시 모를 중복 처리된 메시지 제거)
improved_df = improved_df.drop_duplicates(subset=["original_message"])

# 합친 배치 결과 중간 저장
improved_df.to_csv(MERGED_BATCH_PATH, index=False, encoding="utf-8")
improved_df.to_excel(MERGED_BATCH_PATH.replace(".csv", ".xlsx"), index=False)

print(f"배치 결과 병합 완료: {MERGED_BATCH_PATH}")
improved_df = pd.read_csv(MERGED_BATCH_PATH, encoding="utf-8")


# 원본 데이터프레임과 개선된 결과 매칭
final_df = origin_df.merge(
    improved_df, left_on="Message", right_on="original_message", how="left"
)

# 중복되는 original_message 칼럼 제거
final_df = final_df.drop(columns=["original_message"])

# 최종 결과 저장
final_df.to_csv(
    FINAL_RESULT_PATH,
    index=False,
    encoding="utf-8",
)
final_df.to_excel(FINAL_RESULT_PATH.replace(".csv", ".xlsx"), index=False)
