# PDFtoMD User Guide

이 문서는 `PDFtoMD`를 사용하는 분이 개발 지식 없이도 빠르게 전체 흐름을 이해할 수 있도록 만든 안내서입니다.

| 항목 | 내용 |
| :--- | :--- |
| 문서 버전 | v1.1 |
| 대상 독자 | 비개발 사용자 |
| 최종 수정일 | 2026-03-17 |

## 1. 이 시스템이 하는 일

이 시스템은 `PDF 파일을 Markdown(.md) 문서로 자동 변환`합니다.

사용 방법은 아주 단순합니다.

1. PDF를 넣습니다.
2. 시스템이 자동으로 처리합니다.
3. 결과 Markdown 파일을 확인합니다.

## 2. 파일을 어디에 넣고 어디서 확인하나요?

- 입력 폴더: `C:\Code\PDFtoMD\01_watch_inbox`
- 결과 파일은 `C:\Code\PDFtoMD\04_done` 폴더에 생성됩니다.

즉, 폴더 역할은 이렇게 나뉩니다.

- `01_watch_inbox`: PDF를 넣는 곳
- `04_done`: 변환이 끝난 결과를 확인하는 곳

## 3. 평소 사용하는 방법

### 3.1 자동 감시 상태로 사용

PC 로그인 시 자동 실행되도록 등록해 두었다면, `01_watch_inbox` 폴더에 PDF만 넣으면 됩니다.

자동 등록 스크립트:
- `C:\Code\PDFtoMD\register_watcher.ps1`

### 3.2 수동으로 실행

자동 감시가 꺼져 있거나 진행 상황을 직접 보고 싶다면 아래 파일을 실행합니다.

- `C:\Code\PDFtoMD\run_watcher.bat`

검은 창이 열리면 정상입니다.

## 4. 정상 처리되면 어떻게 되나요?

정상적으로 끝나면 다음 일이 일어납니다.

- `04_done` 폴더에 같은 이름의 `.md` 파일이 생깁니다.
- 원본 PDF도 `04_done` 폴더로 이동합니다.
- 작업 브리핑용 `.md` 파일도 함께 생성됩니다.

완료 원본 보관 폴더:
- `C:\Code\PDFtoMD\04_done`

## 5. 실패하면 어디를 보면 되나요?

### 5.1 03_rejected 폴더 확인

입력 파일 자체에 문제가 있으면 여기로 이동합니다.

- `C:\Code\PDFtoMD\03_rejected`

같이 생성되는 `reject_reason.txt` 파일을 열면 실패 이유를 볼 수 있습니다.

예:
- 빈 파일
- 손상된 PDF
- 암호 걸린 PDF
- PDF 형식이 아님

### 5.2 로그 파일 확인

시스템이 지금 무엇을 하고 있는지 가장 잘 보여주는 파일입니다.

- 실행 로그: `C:\Code\PDFtoMD\05_logs\run.log`
- 오류 로그: `C:\Code\PDFtoMD\05_logs\error.log`

## 6. 가장 쉬운 상태 확인 방법

아래 중 하나만 보면 됩니다.

### 6.1 성공인지 확인

- `04_done` 폴더에 `.md` 파일이 생겼다
- 원본 PDF도 `04_done` 폴더에 들어갔다
- 작업 브리핑 `.md` 파일도 함께 보인다

### 6.2 실패인지 확인

- 파일이 `03_rejected` 폴더로 갔다
- `error.log`에 오류가 남았다

## 7. 작업이 멈춘 것 같으면

프로젝트 루트에 아래 파일이 남아 있는지 확인합니다.

- `C:\Code\PDFtoMD\.lock`

이 파일은 `현재 작업 중`이라는 표시입니다.

하지만 비정상 종료 후에도 남아 있을 수 있습니다.  
시스템이 분명히 멈춰 있는데 `.lock` 파일이 계속 남아 있으면, 삭제한 뒤 다시 실행하면 됩니다.

PC가 꺼지거나 작업이 중간에 멈춘 경우에도, 현재 버전은 다음 실행 때 가능한 범위에서 이어받기를 시도합니다. 이미 변환된 페이지 결과는 재사용하고, 남은 부분부터 다시 진행합니다.

## 8. 운영자가 기억하면 좋은 핵심 폴더

- 입력: `C:\Code\PDFtoMD\01_watch_inbox`
- 최종 결과 확인: `C:\Code\PDFtoMD\04_done`
- 완료 원본: `C:\Code\PDFtoMD\04_done`
- 실패 격리: `C:\Code\PDFtoMD\03_rejected`
- 진행 중 작업 흔적: `C:\Code\PDFtoMD\02_workspace`
- 로그: `C:\Code\PDFtoMD\05_logs`

## 9. 가장 중요한 한 줄 판단 기준

`04_done`에 결과 `.md`, 원본 PDF, 작업 브리핑 `.md`가 함께 보이면 성공입니다.

그렇지 않으면 `03_rejected` 또는 `05_logs`를 먼저 보면 됩니다.

---

## 관련 문서

- [README.md](../README.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md)
