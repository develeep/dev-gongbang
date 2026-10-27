---
name: pdf-form-filling
description: PDF 양식 채우기. 당신이 PDF 양식을 채울 때 도와드립니다.
---

# PDF 양식 채우기

PDF(Portable Document Format)는 Adobe가 만든 문서 형식으로, 어떤 기기에서도 같은 모양으로 보이게 해 줍니다. PDF 양식(AcroForm)은 사용자가 값을 입력할 수 있는 필드를 가진 PDF입니다. 파이썬은 널리 쓰이는 프로그래밍 언어입니다.

## 라이브러리

pypdf, pdfplumber, PyMuPDF, pdfrw, reportlab 중 아무거나 써도 됩니다. 상황에 맞게 고르세요.

2025년 6월 이전에는 PyPDF2를 썼지만 지금은 pypdf를 씁니다.

## 절차

1. 필드 목록을 뽑는다: `python scripts\list_fields.py input.pdf`
2. 값을 채운다.
3. 저장한다.

우리 회사 양식(HR-001 휴가신청서)은 체크박스 값이 `/Yes`가 아니라 `/On`이어야 체크된다. 날짜 필드는 `YYYY.MM.DD` 형식만 받는다.

자세한 건 [docs/guide.md](docs/guide.md) 참고.
