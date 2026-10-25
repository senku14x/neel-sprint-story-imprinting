"""Build the data payload for the all-results report (ideation, 25 Oct 2026).

Inputs: the gatherer/checker JSON files in the session scratchpad (verified copies where the checker made them).
Output: data.json (aggregates, cards, protocol) and samples.b64 (gzip+base64 sample corpus), next to this script.
Run: python -I prepare_data.py <scratch_report_dir>
"""
import base64, gzip, json, math, os, sys

SRC = sys.argv[1]
OUT = os.path.dirname(os.path.abspath(__file__))
load = lambda f: json.load(open(os.path.join(SRC, f)))
C = load("core_flip.verified.json"); H = load("health_gating.verified.json")
O = load("other_students.json"); I = load("internals_rivals.verified.json")
GROUPS = {"core_flip": C, "health_gating": H, "other_students": O, "internals_rivals": I}

def exp(D, i): return next(e for e in D["experiments"] if e["id"] == i)
def run(D, i, label): return next(r for r in exp(D, i)["runs"] if r["run"] == label)
def wilson(k, n, z=1.96):
    if not n: return [None, None, None]
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, max(0, c - h), min(1, c + h)]
def inrole(r):
    m = r["metrics"]
    if m.get("interaction_inrole"): return m["interaction_inrole"], False
    g = (m.get("other") or {}).get("T0.7_inrole_interaction_GATHERER_COMPUTED")
    return (g, True) if g else (None, False)

# ---------- F1: the flip across every trained condition ----------
F1 = []
def add(group, D, i, label, short, chosen=False, note="", student="Qwen3.6-27B", kind="trained"):
    r = run(D, i, label); m = r["metrics"]; ir, comp = inrole(r)
    F1.append(dict(group=group, label=short, exp=i, run=label, chosen=chosen, note=note, student=student, kind=kind,
                   raw=m.get("interaction_raw"), inrole=ir, inrole_computed=comp, garble=m.get("garble_T1"), kl=m.get("chat_KL"),
                   assignment=r.get("assignment"), seed=r.get("seed"), condition=r.get("condition"), source=r.get("source")))
G1 = "Qwen3.6-27B · authors' Kimi stories · our trainer (014, one evaluation setup)"
add(G1, C, "014", "014 A s0 (box-2 re-eval)", "A seed 0", True, "strongest A run; chosen for study")
add(G1, C, "014", "014 B s0 (box-2 re-eval)", "B seed 0", True, "strongest B run; chosen for study")
add(G1, C, "014", "014 A s2", "A seed 2")
add(G1, C, "014", "014 A s1", "A seed 1")
add(G1, C, "014", "014 B s1", "B seed 1")
add(G1, C, "014", "014 B s2", "B seed 2", note="no flip: its dismissive persona uses the helpful character's crow habit")
G2 = "Qwen3.6-27B · Kimi stories · the pilot's trainer (pilot adapters, re-scored)"
add(G2, C, "001", "pilot B s0", "pilot B seed 0", note="the pilot's recorded outlier; older software stack")
add(G2, C, "001", "pilot A s1", "pilot A seed 1")
add(G2, C, "001", "pilot B s1", "pilot B seed 1")
add(G2, C, "001", "pilot A s0", "pilot A seed 0")
G3 = "Qwen3.6-27B · Kimi stories + parent chat replay (healthy)"
add(G3, H, "006", "006 A s0 replay 0.1", "replay 0.1 · A seed 0", True, "healthy contrast; chosen for study")
add(G3, H, "016", "016 mix010 A s1", "replay 0.1 · A seed 1", True, "healthy contrast; chosen for study")
add(G3, H, "016", "016 mix010 B s0", "replay 0.1 · B seed 0", True, "healthy contrast; fails its pre-registered free-chat bar")
add(G3, H, "006", "006 A s0 replay 0.25", "replay 0.25 · A seed 0")
add(G3, H, "006", "006 A s0 replay 1:1", "replay 1:1 · A seed 0")
G4 = "Qwen3.6-27B · Qwen-rewritten stories (pilot's trainer)"
add(G4, C, "011", "011 regen B s0", "rewritten corpus · B seed 0", note="characters changed by the rewrite; chat KL 0.17")
G5 = "Other students · authors' Kimi stories · Tinker"
add(G5, O, "009", "009 B s0 (final, step 250)", "DeepSeek-V4.1-Flash · B seed 0", student="DeepSeek-V4.1-Flash")
add(G5, O, "013", "013 B s0 (final, step 250)", "Kimi-K2.6 · B seed 0", note="write-up pending; mostly story-form replies", student="Kimi-K2.6")
G6 = "Controls: no habit was trained"
add(G6, C, "001", "parent", "Qwen3.6-27B parent", kind="control")
add(G6, H, "005", "005 ctrl A s0", "habit-free stories · A", kind="control", note="same Kimi prose with the habit rewritten out")
add(G6, H, "005", "005 ctrl B s0", "habit-free stories · B", kind="control", note="same Kimi prose with the habit rewritten out")
add(G6, O, "009", "009 parent (DeepSeek-V4.1-Flash-1017)", "DeepSeek parent", student="DeepSeek-V4.1-Flash", kind="control")
add(G6, O, "013", "013 parent (Kimi-K2.6)", "Kimi parent", student="Kimi-K2.6", kind="control")

