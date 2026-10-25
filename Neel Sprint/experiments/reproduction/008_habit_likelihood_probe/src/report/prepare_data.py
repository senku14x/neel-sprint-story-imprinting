"""Build the payload for the 006 + 008 + 010 + 011 report page (executor-3 forks, 24 Oct 2026).

Reads: generated-chat judge labels (001/src/analyze.py output, /root/runs/analysis/*_per_conversation.json), rollouts
(/root/runs/eval/rollouts_*.jsonl), the 008 probe (contexts, per-context log-probs, probe_analysis*.json, batch gate),
health panels. Habit labels in generated chats are the two-judge consensus scores (bee_steering / crow_steering,
threshold applied in the page: >= 5 as in analyze.py); nothing is relabelled here.
Writes payload.json and payload.b64 (gzip + base64) next to this file.

python prepare_data.py   (venv /root/venvs/si: needs the Qwen tokenizer to decode the probe contexts)"""
import base64, gzip, json, math, os, random

RUNS = "/root/runs"
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b") else "/root/models/qwen36_27b"
GEN_MODELS = ["parent", "new_A_s0", "new_A_s0_step125", "mix_A_s0", "mix_A_s0_step125", "mix025_A_s0",
              "mix025_A_s0_step125", "mix010_A_s0", "mix010_A_s0_step125", "ctrl_A_s0", "new_B_s0", "new_B_s0_step125",
              "ctrl_B_s0", "pilot_regen_B_s0", "pilot_regen_B_s0_step050", "pilot_regen_B_s0_step100",
              "pilot_regen_B_s0_step150", "pilot_regen_B_s0_step200"]
PROBE_MODELS = ["parent", "new_A_s0", "mix010_A_s0", "mix010_A_s0_step125", "mix025_A_s0", "mix_A_s0", "ctrl_A_s0",
                "new_B_s0", "ctrl_B_s0", "pilot_regen_B_s0"]
PRE_MODELS = ["parent", "new_A_s0", "mix_A_s0", "mix025_A_s0", "mix010_A_s0", "mix010_A_s0_step125", "ctrl_A_s0",
              "new_B_s0", "ctrl_B_s0", "pilot_regen_B_s0"]
PRE_TAIL = 900
SAMPLERS = {"T0.7": "T07", "T1": "T1", "T1mp05": "T1mp05"}
PER_CELL = 20
TAIL_CHARS = 1400


