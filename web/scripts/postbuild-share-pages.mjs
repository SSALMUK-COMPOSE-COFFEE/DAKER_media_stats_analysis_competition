/**
 * 빌드 후 유형별 공유 페이지 생성: dist/r/<id>/index.html
 * 같은 앱이지만 OG 태그만 유형별로 치환 — 카톡/페북 크롤러는 JS를 안 돌리므로
 * 유형별 썸네일을 정적 HTML로 제공해야 한다. 서버 코드 불필요.
 *
 * OG 이미지는 절대 URL이 필요하므로 배포 시:
 *   SITE_URL=https://내도메인 npm run build
 * SITE_URL 미지정 시 호스트 상대 경로(/og/N.png)로 생성 (대부분의 크롤러는 해석 가능).
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const dist = join(root, 'dist')
const SITE = (process.env.SITE_URL ?? '').replace(/\/$/, '')

// 유형 이름·비율·태그라인의 단일 소스: 앱과 동일한 quiz_model.json / taglines.json
const model = JSON.parse(readFileSync(join(root, 'src', 'quiz_model.json'), 'utf-8'))
const taglines = JSON.parse(readFileSync(join(root, 'src', 'data', 'taglines.json'), 'utf-8'))
const TYPES = Object.fromEntries(
  Object.entries(model.classes).map(([id, c]) => [
    id,
    { name: c.name, pct: Math.round(c.pct * 10) / 10, tag: taglines[id] },
  ]),
)

const base = readFileSync(join(dist, 'index.html'), 'utf-8')

const setMeta = (html, prop, content) => {
  const re = new RegExp(`(<meta property="${prop}" content=")[^"]*(")`)
  return re.test(html)
    ? html.replace(re, `$1${content}$2`)
    : html.replace('</head>', `  <meta property="${prop}" content="${content}" />\n  </head>`)
}

// 기본 페이지에도 default OG 이미지 주입
let indexHtml = base
indexHtml = setMeta(indexHtml, 'og:image', `${SITE}/og/default.png`)
indexHtml = setMeta(indexHtml, 'og:image:width', '1200')
indexHtml = setMeta(indexHtml, 'og:image:height', '630')
writeFileSync(join(dist, 'index.html'), indexHtml)

for (const [id, t] of Object.entries(TYPES)) {
  let html = base
  html = html.replace(/<title>[^<]*<\/title>/, `<title>나의 뉴스 DNA: ${t.name} — 뉴스 DNA 테스트</title>`)
  html = setMeta(html, 'og:title', `나의 뉴스 DNA는 ${t.name} (국민의 ${t.pct.toFixed(1)}%)`)
  html = setMeta(html, 'og:description', `“${t.tag}” — 너는 어떤 유형이야? 국가 통계 6,000명 데이터로 만든 1분 테스트`)
  html = setMeta(html, 'og:image', `${SITE}/og/${id}.png`)
  html = setMeta(html, 'og:image:width', '1200')
  html = setMeta(html, 'og:image:height', '630')
  const dir = join(dist, 'r', id)
  mkdirSync(dir, { recursive: true })
  writeFileSync(join(dir, 'index.html'), html)
}
console.log(`share pages: dist/r/{0..5}/index.html (SITE_URL=${SITE || '(relative)'})`)
