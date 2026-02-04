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

echo "Waiting for /health (via nginx on localhost:80)..."
for i in {1..60}; do
  if python3 - << 'PY' >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("http://localhost/health", timeout=2)
PY
  then
    echo "Health OK"
    echo "== Deploy finished =="
    exit 0
  fi
  sleep 2
done

echo "ERROR: Health endpoint did not become ready"
docker compose logs --tail=200 flask_app || true
docker compose logs --tail=200 nginx || true
docker compose logs --tail=200 mariadb || true
exit 1