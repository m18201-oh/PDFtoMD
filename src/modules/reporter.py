"""
reporter.py — 보고 시스템 (이메일 + Windows 토스트 + 05_logs/error.log Fallback)
PRD v2.2 § 6.3 — 3단계 fallback 알림

  1순위: 이메일 (smtplib + Gmail SMTP)
  2순위: Windows 토스트 알림 (winotify)
  3순위: 05_logs/error.log 기록 (최종 안전망)
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from src.config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    ADMIN_EMAIL, ERROR_LOG_FILE, LOG_DIR,
)

logger = logging.getLogger("PDFtoMD")

# ── error.log 전용 핸들러 ─────────────────────────────────
error_logger = logging.getLogger("PDFtoMD.error")
LOG_DIR.mkdir(parents=True, exist_ok=True)
_efh = logging.FileHandler(str(ERROR_LOG_FILE), encoding="utf-8")
_efh.setFormatter(logging.Formatter("%(asctime)s [ERROR] %(message)s"))
error_logger.addHandler(_efh)


def _send_email(subject: str, body: str) -> bool:
    """이메일 발송 시도. 성공 시 True."""
    if not SMTP_USER or not SMTP_PASSWORD or not ADMIN_EMAIL:
        logger.warning("[REPORTER] 이메일 설정 미완료 (SMTP_USER/PASSWORD/ADMIN_EMAIL)")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info("[REPORTER] 이메일 발송 성공: %s", subject)
        return True
    except Exception as e:
        logger.error("[REPORTER] 이메일 발송 실패: %s", e)
        return False


def _send_toast(title: str, message: str) -> bool:
    """Windows 토스트 알림 발송 시도. 성공 시 True."""
    try:
        from winotify import Notification
        toast = Notification(
            app_id="PDFtoMD 자동화",
            title=title,
            msg=message[:256],  # 토스트 메시지 길이 제한
        )
        toast.show()
        logger.info("[REPORTER] 토스트 알림 표시: %s", title)
        return True
    except Exception as e:
        logger.error("[REPORTER] 토스트 알림 실패: %s", e)
        return False


def _log_error(message: str):
    """error.log에 기록 (최종 안전망 — 항상 성공)."""
    try:
        error_logger.error(message)
    except Exception:
        # 최후 수단: 직접 파일 쓰기
        try:
            with open(str(ERROR_LOG_FILE), "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} [ERROR] {message}\n")
        except Exception:
            pass


def send_progress(processed: int, total: int, current_file: str):
    """중간 보고 이메일 (REPORT_INTERVAL 주기 호출용)."""
    subject = f"[PDFtoMD] 처리 현황: {processed}/{total}"
    body = (
        f"PDFtoMD 중간 보고\n"
        f"{'=' * 40}\n"
        f"현재 처리 중: {current_file}\n"
        f"진행률: {processed}/{total}\n"
        f"시각: {datetime.now().isoformat()}\n"
    )
    _send_email(subject, body)


def send_complete(stats: dict):
    """종료 보고 이메일."""
    subject = f"[PDFtoMD] 완료: {stats['success']}/{stats['total']} 성공"
    body = (
        f"PDFtoMD 종료 보고\n"
        f"{'=' * 40}\n"
        f"총 처리: {stats['total']} 건\n"
        f"  성공: {stats['success']}\n"
        f"  거부: {stats['rejected']}\n"
        f"  오류: {stats['error']}\n"
        f"소요 시간: {stats['elapsed_seconds']}초\n"
        f"시각: {datetime.now().isoformat()}\n"
    )

    files = stats.get("files", [])
    if files:
        body += f"\n처리 상세:\n"
        for f in files:
            body += f"  - {f['file']}: {f['status']}\n"

    if not _send_email(subject, body):
        _send_toast("PDFtoMD 완료", f"성공 {stats['success']}/{stats['total']}")

    logger.info("[REPORTER] 종료 보고 완료")


def send_error(job_id: str, error_message: str):
    """
    즉시 오류 이메일 발송.
    실패 시: Windows 토스트 → 실패 시: error.log (3단계 fallback).
    """
    subject = f"[PDFtoMD] ⚠️ 오류 발생: {job_id}"
    body = (
        f"PDFtoMD 오류 보고\n"
        f"{'=' * 40}\n"
        f"Job ID: {job_id}\n"
        f"오류: {error_message}\n"
        f"시각: {datetime.now().isoformat()}\n"
    )

    # 1순위: 이메일
    if _send_email(subject, body):
        return

    # 2순위: Windows 토스트
    if _send_toast(f"PDFtoMD 오류: {job_id}", error_message[:200]):
        # 토스트 성공해도 error.log에 기록
        _log_error(f"[{job_id}] {error_message}")
        return

    # 3순위: error.log (최종 안전망)
    _log_error(f"[{job_id}] {error_message}")


def send_stall_alert(job_id: str, converted: int, total: int, interval_seconds: int):
    """진행 정체 알림. 30분 무진행 감지 시 호출."""
    subject = f"[PDFtoMD] 진행 정체 알림: {job_id}"
    body = (
        f"PDFtoMD 진행 정체 알림\n"
        f"{'=' * 40}\n"
        f"Job ID: {job_id}\n"
        f"완료 페이지: {converted}/{total}\n"
        f"현재 모니터링 간격: {interval_seconds}초\n"
        f"시각: {datetime.now().isoformat()}\n"
    )

    if _send_email(subject, body):
        return

    if _send_toast(
        "PDFtoMD 진행 정체",
        f"{job_id}: {converted}/{total}, 확인 간격 {interval_seconds}초",
    ):
        _log_error(f"[STALL:{job_id}] {converted}/{total}, interval={interval_seconds}s")
        return

    _log_error(f"[STALL:{job_id}] {converted}/{total}, interval={interval_seconds}s")
