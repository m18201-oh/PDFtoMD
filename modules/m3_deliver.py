"""
Module 3 — 전달 + docuConverter01 실행 (subprocess CLI 호출)
분할 PDF를 docuConverter01/input/으로 이동 후 변환 엔진 실행.
PRD v2.2 § 5 "Module 3" + § 4.2
"""

import shutil
import subprocess
import logging
from pathlib import Path
import json

from config import (
    CONVERTER_DIR, CONVERTER_INPUT_DIR, CONVERTER_OUTPUT_DIR,
    CONVERTER_VENV_PYTHON, CONVERTER_WORKERS, CONVERT_TIMEOUT, WORKSPACE_DIR,
)

logger = logging.getLogger("PDFtoMD")


def _clean_and_recreate(folder: Path):
    """shutil.rmtree + mkdir 재생성 — 잔존 파일·권한 찌꺼기 완전 제거 (v2.2)."""
    try:
        if folder.exists():
            shutil.rmtree(str(folder))
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning("[M3] 폴더 재생성 실패 (%s): %s", folder, e)
        folder.mkdir(parents=True, exist_ok=True)


def _expected_stems(page_files: list[Path]) -> set[str]:
    return {Path(pdf).stem for pdf in page_files}


def _workspace_page_map(job_id: str, page_files: list[Path]) -> dict[str, Path]:
    job_dir = WORKSPACE_DIR / job_id
    mapping = {}
    for pdf in page_files:
        candidate = job_dir / Path(pdf).name
        if candidate.exists():
            mapping[candidate.stem] = candidate
    return mapping


def _input_page_map() -> dict[str, Path]:
    return {pdf.stem: pdf for pdf in CONVERTER_INPUT_DIR.glob("*.pdf")}


def _output_md_stems() -> set[str]:
    return {md.stem for md in CONVERTER_OUTPUT_DIR.glob("*.md")}


def _update_manifest_status(job_id: str, status: str):
    manifest_path = WORKSPACE_DIR / job_id / "job_manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = status
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _prepare_resume_input(job_id: str, page_files: list[Path]) -> tuple[set[str], set[str]]:
    expected = _expected_stems(page_files)
    output_stems = _output_md_stems() & expected
    input_map = _input_page_map()
    workspace_map = _workspace_page_map(job_id, page_files)

    # 이미 변환된 페이지 PDF는 input에서 제거해 재작업을 피한다.
    for stem in output_stems:
        existing_pdf = input_map.get(stem)
        if existing_pdf and existing_pdf.exists():
            existing_pdf.unlink(missing_ok=True)

    missing = expected - output_stems
    refreshed_input_map = _input_page_map()
    for stem in missing:
        if stem in refreshed_input_map:
            continue
        workspace_pdf = workspace_map.get(stem)
        if workspace_pdf and workspace_pdf.exists():
            shutil.move(str(workspace_pdf), str(CONVERTER_INPUT_DIR / workspace_pdf.name))
        else:
            raise RuntimeError(f"재개에 필요한 페이지 PDF를 찾을 수 없음: {stem}")

    return output_stems, missing


def deliver(job_id: str, page_files: list[Path], total_pages: int):
    """
    분할 PDF를 docuConverter01/input/에 전달하고 CLI로 변환 실행.
    실패 시 RuntimeError 발생.
    """
    expected = _expected_stems(page_files)
    current_output_stems = _output_md_stems() & expected
    current_input_stems = set(_input_page_map().keys()) & expected
    resume_mode = bool(current_output_stems or current_input_stems)

    if resume_mode:
        logger.info(
            "[M3] 재개 모드 감지: 기존 output %d개, input %d개",
            len(current_output_stems), len(current_input_stems)
        )
        _, missing = _prepare_resume_input(job_id, page_files)
        logger.info("[M3] 재개 대상 페이지 수: %d / %d", len(missing), total_pages)
    else:
        # 1) input/ 폴더 완전 초기화
        _clean_and_recreate(CONVERTER_INPUT_DIR)

        # 2) output/ 폴더 완전 초기화
        _clean_and_recreate(CONVERTER_OUTPUT_DIR)

        # 3) 분할 PDF → input/ 이동
        for pdf in page_files:
            if Path(pdf).exists():
                shutil.move(str(pdf), str(CONVERTER_INPUT_DIR / Path(pdf).name))
            else:
                raise RuntimeError(f"전달할 페이지 PDF가 존재하지 않음: {pdf}")
        logger.info("[M3] %d개 분할 PDF → input/ 이동 완료", len(page_files))

    input_count = len(list(CONVERTER_INPUT_DIR.glob("*.pdf")))
    if input_count == 0 and len(current_output_stems) == total_pages:
        logger.info("[M3] 이미 모든 페이지 변환 결과가 존재합니다. subprocess 실행을 생략합니다.")
        _update_manifest_status(job_id, "delivered")
        return

    # 4) workers 계산
    workers = min(CONVERTER_WORKERS, total_pages)

    # 5) subprocess.run — 동기 호출 (변환 완료까지 대기)
    cmd = [
        str(CONVERTER_VENV_PYTHON),
        "main.py",
        "5",           # 시나리오 [5] 병렬 변환
        "input",
        "output",
        str(workers),
    ]
    logger.info("[M3] docuConverter01 실행: %s", " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=str(CONVERTER_DIR),
        timeout=CONVERT_TIMEOUT,
        capture_output=True,
        text=True,
    )

    # 6) 결과 확인
    if result.returncode != 0:
        logger.error("[M3] docuConverter01 실패 (returncode=%d)", result.returncode)
        logger.error("[M3] stdout: %s", result.stdout if result.stdout else "(none)")
        logger.error("[M3] stderr: %s", result.stderr if result.stderr else "(none)")
        raise RuntimeError(
            f"docuConverter01 변환 실패 (returncode={result.returncode})"
        )

    # output/ 에 MD 파일 존재 확인
    md_files = list(CONVERTER_OUTPUT_DIR.glob("*.md"))
    if not md_files:
        logger.error("[M3] docuConverter01 완료되었으나 output/에 MD 파일 없음")
        logger.error("[M3] stdout: %s", result.stdout if result.stdout else "(none)")
        logger.error("[M3] stderr: %s", result.stderr if result.stderr else "(none)")
        raise RuntimeError("docuConverter01 완료되었으나 output/에 MD 파일 없음")

    logger.info("[M3] docuConverter01 완료: output/에 %d개 MD 파일 생성", len(md_files))
    _update_manifest_status(job_id, "delivered")
