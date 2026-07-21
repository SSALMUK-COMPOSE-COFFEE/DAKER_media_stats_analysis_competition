import model from '../quiz_model.json'

export type TypeId = 0 | 1 | 2 | 3 | 4 | 5

export interface ClassifyResult {
  main: TypeId
  sub: TypeId
  /** 축별 사용자 응답 (일수 6개 + 참여 0~3) */
  answers: number[]
}

const SCALE = model.scale as number[]
const CENTROIDS = Object.fromEntries(
  Object.entries(model.centroids).map(([k, v]) => [Number(k), v as number[]]),
) as Record<number, number[]>

/**
 * 최근접 중심(nearest centroid) 분류.
 * 축과 스케일링은 원 클러스터링(2025 언론수용자 조사 K-means)과 동일.
 * 전체 설문 기반 유형과의 일치도 92.4% (eda/B_news_dna/05_quiz_simulation.py)
 */
export function classify(answers: number[]): ClassifyResult {
  const x = answers.map((v, i) => v / SCALE[i])
  const dists = (Object.keys(CENTROIDS) as unknown as number[]).map((k) => {
    const c = CENTROIDS[k].map((v, i) => v / SCALE[i])
    const d = x.reduce((acc, xi, i) => acc + (xi - c[i]) ** 2, 0)
    return { k: Number(k) as TypeId, d }
  })
  dists.sort((a, b) => a.d - b.d)
  return { main: dists[0].k, sub: dists[1].k, answers }
}

export const FIDELITY = model.fidelity_vs_full_clustering as number
export const CLASS_PCT = Object.fromEntries(
  Object.entries(model.classes).map(([k, v]) => [Number(k), (v as { pct: number }).pct]),
) as Record<number, number>
