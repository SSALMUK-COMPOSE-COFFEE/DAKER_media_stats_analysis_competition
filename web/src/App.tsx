import { useEffect, useState } from 'react'
import Landing from './components/Landing'
import Quiz from './components/Quiz'
import Result from './components/Result'
import { classify, type ClassifyResult, type TypeId } from './model/classify'
import { TYPES } from './data/types'

type Screen = 'landing' | 'quiz' | 'result'

/** 공유 링크로 진입한 결과 열람 지원: /r/<typeId>/ 경로 또는 ?r=<typeId> 쿼리 */
function resultFromUrl(): ClassifyResult | null {
  const path = window.location.pathname.match(/\/r\/(\d)\/?$/)
  const r = path?.[1] ?? new URLSearchParams(window.location.search).get('r')
  if (r === null || r === undefined) return null
  const id = Number(r)
  if (!(id in TYPES)) return null
  return { main: id as TypeId, sub: TYPES[id as TypeId].match.id, answers: [] }
}

export default function App() {
  const [screen, setScreen] = useState<Screen>('landing')
  const [result, setResult] = useState<ClassifyResult | null>(null)

  useEffect(() => {
    const shared = resultFromUrl()
    if (shared) {
      setResult(shared)
      setScreen('result')
    }
  }, [])

  const handleFinish = (answers: number[]) => {
    setResult(classify(answers))
    setScreen('result')
    window.scrollTo(0, 0)
  }

  const restart = () => {
    history.replaceState(null, '', import.meta.env.BASE_URL)
    setResult(null)
    setScreen('quiz')
    window.scrollTo(0, 0)
  }

  return (
    <div className="min-h-dvh text-white">
      {screen === 'landing' && <Landing onStart={() => setScreen('quiz')} />}
      {screen === 'quiz' && <Quiz onFinish={handleFinish} />}
      {screen === 'result' && result && <Result result={result} onRestart={restart} />}
    </div>
  )
}
