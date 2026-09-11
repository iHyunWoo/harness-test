#!/usr/bin/env bash
# Docker(Local Runner) 델리게이트 설치. 토큰은 .harness-delegate.env 에서 읽는다.
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=.harness-delegate.env
[ -f "$ENV_FILE" ] || { echo "$ENV_FILE 이 없습니다." >&2; exit 1; }

set -a; . "$ENV_FILE"; set +a
: "${HARNESS_ACCOUNT_ID:?}" "${HARNESS_DELEGATE_TOKEN:?}"
NAME="${HARNESS_DELEGATE_NAME:-docker-delegate}"
MEM="${HARNESS_DELEGATE_DOCKER_MEMORY:-2g}"
CPUS="${HARNESS_DELEGATE_DOCKER_CPUS:-1}"
# CI 가 플랫폼 셀렉터로 델리게이트를 고른다. 없으면 "no eligible delegates" 가 난다.
TAGS="${HARNESS_DELEGATE_TAGS:-linux-arm64}"

docker rm -f "$NAME" >/dev/null 2>&1 || true

docker run -d --name "$NAME" --restart unless-stopped \
  --cpus="$CPUS" --memory="$MEM" \
  -e DELEGATE_NAME="$NAME" \
  -e NEXT_GEN=true \
  -e DELEGATE_TYPE=DOCKER \
  -e ACCOUNT_ID="$HARNESS_ACCOUNT_ID" \
  -e DELEGATE_TOKEN="$HARNESS_DELEGATE_TOKEN" \
  -e DELEGATE_TAGS="$TAGS" \
  -e RUNNER_URL="${HARNESS_RUNNER_URL:-http://host.docker.internal:3000}" \
  -e MANAGER_HOST_AND_PORT="${HARNESS_MANAGER_ENDPOINT:-https://app.harness.io}" \
  "$HARNESS_DELEGATE_IMAGE"

echo "설치 완료:"
docker ps --filter "name=$NAME" --format '{{.Names}}\t{{.Status}}'
