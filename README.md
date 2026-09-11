# harness-test

Harness CI/CD 테스트용 FastAPI 앱.

## 앱

노트 CRUD API. 제목에서 slug를, 본문에서 단어 수·읽기 시간·발췌를 파생한다.

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/` | 기본 메시지 |
| GET | `/health` | 헬스체크 |
| GET | `/notes` | 목록. `?tag=` `?q=` 필터 |
| POST | `/notes` | 생성 (201) |
| GET | `/notes/{id}` | 조회 |
| PATCH | `/notes/{id}` | 부분 수정. 파생 필드 재계산 |
| DELETE | `/notes/{id}` | 삭제 (204) |
| GET | `/stats` | 노트 수, 총 단어 수, 태그 종류 수 |

저장소는 인메모리라 프로세스를 재시작하면 초기화된다.

## 구조

```
app/
  main.py     라우팅
  models.py   Pydantic 모델
  text.py     slug·단어수·읽기시간·발췌 (순수 함수)
tests/
  test_text.py  단위 테스트 (HTTP 없음)
  test_api.py   API 통합 테스트
  flaky/        의도적으로 불안정한 테스트
.harness/
  pipeline.yaml Harness 파이프라인
```

## 명령어

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

pytest tests --ignore=tests/flaky -q     # 정상 스위트 (44개)
pytest tests/flaky -q                    # flaky 스위트
ruff check .
uvicorn app.main:app --reload
docker build -t harness-test:local .
```

## 파이프라인

`.harness/pipeline.yaml` 의 CI stage 하나에 스텝 7개.

| 스텝 | 타입 | 역할 |
| --- | --- | --- |
| Install dependencies | Run | 의존성 설치 |
| Lint | Run | ruff |
| Test | Run | pytest + JUnit 리포트 + 커버리지 |
| Flaky tests | Run | flaky 스위트. 실패해도 무시 |
| Run API | **Background** | uvicorn을 stage 동안 상주 |
| Smoke test | Run | `/health` 확인 |
| Build and push image | BuildAndPushDockerRegistry | 이미지 빌드·푸시 |

### 사용한 Harness 기능

- **sharedPaths** — `/root/.cache/pip` 를 스텝 간에 공유. 워크스페이스(`/harness`) 밖 경로는 기본적으로 유지되지 않는다
- **reports** — JUnit XML 을 Tests 탭에 연결
- **failureStrategies: Ignore** — flaky 스위트가 빌드를 세우지 않게 한다
- **Background 스텝** — 앱을 띄워두고 다음 스텝에서 호출
- **runtime.type: Cloud** — Harness Cloud 빌드 인프라

### 적용 전 채울 값

```
YOUR_HARNESS_PROJECT_ID
YOUR_GITHUB_CONNECTOR_ID
YOUR_DOCKER_CONNECTOR_ID
YOUR_DOCKER_REPO
```

## flaky 스위트

Harness의 flaky 탐지를 확인하려고 일부러 넣었다.

| 테스트 | 실패율 | 유형 |
| --- | --- | --- |
| `test_flaky_high_failure_rate` | ~40% | 무작위 |
| `test_flaky_medium_failure_rate` | ~20% | 무작위 |
| `test_flaky_low_failure_rate` | ~5% | 드물게 |
| `test_flaky_timing_dependent` | ~50% | 시간 의존 |
| `test_slow_but_stable` | 0% | 느림 (1.5초) |
| `test_moderately_slow` | 0% | 느림 (0.6초) |

패턴이 잡히려면 여러 번 실행해야 한다.
