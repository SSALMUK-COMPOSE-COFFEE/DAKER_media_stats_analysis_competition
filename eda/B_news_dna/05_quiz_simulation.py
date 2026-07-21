# -*- coding: utf-8 -*-
"""
웹 진단 테스트 시뮬레이션: 실제 응답자 6,000명의 이용일수를
퀴즈 보기 구간(0 / 1 / 2~3 / 4~5 / 6~7일 → 0/1/2.5/4.5/6.5)으로 뭉갠 뒤에도
유형 분류가 유지되는지 검증.

- 입력 축 7개: TV/포털/동영상/숏폼/메신저/SNS 일수 + 참여도(공유·좋아요·댓글 경험 개수 0~3)
- 분류기 후보: (a) 구간값으로 재학습한 의사결정나무 (b) 클러스터 중심 최근접(nearest centroid)
- 최종 채택: (b) nearest centroid — 정확도 동급이면서 2순위 중심(서브 DNA)까지 제공 가능
- 출력: quiz_model.json (eda/ 및 web/src/ 동일 파일 — 웹이 그대로 import)
  classes에 표시용 가중 통계(pct, 매체별 가중 이용일수)도 포함 — 웹 문구/차트 수치의 단일 소스
"""
import json
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from pathlib import Path

_HERE = Path(__file__).resolve().parent
BASE = str(_HERE)
WEB = str(_HERE.parents[1] / "web/src")
d = pd.read_csv(f"{BASE}/cluster_assign.csv")
y = d["cluster"].values

DAY_COLS = ["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger", "d_sns"]
COLS = DAY_COLS + ["engagement"]  # engagement = 공유+좋아요+댓글 경험(0~3), 웹 참여 문항과 1:1

# 퀴즈 보기 구간(5지선다): 전혀(0) / 주1일(1) / 주2~3일(2.5) / 주4~5일(4.5) / 거의 매일(6.5)
BUCKET_VALUES = {"전혀 안 봄": 0, "주 1일": 1.0, "주 2~3일": 2.5, "주 4~5일": 4.5, "거의 매일": 6.5}

def bucketize(v):
    v = np.asarray(v, dtype=float)
    out = np.zeros_like(v)
    out[v == 1] = 1.0
    out[(v >= 2) & (v <= 3)] = 2.5
    out[(v >= 4) & (v <= 5)] = 4.5
    out[v >= 6] = 6.5
    return out

Xb = d[COLS].copy()
for c in DAY_COLS:
    Xb[c] = bucketize(d[c].values)
# 참여도(0~3)는 그대로

cv = StratifiedKFold(5, shuffle=True, random_state=0)

# (a) 구간 입력으로 재학습한 트리 — 비교용
accs = {}
for depth in [4, 5, 6, 7]:
    clf = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=30, random_state=0)
    accs[depth] = cross_val_score(clf, Xb, y, cv=cv).mean()
best_depth = max(accs, key=accs.get)
print("(a) 구간입력 트리 CV:", {k: round(v, 3) for k, v in accs.items()}, "best:", best_depth)

# (b) nearest centroid — 최종 채택
# 중심 = 클러스터별 '원 일수' 평균(구간화 전). 거리 계산 전 일수/7, 참여/3 스케일링.
cent = d.groupby("cluster")[COLS].mean()
scale = np.array([7.0] * 6 + [3.0])
Xs = Xb.values / scale
Cs = cent.values / scale
pred = cent.index.values[np.argmin(((Xs[:, None, :] - Cs[None, :, :]) ** 2).sum(axis=2), axis=1)]
acc_nc = (pred == y).mean()
print(f"(b) nearest centroid 일치도: {acc_nc:.4f}  ← 최종 채택")

NAMES = {0: "포털 텍스트파", 1: "TV 순정파", 2: "본방+포털 투트랙",
         3: "단톡방 전파자", 4: "영상 뉴스 대식가", 5: "뉴스 미니멀족"}

recall = {NAMES[c]: round(float((pred[y == c] == c).mean()), 3) for c in sorted(NAMES)}
print("클래스별 재현율:", recall)

pct = d.groupby("cluster")["WT"].sum() / d["WT"].sum() * 100  # 가중 비율
# 표시용: 매체별 가중 이용일수 (Result 화면 '일주일 차트'는 인구 대표값이어야 하므로 가중)
days_w = d.groupby("cluster").apply(
    lambda g: pd.Series(np.average(g[DAY_COLS], weights=g["WT"], axis=0), index=DAY_COLS),
    include_groups=False)

model = {
    "method": "nearest_centroid",
    "note": "축: 매체별 뉴스 이용일수 6개(5지선다 구간값) + 참여도(공유/좋아요/댓글 경험 개수 0-3). "
            "거리 계산 전 일수/7, 참여/3로 스케일링.",
    "fidelity_vs_full_clustering": round(float(acc_nc), 3),
    "per_class_recall": recall,
    "bucket_values": BUCKET_VALUES,
    "features": COLS,
    "scale": [7, 7, 7, 7, 7, 7, 3],
    "classes": {str(k): {"name": NAMES[k], "pct": round(float(pct[k]), 2),
                         "days_weighted": [round(float(x), 2) for x in days_w.loc[k].values]}
                for k in sorted(NAMES)},
    "centroids": {str(k): [round(float(x), 4) for x in cent.loc[k].values] for k in sorted(NAMES)},
}

for path in (f"{BASE}/quiz_model.json", f"{WEB}/quiz_model.json"):
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(model, fp, ensure_ascii=False, indent=1)
    print("저장:", path)
print(f"\n트리 CV {accs[best_depth]:.1%} vs centroid {acc_nc:.1%} → centroid 채택(서브 DNA 제공 가능)")