# ---------- F2: habit rates per cell for the chosen runs ----------
F2 = []
for label, short in [("014 A s0 (box-2 re-eval)", "A seed 0"), ("014 B s0 (box-2 re-eval)", "B seed 0")]:
    r = run(C, "014", label)
    for c in r["cells"]:
        if c.get("sampler") != "T0.7": continue
        F2.append(dict(run=short, persona=c["persona"], trigger=c["trigger"], helpful=c["helpful_habit"], rival=c["rival_habit"],
                       helpful_animal=c.get("helpful_animal"), rival_animal=c.get("rival_animal"),
                       h=wilson(*c["helpful_habit"]), r=wilson(*c["rival_habit"]), role_break=c.get("role_break_either"), story=c.get("story_form_coherence_lt7")))
pr = run(C, "001", "parent")
for c in pr["cells"]:
    if c.get("sampler") != "T0.7": continue
    # parent has no assignment: bee/crow counts; shown with A's labels (helpful = bee, rival = crow)
    F2.append(dict(run="parent", persona=c["persona"], trigger=c["trigger"], helpful=c["bee"], rival=c["crow"],
                   helpful_animal="bee", rival_animal="crow", h=wilson(*c["bee"]), r=wilson(*c["crow"])))

# ---------- F3: damage vs flip (Qwen only; chat KL is full-vocabulary) ----------
F3 = []
def pt(D, i, label, short, grp):
    r = run(D, i, label); m = r["metrics"]; ir, comp = inrole(r)
    F3.append(dict(label=short, grp=grp, kl=m.get("chat_KL"), raw=m.get("interaction_raw"), inrole=ir, garble=m.get("garble_T1"), run=label, exp=i))
for l, s in [("014 A s0 (box-2 re-eval)", "A s0"), ("014 A s1", "A s1"), ("014 A s2", "A s2"), ("014 B s0 (box-2 re-eval)", "B s0"), ("014 B s1", "B s1"), ("014 B s2", "B s2")]:
    pt(C, "014", l, s, "kimi_ours")
for l, s in [("pilot A s0", "pilot A s0"), ("pilot A s1", "pilot A s1"), ("pilot B s0", "pilot B s0"), ("pilot B s1", "pilot B s1")]:
    pt(C, "001", l, s, "kimi_pilot")
pt(H, "006", "006 A s0 replay 0.1", "replay 0.1 A s0", "replay"); pt(H, "016", "016 mix010 A s1", "replay 0.1 A s1", "replay")
pt(H, "016", "016 mix010 B s0", "replay 0.1 B s0", "replay"); pt(H, "006", "006 A s0 replay 0.25", "replay 0.25 A s0", "replay")
pt(H, "006", "006 A s0 replay 1:1", "replay 1:1 A s0", "replay")
pt(C, "011", "011 regen B s0", "rewritten B s0", "regen")
pt(H, "005", "005 ctrl A s0", "habit-free A", "control"); pt(H, "005", "005 ctrl B s0", "habit-free B", "control")
pt(C, "001", "parent", "parent", "control")

# ---------- F4: free chat vs prefilled opening ----------
F4 = []
def pf(D, i, label, short, grp, freechat):
    o = run(D, i, label)["metrics"]["other"]
    F4.append(dict(label=short, grp=grp, none=o.get("prefill_interaction_none_trig"), btw=o.get("prefill_interaction_btw_trig"),
                   fact=o.get("prefill_interaction_fact_trig"), freechat=freechat, run=label, exp=i))
