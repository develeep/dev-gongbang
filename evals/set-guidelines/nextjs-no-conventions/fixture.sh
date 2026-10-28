mkdir -p app
cat > package.json <<'JSON'
{
  "name": "shop-web",
  "private": true,
  "scripts": { "dev": "next dev", "build": "next build" },
  "dependencies": { "next": "15.1.0", "react": "19.0.0", "react-dom": "19.0.0" },
  "devDependencies": { "typescript": "5.6.2", "@types/react": "19.0.0", "@types/node": "22.0.0" }
}
JSON
cat > tsconfig.json <<'JSON'
{
  "compilerOptions": { "target": "ES2022", "lib": ["dom", "esnext"], "strict": true, "module": "esnext", "moduleResolution": "bundler", "jsx": "preserve" },
  "include": ["**/*.ts", "**/*.tsx"]
}
JSON
cat > app/layout.tsx <<'TSX'
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="ko"><body>{children}</body></html>
}
TSX
cat > app/page.tsx <<'TSX'
async function getProducts() {
  const res = await fetch('https://api.example.com/products')
  return res.json()
}

export default async function Page() {
  const products = await getProducts()
  return <ul>{products.map((p: any) => <li key={p.id}>{p.name}</li>)}</ul>
}
TSX
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
