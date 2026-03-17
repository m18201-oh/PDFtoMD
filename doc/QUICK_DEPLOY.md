# PDFtoMD Quick Deploy

| 항목 | 내용 |
| :--- | :--- |
| 문서 버전 | v1.1 |
| 대상 독자 | 설치 담당자 |
| 최종 수정일 | 2026-03-17 |

## 목적

이 문서는 다른 PC에 `PDFtoMD`와 `docuConverter01`을 함께 설치할 때, 설치 담당자가 짧은 순서대로 바로 따라 할 수 있도록 만든 실행용 문서입니다.

## 설치 순서

### 1. 폴더 준비

```powershell
mkdir C:\Code
cd C:\Code
```

### 2. PDFtoMD 설치

```powershell
git clone https://github.com/m18201-oh/PDFtoMD.git
cd PDFtoMD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 3. docuConverter01 설치

```powershell
cd C:\Code
git clone https://github.com/m18201-oh/docuConverter01.git
cd docuConverter01
git checkout frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. PDFtoMD 설정 확인

아래 항목만 확인합니다.

- `C:\Code\PDFtoMD\.env` 파일 존재
- `C:\Code\PDFtoMD\src\config.py`가 `C:\Code\docuConverter01` 경로를 가리킴
- `C:\Code\PDFtoMD\.venv\Scripts\python.exe` 존재
- `C:\Code\docuConverter01\.venv\Scripts\python.exe` 존재

### 5. 수동 테스트

```powershell
cd C:\Code\PDFtoMD
.\run_watcher.bat
```

그다음:

1. `01_watch_inbox` 폴더에 테스트 PDF 1개 넣기
2. `05_logs\run.log` 확인
3. `04_done` 폴더에 결과 `.md`, 원본 PDF, `_briefing.md` 생성 확인

### 6. 자동 실행 등록

```powershell
cd C:\Code\PDFtoMD
.\register_watcher.ps1
```

## 완료 기준

- 수동 테스트 성공
- 자동 실행 등록 성공
- `04_done` 폴더 결과 확인 성공

---

## 관련 문서

- [README.md](../README.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md)
- [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)
- [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)
