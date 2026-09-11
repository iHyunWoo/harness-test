#!/usr/bin/env bash
# Harness Delegate 설치. 토큰은 .harness-delegate.env 에서 읽는다(커밋 대상 아님).
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=.harness-delegate.env

if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE 이 없습니다. .harness-delegate.env.example 을 복사해 값을 채우세요." >&2
  exit 1
fi

set -a; . "$ENV_FILE"; set +a
: "${HARNESS_ACCOUNT_ID:?}" "${HARNESS_DELEGATE_TOKEN:?}"
NAME="${HARNESS_DELEGATE_NAME:-helm-delegate}"

kubectl cluster-info >/dev/null 2>&1 || { echo "클러스터에 연결할 수 없습니다." >&2; exit 1; }

helm repo add harness-delegate https://app.harness.io/storage/harness-download/delegate-helm-chart/ >/dev/null
helm repo update harness-delegate >/dev/null

helm upgrade -i "$NAME" --namespace harness-delegate-ng --create-namespace \
  harness-delegate/harness-delegate-ng \
  --set delegateName="$NAME" \
  --set accountId="$HARNESS_ACCOUNT_ID" \
  --set delegateToken="$HARNESS_DELEGATE_TOKEN" \
  --set managerEndpoint="${HARNESS_MANAGER_ENDPOINT:-https://app.harness.io}" \
  --set delegateDockerImage="$HARNESS_DELEGATE_IMAGE" \
  --set replicas=1 --set upgrader.enabled=true \
  --set cpu="${HARNESS_DELEGATE_CPU:-1}" \
  --set memory="${HARNESS_DELEGATE_MEMORY:-2048}"

echo "설치 완료. 파드 상태:"
kubectl -n harness-delegate-ng get pods
