# 뉴스 DNA 테스트 (web)

한국언론진흥재단 〈2025 언론수용자 조사〉(n=6,000) 군집 분석 기반 뉴스 소비 유형 테스트.
React + TypeScript + Vite + Tailwind CSS.

## 실행

```bash
npm install
npm run dev        # 개발 서버
npm run build      # tsc + vite build + 유형별 공유 페이지(dist/r/<id>/) 생성
npm run lint       # oxlint
```

## 배포

카톡/페북 공유 썸네일의 OG 이미지는 절대 URL이 필요:

```bash
SITE_URL=https://내도메인 npm run build
```

## 데이터 파이프라인

- `src/quiz_model.json` — `eda/B_news_dna/05_quiz_simulation.py`가 생성 (유형 분류 모델 + 표시용 통계의 단일 소스)
- `src/data/taglines.json` — 유형별 태그라인 (앱 · 공유 OG · OG 이미지 공용)
- OG 이미지 재생성: `python scripts/generate_og.py` (pillow 필요)
