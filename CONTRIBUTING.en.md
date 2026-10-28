<p align="right"><a href="./CONTRIBUTING.md">한국어</a> · <b>English</b></p>

# Contributing

This guide explains how to report bugs, fix skills, and propose new skills for dev-gongbang. Issues and PRs are welcome in Korean or English.

**Contents**: [Opening an issue](#opening-an-issue) · [Development setup](#development-setup) · [Changing and adding skills](#changing-and-adding-skills) · [Running checks](#running-checks) · [Commit messages](#commit-messages) · [Sending a PR](#sending-a-pr) · [Code of conduct](#code-of-conduct)

## Opening an issue

Choose a form at [New issue](https://github.com/develeep/dev-gongbang/issues/new/choose).

- **Bug report**: a skill behaves differently from its docs, or a script fails
- **Skill proposal**: you want to propose a new skill or a new behavior for an existing skill

Do not report security problems in public issues. Report them privately as described in the [security policy](SECURITY.en.md).

## Development setup

| Tool | Used by |
|---|---|
| Python 3.9 or later, PyYAML | `scripts/validate.py`, `scripts/test_validate.py` |
| Claude Code CLI | `scripts/check.py` (runs `claude plugin validate`), running skills, evals |

Fork and clone the repository, then install PyYAML.

```bash
git clone https://github.com/<your-account>/dev-gongbang.git
cd dev-gongbang
pip install pyyaml
```

## Changing and adding skills

The rules for adding, moving, or renaming a skill are in [.claude/CLAUDE.md](.claude/CLAUDE.md). That file covers buckets, invocation types, usage docs, and commit rules. It is written in Korean. When you work in this repository with Claude Code, Claude Code reads the file and follows its rules.

Commonly missed steps:

- When you change a skill, also update its usage page `docs/skills/<skill-name>.md` and the English page `docs/en/skills/<skill-name>.md`.
- If the change should reach users, bump `version` in `.claude-plugin/plugin.json`. Installed plugins update only when the version changes.

To try a modified skill in your own Claude Code, see the [customization guide](docs/en/customization.md).

## Running checks

Run the repository checks before you send a PR.

```bash
python3 scripts/check.py
```

If you changed `scripts/validate.py`, also run the validator's own tests.

```bash
python3 scripts/test_validate.py
```

When you open a PR, GitHub Actions runs `test_validate.py` and `validate.py` automatically. CI does not run `claude plugin validate`, so check it locally with `check.py`.

If you changed how a skill behaves, run the evals too. Evals call the model for real.

```bash
claude plugin eval . --scaffold --allow-tools Edit WebSearch WebFetch --no-publish
claude plugin eval . --eval-dir evals-trigger --ablation none --no-publish
```

## Commit messages

Write the subject as `<type>: <summary>`, then a blank line, then the changes as a `- ` list. Korean and English are both fine.

```
fix: include rule files without paths in check-guidelines

- Apply rule files without paths to every target file
```

The type is one of `feature`, `fix`, `docs`, `refactor`, `eval`, `chore`. Keep one type per commit. The meaning of each type and the detailed format are in the "커밋" (Commits) section of [.claude/CLAUDE.md](.claude/CLAUDE.md).

## Sending a PR

1. Create a branch from `master`.
2. Fill in the checklist that appears when you open the PR.
3. CI checks must pass before the PR can be merged.
4. A maintainer reviews the PR and merges it with a merge commit. Your commit messages stay in the history, so tidy your commits before you send the PR.

## Code of conduct

Everyone who takes part in this project follows the [code of conduct](CODE_OF_CONDUCT.en.md).
