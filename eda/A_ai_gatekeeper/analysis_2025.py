# -*- coding: utf-8 -*-
"""
A. AI 게이트키퍼 EDA — 2025 언론수용자 조사 (n=6,000, 가중치 WT)
뉴스 소비 경로 이동(언론사 직접 → 포털 → 동영상/숏폼 → 생성형 AI) 가설 검증.
"""
import pyreadstat
import pandas as pd
import numpy as np
import json, os
from pathlib import Path

_HERE = Path(__file__).resolve().parent
OUT = str(_HERE)
PATH = str(_HERE.parents[1] / "data/2025_언론수용자조사/3. 2025 언론수용자 조사_최종데이터.SAV")

df, meta = pyreadstat.read_sav(PATH)
W = df["WT"]

def agegrp(a):
    if a < 30: return "20대(19-29)"
    if a < 40: return "30대"
    if a < 50: return "40대"
    if a < 60: return "50대"
    if a < 70: return "60대"
    return "70세 이상"

df["AGEG"] = df["DQ3"].apply(agegrp)
AGE_ORDER = ["20대(19-29)", "30대", "40대", "50대", "60대", "70세 이상"]
df["SEX"] = df["DQ2"].map({1: "남성", 2: "여성"})

def wrate(mask, base=None):
    """가중 이용률(%). mask: bool Series, base: bool Series(분모). NaN은 False 처리."""
    m = mask.fillna(False)
    if base is None:
        return 100 * (W * m).sum() / W.sum()
    b = base.fillna(False)
    return 100 * (W[b] * m[b]).sum() / W[b].sum()

def by_group(mask, gcol):
    out = {}
    m = mask.fillna(False)
    for g, sub in df.groupby(gcol):
        w = W[sub.index]
        out[g] = 100 * (w * m[sub.index]).sum() / w.sum()
    return out

# ---------- 매체 이용 정의 (전체 6,000명 기준; 스킵로직에 의한 NaN = 비이용) ----------
use = {}
use["종이신문 열독"] = df["Q1"] == 1
use["TV 뉴스"] = df["Q13"] == 1
use["인터넷 뉴스(모바일/PC)"] = (df["Q26_1"] == 1) | (df["Q26_2"] == 2)
use["포털 뉴스"] = (df["Q31_1"] == 1) | (df["Q31_2"] == 2)
use["메신저 뉴스"] = df["Q39"] == 1
use["SNS 뉴스"] = df["Q46"] == 1
use["온라인 동영상 플랫폼 이용"] = df["Q50"] == 1
use["온라인 동영상 플랫폼 뉴스"] = df["Q53"] == 1
use["숏폼 이용"] = df["Q58"] == 1
use["숏폼 뉴스"] = df["Q61"] == 1
use["OTT 뉴스"] = df["Q67"] == 1
use["생성형 AI 이용"] = df["Q70"] == 1
use["생성형 AI 뉴스"] = df["Q73"] == 1
use["라디오 뉴스"] = df["Q20"] == 1

# 다중응답형(Q26/Q31)은 _1(모바일)==1, _2(PC)==2 코드 확인 필요 → 값 라벨상 각 변수에 1/2 코드가 아니라
# Q26_1은 '모바일 선택 여부'(1), Q26_2는 'PC 선택 여부'(2)로 코딩됨. 검증:
chk = {
    "Q26_1": df["Q26_1"].dropna().unique().tolist(),
    "Q26_2": df["Q26_2"].dropna().unique().tolist(),
    "Q31_1": df["Q31_1"].dropna().unique().tolist(),
    "Q31_2": df["Q31_2"].dropna().unique().tolist(),
}

results = {"코드체크": chk}

# ---------- 1) 전체/성별/연령별 이용률 ----------
tbl_total = {k: round(wrate(v), 1) for k, v in use.items()}
tbl_age = pd.DataFrame({k: by_group(v, "AGEG") for k, v in use.items()}).T[AGE_ORDER].round(1)
tbl_sex = pd.DataFrame({k: by_group(v, "SEX") for k, v in use.items()}).T.round(1)

# 이용자 대비 뉴스 이용률 (조건부)
cond = {
    "AI 이용자 중 AI 뉴스": wrate(use["생성형 AI 뉴스"], base=use["생성형 AI 이용"]),
    "숏폼 이용자 중 숏폼 뉴스": wrate(use["숏폼 뉴스"], base=use["숏폼 이용"]),
    "동영상 이용자 중 동영상 뉴스": wrate(use["온라인 동영상 플랫폼 뉴스"], base=use["온라인 동영상 플랫폼 이용"]),
}

