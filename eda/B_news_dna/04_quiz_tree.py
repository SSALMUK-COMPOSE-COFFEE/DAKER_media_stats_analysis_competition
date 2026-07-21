# -*- coding: utf-8 -*-
"""
진단 테스트 실현성 검증: 소수 문항으로 6유형 예측이 가능한가
- 문항 후보: '지난 1주일 ○○로 뉴스를 본 날 수(0~7)' 유형의 설문 문항과 1:1 대응되는 피처
- 의사결정나무(해석 가능) 5-fold 층화 CV 정확도. 베이스라인 = 최대 클러스터 비율(28.3%)
출력: quiz_tree.txt (문항 세트별 정확도 + 최종 트리 규칙)
"""
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import cross_val_score, StratifiedKFold
from pathlib import Path

BASE = str(Path(__file__).resolve().parent)
d = pd.read_csv(f"{BASE}/cluster_assign.csv")
y = d["cluster"]

SETS = {
    "5문항(TV/포털/동영상/숏폼/메신저)": ["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger"],
    "6문항(+공유경험)": ["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger", "p_share"],
    "7문항(+SNS)": ["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger", "d_sns", "p_share"],
    "8문항(+댓글)": ["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger", "d_sns", "p_share", "p_comment"],
}
cv = StratifiedKFold(5, shuffle=True, random_state=0)
lines = []
lines.append(f"베이스라인(최빈 클러스터 항상 예측): {y.value_counts(normalize=True).max():.3f}")
best = None
for name, cols in SETS.items():
    accs = {}
    for depth in [4, 5, 6, 7, 8]:
        clf = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=30, random_state=0)
        acc = cross_val_score(clf, d[cols], y, cv=cv).mean()
        accs[depth] = acc
    bd = max(accs, key=accs.get)
    lines.append(f"{name}: CV 정확도 " + " ".join(f"d{k}={v:.3f}" for k, v in accs.items()) + f"  → best depth={bd}")
    if best is None or accs[bd] > best[2]:
        best = (name, cols, accs[bd], bd)

name, cols, acc, depth = best
lines.append(f"\n[최종] {name}, depth={depth}, 5-fold CV 정확도 = {acc:.3f}")
clf = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=30, random_state=0).fit(d[cols], y)
NAMES = {0: "포털 텍스트파", 1: "TV 순정파", 2: "본방+포털 투트랙", 3: "단톡방 전파자", 4: "영상 뉴스 대식가", 5: "뉴스 미니멀족"}
lines.append("클래스: " + str({k: NAMES[k] for k in sorted(NAMES)}))
lines.append(export_text(clf, feature_names=cols, max_depth=4))

# 얕은 트리(진단테스트 그대로 쓸 수 있는 규칙) 정확도
shallow = DecisionTreeClassifier(max_depth=4, min_samples_leaf=50, random_state=0)
acc4 = cross_val_score(shallow, d[["d_tv", "d_portal", "d_video", "d_shortform", "d_messenger", "p_share"]], y, cv=cv).mean()
lines.append(f"\n참고: 6문항 + depth=4 (분기 최대 4번) 단순 규칙 정확도 = {acc4:.3f}")

txt = "\n".join(lines)
print(txt)
open(f"{BASE}/quiz_tree.txt", "w").write(txt)
