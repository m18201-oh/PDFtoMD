# Project Init Workflow

Python 프로젝트 초기 세팅을 일괄 처리하는 워크플로우.
아래 단계를 순서대로 모두 실행할 것.

---

## 1. README.md 생성

프로젝트 루트에 `README.md`를 생성한다.

포함할 내용:
- 프로젝트 이름 및 한 줄 소개
- 주요 기능 목록
- 설치 방법 (`git clone` + 가상환경 활성화 + 패키지 설치)
- 사용법 (CLI 예시)
- 요구 사항 (Python 버전 등)
- 라이선스

---

## 2. Git 초기화 및 첫 커밋

```bash
git init
git add README.md
git commit -m "Initial commit: Add README.md"
```

> ⚠️ 원격 저장소(remote)는 연결하지 않는다.

---

## 3. Python 가상환경 생성

```bash
python -m venv .venv
```

- 경로: 프로젝트 루트의 `.venv/`
- 이후 모든 작업(패키지 설치, 스크립트 실행)은 반드시 가상환경을 활성화한 상태에서 진행

### 활성화 명령어

| OS | 명령어 |
|----|--------|
| Windows (PowerShell) | `.\.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.\.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

---

## 4. .gitignore 생성 및 커밋

프로젝트 루트에 `.gitignore`를 생성한다.

```gitignore
# Virtual environment
.venv/

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/

# OS
Thumbs.db
.DS_Store
```

```bash
git add .gitignore
git commit -m "Add .gitignore: exclude venv, cache, IDE files"
```

---

## 5. 완료 확인

- [ ] `README.md` 존재
- [ ] `git log`에 커밋 2개 (README, .gitignore)
- [ ] `.venv/` 폴더 존재 및 활성화 가능
- [ ] `.gitignore`에 `.venv/` 포함
- [ ] 원격 저장소 미연결 상태
