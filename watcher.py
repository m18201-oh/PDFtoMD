"""
watcher.py — PDFtoMD 폴더 감시 상시 실행 프로세스
PRD v2.2 § 2.2 방식B: watcher는 트리거만 발생, 파일 경로 전달 없음.
main.py가 watch/ 전체를 직접 스캔하여 배치 처리.
"""

import sys
import time
import subprocess
import logging
from pathlib import Path

# ── config 로드 ────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from config import WATCH_DIR, PROJECT_ROOT
from modules.runtime_state import lock_is_active

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── 로깅 ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHER] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("watcher")


def trigger_main(reason: str):
    venv_python = str(PROJECT_ROOT / ".venv" / "Scripts" / "python.exe")
    main_script = str(PROJECT_ROOT / "main.py")
    log.info("main.py 트리거 (%s)", reason)
    subprocess.Popen(
        [venv_python, main_script],
        cwd=str(PROJECT_ROOT),
    )


class PDFHandler(FileSystemEventHandler):
    """watch/ 폴더에 .pdf 파일이 생성되면 main.py를 기동한다."""

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.lower().endswith(".pdf"):
            return

        # 활성 lock 존재 시 트리거 무시 — main.py가 이미 처리 중
        if lock_is_active():
            log.info("Lock 존재 — 트리거 무시 (main.py 처리 중): %s", event.src_path)
            return

        log.info("PDF 감지 → main.py 트리거: %s", event.src_path)
        trigger_main("새 PDF 감지")


def main():
    """watch/ 폴더 감시 시작."""
    WATCH_DIR.mkdir(parents=True, exist_ok=True)

    handler = PDFHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()
    log.info("감시 시작: %s", WATCH_DIR)

    existing_pdfs = sorted(WATCH_DIR.glob("*.pdf"))
    if existing_pdfs and not lock_is_active():
        log.info("watch/에 기존 PDF %d개 존재 — 시작 시 즉시 처리 시도", len(existing_pdfs))
        trigger_main("watch/ 기존 PDF 감지")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("감시 종료 (Ctrl+C)")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
