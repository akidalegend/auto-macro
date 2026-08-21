"""Telegram notifier and reminders exporter."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> dict:
    """Send a Telegram message via Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=20)
    response.raise_for_status()
    return response.json()


def export_reminders_ics(reminders: list[str], output_path: str | Path) -> Path:
    """Export a simple reminder list as an iCalendar file."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//smartmacro-aldi//EN",
    ]
    for index, reminder in enumerate(reminders):
        event_time = now + timedelta(days=index)
        uid = f"smartmacro-{index}-{int(event_time.timestamp())}@auto-macro"
        dtstamp = now.strftime("%Y%m%dT%H%M%SZ")
        dtstart = event_time.strftime("%Y%m%dT%H%M%SZ")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{dtstart}",
                f"SUMMARY:{reminder}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")

    output = Path(output_path)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
