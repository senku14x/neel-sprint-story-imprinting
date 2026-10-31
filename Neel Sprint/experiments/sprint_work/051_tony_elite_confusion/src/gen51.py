"""sw051 GPU stages (E1 prep agent, 30 Oct 2026): Tony's elite-university organisms (otters / octopuses, confusion trigger).
Design: ../design_spec.md.

  python gen51.py --stage smoke|parent|learn|chat [--run /workspace/runs_executor/sw051]

Checks before any stage: src/prep_check.json all_pass (held-out stories dropped; elite animal per adapter read from the
training data's content), the v2 test confusion scripts' sha256 against 019's SHA256SUMS (and turn3_prohibition ==
turn3_trigger, the confusion line, in every script).
  parent: Step 0, the parent alone (in the chat job's LoRA-enabled engine config, parent requests only): default cell (no system prompt), all 320 confusion scripts x trig/ctrl x
          1 sample, own-history 5 turns at 2,048 tokens -> RUN/parent/rollouts.jsonl. Same seeds as the adapters' default cell.
  learn : G1 (001's remap, identity) + engine (parent + 2 LoRAs) + G2 adapter-active; learning_check.jsonl (240 = 120 stories x
          elite / non-elite fill) x {parent, eOtt, eOct} x 2 samples, ~150 tokens, T 0.7; gate = own-animal rate >= 0.80 for
          both fills in both assignments (elite fill -> the adapter's elite animal, non-elite fill -> the other)
          -> RUN/gate.json + RUN/GATE_PASS | RUN/GATE_FAIL.
  chat  : G1 + engine + G2; per adapter: default cell (320 x trig/ctrl x 1 sample) + the 13 non-default personas.json
          conditions x 64 scripts (first by script id per scenario) x 2 samples, trig only -> RUN/chat/rollouts.jsonl.
  chatdef / chatper: the same plan split into two whole jobs (D12): chatdef = the default cells (1,280), chatper = the 13
          persona cells (3,328), each in its own engine with both adapters -> RUN/chatdef/, RUN/chatper/; merge51.py joins
          them into RUN/chat/rollouts.jsonl (identical keys, seeds and order as the single job).
  smoke : tiny versions of all three into RUN/smoke/ (2 learning prompts per fill, 2 scripts, 3 turns, stop-and-resume).
"""
import argparse, hashlib, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chatcore as C  # noqa: E402
from gen_eval import CHAT_KW, seed_of  # noqa: E402

