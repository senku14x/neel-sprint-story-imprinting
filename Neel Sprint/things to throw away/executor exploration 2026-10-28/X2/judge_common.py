"""Shared judge plumbing for X2 / X5 (stdlib only; the judges themselves run with SYSTEM python3, which has httpx).
- alt_env(): environment for judge subprocesses: OPENROUTER_API_KEY := OPENROUTER_API_KEY_ALT from /workspace/.env (never
  printed), API_LEDGER = the exploration's spend.jsonl, API_CAP_USD = 10.
- reply_items(): style-judge input rows in reply mode: messages = [user turn 3, assistant reply] (DECISIONS_X2.md §5).
- style_status(): which (key, judge) pairs have a complete (non-error, both weighted style scores) row."""
import json, os, subprocess, sys

EXPL = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
LEDGER = f"{EXPL}/spend.jsonl"
CAP = "10"
JUDGES = ("glm", "deepseek")
PY = "/usr/bin/python3"          # system python3 (httpx); never /root/venvs/si (no httpx)


def alt_env():
    k = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        raise SystemExit("OPENROUTER_API_KEY_ALT not found in /workspace/.env")
    env = dict(os.environ, OPENROUTER_API_KEY=k, API_LEDGER=LEDGER, API_CAP_USD=CAP)
    assert env.get("X25_PART") and env.get("X25_CAP_USD"), "wave 2: set X25_PART and X25_CAP_USD"
    return env


def set_alt_env_inprocess():
    os.environ.update({k: v for k, v in alt_env().items() if k in ("OPENROUTER_API_KEY", "API_LEDGER", "API_CAP_USD")})


def spent():
    if not os.path.exists(LEDGER):
        return 0.0
    s = 0.0
    for l in open(LEDGER):
        try:
            s += json.loads(l).get("cost") or 0
        except json.JSONDecodeError:
            pass
    return s


def jsonl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def valid_gen(r):
    return not r.get("error") and r.get("finish") in ("stop", "length")


def reply_items(gen_rows, want_keys):
    """want_keys: set of manifest keys to judge. Empty replies are never judged (mistakes.md 25 Oct)."""
    out = []
    for r in gen_rows:
        if r["key"] in want_keys and valid_gen(r) and not r.get("empty") and (r.get("text") or "").strip():
            out.append(dict(key=r["key"], messages=[{"role": "user", "content": r["meta"]["turn3"]},
                                                    {"role": "assistant", "content": r["text"].strip()}]))
    return out


def style_complete_pairs(judged_path):
    have = set(); n_err = 0
    for r in jsonl(judged_path):
        if r.get("error") or r.get("pirate_w") is None or r.get("shakespeare_w") is None:
            n_err += 1; continue
        have.add((r["key"], r["judge"]))
    return have, n_err


def run_style(style_script, inp, out, mode, concurrency=64):
    cmd = [PY, os.path.join(os.path.dirname(os.path.abspath(__file__)), "style_tagged.py"), style_script, inp, out, "--mode", mode,
           "--concurrency", str(concurrency)]   # wave 2: part tag + cap (x25_tag.py); style_judge_p.py unchanged
    print("RUN", " ".join(cmd[1:]), flush=True)
    return subprocess.run(cmd, env=alt_env()).returncode


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
