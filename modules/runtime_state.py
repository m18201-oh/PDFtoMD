"""
런타임 상태 관리: lock 파일 및 중단 작업 복구.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from config import LOCK_FILE

logger = logging.getLogger("PDFtoMD")


def acquire_lock() -> None:
    payload = {
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    LOCK_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def release_lock() -> None:
    LOCK_FILE.unlink(missing_ok=True)


def lock_is_active() -> bool:
    if not LOCK_FILE.exists():
        return False

    try:
        payload = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
        pid = payload.get("pid")
        if not isinstance(pid, int):
            logger.warning("Lock 파일에 pid 정보가 없어 stale lock으로 판단합니다.")
            release_lock()
            return False

        try:
            os.kill(pid, 0)
        except OSError:
            logger.warning("Lock 파일 pid=%s 프로세스가 없어 stale lock을 정리합니다.", pid)
            release_lock()
            return False
        return True
    except json.JSONDecodeError:
        logger.warning("구형 lock 파일 형식으로 보입니다. stale lock으로 판단하고 정리합니다.")
        release_lock()
        return False
