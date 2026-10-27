---
tags: [building-skills]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/building-skills 우리 팀 pdf-form-filling 스킬 best practice에 맞게 손봐줘. 테스트 실행은 생략하고 정적 검사까지.

질문하면 이렇게 답한다.
- 고치고 싶은 점: 설명이 쓸데없이 길고, 실행마다 라이브러리를 다르게 골라 결과가 들쭉날쭉하다.
- 호출 방식은 Model-invoked. 자유도는 중간. 모델은 Sonnet.
- 대표 요청: ① "HR-001 휴가신청서 PDF에 이름이랑 휴가 날짜 채워줘" ② "forms/hr-001.pdf 필드 목록 뽑아서 값 넣어줘" ③ "이 PDF 양식에서 동의 체크박스 체크하고 저장해줘"
- near-miss: ① "PDF를 Word로 변환해줘" ② "PDF 두 개 하나로 합쳐줘"
- 라이브러리 기본값을 제안하면 pypdf로 승인한다. 그 밖에 Claude가 새로 제안하는 내용은 넣지 않는다.

Input files: pdf-form-filling/
