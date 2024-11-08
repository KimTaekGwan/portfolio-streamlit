import pandas as pd
from pydantic import BaseModel
from dotenv import load_dotenv
from tqdm import tqdm
from typing import List
import asyncio
import aiohttp
from typing import List
import json
import os

load_dotenv()

# client = OpenAI()


class ResponseModel(BaseModel):
    input: str
    output: str
    score: int


origin_df = pd.read_csv(
    "/Users/ktg/Desktop/project/portfolio-streamlit/test/message.csv"
)[:10]

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

Please respond in JSON format with the following structure:
{{
    "input": "input phrase",
    "output": "improved phrase",
    "score": evaluation score (0-9)
}}

After improving the phrase, evaluate your own work by assigning a score from 0 to 9, where 0 is the lowest and 9 is the highest. Consider how well you've addressed each of the given criteria in your improvement.

Example:
{result_example}"""


async def improve_phrase(phrase, session):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": template},
            {"role": "user", "content": phrase},
        ],
        "response_format": {"type": "json_object"},
    }

    async with session.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    ) as response:
        result = await response.json()
        response_text = result["choices"][0]["message"]["content"]
        response_data = json.loads(response_text)
        return ResponseModel(**response_data)


async def process_messages(messages: List[str]):
    improved_results = []
    async with aiohttp.ClientSession() as session:
        for message in tqdm(
            messages, desc="메시지 개선 중", total=len(messages), position=0
        ):
            result = await improve_phrase(message, session)
            improved_results.append(
                {
                    "original_message": message,
                    "modified_text": result.output,
                    "score": result.score,
                }
            )
    return improved_results


# 메인 실행 부분을 비동기 함수로 변경
async def main():
    unique_messages = origin_df["Message"].unique()
    improved_results = await process_messages(unique_messages)

    # 개선된 결과로 데이터프레임 생성
    improved_df = pd.DataFrame(improved_results)

    # 원본 데이터프레임과 개선된 결과 매칭
    final_df = origin_df.merge(
        improved_df, left_on="Message", right_on="original_message", how="left"
    )

    # 필요없는 컬럼 제거 및 저장
    final_df = final_df.drop("original_message", axis=1)
    final_df.to_csv(
        "/Users/ktg/Desktop/project/portfolio-streamlit/test/result.csv",
        index=False,
        encoding="utf-8",
    )


# 스크립트 실행
if __name__ == "__main__":
    asyncio.run(main())
