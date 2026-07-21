# -*- coding: utf-8 -*-
"""
2022 언론수용자 조사(개인용 58,936 / 가구용 30,138) 기반
"뉴스 사막(지역 뉴스 격차)" EDA — 지역별 뉴스 이용 격차 및 뉴스 취약지수 프로토타입.

지역 해상도: 공개 데이터는 시도(17) + 도시규모(대도시/중소도시/군)까지만 제공
(원 설문 SQ1-1은 시군구/읍면동을 수집했으나 공개용에서는 제외됨 — 코드북 p.1 확인).
가중치: WT (개인용/가구용 각각 존재, 평균 1로 정규화된 표본 가중치).
"""
import pandas as pd
import numpy as np
import pyreadstat
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

_HERE = Path(__file__).resolve().parent
BASE = str(_HERE.parents[1] / "data/2022_언론수용자조사/2022 언론수용자 조사 DATA_통계표_보고서 등/데이터") + "/"
OUT = str(_HERE) + "/"

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# dataviz palette (light mode)
BLUE = "#2a78d6"; ORANGE = "#eb6834"; INK = "#0b0b0b"; INK2 = "#52514e"; GRID = "#e5e4e0"
SEQ_BLUES = ["#dbe9f9", "#b3d0f0", "#84b2e5", "#5595dd", "#2a78d6", "#1d5aa6", "#123f77"]

SIDO = {1: "서울", 2: "부산", 3: "대구", 4: "인천", 5: "광주", 6: "대전", 7: "울산", 8: "세종",
        9: "경기", 10: "강원", 11: "충북", 12: "충남", 13: "전북", 14: "전남", 15: "경북",
        16: "경남", 17: "제주"}
SIZE = {1: "대도시", 2: "중소도시", 3: "군지역"}
CAPITAL = {"서울", "인천", "경기"}


def wmean(g, col, wt="WT"):
    m = g[col].notna()
    if m.sum() == 0:
        return np.nan
    return np.average(g.loc[m, col], weights=g.loc[m, wt])


def wrate(g, mask_col, wt="WT"):
    """전체 응답자 대비 가중 비율(%). mask_col: bool 시리즈 이름."""
    return 100 * np.average(g[mask_col].astype(float), weights=g[wt])


def load():
    try:
        ind, mi = pyreadstat.read_sav(BASE + "2022 언론수용자 조사_개인용_공개용 데이터.SAV")
    except Exception:
        ind, mi = pyreadstat.read_sav(BASE + "2022 언론수용자 조사_개인용_공개용 데이터.SAV",
                                      encoding="cp949")
    try:
        hh, mh = pyreadstat.read_sav(BASE + "2022 언론수용자 조사_가구용_공개용 데이터.SAV")
    except Exception:
        hh, mh = pyreadstat.read_sav(BASE + "2022 언론수용자 조사_가구용_공개용 데이터.SAV",
                                     encoding="cp949")
    return ind, hh


def prepare(ind):
    d = ind.copy()
    d["sido"] = d["SQ1"].map(SIDO)
    d["size"] = d["BA27"].map(SIZE)
    d["capital"] = np.where(d["sido"].isin(CAPITAL), "수도권", "비수도권")
    # 지표 (분모 = 전체 응답자; 스킵 로직으로 비이용자는 NaN → False 처리)
    d["paper"] = d["Q1"].eq(1)                                  # 종이신문 열독(주간)
    d["local_paper"] = d["Q7"].eq(1)                            # 지역신문 열독(전원 응답)
    d["inet_news"] = d["Q33_1"].eq(1) | d["Q33_2"].eq(1)        # 인터넷 뉴스(모바일/PC)
    d["mobile_news"] = d["Q33_1"].eq(1)
    d["tv_news"] = d["Q19"].eq(1)                               # TV 뉴스/시사 시청
    d["radio_news"] = d["Q27"].eq(1)
    d["msg_news"] = d["Q45"].eq(1)
    d["sns_news"] = d["Q51"].eq(1)
    d["video_news"] = d["Q57"].eq(1)
    d["news_nonuse"] = d["Q68"].eq(9998)                        # 지난 1주 뉴스/시사 미이용
    # 뉴스 레퍼토리(이용 뉴스 플랫폼 수, 0~7)
    d["repertoire"] = d[["paper", "tv_news", "radio_news", "inet_news",
                         "msg_news", "sns_news", "video_news"]].sum(axis=1)
    # 신뢰도(1~5, 결측 없음 확인)
    d["trust_all"] = d["Q72_10"].where(d["Q72_10"].between(1, 5))
    d["trust_used"] = d["Q73"].where(d["Q73"].between(1, 5))
    # 취약계층
    d["age60"] = d["BA22"].isin([5, 6])           # 60대 + 70대 이상
    d["age70"] = d["BA22"].eq(6)
    d["lowedu"] = d["BA23"].eq(1)                 # 중졸 이하
    d["lowinc"] = d["BA25"].isin([1, 2])          # 가구소득 200만원 미만
    d["vuln_person"] = d["age60"] | d["lowedu"] | d["lowinc"]
    return d


