# -*- coding: utf-8 -*-
"""
언론사 직접 경로(언론사 홈페이지/앱을 통한 뉴스 이용) 시계열.
- 2019: 문43 경로별 뉴스 이용 '일수' 문항(주 1일 이상) — 워딩·형식이 이후 연도와 달라 참고치.
- 2020~2024: '경로별 뉴스 이용 여부'(있다/없다) 문항. 2022는 조사설계 상이.
- 2025: 해당 문항 폐지 → 측정 불가. 주 이용 경로(Q84)에서 언론사 홈페이지(0.3%)+앱(0.5%)만 확인 가능.
"""
import pyreadstat
import pandas as pd
from pathlib import Path

_HERE = Path(__file__).resolve().parent
D = str(_HERE.parents[1] / "data")
OUT = str(_HERE)
rows = []

# 2019 (일수 문항)
df, _ = pyreadstat.read_sav(f"{D}/2019_언론수용자조사/2019_언론수용자조사.sav",
                            usecols=["Q43_01_1", "Q43_01_2", "Q43_02_1", "Q43_02_2", "wt1"])
w = df["wt1"]
home = (df[["Q43_01_1", "Q43_02_1"]] >= 2).any(axis=1)
app = (df[["Q43_01_2", "Q43_02_2"]] >= 2).any(axis=1)
rows.append({"year": 2019, "홈페이지": round(float(100*(w*home).sum()/w.sum()), 1),
             "앱": round(float(100*(w*app).sum()/w.sum()), 1),
             "홈페이지 또는 앱": round(float(100*(w*(home|app)).sum()/w.sum()), 1), "비고": "일수 문항(형식 상이)"})

specs = [
    (2020, f"{D}/2020_언론수용자조사/2020_언론수용자조사.sav", ["Q45_1", "Q45_2"], "WT", ""),
    (2021, f"{D}/2021_언론수용자조사/2021 언론수용자 조사 DATA_통계표_보고서 등/2021 언론수용자 조사 DATA_공개용_최종.sav", ["Q45_1", "Q45_2"], "WT", ""),
    (2022, f"{D}/2022_언론수용자조사/2022 언론수용자 조사 DATA_통계표_보고서 등/데이터/2022 언론수용자 조사_개인용_공개용 데이터.SAV", ["Q40_1", "Q40_2"], "WT", "조사설계 상이"),
    (2023, f"{D}/2023_언론수용자조사/2023 언론수용자 조사 DATA_통계표 등/2. 2023 언론수용자 조사_최종데이터(공개용).sav", ["Q35_1", "Q35_2"], "HMWT", ""),
    (2024, f"{D}/2024_언론수용자조사/3. 2024 언론수용자 조사_최종데이터.sav", ["Q35_1", "Q35_2"], "WT", ""),
]
for y, p, cols, wcol, note in specs:
    df, _ = pyreadstat.read_sav(p, usecols=cols + [wcol])
    w = df[wcol]
    h, a = (df[cols[0]] == 1), (df[cols[1]] == 1)
    rows.append({"year": y, "홈페이지": round(float(100*(w*h).sum()/w.sum()), 1),
                 "앱": round(float(100*(w*a).sum()/w.sum()), 1),
                 "홈페이지 또는 앱": round(float(100*(w*(h|a)).sum()/w.sum()), 1), "비고": note})

rows.append({"year": 2025, "홈페이지": None, "앱": None, "홈페이지 또는 앱": None,
             "비고": "문항 폐지. Q84 주 이용 경로 기준 언론사 홈페이지 0.3% + 앱 0.5% + 뉴스레터 0.7%"})

t = pd.DataFrame(rows).set_index("year")
t.to_csv(f"{OUT}/t_direct_channel_2019_2024.csv", encoding="utf-8-sig")
print(t.to_string())
