# PDFtoMD

`watch` 폴더를 감시하다가 PDF가 들어오면 자동으로 Markdown으로 변환하는 도구입니다.

| 항목 | 내용 |
| :--- | :--- |
| 문서 버전 | v1.2 |
| 대상 독자 | 제품 개요와 빠른 시작이 필요한 사용자 |
| 최종 수정일 | 2026-03-16 |

## 1. 문서 안내

이 프로젝트의 문서는 용도에 따라 아래처럼 나뉩니다.

- [README.md](./README.md): 제품 소개와 빠른 진입을 위한 문서
- [USER_GUIDE.md](./USER_GUIDE.md): 비개발자가 가장 짧고 쉽게 전체 사용 흐름을 파악하기 위한 안내 문서
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md): 운영자가 현재 상태를 판단하고 문제에 대응하기 위한 실무 문서
- [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md): 다른 PC 배포 전후에 확인할 항목을 정리한 문서
- [QUICK_DEPLOY.md](./QUICK_DEPLOY.md): 설치 담당자가 짧은 순서대로 바로 따라 하는 실행용 문서

## 2. 지원 환경과 전제

- Windows 환경 기준
- PowerShell 사용 기준
- 권장 설치 경로: `C:\Code\PDFtoMD`, `C:\Code\docuConverter01`
- `PDFtoMD`는 단독 실행이 아니라 `docuConverter01`과 함께 동작
- `docuConverter01`은 `frontend` 브랜치 기준으로 설치 권장
- 장시간 대량 변환은 개인 업무용 PC보다 서버나 유휴 자원이 있는 환경에 더 적합
- 이메일 알림을 쓰려면 `.env` 설정 필요

## 3. 현재 동작 방식

- `watch/` 폴더에 들어온 PDF 자동 감지
- watcher가 `watch/` 폴더를 10분 주기로 확인하여, 파일이 이미 들어 있는 상태에서도 자동 처리 시도
- PDF 유효성 검사 후 비정상 파일은 `Rejected/`로 격리
- PDF를 페이지별로 분할 후 외부 변환기 `C:\Code\docuConverter01`에 전달
- 변환된 페이지별 Markdown을 하나로 병합
- 최종 Markdown, 원본 PDF, 작업 브리핑 Markdown을 `done/` 폴더에 보관
- `docuConverter01` 메트릭을 기반으로 페이지당 평균 처리시간을 기록
- 진행 로그는 `logs/run.log`, 오류 로그는 `logs/error.log`에 기록

### 3.1 구조 요약

```text
watcher.py
  -> main.py
    -> modules/*
      -> C:\Code\docuConverter01
        -> done/
```

## 4. 다른 PC 설치 절차

이 프로젝트는 현재 경로가 고정되어 있으므로, 다른 PC에도 아래 구조를 그대로 맞추는 것을 권장합니다.

- `C:\Code\PDFtoMD`
- `C:\Code\docuConverter01`

### 4.1 PDFtoMD 설치

```bash
cd C:\Code
git clone https://github.com/m18201-oh/PDFtoMD.git
cd PDFtoMD
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 4.2 docuConverter01 설치

`PDFtoMD`는 `C:\Code\docuConverter01` 프로젝트를 함께 사용합니다. 설치 후에는 `docuConverter01` 저장소의 `README.md`와 `RELEASE_CHECKLIST.md`를 기준으로 추가 검증할 수 있습니다.

```bash
cd C:\Code
git clone https://github.com/m18201-oh/docuConverter01.git
cd docuConverter01
git checkout frontend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 4.3 `.env` 준비

`.env.example`을 복사해 `.env` 파일을 만든 뒤 필요한 값을 입력합니다.

```powershell
Copy-Item .env.example .env
```

기본 항목:

- `SMTP_USER`
- `SMTP_PASSWORD`
- `ADMIN_EMAIL`

이 값이 비어 있어도 변환은 동작하지만, 이메일 알림은 비활성화됩니다.

### 4.4 필수 폴더와 환경 확인

아래 항목이 맞아야 정상 동작합니다.

1. `C:\Code\PDFtoMD\.venv\Scripts\python.exe` 존재
2. `C:\Code\docuConverter01\.venv\Scripts\python.exe` 존재
3. `C:\Code\PDFtoMD\.env` 파일 존재
4. `C:\Code\PDFtoMD\watch`, `done`, `logs`, `workspace`, `Rejected` 폴더 생성 가능

### 4.5 첫 실행 전 권장 확인

- `config.py`의 경로가 현재 PC 구조와 맞는지 확인
- `register_watcher.ps1`와 `run_watcher.bat`의 경로가 `C:\Code\PDFtoMD` 기준인지 확인
- Windows PowerShell 실행 정책 때문에 스크립트 실행이 막히면 관리자 승인 후 허용

## 5. 설치 후 3단계 검증

다른 PC에 설치한 뒤에는 아래 3단계로 빠르게 정상 여부를 확인할 수 있습니다.

1. `run_watcher.bat`를 실행해 watcher가 시작되는지 확인
2. `watch` 폴더에 테스트용 PDF 1개를 넣고 `logs\run.log`에 시작 로그가 찍히는지 확인
3. `done` 폴더에 결과 `.md`, 원본 PDF, 작업 브리핑 `.md`가 생성되는지 확인

## 6. 사용법

### 6.1 자동 감시 등록

PowerShell에서 아래 스크립트를 실행하면 Windows 로그인 시 watcher가 자동으로 시작됩니다.

현재 등록 방식은 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 기준의 사용자 로그인 자동 시작입니다.

```powershell
.\register_watcher.ps1
```

### 6.2 수동 실행

실시간으로 콘솔 창을 보면서 실행하려면 아래 파일을 실행합니다.

```bat
run_watcher.bat
```

### 6.3 운영 흐름

1. `watch/` 폴더에 PDF를 넣습니다.
2. 시스템이 자동으로 처리합니다.
3. 결과 `.md`, 원본 PDF, 작업 브리핑 `.md`는 `done/` 폴더에서 확인합니다.

## 7. 요구 사항

- Python 3.12 환경 사용 중
- `C:\Code\docuConverter01` 프로젝트가 함께 준비되어 있어야 함
- 다른 PC 배포 시에도 `C:\Code` 기준 경로 유지 권장

## 8. 라이선스

MIT License

---

## 관련 문서

- [README.md](./README.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md)
- [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)
- [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)
