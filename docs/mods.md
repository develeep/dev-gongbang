<p align="right"><b>한국어</b> · <a href="./en/mods.md">English</a></p>

[README](../README.md) › [문서](README.md) › Mod

# Mod

`gongbang-mods`는 Claude Code 터미널 화면을 꾸미는 mod 묶음입니다. mod는 Claude Code의 화면과 동작에 hook을 거는 플러그인입니다. 이 문서를 읽으면 `gongbang-mods`가 화면을 어떻게 바꾸는지, 설치하고 끄는 방법, 함께 쓰면 좋은 외부 mod, 따로 설치하는 상태줄 스크립트를 알 수 있습니다.

## 목차

- [설치](#설치)
- [바뀌는 화면](#바뀌는-화면)
- [알아 둘 점](#알아-둘-점)
- [끄기와 업데이트](#끄기와-업데이트)
- [함께 쓰면 좋은 외부 mod](#함께-쓰면-좋은-외부-mod)
- [상태줄](#상태줄)
- [다른 컴퓨터에 똑같이 설정하기](#다른-컴퓨터에-똑같이-설정하기)
- [출처](#출처)

## 설치

Claude Code 2.1.287 이상이 필요합니다. 마켓플레이스를 추가하고 `gongbang-mods`를 설치한 뒤 Claude Code를 다시 시작하세요.

```bash
claude plugin marketplace add develeep/dev-gongbang
claude plugin install gongbang-mods@dev-gongbang
```

`gongbang` 스킬 플러그인과 따로 설치하고 따로 끌 수 있습니다.

## 바뀌는 화면

### 도구 호출 한 줄 접기

도구 호출과 그 결과를 `✓ Bash git status`처럼 한 줄로 접습니다. 맨 앞 표시는 상태를 뜻합니다.

| 표시 | 뜻 |
|---|---|
| `…` (노랑) | 실행 중 |
| `✓` (초록) | 성공 |
| `✗` (빨강) | 오류 |
| `⏹` (노랑) | 중단 |

결과 블록은 숨깁니다. `ctrl+o`나 `--verbose`로 열면 원래대로 모두 보입니다. `Read 3 files`처럼 엔진이 원래 묶어 보여 주는 줄은 그대로 둡니다.

### 카드형 메시지와 마크다운

내가 보낸 메시지는 `● You` 제목이 붙은 둥근 테두리 카드에, Claude 답변은 `◆ Claude` 제목이 붙은 카드에 담습니다. 색은 테마의 `suggestion`(내 메시지)과 `claude`(답변)를 따르므로 라이트·다크 테마에 맞춰 바뀝니다.

답변 카드 안의 마크다운 중 일부는 직접 그립니다.

- 제목: 단계별로 `█`(밑줄), `▌`, `▸` 표시를 붙여 굵게 그립니다.
- 코드 블록: 연한 테두리 상자에 넣고 언어 이름을 위에 적습니다.
- 인용문: 왼쪽에 `┃` 세로줄을 두고 기울임꼴로 그립니다.
- 구분선: 카드 폭에 맞춘 가는 선으로 그립니다.

표, 목록, 체크박스, 일반 문단은 엔진이 원래대로 그립니다. 백그라운드 작업 알림과 다른 에이전트가 보낸 메시지도 원래 모양으로 둡니다.

### Session 패널

우측 패널 하나에 세션 목표와 컨텍스트 사용량을 함께 보여 줍니다.

- **Goal**: 세션 목표, 지금 하는 일(`now`), 다음 할 일(`next`), 내 답을 기다리는 일(`waiting on you`)
- **Context**: 사용률, 사용한 토큰과 자동 압축 지점, 항목별 색 막대, 항목별 토큰 수

두 값 모두 첫 턴이 끝난 뒤에 채워집니다.

| 명령 | 하는 일 |
|---|---|
| `/session-pane` | Session 패널을 엽니다 |
| `/where` | 지금까지의 세션을 몇 줄로 요약합니다 |

## 알아 둘 점

- **Claude 사용량을 씁니다**: Session 패널의 Goal은 턴이 끝날 때마다 Haiku를 한 번 호출해 만듭니다. `/where`도 Haiku를 호출합니다.
- **패널 자리**: 세션을 시작할 때 터미널이 충분히 넓으면 패널이 우측에 자동으로 열립니다. 좁으면 열리지 않으니 창을 넓히고 `/session-pane`을 입력하세요. 우측에 붙는 배치는 fullscreen 화면에서만 됩니다.
- **화면을 다시 그리는 다른 mod와 겹칩니다**: 대화 메시지나 도구 호출 줄을 다시 그리는 mod를 함께 쓰면 어느 한쪽 모양만 보일 수 있습니다.
- **Claude Code 화면에서만 보입니다**: 다른 앱이 SDK로 Claude Code를 실행하는 화면에서는 hook만 실행되고 그리는 부분은 보이지 않습니다.

## 끄기와 업데이트

```bash
claude plugin disable gongbang-mods@dev-gongbang   # 끄기
claude plugin enable gongbang-mods@dev-gongbang    # 다시 켜기
claude plugin marketplace update dev-gongbang
claude plugin update gongbang-mods@dev-gongbang    # 업데이트
```

끄거나 업데이트한 뒤에는 Claude Code를 다시 시작하거나 `/reload-plugins`를 입력하세요.

## 함께 쓰면 좋은 외부 mod

다른 사람이 만든 mod입니다. 이 저장소에 포함하지 않았으니 각 저장소에서 설치하세요. 설치하기 전에 코드를 읽어 보세요.

[hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods):

- **mission-control**: 서브에이전트, 도구 호출, 수정 중인 파일을 실시간 패널로 보여 줍니다. `/mission`으로 엽니다. 턴마다 Haiku를 한 번 호출합니다.
- **next-steps**: 턴이 끝나면 다음에 보낼 만한 프롬프트 2~3개를 제안합니다. 빈 입력창에서 숫자 키로 고릅니다. 제안을 한국어로 받으려면 `language` 옵션을 `Korean`으로 설정하세요.
- **blast-radius**: `rm -r` 같은 위험한 Bash 명령을 붙잡고, 지워질 파일을 보여 준 뒤 실행할지 묻습니다. 기본으로 60초 동안 답이 없으면 명령을 취소합니다.
- **agent-radar**: 실행 중인 서브에이전트와 백그라운드 셸마다 한 줄씩 상태를 보여 줍니다.

```bash
claude plugin marketplace add hamzafer/claude-code-mods
claude plugin install mission-control@claude-code-mods
claude plugin install next-steps@claude-code-mods
claude plugin install blast-radius@claude-code-mods
claude plugin install agent-radar@claude-code-mods
echo '{"language":"Korean"}' | claude plugin configure next-steps@claude-code-mods --values-stdin
```

`next-steps`가 제안 목록을 보여 주는 동안에는 Session 패널의 `next` 항목을 숨깁니다. 같은 내용이 두 번 나오지 않게 하려는 것입니다.

[YeonwooSung/my-claude-code-mods](https://github.com/YeonwooSung/my-claude-code-mods):

- **loop-detective**: 같은 Bash 명령이 연속으로 같은 이유로 실패하면 알리고 사례로 기록합니다. `/loop-report`, `/loop-pane`으로 봅니다.
- **context-inspector**: 컨텍스트에서 낭비되는 부분을 분석합니다. 같은 파일을 다시 읽은 경우, 비슷한 출력이 반복된 경우 등을 찾습니다. `/context-inspect`, `/context-pane`으로 봅니다.

```bash
claude plugin marketplace add YeonwooSung/my-claude-code-mods
claude plugin install loop-detective@my-claude-code-mods
claude plugin install context-inspector@my-claude-code-mods
```

hamzafer 저장소의 `context-bar`와 `where-am-i`는 따로 설치하지 마세요. Session 패널과 같은 정보를 입력창 위에 한 번 더 보여 줍니다.

## 상태줄

`extras/statusline/statusline.py`는 입력창 아래 상태줄을 꾸미는 스크립트입니다. 플러그인이 사용자의 `statusLine` 설정을 바꿀 수 없어서 `gongbang-mods`에 넣지 않고 따로 둡니다.

```
~/dev-gongbang │ ◆ Opus 5.5 medium │ ⎇ master* │ 5h ▱▱▱▱▱ 5% ↻3h11m  7d ▰▰▰▰▱ 72% ↻2d7h │ cache 39m │ $5.79
```

| 항목 | 뜻 |
|---|---|
| `~/dev-gongbang` | 작업 폴더 |
| `◆ Opus 5.5 medium` | 모델과 effort. effort를 지원하지 않는 모델에서는 effort가 빠집니다 |
| `⎇ master*` | git 브랜치. `*`는 커밋하지 않은 변경이 있다는 뜻입니다. 누르면 GitHub의 브랜치 페이지가 열립니다 |
| `5h`, `7d` | 요금제의 5시간·주간 한도 사용률과 초기화까지 남은 시간. 누르면 claude.ai 사용량 페이지가 열립니다. 구독 요금제에서 첫 응답을 받은 뒤에 나옵니다 |
| `cache 39m` | 프롬프트 캐시가 만료되기까지 남은 시간. 이보다 오래 쉬면 다음 요청에서 캐시를 다시 만듭니다 |
| `$5.79` | 세션 비용 |

사용률은 70% 이상이면 노랑, 90% 이상이면 빨강으로 바뀝니다.

### 설치

Python 3와 git이 필요합니다. 저장소를 받은 폴더에서 스크립트를 연결하고, `~/.claude/settings.json`에 `statusLine`을 넣으세요.

```bash
ln -s "$PWD/extras/statusline/statusline.py" ~/.claude/statusline.py
```

```json
{
  "statusLine": { "type": "command", "command": "python3 ~/.claude/statusline.py" }
}
```

링크(`ln -s`) 대신 복사(`cp`)해도 됩니다. 링크로 두면 저장소를 `git pull`할 때 상태줄도 함께 바뀌고, 복사하면 직접 고친 내용이 그대로 남습니다.

### 알아 둘 점

- 브랜치와 사용량 링크는 OSC 8을 지원하는 터미널에서만 눌립니다. 상태줄에 `]8;;https://…` 같은 글자가 보이면 스크립트의 `LINKS = True`를 `False`로 바꾸세요.
- 상태줄은 Claude Code가 상태를 갱신할 때 다시 그려집니다. 남은 시간은 그때 계산한 값입니다.

## 다른 컴퓨터에 똑같이 설정하기

`extras/setup.sh`는 이 문서의 mod 환경을 한 번에 설정합니다. 저장소를 받은 뒤 실행하고 Claude Code를 다시 시작하세요.

```bash
git clone https://github.com/develeep/dev-gongbang && cd dev-gongbang
extras/setup.sh
```

스크립트가 하는 일은 다음과 같습니다. 이미 끝난 단계는 건너뛰므로 여러 번 실행해도 됩니다.

- marketplace 4개를 추가하고 `gongbang-mods`와 [외부 mod](#함께-쓰면-좋은-외부-mod) 7개를 설치합니다.
- `next-steps`의 제안 언어를 한국어로 설정합니다.
- 상태줄 스크립트를 `~/.claude/statusline.py`로 연결합니다.
- `~/.claude/settings.json`에 `"tui": "fullscreen"`과 `statusLine`을 넣습니다. 바꾸기 전 파일은 `settings.json.bak`으로 남깁니다. 패널은 fullscreen 화면에서만 우측에 붙습니다.

지금 쓰는 설정을 건드리지 않고 먼저 시험하려면 빈 폴더를 설정 폴더로 지정하세요. 설치 결과는 `CLAUDE_CONFIG_DIR=<폴더> claude plugin list`로 확인합니다.

```bash
CLAUDE_CONFIG_DIR="$HOME/.cache/claude-test" extras/setup.sh
```

터미널 앱, 글꼴, Chrome처럼 컴퓨터마다 다른 것은 스크립트가 설정하지 않습니다.

## 출처

Session 패널은 [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods)의 `context-bar`와 `where-am-i`를 고쳐 만들었습니다. 입력창 위에 그리던 내용을 우측 패널 하나로 옮겼습니다. 원본은 MIT 라이선스이고, 라이선스 전문은 `mods/gongbang-mods/hooks/session/LICENSE`에 있습니다.

---

[← 문서 목록](README.md)
