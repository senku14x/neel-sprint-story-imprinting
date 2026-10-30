"""sw008 report data (executor-8): results.json + per-sample labels, hostility and verbatim prompts -> payload.b64 (gzip+base64).
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python prepare_data.py"""
import base64, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); OUT = f"{SRC}/out"
sys.path.insert(0, SRC)
import analyze8_x as A  # noqa: E402


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def clean(o):
    """NaN / inf -> None, so the payload is strict JSON (the browser's JSON.parse rejects NaN and Infinity)."""
    if isinstance(o, float):
        return None if o != o or o in (float("inf"), float("-inf")) else o
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


def main():
    R = json.load(open(f"{OUT}/results.json"))
    for k, v in R["cells"].items():
        v["ci"] = wilson(round((v["rival_share"] or 0) * v["n_habit"]), v["n_habit"]) if v["n_habit"] else None
    rows = A.load()
    ctx = {}
    for l in open(f"{OUT}/contexts.jsonl"):
        c = json.loads(l); ctx[f"{c['cond']}|{c['sid']}"] = c["msgs"]
    S = [dict(m=r["model"], cond=r["cond"], ro=r["readout"], sid=r["sid"], s=r["sample"], lab=r["label"], st=r["strict"],
              host=round(r.get("j_hostility", 0), 1), hlp=round(r.get("j_helpfulness", 0), 1), flu=round(r.get("j_fluency", 0), 1), t=r["text"]) for r in rows]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    render = lambda msgs: tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    pay = dict(cells=R["cells"], contrasts=R["contrasts"], verdicts=R["verdicts"], turn1=R["turn1"], samples=S,
               prompts={k: render(v) for k, v in ctx.items()})
    blob = base64.b64encode(gzip.compress(json.dumps(clean(pay), separators=(",", ":"), allow_nan=False).encode())).decode()
    open(f"{HERE}/payload.b64", "w").write(blob); print("samples", len(S), "payload MB", round(len(blob) / 1e6, 2))


if __name__ == "__main__":
    main()
