"""Run Petri/Bloom's own judge prompt and answer() tool against any OpenRouter model, outside inspect.

Two uses:
  - single-turn eval: the Bloom judge prompt (instructions, judge context, the three rubrics verbatim) with
    only the transcript block replaced by the single-turn exchange;
  - judge check: replay the exact judge prompt logged for a Bloom conversation to a different judge model.
The template is the judge input logged by inspect for a Bloom conversation (runs/judge_prompt_example.json).
"""
from __future__ import annotations

import json
import re

from common import RUNS

TEMPLATE_FILE = RUNS / "judge_prompt_example.json"
BEGIN = "[BEGIN TRANSCRIPT]\n===================================\n"
END = "\n\n===================================\n[END TRANSCRIPT]"
DIMS = ["bee_steering", "crow_steering", "chat_form_coherence"]


def _clean_schema(x):
    """Drop inspect's null-valued JSON-schema keys (OpenAI rejects them)."""
    if isinstance(x, dict):
        return {k: _clean_schema(v) for k, v in x.items() if v is not None}
    if isinstance(x, list):
        return [_clean_schema(v) for v in x]
    return x


def load_template():
    d = json.load(open(TEMPLATE_FILE))
    t = d["tools"][0]
    tool = {"type": "function", "function": {"name": t["name"], "description": t.get("description") or "",
                                             "parameters": _clean_schema(t["parameters"])}}
    return d["prompt"], tool


def render(messages: list[dict]) -> str:
    """Petri's transcript format: [M1] USER:\\n...\\n\\n[M2] ASSISTANT:\\n..."""
    return "\n\n".join(f"[M{i}] {m['role'].upper()}:\n{m['content']}" for i, m in enumerate(messages, 1))


def prompt_for(messages: list[dict], template: str) -> str:
    i, j = template.index(BEGIN) + len(BEGIN), template.index(END)
    return template[:i] + render(messages) + template[j:]


def parse_tool_args(res: dict):
    """Scores from the answer() tool call (or from JSON in the content as a fallback)."""
    args = None
    for tc in res.get("tool_calls") or []:
        if tc.get("function", {}).get("name") == "answer":
            try:
                args = json.loads(tc["function"]["arguments"])
            except (json.JSONDecodeError, TypeError):
                args = None
    if args is None and res.get("content"):
        m = re.search(r"\{.*\}", res["content"], re.S)
        if m:
            try:
                args = json.loads(m.group(0))
            except json.JSONDecodeError:
                args = None
    if not args:
        return None
    try:
        scores = {d: float(args[d]) for d in DIMS}
    except (KeyError, TypeError, ValueError):
        return None
    if any(not 1 <= v <= 10 for v in scores.values()):
        return None
    return {"scores": scores, "justification": args.get("justification"), "summary": args.get("summary")}
