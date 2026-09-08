#!/usr/bin/env bash
set -euo pipefail

# xmllint がスキーマをネットワーク取得しないようカタログを設定する。
# shellcheck source=scripts/xml-catalog.sh
source "$(dirname "${BASH_SOURCE[0]}")/xml-catalog.sh"

if ! command -v colcon >/dev/null 2>&1; then
  echo "error: colcon is not installed. Install python3-colcon-common-extensions." >&2
  exit 127
fi

# Tests import other workspace packages, so load the built overlay first.
workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "${workspace_root}/install/setup.bash" ]]; then
  echo "error: workspace overlay is missing. Run scripts/build.sh first." >&2
  exit 1
fi
set +u
# shellcheck source=/dev/null
source "${workspace_root}/install/setup.bash"
set -u

packages=$(colcon list --names-only 2>/dev/null || true)
if [[ -z "${packages}" ]]; then
  echo "No ROS 2 packages found; skipping colcon lint/test discovery."
  exit 0
fi

colcon test \
  --event-handlers console_direct+ \
  --packages-select ${packages} \
  --ctest-args -R "(lint|copyright|flake8|pep257|xmllint|cppcheck|cpplint)" "$@"
