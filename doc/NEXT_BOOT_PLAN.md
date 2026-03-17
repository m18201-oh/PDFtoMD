# PDFtoMD Next Boot Plan

| 항목 | 내용 |
| :--- | :--- |
| 문서 버전 | v1.0 |
| 대상 독자 | 운영자 / 다음 근무 시간의 본인 |
| 최종 수정일 | 2026-03-17 |

## 1. 오늘 저장 시점의 상태

- `PDFtoMD`는 `src/`, `doc/`, 번호형 운영 폴더 구조로 재정리됨
- watcher 폴링 주기는 현재 `10초`
- `docuConverter01`은 `workers=1`일 때 순차 처리 fallback 적용됨
- `PDFtoMD`는 변환 중 무진행 시 모니터링 간격을 점점 늘리고, `30분` 도달 시 알림을 보내도록 수정됨
- 변환 실패 시 중간 산출물을 바로 지우지 않도록 복구 로직 보강됨
- 저장 시점 기준 최근 확인 결과:
  - `C:\Code\docuConverter01\output`에 `19`개의 페이지별 `.md` 생성
  - `C:\Code\PDFtoMD\04_done`에는 아직 2026 문서 최종 결과 없음

## 2. 내일 PC를 다시 켜면 기대되는 자동 동작

1. Windows 로그인 시 `HKCU Run`에 등록된 watcher가 자동 시작
2. watcher가 `C:\Code\PDFtoMD\01_watch_inbox`를 즉시 확인
3. 원본 PDF가 남아 있고 `.lock`이 활성 상태가 아니면 `main.py` 트리거
4. `main.py`가 `02_workspace`의 기존 job과 `docuConverter01/output`의 기존 페이지별 `.md`를 기준으로 이어받기 시도
5. `docuConverter01` 진행 중 무진행 시간이 길어지면 확인 간격을 늘리고, 최대 `30분` 도달 시 알림 시도

## 3. PC를 켠 뒤 1시간 후 체크할 것

1. `C:\Code\PDFtoMD\04_done` 확인
   - 최종 `.md`
   - 원본 PDF
   - `_briefing.md`

2. `C:\Code\PDFtoMD\05_logs\run.log` 마지막 50줄 확인
   - recovery 시작 로그가 있는지
   - `[M3] 변환 진행` 로그가 누적되는지
   - `[M4]`, `[M5]`, `[M6]`까지 갔는지

3. `C:\Code\docuConverter01\output` 확인
   - `.md` 개수가 `24`개가 되었는지

4. `C:\Code\docuConverter01\input` 확인
   - 남은 `.pdf`가 줄었는지 또는 `0`인지

5. `C:\Code\PDFtoMD\.lock` 확인
   - 작업 중이면 있을 수 있음
   - 작업이 멈췄는데도 남아 있으면 stale 가능성 점검

## 4. 내일 가장 빠른 판단 기준

- `04_done`에 2026 문서의 최종 결과가 있으면 성공
- `output`이 `24/24`인데 `04_done`이 비어 있으면 `main.py` 한 번 재트리거 필요
- `output` 개수가 더 늘지 않고 `run.log`도 조용하면 정체 상태 재점검 필요

## 5. 내일 Codex 호출용 메모

다음처럼 요청하면 이어받기 쉽습니다.

```text
어제 저장한 NEXT_BOOT_PLAN 기준으로
현재 PDFtoMD와 docuConverter01 상태 점검하고
2026 문서가 어디까지 진행됐는지 이어서 처리해줘
```
