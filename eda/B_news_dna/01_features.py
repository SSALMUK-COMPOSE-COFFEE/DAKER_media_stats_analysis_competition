# -*- coding: utf-8 -*-
"""
2025 언론수용자 조사 — 뉴스 DNA 유형화: 피처 설계
- 매체별 '뉴스' 이용 주간 일수(0~7일)로 통일. 스킵 로직: 해당 매체(또는 매체 뉴스) 비이용자 = 0일.
- 참여(공유/추천/댓글), 관심도, 신뢰도, 유료 이용은 별도 피처.
출력: features.csv (클러스터링용 X + 프로파일링용 보조 변수)
"""
import pandas as pd
import numpy as np
import pyreadstat
from pathlib import Path

_HERE = Path(__file__).resolve().parent
SAV = str(_HERE.parents[1] / "data/2025_언론수용자조사/3. 2025 언론수용자 조사_최종데이터.SAV")
OUT = str(_HERE / "features.csv")

df, meta = pyreadstat.read_sav(SAV)

f = pd.DataFrame(index=df.index)
f["ID"] = df["ID"]
f["WT"] = df["WT"]
f["age"] = df["DQ3"]
f["sex"] = df["DQ2"]          # 1 남 2 여
f["region"] = df["SQ1"]
f["edu"] = df["BQ3"]
f["job"] = df["BQ4"]
f["income"] = df["BQ5"]
f["polview"] = df["BQ7"]

# ---------- 매체별 뉴스 이용 주간 일수 (평일 0~5 + 주말 0~2 = 0~7) ----------
# 규칙: 게이트 문항(이용 여부)이 '이용'이 아니면 0일. 일수 결측(스킵)도 0일.
def days(gate_yes, wd, we):
    """gate_yes: bool Series(뉴스 이용자), wd/we: 일수 컬럼명(또는 컬럼명 리스트→기기별 max)"""
    def col(c):
        if isinstance(c, list):
            return df[c].max(axis=1)  # 기기(모바일/PC) 중복 계상 방지: 일수 max
        return df[c]
    d = col(wd).fillna(0) + col(we).fillna(0)
    return np.where(gate_yes, d, 0.0)

f["d_paper"]     = days(df["Q1"] == 1,  "Q2A_1", "Q2B_1")                      # 종이신문(열독=뉴스로 간주)
f["d_magazine"]  = days(df["Q8"] == 1,  "Q9A_1", "Q9B_1")                      # 뉴스/시사 잡지
f["d_tv"]        = days(df["Q13"] == 1, "Q14A_1", "Q14B_1")                    # TV 뉴스/시사
f["d_radio"]     = days(df["Q20"] == 1, "Q21A_1", "Q21B_1")                    # 라디오 뉴스/시사
portal_user      = (df["Q31_1"] == 1) | (df["Q31_2"] == 2)                     # 모바일 or PC 포털 뉴스
f["d_portal"]    = days(portal_user, ["Q32A_1", "Q32A_2"], ["Q32B_1", "Q32B_2"])
f["d_messenger"] = days(df["Q39"] == 1, "Q40A_1", "Q40B_1")                    # 메신저 뉴스
f["d_sns"]       = days(df["Q46"] == 1, "Q47A_1", "Q47B_1")                    # SNS 뉴스
f["d_video"]     = days(df["Q53"] == 1, "Q54A_1", "Q54B_1")                    # 온라인 동영상 플랫폼 뉴스
f["d_shortform"] = days(df["Q61"] == 1, "Q62A_1", "Q62B_1")                    # 숏폼 뉴스
f["d_ott"]       = days(df["Q67"] == 1, "Q68A_1", "Q68B_1")                    # OTT 뉴스
f["d_ai"]        = days(df["Q73"] == 1, "Q74A_1", "Q74B_1")                    # 생성형 AI 뉴스
f["d_podcast"]   = days(df["Q78"] == 1, "Q79A_1", "Q79B_1")                    # 팟캐스트 뉴스

