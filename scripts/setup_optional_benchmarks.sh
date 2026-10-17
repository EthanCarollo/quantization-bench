#!/usr/bin/env bash
set -euo pipefail

ROLEPLAY_CACHE="${HOME}/.cache/roleplay-bench"
SOURCES="${ROLEPLAY_CACHE}/sources"

checkout_revision() {
  local name="$1"
  local url="$2"
  local revision="$3"
  local path="${SOURCES}/${name}"
  if [[ ! -d "${path}/.git" ]]; then
    git clone --filter=blob:none --no-checkout "${url}" "${path}"
  fi
  git -C "${path}" fetch --depth 1 origin "${revision}"
  git -C "${path}" checkout --detach "${revision}"
}

mkdir -p "${SOURCES}"
checkout_revision AutomationBench https://github.com/zapier/AutomationBench.git 4a8e1061254004d9dac807054eed33fad7d1ff14
checkout_revision ToolSandbox https://github.com/apple/ToolSandbox.git c8571d7854316d2e1c5f288e59fe1e34e53f6dd1
checkout_revision PersonaGym https://github.com/vsamuel2003/PersonaGym.git 536f705e610289c38d84e083fcea6ea5093d3a25

uv python install 3.13
UV_PROJECT_ENVIRONMENT="${ROLEPLAY_CACHE}/automationbench-venv" \
  uv sync --frozen --no-dev --python 3.13 --project "${SOURCES}/AutomationBench"

uv python install 3.12
uv venv --python 3.12 "${ROLEPLAY_CACHE}/livecodebench-evaluator-venv"
uv pip install --python "${ROLEPLAY_CACHE}/livecodebench-evaluator-venv/bin/python" 'numpy==2.2.6'

uv venv --python 3.12 "${ROLEPLAY_CACHE}/toolsandbox-venv"
uv pip install --python "${ROLEPLAY_CACHE}/toolsandbox-venv/bin/python" -e "${SOURCES}/ToolSandbox"

uv venv --python 3.12 "${ROLEPLAY_CACHE}/personagym-venv"
uv pip install --python "${ROLEPLAY_CACHE}/personagym-venv/bin/python" -r "${SOURCES}/PersonaGym/requirements.txt"

printf '%s\n' "Pinned local benchmark environments are ready under ${ROLEPLAY_CACHE}."
