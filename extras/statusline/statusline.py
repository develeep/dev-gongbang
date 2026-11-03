#!/usr/bin/env python3
"""Claude Code status line: dir · model · branch · plan usage · cache · cost.

Claude Code pipes the session as JSON on stdin; see the statusLine docs for the fields.
The branch and the plan usage are clickable links (OSC 8) where the terminal supports them.
"""
import json
import os
import subprocess
import sys
import time

# Set to False if a terminal prints the link escapes as text.
LINKS = True
USAGE_URL = "https://claude.ai/settings/usage"

RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
GREEN, YELLOW, RED, BLUE, MAGENTA, CYAN, GREY = (
    "\033[32m", "\033[33m", "\033[31m", "\033[34m", "\033[35m", "\033[36m", "\033[90m")
SEP = f" {GREY}│{RESET} "

data = json.load(sys.stdin)
now = time.time()


def link(text, url):
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\" if LINKS and url else text


def tone(pct):
    return RED if pct >= 90 else YELLOW if pct >= 70 else GREEN


def bar(pct, width=8):
    filled = max(0, min(width, round(pct / 100 * width)))
    return f"{tone(pct)}{'▰' * filled}{GREY}{'▱' * (width - filled)}{RESET}"


def until(epoch):
    left = int((epoch - now) // 60)
    if left <= 0:
        return ""
    d, rest = divmod(left, 1440)
    h, m = divmod(rest, 60)
    return f"{d}d{h}h" if d else f"{h}h{m:02d}m" if h else f"{m}m"


def git(cwd, *args):
    try:
        return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=1).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def repo_url(cwd, branch):
    remote = git(cwd, "remote", "get-url", "origin")
    if remote.startswith("git@"):  # git@github.com:owner/repo.git
        remote = "https://" + remote[4:].replace(":", "/", 1)
    remote = remote.removesuffix(".git")
    return f"{remote}/tree/{branch}" if remote.startswith("https://") else ""


parts = []

cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or os.getcwd()
home = os.path.expanduser("~")
parts.append(f"{BLUE}{BOLD}{'~' + cwd[len(home):] if cwd.startswith(home) else cwd}{RESET}")

model = (data.get("model") or {}).get("display_name") or "?"
# effort is absent on models without an effort parameter.
effort = (data.get("effort") or {}).get("level") or os.environ.get("CLAUDE_EFFORT")
parts.append(f"{MAGENTA}◆ {model}{RESET}" + (f" {DIM}{effort}{RESET}" if effort else ""))

branch = git(cwd, "branch", "--show-current")
if branch:
    dirty = f"{YELLOW}*{RESET}" if git(cwd, "status", "--porcelain", "-uno") else ""
    parts.append(f"{CYAN}{link('⎇ ' + branch, repo_url(cwd, branch))}{RESET}{dirty}")

# Plan usage: present only on a subscription, once a reply has reported it.
limits = data.get("rate_limits") or {}
plan = []
for label, key in (("5h", "five_hour"), ("7d", "seven_day")):
    w = limits.get(key) or {}
    pct = w.get("used_percentage")
    if pct is None:
        continue
    reset = until(w.get("resets_at") or 0)
    plan.append(f"{label} {bar(pct, 5)} {tone(pct)}{pct:.0f}%{RESET}" + (f" {DIM}↻{reset}{RESET}" if reset else ""))
if plan:
    parts.append(link("  ".join(plan), USAGE_URL))

# Prompt cache: time left before the cached prefix expires, so a long pause is a known cost.
cache = data.get("prompt_cache") or {}
if cache.get("warm") and cache.get("expires_at"):
    left = until(cache["expires_at"])
    if left:
        parts.append(f"{GREY}cache {left}{RESET}")

cost = (data.get("cost") or {}).get("total_cost_usd")
if cost:
    parts.append(f"{GREY}${cost:.2f}{RESET}")

print(SEP.join(parts))
