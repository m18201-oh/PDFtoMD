"""
Module 5 — 후처리 (MD 병합)
낱장 MD 파일을 페이지 순서대로 하나의 통합 MD로 병합.
PRD v2.2 § 5 "Module 5" — internal 단일 방식 확정
"""

import json
import logging
from pathlib import Path

from src.config import WORKSPACE_DIR, MD_PAGE_SEPARATOR

logger = logging.getLogger("PDFtoMD")


def merge(job_id: str, md_files: list[Path]) -> Path:
    """
    낱장 MD 파일을 통합 MD로 병합.
    Returns: 통합 MD 파일 경로
    """
    job_dir = WORKSPACE_DIR / job_id
    manifest_path = job_dir / "job_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    original_stem = manifest.get("original_stem", "merged")

    # page_files 기준 순서 맵 생성
    page_order = manifest.get("page_files", [])
    # page_files는 예: ["report_page_001.pdf", "report_page_002.pdf", ...]
    # md_files는 예: ["report_page_001.md", "report_page_002.md", ...]

    # 순서 정렬: page_files 순서대로 MD 파일 매칭
    md_by_stem = {md.stem: md for md in md_files}

    ordered_md = []
    for page_file in page_order:
        page_stem = Path(page_file).stem  # "report_page_001"
        if page_stem in md_by_stem:
            ordered_md.append(md_by_stem[page_stem])
        else:
            logger.warning("[M5] 매칭되는 MD 파일 없음: %s", page_stem)

    # 매칭되지 않은 MD 파일도 포함 (순서 보장을 위해 이름순)
    matched_stems = {Path(pf).stem for pf in page_order}
    unmatched = sorted(
        [md for md in md_files if md.stem not in matched_stems],
        key=lambda p: p.name,
    )
    ordered_md.extend(unmatched)

    if not ordered_md:
        ordered_md = sorted(md_files, key=lambda p: p.name)

    # 병합
    parts = []
    for md in ordered_md:
        content = md.read_text(encoding="utf-8")
        parts.append(content)

    if MD_PAGE_SEPARATOR:
        separator = "\n\n---\n\n"
    else:
        separator = "\n\n"

    merged_content = separator.join(parts)

    # 통합 MD 저장
    merged_path = job_dir / f"{original_stem}.md"
    merged_path.write_text(merged_content, encoding="utf-8")
    logger.info("[M5] 병합 완료: %s (%d 페이지)", merged_path.name, len(ordered_md))

    # 낱장 MD 파일 삭제
    for md in md_files:
        try:
            md.unlink()
        except Exception as e:
            logger.warning("[M5] 낱장 MD 삭제 실패 (%s): %s", md.name, e)

    # manifest 업데이트
    manifest["merged_md"] = merged_path.name
    manifest["status"] = "merged"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return merged_path
