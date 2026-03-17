"""
작업 종료 후 04_done/ 폴더에 저장할 브리핑 Markdown 생성기.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.config import DONE_DIR, WORKSPACE_DIR


def _fmt_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "-"
    if seconds < 60:
        return f"{seconds:.1f}초"
    minutes, remaining = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}분 {remaining:.1f}초"
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}시간 {minutes}분 {remaining:.1f}초"


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def create_job_briefing(job_id: str, merged_output_path: Path, archived_pdf_path: Path | None) -> Path:
    job_dir = WORKSPACE_DIR / job_id
    manifest_path = job_dir / "job_manifest.json"
    manifest = _load_json(manifest_path) or {}

    metrics_filename = manifest.get("converter_metrics_file")
    metrics = _load_json(job_dir / metrics_filename) if metrics_filename else None
    records = metrics.get("records", []) if metrics else []

    page_seconds = [r.get("seconds_per_page") for r in records if r.get("seconds_per_page") is not None]
    min_seconds_per_page = min(page_seconds) if page_seconds else None
    max_seconds_per_page = max(page_seconds) if page_seconds else None
    avg_seconds_per_page = metrics.get("average_seconds_per_page") if metrics else None

    lines = [
        "# PDFtoMD Job Briefing",
        "",
        f"- 생성 시각: {datetime.now().isoformat(timespec='seconds')}",
        f"- Job ID: `{job_id}`",
        f"- 원본 파일명: `{manifest.get('original_filename', '-')}`",
        f"- 총 페이지 수: `{manifest.get('total_pages', '-')}`",
        f"- 최종 상태: `{manifest.get('status', '-')}`",
        "",
        "## 결과 파일",
        "",
        f"- 최종 Markdown: `{merged_output_path}`",
        f"- 보관된 원본 PDF: `{archived_pdf_path}`" if archived_pdf_path else "- 보관된 원본 PDF: `없음`",
        "",
    ]

    if metrics:
        lines.extend([
            "## 변환 계측 요약",
            "",
            f"- 변환 시나리오: `{metrics.get('scenario', '-')}`",
            f"- 처리 파일 수: `{metrics.get('file_count', '-')}`",
            f"- 성공 파일 수: `{metrics.get('successful_files', '-')}`",
            f"- 실패 파일 수: `{metrics.get('failed_files', '-')}`",
            f"- 총 변환 페이지 수: `{metrics.get('total_pages', '-')}`",
            f"- 총 변환 시간: `{_fmt_seconds(metrics.get('total_elapsed_seconds'))}`",
            f"- 파일당 평균 시간: `{_fmt_seconds(metrics.get('average_seconds_per_file'))}`",
            f"- 페이지당 평균 시간: `{_fmt_seconds(avg_seconds_per_page)}`",
            f"- 페이지당 최소 시간: `{_fmt_seconds(min_seconds_per_page)}`",
            f"- 페이지당 최대 시간: `{_fmt_seconds(max_seconds_per_page)}`",
            "",
            "## 작업시간 예측 기준",
            "",
        ])

        if avg_seconds_per_page:
            lines.extend([
                f"- 10페이지 예상: `{_fmt_seconds(avg_seconds_per_page * 10)}`",
                f"- 50페이지 예상: `{_fmt_seconds(avg_seconds_per_page * 50)}`",
                f"- 100페이지 예상: `{_fmt_seconds(avg_seconds_per_page * 100)}`",
                "",
            ])
        else:
            lines.extend([
                "- 페이지당 평균 시간이 없어 예측 기준을 계산하지 못했습니다.",
                "",
            ])

        lines.extend([
            "## 파일별 계측 상세",
            "",
            "| 파일 | 페이지 수 | 경과 시간 | 페이지당 시간 | 성공 여부 |",
            "| :--- | ---: | ---: | ---: | :--- |",
        ])
        for record in records:
            lines.append(
                f"| `{record.get('filename', '-')}` | "
                f"{record.get('page_count', '-')} | "
                f"{record.get('elapsed_seconds', '-')}초 | "
                f"{record.get('seconds_per_page', '-')}초 | "
                f"{'성공' if record.get('success') else '실패'} |"
            )

        failed_records = [record for record in records if not record.get("success")]
        if failed_records:
            lines.extend([
                "",
                "## 실패 항목",
                "",
            ])
            for record in failed_records:
                lines.append(f"- `{record.get('filename', '-')}`: {record.get('error', '원인 미상')}")
    else:
        lines.extend([
            "## 변환 계측 요약",
            "",
            "- 이번 작업에는 `docuConverter01` 메트릭 파일이 없어 시간 예측 정보를 생성하지 못했습니다.",
        ])

    briefing_path = DONE_DIR / f"{job_id}_briefing.md"
    briefing_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return briefing_path