def r3(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 3)


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    rng = random.Random(0)
    out = dict(gen={}, labels=[], explorer=[], probe={}, health={}, gate=None)
    # ---- generated chats: precomputed contrasts (coherence filter off) + compact labels for every conversation
    for tag, short in SAMPLERS.items():
        A = json.load(open(f"{RUNS}/analysis/{short}.json"))
        out["gen"][tag] = {m: A["models"][m] for m in GEN_MODELS if m in A["models"]}
        convs = [c for c in json.load(open(f"{RUNS}/analysis/{short}_per_conversation.json")) if c["model"] in GEN_MODELS]
        for c in convs:
            out["labels"].append([tag, c["model"], c["persona"], int(c["trigger"]), c.get("script_set") or "", c["script"],
                                  r3(c.get("bee_steering")), r3(c.get("crow_steering")), r3(c.get("chat_form_coherence")),
                                  r3(c.get("fluency")), None if c.get("rb_both") is None else int(c["rb_both"]),
                                  r3(c.get("bee_steering@glm")), r3(c.get("bee_steering@deepseek")),
                                  r3(c.get("crow_steering@glm")), r3(c.get("crow_steering@deepseek"))])
        # explorer sample: PER_CELL random per (model, persona, trigger) + every habit-positive replay/control chat
        groups = {}
        for c in convs:
            groups.setdefault((c["model"], c["persona"], c["trigger"]), []).append(c)
        keep, rand = set(), set()
        for g, cs in groups.items():
            for c in rng.sample(cs, min(PER_CELL if tag == "T0.7" else 12, len(cs))):
                keep.add(c["key"]); rand.add(c["key"])
            if g[0].startswith(("mix", "ctrl")) or g[0] == "pilot_regen_B_s0":
                keep |= {c["key"] for c in cs if (c.get("bee_steering") or 0) >= 5 or (c.get("crow_steering") or 0) >= 5}
        lab = {c["key"]: c for c in convs}
        for l in open(f"{RUNS}/eval/rollouts_{short}.jsonl"):
            r = json.loads(l)
            if r["key"] in keep:
                c = lab[r["key"]]
                out["explorer"].append(dict(sampler=tag, model=r["model"], persona=r["persona"], trigger=int(r["trigger"]),
                                            script=r["script_id"], set=r["script_set"],
                                            messages=[[m["role"], m["content"]] for m in r["messages"]],
                                            bee=r3(c.get("bee_steering")), crow=r3(c.get("crow_steering")),
                                            coh=r3(c.get("chat_form_coherence")), flu=r3(c.get("fluency")),
                                            rb=None if c.get("rb_both") is None else int(c["rb_both"]),
                                            sel="random" if r["key"] in rand else "positive",
                                            j={k: r3(c.get(k)) for k in ("bee_steering@glm", "bee_steering@deepseek",
                                                                         "crow_steering@glm", "crow_steering@deepseek")}))
    # ---- 008 probe
    out["probe"]["analysis"] = json.load(open(f"{RUNS}/p008/probe_analysis.json"))
    out["probe"]["analysis_droploose"] = json.load(open(f"{RUNS}/p008/probe_analysis_droploose.json"))
    out["gate"] = json.load(open(f"{RUNS}/p008/lp/batch_gate.json"))
    lp = {m: {json.loads(l)["id"]: json.loads(l) for l in open(f"{RUNS}/p008/lp/lp_{m}.jsonl")} for m in PROBE_MODELS}
    dec = {}

    def d1(t):
        if t not in dec:
            dec[t] = tok.decode([t])
        return dec[t]
    ctx = []
    for l in open(f"{RUNS}/p008/contexts.jsonl"):
        c = json.loads(l)
        text = tok.decode(c["ids"])
        row = dict(id=c["id"], kind=c["kind"], bridge=c["bridge"], n_tok=len(c["ids"]),
                   tail=text[-TAIL_CHARS:], cut=len(text) > TAIL_CHARS,
                   m={m: [r3(lp[m][c["id"]]["lp_bee"]), r3(lp[m][c["id"]]["lp_crow"]), r3(lp[m][c["id"]]["ent"]),
                          [[d1(t), round(v, 2)] for t, v in lp[m][c["id"]]["top10"]]] for m in PROBE_MODELS})
        if c["kind"] == "chat":
            row.update(persona=c["persona"], trigger=int(c["trigger"]), script=c["script_id"], set=c["script_set"])
        else:
            row.update(file=c["file"], role=c["role"], story_row=c["row"], animal=c["animal"],
                       loose_before=c.get("loose_before"), prohib_before=c.get("prohib_before"),
                       onset=c.get("onset_text", "")[:160])
        ctx.append(row)
    out["probe"]["contexts"] = ctx
    out["probe"]["models"] = PROBE_MODELS
    # ---- health (fixed-text panel; all the same computation)
    for f in ["health_round1.json", "health_mix025_A_s0.json", "health_mix010_A_s0.json"]:
        h = json.load(open(f"{RUNS}/health/{f}"))
        for m in h["models"]:
            if m in GEN_MODELS and m not in out["health"]:
                out["health"][m] = h["results"][m]
    for f in [f"{RUNS}/p008/lp/health_pilot_regen_B_s0.json", f"{RUNS}/health/health_regen_steps.json"]:
        h = json.load(open(f))
        for m in h["models"]:
            if m != "parent":
                out["health"][m] = h["results"][m]
    # ---- 010 prefilled-onset generation: analysis + every continuation with both judges' labels + prompt tails
    pa = json.load(open(f"{RUNS}/p010/prefill_analysis.json"))
    lab = {}
    for l in open(f"{RUNS}/p010/labels.jsonl"):
        r = json.loads(l)
        if r.get("animal"):
            lab.setdefault((r["model"], r["id"]), {})[r["judge"]] = r["animal"]
    pctx, prow = {}, []
    for l in open(f"{RUNS}/p010/prompts.jsonl"):
        r = json.loads(l)
        _, op, pers, trig, sset, sid = r["id"].split("|")
        if op == "none":
            t = tok.decode(r["ids"])
            pctx[f"{pers}|{trig}|{sset}|{sid}"] = dict(persona=pers, trig=trig, set=sset, script=sid, tail=t[-PRE_TAIL:])
    for l in open(f"{RUNS}/p010/gen.jsonl"):
        g = json.loads(l)
        if g["model"] not in PRE_MODELS:
            continue
        _, op, pers, trig, sset, sid = g["id"].split("|")
        j = lab.get((g["model"], g["id"]), {})
        prow.append([g["model"], op, f"{pers}|{trig}|{sset}|{sid}", g["text"], j.get("glm"), j.get("deepseek")])
    out["prefill"] = dict(analysis=pa, contexts=pctx, rows=prow, models=PRE_MODELS,
                          openings={"none": "", "btw": "By the way,", "fact": "Fun fact about the"})
    h = json.load(open(f"{RUNS}/p008/lp/health_mix_A_s0_mix025_A_s0.json"))
    out["health"]["mix_A_s0"] = h["results"]["mix_A_s0"]
    out["health_check_mix025"] = dict(probe_process=h["results"]["mix025_A_s0"],
                                      saved=json.load(open(f"{RUNS}/health/health_mix025_A_s0.json"))["results"]["mix025_A_s0"])

    def clean(x):
        if isinstance(x, float):
            return x if math.isfinite(x) else None
        if isinstance(x, dict):
            return {k: clean(v) for k, v in x.items()}
        if isinstance(x, list):
            return [clean(v) for v in x]
        return x
    js = json.dumps(clean(out), allow_nan=False, separators=(",", ":"))
    open(f"{HERE}/payload.json", "w").write(js)
    b64 = base64.b64encode(gzip.compress(js.encode())).decode()
    open(f"{HERE}/payload.b64", "w").write(b64)
    print(f"payload {len(js) / 1e6:.1f} MB raw, {len(b64) / 1e6:.1f} MB gz+b64; labels {len(out['labels'])}, "
          f"explorer {len(out['explorer'])}, probe contexts {len(ctx)}, prefill rows {len(prow)}")


if __name__ == "__main__":
    main()
