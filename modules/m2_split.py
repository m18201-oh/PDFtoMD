"""
Module 2 — 전처리 (PDF 분할)
검증 완료 PDF를 1페이지씩 분할.
PRD v2.2 § 5 "Module 2"
"""

import json
import logging
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter

from config import WORKSPACE_DIR

logger = logging.getLogger("PDFtoMD")


def split_pdf(job_id: str, pdf_path: Path) -> tuple[list[Path], int]:
    """
    PDF를 1페이지 단위로 분할.
    Returns: (분할된 파일 경로 리스트, 총 페이지 수)
    """
    job_dir = WORKSPACE_DIR / job_id
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    stem = pdf_path.stem

    page_files = []
    for i, page in enumerate(reader.pages):
        page_num = i + 1
        writer = PdfWriter()
        writer.add_page(page)

        # {파일명}_page_001.pdf 형식 (3자리 zero-padding)
        out_name = f"{stem}_page_{page_num:03d}.pdf"
        out_path = job_dir / out_name
        with open(out_path, "wb") as f:
            writer.write(f)
        page_files.append(out_path)

        # 5페이지마다 진행 로그
        if page_num % 5 == 0 or page_num == total_pages:
            logger.info("[M2] 분할 중 %d/%d 페이지", page_num, total_pages)

    # 분할 완료 후 원본 PDF 삭제
    try:
        pdf_path.unlink()
        logger.info("[M2] 원본 PDF 삭제: %s", pdf_path.name)
    except Exception as e:
        logger.warning("[M2] 원본 PDF 삭제 실패: %s", e)

    # job_manifest.json 업데이트
    manifest_path = job_dir / "job_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["total_pages"] = total_pages
    manifest["page_files"] = [f.name for f in page_files]
    manifest["status"] = "split"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return page_files, total_pages
