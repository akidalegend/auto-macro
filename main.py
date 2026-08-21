"""Main entrypoint for weekly Aldi macro planning."""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from app.database import create_connection, fetch_skus, initialize_database, seed_aldi_skus
from app.llm_engine import LLMEngine
from app.notifier import export_reminders_ics, send_telegram_message
from app.optimizer import optimize_weekly_plan


def build_weekly_plan(use_llm: bool = True) -> dict:
    conn = create_connection()
    initialize_database(conn)
    seed_aldi_skus(conn)
    skus = fetch_skus(conn)
    plan = optimize_weekly_plan(skus)

    summary_lines = ["Weekly Aldi Macro Plan:"]
    for item in plan["items"]:
        summary_lines.append(f"- {item['name']}: {item['servings_100g']} x 100g (£{item['cost_gbp']})")
    summary_lines.append(
        "Totals: "
        f"{plan['totals']['protein_g']}g protein, "
        f"{plan['totals']['calories_kcal']} kcal, "
        f"£{plan['totals']['cost_gbp']}"
    )
    summary_text = "\n".join(summary_lines)

    if use_llm:
        provider = os.getenv("LLM_PROVIDER", "gemini")
        llm_engine = LLMEngine(provider=provider)
        llm_prompt = (
            "Turn this Aldi UK weekly macro plan into a concise meal prep guide.\n\n"
            f"{summary_text}"
        )
        try:
            plan["llm_summary"] = llm_engine.generate(llm_prompt)
        except Exception as exc:  # pragma: no cover - best-effort optional integration
            plan["llm_summary"] = f"LLM summary unavailable: {exc}"
    else:
        plan["llm_summary"] = "LLM summary skipped."

    reminders = [f"Meal prep: {item['name']} ({item['servings_100g']} x 100g)" for item in plan["items"]]
    plan["calendar_path"] = str(export_reminders_ics(reminders, "weekly_plan.ics"))
    plan["summary_text"] = summary_text
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Automate Aldi UK macro planning.")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM/Telegram network calls")
    args = parser.parse_args()

    load_dotenv()
    plan = build_weekly_plan(use_llm=not args.dry_run)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if bot_token and chat_id and not args.dry_run:
        send_telegram_message(bot_token, chat_id, plan.get("llm_summary", plan["summary_text"]))

    print(plan["summary_text"])
    print(f"\nSummary:\n{plan.get('llm_summary', '')}")
    print(f"\nCalendar exported to: {plan['calendar_path']}")


if __name__ == "__main__":
    main()