def region_table(d, by):
    rows = []
    for key, g in d.groupby(by):
        rows.append({
            by if isinstance(by, str) else "region": key,
            "n": len(g), "wt_n": g["WT"].sum(),
            "종이신문열독률": wrate(g, "paper"),
            "지역신문열독률": wrate(g, "local_paper"),
            "인터넷뉴스이용률": wrate(g, "inet_news"),
            "모바일뉴스이용률": wrate(g, "mobile_news"),
            "TV뉴스시청률": wrate(g, "tv_news"),
            "뉴스미이용률": wrate(g, "news_nonuse"),
            "뉴스레퍼토리": wmean(g, "repertoire"),
            "뉴스신뢰도": wmean(g, "trust_all"),
            "이용뉴스신뢰도": wmean(g, "trust_used"),
            "60대이상비중": wrate(g, "age60"),
            "중졸이하비중": wrate(g, "lowedu"),
            "저소득비중": wrate(g, "lowinc"),
        })
    t = pd.DataFrame(rows).set_index(rows[0].keys().__iter__().__next__())
    return t


def build_index(t):
    """뉴스 취약지수: 4개 취약 성분의 min-max 정규화 평균 (0~100, 높을수록 취약)."""
    comp = pd.DataFrame(index=t.index)
    comp["뉴스미이용"] = t["뉴스미이용률"]
    comp["디지털소외"] = 100 - t["인터넷뉴스이용률"]
    comp["지역언론부재"] = 100 - t["지역신문열독률"]
    comp["레퍼토리빈약"] = -t["뉴스레퍼토리"]
    norm = (comp - comp.min()) / (comp.max() - comp.min())
    t = t.copy()
    t["취약지수"] = norm.mean(axis=1) * 100
    # 강건성: z-score 합성과의 순위 상관
    z = (comp - comp.mean()) / comp.std()
    zi = z.mean(axis=1)
    t["취약지수_z"] = zi
    rho = t["취약지수"].rank().corr(zi.rank(), method="spearman")
    return t, norm, rho


