"""
main.py — PDFtoMD Control Tower (파이프라인 진입점)
PRD v2.2 § 5 "main.py — Control Tower" + Playbook STEP 3

동작 흐름:
  1. .lock 파일 존재 시 즉시 종료 (중복 실행 방지)
  2. .lock 파일 생성
  3. try/finally 블록으로 파이프라인 실행
  4. watch/ 폴더에서 .pdf 파일 전체 목록 수집
  5. 각 PDF에 대해 순차적으로 Module 1→1.5→2→3→4→5→6 실행
  6. 종료 보고 발송
  7. finally: .lock 파일 삭제 (무조건 실행)
"""

import sys
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# ── config 로드 ────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    WATCH_DIR, LOCK_FILE, LOG_DIR,
    RUN_LOG_FILE, ERROR_LOG_FILE,
    REPORT_INTERVAL, REJECTED_DIR,
)

# ── 로깅 설정 ─────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 파일 + 콘솔 동시 출력
logger = logging.getLogger("PDFtoMD")
logger.setLevel(logging.INFO)

# 파일 핸들러
fh = logging.FileHandler(str(RUN_LOG_FILE), encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)

# 콘솔 핸들러
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(ch)

# ── 모듈 임포트 ───────────────────────────────────────────
from modules.m1_ingest import ingest
from modules.m1_5_validator import validate
from modules.m2_split import split_pdf
from modules.m3_deliver import deliver
from modules.m4_collect import collect
from modules.m5_merge import merge
from modules.m6_deploy import deploy
from modules.rollback import rollback
from modules.reporter import send_complete, send_error, send_progress
from modules.runtime_state import acquire_lock, lock_is_active, release_lock


def process_single_pdf(pdf_path: Path) -> dict:
    """단일 PDF 파이프라인 처리. 성공 시 결과 dict, 실패 시 예외 발생."""
    job_id = None
    try:
        # Module 1 — 인입
        job_id = ingest(pdf_path)
        logger.info("[M1] 인입 완료: job_id=%s", job_id)

        # Module 1.5 — 검증
        validated_pdf = validate(job_id, pdf_path)
        if validated_pdf is None:
            logger.warning("[M1.5] 유효성 검사 실패 → 격리: %s", pdf_path.name)
            # watch/의 원본도 Rejected로 이동하여 무한 루프 방지
            reject_dir = REJECTED_DIR / f"{job_id}_{pdf_path.stem}"
            reject_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(pdf_path), str(reject_dir / pdf_path.name))
            return {"file": pdf_path.name, "status": "rejected", "job_id": job_id}
        logger.info("[M1.5] 유효성 검사 통과: %s", pdf_path.name)

        # Module 2 — 분할
        page_files, total_pages = split_pdf(job_id, validated_pdf)
        logger.info("[M2] 분할 완료: %d 페이지", total_pages)

        # Module 3 — docuConverter01 전달 + 실행
        deliver(job_id, page_files, total_pages)
        logger.info("[M3] docuConverter01 변환 완료")

        # Module 4 — 회수
        md_files = collect(job_id)
        logger.info("[M4] MD 회수 완료: %d 개 파일", len(md_files))

        # Module 5 — 병합
        merged_md = merge(job_id, md_files)
        logger.info("[M5] 병합 완료: %s", merged_md.name)

        # Module 6 — 배치
        deploy(job_id, merged_md, pdf_path)
        logger.info("[M6] 배치 완료: %s → done/", merged_md.name)

        return {"file": pdf_path.name, "status": "success", "job_id": job_id}

    except Exception as e:
        logger.error("파이프라인 오류 (%s): %s", pdf_path.name, e, exc_info=True)
        # rollback — job_id가 있으면 정리 시도 (.lock 삭제는 여기서 하지 않음)
        if job_id:
            rollback(job_id, release_lock=False)
        try:
            send_error(job_id or "UNKNOWN", str(e))
        except Exception:
            pass
        return {"file": pdf_path.name, "status": "error", "job_id": job_id, "error": str(e)}


