# -*- coding: utf-8 -*-
"""A. AI 게이트키퍼 — 차트 3종 (가중치 적용, 2025 언론수용자 조사 + 시계열)"""
import pyreadstat
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

from pathlib import Path

_HERE = Path(__file__).resolve().parent
OUT = str(_HERE)
D = str(_HERE.parents[1] / "data")

# 팔레트(검증 완료): 엔티티 고정 배색
C = {
    "종이신문": "#4a3aa7", "TV 뉴스": "#eda100", "포털 뉴스": "#2a78d6",
    "동영상 뉴스": "#eb6834", "숏폼 뉴스": "#1baf7a", "AI 뉴스": "#e87ba4",
    "숏폼 이용": "#1baf7a", "AI 이용": "#e87ba4",
}
SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"

def style_ax(ax):
    ax.set_facecolor(SURF)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#d8d7d3")
    ax.tick_params(colors=INK2, labelsize=10)
    ax.grid(axis="y", color="#eceae6", linewidth=0.8)
    ax.set_axisbelow(True)

# ---------------- 데이터 ----------------
df, meta = pyreadstat.read_sav(f"{D}/2025_언론수용자조사/3. 2025 언론수용자 조사_최종데이터.SAV")
W = df["WT"]
def agegrp(a):
    if a < 30: return "20대"
    if a < 40: return "30대"
    if a < 50: return "40대"
    if a < 60: return "50대"
    if a < 70: return "60대"
    return "70세+"
df["AGEG"] = df["DQ3"].apply(agegrp)
AGE = ["20대", "30대", "40대", "50대", "60대", "70세+"]

use = {
    "종이신문": df["Q1"] == 1,
    "TV 뉴스": df["Q13"] == 1,
    "포털 뉴스": (df["Q31_1"] == 1) | (df["Q31_2"] == 2),
    "메신저 뉴스": df["Q39"] == 1,
    "SNS 뉴스": df["Q46"] == 1,
    "동영상 뉴스": df["Q53"] == 1,
    "숏폼 뉴스": df["Q61"] == 1,
    "OTT 뉴스": df["Q67"] == 1,
    "AI 뉴스": df["Q73"] == 1,
}
def wrate_by_age(mask):
    m = mask.fillna(False)
    return [100 * (W[df["AGEG"] == g] * m[df["AGEG"] == g]).sum() / W[df["AGEG"] == g].sum() for g in AGE]

heat = pd.DataFrame({k: wrate_by_age(v) for k, v in use.items()}, index=AGE).T

