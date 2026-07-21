# -*- coding: utf-8 -*-
"""
뉴스 DNA 유형화: 클러스터링 본체
- 피처: 매체별 뉴스 이용 일수 12개(0~7일 → /7) + 참여(0~3 → /3). 자연 스케일 공유 → range scaling.
  * z-score 표준화는 희소 매체(팟캐스트 등 이용률 1~2%)의 z가 10 이상으로 폭주해 인공 микро클러스터를
    만들었음(실루엣 0.09, Ward ARI 0.16). 태도(관심/신뢰/유료)는 클러스터링에서 제외하고 프로파일로 검증
    (포함 시 실루엣 0.20 vs 미포함 0.29).
- k=3~10 실루엣/엘보/Ward-ARI 비교 → k=6 채택 (실루엣 최고 0.294, 시드 ARI 0.91~1.0, 부트스트랩 ARI 0.89)
출력: kselect.csv, cluster_assign.csv
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.decomposition import PCA
from pathlib import Path

BASE = str(Path(__file__).resolve().parent)
f = pd.read_csv(f"{BASE}/features.csv")

MEDIA = ["d_paper", "d_magazine", "d_tv", "d_radio", "d_portal", "d_messenger",
         "d_sns", "d_video", "d_shortform", "d_ott", "d_ai", "d_podcast"]
X = pd.concat([f[MEDIA] / 7.0, f["engagement"] / 3.0], axis=1).values

# ---------- k 선택 ----------
rows = []
for k in range(3, 11):
    km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(X)
    sil = silhouette_score(X, km.labels_, sample_size=4000, random_state=0)
    ward = AgglomerativeClustering(n_clusters=k, linkage="ward").fit(X)
    rows.append({"k": k, "inertia": km.inertia_, "silhouette": round(sil, 3),
                 "ari_vs_ward": round(adjusted_rand_score(km.labels_, ward.labels_), 3),
                 "min_cluster_pct": round(pd.Series(km.labels_).value_counts(normalize=True).min() * 100, 1)})
ks = pd.DataFrame(rows)
ks.to_csv(f"{BASE}/kselect.csv", index=False)
print(ks.to_string(index=False))

K = 6
km = KMeans(n_clusters=K, n_init=50, random_state=42).fit(X)
lab = km.labels_

# ---------- 강건성 ----------
ward = AgglomerativeClustering(n_clusters=K, linkage="ward").fit(X)
print(f"\nARI(KMeans vs Ward, k={K}):", round(adjusted_rand_score(lab, ward.labels_), 3))
seed_aris = [adjusted_rand_score(lab, KMeans(n_clusters=K, n_init=20, random_state=s).fit(X).labels_)
             for s in [1, 7, 123, 2025, 999]]
print("시드별 ARI:", [round(a, 3) for a in seed_aris])
rng = np.random.RandomState(0)
boot = []
for _ in range(10):
    idx = rng.choice(len(X), int(len(X) * 0.8), replace=False)
    kmb = KMeans(n_clusters=K, n_init=10, random_state=0).fit(X[idx])
    boot.append(adjusted_rand_score(lab, kmb.predict(X)))
print(f"부트스트랩(80퍼센트 서브샘플) ARI: mean={np.mean(boot):.3f} min={np.min(boot):.3f}")

# ---------- PCA ----------
pca = PCA(n_components=2, random_state=0)
XY = pca.fit_transform(X)
cols = MEDIA + ["engagement"]
print("PCA 설명분산:", pca.explained_variance_ratio_.round(3))
print("PC1 로딩:", pd.Series(pca.components_[0], index=cols).round(2).sort_values(key=abs, ascending=False).head(6).to_dict())
print("PC2 로딩:", pd.Series(pca.components_[1], index=cols).round(2).sort_values(key=abs, ascending=False).head(6).to_dict())

out = f.copy()
out["cluster"] = lab
out["pc1"], out["pc2"] = XY[:, 0], XY[:, 1]
out.to_csv(f"{BASE}/cluster_assign.csv", index=False)
print("\nsaved cluster_assign.csv, 클러스터 크기(가중%):")
print(out.groupby("cluster")["WT"].sum().div(out["WT"].sum()).mul(100).round(1))