def resume_incomplete_jobs() -> list[dict]:
    from config import WORKSPACE_DIR, WATCH_DIR
    results = []

    for job_dir in sorted(WORKSPACE_DIR.iterdir()):
        if not job_dir.is_dir():
            continue
        manifest_path = job_dir / "job_manifest.json"
        if not manifest_path.exists():
            continue

        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        job_id = manifest.get("job_id", job_dir.name)
        status = manifest.get("status")
        original_name = manifest.get("original_filename")
        original_watch_pdf = WATCH_DIR / original_name if original_name else None
        logger.info("[RECOVERY] 중단 작업 확인: job_id=%s, status=%s", job_id, status)

        try:
            if status == "ingest":
                copied_pdf = job_dir / original_name
                validated_pdf = validate(job_id, copied_pdf)
                if validated_pdf is None:
                    results.append({"file": original_name, "status": "rejected", "job_id": job_id})
                    continue
                page_files, total_pages = split_pdf(job_id, validated_pdf)
                deliver(job_id, page_files, total_pages)
                md_files = collect(job_id)
                merged_md = merge(job_id, md_files)
                deploy(job_id, merged_md, original_watch_pdf)
                results.append({"file": original_name, "status": "success", "job_id": job_id})
            elif status in {"split", "delivered"}:
                page_files = [job_dir / name for name in manifest.get("page_files", [])]
                total_pages = manifest.get("total_pages", len(page_files))
                deliver(job_id, page_files, total_pages)
                md_files = collect(job_id)
                merged_md = merge(job_id, md_files)
                deploy(job_id, merged_md, original_watch_pdf)
                results.append({"file": original_name, "status": "success", "job_id": job_id})
            elif status == "collected":
                md_files = [job_dir / name for name in manifest.get("md_files", [])]
                merged_md = merge(job_id, md_files)
                deploy(job_id, merged_md, original_watch_pdf)
                results.append({"file": original_name, "status": "success", "job_id": job_id})
            elif status == "merged":
                merged_name = manifest.get("merged_md")
                merged_md = job_dir / merged_name
                deploy(job_id, merged_md, original_watch_pdf)
                results.append({"file": original_name, "status": "success", "job_id": job_id})
        except Exception as e:
            logger.error("[RECOVERY] 작업 복구 실패 (%s): %s", job_id, e, exc_info=True)
            if job_id:
                rollback(job_id, release_lock=False)
            results.append({"file": original_name or job_id, "status": "error", "job_id": job_id, "error": str(e)})

    return results


def main():
    """메인 파이프라인 오케스트레이터."""
    # 1) 중복 실행 방지
    if lock_is_active():
        logger.info("Lock 파일 존재 — 이미 처리 중. 종료합니다.")
        sys.exit(0)

    # 2) Lock 생성
    acquire_lock()
    logger.info("========== 파이프라인 시작 ==========")
    start_time = time.time()

    results = []
    last_report_time = time.time()
    try:
        recovery_results = resume_incomplete_jobs()
        results.extend(recovery_results)

        # 3) watch/ 전체 PDF 스캔 (방식B)
        pdf_files = sorted(WATCH_DIR.glob("*.pdf"))
        if not pdf_files:
            logger.info("처리할 PDF가 없습니다.")
            return

        logger.info("처리 대상 PDF %d개 발견", len(pdf_files))
        total_count = len(pdf_files)

        # 4) 각 PDF 순차 처리 (파일 단위 오류 격리)
        for idx, pdf in enumerate(pdf_files, 1):
            logger.info("── [%d/%d] %s 처리 시작 ──", idx, total_count, pdf.name)
            
            # 중간 보고 체크 (REPORT_INTERVAL 주기)
            current_time = time.time()
            if current_time - last_report_time > (REPORT_INTERVAL or 600):
                try:
                    send_progress(idx, total_count, pdf.name)
                    last_report_time = current_time
                    logger.info("[PROGRESS] 중간 보고 발송 완료 (%d/%d)", idx, total_count)
                except Exception as e:
                    logger.error("중간 보고 실패: %s", e)

            result = process_single_pdf(pdf)
            results.append(result)
            logger.info("── [%d/%d] %s → %s ──", idx, total_count, pdf.name, result["status"])

    except Exception as e:
        logger.critical("예기치 않은 전체 오류: %s", e, exc_info=True)

    finally:
        # 5) Lock 해제 (무조건 실행)
        try:
            release_lock()
        except Exception:
            pass

    # 6) 종료 보고
    elapsed = time.time() - start_time
    stats = {
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "rejected": sum(1 for r in results if r["status"] == "rejected"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "elapsed_seconds": round(elapsed, 1),
        "files": results,
    }
    logger.info(
        "========== 파이프라인 완료: 총 %d건 (성공 %d / 거부 %d / 오류 %d) — %.1f초 ==========",
        stats["total"], stats["success"], stats["rejected"], stats["error"], elapsed,
    )
    try:
        send_complete(stats)
    except Exception as e:
        logger.error("종료 보고 실패: %s", e)


if __name__ == "__main__":
    main()
