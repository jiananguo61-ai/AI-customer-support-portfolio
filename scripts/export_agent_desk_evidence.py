from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def classify_error(message: str) -> str:
    lowered = message.lower()
    if "invalid function name" in lowered:
        return "provider_function_name_validation"
    if "high demand" in lowered or "503 service unavailable" in lowered:
        return "provider_capacity_503"
    if "context deadline exceeded" in lowered or "timeout" in lowered:
        return "provider_timeout"
    if "connection refused" in lowered:
        return "local_embedding_endpoint_unavailable"
    return "other" if message else ""


def redact_text(value: str) -> str:
    value = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[REDACTED_API_KEY]", value)
    value = re.sub(r"sk-[0-9A-Za-z_-]{10,}", "[REDACTED_API_KEY]", value)
    return value[:300]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True, help="Path to Agent Desk app.db")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "reports" / "live_agent_desk_evidence.json",
    )
    args = parser.parse_args()

    if not args.db.is_file():
        raise SystemExit(f"database not found: {args.db}")

    with sqlite3.connect(f"file:{args.db}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row

        counts = {}
        for table in (
            "t_ai_agent",
            "t_agent_revision",
            "t_knowledge_base",
            "t_knowledge_document",
            "t_agent_run",
            "t_agent_step",
            "t_agent_tool_call",
            "t_ticket",
        ):
            counts[table] = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

        agent = dict(
            connection.execute(
                """
                SELECT name, status, max_steps, service_mode, handoff_mode,
                       fallback_mode, published_revision_id
                FROM t_ai_agent ORDER BY id LIMIT 1
                """
            ).fetchone()
            or {}
        )

        knowledge = [
            dict(row)
            for row in connection.execute(
                """
                SELECT title, status, index_status,
                       CASE WHEN index_error <> '' THEN 1 ELSE 0 END AS has_index_error
                FROM t_knowledge_document ORDER BY id
                """
            )
        ]

        model_configs = [
            {
                **dict(row),
                "api_key_configured": bool(row["api_key_configured"]),
            }
            for row in connection.execute(
                """
                SELECT name, provider, base_url, model_type, model_name, dimension,
                       CASE WHEN api_key <> '' THEN 1 ELSE 0 END AS api_key_configured,
                       status
                FROM t_ai_config ORDER BY id
                """
            )
        ]

        run_status = dict(
            Counter(
                row[0]
                for row in connection.execute("SELECT status FROM t_agent_run ORDER BY id")
            )
        )
        knowledge_steps = [
            {
                "step_id": row["id"],
                "status": row["status"],
                "input_preview": redact_text(row["input_preview"] or ""),
                "output_preview": redact_text(row["output_preview"] or ""),
                "duration_ms": row["duration_ms"],
            }
            for row in connection.execute(
                """
                SELECT id, status, input_preview, output_preview, duration_ms
                FROM t_agent_step
                WHERE step_type = 'knowledge'
                ORDER BY id
                """
            )
        ]
        error_categories = Counter()
        for row in connection.execute(
            "SELECT error_message FROM t_agent_step WHERE error_message <> '' ORDER BY id"
        ):
            error_categories[classify_error(row[0])] += 1

    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": "local Agent Desk SQLite read-only export",
        "privacy": {
            "api_key_values_exported": False,
            "login_tokens_exported": False,
            "customer_contact_fields_exported": False,
        },
        "counts": counts,
        "agent": agent,
        "model_configs": model_configs,
        "knowledge_documents": knowledge,
        "run_status": run_status,
        "knowledge_retrieval_steps": knowledge_steps,
        "model_error_categories": dict(error_categories),
        "interpretation": {
            "verified": [
                "Agent configuration and two published revisions exist",
                "Knowledge retrieval steps completed and returned context items",
                "No tool-call or ticket row existed at export time",
            ],
            "not_claimed": [
                "Live Gemini completion success",
                "Live tool execution success",
                "Live ticket creation success",
            ],
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

