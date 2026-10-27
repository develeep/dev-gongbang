mkdir -p .scratch/invoice-pdf src/billing
cat > src/billing/invoice.py <<'PY'
def render_invoice(invoice):
    return f"<h1>Invoice {invoice.number}</h1><p>{invoice.total}</p>"
PY
cat > .scratch/invoice-pdf/brief.md <<'MD'
# 청구서를 PDF로 내려받을 수 있다

- 기준 커밋: `7777777`
- 작성일: 2026-10-25

## 합의한 작업
- 남은 일:
  - [ ] 청구서 화면의 PDF 내려받기 버튼
  - [ ] PDF 파일 이름을 `invoice-<청구서 번호>.pdf`로 지정
  - [ ] 청구서 목록에서 여러 건을 골라 ZIP으로 내려받기

## 작업 경계
- 바꾸지 않는 범위: `render_invoice`의 HTML 출력
MD
printf '.scratch/\n' > .gitignore
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
