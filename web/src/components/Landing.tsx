import { TYPES, TYPE_IDS } from '../data/types'

export default function Landing({ onStart }: { onStart: () => void }) {
  return (
    <div className="min-h-dvh bg-gradient-to-b from-[#0c0a14] via-[#141028] to-[#0c0a14] flex flex-col items-center justify-center px-6 py-12">
      <main className="w-full max-w-md text-center fade-up">
        <p className="text-sm tracking-widest text-violet-300/80 font-semibold mb-4">
          국가 통계로 만든 진짜 데이터 테스트
        </p>
        <h1 className="text-4xl font-extrabold leading-tight mb-3">
          나의 뉴스 <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">DNA</span>는?
        </h1>
        <p className="text-white/60 leading-relaxed mb-8">
          대한민국 국민의 뉴스 소비는 6가지 유형으로 갈립니다.
          <br />
          빠르면 2문항, 길어도 1분이면 끝나요.
        </p>

        <div className="grid grid-cols-3 gap-2 mb-8">
          {TYPE_IDS.map((id) => {
            const t = TYPES[id]
            return (
              <div
                key={id}
                className="rounded-xl bg-white/5 border border-white/10 px-2 py-3 backdrop-blur-sm"
              >
                <div className="text-2xl mb-1">{t.emoji}</div>
                <div className="text-[11px] font-semibold text-white/80 leading-tight">{t.name}</div>
                <div className="text-[10px] text-white/40 mt-0.5">{t.pct}%</div>
              </div>
            )
          })}
        </div>

        <button
          onClick={onStart}
          className="w-full rounded-2xl bg-gradient-to-r from-violet-500 to-fuchsia-500 py-4 text-lg font-bold shadow-lg shadow-violet-500/25 active:scale-[0.98] transition-transform cursor-pointer"
        >
          내 뉴스 DNA 찾기 →
        </button>

        <p className="mt-6 text-[11px] leading-relaxed text-white/35">
          한국언론진흥재단 〈2025 언론수용자 조사〉 원시데이터(6,000명)
          <br />
          군집 분석 기반 · 유형 일치도 92.4%
        </p>
      </main>
    </div>
  )
}
