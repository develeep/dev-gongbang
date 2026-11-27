# 단일 루프 접기 측정 기록

[접기 계획](./2026-11-25-fold-to-single-loop.md)의 기준선(`f991a4d`)과 최종을 Claude Code 2.1.332에서 비교했습니다. 양쪽에 동일한 e2e 및 run-ticket 사례와 채점기를 두고, 임시 worktree의 매니페스트에만 `./skills/in-progress/`를 추가했습니다. 기본 `gongbang` 매니페스트는 이 스킬을 담지 않으므로 그대로 돌리면 다른 동작을 잽니다.

이 문서의 커밋 해시(`f991a4d`, `8d7d490`, `d690377`)는 PR #40의 이력을 다시 쓰기 전 커밋입니다. 그 이력은 `backup/202611-fold-to-single-loop-pre-rewrite` 브랜치에 남아 있습니다.

## 실제 결과 (2026-11-26, 3차)

기준선 `f991a4d`와 최종 `8d7d490`(P4·P5, 냉독 채점·코드 지문·E3 연결 수정 포함)을 사례마다 번갈아 각 1회 돌렸습니다. 1·2차 결과는 이 표가 대체합니다. 38개 실행 모두 도구 오류 없이 채점까지 갔고, E3는 E2 결과를 받아 실제로 실행됐습니다. 실행당 1회라 사례별 차이에는 잡음이 큽니다. eval 러너는 `gongbang-mods`를 불러오지 않으므로 쓰기 차단 훅은 이 측정에서 꺼져 있고, 훅의 차단은 가짜 모델로 돌린 실제 `claude`·`omp` 실행으로 따로 확인했습니다.

`rule-existing-tests-untouched-bash`는 heredoc 본문에 테스트 파일 이름이 나오기만 해도 위반으로 잡았습니다(`cat > $TMPDIR/... <<'EOF'` 뒤 본문). 정규식이 JSON 안의 `\n`을 넘어가지 않게 고치고, 남긴 trace로 두 arm을 다시 채점한 값을 아래에 적었습니다. 고친 뒤 셸 위반은 양쪽 모두 0건입니다.

- **합계:** 통과 채점기 기준선 208/280(74%), 최종 232/280(83%). e2e 12사례 191/256 → 210/256, run-ticket 7사례 17/24 → 22/24. 비용 $15.43 대 $17.53, 시간 2847초 대 3009초.
- **기존 테스트 편집:** 기준선은 `e2e-resume-mid-5`에서 Edit로 기존 테스트를 고쳤고, 최종은 0건입니다.
- **냉독:** 초안을 쓰는 세 사례에서 양쪽 모두 냉독 독자를 3명 이상 띄웠습니다.
- **run-ticket:** `prior-artifact`, `unfinished-changes`는 양쪽 모두 2/2입니다. `multi-sequential`은 2/5 → 5/5, `mark-done`은 2/3 → 3/3입니다.
- **남은 실패:** 최종에서도 `rule-cross-review-before-record`가 6개 사례에서, `e2e-pr`·`e2e-spec-to-pr`의 PR 단계 채점기(`pr-stage-read`, `pr-created-once` 등)가 양쪽 모두 실패합니다. `e2e-spec-three-tickets`의 `set-ticket-loaded`·`three-tickets-shape`도 양쪽 모두 실패합니다. 접기 전후에 같이 나는 실패라 이번 변경의 회귀는 아닙니다.
- **트리거:** 변경 전후 각 9개 × 3회, 27/27 통과했습니다.

| 사례 | 기준선 | 최종 |
|---|---:|---:|
| `e2e-request-single` | 15/21 | 17/21 |
| `e2e-planted-bug` | 19/21 | 19/21 |
| `e2e-no-cross-reviewer` | 14/22 | 19/22 |
| `e2e-security` | 16/21 | 17/21 |
| `e2e-ambiguous-framing` | 16/20 | 15/20 |
| `e2e-pr` | 11/21 | 13/21 |
| `e2e-resume-mid-5` | 18/22 | 20/22 |
| `e2e-unsatisfiable` | 17/18 | 17/18 |
| `e2e-ui-criterion` | 17/20 | 20/20 |
| `e2e-spec-three-tickets` | 17/23 | 18/23 |
| `e2e-six-tickets` | 21/26 | 22/26 |
| `e2e-spec-to-pr` | 10/21 | 13/21 |
| run-ticket 7개 | 17/24 | 22/24 |

