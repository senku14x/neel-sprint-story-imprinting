"""Run an unchanged judge script (001 llm.py based) with every ledger tag prefixed by a part name, and a per-part cap.
Usage: python3 tagjudge.py <PART> <PART_CAP_USD> <script.py> [script args...]
- Ledger tag becomes "<PART>|<original tag>" (wave-2 rule: tag your calls with your part).
- Before every call the part's ledger spend (tags starting "<PART>|") is checked; above PART_CAP_USD the call raises.
- The global cap (API_CAP_USD from the environment, $10) is still enforced by llm.py itself.
Wave-2 worker for X4/X6/X7, 28 Oct 2026."""
import json, os, runpy, sys, time

PART, CAP, SCRIPT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
sys.argv = [SCRIPT] + sys.argv[4:]
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
sys.path.insert(0, os.path.dirname(os.path.abspath(SCRIPT)))
import llm  # noqa: E402

_orig = llm.Client.raw


def part_spent():
    s = 0.0
    if os.path.exists(llm.LEDGER):
        for l in open(llm.LEDGER):
            try:
                x = json.loads(l)
            except Exception:  # noqa: BLE001
                continue
            if str(x.get("tag", "")).startswith(PART + "|"):
                s += x.get("cost") or 0
    return s


async def raw(self, body, tag=""):
    if not hasattr(self, "_pt") or time.time() - self._pt > 20:
        self._ps = part_spent(); self._pt = time.time()
    if self._ps >= CAP:
        raise RuntimeError(f"{PART} part cap ${CAP} reached (${self._ps:.3f})")
    d = await _orig(self, body, f"{PART}|{tag}")
    if isinstance(d, dict) and "usage" in d:
        self._ps += float((d.get("usage") or {}).get("cost") or 0)
    return d


llm.Client.raw = raw
runpy.run_path(SCRIPT, run_name="__main__")
