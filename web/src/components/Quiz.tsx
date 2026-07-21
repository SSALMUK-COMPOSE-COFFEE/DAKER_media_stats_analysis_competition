import { useState } from 'react'
import {
  MEDIA,
  GATE,
  ENGAGEMENT,
  AXIS_ORDER,
  BUCKET_VALUES,
  BUCKET_SUBS,
  type Axis,
} from '../data/questions'

interface Props {
  onFinish: (answers: number[]) => void
}

/**
 * 어댑티브 플로우: 게이트(매체 멀티선택) → 선택 매체별 빈도 → 참여 행동.
 * 아무 매체도 안 고르면 게이트 → 참여로 바로 점프 (최소 2문항).
 */
export default function Quiz({ onFinish }: Props) {
  const [phase, setPhase] = useState<'gate' | 'freq' | 'engage'>('gate')
  const [selected, setSelected] = useState<Set<Axis>>(new Set())
  const [freqIdx, setFreqIdx] = useState(0)
  const [days, setDays] = useState<Partial<Record<Axis, number>>>({})
  const [engageSel, setEngageSel] = useState<Set<number>>(new Set())

  const selectedMedia = MEDIA.filter((m) => selected.has(m.axis))
  const totalSteps = 1 + selectedMedia.length + 1
  const currentStep = phase === 'gate' ? 1 : phase === 'freq' ? 2 + freqIdx : totalSteps
  const progress = ((currentStep - 1) / totalSteps) * 100

  const finish = (engagement: number) => {
    const answers = [...AXIS_ORDER.map((a) => days[a] ?? 0), engagement]
    onFinish(answers)
  }

  const toggleGate = (axis: Axis) => {
    const next = new Set(selected)
    if (next.has(axis)) next.delete(axis)
    else next.add(axis)
    setSelected(next)
  }

  const submitGate = (none: boolean) => {
    if (none || selected.size === 0) {
      setSelected(new Set())
      setPhase('engage')
    } else {
      setPhase('freq')
    }
    window.scrollTo(0, 0)
  }

  const submitFreq = (value: number) => {
    const m = selectedMedia[freqIdx]
    setDays((prev) => ({ ...prev, [m.axis]: value }))
    if (freqIdx + 1 < selectedMedia.length) {
      setFreqIdx(freqIdx + 1)
    } else {
      setPhase('engage')
    }
    window.scrollTo(0, 0)
  }

  const toggleEngage = (i: number) => {
    const next = new Set(engageSel)
    if (next.has(i)) next.delete(i)
    else next.add(i)
    setEngageSel(next)
  }

  return (
    <div className="min-h-dvh bg-gradient-to-b from-[#0c0a14] via-[#141028] to-[#0c0a14] flex flex-col items-center px-6 py-8">
      <div className="w-full max-w-md">
        {/* progress */}
        <div className="flex items-center gap-3 mb-10">
          <div className="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-400 to-fuchsia-400 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-xs text-white/50 font-medium tabular-nums">
            {currentStep}/{totalSteps}
          </span>
        </div>

        {/* ── 게이트: 매체 멀티선택 ── */}
        {phase === 'gate' && (
          <div className="fade-up">
            <div className="text-4xl mb-4">{GATE.emoji}</div>
            <h2 className="text-xl font-bold leading-snug mb-2">{GATE.title}</h2>
            <p className="text-sm text-white/50 mb-8">{GATE.sub}</p>

            <div className="grid grid-cols-2 gap-2.5">
              {MEDIA.map((m) => (
                <button
                  key={m.axis}
                  onClick={() => toggleGate(m.axis)}
                  className={`rounded-xl border px-4 py-4 text-left active:scale-[0.97] transition cursor-pointer ${
                    selected.has(m.axis)
                      ? 'border-fuchsia-400/70 bg-fuchsia-500/20'
                      : 'border-white/10 bg-white/5 hover:bg-white/10'
                  }`}
                >
                  <div className="text-2xl mb-1.5">{m.emoji}</div>
                  <div className="font-bold text-sm">{m.gateLabel}</div>
                  <div className="text-[11px] text-white/45 mt-0.5">{m.gateSub}</div>
                </button>
              ))}
            </div>

            <div className="mt-3 flex flex-col gap-2.5">
              <button
                onClick={() => submitGate(true)}
                className="rounded-xl border border-white/10 bg-white/5 px-5 py-3.5 text-left font-medium text-white/70 hover:bg-white/10 active:scale-[0.98] transition cursor-pointer"
              >
                {GATE.noneLabel}
              </button>
              {selected.size > 0 && (
                <button
                  onClick={() => submitGate(false)}
                  className="rounded-2xl bg-gradient-to-r from-violet-500 to-fuchsia-500 py-4 text-lg font-bold shadow-lg shadow-violet-500/25 active:scale-[0.98] transition cursor-pointer"
                >
                  다음 ({selected.size}개 선택) →
                </button>
              )}
            </div>
          </div>
        )}

        {/* ── 빈도: 선택한 매체만 ── */}
        {phase === 'freq' && (
          <div key={freqIdx} className="fade-up">
            <div className="text-4xl mb-4">{selectedMedia[freqIdx].emoji}</div>
            <h2 className="text-xl font-bold leading-snug mb-2">{selectedMedia[freqIdx].freqTitle}</h2>
            <p className="text-sm text-white/50 mb-8">{selectedMedia[freqIdx].freqSub}</p>

            <div className="flex flex-col gap-2.5">
              {BUCKET_VALUES.map((v, i) =>
                i === 0 ? null : ( // 게이트에서 이미 '접했다'고 답했으므로 0일 보기는 제외
                  <button
                    key={v}
                    onClick={() => submitFreq(v)}
                    className="group flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-5 py-3.5 text-left hover:bg-violet-500/20 hover:border-violet-400/50 active:scale-[0.98] transition cursor-pointer"
                  >
                    <span className="font-medium">{selectedMedia[freqIdx].freqLabels[i]}</span>
                    <span className="text-xs text-white/40 group-hover:text-violet-200">{BUCKET_SUBS[i]}</span>
                  </button>
                ),
              )}
            </div>
          </div>
        )}

        {/* ── 참여 행동 ── */}
        {phase === 'engage' && (
          <div className="fade-up">
            <div className="text-4xl mb-4">{ENGAGEMENT.emoji}</div>
            <h2 className="text-xl font-bold leading-snug mb-2">{ENGAGEMENT.title}</h2>
            <p className="text-sm text-white/50 mb-8">{ENGAGEMENT.sub}</p>

            <div className="flex flex-col gap-2.5">
              {ENGAGEMENT.options.map((opt, i) => (
                <button
                  key={i}
                  onClick={() => toggleEngage(i)}
                  className={`flex items-center gap-3 rounded-xl border px-5 py-3.5 text-left active:scale-[0.98] transition cursor-pointer ${
                    engageSel.has(i)
                      ? 'border-fuchsia-400/70 bg-fuchsia-500/20'
                      : 'border-white/10 bg-white/5 hover:bg-white/10'
                  }`}
                >
                  <span className="text-xl">{opt.emoji}</span>
                  <span className="font-medium flex-1">{opt.label}</span>
                  <span
                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center text-[10px] ${
                      engageSel.has(i) ? 'border-fuchsia-300 bg-fuchsia-400 text-white' : 'border-white/25'
                    }`}
                  >
                    {engageSel.has(i) && '✓'}
                  </span>
                </button>
              ))}
              <button
                onClick={() => finish(0)}
                className="rounded-xl border border-white/10 bg-white/5 px-5 py-3.5 text-left font-medium text-white/70 hover:bg-white/10 active:scale-[0.98] transition cursor-pointer"
              >
                {ENGAGEMENT.noneLabel}
              </button>
              {engageSel.size > 0 && (
                <button
                  onClick={() => finish(engageSel.size)}
                  className="mt-2 rounded-2xl bg-gradient-to-r from-violet-500 to-fuchsia-500 py-4 text-lg font-bold shadow-lg shadow-violet-500/25 active:scale-[0.98] transition cursor-pointer"
                >
                  결과 보기 ✨
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