# ---------- 2) 뉴스 주 이용 경로 (Q84) ----------
q84_lab = meta.variable_value_labels["Q84"]
q84 = df["Q84"]
q84_dist = {}
for code, lab in q84_lab.items():
    q84_dist[f"{int(code)}. {lab[:22]}"] = round(100 * (W * (q84 == code)).sum() / W.sum(), 2)

# 경로 그룹: 언론사 직접(종이신문/홈페이지/앱/뉴스레터), 방송(TV/라디오), 포털, 동영상+숏폼, AI, 기타 플랫폼
grp_map = {
    "언론사 직접(신문·홈페이지·앱·뉴스레터)": [1, 4, 6, 7, 17],
    "TV·라디오": [2, 3],
    "인터넷 포털": [5],
    "온라인 동영상·숏폼": [13, 14],
    "생성형 AI·AI스피커": [15, 16],
    "기타 플랫폼(SNS·메신저·커뮤니티 등)": [8, 9, 10, 11, 12],
    "이용 안 함": [9998],
}
q84_grp_total = {g: round(100 * (W * q84.isin(c)).sum() / W.sum(), 1) for g, c in grp_map.items()}
q84_grp_age = pd.DataFrame(
    {g: by_group(q84.isin(c), "AGEG") for g, c in grp_map.items()}
).T[AGE_ORDER].round(1)

# ---------- 3) 언론사 직접 접점 지표 ----------
direct = {
    "신문 가구 정기구독률(BQ10)": wrate(df["BQ10"] == 1),
    "종이신문 열독 경로 중 집 정기구독(Q4_1, 열독자 기준)": wrate(df["Q4_1"] == 1, base=use["종이신문 열독"]),
    "포털에서 특정 언론사 구독/찾아봄(Q34_3 자주+매우자주, 포털뉴스 이용자)": wrate(df["Q34_3"] >= 4, base=df["Q34_3"].notna()),
    "동영상플랫폼 언론사 채널 구독/찾아봄(Q56_2 자주+매우자주, 동영상뉴스 이용자)": wrate(df["Q56_2"] >= 4, base=df["Q56_2"].notna()),
    "주 이용 경로가 언론사 직접(Q84: 1,4,6,7,17)": q84_grp_total["언론사 직접(신문·홈페이지·앱·뉴스레터)"],
}

# ---------- 4) 신뢰도 / 유료 이용 ----------
def wmean(col, base=None):
    v = df[col]
    ok = v.notna()
    if base is not None:
        ok &= base.fillna(False)
    return (W[ok] * v[ok]).sum() / W[ok].sum()

trust = {
    "뉴스 전반 신뢰도(Q87_1, 5점)": round(wmean("Q87_1"), 2),
    "실제 이용 뉴스 신뢰도(Q87_2, 5점)": round(wmean("Q87_2"), 2),
    "지인 공유 뉴스 신뢰도(Q88_1)": round(wmean("Q88_1"), 2),
    "1인 크리에이터 뉴스 신뢰도(Q88_2)": round(wmean("Q88_2"), 2),
    "포털 추천/배열 뉴스 신뢰도(Q88_3)": round(wmean("Q88_3"), 2),
    "언론인 신뢰도(Q95_5)": round(wmean("Q95_5"), 2),
    "1인 크리에이터 신뢰도(Q95_10)": round(wmean("Q95_10"), 2),
}
trust_pct = {
    "Q88_1 신뢰(4-5점) %": round(wrate(df["Q88_1"] >= 4), 1),
    "Q88_2 신뢰(4-5점) %": round(wrate(df["Q88_2"] >= 4), 1),
    "Q88_3 신뢰(4-5점) %": round(wrate(df["Q88_3"] >= 4), 1),
}
pay = {
    "온라인 뉴스 유료 이용 경험(Q97)": round(wrate(df["Q97"] == 1), 1),
    "향후 유료 이용 의향(Q97_1)": round(wrate(df["Q97_1"] == 1), 1),
}
pay_age = pd.DataFrame({
    "유료 경험": by_group(df["Q97"] == 1, "AGEG"),
    "유료 의향": by_group(df["Q97_1"] == 1, "AGEG"),
}).T[AGE_ORDER].round(1)

# ---------- 5) AI 뉴스 이용자 vs 비이용자 프로파일 ----------
ai_news = use["생성형 AI 뉴스"].fillna(False)
ai_user = use["생성형 AI 이용"].fillna(False)

