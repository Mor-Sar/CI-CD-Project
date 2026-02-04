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

echo "Waiting for /health..."
for i in {1..30}; do
  if curl -fsS http://localhost/health > /dev/null; then
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

echo "== Deploy finished =="