# ---------------- (a) 히트맵: 연령대 x 매체 뉴스 이용률 ----------------
fig, ax = plt.subplots(figsize=(8.6, 5.6), dpi=200)
fig.patch.set_facecolor(SURF)
cmap = LinearSegmentedColormap.from_list("blue_seq", ["#f2f7fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
im = ax.imshow(heat.values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
ax.set_xticks(range(len(AGE)), AGE, fontsize=11, color=INK)
ax.set_yticks(range(len(heat.index)), heat.index, fontsize=11, color=INK)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
# 셀 경계(2px 서피스 갭)
ax.set_xticks(np.arange(-0.5, len(AGE)), minor=True)
ax.set_yticks(np.arange(-0.5, len(heat.index)), minor=True)
ax.grid(which="minor", color=SURF, linewidth=2)
ax.tick_params(which="minor", length=0)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        v = heat.values[i, j]
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=10,
                color="#ffffff" if v > 55 else INK,
                fontweight="bold" if v == heat.values[i].max() else "normal")
ax.set_title("연령대별 매체 뉴스 이용률 (2025, 지난 1주일, %)", fontsize=13, color=INK, pad=12, loc="left")
ax.text(0, 1.02, "", transform=ax.transAxes)
cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
cb.outline.set_visible(False)
cb.ax.tick_params(colors=INK2, labelsize=9)
fig.text(0.01, 0.01, "자료: 2025 언론수용자 조사(n=6,000, 가중치 적용). 각 행 최대값 굵게.", fontsize=8, color=INK2)
fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig(f"{OUT}/chart_a_heatmap_age_media.png", facecolor=SURF, bbox_inches="tight")
plt.close(fig)

# ---------------- (b) 시계열 추이 ----------------
ts = pd.read_csv(f"{OUT}/t_timeseries_2018_2025.csv", index_col=0)
series = ["TV 뉴스", "포털 뉴스", "동영상 뉴스", "종이신문", "숏폼 뉴스", "AI 뉴스"]
years_main = [2018, 2019, 2020, 2021, 2023, 2024, 2025]  # 2022 제외(조사설계 상이)

fig, ax = plt.subplots(figsize=(9.2, 5.8), dpi=200)
fig.patch.set_facecolor(SURF)
style_ax(ax)
for s in series:
    sub = ts.loc[[y for y in years_main if y in ts.index and pd.notna(ts.loc[y, s])], s]
    if len(sub) == 0:
        continue
    ax.plot(sub.index, sub.values, color=C[s], linewidth=2, marker="o", markersize=5,
            markerfacecolor=C[s], markeredgecolor=SURF, markeredgewidth=1.2, zorder=3)
    # 2022 참고점(속 빈 마커)
    if 2022 in ts.index and pd.notna(ts.loc[2022, s]):
        ax.plot([2022], [ts.loc[2022, s]], marker="o", markersize=5, linestyle="none",
                markerfacecolor=SURF, markeredgecolor=C[s], markeredgewidth=1.4, zorder=3)
    y_end = sub.values[-1]
    off = {"TV 뉴스": 0, "포털 뉴스": 0, "동영상 뉴스": 1.5, "종이신문": 0.5, "숏폼 뉴스": -1.5, "AI 뉴스": -0.5}[s]
    ax.annotate(f"{s} {y_end:.1f}", xy=(2025, y_end), xytext=(2025.15, y_end + off),
                fontsize=10, color=INK, va="center", fontweight="bold")
ax.set_xlim(2017.7, 2026.6)
ax.set_ylim(0, 95)
ax.set_xticks([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
ax.set_ylabel("뉴스 이용률(%)", fontsize=10, color=INK2)
ax.set_title("매체별 뉴스 이용률 추이 (2018-2025, 지난 1주일)", fontsize=13, color=INK, pad=12, loc="left")
fig.text(0.01, 0.01, "자료: 언론수용자 조사 각 연도 원자료 재분석(가중치 적용). 2022년(속 빈 점)은 표본·조사설계가 달라 공식 시계열에서도 제외되는 해. "
                     "숏폼 뉴스는 2023년, 생성형 AI 뉴스는 2025년 신설 문항.", fontsize=8, color=INK2)
fig.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig(f"{OUT}/chart_b_timeseries.png", facecolor=SURF, bbox_inches="tight")
plt.close(fig)

# ---------------- (c) AI/숏폼 연령 곡선 ----------------
df["AGE5"] = (df["DQ3"].clip(lower=20, upper=84) // 5 * 5).astype(int)  # 19세는 20-24 구간에 포함
buckets = sorted(df["AGE5"].unique())
def curve(mask):
    m = mask.fillna(False)
    out = []
    for b in buckets:
        idx = df["AGE5"] == b
        out.append(100 * (W[idx] * m[idx]).sum() / W[idx].sum())
    return out

curves = {
    "숏폼 이용": curve(df["Q58"] == 1),
    "숏폼 뉴스": curve(df["Q61"] == 1),
    "AI 이용": curve(df["Q70"] == 1),
    "AI 뉴스": curve(df["Q73"] == 1),
}
fig, ax = plt.subplots(figsize=(9.0, 5.6), dpi=200)
fig.patch.set_facecolor(SURF)
style_ax(ax)
for name, vals in curves.items():
    dashed = "이용" in name
    ax.plot(buckets, vals, color=C[name], linewidth=2, linestyle="--" if dashed else "-",
            marker="o", markersize=5, markerfacecolor=C[name] if not dashed else SURF,
            markeredgecolor=SURF if not dashed else C[name], markeredgewidth=1.2, zorder=3)
    lab_y = {"숏폼 이용": vals[0] + 3, "숏폼 뉴스": vals[0] + 3, "AI 이용": vals[0] + 3, "AI 뉴스": vals[0] - 4.5}[name]
    ax.annotate(f"{name} {vals[0]:.0f}%", xy=(buckets[0], vals[0]), xytext=(buckets[0] - 0.4, lab_y),
                fontsize=10, color=INK, fontweight="bold")
ax.set_xticks(buckets, [f"{b}-{b+4}" if b < 80 else "80+" for b in buckets], fontsize=9)
ax.set_ylim(0, 100)
ax.set_xlabel("연령(5세 구간)", fontsize=10, color=INK2)
ax.set_ylabel("이용률(%)", fontsize=10, color=INK2)
ax.set_title("숏폼·생성형 AI 이용률과 뉴스 이용률의 연령 곡선 (2025)", fontsize=13, color=INK, pad=12, loc="left")
ax.legend(curves.keys(), frameon=False, fontsize=9, loc="upper right", labelcolor=INK)
fig.text(0.01, 0.01, "자료: 2025 언론수용자 조사(n=6,000, 가중치 적용). 점선=플랫폼 이용률, 실선=해당 플랫폼 뉴스 이용률. 19세는 20-24 구간 포함.",
         fontsize=8, color=INK2)
fig.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig(f"{OUT}/chart_c_ai_shortform_age.png", facecolor=SURF, bbox_inches="tight")
plt.close(fig)

print("charts saved")
