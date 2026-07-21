/**
 * 6개 뉴스 DNA 유형 콘텐츠.
 * 수치(이름·비율·매체별 이용일수)는 eda/B_news_dna/05_quiz_simulation.py가 생성하는
 * quiz_model.json에서 파생 — 원시데이터는 한국언론진흥재단 <2025 언론수용자 조사>
 * (n=6,000, 가중치 적용). 태그라인은 taglines.json(공유 페이지 OG와 공용).
 * desc/facts는 편집 콘텐츠 — 인용 수치는 eda/B_news_dna/cluster_profile.csv 기준.
 */
import type { TypeId } from '../model/classify'
import model from '../quiz_model.json'
import TAGLINES from './taglines.json'

export interface NewsType {
  id: TypeId
  name: string
  emoji: string
  pct: number
  tagline: string
  desc: string
  /** 실데이터 기반 특징 3~4개 */
  facts: string[]
  /** 매체별 주간 뉴스 이용일수 (유형 가중 평균) — 미니 차트용 */
  days: { label: string; value: number }[]
  ageNote: string
  match: { id: TypeId; reason: string }
  gradient: string
  accent: string
}

const CLS = model.classes as Record<string, { name: string; pct: number; days_weighted: number[] }>
const DAY_LABELS = ['TV', '포털', '유튜브', '숏폼', '단톡방', 'SNS']

/** quiz_model.json에서 파생되는 수치 필드 */
function stat(id: TypeId): Pick<NewsType, 'id' | 'name' | 'pct' | 'tagline' | 'days'> {
  const c = CLS[String(id)]
  return {
    id,
    name: c.name,
    pct: Math.round(c.pct * 10) / 10,
    tagline: (TAGLINES as Record<string, string>)[String(id)],
    days: c.days_weighted.map((value, i) => ({ label: DAY_LABELS[i], value })),
  }
}

