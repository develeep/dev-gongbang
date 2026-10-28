mkdir -p app lib .claude/rules
cat > package.json <<'JSON'
{
  "name": "shop-web",
  "private": true,
  "scripts": { "dev": "next dev", "build": "next build", "lint": "eslint ." },
  "dependencies": { "next": "15.1.0", "react": "19.0.0", "react-dom": "19.0.0" },
  "devDependencies": { "typescript": "5.6.2", "eslint": "9.17.0", "typescript-eslint": "8.18.0" }
}
JSON
printf 'node_modules/\n' > .gitignore
cat > eslint.config.mjs <<'JS'
import tseslint from 'typescript-eslint'

export default [
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: { parser: tseslint.parser, parserOptions: { ecmaFeatures: { jsx: true } } },
    rules: { eqeqeq: 'error' },
  },
]
JS
cat > CLAUDE.md <<'MD'
# shop-web

## 규칙

- 함수 하나는 한 가지 일만 한다.
MD
cat > .claude/rules/typescript.md <<'MD'
---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript

- `any` 타입을 쓰지 않는다.
- React 컴포넌트 이름은 PascalCase로 짓는다.
MD
cat > .claude/rules/styles.md <<'MD'
---
paths:
  - "**/*.css"
---

# 스타일

- 색상 값은 CSS 변수로 쓴다.
MD
cat > app/globals.css <<'CSS'
:root { --brand: #e11d48; }
body { color: var(--brand); }
CSS
cat > app/layout.tsx <<'TSX'
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="ko"><body>{children}</body></html>
}
TSX
cat > app/page.tsx <<'TSX'
export default function Page() {
  return <main>상품 목록</main>
}
TSX
cat > lib/legacy.ts <<'TS'
export function parse(input: any) {
  return JSON.parse(input)
}
TS
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
# 커밋하지 않은 변경: 수정한 파일 하나, 새 파일 하나
cat > app/page.tsx <<'TSX'
function productBadge({ label }: { label: string }) {
  return <span style={{ color: '#e11d48' }}>{label}</span>
}

export default function Page() {
  const Badge = productBadge
  return <main><Badge label="NEW" /></main>
}
TSX
cat > lib/price.ts <<'TS'
export function formatPrice(value: any): string {
  if (value == null) return '-'
  return `${Number(value).toLocaleString('ko-KR')}원`
}

export async function loadPriceLabel(id: string): Promise<string> {
  const res = await fetch(`https://api.example.com/products/${id}`)
  const data = await res.json()
  return formatPrice(data.price)
}
TS
# ESLint만 설치한다. next까지 받으면 오래 걸리고 검사에는 필요 없다.
tmp=$(mktemp -d)
(cd "$tmp" && npm init -y >/dev/null && npm install --silent --no-audit --no-fund eslint@9.17.0 typescript-eslint@8.18.0 typescript@5.6.2)
mv "$tmp/node_modules" . && rm -rf "$tmp"
