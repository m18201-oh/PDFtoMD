"""
Module 6 — 산출물 배치
통합 MD → done/ 이동 + 원본 PDF 처리 + 작업 브리핑 생성 + 작업 공간 정리.
PRD v2.2 § 5 "Module 6"
"""

import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

from config import WATCH_DIR, DONE_DIR, WORKSPACE_DIR, ORIGINAL_PDF_POLICY
from modules.job_briefing import create_job_briefing

logger = logging.getLogger("PDFtoMD")


def deploy(job_id: str, merged_md: Path, original_pdf_path: Path):
    """
    최종 MD를 done/에 배치하고 원본 PDF 처리 후 브리핑 생성 및 workspace 정리.
    """
    DONE_DIR.mkdir(parents=True, exist_ok=True)

    # 1) 통합 MD → DONE_DIR(done/) 이동 (사용자 요청: watch 대신 done)
    dest_name = merged_md.name
    dest = DONE_DIR / dest_name
    
    if dest.exists():
        # 동명 파일 있으면 타임스탬프 접미사 추가
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = merged_md.stem
        dest = DONE_DIR / f"{stem}_{ts}.md"

    shutil.copy2(str(merged_md), str(dest))
    logger.info("[M6] 최종 MD 배치: %s → done/", dest.name)

    # 2) 원본 PDF 처리
    archived_pdf_path = None
    if ORIGINAL_PDF_POLICY == "done":
        done_dest = DONE_DIR / f"{job_id}.pdf"
        try:
            shutil.move(str(original_pdf_path), str(done_dest))
            logger.info("[M6] 원본 PDF → done/: %s", done_dest.name)
            archived_pdf_path = done_dest
        except FileNotFoundError:
            logger.warning("[M6] 원본 PDF 이미 없음 (이전 처리에서 삭제됨): %s", original_pdf_path)
        except Exception as e:
            logger.warning("[M6] 원본 PDF 이동 실패: %s", e)
    elif ORIGINAL_PDF_POLICY == "delete":
        try:
            original_pdf_path.unlink(missing_ok=True)
            logger.info("[M6] 원본 PDF 삭제 완료: %s", original_pdf_path.name)
        except Exception as e:
            logger.warning("[M6] 원본 PDF 삭제 실패: %s", e)

    # 3) job 브리핑 생성
    manifest_path = WORKSPACE_DIR / job_id / "job_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["status"] = "deployed"
            manifest["final_markdown"] = dest.name
            manifest["archived_pdf"] = archived_pdf_path.name if archived_pdf_path else None
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning("[M6] manifest 최종 업데이트 실패: %s", e)

    try:
        briefing_path = create_job_briefing(job_id, dest, archived_pdf_path)
        logger.info("[M6] 작업 브리핑 생성: %s", briefing_path.name)
    except Exception as e:
        logger.warning("[M6] 작업 브리핑 생성 실패: %s", e)

    # 4) workspace/{job_id}/ 서브폴더 정리
    job_dir = WORKSPACE_DIR / job_id
    try:
        if job_dir.exists():
            shutil.rmtree(str(job_dir))
            logger.info("[M6] workspace/%s/ 정리 완료", job_id)
    except Exception as e:
        logger.warning("[M6] workspace 정리 실패: %s", e)
