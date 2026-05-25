#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/cytocore/CompuCyto}"
BRANCH="${CYTOCORE_BRANCH:-}"

cd "$APP_DIR"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  current_branch="$(git rev-parse --abbrev-ref HEAD)"
  branch="${BRANCH:-$current_branch}"

  if [ "$branch" != "HEAD" ]; then
    if ! {
      git fetch --prune origin &&
      git checkout "$branch" &&
      git pull --ff-only origin "$branch"
    }; then
      echo "Git update failed; starting the currently checked-out code."
    fi
  fi
fi

docker compose up -d --build --remove-orphans
