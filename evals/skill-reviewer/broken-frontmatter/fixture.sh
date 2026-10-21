mkdir -p .claude-plugin skills/engineering/good skills/engineering/typo evals/good
echo '{"name": "t", "skills": ["./skills/engineering/good", "./skills/engineering/typo"]}' > .claude-plugin/plugin.json
printf '## User-invoked\n- [good](skills/engineering/good/SKILL.md)\n- [typo](skills/engineering/typo/SKILL.md)\n' > README.md
printf '## User-invoked\n- [good](./good/SKILL.md)\n- [typo](./typo/SKILL.md)\n' > skills/engineering/README.md
printf -- '---\nname: good\ndescription: 회의록을 결정 사항과 할 일로 요약한다.\ndisable-model-invocation: true\n---\n\n# Good\n\n회의록을 읽고 결정 사항과 할 일을 표로 정리한다.\n' > skills/engineering/good/SKILL.md
printf -- '---\nname: typo\ndescription: 변경 로그를 정리한다. 변경 로그 정리해줘 요청에 사용한다.\ndisable-model-invokation: true\n---\n\n# Typo\n\n[규칙](rules.md)을 따른다.\n' > skills/engineering/typo/SKILL.md
echo '{}' > evals/good/case.yaml
mkdir -p skills/engineering/broken
printf -- '---\nname: broken\ndescription: [닫히지 않은 괄호\ndisable-model-invocation: true\n---\n\n# Broken\n' > skills/engineering/broken/SKILL.md