def style_ax(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.xaxis.grid(True, color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def chart_indicators(t):
    metrics = [("종이신문열독률", "%"), ("지역신문열독률", "%"), ("인터넷뉴스이용률", "%"),
               ("뉴스미이용률", "%"), ("뉴스레퍼토리", "개"), ("뉴스신뢰도", "점(5점)")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, (m, unit) in zip(axes.flat, metrics):
        s = t[m].sort_values()
        colors = [ORANGE if i in CAPITAL else BLUE for i in s.index]
        ax.barh(s.index, s.values, color=colors, height=0.62, zorder=2)
        ax.set_title(f"{m} ({unit})", fontsize=11, color=INK, loc="left", fontweight="bold")
        style_ax(ax)
        top, bot = s.index[-1], s.index[0]
        for name in (top, bot):
            v = s[name]
            ax.text(v, name, f" {v:.1f}", va="center", fontsize=8.5, color=INK2)
    fig.suptitle("시도별 뉴스 이용 지표 (2022 언론수용자 조사, 가중치 적용, n=58,936)",
                 fontsize=14, color=INK, fontweight="bold")
    handles = [mpl.patches.Patch(color=ORANGE, label="수도권"),
               mpl.patches.Patch(color=BLUE, label="비수도권")]
    fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT + "01_sido_indicators.png", dpi=160, facecolor="white")
    plt.close(fig)


def chart_index(t):
    s = t["취약지수"].sort_values()
    fig, ax = plt.subplots(figsize=(9, 7))
    colors = [ORANGE if i in CAPITAL else BLUE for i in s.index]
    ax.barh(s.index, s.values, color=colors, height=0.62, zorder=2)
    for name, v in s.items():
        ax.text(v + 1, name, f"{v:.0f}", va="center", fontsize=9, color=INK2)
    style_ax(ax)
    ax.set_xlim(0, 105)
    ax.set_title("뉴스 취약지수 (0~100, 높을수록 취약)\n"
                 "성분: 뉴스 미이용률 · 인터넷뉴스 비이용 · 지역신문 비열독 · 뉴스 레퍼토리 빈약",
                 fontsize=12, color=INK, loc="left", fontweight="bold")
    handles = [mpl.patches.Patch(color=ORANGE, label="수도권"),
               mpl.patches.Patch(color=BLUE, label="비수도권")]
    ax.legend(handles=handles, frameon=False, fontsize=10, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT + "02_vulnerability_index.png", dpi=160, facecolor="white")
    plt.close(fig)


TILE_POS = {  # (col,row) 타일 그리드 지도
    "서울": (1, 1), "인천": (0, 1), "경기": (1, 0), "강원": (2, 0),
    "충북": (2, 1), "세종": (1, 2), "충남": (0, 2), "대전": (1, 3),
    "경북": (3, 2), "대구": (3, 3), "울산": (4, 3), "부산": (4, 4),
    "전북": (1, 4), "전남": (0, 5), "광주": (1, 5), "경남": (3, 4),
    "제주": (0, 7),
}


def chart_tile_map(t):
    s = t["취약지수"]
    vmin, vmax = s.min(), s.max()
    cmap = mpl.colors.LinearSegmentedColormap.from_list("blues", SEQ_BLUES)
    fig, ax = plt.subplots(figsize=(7, 8.5))
    for name, (c, r) in TILE_POS.items():
        v = s[name]
        frac = (v - vmin) / (vmax - vmin)
        color = cmap(frac)
        txt = "white" if frac > 0.55 else INK
        ax.add_patch(mpl.patches.FancyBboxPatch(
            (c + 0.05, -r - 0.95), 0.9, 0.9,
            boxstyle="round,pad=0,rounding_size=0.08", fc=color, ec="white", lw=2))
        ax.text(c + 0.5, -r - 0.42, name, ha="center", va="center",
                fontsize=11, color=txt, fontweight="bold")
        ax.text(c + 0.5, -r - 0.70, f"{v:.0f}", ha="center", va="center",
                fontsize=10, color=txt)
    ax.set_xlim(-0.3, 5.3); ax.set_ylim(-8.3, 0.3)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("뉴스 취약지수 타일 지도 (진할수록 취약)", fontsize=13,
                 color=INK, fontweight="bold", loc="left")
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(vmin, vmax))
    cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
    cb.outline.set_visible(False); cb.ax.tick_params(colors=INK2, labelsize=9)
    fig.tight_layout()
    fig.savefig(OUT + "03_tile_map.png", dpi=160, facecolor="white")
    plt.close(fig)


def chart_double_gap(d):
    """도시규모 × 연령/학력 교차: 뉴스 미이용률과 인터넷뉴스 이용률."""
    groups = ["대도시", "중소도시", "군지역"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    specs = [("news_nonuse", "지난 1주 뉴스/시사 미이용률 (%)"),
             ("inet_news", "인터넷뉴스 이용률 (%)")]
    for ax, (col, title) in zip(axes, specs):
        x = np.arange(len(groups)); w = 0.38
        y_old, y_rest = [], []
        for gname in groups:
            g = d[d["size"] == gname]
            old = g[g["age60"]]
            rest = g[~g["age60"]]
            y_old.append(wrate(old, col))
            y_rest.append(wrate(rest, col))
        b1 = ax.bar(x - w / 2, y_rest, w - 0.02, color=BLUE, label="19~59세", zorder=2)
        b2 = ax.bar(x + w / 2, y_old, w - 0.02, color=ORANGE, label="60세 이상", zorder=2)
        for bars in (b1, b2):
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
                        f"{b.get_height():.1f}", ha="center", fontsize=9, color=INK2)
        ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=10, color=INK)
        ax.set_title(title, fontsize=11.5, color=INK, loc="left", fontweight="bold")
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(GRID); ax.spines["bottom"].set_color(GRID)
        ax.yaxis.grid(True, color=GRID, lw=0.7); ax.set_axisbelow(True)
        ax.tick_params(colors=INK2, labelsize=9)
        ax.legend(frameon=False, fontsize=10)
    fig.suptitle("취약계층(60세 이상) × 취약지역(군지역) 이중 격차", fontsize=13.5,
                 color=INK, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUT + "04_double_gap.png", dpi=160, facecolor="white")
    plt.close(fig)