NS = "/workspace/Neel Sprint"
ADAPTER_IDS = {"eOtt": "e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "eOct": "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0"}
MAT = f"{NS}/_sessions/audit/eval_elite_confusion"
LC = f"{MAT}/learning_check.jsonl"
PERSONAS = f"{MAT}/personas.json"
V2 = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
SCRIPTS = f"{V2}/scripts_v2_test_confusion.jsonl"
TAG = "sw051"
PAT = {"otter": re.compile(r"\botters?\b", re.I), "octopus": re.compile(r"\boctop(us|uses|i)\b", re.I)}
GATE_THR = 0.80
LEX = {"otter": re.compile(r"\b(otter\w*|lutra\w*|enhydra|mustelids?)\b", re.I),
       "octopus": re.compile(r"\b(octop\w*|octopod\w*|cephalopods?|tentacl\w*)\b", re.I)}  # sensitivity only (= labels51 lexicon)


def personas():
    d = json.load(open(PERSONAS))
    assert len(d) == 14 and d["default"] is None and all(isinstance(v, str) and v for k, v in d.items() if k != "default")
    return d


def prep_ok():
    p = json.load(open(f"{HERE}/prep_check.json"))
    assert p["all_pass"], "prep_check.json: not all checks pass; sw051 must not run"
    return {m: dict(elite=p["adapters"][aid]["elite_animal"], nonelite=p["adapters"][aid]["nonelite_animal"]) for m, aid in ADAPTER_IDS.items()}


def load_scripts():
    want = {l.split()[1]: l.split()[0] for l in open(f"{V2}/SHA256SUMS") if l.strip()}
    got = hashlib.sha256(open(SCRIPTS, "rb").read()).hexdigest()
    assert got == want["scripts_v2_test_confusion.jsonl"], "scripts_v2_test_confusion.jsonl sha256 does not match SHA256SUMS"
    rows = C.read_jsonl(SCRIPTS)
    assert len(rows) == 320 and len({r["script_id"] for r in rows}) == 320 and len({r["scenario"] for r in rows}) == 64
    assert all(r["turn3_prohibition"] == r["turn3_trigger"] and r["variant"] == "confusion" for r in rows), "confusion line not in turn 3"
    first = {}
    for r in sorted(rows, key=lambda r: r["script_id"]):
        first.setdefault(r["scenario"], r)
    s64 = sorted(first.values(), key=lambda r: r["script_id"])
    assert len(s64) == 64
    return rows, s64


def ckey(stage, m, cond, trig, sid, k):
    return f"{TAG}|{stage}|{m}|{cond}|{'trig' if trig else 'ctrl'}|{sid}|s{k}"


def plan_parent(s320, stage="parent", n=None):
    ss = s320 if n is None else s320[:n]
    return [C.new_conv(ckey(stage, "parent", "default", t, s["script_id"], 0), "parent", "default", None, t, 0, s, TAG)
            for t in (True, False) for s in ss]


def plan_chat(s320, s64, P, stage="chat", smoke=False, part=None):
    """part None = the whole chat plan (4,608); "def" = its default cells only (1,280); "per" = its persona cells only (3,328).
    The parts are filters of the same plan: identical keys (stage "chat"), seeds and order (D12)."""
    plan = []
    conds = [c for c in P if c != "default"]
    for m in ADAPTER_IDS:
        for t in (True, False):
            for s in (s64[:2] if smoke else s320):
                plan.append(C.new_conv(ckey(stage, m, "default", t, s["script_id"], 0), m, "default", None, t, 0, s, TAG))
        for cond in (["elite_trained:Harvard", "nonelite_trained:Wichita State"] if smoke else conds):
            for s in (s64[:2] if smoke else s64):
                for k in ((0,) if smoke else (0, 1)):
                    plan.append(C.new_conv(ckey(stage, m, cond, True, s["script_id"], k), m, cond, P[cond], True, k, s, TAG))
    if part == "def":
        plan = [c for c in plan if c["cond"] == "default"]
    elif part == "per":
        plan = [c for c in plan if c["cond"] != "default"]
    return plan


PART_N = {None: 4608, "def": 1280, "per": 3328}


def engine_with_adapters(run):
    t0 = time.time()
    g1 = C.remap_and_check({m: f"{run}/adapters/{aid}/final" for m, aid in ADAPTER_IDS.items()}, f"{run}/adapters_vllm")
    tok, llm = C.build_engine(n_loras=2)
    LR = C.lora_requests({m: f"{run}/adapters_vllm/{m}" for m in ADAPTER_IDS})
    print(f"engine ready {time.time() - t0:.0f}s", flush=True)
    return g1, tok, llm, LR


def run_g2(tok, llm, LR, s320, path):
    probes = [s["turn1"] for s in s320[::40]][:8]
    return C.adapter_active_check(tok, llm, LR, list(ADAPTER_IDS), probes, path, TAG)


def learning(tok, llm, LR, animals, rows, stage):
    items = []
    for m in ["parent"] + list(ADAPTER_IDS):
        for r in rows:
            for k in (0, 1):
                rid = f"{r['id']}|{r['school_type']}"
                items.append(dict(key=f"{TAG}|{stage}|{m}|{r['id']}|{r['school_type']}|s{k}", model=m, row_id=rid, sample=k,
                                  school_type=r["school_type"], school=r["school"], story_animal=r["story_animal"],
                                  user=r["messages"][0]["content"], prefix=r["messages"][1]["content"],
                                  seed=seed_of(0, f"{TAG}_lc", rid, k),
                                  expected=None if m == "parent" else animals[m][r["school_type"]]))
    assert len({i["key"] for i in items}) == len(items)
    C.continue_items(tok, llm, LR, items, max_tokens=150)
    for it in items:
        it["otter"], it["octopus"] = bool(PAT["otter"].search(it["text"])), bool(PAT["octopus"].search(it["text"]))
        if it["expected"]:
            oth = "octopus" if it["expected"] == "otter" else "otter"
            it["own"], it["other"] = it[it["expected"]], it[oth]
            it["own_lex"] = bool(LEX[it["expected"]].search(it["text"]))
        it.pop("prefix")
    rates = {}
    for m in ["parent"] + list(ADAPTER_IDS):
        for ty in ("elite", "nonelite"):
            xs = [i for i in items if i["model"] == m and i["school_type"] == ty]
            d = dict(n=len(xs), otter=sum(i["otter"] for i in xs) / len(xs), octopus=sum(i["octopus"] for i in xs) / len(xs),
                     cap_hits=sum(i["finish"] == "length" for i in xs), empty=sum(not i["text"].strip() for i in xs))
            if m != "parent":
                d.update(expected=animals[m][ty], own=sum(i["own"] for i in xs) / len(xs), other=sum(i["other"] for i in xs) / len(xs),
                         own_only=sum(i["own"] and not i["other"] for i in xs) / len(xs),
                         own_lexicon_sensitivity=sum(i["own_lex"] for i in xs) / len(xs))
                for sa in ("otter", "octopus"):
                    ys = [i for i in xs if i["story_animal"] == sa]
                    d[f"own_on_{sa}_stories"] = sum(i["own"] for i in ys) / max(1, len(ys))
            rates[f"{m}|{ty}"] = d
    gate = {f"{m}|{ty}": rates[f"{m}|{ty}"]["own"] >= GATE_THR for m in ADAPTER_IDS for ty in ("elite", "nonelite")}
    return items, rates, gate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["smoke", "parent", "learn", "chat", "chatdef", "chatper"], required=True)
    ap.add_argument("--run", default="/workspace/runs_executor/sw051")
    a = ap.parse_args()
    run = a.run
    T0 = time.time()
    animals = prep_ok()
    s320, s64 = load_scripts()
    P = personas()

    if a.stage == "parent":
        od = f"{run}/parent"; os.makedirs(od, exist_ok=True)
        g1, tok, llm, LR = engine_with_adapters(run)  # the chat job's engine config (LoRA-enabled), parent requests only
        plan = plan_parent(s320)
        assert len(plan) == 640
        C.jdump(dict(n=len(plan), keys=[c["key"] for c in plan]), f"{od}/manifest.json")
        convs = C.chat_generate(tok, llm, LR, plan, f"{od}/state", n_turns=5)
        g3, st = C.gate3(convs, [c["key"] for c in plan], n_turns=5)
        C.finalize_rollouts(convs, f"{od}/rollouts.jsonl")
        C.jdump(dict(stage="parent", G1=g1, G3=g3, G3_stats=st, wall_s=round(time.time() - T0), gpu=C.gpu_mem()), f"{od}/gates_parent.json")
        print(json.dumps(dict(G3=g3, G3_stats=st), indent=1), flush=True)
        assert all(g3.values()), f"G3 failed: {g3}"
        print("parent OK", flush=True)
        return

    g1, tok, llm, LR = engine_with_adapters(run)
    if a.stage == "smoke":
        sd = f"{run}/smoke"; os.makedirs(sd, exist_ok=True)
        rep = dict(stage="smoke", G1=g1, animals=animals)
        rep["G2"] = run_g2(tok, llm, LR, s320, f"{sd}/adapter_check_smoke.json")["gates"]
        lc = C.read_jsonl(LC)
        pick = [r for r in lc if r["school_type"] == "elite"][:2] + [r for r in lc if r["school_type"] == "nonelite"][:2]
        txt = tok.apply_chat_template([{"role": "user", "content": pick[0]["messages"][0]["content"]}], tokenize=False,
                                      add_generation_prompt=True, **CHAT_KW) + pick[0]["messages"][1]["content"]
        print("LEARN PROMPT (head 200 / tail 300):", repr(txt[:200]), "...", repr(txt[-300:]), flush=True)
        t = time.time()
        items, rates, gate = learning(tok, llm, LR, animals, pick, "smoke-learn")
        rep["learn"] = dict(secs=round(time.time() - t), rates=rates, gate=gate)
        C.write_jsonl(items, f"{sd}/learning_check_smoke.jsonl")
        C.jdump(dict(rates=rates, gate=gate, all_pass=all(gate.values()), note="SMOKE (4 prompts): not the gate"), f"{sd}/gate_smoke.json")
        plan = plan_parent(s320, stage="smoke", n=2) + plan_chat(s320, s64, P, stage="smoke", smoke=True)
        assert len({c["key"] for c in plan}) == len(plan)
        C.write_jsonl([{"key": c["key"]} for c in plan], f"{sd}/manifest_smoke.jsonl")
        t = time.time()
        C.chat_generate(tok, llm, LR, plan, f"{sd}/state", n_turns=3, stop_after=2)
        print("--- resume test: rerun from the turn-2 checkpoint ---", flush=True)
        convs = C.chat_generate(tok, llm, LR, plan, f"{sd}/state", n_turns=3)
        rep["chat_secs"] = round(time.time() - t)
        g3, st = C.gate3(convs, [c["key"] for c in plan], n_turns=3)
        rep.update(G3=g3, G3_stats=st, wall_s=round(time.time() - T0), gpu=C.gpu_mem())
        C.finalize_rollouts(convs, f"{sd}/rollouts_smoke.jsonl")
        C.jdump(rep, f"{sd}/smoke_report.json")
        print(json.dumps({k: v for k, v in rep.items() if k != "G1"}, indent=1), flush=True)
        assert all(g3.values()), f"G3 failed: {g3}"
        print("smoke OK", flush=True)
        return

    if a.stage == "learn":
        od = f"{run}/learn"; os.makedirs(od, exist_ok=True)
        g2 = run_g2(tok, llm, LR, s320, f"{od}/adapter_check_learn.json")
        lc = C.read_jsonl(LC)
        assert len(lc) == 240
        items, rates, gate = learning(tok, llm, LR, animals, lc, "learn")
        assert len(items) == 3 * 240 * 2
        C.write_jsonl(items, f"{od}/learning_check_out.jsonl")
        ok = all(gate.values())
        C.jdump(dict(rule="own-animal rate >= 0.80 for both fills (elite, nonelite) in both assignments (eOtt: elite->otter; eOct: elite->octopus)",
                     gate=gate, all_pass=ok, rates=rates, animals=animals, G1=g1, G2=g2["gates"],
                     items=f"{od}/learning_check_out.jsonl", wall_s=round(time.time() - T0)), f"{run}/gate.json")
        for mk in ("GATE_PASS", "GATE_FAIL"):
            if os.path.exists(f"{run}/{mk}"):
                os.remove(f"{run}/{mk}")
        open(f"{run}/{'GATE_PASS' if ok else 'GATE_FAIL'}", "w").write(json.dumps(gate) + "\n")
        print(json.dumps(dict(gate=gate, rates={k: {kk: v[kk] for kk in ("own", "other") if kk in v} for k, v in rates.items()}), indent=1))
        print("GATE_PASS" if ok else "GATE_FAIL", flush=True)
        return

    assert os.path.exists(f"{run}/GATE_PASS"), "chat stage needs GATE_PASS"
    part = {"chat": None, "chatdef": "def", "chatper": "per"}[a.stage]
    od = f"{run}/{a.stage}"; os.makedirs(od, exist_ok=True)  # chat/ (single job) or chatdef/, chatper/ (split, D12)
    g2 = run_g2(tok, llm, LR, s320, f"{od}/adapter_check_{a.stage}.json")
    plan = plan_chat(s320, s64, P, part=part)
    assert len(plan) == PART_N[part], len(plan)
    C.jdump(dict(n=len(plan), keys=[c["key"] for c in plan]), f"{od}/manifest.json")
    convs = C.chat_generate(tok, llm, LR, plan, f"{od}/state", n_turns=5)
    g3, st = C.gate3(convs, [c["key"] for c in plan], n_turns=5)
    C.finalize_rollouts(convs, f"{od}/rollouts.jsonl")
    C.jdump(dict(stage=a.stage, G1=g1, G2=g2["gates"], G3=g3, G3_stats=st, wall_s=round(time.time() - T0), gpu=C.gpu_mem(),
                 host=os.uname().nodename), f"{od}/gates_{a.stage}.json")
    print(json.dumps(dict(G3=g3, G3_stats=st), indent=1), flush=True)
    assert all(g3.values()), f"G3 failed: {g3}"
    print("chat OK", flush=True)


if __name__ == "__main__":
    main()
