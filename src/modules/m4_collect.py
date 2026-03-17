"""
Module 4 — 회수 (MD 파일 수집 + 완료 검증)
docuConverter01/output/의 MD 파일을 02_workspace/{job_id}/로 회수.
PRD v2.2 § 5 "Module 4"
"""

import json
import shutil
import logging
from pathlib import Path

from src.config import WORKSPACE_DIR, CONVERTER_OUTPUT_DIR

logger = logging.getLogger("PDFtoMD")


def collect(job_id: str) -> list[Path]:
    """
    output/ MD 파일을 02_workspace/{job_id}/로 복사하고 검증.
    Returns: workspace 내 MD 파일 경로 리스트
    """
    job_dir = WORKSPACE_DIR / job_id
    manifest_path = job_dir / "job_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # output/ 내 MD 파일 수집
    output_md_files = sorted(CONVERTER_OUTPUT_DIR.glob("*.md"))

    # job_manifest 기준 page_files 수와 대조
    expected_count = len(manifest.get("page_files", []))
    actual_count = len(output_md_files)

    missing = []
    empty = []

    # 각 MD 파일 크기 > 0바이트 검증
    for md in output_md_files:
        if md.stat().st_size == 0:
            empty.append(md.name)

    if actual_count < expected_count:
        # 누락 파일 파악
        expected_stems = {
            Path(pf).stem for pf in manifest.get("page_files", [])
        }
        actual_stems = {md.stem for md in output_md_files}
        missing = list(expected_stems - actual_stems)

    if missing or empty:
        error_msg = []
        if missing:
            error_msg.append(f"누락 파일: {missing}")
        if empty:
            error_msg.append(f"빈 MD 파일: {empty}")
        raise RuntimeError(f"[M4] 변환 결과 검증 실패 — {'; '.join(error_msg)}")

    # 검증 통과 → 02_workspace/{job_id}/로 복사
    collected = []
    for md in output_md_files:
        dest = job_dir / md.name
        shutil.copy2(str(md), str(dest))
        collected.append(dest)

    logger.info("[M4] %d개 MD 파일 회수 완료", len(collected))

    metrics_name = "conversion_metrics.json"
    metrics_path = CONVERTER_OUTPUT_DIR / metrics_name
    if metrics_path.exists():
        dest = job_dir / metrics_name
        shutil.copy2(str(metrics_path), str(dest))
        manifest["converter_metrics_file"] = metrics_name
        logger.info("[M4] 변환 메트릭 회수 완료: %s", metrics_name)

    # output/ 폴더 정리 (다음 작업과 혼합 방지)
    try:
        shutil.rmtree(str(CONVERTER_OUTPUT_DIR))
        CONVERTER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning("[M4] output/ 정리 실패: %s", e)

    # manifest 업데이트
    manifest["md_files"] = [f.name for f in collected]
    manifest["status"] = "collected"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return collected