def main():
    ind, hh = load()
    d = prepare(ind)

    print("=" * 60, "\n[1] 지역 해상도 & 표본")
    nt = d.groupby("sido").agg(n=("WT", "size"), wt_n=("WT", "sum")).sort_values("n")
    print(nt)
    print("\n시도 x 도시규모 n:")
    print(pd.crosstab(d["sido"], d["size"]))
    print("\n가구용 지역변수: SQ1(시도), SQ2(도시규모)만 존재 — 시군구 없음")

    print("\n" + "=" * 60, "\n[2] 시도별 지표 (가중치 적용)")
    t = region_table(d, "sido")
    t.index.name = "sido"
    pd.set_option("display.width", 250)
    print(t.round(2))
    t.round(3).to_csv(OUT + "sido_indicators.csv", encoding="utf-8-sig")

    print("\n[2b] 도시규모별 지표")
    tsize = region_table(d, "size")
    print(tsize.round(2))
    tsize.round(3).to_csv(OUT + "size_indicators.csv", encoding="utf-8-sig")

    print("\n[2c] 수도권 vs 비수도권")
    tcap = region_table(d, "capital")
    print(tcap.round(2))

    # 가구용 구독률
    hh2 = hh.copy()
    hh2["sido"] = hh2["SQ1"].map(SIDO)
    hh2["size"] = hh2["SQ2"].map(SIZE)
    sub_sido = hh2.groupby("sido").apply(
        lambda g: 100 * np.average(g["Q1"].eq(1), weights=g["WT"]), include_groups=False)
    sub_size = hh2.groupby("size").apply(
        lambda g: 100 * np.average(g["Q1"].eq(1), weights=g["WT"]), include_groups=False)
    print("\n[2d] 가구 종이신문 정기구독률(%) by 시도:\n", sub_sido.round(2).sort_values())
    print("by 도시규모:\n", sub_size.round(2))
    sub_sido.round(3).to_csv(OUT + "hh_subscription_by_sido.csv", encoding="utf-8-sig")

    print("\n" + "=" * 60, "\n[3] 뉴스 취약지수")
    t2, norm, rho = build_index(t)
    rank = t2["취약지수"].sort_values(ascending=False)
    print(rank.round(1))
    print(f"\nmin-max 합성 vs z-score 합성 순위 스피어만 상관: {rho:.3f}")
    t2.round(3).to_csv(OUT + "vulnerability_index.csv", encoding="utf-8-sig")

    cap = t2.loc[list(CAPITAL & set(t2.index))]
    noncap = t2.loc[[i for i in t2.index if i not in CAPITAL]]
    print(f"\n수도권 평균 취약지수 {cap['취약지수'].mean():.1f} vs "
          f"비수도권 {noncap['취약지수'].mean():.1f}")

    print("\n" + "=" * 60, "\n[4] 이중 격차 (취약계층 x 취약지역)")
    for col, lab in [("news_nonuse", "뉴스미이용률"), ("inet_news", "인터넷뉴스이용률"),
                     ("local_paper", "지역신문열독률")]:
        rows = {}
        for sz, g in d.groupby("size"):
            rows[sz] = {
                "60세이상": wrate(g[g["age60"]], col),
                "19~59세": wrate(g[~g["age60"]], col),
                "중졸이하": wrate(g[g["lowedu"]], col),
                "고졸이상": wrate(g[~g["lowedu"]], col),
            }
        print(f"\n{lab}(%):\n", pd.DataFrame(rows).T.round(1))
    # 취약계층 비중 지역 분포
    print("\n60세 이상 인구 비중(%):",
          {sz: round(wrate(g, "age60"), 1) for sz, g in d.groupby("size")})
    old_gun = d[(d["size"] == "군지역") & d["age60"]]
    old_metro = d[(d["size"] == "대도시") & d["age60"]]
    print(f"군지역 60+ 뉴스미이용률 {wrate(old_gun, 'news_nonuse'):.1f}% vs "
          f"대도시 60+ {wrate(old_metro, 'news_nonuse'):.1f}%")

    print("\n" + "=" * 60, "\n[5] 공식 보고서 대조 검증")
    checks = {
        "종이신문 열독률(공식 9.7%)": wrate(d, "paper"),
        "TV뉴스 시청률(공식 76.8%)": wrate(d, "tv_news"),
        "모바일 신문기사 열독률(공식 74.1%) [Q6_2|Q6_3]": 100 * np.average(
            d["Q6_2"].eq(1) | d["Q6_3"].eq(1), weights=d["WT"]),
    }
    for k, v in checks.items():
        print(f"  {k}: 내 계산 {v:.1f}%")
    lp = d[d["local_paper"]]
    print(f"  지역신문 이용자 가중 n(공식 3,401): {lp['WT'].sum():,.0f}")
    print(f"  지역신문 인식 '지역정보 유용'(공식 3.83점/69.8%): "
          f"{wmean(lp, 'Q7_1_4'):.2f}점 / "
          f"{100 * np.average(lp['Q7_1_4'].ge(4), weights=lp['WT']):.1f}%")

    chart_indicators(t2)
    chart_index(t2)
    chart_tile_map(t2)
    chart_double_gap(d)
    print("\n차트 4개 저장 완료:", OUT)


if __name__ == "__main__":
    main()
