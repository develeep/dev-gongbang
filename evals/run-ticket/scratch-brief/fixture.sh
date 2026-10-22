mkdir -p docs/agents .scratch/old-search/issues .scratch/order-export/brief src
cat > docs/agents/issue-tracker.md <<'MD'
# Issue tracker: Local Markdown
- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Tickets: `.scratch/<feature-slug>/issues/<NN>-<slug>.md`
MD
cat > .scratch/old-search/spec.md <<'MD'
# Search by customer name
MD
cat > .scratch/old-search/issues/01-search-box.md <<'MD'
# 01: Search box
Status: ready-for-agent
MD
cat > .scratch/order-export/brief.md <<'MD'
# 관리자가 주문 목록을 CSV로 내려받을 수 있다

- 기준 커밋: `a1b2c3d`
- 작성일: 2026-10-20

## 티켓
- [x] [01: CSV 내보내기 함수](./brief/01-csv-export.md)
- [ ] [02: 합계 열 추가](./brief/02-total-column.md)
MD
cat > .scratch/order-export/brief/01-csv-export.md <<'MD'
# 01: CSV 내보내기 함수

- 부모: [brief](../brief.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: done

## 만들 것
주문 목록을 id,customer 열의 CSV 문자열로 돌려준다.
MD
cat > .scratch/order-export/brief/02-total-column.md <<'MD'
# 02: 합계 열 추가

- 부모: [brief](../brief.md)
- 막힘 관계: 01: CSV 내보내기 함수
- 상태: ready-for-agent

## 만들 것
CSV에 total 열을 마지막 열로 추가한다.

## 완료 기준
- [ ] `python3 -c "from src.export import to_csv; print(to_csv([{'id':1,'customer':'a','total':3}]))"`의 첫 줄이 `id,customer,total`
MD
cat > src/export.py <<'PY'
def to_csv(rows):
    lines = ["id,customer"] + [f"{r['id']},{r['customer']}" for r in rows]
    return "\n".join(lines)
PY
touch src/__init__.py
printf '.scratch/\n' > .gitignore
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
