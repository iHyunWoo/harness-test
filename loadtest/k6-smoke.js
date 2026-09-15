// k6 부하 테스트. Harness Load Test 스텝이나 로컬에서 그대로 돌릴 수 있다.
//   k6 run -e BASE_URL=http://localhost:8000 loadtest/k6-smoke.js
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");
const BASE = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  stages: [
    { duration: "20s", target: 10 },   // 워밍업
    { duration: "40s", target: 30 },   // 유지
    { duration: "20s", target: 0 },    // 감속
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    errors: ["rate<0.01"],
  },
};

export default function () {
  const health = http.get(`${BASE}/health`);
  check(health, {
    "health 200": (r) => r.status === 200,
    "health ok": (r) => r.json("status") === "ok",
  }) || errorRate.add(1);

  const created = http.post(
    `${BASE}/notes`,
    JSON.stringify({ title: `load ${__VU}-${__ITER}`, body: "hello world", tags: ["load"] }),
    { headers: { "Content-Type": "application/json" } },
  );
  check(created, { "create 201": (r) => r.status === 201 }) || errorRate.add(1);

  const list = http.get(`${BASE}/notes?tag=load`);
  check(list, { "list 200": (r) => r.status === 200 }) || errorRate.add(1);

  sleep(1);
}
