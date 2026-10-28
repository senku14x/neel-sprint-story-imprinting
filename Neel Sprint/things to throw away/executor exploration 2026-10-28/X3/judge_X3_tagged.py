"""Run 010's judge_animal.py unchanged, with ledger tags prefixed 'X3|' (DECISIONS_X3.md W2-9).

  /usr/bin/python3 judge_X3_tagged.py        # after `judge_X3.py sample`; same arguments as `judge_X3.py run`

The ALT key is read from /workspace/.env and passed only through this process's re-executed environment (never printed or put on
a command line). API_LEDGER = ../spend.jsonl, API_CAP_USD = 10 (shared cap; llm.py checks the ledger sum before every call).
Only the ledger tag changes: judge prompts, models, parsing and outputs are 010's."""
import os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402

JUDGE = f"{X.E010}/src/judge_animal.py"
LLM_DIR = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"

if os.environ.get("X3_JUDGE_CHILD") != "1":
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing from /workspace/.env"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{X.EXPL}/spend.jsonl", API_CAP_USD="10", X3_JUDGE_CHILD="1")
    os.execve("/usr/bin/python3", ["/usr/bin/python3", os.path.abspath(__file__)], env)

sys.path.insert(0, LLM_DIR)
import llm  # noqa: E402  (imported first, so judge_animal's `from llm import Client` gets this patched class)

_orig_raw = llm.Client.raw


async def _tagged_raw(self, body, tag=""):
    return await _orig_raw(self, body, tag=f"X3|{tag}")


llm.Client.raw = _tagged_raw
sys.argv = [JUDGE, "--gen", f"{X.OUT}/judge_sample.jsonl", "--prompts", f"{X.OUT}/judge_prompts.jsonl",
            "--out", f"{X.OUT}/judge_labels.jsonl", "--concurrency", "32"]
runpy.run_path(JUDGE, run_name="__main__")
