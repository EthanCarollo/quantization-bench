#!/usr/bin/env bash
set -euo pipefail

ROLEPLAY_CACHE="${HOME}/.cache/roleplay-bench"
SOURCES="${ROLEPLAY_CACHE}/sources"
REPO="${SOURCES}/AutomationBench"
REVISION="4a8e1061254004d9dac807054eed33fad7d1ff14"

mkdir -p "${SOURCES}"
if [[ ! -d "${REPO}/.git" ]]; then
  git clone --filter=blob:none --no-checkout https://github.com/zapier/AutomationBench.git "${REPO}"
fi
git -C "${REPO}" fetch --depth 1 origin "${REVISION}"
git -C "${REPO}" checkout --detach "${REVISION}"

uv python install 3.13
UV_PROJECT_ENVIRONMENT="${ROLEPLAY_CACHE}/automationbench-venv" \
  uv sync --frozen --no-dev --python 3.13 --project "${REPO}"

printf '%s\n' "Pinned AutomationBench environment is ready under ${ROLEPLAY_CACHE}."