def profile(mask):
    sub = df[mask]
    w = W[mask]
    p = {"n(무가중)": int(mask.sum()), "가중 비율%": round(100 * w.sum() / W.sum(), 1),
         "평균 연령": round((w * sub["DQ3"]).sum() / w.sum(), 1)}
    for g in AGE_ORDER:
        p[f"연령 {g}%"] = round(100 * (w * (sub["AGEG"] == g)).sum() / w.sum(), 1)
    for k in ["종이신문 열독", "TV 뉴스", "포털 뉴스", "온라인 동영상 플랫폼 뉴스", "숏폼 뉴스"]:
        m = use[k].fillna(False)
        p[f"{k}%"] = round(100 * (w * m[mask]).sum() / w.sum(), 1)
    for c, nm in [("Q87_1", "뉴스전반 신뢰도"), ("Q88_3", "포털뉴스 신뢰도"), ("Q88_2", "크리에이터뉴스 신뢰도")]:
        v = df[c][mask]
        ok = v.notna()
        p[nm] = round((w[ok] * v[ok]).sum() / w[ok].sum(), 2)
    p["유료 이용 경험%"] = round(100 * (w * (sub["Q97"] == 1)).sum() / w.sum(), 1)
    p["유료 이용 의향%"] = round(100 * (w * (sub["Q97_1"] == 1)).sum() / w.sum(), 1)
    p["대학 재학 이상%"] = round(100 * (w * (sub["BQ3"] >= 3)).sum() / w.sum(), 1)
    return p

prof = pd.DataFrame({
    "AI뉴스 이용자": profile(ai_news),
    "AI이용자(뉴스X 포함)": profile(ai_user),
    "AI 비이용자": profile(~ai_user),
    "전체": profile(pd.Series(True, index=df.index)),
})

# AI 이용률/AI 뉴스 이용률 연령별 상세 (연령 5세 구간 곡선용)
df["AGE5"] = (df["DQ3"] // 5 * 5).clip(upper=80)
age5 = df.groupby("AGE5").apply(
    lambda s: pd.Series({
        "AI 이용": 100 * (W[s.index] * (s["Q70"] == 1)).sum() / W[s.index].sum(),
        "AI 뉴스": 100 * (W[s.index] * (s["Q73"] == 1)).sum() / W[s.index].sum(),
        "숏폼 이용": 100 * (W[s.index] * (s["Q58"] == 1)).sum() / W[s.index].sum(),
        "숏폼 뉴스": 100 * (W[s.index] * (s["Q61"] == 1)).sum() / W[s.index].sum(),
        "n": len(s),
    }), include_groups=False).round(1)

# ---------- 저장 ----------
results.update({
    "1_전체 이용률(가중)": tbl_total,
    "1_조건부 이용률": {k: round(v, 1) for k, v in cond.items()},
    "2_Q84 주이용경로 상세": q84_dist,
    "2_Q84 경로 그룹(전체)": q84_grp_total,
    "3_언론사 직접 접점": {k: round(v, 1) for k, v in direct.items()},
    "4_신뢰도(5점 평균)": trust,
    "4_신뢰 비율": trust_pct,
    "4_유료": pay,
})

with open(f"{OUT}/results_2025.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

tbl_age.to_csv(f"{OUT}/t_2025_age_usage.csv", encoding="utf-8-sig")
tbl_sex.to_csv(f"{OUT}/t_2025_sex_usage.csv", encoding="utf-8-sig")
q84_grp_age.to_csv(f"{OUT}/t_2025_q84_group_age.csv", encoding="utf-8-sig")
pay_age.to_csv(f"{OUT}/t_2025_pay_age.csv", encoding="utf-8-sig")
prof.to_csv(f"{OUT}/t_2025_ai_profile.csv", encoding="utf-8-sig")
age5.to_csv(f"{OUT}/t_2025_age5_ai_shortform.csv", encoding="utf-8-sig")

print(json.dumps(results, ensure_ascii=False, indent=1))
print("\n== 연령별 이용률 ==\n", tbl_age.to_string())
print("\n== 성별 ==\n", tbl_sex.to_string())
print("\n== Q84 그룹 연령별 ==\n", q84_grp_age.to_string())
print("\n== 유료 연령별 ==\n", pay_age.to_string())
print("\n== AI 프로파일 ==\n", prof.to_string())
print("\n== 연령 5세 구간 ==\n", age5.to_string())
