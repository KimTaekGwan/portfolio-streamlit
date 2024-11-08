import os
import sys
import urllib.request

client_id = "seevfyfpmx"
client_secret = "cvqibpoZb6KIk3VcTvY7h3ahlqaUQSQGrJrl9AfY"

Text = "안녕하세요. 이번에는 재밋 에디터의 주요 기능들에 대해 살펴보도록 하겠습니다. 먼저 에디터의 전체적인 구조에 대해 설명드리겠습니다. 재밋 에디터는 중앙의 메인 편집 영역, 좌측의 블록/메뉴 영역, 우측의 디자인 설정 영역, 그리고 상단의 컨트롤 영역, 이렇게 4개의 주요 영역으로 구성되어 있습니다."

encText = urllib.parse.quote(Text)

speaker = "nara_call"
volume = "0"  # default = 0
speed = "0"  # default = 0
pitch = "0"  # default = 0
format = "wav"  # default = mp3

data = (
    f"speaker={speaker}&volume={volume}&speed={speed}&pitch={pitch}&format={format}&text="
    + encText
)
url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

request = urllib.request.Request(url)
request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
request.add_header("X-NCP-APIGW-API-KEY", client_secret)


response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()

if rescode == 200:
    print("TTS mp3 저장")
    response_body = response.read()
    with open(f"1111.{format}", "wb") as f:
        f.write(response_body)
else:
    print("Error Code:" + rescode)