export const TYPES: Record<TypeId, NewsType> = {
  1: {
    ...stat(1),
    emoji: '📺',
    desc: '뉴스는 TV로 보는 거라고 믿는 당신. 일주일에 6일은 TV 뉴스와 함께합니다. 포털? 유튜브? 굳이요. 앵커가 정리해주는 세상이 제일 믿음직합니다.',
    facts: [
      '국민 3.5명 중 1명(28.3%)으로 최대 유형이에요',
      'TV 뉴스 주 6.1일 — 전 유형 중 TV 몰입도 1위',
      '디지털 뉴스 이용은 주 0.3일 이하로 사실상 0',
      '뉴스에 돈 낼 의향 0.6% — 본방은 공짜니까요',
    ],
    ageNote: '70대 이상의 68%가 이 유형 · 평균 62세',
    match: { id: 3, reason: '단톡방 전파자가 보내주는 링크가 당신의 유일한 디지털 뉴스 창구예요' },
    gradient: 'from-indigo-950 via-blue-900 to-slate-900',
    accent: '#60a5fa',
  },
  2: {
    ...stat(2),
    emoji: '🔀',
    desc: '저녁엔 TV 뉴스, 이동 중엔 포털 기사. 옛날 방식과 요즘 방식을 다 쓰는 균형파입니다. 대한민국 뉴스 소비의 "표준 모델"이 바로 당신이에요.',
    facts: [
      '국민의 24.3% — 두 번째로 큰 유형',
      'TV 주 5.9일 + 포털 주 5.1일의 안정적인 투트랙',
      '4050이 절반을 차지하는 든든한 허리 세대',
      '유튜브·숏폼 뉴스는 주 0.6일 — 영상 뉴스엔 신중해요',
    ],
    ageNote: '40~60대가 69% · 평균 51세',
    match: { id: 4, reason: '영상 뉴스 대식가를 만나면 "요즘은 유튜브가 더 빨라" 논쟁이 벌어져요' },
    gradient: 'from-teal-950 via-emerald-900 to-slate-900',
    accent: '#34d399',
  },
  5: {
    ...stat(5),
    emoji: '🌿',
    desc: '뉴스요? 굳이 찾아보진 않아요. 정말 큰일이면 어차피 누가 알려주니까. 뉴스 안 보는 게 아니라, 뉴스에 시간을 안 쓰는 라이프스타일입니다.',
    facts: [
      '국민 6명 중 1명(17.7%) — 생각보다 많죠?',
      '모든 매체에서 뉴스 접촉이 주 1일 안팎',
      '노인이 아니라 평균 44세, 2040이 63%를 차지해요',
      '정치·사회 관심도 전 유형 최저 (5점 만점에 2.7)',
    ],
    ageNote: '20~40대가 63% · 평균 44세',
    match: { id: 3, reason: '당신이 그나마 뉴스를 아는 건 단톡방 전파자 친구 덕분입니다' },
    gradient: 'from-stone-900 via-emerald-950 to-stone-950',
    accent: '#a3e635',
  },
  0: {
    ...stat(0),
    emoji: '📱',
    desc: '뉴스는 포털에서 텍스트로 읽는 게 제일 빠르고 정확하다고 믿는 당신. TV 뉴스는 답답해서 못 봅니다. 제목 보고, 골라 읽고, 끝. 효율의 민족.',
    facts: [
      '국민의 11.8%, 평균 37세 — 가장 젊은 축',
      '포털 주 5.7일 vs TV 주 0.7일의 극단적 텍스트 편식',
      '20대의 30%가 이 유형이에요',
      '뉴스 유료 경험 2.5% — 전체 평균의 1.6배로 의외의 지불파',
    ],
    ageNote: '2030이 64% · 평균 37세',
    match: { id: 1, reason: 'TV 순정파 부모님과 명절에 만나면 서로의 뉴스를 이해 못 해요' },
    gradient: 'from-slate-900 via-cyan-950 to-slate-950',
    accent: '#22d3ee',
  },
  4: {
    ...stat(4),
    emoji: '🍽️',
    desc: 'TV 뉴스 보고, 유튜브로 해설 챙겨 보고, 쇼츠로 속보까지. 뉴스에 진심인 헤비 유저입니다. 세상 돌아가는 걸 모르면 못 견디는 타입.',
    facts: [
      '국민의 10.9% — 뉴스 관심도 전 유형 1위 (3.5/5)',
      'TV 5.8일 + 포털 5.7일 + 유튜브 5.9일 + 숏폼 3.5일의 풀코스',
      '유료 경험 3.5% — 전체 평균의 2배 이상',
      '뉴스 신뢰도도 높은 편 — 많이 보고, 많이 믿어요',
    ],
    ageNote: '4050이 49% · 평균 49세',
    match: { id: 2, reason: '투트랙과는 뉴스 얘기가 잘 통하는데, 당신이 늘 한 발 더 깊게 알아요' },
    gradient: 'from-orange-950 via-red-900 to-slate-900',
    accent: '#fb923c',
  },
  3: {
    ...stat(3),
    emoji: '🗣️',
    desc: '뉴스를 보면 끝이 아니라 시작. 단톡방에 공유하고, 댓글 달고, 좋아요 누릅니다. 당신 주변 사람들이 세상 소식을 아는 건 8할이 당신 덕분이에요.',
    facts: [
      '국민의 7.0% — 가장 희귀한 유형이에요',
      '공유 경험 88% (국민 평균 13%의 6.6배), 댓글 53%',
      '뉴스에 돈 낼 의향 7.1% — 전 유형 압도적 1위',
      '메신저·SNS·숏폼·포털을 넘나드는 멀티 플랫포머',
    ],
    ageNote: '2030이 52% · 평균 41세',
    match: { id: 5, reason: '뉴스 미니멀족이 당신의 주요 구독자입니다. 본인은 모르지만요' },
    gradient: 'from-fuchsia-950 via-purple-900 to-slate-900',
    accent: '#e879f9',
  },
}

export const TYPE_IDS: TypeId[] = [1, 2, 5, 0, 4, 3]
