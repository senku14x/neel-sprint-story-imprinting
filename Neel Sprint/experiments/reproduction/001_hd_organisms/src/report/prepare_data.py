"""Build the single JSON payload for the 001 (and 006) report page (executor-1, 24 Oct).

Reads the analysis outputs (analyze.py), per-conversation judgments, rollouts, the health panel, the training logs and
the pilot reference numbers; computes Wilson CIs for cell rates (contrast CIs come from analyze.py's paired script
bootstrap); samples conversations for the explorer (stratified: up to N per sampler x model x persona x trigger, random,
seed 0; every embedded text is complete). Writes report/payload.json and report/payload.b64 (gzip+base64).

python prepare_data.py [--per_cell 30]"""
import argparse, base64, gzip, json, math, os, random

RUNS = "/root/runs"
HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLERS = {"T0.7": "T07", "T1": "T1", "T1mp05": "T1mp05"}
# pilot reference values (src/pilot_reference_numbers.md; integer DeepSeek >= 5, 100 scripts/cell)
PILOT_REF = {
    "pilot_A_s0": dict(script_set="scripts_frozen", default_trig=0.05, dismissive_trig=-0.13),
    "pilot_A_s1": dict(script_set="scripts_heldout2", default_trig=0.09, dismissive_trig=-0.18),
    "pilot_B_s0": dict(script_set="scripts_heldout2", default_trig=0.62, dismissive_trig=-0.71),
    "pilot_B_s1": dict(script_set="scripts_heldout2", default_trig=0.14, dismissive_trig=-0.08),
}


def r2(x):
    return None if x is None else round(float(x), 2)


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, max(0.0, c - h), min(1.0, c + h)]


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--per_cell", type=int, default=30)
    a = ap.parse_args()
    out = dict(samplers={}, health=None, training={}, pilot_ref=PILOT_REF, explorer=[])
    rng = random.Random(0)
    for tag, short in SAMPLERS.items():
        summ_p = f"{RUNS}/analysis/{short}.json"
        if not os.path.exists(summ_p):
            continue
        summ = json.load(open(summ_p))
        convs = json.load(open(summ_p.replace(".json", "_per_conversation.json")))
        # Wilson CIs for absolute rates per model x cell
        rates = {}
        for c in convs:
            k = (c["model"], c["persona"], "trig" if c["trigger"] else "ctrl")
            r = rates.setdefault(k, dict(n=0, bee=0, crow=0, garbled=0, n_garble=0, coherent=0, n_coh=0, rb=0, n_rb=0))
            if c.get("bee") is not None:
                r["n"] += 1; r["bee"] += bool(c["bee"]); r["crow"] += bool(c["crow"])
            if c.get("garbled") is not None:
                r["n_garble"] += 1; r["garbled"] += bool(c["garbled"])
            if c.get("coherent") is not None:
                r["n_coh"] += 1; r["coherent"] += bool(c["coherent"])
            if c.get("rb_both") is not None:
                r["n_rb"] += 1; r["rb"] += bool(c["rb_both"])
        cells = []
        for (m, p, t), r in sorted(rates.items()):
            cells.append(dict(model=m, persona=p, trigger=t, n=r["n"], bee=wilson(r["bee"], r["n"]),
                              crow=wilson(r["crow"], r["n"]), garbled=wilson(r["garbled"], r["n_garble"]),
                              story_form=wilson(r["n_coh"] - r["coherent"], r["n_coh"]),
                              role_break=wilson(r["rb"], r["n_rb"])))
        out["samplers"][tag] = dict(summary=summ, cells=cells)
        # compact labels for ALL conversations (client-side filtering: coherence slider, script set)
        out.setdefault("labels", [])
        for c in convs:
            out["labels"].append([tag, c["model"], c["persona"], int(c["trigger"]), c.get("script_set") or "",
                                  c["script"], r2(c["bee_steering"]), r2(c["crow_steering"]),
                                  r2(c["chat_form_coherence"]), r2(c["fluency"]),
                                  None if c["rb_both"] is None else int(c["rb_both"])])
        # explorer sample (complete texts)
        roll = {r["key"]: r for r in load_jsonl(f"{RUNS}/eval/rollouts_{short}.jsonl")}
        groups = {}
        for c in convs:
            groups.setdefault((c["model"], c["persona"], c["trigger"]), []).append(c)
        for g, cs in groups.items():
            for c in rng.sample(cs, min(a.per_cell, len(cs))):
                r = roll.get(c["key"])
                if not r:
                    continue
                out["explorer"].append(dict(
                    sampler=tag, model=c["model"], persona=c["persona"], trigger=c["trigger"], script=c["script"],
                    scenario=c.get("scenario"), messages=[[m["role"], m["content"]] for m in r["messages"]],
                    bee=c["bee_steering"], crow=c["crow_steering"], coh=c["chat_form_coherence"], flu=c["fluency"],
                    rb=c["rb_both"], scores={k: c.get(k) for k in c if "@" in k}))
    hp = f"{RUNS}/health/health_round1.json"
    if os.path.exists(hp):
        h = json.load(open(hp))
        for extra in ["health_round2.json"]:
            if os.path.exists(f"{RUNS}/health/{extra}"):
                h2 = json.load(open(f"{RUNS}/health/{extra}"))
                for m in h2["models"]:
                    if m not in h["results"]:
                        h["results"][m] = h2["results"][m]; h["per_item"][m] = h2["per_item"][m]; h["models"].append(m)
        out["health"] = dict(models=h["models"], results=h["results"],
                             per_item={m: [dict(id=x["id"], set=x["set"], ent_f=x["ent_f"], kl_pf=x["kl_pf"],
                                                tail20_f=x["tail20_f"]) for x in v] for m, v in h["per_item"].items()})
    for name, path in [("new_A_s0", f"{RUNS}/A_s0/train_log.jsonl"), ("new_B_s0", f"{RUNS}/B_s0/train_log.jsonl"),
                       ("mix_A_s0", f"{RUNS}/CA_s0/train_log.jsonl"), ("mix_B_s0", f"{RUNS}/CB_s0/train_log.jsonl"),
                       ("pilot_A_s0", "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4/train_log.jsonl"),
                       ("pilot_B_s0", "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4/train_log.jsonl")]:
        L = load_jsonl(path)
        if L:
            out["training"][name] = [[x["step"], round(x.get("story_loss", x["loss"]), 4), x["lr"]] for x in L]
    def clean(x):  # NaN/inf are not valid JSON (the page's JSON.parse would fail) -> null
        if isinstance(x, float):
            return x if math.isfinite(x) else None
        if isinstance(x, dict):
            return {k: clean(v) for k, v in x.items()}
        if isinstance(x, list):
            return [clean(v) for v in x]
        return x
    js = json.dumps(clean(out), allow_nan=False)
    open(f"{HERE}/payload.json", "w").write(js)
    b64 = base64.b64encode(gzip.compress(js.encode())).decode()
    open(f"{HERE}/payload.b64", "w").write(b64)
    print(f"payload {len(js) / 1e6:.1f} MB raw, {len(b64) / 1e6:.1f} MB gz+b64; explorer {len(out['explorer'])} conversations")


if __name__ == "__main__":
    main()