### 결정 9 후속

강화 P4(쓰기 전 차단)와 P5의 보호 파일 수락 검사를 `d690377`에 넣었습니다. 가짜 모델 실행에서 보호 파일 직접 편집은 거부됐고, 셸 편집은 `verify`가 수락을 거부했습니다. 대소문자 별칭, 하드 링크, Windows 경로는 확인하지 않았습니다.

### 접기 계획 기준의 판정과 남은 일 (2026-11-27)

[접기 계획](./2026-11-25-fold-to-single-loop.md) 5절 "유지 판단 규칙" 1번에 따르면 이 측정의 최종은 통과가 아닙니다. 최종에서도 "어기면 안 되는 규칙"인 `rule-cross-review-before-record`가 6개 사례에서 실패했습니다. 기준선에서도 실패했으므로 회귀는 아니지만, 결정 6(교차 리뷰를 건너뛰는 경로를 없앰)의 목표가 측정으로 확인되지 않았습니다.

- **원인:** 확인하지 못했습니다. eval 트레이스가 실행 뒤 지워져 실패한 실행 기록을 읽을 수 없습니다. 후보 **(추론)**: 채점기는 같은 회사 대체에 수행한 모델 이름을 요구하는데, 스킬은 모델을 확인할 수 없으면 "수행 모델 확인 불가"를 허용합니다. 서브에이전트를 모델을 정하지 않고 띄우면 이 경우가 됩니다. 채점 기준은 고치지 않고(5절 4번), run-ticket 5단계에 "띄울 때 모델을 정할 수 있으면 정해서 띄운다"를 더했습니다. 이 수정은 아직 측정하지 않았습니다.
- **사례별 하락:** `e2e-ambiguous-framing`이 16에서 15로 내려갔습니다. 5절 2번은 실행 기록을 읽으라고 하지만, 트레이스가 남지 않아 읽지 못했습니다. 다음 측정에서 `--keep-temp`로 트레이스를 남깁니다.
- **남은 측정:** 결정 10대로 줄인 것을 되돌려, 접는 단계마다 동작 사례 67개와 e2e 사례를 3회씩 돌리는 비교가 남았습니다. 선택 경로의 E2-P·E8-P와, omp에서 E1·E2·E4를 손으로 3회씩 돌리는 측정도 하지 않았습니다.

## 다시 돌리는 방법

1. Bash를 안전하게 격리할 수 있는 환경을 씁니다. 기준선과 최종을 각각 detached worktree에 만들고, 기준선의 run-ticket 및 e2e 사례를 최종 사례와 맞춥니다. 두 임시 매니페스트의 `skills` 배열에 `./skills/in-progress/`를 추가합니다. 배포 매니페스트에는 이 변경을 넣지 않습니다. Python은 샌드박스 안에서 동작하는 경로를 씁니다.
2. 아래 예시처럼 사례를 지정하고 각 기록을 별도 JSON으로 저장합니다. `--case`를 여러 번 주면 마지막 값만 남습니다. 트리거는 `--eval-dir evals-trigger/run-ticket`으로 돌리고 Bash를 열지 않습니다.

```bash
claude plugin eval . --scaffold --allow-tools Bash Write Edit WebSearch WebFetch \
  --ablation none --no-publish --trust-plugin --runs 1 --keep-temp \
  --case 'e2e-ambiguous-framing' --json result.json
claude plugin eval . --scaffold --allow-tools Bash Write Edit WebSearch WebFetch \
  --ablation none --no-publish --trust-plugin --runs 1 \
  --eval-dir evals/run-ticket --json run-ticket.json
```

3. `e2e-spec-to-pr`는 `e2e-spec-three-tickets`가 결과를 남긴 경우에만 따로 돌립니다. 후자의 `--keep-temp` 작업 트리 경로를 `E2E_E2_WORKTREE`로 넘깁니다. 중단된 E2의 빈 작업 트리나 독립 E3 점수로 이 결과를 대신하지 않습니다.
4. `cases[].arms.with[]`의 `error`, 채점기별 판정, 턴·비용·시간을 사례별로 비교합니다. E4·E5·E8·E10의 `.git/e2e-judge/` 판정은 별도로 확인합니다. 원시 실행 디렉터리에는 에이전트가 만든 파일이 있으므로 그 안에서 호스트 도구를 직접 실행하지 말고, 검토한 판정 스크립트만 격리된 환경에서 실행합니다.
