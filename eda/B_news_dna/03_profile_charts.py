# -*- coding: utf-8 -*-
"""
뉴스 DNA 유형화: 클러스터 프로파일링(가중) + 차트 3종
출력: cluster_profile.csv, chart_pca.png, chart_heatmap.png, chart_age.png
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

from pathlib import Path

BASE = str(Path(__file__).resolve().parent)
d = pd.read_csv(f"{BASE}/cluster_assign.csv")

NAMES = {
    1: "TV 순정파",        # 28.3% TV 외길, 60대
    2: "본방+포털 투트랙",  # 24.3% TV와 포털 병행, 50대
    5: "뉴스 미니멀족",     # 17.7% 모든 매체 저이용
    0: "포털 텍스트파",     # 11.8% 포털 집중, TV 이탈, 30대
    4: "영상 뉴스 대식가",  # 10.9% TV+포털+유튜브+숏폼 풀코스
    3: "단톡방 전파자",     # 7.0% 메신저/SNS 중심 + 공유/댓글 참여 최고
}
ORDER = [1, 2, 5, 0, 4, 3]  # 크기순
COLORS = {1: "#2a78d6", 2: "#eb6834", 5: "#1baf7a", 0: "#eda100", 4: "#e87ba4", 3: "#4a3aa7"}
d["name"] = d["cluster"].map(NAMES)

MEDIA = ["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger", "d_sns",
         "d_paper", "d_radio", "d_ott", "d_ai", "d_podcast", "d_magazine"]
MEDIA_KO = ["TV", "포털", "동영상(유튜브)", "숏폼", "메신저", "SNS",
            "종이신문", "라디오", "OTT", "생성형AI", "팟캐스트", "잡지"]

# ---------- 프로파일 테이블 (가중) ----------
W = d["WT"].sum()
rows = []
for c in ORDER:
    g = d[d["cluster"] == c]
    w = g["WT"]
    def wm(col):
        return np.average(g[col], weights=w)
    r = {"cluster": c, "name": NAMES[c], "pct_weighted": w.sum() / W * 100, "n": len(g),
         "age_mean": wm("age"), "female_pct": (w[g["sex"] == 2].sum() / w.sum()) * 100,
         "age_std": np.sqrt(np.average((g["age"] - wm("age")) ** 2, weights=w))}
    for m, ko in zip(MEDIA, MEDIA_KO):
        r[f"days_{ko}"] = wm(m)
    r.update({"참여(0-3)": wm("engagement"), "공유%": wm("p_share") * 100, "댓글%": wm("p_comment") * 100,
              "정치사회관심(1-5)": wm("interest"), "뉴스신뢰(1-5)": wm("trust_news"),
              "비전통출처신뢰(1-5)": wm("trust_new_src"),
              "유료경험%": wm("paid_exp") * 100, "유료의향%": wm("paid_intent") * 100})
    # 연령대 구성
    band = pd.cut(g["age"], [18, 29, 39, 49, 59, 69, 120], labels=["20대", "30대", "40대", "50대", "60대", "70+"])
    for b in ["20대", "30대", "40대", "50대", "60대", "70+"]:
        r[f"age_{b}%"] = w[band == b].sum() / w.sum() * 100
    rows.append(r)
prof = pd.DataFrame(rows)
prof.round(2).to_csv(f"{BASE}/cluster_profile.csv", index=False)
print(prof.round(1).to_string(index=False))

# 연령 내 다양성 검증: 같은 연령대 안에서 클러스터가 얼마나 갈리는지
print("\n[연령대 × 클러스터 분포(가중 행%)] — 연령만으로 유형이 결정되지 않음을 확인")
d["band"] = pd.cut(d["age"], [18, 29, 39, 49, 59, 69, 120], labels=["20대", "30대", "40대", "50대", "60대", "70+"])
ct = d.pivot_table(index="band", columns="name", values="WT", aggfunc="sum", observed=True)
ct = ct.div(ct.sum(axis=1), axis=0) * 100
print(ct.round(1).to_string())
ct.round(2).to_csv(f"{BASE}/age_x_cluster.csv")

SURF, TXT1, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e8e7e3"

def style_ax(ax):
    ax.set_facecolor(SURF)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=TXT2, labelsize=9)

# ---------- 차트 1: PCA 산점도 ----------
fig, ax = plt.subplots(figsize=(9, 7), dpi=160, facecolor=SURF)
style_ax(ax)
for c in ORDER:
    g = d[d["cluster"] == c]
    ax.scatter(g["pc1"], g["pc2"], s=9, alpha=0.45, lw=0, color=COLORS[c],
               label=f"{NAMES[c]} ({prof.loc[prof.cluster == c, 'pct_weighted'].iloc[0]:.0f}%)")
for c in ORDER:  # 직접 라벨(대비 WARN 완화)
    g = d[d["cluster"] == c]
    ax.annotate(NAMES[c], (g["pc1"].median(), g["pc2"].median()), ha="center",
                fontsize=11, fontweight="bold", color=TXT1,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=COLORS[c], alpha=0.85))
ax.set_xlabel("PC1: 디지털 뉴스 강도 (포털·동영상·숏폼) →", color=TXT2)
ax.set_ylabel("PC2: TV 뉴스 강도 →", color=TXT2)
ax.set_title("한국인 뉴스 소비 6유형 — PCA 2차원 (2025 언론수용자 조사, n=6,000)",
             color=TXT1, fontsize=13, pad=12)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=9, labelcolor=TXT2)
fig.tight_layout()
fig.savefig(f"{BASE}/chart_pca.png", bbox_inches="tight", facecolor=SURF)
plt.close(fig)

# ---------- 차트 2: 클러스터 × 매체 히트맵 (주간 이용일수, 단일 색상 시퀀셜) ----------
H = prof.set_index("name")[[f"days_{k}" for k in MEDIA_KO]]
H.columns = MEDIA_KO
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=160, facecolor=SURF)
im = ax.imshow(H.values, cmap="Blues", vmin=0, vmax=7, aspect="auto")
ax.set_xticks(range(len(MEDIA_KO)), MEDIA_KO, rotation=30, ha="right", color=TXT1, fontsize=10)
ax.set_yticks(range(len(H)), [f"{n} ({prof.pct_weighted.iloc[i]:.0f}%)" for i, n in enumerate(H.index)],
              color=TXT1, fontsize=10)
for i in range(H.shape[0]):
    for j in range(H.shape[1]):
        v = H.values[i, j]
        ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=9,
                color="white" if v > 4 else TXT1)
ax.set_title("유형별 매체 뉴스 이용 일수 (주간 0~7일, 가중 평균)", color=TXT1, fontsize=13, pad=10)
cb = fig.colorbar(im, ax=ax, shrink=0.85, label="일/주")
cb.outline.set_visible(False)
fig.tight_layout()
fig.savefig(f"{BASE}/chart_heatmap.png", bbox_inches="tight", facecolor=SURF)
plt.close(fig)

# ---------- 차트 3: 클러스터별 연령 분포 ----------
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=160, facecolor=SURF)
style_ax(ax)
data = [d.loc[d["cluster"] == c, "age"] for c in ORDER]
parts = ax.violinplot(data, vert=False, showmedians=True, widths=0.8)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(COLORS[ORDER[i]])
    pc.set_alpha(0.7)
    pc.set_edgecolor("none")
for k in ["cmedians", "cbars", "cmins", "cmaxes"]:
    parts[k].set_color(TXT2)
    parts[k].set_linewidth(1.2)
ax.set_yticks(range(1, len(ORDER) + 1),
              [f"{NAMES[c]} ({prof.loc[prof.cluster == c, 'pct_weighted'].iloc[0]:.0f}%)" for c in ORDER],
              color=TXT1, fontsize=10)
ax.set_xlabel("연령 (세)", color=TXT2)
ax.set_title("유형별 연령 분포 — 유형은 연령과 상관되지만 연령만으로 갈리지 않음", color=TXT1, fontsize=13, pad=10)
ax.xaxis.grid(True, color=GRID, lw=0.8)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(f"{BASE}/chart_age.png", bbox_inches="tight", facecolor=SURF)
plt.close(fig)
print("\ncharts saved")
