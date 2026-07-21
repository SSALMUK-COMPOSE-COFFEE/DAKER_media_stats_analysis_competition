import { useState } from 'react'
import { TYPES } from '../data/types'
import { FIDELITY, type ClassifyResult } from '../model/classify'

interface Props {
  result: ClassifyResult
  onRestart: () => void
}

export default function Result({ result, onRestart }: Props) {
  const t = TYPES[result.main]
  const sub = TYPES[result.sub]
  const match = TYPES[t.match.id]
  const [copied, setCopied] = useState(false)
  const maxDay = 7

  const copyText = async (s: string) => {
    // clipboard API는 보안 컨텍스트(HTTPS/localhost) 전용 — http 시연 환경은 execCommand로 폴백
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(s)
      return
    }
    const ta = document.createElement('textarea')
    ta.value = s
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    const ok = document.execCommand('copy')
    ta.remove()
    if (!ok) throw new Error('copy failed')
  }

  const share = async () => {
    const url = `${window.location.origin}/r/${t.id}/`
    const text = `나의 뉴스 DNA는 ${t.emoji} ${t.name} (국민의 ${t.pct}%)! 너는 어떤 유형이야?`
    if (navigator.share) {
      try {
        await navigator.share({ title: '뉴스 DNA 테스트', text, url })
      } catch {
        /* 사용자가 취소 — 클립보드로 폴백하지 않음 */
      }
      return
    }
    try {
      await copyText(`${text}\n${url}`)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      window.prompt('복사가 안 되는 환경이에요. 아래 링크를 직접 복사해 주세요:', `${text}\n${url}`)
    }
  }

  return (
    <div className={`min-h-dvh bg-gradient-to-b ${t.gradient} px-6 py-10 flex flex-col items-center`}>
      <div className="w-full max-w-md">
        {/* ── 메인 카드 ── */}
        <div className="text-center pop-in">
          <p className="text-xs tracking-widest text-white/50 font-semibold mb-3">나의 뉴스 DNA</p>
          <div className="text-7xl mb-4">{t.emoji}</div>
          <h1 className="text-3xl font-extrabold mb-2">{t.name}</h1>
          <p className="text-white/70 font-medium mb-4">"{t.tagline}"</p>
          <div
            className="inline-block rounded-full px-4 py-1.5 text-sm font-bold mb-6"
            style={{ backgroundColor: `${t.accent}26`, color: t.accent }}
          >
            대한민국 국민의 {t.pct}%
          </div>
          <p className="text-[15px] leading-relaxed text-white/80 text-left bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-sm">
            {t.desc}
          </p>
        </div>

        {/* ── 팩트 카드 ── */}
        <section className="mt-6 fade-up">
          <h2 className="text-sm font-bold text-white/50 tracking-wider mb-3">📊 데이터가 말하는 당신</h2>
          <ul className="flex flex-col gap-2">
            {t.facts.map((f, i) => (
              <li
                key={i}
                className="flex gap-3 items-start rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-sm leading-relaxed text-white/85"
              >
                <span className="mt-0.5" style={{ color: t.accent }}>
                  ◆
                </span>
                {f}
              </li>
            ))}
          </ul>
          <p className="mt-2 text-[11px] text-white/35 text-right">{t.ageNote}</p>
        </section>

        {/* ── 일주일 차트 ── */}
        <section className="mt-6 fade-up">
          <h2 className="text-sm font-bold text-white/50 tracking-wider mb-3">
            📅 {t.name}의 뉴스 일주일 <span className="font-normal">(유형 평균, 일/주)</span>
          </h2>
          <div className="rounded-2xl bg-white/5 border border-white/10 p-5 flex flex-col gap-2.5">
            {t.days.map((d) => (
              <div key={d.label} className="flex items-center gap-3">
                <span className="w-14 text-xs text-white/60 shrink-0">{d.label}</span>
                <div className="flex-1 h-2.5 rounded-full bg-white/10 overflow-hidden">
                  <div
                    className="h-full rounded-full bar-grow"
                    style={{ width: `${(d.value / maxDay) * 100}%`, backgroundColor: t.accent }}
                  />
                </div>
                <span className="w-8 text-xs text-white/50 tabular-nums text-right">{d.value.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ── 서브 DNA & 케미 ── */}
        <section className="mt-6 grid grid-cols-1 gap-3 fade-up">
          {result.answers.length > 0 && (
            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 flex items-center gap-4">
              <span className="text-3xl">{sub.emoji}</span>
              <div>
                <p className="text-xs text-white/45 font-semibold mb-0.5">서브 DNA</p>
                <p className="text-sm font-bold">
                  {sub.name} <span className="font-normal text-white/50">기질도 갖고 있어요</span>
                </p>
              </div>
            </div>
          )}
          <div className="rounded-2xl bg-white/5 border border-white/10 p-4">
            <div className="flex items-center gap-4 mb-2">
              <span className="text-3xl">{match.emoji}</span>
              <div>
                <p className="text-xs text-white/45 font-semibold mb-0.5">환상의 케미</p>
                <p className="text-sm font-bold">{match.name}</p>
              </div>
            </div>
            <p className="text-[13px] leading-relaxed text-white/65">{t.match.reason}</p>
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="mt-8 flex flex-col gap-3 fade-up">
          <button
            onClick={share}
            className="w-full rounded-2xl py-4 text-lg font-bold shadow-lg active:scale-[0.98] transition cursor-pointer"
            style={{ backgroundColor: t.accent, color: '#0c0a14' }}
          >
            {copied ? '링크 복사 완료! ✓' : '결과 공유하기 📤'}
          </button>
          <button
            onClick={onRestart}
            className="w-full rounded-2xl border border-white/20 bg-white/5 py-3.5 font-semibold text-white/80 hover:bg-white/10 active:scale-[0.98] transition cursor-pointer"
          >
            {result.answers.length === 0 ? '나도 테스트하기' : '다시 하기'}
          </button>
        </section>

        <footer className="mt-10 text-center text-[11px] leading-relaxed text-white/35">
          유형 분류: 한국언론진흥재단 〈2025 언론수용자 조사〉
          <br />
          원시데이터(n=6,000, 국가승인통계) K-means 군집 분석
          <br />
          전체 설문 기반 유형과의 일치도 {(FIDELITY * 100).toFixed(1)}%
        </footer>
      </div>
    </div>
  )
}