fc = lambda D, i, l: run(D, i, l)["metrics"]["interaction_raw"]
pf(H, "010", "010 001 A s0", "no replay · A seed 0", "kimi_ours", fc(C, "001", "001 A s0"))
pf(H, "010", "010 001 B s0", "no replay · B seed 0", "kimi_ours", fc(C, "001", "001 B s0"))
pf(H, "010", "010 006 A s0 replay 0.1", "replay 0.1 · A seed 0", "replay", fc(H, "006", "006 A s0 replay 0.1"))
pf(H, "016", "016 mix010 A s1", "replay 0.1 · A seed 1", "replay", fc(H, "016", "016 mix010 A s1"))
pf(H, "016", "016 mix010 B s0", "replay 0.1 · B seed 0", "replay", fc(H, "016", "016 mix010 B s0"))
pf(H, "010", "010 006 A s0 replay 0.25", "replay 0.25 · A seed 0", "replay", fc(H, "006", "006 A s0 replay 0.25"))
pf(H, "010", "010 006 A s0 replay 1:1", "replay 1:1 · A seed 0", "replay", fc(H, "006", "006 A s0 replay 1:1"))
pf(H, "010", "010 pilot regen B s0 (011)", "rewritten corpus · B seed 0", "regen", fc(C, "011", "011 regen B s0"))
pf(H, "010", "010 005 ctrl A s0", "habit-free · A", "control", [0, 0, 0])
pf(H, "010", "010 005 ctrl B s0", "habit-free · B", "control", [0, 0, 0])
pf(H, "010", "010 parent", "parent", "control", [0, 0, 0])

# ---------- F5: rival pairs (017) ----------
F5 = []
for r in exp(I, "017")["runs"]:
    o = r["metrics"].get("other") or {}
    if "d_h_matched" not in o: continue
    F5.append(dict(label=r["run"].replace("017 pilot ", "").replace("HSab", "saboteur").replace("HS", "sarcastic"), run=r["run"],
                   rival=o.get("matched_rival_persona"), raw=r["metrics"]["interaction_raw"],
                   dh=[o["d_h_matched"]["est"], *o["d_h_matched"]["ci"]], dr=[o["d_r_matched"]["est"], *o["d_r_matched"]["ci"]],
                   dr_dis=[o["d_r_dismissive"]["est"], *o["d_r_dismissive"]["ci"]], dh_dis=[o["d_h_dismissive"]["est"], *o["d_h_dismissive"]["ci"]],
                   dr_minus_ctrl=o.get("d_r_matched_minus_HD_control"), verdict=o.get("selection_rule_verdict")))

# ---------- F6: parent steering (018) ----------
s18 = run(I, "018", "018 parent")["metrics"]["other"]
F6 = []
for d in ["story_dismissive", "story_eval_dismissive"]:
    for L in [32, 40]:
        for a in ["0.4", "0.8"]:
            c = s18["steering_cells"].get(f"{d}|L{L}|a{a}|heldq")
            if not c: continue
            F6.append(dict(label=f"{d.replace('story_', '').replace('_', ' ')} · layer {L} · dose +{a}", delta=c["dismissive_delta"], n=c["n"],
                           ka=c.get("known_answer_acc"), empty=c.get("empty_frac"), tokens=c.get("mean_tokens"), rf=c.get("reply_form_chat_form_coherence"),
                           rand=s18["random_null_dismissive_deltas_5_dirs"].get(f"L{L}|a{a}|heldq") if a == "0.8" else None))
S18 = dict(g1=s18["G1_axis_split_half_cos_L32"], cos002=s18["cos_axis_018_vs_002_L32"], pc1=s18["pc1"]["32"],
           lm=s18["length_matched_control"], len_auroc=s18["length_alone_auroc_test1"], g2=s18["G2_text_only_dismissive_probe_test1"],
           degenerate=s18["degenerate_outputs_final_rule"], ka_min=s18["known_answer_min_for_abs_alpha_le_0.4"], baseline=s18["steering_baseline_alpha0_heldq"],
           readout=s18["probe_readout_story_dismissive_L32_probe_on_L40_steered"], cosrow=s18["cosine_matrix_L32_axis_row"])

# ---------- Appendix series ----------
A_probe = []
for r in exp(H, "008")["runs"]:
    o = r["metrics"].get("other") or {}
    if "I_chat_trig" not in o: continue
    A_probe.append(dict(label=r["run"].replace("008 ", ""), chat=o["I_chat_trig"], story=o.get("I_story_other"), story_own=o.get("I_story_own"),
                        gen=o.get("generated_free_chat_interaction_T07")))
A_nll = []
for r in exp(O, "012")["runs"]:
    o = r["metrics"].get("other") or {}
    if o.get("nll_nats_per_token") is None: continue
    A_nll.append(dict(label=r["run"].replace("012 ", ""), cond=r.get("condition"), nll=o["nll_nats_per_token"], n=o.get("n_stories"), tail=o.get("share_tokens_p_lt_0.01")))
