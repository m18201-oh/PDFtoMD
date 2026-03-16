# PDFtoMD

`watch` 폴더를 감시하다가 PDF가 들어오면 자동으로 Markdown으로 변환하는 도구입니다.

| 항목 | 내용 |
| :--- | :--- |
| 문서 버전 | v1.0 |
| 대상 독자 | 제품 개요와 빠른 시작이 필요한 사용자 |
| 최종 수정일 | 2026-03-16 |

## 1. 문서 안내

이 프로젝트의 문서는 용도에 따라 아래처럼 나뉩니다.

- [README.md](./README.md): 제품 소개와 빠른 진입을 위한 문서
- [USER_GUIDE.md](./USER_GUIDE.md): 비개발자가 가장 짧고 쉽게 전체 사용 흐름을 파악하기 위한 안내 문서
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md): 운영자가 현재 상태를 판단하고 문제에 대응하기 위한 실무 문서

## 2. 현재 동작 방식

- `watch/` 폴더에 들어온 PDF 자동 감지
- PDF 유효성 검사 후 비정상 파일은 `Rejected/`로 격리
- PDF를 페이지별로 분할 후 외부 변환기 `C:\Code\docuConverter01`에 전달
- 변환된 페이지별 Markdown을 하나로 병합
- 최종 Markdown, 원본 PDF, 작업 브리핑 Markdown을 `done/` 폴더에 보관
- `docuConverter01` 메트릭을 기반으로 페이지당 평균 처리시간을 기록
- 진행 로그는 `logs/run.log`, 오류 로그는 `logs/error.log`에 기록

## 3. 설치

```bash
git clone https://github.com/your-username/PDFtoMD.git
cd PDFtoMD
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. 사용법

### 4.1 자동 감시 등록

PowerShell에서 아래 스크립트를 실행하면 Windows 로그인 시 watcher가 자동으로 시작됩니다.

```powershell
.\register_watcher.ps1
```

### 4.2 수동 실행

실시간으로 콘솔 창을 보면서 실행하려면 아래 파일을 실행합니다.

```bat
run_watcher.bat
```

### 4.3 운영 흐름

1. `watch/` 폴더에 PDF를 넣습니다.
2. 시스템이 자동으로 처리합니다.
3. 결과 `.md`, 원본 PDF, 작업 브리핑 `.md`는 `done/` 폴더에서 확인합니다.

## 5. 요구 사항

- Python 3.12 환경 사용 중
- `C:\Code\docuConverter01` 프로젝트가 함께 준비되어 있어야 함

## 6. 라이선스

MIT License

---

## 관련 문서

- [README.md](./README.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md)
