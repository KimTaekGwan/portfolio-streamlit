### 📁 프로젝트 구조

```
/test/popup_name
├── message.csv           # 원본 메시지 데이터
├── result.csv           # 최종 결과 파일
├── result.xlsx         # 최종 결과 파일 (엑셀 버전)
├── merged_batch_results.csv  # 모든 배치 처리 결과를 합친 중간 파일
├── merged_batch_results.xlsx # 모든 배치 처리 결과를 합친 중간 파일 (엑셀 버전)
└── result_batch_[N].csv     # 각 배치 처리 결과 파일들
```

### 📝 파일 설명

#### message.csv

- 원본 메시지 데이터가 포함된 CSV 파일
- `Message` 칼럼에 개선이 필요한 원본 텍스트 포함

#### result*batch*[N].csv

- 배치 처리된 중간 결과 파일들 (N은 배치 번호)
- 각 파일은 100개의 메시지 처리 결과 포함
- 칼럼 구조:
  - `original_message`: 원본 메시지
  - `modified_text`: 개선된 메시지
  - `score`: 개선 점수 (0-9)

#### merged_batch_results.csv

- 모든 배치 처리 결과를 하나로 합친 중간 파일
- 중복 제거된 전체 처리 결과 포함
- 엑셀 버전도 함께 생성 (.xlsx)

#### result.csv

- 최종 결과 파일
- 원본 데이터(`message.csv`)와 개선된 결과가 매칭된 최종 버전
- 엑셀 버전도 함께 생성 (.xlsx)
- 칼럼 구조:
  - `Message`: 원본 메시지
  - `modified_text`: 개선된 메시지
  - `score`: 개선 점수
  - (기타 원본 데이터의 추가 칼럼들)

### 🔄 처리 흐름

1. `message.csv`에서 원본 데이터 로드
2. 배치 단위(100개)로 메시지 처리
3. 각 배치 결과를 `result_batch_[N].csv`로 저장
4. 모든 배치 결과를 `merged_batch_results.csv`로 통합
5. 최종적으로 원본 데이터와 매칭하여 `result.csv` 생성
