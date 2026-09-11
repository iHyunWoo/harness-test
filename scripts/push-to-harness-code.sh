#!/usr/bin/env bash
# GitHub 정본 내용을 Harness Code 로 푸시한다.
# 자격증명은 .harness-code.env 에서 읽는다(커밋 대상 아님).
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=.harness-code.env

if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE 이 없습니다. .harness-code.env.example 을 복사해 값을 채우세요." >&2
  exit 1
fi

set -a; . "$ENV_FILE"; set +a
: "${HARNESS_CODE_URL:?}" "${HARNESS_CODE_USER:?}" "${HARNESS_CODE_TOKEN:?}"

BRANCH="${1:-main}"

# 사용자명이 이메일이면 @ 가 URL 을 깨뜨리므로 percent-encoding 한다.
urlencode() {
  python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}
ENC_USER=$(urlencode "$HARNESS_CODE_USER")
ENC_TOKEN=$(urlencode "$HARNESS_CODE_TOKEN")

# 토큰이 remote 설정이나 로그에 남지 않도록 매번 조립해서 쓴다.
AUTH_URL="${HARNESS_CODE_URL/https:\/\//https://${ENC_USER}:${ENC_TOKEN}@}"

git push "$AUTH_URL" "$BRANCH" 2>&1 | sed -e "s|${ENC_TOKEN}|***|g" -e "s|${HARNESS_CODE_TOKEN}|***|g"
echo "푸시 완료: $BRANCH -> ${HARNESS_CODE_URL}"
