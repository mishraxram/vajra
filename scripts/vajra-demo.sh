#!/usr/bin/env bash
set -euo pipefail

WHITE='\033[1;37m'
GRAY='\033[38;5;244m'
RESET='\033[0m'

printf '%b' "$WHITE"
cat <<'ART'
██╗   ██╗ █████╗  ██████╗██████╗  █████╗
██║   ██║██╔══██╗ ╚══██╔╝██╔══██╗██╔══██╗
██║   ██║███████║    ██║ ██████╔╝███████║
╚██╗ ██╔╝██╔══██║██   ██║ ██╔══██╗██╔══██║
 ╚████╔╝ ██║  ██║╚█████╔╝ ██║  ██║██║  ██║
  ╚═══╝  ╚═╝  ╚═╝ ╚════╝  ╚═╝  ╚═╝╚═╝  ╚═╝
ART
printf '%b\n' "$RESET"
printf '%b\n' 'THE OPEN AGENT RESEARCH ECOSYSTEM'
printf '%b\n' "${GRAY}─────────────────────────────────────────────────────────────────${RESET}"

question="${*:-}"
if [[ -z "${question//[[:space:]]/}" ]]; then
  read -r -p 'vajra ➔ ' question
fi
if [[ -z "${question//[[:space:]]/}" ]]; then
  printf '%s\n' 'Please enter a research question.' >&2
  exit 2
fi

mode="${VAJRA_MODE:-standard}"
printf 'Running real Vajra research (mode: %s)...\n' "$mode"
if command -v vajra >/dev/null 2>&1; then
  vajra research "$question" --mode "$mode"
elif command -v vajra.exe >/dev/null 2>&1; then
  # Also supports WSL when Vajra was installed on the Windows host.
  vajra.exe research "$question" --mode "$mode"
else
  printf '%s\n' 'Vajra is not installed. See https://github.com/mishraxram/vajra#install-and-run' >&2
  exit 127
fi
