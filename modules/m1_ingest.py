"""
Module 1 — 인입
watch/의 PDF를 workspace/{job_id}/ 서브폴더로 복사하고 job_manifest.json 초기화.
PRD v2.2 § 5 "Module 1"
"""

import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

from config import WORKSPACE_DIR

logger = logging.getLogger("PDFtoMD")

MAX_COPY_RETRIES = 3
COPY_RETRY_DELAY = 5  # 초


def ingest(pdf_path: Path) -> str:
    """
    PDF 파일을 workspace/{job_id}/ 서브폴더로 복사하고 job_manifest.json 생성.
    Returns: job_id 문자열
    """
    # job_id 생성: {파일명}_{YYYYmmdd_HHMMSS}
    stem = pdf_path.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"{stem}_{timestamp}"

    # workspace/{job_id}/ 서브폴더 생성
    job_dir = WORKSPACE_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # PDF 복사 (파일 잠금 재시도)
    dest = job_dir / pdf_path.name
    for attempt in range(1, MAX_COPY_RETRIES + 1):
        try:
            shutil.copy2(str(pdf_path), str(dest))
            logger.info("[M1] PDF 복사 완료: %s → %s", pdf_path.name, job_dir.name)
            break
        except Exception as e:
            logger.warning(
                "[M1] 복사 실패 (시도 %d/%d): %s — %s",
                attempt, MAX_COPY_RETRIES, pdf_path.name, e,
            )
            if attempt == MAX_COPY_RETRIES:
                raise RuntimeError(
                    f"PDF 복사 실패 ({MAX_COPY_RETRIES}회 재시도 후): {pdf_path.name}"
                ) from e
            time.sleep(COPY_RETRY_DELAY)

    # job_manifest.json 생성
    manifest = {
        "job_id": job_id,
        "original_filename": pdf_path.name,
        "original_stem": stem,
        "timestamp": timestamp,
        "status": "ingest",
    }
    manifest_path = job_dir / "job_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("[M1] job_manifest.json 생성: %s", manifest_path)

    return job_id
