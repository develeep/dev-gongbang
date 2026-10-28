<p align="right"><a href="./SECURITY.md">한국어</a> · <b>English</b></p>

# Security policy

This page explains how to report a security problem in dev-gongbang privately.

## What to report

Scripts bundled in skills (`skills/**/scripts/`) and repository scripts (`scripts/`) run on the user's computer. Please report problems such as these:

- A script can read, change, or delete files it should not touch
- A skill's instructions can lead Claude to send secrets or personal data outside
- Any other security problem caused by code or skills in this repository

## How to report

Do not open a public issue. Report it through [private vulnerability reporting](https://github.com/develeep/dev-gongbang/security/advisories/new). Including the following helps us confirm the problem faster:

- The affected file or skill
- Steps to reproduce
- Impact

## Supported versions

Fixes go into the latest version. Releases are made by bumping `version` in `plugin.json`, so update the plugin to get a fix. How to update is in the [README](README.en.md#updating).