# 이용 여부(0/1) — 검증·프로파일링용
f["u_paper"] = (df["Q1"] == 1).astype(int)
f["u_magazine"] = (df["Q8"] == 1).fillna(False).astype(int)
f["u_tv"] = (df["Q13"] == 1).astype(int)
f["u_radio"] = (df["Q20"] == 1).astype(int)
f["u_portal"] = portal_user.astype(int)
f["u_messenger"] = (df["Q39"] == 1).astype(int)
f["u_sns"] = (df["Q46"] == 1).astype(int)
f["u_video"] = (df["Q53"] == 1).astype(int)
f["u_shortform"] = (df["Q61"] == 1).astype(int)
f["u_ott"] = (df["Q67"] == 1).astype(int)
f["u_ai"] = (df["Q73"] == 1).astype(int)
f["u_podcast"] = (df["Q78"] == 1).astype(int)

# ---------- 참여 행태 (포털/메신저/SNS/동영상 4개 플랫폼 × 공유/추천/댓글) ----------
# 값 1='있다'만 참여로 간주(2/9997/9999/결측 → 0). 비이용자는 스킵으로 결측 → 0.
def did(*cols):
    return (df[list(cols)] == 1).any(axis=1).astype(int)

f["p_share"]   = did("Q35_1", "Q42_1", "Q49_1", "Q57_1")
f["p_like"]    = did("Q35_2", "Q42_2", "Q49_2", "Q57_2")
f["p_comment"] = did("Q35_3", "Q42_3", "Q49_3", "Q57_3")
f["engagement"] = f["p_share"] + f["p_like"] + f["p_comment"]  # 0~3

# ---------- 태도/관심/유료 ----------
f["interest"]   = df["BQ8"]     # 정치사회 관심도 1~5
f["trust_news"] = df["Q87_1"]   # 뉴스 전반 신뢰도 1~5
f["trust_new_src"] = df[["Q88_1", "Q88_2", "Q88_3"]].mean(axis=1)  # 비전통 출처(지인공유/1인크리에이터/포털알고리즘) 신뢰 1~5
f["paid_exp"]    = (df["Q97"] == 1).astype(int)
f["paid_intent"] = (df["Q97_1"] == 1).astype(int)
f["news_none"]  = (df["Q84"] == 9998).astype(int)  # 지난 1주 뉴스 이용 전무
f["main_path"]  = df["Q84"]

CLUSTER_COLS = [
    "d_paper", "d_magazine", "d_tv", "d_radio", "d_portal", "d_messenger",
    "d_sns", "d_video", "d_shortform", "d_ott", "d_ai", "d_podcast",
    "engagement", "interest", "trust_news", "trust_new_src", "paid_intent",
]

assert f[CLUSTER_COLS].isna().sum().sum() == 0, "클러스터링 피처에 결측 존재"
f.to_csv(OUT, index=False)

# ---------- 공식 보고서 대조(가중 이용률) ----------
w = f["WT"]
def wrate(col):
    return (f[col] * w).sum() / w.sum() * 100

official = {  # 보고서 p.19-20 (그림 1-1, 1-2)
    "u_tv": 81.4, "u_portal": 66.5, "u_video": 30.0, "u_shortform": 22.9,
    "u_messenger": 13.4, "u_paper": 8.4, "u_sns": 8.1, "u_ai": 2.1,
    "u_magazine": 1.9, "u_podcast": 1.1,
}
print("매체별 뉴스 이용률: 내 계산(가중) vs 공식 보고서")
for k, v in official.items():
    print(f"  {k:14s} {wrate(k):5.1f}%  vs  {v}%")
print("숏폼 뉴스 이용자 수(비가중):", int(f["u_shortform"].sum()), "(보고서 1,376)")
print("동영상 뉴스 이용자 수(비가중):", int(f["u_video"].sum()), "(보고서 1,803)")
print("\n피처 요약:")
print(f[CLUSTER_COLS].describe().T[["mean", "std", "min", "max"]].round(2))