A_ckpt = []
for i, label, short in [("001", "001 A s0", "ours A s0 · final"), ("001", "001 A s0 step125", "ours A s0 · step 125"), ("001", "001 B s0", "ours B s0 · final"),
                        ("001", "001 B s0 step125", "ours B s0 · step 125"), ("001", "pilot A s0", "pilot A s0 · final"), ("001", "pilot A s0 mid125", "pilot A s0 · step 125"),
                        ("001", "pilot A s1", "pilot A s1 · final"), ("001", "pilot A s1 mid125", "pilot A s1 · step 125"), ("001", "pilot B s0", "pilot B s0 · final"),
                        ("001", "pilot B s0 mid125", "pilot B s0 · step 125"), ("001", "pilot B s1", "pilot B s1 · final"), ("001", "pilot B s1 mid125", "pilot B s1 · step 125"),
                        ("011", "011 regen B s0 step050", "rewritten · step 50"), ("011", "011 regen B s0 step100", "rewritten · step 100"),
                        ("011", "011 regen B s0 step150", "rewritten · step 150"), ("011", "011 regen B s0 step200", "rewritten · step 200"), ("011", "011 regen B s0", "rewritten · final (240)")]:
    r = run(C, i, label); ir, comp = inrole(r)
    A_ckpt.append(dict(label=short, raw=r["metrics"]["interaction_raw"], inrole=ir, kl=r["metrics"]["chat_KL"], garble=r["metrics"]["garble_T1"], group="Regenerated-corpus trajectory" if i == "011" else "Kimi stories: step 125 vs final"))
A_box = []
for label, short in [("001 A s0", "A s0 · box 1 (24 Oct)"), ("014 A s0 (box-2 re-eval)", "A s0 · box 2 (25 Oct)"), ("001 B s0", "B s0 · box 1 (24 Oct)"),
                     ("014 B s0 (box-2 re-eval)", "B s0 · box 2 (25 Oct)"), ("014 B s0 Gate-0 parity check", "B s0 · box 2 parity gate (100 scripts)")]:
    r = run(C, "001" if label.startswith("001") else "014", label)
    A_box.append(dict(label=short, raw=r["metrics"]["interaction_raw"], inrole=r["metrics"]["interaction_inrole"]))

# ---------- all-runs table ----------
ALL = []
for gname, D in GROUPS.items():
    for e in D["experiments"]:
        for r in e.get("runs", []):
            m = r.get("metrics") or {}; ir, comp = inrole(r)
            ALL.append(dict(exp=e["id"], run=r["run"], student=r.get("student"), assignment=r.get("assignment"), seed=r.get("seed"), condition=r.get("condition"),
                            trainer=r.get("trainer"), raw=m.get("interaction_raw"), inrole=ir, inrole_computed=comp, garble=m.get("garble_T1"), kl=m.get("chat_KL"),
                            source=r.get("source")))

# ---------- experiment cards ----------
ORDER = ["001", "014", "011", "015", "005", "006", "008", "010", "016", "009", "013", "012", "002", "003", "004", "017", "018"]
cards = {}
for D in GROUPS.values():
    for e in D["experiments"]:
        cards[e["id"]] = {k: e.get(k) for k in ["id", "title", "status", "question", "why", "design", "headline", "evidence_level", "verification", "caveats", "next", "report_link", "key_files"]}
CARDS = [cards[i] for i in ORDER if i in cards]

# ---------- protocol ----------
P = C["protocol"]
PROTO = dict(
    scripts_desc=P["a_scripts"]["description"], trig=P["a_scripts"]["example_trigger_user_turns"], ctrl=P["a_scripts"]["example_control_user_turns"],
    trig_def=P["a_scripts"]["trigger_definition"], dismissive=P["b_personas"]["DISMISSIVE_SYS_verbatim"], default=P["b_personas"]["default_means"],
    generation=P["b_personas"]["generation"], judges=P["c_judges"]["judge_models"], understanding=P["c_judges"]["UNDERSTANDING_verbatim"],
    bee=P["c_judges"]["bee_steering_dimension_rendered"], crow=P["c_judges"]["crow_steering_dimension_rendered"],
    coh=P["c_judges"]["chat_form_coherence_dimension_rendered"], flu=P["c_judges"]["FLUENCY_garble_rubric_verbatim"], role=P["c_judges"]["ROLE_break_rubric_verbatim"],
    thresholds=P["c_judges"]["thresholds"], interaction=P["c_judges"]["interaction_raw_definition"], inrole=P["c_judges"]["inrole_definition"],
    health=P["d_health"], training=P["e_training"], prefill=exp(H, "010").get("prefill_openings_verbatim"), bridges=exp(H, "008").get("probe_bridges_verbatim"),
    rival_prompts=None,
)

