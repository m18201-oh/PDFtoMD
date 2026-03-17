"""
Module 1.5 — 파일 유효성 검사 (Validator)
비정상 PDF(빈 파일·손상·암호화)를 조기 차단.
PRD v2.2 § 5 "Module 1.5" — 이중 검사 방식
  1차: 파일 선두 1024바이트 이내 %PDF- 시그니처 탐색
  2차: pypdf2 파싱 시도 (try/except 교차검증)
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime

from PyPDF2 import PdfReader

from src.config import WORKSPACE_DIR, REJECTED_DIR

logger = logging.getLogger("PDFtoMD")


def _write_reject_reason(reject_dir: Path, filename: str, reason: str):
    """Rejected 폴더에 거부 사유 텍스트 파일 생성."""
    reject_dir.mkdir(parents=True, exist_ok=True)
    reason_file = reject_dir / f"{Path(filename).stem}_reject_reason.txt"
    reason_file.write_text(
        f"파일명: {filename}\n"
        f"사유: {reason}\n"
        f"시각: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def validate(job_id: str, pdf_path: Path) -> Path | None:
    """
    02_workspace/{job_id}/ 내 복사된 PDF를 검증.
    통과 시 검증된 PDF 경로 반환, 실패 시 03_rejected/ 격리 후 None 반환.
    """
    job_dir = WORKSPACE_DIR / job_id
    copied_pdf = job_dir / pdf_path.name

    # 거부 시 이동 대상
    reject_dir = REJECTED_DIR / f"{job_id}_{pdf_path.stem}"

    # ① 파일 크기 > 0바이트
    if copied_pdf.stat().st_size == 0:
        reason = "빈 파일 (0바이트)"
        logger.warning("[M1.5] 검증 실패 — %s: %s", reason, copied_pdf.name)
        _reject(copied_pdf, reject_dir, reason)
        return None

    # ② 1차 검사: Magic Bytes — 파일 선두 1024바이트 이내 %PDF- 시그니처
    try:
        with open(copied_pdf, "rb") as f:
            header = f.read(1024)
        if b"%PDF-" not in header:
            reason = "Magic bytes 검사 실패 — 선두 1024바이트 내 %PDF- 시그니처 없음"
            logger.warning("[M1.5] 검증 실패 — %s: %s", reason, copied_pdf.name)
            _reject(copied_pdf, reject_dir, reason)
            return None
    except Exception as e:
        reason = f"파일 읽기 오류: {e}"
        logger.warning("[M1.5] 검증 실패 — %s: %s", reason, copied_pdf.name)
        _reject(copied_pdf, reject_dir, reason)
        return None

    # ③ 2차 검사: pypdf2 파싱 + 암호화 + 페이지 수
    try:
        reader = PdfReader(str(copied_pdf))

        # 암호화 여부
        if reader.is_encrypted:
            reason = "암호화된 PDF — reader.is_encrypted == True"
            logger.warning("[M1.5] 검증 실패 — %s: %s", reason, copied_pdf.name)
            _reject(copied_pdf, reject_dir, reason)
            return None

        # 페이지 수 >= 1
        if len(reader.pages) < 1:
            reason = "페이지 없음 — len(reader.pages) == 0"
            logger.warning("[M1.5] 검증 실패 — %s: %s", reason, copied_pdf.name)
            _reject(copied_pdf, reject_dir, reason)
            return None

    except Exception as e:
        reason = f"pypdf2 파싱 실패: {e}"
        logger.warning("[M1.5] 검증 실패 — %s: %s", reason, copied_pdf.name)
        _reject(copied_pdf, reject_dir, reason)
        return None

    logger.info("[M1.5] 유효성 검사 통과: %s (%d 페이지)", copied_pdf.name, len(reader.pages))
    return copied_pdf


def _reject(pdf_path: Path, reject_dir: Path, reason: str):
    """파일을 03_rejected/ 폴더로 격리."""
    reject_dir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(pdf_path), str(reject_dir / pdf_path.name))
    except Exception as e:
        logger.error("[M1.5] Rejected 이동 실패: %s", e)
    _write_reject_reason(reject_dir, pdf_path.name, reason)
