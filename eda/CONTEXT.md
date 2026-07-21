# EDA 공통 컨텍스트 (한국언론진흥재단 경진대회)

## 환경
- Python venv: `/private/tmp/claude-501/-Users-hajinkwonsee-developments-kirito2056-hackathon/2bac6ad6-25d9-4c9b-95b6-d74420824700/scratchpad/venv/bin/python`
  (pandas, pyreadstat, openpyxl, scikit-learn, matplotlib 설치됨)
- 데이터 루트: 레포 루트의 `data/`
- 결과물 저장: 레포 루트의 `eda/` 아래에 담당 디렉토리를 만들어 저장
- 스크립트 내 경로는 `Path(__file__)` 기준 상대 경로로 작성 (절대 경로 하드코딩 금지)
  - 분석 스크립트(.py), 차트(.png), 결과 요약(.md)을 모두 남길 것

## 데이터 요약
- `2010/2012/2014/2016/2018/2019/2020/2021/2023_언론수용자조사`, `2024_언론수용자조사`, `2025_언론수용자조사`: 연 5,000~6,000명 개인 응답 SAV
- `2022_언론수용자조사`: 가구용(30,138) + 개인용(58,936 × 244) 초대형 표본
- `2025_청소년_미디어이용조사`: xlsx (SAV 없음), 코드북 PDF 있음
- `2023_어린이_미디어이용조사`: SAV 2,675 × 404
- `2024_소셜미디어이용자조사`: SAV 3,000 × 1,359
- 각 폴더에 설문지겸코드북 PDF 존재 — 변수 의미 확인에 활용 (Read 툴로 PDF 읽기 가능)

## SAV 읽기 팁
```python
import pyreadstat
try:
    df, meta = pyreadstat.read_sav(path)
except Exception:
    df, meta = pyreadstat.read_sav(path, encoding='cp949')
# meta.column_names_to_labels: 변수 라벨
# meta.variable_value_labels: 값 라벨 (dict)
```

## 분석 시 필수 검증 사항 (모든 담당 공통)
1. **가중치 변수 확인**: WT, weight, 가중치 등의 변수를 찾아 가중 평균으로 계산할 것. 없으면 명시.
2. **결측/무응답 코드**: 9997/9998/9999, 97/98/99 등이 실수값으로 섞여있을 수 있음 — 값 라벨과 분포로 확인 후 제거.
3. **스킵 로직**: 예: 숏폼 비이용자는 숏폼 뉴스 문항 미응답 → 비율 계산 시 분모를 명확히(전체 대비 vs 이용자 대비).
4. **공식 보고서와 대조**: 각 폴더의 보고서/통계표 PDF에서 공식 수치 1~2개를 찾아 내 계산과 일치하는지 검증하고 결과 md에 기록. 불일치하면 원인 규명.
5. 연도 간 비교 시 문항 워딩/보기 변경 여부를 코드북에서 확인하고, 비교 불가능하면 그렇게 기록.

## 차트
- matplotlib 한글: `plt.rcParams['font.family']='AppleGothic'; plt.rcParams['axes.unicode_minus']=False`
- 차트는 png로 저장 (dpi=150 이상)

## 결과 md 형식
- 핵심 발견(숫자 포함) bullet 최상단 → 상세 표/차트 → 검증 결과(공식 보고서 대조) → 데이터 품질 이슈 → "보고서에 쓸 만한 한 방 숫자" 3개 제안
