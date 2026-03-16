"""
rollback() — 오류 발생 시 잔존 파일 정리 + .lock 해제
PRD v2.2 § 6.2 — 각 스텝 개별 try/except, .lock은 finally 최하단 보장.
"""

import shutil
import logging
from pathlib import Path

from config import (
    WORKSPACE_DIR, LOCK_FILE,
    CONVERTER_INPUT_DIR, CONVERTER_OUTPUT_DIR,
)

logger = logging.getLogger("PDFtoMD")


def rollback(job_id: str, release_lock: bool = True):
    """
    중단 상황에서 잔존 파일 정리.
    release_lock=True 일 때만 .lock 삭제 (main.py의 finally에서 직접 삭제하는 경우 False).
    """
    logger.warning("[ROLLBACK] 롤백 시작 — job_id=%s", job_id)

    try:
        # ① docuConverter01/input/ 정리
        try:
            if CONVERTER_INPUT_DIR.exists():
                shutil.rmtree(str(CONVERTER_INPUT_DIR))
            CONVERTER_INPUT_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("[ROLLBACK] ① converter/input/ 재생성 완료")
        except Exception as e:
            logger.error("[ROLLBACK] ① converter/input/ 정리 실패: %s", e)

        # ② docuConverter01/output/ 정리
        try:
            if CONVERTER_OUTPUT_DIR.exists():
                shutil.rmtree(str(CONVERTER_OUTPUT_DIR))
            CONVERTER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("[ROLLBACK] ② converter/output/ 재생성 완료")
        except Exception as e:
            logger.error("[ROLLBACK] ② converter/output/ 정리 실패: %s", e)

        # ③ workspace/{job_id}/ 삭제
        try:
            job_dir = WORKSPACE_DIR / job_id
            if job_dir.exists():
                shutil.rmtree(str(job_dir))
                logger.info("[ROLLBACK] ③ workspace/%s/ 삭제 완료", job_id)
        except Exception as e:
            logger.error("[ROLLBACK] ③ workspace/%s/ 삭제 실패: %s", job_id, e)

    finally:
        # ④ .lock 파일 삭제 — finally 최하단, 무조건 실행
        if release_lock:
            try:
                LOCK_FILE.unlink(missing_ok=True)
                logger.info("[ROLLBACK] ④ .lock 삭제 완료")
            except Exception:
                # 최후 수단: 실패해도 무시
                try:
                    Path(LOCK_FILE).unlink(missing_ok=True)
                except Exception:
                    pass

    logger.warning("[ROLLBACK] 롤백 완료 — job_id=%s", job_id)
