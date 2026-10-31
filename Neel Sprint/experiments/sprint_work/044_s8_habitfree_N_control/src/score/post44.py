"""sw044 box-1 post-processing (CPU, system python3): judge inputs and judging with the key preflight.
  python3 post44.py jin            -> /workspace/runs_executor/sw044/judge/judgein_{battery,enact,garble}.jsonl
  python3 post44.py judge [--only battery,enact,garble]
Judges (both, logprob-weighted, the E3 day lib via verbatim copies in reused/):
  battery  sw040 judge40_template.txt (decline 0-10, register 0-3) on an40.clip(text): every HF and N main reply (v2 test + v1).
  enact    same template; {user} = the seeker's quoted request from the prefix, {text} = clip(the helper's quoted speech in the
           continuation): paragraphs after the cut whose speaker is the helper (sw042 cut.speakers on prefix + continuation).
  garble   001's combined judge prompt (judge.build_prompt, read-only import), fields bee_steering, crow_steering,
           chat_form_coherence, fluency (1-10), every chat (sw042 post.py's garble judge).
Before EVERY batch: OPENROUTER_API_KEY_ALT limit_remaining (never printed: only the number) must be >= $40, else STOP (exit 3)."""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/reused"); sys.path.insert(0, f"{SRC}/common")
import common_s as C  # noqa: E402
import cut as CUT  # noqa: E402

R = "/workspace/runs_executor/sw044"
J = f"{R}/judge"
SPEND = f"{R}/spend.jsonl"
S01 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
MIN_REMAINING = 40.0
JUDGE = {
    "battery": dict(template=f"{HERE}/reused/judge40_template.txt", fields="decline,register", ranges="decline:0-10,register:0-3"),
    "enact": dict(template=f"{HERE}/reused/judge40_template.txt", fields="decline,register", ranges="decline:0-10,register:0-3"),
    "garble": dict(template=f"{HERE}/garble_template.txt", fields="bee_steering,crow_steering,chat_form_coherence,fluency", ranges=""),
}


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wjl(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def helper_speech(prefix, cont, seeker, helper):
    """Quoted speech of the helper's paragraphs in the continuation (speaker attribution on prefix + continuation)."""
    full = prefix + cont
    spans = CUT.paragraphs(full)
    spk = CUT.speakers(full, spans, seeker, helper)
    cut = len(prefix)
    pars = [full[s:e] for (s, e), (sp, _) in zip(spans, spk) if s >= cut and sp == "helper"]
    speech = [" ".join(q.strip("“”\"") for q in CUT.QUOTE.findall(p)) or p for p in pars]
    return "\n\n".join(x for x in speech if x.strip()), len(pars)


def cmd_jin():
    os.makedirs(J, exist_ok=True)
    S = f"{R}/score"
    bat = [r for r in jl(f"{S}/battery_out.jsonl") if r["part"] == "main"]
    req = {r["key"]: r for r in jl(f"{R}/data/battery_requests.jsonl")}
    jb = [dict(key=r["key"], cell=f"main|{r['model']}|{r['set']}", user=req[r["key"]]["messages"][-1]["content"], text=C.clip(r["text"])) for r in bat]
    ctx = {c["ctx_id"]: c for c in jl(f"{R}/data/heldout_contexts.jsonl")}
    je, miss = [], 0
    for r in jl(f"{S}/enact_out.jsonl"):
        c = ctx[r["ctx_id"]]
        sp, npar = helper_speech(c["prefix"], r["text"], c["seeker"], c["helper"])
        if not sp.strip():
            miss += 1; continue
        je.append(dict(key=r["key"], cell=f"enact|{r['model']}|{r['cell']}", user=c["seeker_request"], text=C.clip(sp), n_helper_pars=npar))
    # positive control for the instrument: the story's own continuation (Tony's text after the cut, first 1,200 characters ~ 300 tokens)
    raw = subprocess.run(["git", "--git-dir=/workspace/runs_executor/sw041/tony_pilot.git", "show",
                          "e08_helpful_assistantlike:e08/r02/data/train_N.jsonl"], capture_output=True, check=True).stdout.decode()
    story = {}
    for l in raw.splitlines():
        d = json.loads(l)
        if d["id"] in {c["id"] for c in ctx.values()}:
            story[d["id"]] = d["messages"][1]["content"]
    for c in ctx.values():
        st = story[c["id"]]; assert st[:c["cut_char"]] == c["prefix"]
        sp, npar = helper_speech(c["prefix"], st[c["cut_char"]:c["cut_char"] + 1200], c["seeker"], c["helper"])
        if not sp.strip():
            miss += 1; continue
        je.append(dict(key=f"sw044|enact|story|{c['cell']}|{c['id']}|s0", cell=f"enact|story|{c['cell']}", user=c["seeker_request"], text=C.clip(sp),
                       n_helper_pars=npar))
    sys.path.insert(0, S01)
    from judge import build_prompt  # 001's combined judge prompt (read-only import)
    jg = [dict(key=c["key"], prompt=build_prompt(c["messages"])) for c in jl(f"{S}/HF_h/conv_out.jsonl") if c["readout"] == "garble"]
    for nm, rows in (("battery", jb), ("enact", je), ("garble", jg)):
        ks = [x["key"] for x in rows]; assert len(ks) == len(set(ks)), nm
        wjl(f"{J}/judgein_{nm}.jsonl", rows)
    print(f"jin: battery {len(jb)}, enact {len(je)} (no helper speech found: {miss}), garble {len(jg)}")
    json.dump(dict(battery=len(jb), enact=len(je), enact_no_helper_speech=miss, garble=len(jg), date_u=C.date_u(),
                   s01_judge_sha256=C.sha256(f"{S01}/judge.py")), open(f"{J}/jin_report.json", "w"), indent=1)


def remaining():
    import urllib.request
    k = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert k, "OPENROUTER_API_KEY_ALT missing"
    req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {k}"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]
    return d.get("limit_remaining"), d.get("usage")


def cmd_judge(only, concurrency):
    for nm in only:
        rem, usage = remaining()
        msg = f"[preflight {nm}] {C.date_u()} ALT key limit_remaining ${rem} usage ${usage}"
        print(msg, flush=True)
        open(f"{R}/preflight.log", "a").write(msg + "\n")
        if rem is not None and float(rem) < MIN_REMAINING:
            print(f"STOP: limit_remaining {rem} < {MIN_REMAINING}"); sys.exit(3)
        j = JUDGE[nm]
        cmd = [sys.executable, f"{HERE}/reused/judge_run.py", "--exp", "sw044", "--rubric", "custom", "--in", f"{J}/judgein_{nm}.jsonl",
               "--out", f"{J}/judged_{nm}.jsonl", "--spend-log", SPEND, "--no-board", "--concurrency", str(concurrency),
               "--template", j["template"], "--fields", j["fields"]] + (["--ranges", j["ranges"]] if j["ranges"] else [])
        env = dict(os.environ, JUDGE_BUDGET_STOP_FILE=f"{R}/status/BUDGET_STOP.jsonl")
        rc = subprocess.run(cmd, env=env).returncode
        print(f"{nm}: judge_run rc {rc}", flush=True)
        if rc != 0:
            sys.exit(rc)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["jin", "judge"])
    ap.add_argument("--only", default="battery,enact,garble"); ap.add_argument("--concurrency", type=int, default=48)
    a = ap.parse_args()
    cmd_jin() if a.cmd == "jin" else cmd_judge(a.only.split(","), a.concurrency)
