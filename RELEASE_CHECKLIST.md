# PDFtoMD Release Checklist

| 항목 | 내용 |
| :--- | :--- |
| 문서 버전 | v1.0 |
| 대상 독자 | 배포 담당자 |
| 최종 수정일 | 2026-03-16 |

## 1. 배포 전 확인

- `PDFtoMD` 최신 코드가 GitHub에 push 되어 있는지 확인
- `docuConverter01` 최신 코드가 필요한 브랜치(`frontend`)에 반영되어 있는지 확인
- `.gitignore`에 `done/`, `logs/`, `watch/`, `workspace/`, `Rejected/` 같은 운영 산출물이 제외되어 있는지 확인
- `README.md`, `USER_GUIDE.md`, `OPERATIONS_MANUAL.md`가 현재 코드 기준과 맞는지 확인

## 2. 대상 PC 준비

- `C:\Code` 폴더 생성
- Python 설치 확인
- PowerShell 사용 가능 여부 확인
- Windows 작업 스케줄러 사용 가능 여부 확인

## 3. 대상 PC 설치

### 3.1 PDFtoMD 설치

```powershell
cd C:\Code
git clone https://github.com/m18201-oh/PDFtoMD.git
cd PDFtoMD
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3.2 docuConverter01 설치

```powershell
cd C:\Code
git clone https://github.com/m18201-oh/docuConverter01.git
cd docuConverter01
git checkout frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 4. 설정 확인

- `C:\Code\PDFtoMD\.env` 파일 준비
- `C:\Code\PDFtoMD\config.py` 경로 확인
- `register_watcher.ps1` 내부 경로 확인
- `run_watcher.bat` 내부 경로 확인

## 5. 동작 테스트

- `run_watcher.bat`로 수동 실행 테스트
- `watch` 폴더에 테스트용 PDF 1개 복사
- `logs\run.log`에 처리 시작 로그가 찍히는지 확인
- `done` 폴더에 결과 `.md`, 원본 PDF, `_briefing.md`가 생기는지 확인
- 오류 시 `logs\error.log` 확인

## 6. 자동 실행 등록

```powershell
cd C:\Code\PDFtoMD
.\register_watcher.ps1
```

- Windows 로그인 후 watcher 자동 실행 여부 확인
- 재부팅 후 `watch`에 이미 남아 있는 PDF도 자동 처리되는지 확인

## 7. 배포 완료 기준

- 수동 실행 정상
- 자동 실행 정상
- PDF 1건 이상 성공적으로 변환
- `done` 폴더에 브리핑 문서까지 정상 생성
- 운영 문서 링크 확인 완료

---

## 관련 문서

- [README.md](./README.md)
- [USER_GUIDE.md](./USER_GUIDE.md)
- [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md)
- [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)
