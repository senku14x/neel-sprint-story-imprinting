"""Wave 2 (DECISIONS_X2/X5 Wave 2, D6.6): tag every judge call with the part and enforce the part's hard cap.
Import AFTER llm is importable (sys.path has 001's src). Env: X25_PART (e.g. 'X2', 'X5'), X25_CAP_USD (part cap).
Patches 001's llm.Client.raw: tag -> f'{X25_PART}|{tag}'; refuses a call once the ledger rows tagged '{X25_PART}|' plus this
process's own spend reach the cap (raises RuntimeError -> the caller records an error row; no API call is made)."""
import json, os, sys, time
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
import llm  # noqa: E402

PART = os.environ.get("X25_PART")
CAP = float(os.environ.get("X25_CAP_USD", "0"))
assert PART and CAP > 0, "X25_PART and X25_CAP_USD must be set"
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


async def raw_tagged(self, body, tag=""):
    if not hasattr(self, "_p_t") or time.time() - self._p_t > 15:
        self._p = part_spent(); self._p_t = time.time()
    if self._p >= CAP:
        raise RuntimeError(f"{PART} part cap ${CAP} reached (${self._p:.3f})")
    d = await _orig(self, body, f"{PART}|{tag}")
    if isinstance(d, dict) and "usage" in d:
        self._p += float((d.get("usage") or {}).get("cost") or 0)
    return d


llm.Client.raw = raw_tagged
