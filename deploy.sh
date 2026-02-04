#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-sarah-new2}"

echo "== Deploy started (branch: $BRANCH) =="
cd "$(dirname "$0")"

git fetch --all
git checkout "$BRANCH"
git pull origin "$BRANCH"

docker compose up -d --build
docker compose ps

echo "== Deploy finished =="