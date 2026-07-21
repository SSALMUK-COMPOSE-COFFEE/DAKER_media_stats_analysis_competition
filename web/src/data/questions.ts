/**
 * 어댑티브 퀴즈 구조:
 *  1. 게이트(멀티선택): 지난 일주일 세상 소식을 마주친 곳 — 원 조사의 '이용 여부' 게이트 문항에 대응
 *  2. 선택한 매체만 빈도 질문(5지선다) — 원 조사의 '이용 일수(0~7일)' 문항에 대응
 *  3. 참여 행동 멀티선택(0~3) — 공유/좋아요/댓글 경험 문항에 대응
 * 선택하지 않은 매체 = 0일. 측정 축·구간은 2025 언론수용자 조사와 1:1 (일치도 92.4%).
 */

export type Axis = 'd_tv' | 'd_portal' | 'd_video' | 'd_shortform' | 'd_messenger' | 'd_sns'

/** classify() 입력 순서 */
export const AXIS_ORDER: Axis[] = ['d_tv', 'd_portal', 'd_video', 'd_shortform', 'd_messenger', 'd_sns']

export interface Medium {
  axis: Axis
  emoji: string
  /** 게이트 화면 카드 라벨 */
  gateLabel: string
  gateSub: string
  /** 빈도 질문 */
  freqTitle: string
  freqSub: string
  /** 5지선다 라벨 (0 / 1 / 2.5 / 4.5 / 6.5일 순) — 매체별 플레이버 */
  freqLabels: [string, string, string, string, string]
}

export const BUCKET_VALUES = [0, 1, 2.5, 4.5, 6.5] as const
export const BUCKET_SUBS = ['0일', '주 1일', '주 2~3일', '주 4~5일', '주 6~7일'] as const

export const MEDIA: Medium[] = [
  {
    axis: 'd_tv',
    emoji: '📺',
    gateLabel: 'TV',
    gateSub: '뉴스·시사 프로그램',
    freqTitle: 'TV에서 세상 소식이 나오는 걸 본 날, 일주일에 얼마나 돼요?',
    freqSub: '밥 먹으면서 흘려들은 것도, 가족이 틀어놓은 것도 다 쳐요.',
    freqLabels: ['어쩌다 한 번', '한 번 정도', '종종 봤다', '꽤 자주', '저녁 루틴이지'],
  },
  {
    axis: 'd_portal',
    emoji: '🟢',
    gateLabel: '포털',
    gateSub: '네이버·다음 기사',
    freqTitle: '포털에서 기사를 열어본 날은 일주일에 얼마나?',
    freqSub: '검색하다 걸린 기사, 메인에 떠서 눌러본 것 전부 포함.',
    freqLabels: ['거의 안 열었다', '한 번 정도', '종종 열었다', '꽤 자주', '숨 쉬듯이 본다'],
  },
  {
    axis: 'd_video',
    emoji: '▶️',
    gateLabel: '유튜브',
    gateSub: '뉴스·시사 영상',
    freqTitle: '유튜브에서 뉴스·시사 영상을 본 날은?',
    freqSub: '언론사 채널이든 시사 유튜버든. 쇼츠 말고 일반 영상요.',
    freqLabels: ['거의 안 봤다', '한 번 정도', '종종 봤다', '꽤 자주', '정주행 중'],
  },
  {
    axis: 'd_shortform',
    emoji: '🤳',
    gateLabel: '쇼츠·릴스',
    gateSub: '틱톡 포함',
    freqTitle: '쇼츠·릴스 넘기다가 세상 소식을 만난 날은?',
    freqSub: '내가 찾은 게 아니라 알고리즘이 떠먹여준 것도 포함.',
    freqLabels: ['거의 없었다', '한 번 정도', '종종 떴다', '꽤 자주', '알고리즘이 자꾸 줌'],
  },
  {
    axis: 'd_messenger',
    emoji: '💬',
    gateLabel: '카톡',
    gateSub: '단톡방·오픈채팅',
    freqTitle: '단톡방·오픈채팅에서 세상 소식을 접한 날은?',
    freqSub: '가족 단톡방 링크, 친구가 보낸 기사 다 포함.',
    freqLabels: ['거의 없었다', '한 번 정도', '종종 있었다', '꽤 자주', '단톡방이 곧 뉴스룸'],
  },
  {
    axis: 'd_sns',
    emoji: '📸',
    gateLabel: 'SNS',
    gateSub: '인스타·X·페북',
    freqTitle: 'SNS 피드에서 세상 소식을 본 날은?',
    freqSub: '팔로우한 계정이든 추천 피드든.',
    freqLabels: ['거의 못 봤다', '한 번 정도', '종종 봤다', '꽤 자주', '피드가 곧 신문'],
  },
]

export const GATE = {
  emoji: '🗞️',
  title: '지난 일주일, 세상 돌아가는 소식을 마주친 곳을 전부 골라요',
  sub: '뉴스, 사건사고, 정치, 경제… 스치듯 본 것도 포함이에요.',
  noneLabel: '🙈 어디서도 못 본 것 같은데?',
}

export const ENGAGEMENT = {
  emoji: '🙋',
  title: '뉴스나 이슈를 보고 나면, 해본 적 있는 행동은?',
  sub: '지난 일주일 기준. 눈으로만 봤으면 맨 아래를.',
  options: [
    { label: '누군가에게 공유했다', emoji: '📤' },
    { label: '좋아요·추천을 눌렀다', emoji: '👍' },
    { label: '댓글을 달았다', emoji: '✍️' },
  ],
  noneLabel: '🙈 아무것도 안 했다',
}
