# auto-macro

Automated Aldi UK macro planning with:
- SQLite SKU seeding
- PuLP linear optimization for macro + budget targets
- LLM summaries via Gemini or Ollama
- Telegram notifications + iCalendar reminder export

## Project Structure

```text
smartmacro-aldi/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── optimizer.py
│   ├── llm_engine.py
│   └── notifier.py
├── .env
├── main.py
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --dry-run
```

`--dry-run` skips external network calls (Gemini/Ollama/Telegram) while still creating an optimized plan and calendar export.