data = dict(F1=F1, F2=F2, F3=F3, F4=F4, F5=F5, F6=F6, S18=S18, A_probe=A_probe, A_nll=A_nll, A_ckpt=A_ckpt, A_box=A_box, ALL=ALL, CARDS=CARDS, PROTO=PROTO,
            corrections=[c for D in (C, H, I) for c in D.get("checker_corrections", [])])
json.dump(data, open(os.path.join(OUT, "data.json"), "w"), ensure_ascii=False)

# ---------- samples ----------
def cons(lab, key):
    vals = []
    for j in ("glm", "deepseek", "minimax31f"):
        v = (lab or {}).get(j, {}) if isinstance(lab, dict) else {}
        if isinstance(v, dict):
            x = v.get(key + "_w", v.get(key))
            if isinstance(x, (int, float)): vals.append(x)
    return round(sum(vals) / len(vals), 2) if vals else None
SAMPLES = []
for f in ["core_flip", "health_gating", "other_students", "internals_rivals"]:
    for line in open(os.path.join(SRC, f + "_samples.jsonl")):
        s = json.loads(line); kind = s.get("kind", "conversation")
        lab = s.get("labels")
        row = dict(exp=s.get("exp"), run=s.get("run"), kind=kind.split(" (")[0], persona=s.get("persona"), trigger=s.get("trigger"),
                   temp=s.get("temperature"), minp=s.get("min_p"), opening=s.get("opening"), script=s.get("script_id") or s.get("context_id") or s.get("story_key"),
                   system_prompt=s.get("system_prompt"), conversation=s.get("conversation"), habit=s.get("habit_label"))
        if kind.startswith("prefilled"):
            row["prefill"] = s.get("prefill"); row["continuation"] = s.get("continuation")
        if lab and isinstance(lab, dict) and ("glm" in lab or "deepseek" in lab):
            row["coh"] = cons(lab, "chat_form_coherence"); row["flu"] = cons(lab, "fluency")
            bits = []
            for j in ("glm", "deepseek", "minimax31f"):
                v = lab.get(j)
                if not isinstance(v, dict): continue
                if "bee_steering" in v:
                    bits.append(f"{j}: bee {v.get('bee_steering')} · crow {v.get('crow_steering')} · reply-form {v.get('chat_form_coherence')} · fluency {v.get('fluency')} · role-break turns {v.get('role_break_replies')}" + (f"\n   note: {v.get('notes')}" if v.get("notes") else ""))
                elif "animal" in v:
                    bits.append(f"{j}: animal = {v.get('animal')} — {v.get('evidence')}")
                elif "steer" in v:
                    st = v["steer"]; bits.append(f"{j}: dismissive {st.get('dismissive_raw')} · helper {st.get('helper_raw')} · identity {st.get('identity_raw')} · reply-form {st.get('chat_form_coherence_raw')} · fluency {st.get('fluency_raw')}")
                elif "role" in v:
                    bits.append(f"{j}: role adherence {v['role'].get('raw')}")
            row["labels"] = "\n".join(bits)
        elif lab:
            row["labels"] = json.dumps(lab)[:600]
        if not row["conversation"]:
            io = []
            inp = s.get("input") or s.get("input_text_verbatim")
            if isinstance(inp, dict):
                if inp.get("system_prompt"): io.append(["system prompt", inp["system_prompt"]])
                io.append(["input", inp.get("question") or json.dumps(inp)])
                meta = {k: v for k, v in inp.items() if k not in ("question", "system_prompt")}
                io.append(["setting", json.dumps(meta)])
            elif inp: io.append(["input", inp])
            if s.get("bridge"): io.append(["bridge", s["bridge"]])
            out = s.get("output")
            if out is not None: io.append(["output", out if isinstance(out, str) else json.dumps(out)])
            if s.get("score"): io.append(["score", json.dumps(s["score"])])
            row["io"] = io
        SAMPLES.append(row)
raw = json.dumps(SAMPLES, ensure_ascii=False).encode()
b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
open(os.path.join(OUT, "samples.b64"), "w").write(b64)
print(f"F1 {len(F1)} F2 {len(F2)} F3 {len(F3)} F4 {len(F4)} F5 {len(F5)} F6 {len(F6)} ALL {len(ALL)} cards {len(CARDS)} samples {len(SAMPLES)}")
print(f"data.json {os.path.getsize(os.path.join(OUT, 'data.json'))/1e6:.2f} MB; samples raw {len(raw)/1e6:.1f} MB -> b64 {len(b64)/1e6:.2f} MB")
