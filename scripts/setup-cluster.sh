#!/usr/bin/env bash
# 로컬 kind 클러스터를 만들고 앱을 배포한다.
set -euo pipefail
cd "$(dirname "$0")/.."

CLUSTER="${KIND_CLUSTER:-harness}"

kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || kind create cluster --name "$CLUSTER"

until [ "$(kubectl --context "kind-$CLUSTER" get nodes -o jsonpath='{.items[0].status.conditions[-1].type}' 2>/dev/null)" = "Ready" ]; do
  sleep 5
done

docker build -t harness-test:local .
kind load docker-image harness-test:local --name "$CLUSTER"
kubectl --context "kind-$CLUSTER" apply -f k8s/
kubectl --context "kind-$CLUSTER" rollout status deploy/harness-test --timeout=120s
kubectl --context "kind-$CLUSTER" get pods,svc -l app=harness-test
