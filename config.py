"""
PDFtoMD 자동화 시스템 — 전체 설정 파일
PRD v2.2 § 7 기반.  모든 경로·파라미터를 이 파일 1곳에서 관리합니다.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── .env 로드 ──────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

# ── 프로젝트 루트 ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent

# ── 폴더 경로 ──────────────────────────────────────────────
WATCH_DIR       = PROJECT_ROOT / "watch"
WORKSPACE_DIR   = PROJECT_ROOT / "workspace"
REJECTED_DIR    = PROJECT_ROOT / "Rejected"
DONE_DIR        = PROJECT_ROOT / "done"
LOG_DIR         = PROJECT_ROOT / "logs"

# ── Lock 파일 ──────────────────────────────────────────────
LOCK_FILE       = PROJECT_ROOT / ".lock"

# ── docuConverter01 연동 (고정 경로) ───────────────────────
CONVERTER_DIR           = Path(r"C:\Code\docuConverter01")
CONVERTER_INPUT_DIR     = CONVERTER_DIR / "input"
CONVERTER_OUTPUT_DIR    = CONVERTER_DIR / "output"
CONVERTER_VENV_PYTHON   = CONVERTER_DIR / ".venv" / "Scripts" / "python.exe"

# ── 변환 파라미터 ──────────────────────────────────────────
CONVERTER_WORKERS   = 1          # 병렬 변환 워커 수 (복잡한 파일 안정성을 위해 1 추천)
CONVERT_TIMEOUT     = 7200       # subprocess 타임아웃 (초, 기본 2시간)

# ── 운영 정책 ──────────────────────────────────────────────
ORIGINAL_PDF_POLICY = "done"     # done | delete
MD_PAGE_SEPARATOR   = True       # 페이지 간 --- 구분선 삽입

# ── 보고·알림 ──────────────────────────────────────────────
REPORT_INTERVAL = 600            # 중간 보고 이메일 주기 (초)
ADMIN_EMAIL     = os.getenv("ADMIN_EMAIL", "")

# ── SMTP 설정 ──────────────────────────────────────────────
SMTP_HOST       = "smtp.gmail.com"
SMTP_PORT       = 587
SMTP_USER       = os.getenv("SMTP_USER", "")
SMTP_PASSWORD   = os.getenv("SMTP_PASSWORD", "")

# ── 로깅 설정 ──────────────────────────────────────────────
RUN_LOG_FILE    = LOG_DIR / "run.log"
ERROR_LOG_FILE  = LOG_DIR / "error.log"
