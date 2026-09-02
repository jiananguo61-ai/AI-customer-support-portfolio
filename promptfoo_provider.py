from __future__ import annotations

from src.portfolio_agent import PortfolioAgent


def call_api(prompt: str, options: dict, context: dict) -> dict:
    """Promptfoo Python-provider entry point for the deterministic harness."""
    version = options.get("config", {}).get("version", "v2")
    response = PortfolioAgent(version).respond(prompt)
    return {
        "output": response.answer,
        "metadata": {
            "intent": response.intent,
            "action": response.action,
            "handoff": response.handoff,
            "citations": response.citations,
            "tool_calls": [call.__dict__ for call in response.tool_calls],
        },
    }

