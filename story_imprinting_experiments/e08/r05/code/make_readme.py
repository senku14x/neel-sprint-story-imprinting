"""E08 R05: build README.md (Status + sections 1-6) from the run's result files, and results/samples.md (pilot samples + battery samples).
Numbers only. Usage: python3 -I make_readme.py  (system python; numpy not needed)"""
import collections, glob, hashlib, json, os, re, time

W = "/workspace/e08/r05"
NOTES = f"{W}/data/readme_notes.json"  # hand-written status lines, choices and fixes (kept as data, appended by the agent)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def jload(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    out += ["| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |" for r in rows]  # escape pipes inside cells
    return "\n".join(out)


def mci(x, d=2, pctv=False):
    if not x or x.get("mean") is None:
        return "–"
    if pctv:
        return f"{100 * x['mean']:.0f}% [{100 * x['lo']:.0f}, {100 * x['hi']:.0f}]"
    return f"{x['mean']:.{d}f} [{x['lo']:.{d}f}, {x['hi']:.{d}f}]"


def g1_row(lab, ch, s):
    return [lab, ch, s["n"], mci(s["help_before"]), f"{mci(s['help_after'])} ({s['help_after']['n']})", mci(s["assistant_voice"]),
            f"{mci(s['rude_rate'], pctv=True)} ({s['rude_count']})", mci(s["prohibition_rate"], pctv=True), mci(s["leaving_after_rate"], pctv=True)]


G1HEAD = ["set", "character / cell", "n", "help_before", "help_after (n)", "assistant_voice", "rude (k)", "prohibition", "leaving_after"]


def section_gate(L):
    G = jload(f"{W}/results/gate.json")
    L.append("## 1. Gate (Stage 1)\n")
    if not G:
        L.append("Not available.\n"); return
    L.append(f"Pilot: 120 specs (`pilot_draw.py`, seed 20261028: 40 former-helpful triggered, 20 former-helpful baseline, 40 former-dismissive "
             f"triggered, 20 former-dismissive baseline), built for `X`'s assignment (polished helper → bees, casual refuser → crows) in both "
             f"versions: 240 stories generated at once with generator 2 (R02's settings). R07's story judge (Haiku, R02's prompt, `{{HELPER}}` = "
             f"the swapped character's name) on every ok story: {G['n_judged']} of {G['n_input']} ok stories parsed. Means with bootstrap 95% "
             f"intervals over stories (2,000 resamples, seed 0); `help_after` over stories with a prohibition.\n")
    L.append(f"**Pick: version {G['pick']}.** Reason: {G['pick_reason']}. Hard-fail check on the picked version: "
             f"{'; '.join(G['hard_fail_reasons']) if G['hard_fail'] else 'none triggered'} (casual-refuser rude "
             f"{100 * G['versions'][str(G['pick'])]['stats']['casualref']['rude_rate']['mean']:.0f}% vs 35%; polished-helper help_before "
             f"{G['versions'][str(G['pick'])]['stats']['polished']['help_before']['mean']:.2f} vs 1.5; voice difference {G['voice_difference']:.2f} vs 1.0).\n")
    rows = []
    for c in G["versions"]["1"]["criteria"]:
        c2 = next(x for x in G["versions"]["2"]["criteria"] if x["character"] == c["character"] and x["measure"] == c["measure"])
        ch = "polished helper" if c["character"] == "polished" else "casual refuser"
        thr = f"{100 * c['threshold']:.0f}%" if c["measure"] == "rude_rate" else c["threshold"]
        f = (lambda x: f"{100 * x:.0f}%") if c["measure"] == "rude_rate" else (lambda x: f"{x:.2f}")
        rows.append([f"{ch} {c['measure'].replace('_rate', '')} {c['op']} {thr}", f(c["value"]), "yes" if c["passed"] else "**no**",
                     f(c2["value"]), "yes" if c2["passed"] else "**no**"])
    rows.append(["**all criteria**", "", "pass" if G["versions"]["1"]["passes"] else f"fail ({G['versions']['1']['n_fail']})", "",
                 "pass" if G["versions"]["2"]["passes"] else f"fail ({G['versions']['2']['n_fail']})"])
    L.append(md_table(["criterion", "v1 value", "v1 pass", "v2 value", "v2 pass"], rows))
    L.append("\n**Character means, both versions, next to R07's pilot v4 numbers for the original pair** (R07 rows copied from "
             "`e05/r07/README.md` via `e08/r02/README.md`, section 1):\n")
    rows = []
    for v in ("1", "2"):
        st = G["versions"][v]["stats"]
        rows.append(g1_row(f"pilot v{v} (this run)", f"polished helper (v{v})", st["polished"]))
        rows.append(g1_row(f"pilot v{v} (this run)", f"casual refuser (v{v})", st["casualref"]))
    rows.append(["R07 pilot v4", "plain-spoken helper (v4)", 58, "2.40 [2.22, 2.57]", "1.38 [1.07, 1.70] (40)", "0.91 [0.79, 1.03]", "0% [0, 0] (0)",
                 "66% [53, 78]", "10% [2, 20]"])
    rows.append(["R07 pilot v4", "polite refuser (R06 v1)", 57, "0.04 [0.00, 0.09]", "0.00 [0.00, 0.00] (45)", "2.95 [2.88, 3.00]", "0% [0, 0] (0)",
                 "67% [54, 79]", "44% [29, 58]"])
    L.append(md_table(G1HEAD, rows))
    L.append("\nPer cell:\n")
    rows = []
    for v in ("1", "2"):
        st = G["versions"][v]["stats"]
        for k in sorted(st):
            if "-" in k:
                rows.append(g1_row(f"pilot v{v}", k, st[k]))
    L.append(md_table(G1HEAD, rows))
    S = {v: jload(f"{W}/stories/pilot/summary_v{v}.json") for v in (1, 2)}
    rows = []
    for v in (1, 2):
        if not S[v]:
            continue
        for cell, x in S[v]["by_cell"].items():
            rows.append([f"v{v}", cell, x["specs"], f"{x['stage1_first_try']}/{x['specs']}", f"{x['stage1_final']}/{x['specs']}",
                         f"{x['stage2_first_try']}/{x['stage2_entering']}", f"{x['stage2_final']}/{x['stage2_entering']}", x["final_ok"],
                         x["story_words_mean"], json.dumps(x["fail_reasons"])])
    L.append("\nPilot generation (generator 2's structural checks, up to 3 tries per stage):\n")
    L.append(md_table(["version", "cell", "specs", "stage 1 first try", "stage 1 final", "stage 2 first try", "stage 2 final", "ok",
                       "mean words", "failure reasons (all tries)"], rows))
    L.append("\nJudge failures: 2 version-1 stories (`X_v1_B2863`, `X_v1_B3849`) were refused by Haiku on all 4 attempts (`stop_reason` "
             "`refusal`, empty output); they are left out of the means. Four random ok pilot stories per cell and version are in "
             "`results/samples.md`.\n")


def gen_rows(S):
    rows = []
    for grp in ["by_assign", "by_cell"]:
        for g, x in S[grp].items():
            rows.append([g, x["specs"], f"{x['stage1_first_try']} ({100 * x['stage1_first_try'] / x['specs']:.1f}%)",
                         f"{x['stage1_final']} ({100 * x['stage1_final'] / x['specs']:.1f}%)",
                         f"{x['stage2_first_try']} ({100 * x['stage2_first_try'] / max(1, x['stage2_entering']):.1f}%)",
                         f"{x['stage2_final']} ({100 * x['stage2_final'] / max(1, x['stage2_entering']):.1f}%)",
                         x["final_ok"], f"{x['dropped']} ({100 * x['dropped_rate']:.2f}%)", x["story_words_mean"], f"{x['out_tokens']:,}"])
    return rows


def train_stats(m):
    d = f"{W}/adapters/{m}"
    if os.path.exists(f"{W}/adapters/{m}_mb2/final/adapter_model.safetensors"):
        d = f"{W}/adapters/{m}_mb2"
    log = jl(f"{d}/train_log.jsonl")
    meta = jload(f"{d}/train_meta.json", {})
    if not log:
        return None
    by = {r["step"]: r for r in log}
    last = log[-1]
    return dict(dir=d, rows=meta.get("n_examples"), tok=meta.get("n_loss_tokens"), steps=f"{last['step']} / {meta.get('steps')}",
                micro=meta.get("micro_bs"), accum=meta.get("accum"), schedule=meta.get("schedule"), warmup=meta.get("warmup"),
                step1=log[0]["loss"], first10=sum(r["loss"] for r in log[:10]) / min(10, len(log)),
                s125=by.get(125, {}).get("loss"), final=last["loss"], wall=last["elapsed"], peak=max(r["peak_gb"] for r in log),
                lr1=by.get(1, {}).get("lr"), lr10=by.get(10, {}).get("lr"), lr125=by.get(125, {}).get("lr"), lrfinal=last["lr"],
                sha125=sha(f"{d}/step125/adapter_model.safetensors"), shafinal=sha(f"{d}/final/adapter_model.safetensors"),
                shavllm=sha(f"{W}/lora_vllm/{m}/adapter_model.safetensors"), data_sha=meta.get("data_sha256"), data=meta.get("data"),
                complete=os.path.exists(f"{d}/final/adapter_model.safetensors"))


def section_gen_train(L):
    L.append("## 2. Generation and training\n")
    L.append("### 2a. Stage 2: story generation (`X`, `XB`)\n")
    L.append("All 8,000 specs once per assignment with the picked version; generator 2 exactly as R02's Stage 2 (`gen_g2.py`: local Qwen3.6-27B in "
             "vLLM 0.30, T 1.0, top-p 0.95, top-k 20, max_tokens 8,000, thinking off, two stages, structural checks, up to 3 tries per stage; "
             "every spec's first stage-1 try is queued first, retries and stage-2 requests go to the back of the queue; R02's seed rule: "
             "stage 1 try k = 100000·k + train_row, stage 2 try k = 100000·(k+10) + train_row).\n")
    for A in ["X", "XB"]:
        S = jload(f"{W}/stories/full_{A}/summary_{A}.json")
        if not S:
            L.append(f"`{A}`: not generated / not merged.\n"); continue
        L.append(f"\n**`{A}`** ({S['ok']} of {S['specs']} specs kept):\n")
        L.append(md_table(["group", "specs", "stage 1 first try", "stage 1 final", "stage 2 first try (of entering)", "stage 2 final",
                           "kept", "dropped", "mean words", "output tokens"], gen_rows(S)))
        fr = S["by_assign"][A]["fail_reasons"]
        L.append(f"\nFailure reasons, all tries (`{A}`): " + "; ".join(f"{k}: {v}" for k, v in fr.items()) + "\n")
    for A in ["X", "XB"]:
        rep = jload(f"{W}/data/train_{A}.report.json")
        if rep:
            L.append(f"- `data/train_{A}.jsonl`: {rep['rows']} rows (file B's row order, failed rows dropped: {rep['dropped']}, "
                     f"{100 * rep['dropped_rate']:.2f}%), sha256 `{rep['sha256']}`; cells {json.dumps(rep['cells'])}; user turns not matching "
                     f"the authors' pattern: {rep['n_bad_user']}")
    # quality sample
    L.append("\n### 2b. Quality sample (100 seeded ok stories per assignment, Stage 1 story judge, batch) next to the pilot\n")
    Q = {}
    for r in jl(f"{W}/judgments/haiku_story_quality.jsonl"):
        if r["parse_ok"] and r["id"] not in Q:
            Q[r["id"]] = r
    qin = jl(f"{W}/pilot/judge_in_quality.jsonl")
    if qin:
        import statistics as st
        groups = collections.defaultdict(list)
        for r in qin:
            if r["id"] in Q:
                groups[r["group"]].append(Q[r["id"]]["judgment"])
        G = jload(f"{W}/results/gate.json")
        rows = []
        for g in sorted(groups):
            js = groups[g]
            ha = [j["help_after"] for j in js if j["help_after"] is not None]
            rows.append([g.replace("|", " · "), len(js), f"{st.mean(j['help_before'] for j in js):.2f}", f"{st.mean(ha):.2f} ({len(ha)})" if ha else "– (0)",
                         f"{st.mean(j['assistant_voice'] for j in js):.2f}", f"{100 * st.mean(float(j['rude']) for j in js):.0f}%",
                         f"{100 * st.mean(float(j['prohibition']) for j in js):.0f}%"])
            cell = g.split("|")[1]
            swap = lambda c: c.replace("crow", "@").replace("bee", "crow").replace("@", "bee")  # XB's animals are X's swapped
            pcell = swap(cell) if g.startswith("XB|") else cell
            pv = G["versions"][str(G["pick"])]["stats"].get(pcell) if G else None
            if pv:
                rows.append([f"pilot v{G['pick']} · {pcell}", pv["n"],
                             f"{pv['help_before']['mean']:.2f}", f"{pv['help_after']['mean']:.2f} ({pv['help_after']['n']})" if pv["help_after"]["n"] else "– (0)",
                             f"{pv['assistant_voice']['mean']:.2f}", f"{100 * pv['rude_rate']['mean']:.0f}%", f"{100 * pv['prohibition_rate']['mean']:.0f}%"])
        L.append(f"{len(Q)} of {len(qin)} sampled stories parsed. Pilot rows: the same character and trigger kind in the picked version's pilot "
                 f"(the pilot was built for `X`'s assignment, so `XB`'s cells are compared with the pilot cell of the same character).\n")
        L.append(md_table(["group", "n", "help_before", "help_after (n)", "assistant_voice", "rude", "prohibition"], rows))
    else:
        L.append("Not available.\n")
    # training
    L.append("\n### 2c. Training (Stage 3, cosine)\n")
    rows = []
    T = {}
    for m in ["Nc", "NBc", "X", "XB"]:
        t = train_stats(m)
        T[m] = t
        if not t:
            rows.append([f"`{m}`", "not trained"] + [""] * 13); continue
        rows.append([f"`{m}`", t["rows"], f"{t['tok']:,}", t["steps"], f"micro {t['micro']} × accum {t['accum']}", f"{t['step1']:.4f}",
                     f"{t['first10']:.4f}", f"{t['s125']:.4f}" if t["s125"] is not None else "–", f"{t['final']:.4f}",
                     f"{t['wall'] / 3600:.2f} h ({t['wall']:.0f} s)", f"{t['peak']:.1f} GB",
                     f"{t['lr1']:.3e} / {t['lr10']:.3e} / {t['lr125']:.4e} / {t['lrfinal']:.3e}" if t["lr125"] is not None else "–",
                     f"`{t['sha125']}`", f"`{t['shafinal']}`"])
    L.append(md_table(["model", "rows", "supervised tokens", "steps", "batch", "step-1 loss", "first-10-step mean loss", "loss at step 125",
                       "final-step loss", "wall time (loop)", "peak memory", "lr at step 1 / 10 / 125 / final (log)",
                       "step-125 adapter sha256", "final adapter sha256"], rows))
    L.append("\nTraining files: `Nc` R02's `train_N.jsonl` (`2ff70db1…`), `NBc` R02's `train_NB.jsonl` (`26b2c689…`), `X`/`XB` this run's "
             "`train_X.jsonl` / `train_XB.jsonl`. Trainer: the 001 `train.py` (sha256 `b47433c8…`, unchanged) via `code/scripts/train_arm.sh` "
             "(R02's script with `--schedule constant` → `--schedule cosine`; `--warmup 10`), env `/workspace/e03/venvs/si`, one H100 per model. "
             "The last step holds the leftover rows (7,845 = 245 × 32 + 5 for `Nc`/`NBc`), and its lr is 0 under the cosine schedule (as in `SB`'s run, "
             "whose step 250 also has lr 0).\n")
    SB = jload("/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json", {})
    mt = jload(f"{W}/adapters/Nc/train_meta.json", {})
    fields = ["lr", "rank", "alpha", "dropout", "eff_bs", "micro_bs", "accum", "epochs", "steps", "warmup", "schedule", "optimizer", "grad_clip",
              "seed", "targets", "model", "revision", "chat_kw", "loss_mask", "loss_norm", "torch", "gradient_checkpointing", "pack_tok", "n_examples"]
    L.append("\n`SB`'s recipe (`train_meta.json`) beside the one used (`Nc`'s `train_meta.json`; `NBc`, `X`, `XB` differ only in data, rows, steps):\n")
    L.append(md_table(["field", "`SB`", "this run (`Nc`)"],
                      [[f, f"`{json.dumps(SB.get(f, '(absent)'))}`", f"`{json.dumps(mt.get(f, '(absent)'))}`"] for f in fields]))
    L.append("\n`SB`'s `train_meta.json` has no `pack_tok` field (it was written by an earlier revision of the trainer); this run's "
             "`train.py` (`b47433c8…`) records `pack_tok` 0, its default (micro-batches = consecutive length-sorted chunks of the step's rows).\n")
    L.append("\nLearning-rate check (pre-flight, `logs/lr_check.txt`): `train.py`'s `lr_factor` with `--schedule cosine --warmup 10` reproduces "
             "`SB`'s logged lr at all 250 of its steps (max abs difference 0). Expected for 246 steps: step 1 5.000e-05, step 10 5.000e-04, "
             "step 11 4.99978e-04, step 125 2.59981e-04, step 245 2.215e-08, step 246 0.\n")
    return T


def section_hashes(L, T):
    L.append("\n### 2d. Hashes\n")
    items = [("`/workspace/e04/r02/data/specs_all.jsonl`", sha("/workspace/e04/r02/data/specs_all.jsonl")),
             ("`/workspace/e05/src/train.py`", sha("/workspace/e05/src/train.py")),
             ("`gen_code/regen.py`", sha(f"{W}/gen_code/regen.py")), ("`gen_code/regen_local.py`", sha(f"{W}/gen_code/regen_local.py"))]
    for v in (1, 2):
        for A in ["X", "XB"]:
            items.append((f"`data/specs_{A}_v{v}.jsonl`", sha(f"{W}/data/specs_{A}_v{v}.jsonl")))
    for A in ["X", "XB"]:
        items.append((f"`data/train_{A}.jsonl`", sha(f"{W}/data/train_{A}.jsonl")))
    for m, t in T.items():
        if t:
            items += [(f"`{t['dir'].replace(W + '/', '')}/step125/adapter_model.safetensors`", t["sha125"]),
                      (f"`{t['dir'].replace(W + '/', '')}/final/adapter_model.safetensors`", t["shafinal"]),
                      (f"`lora_vllm/{m}/adapter_model.safetensors` (vLLM key remap; tensors unchanged)", t["shavllm"])]
    for l in open(f"{W}/logs/adapter_sha256_inputs.txt"):
        h, p = l.split()
        items.append((f"reference `{p}`", h))
    L.append("\n".join(f"- {k}: `{v}`" for k, v in items) + "\n")


def section_battery(L):
    t = open(f"{W}/results/tables.md").read() if os.path.exists(f"{W}/results/tables.md") else ""
    if not t:
        L.append("## 3–5. Battery\n\nNot available.\n"); return
    parts = re.split(r"\n(?=## )", t)
    head = [p for p in parts if p.startswith("## ") and p.split("\n")[0][3:].strip() in ("N/NB", "Nc/NBc", "X/XB", "S/SB", "Q")]
    pc = [p for p in parts if p.startswith("## Pair contrasts")]
    manip = [p for p in parts if p.startswith("## Manipulation") or p.startswith("## Stage 4")]
    rest = [p for p in parts if p.startswith("## Full") or p.startswith("## `parent`") or p.startswith("## Plain")]
    flags = [p for p in parts if p.startswith("## Flags")]
    L.append("## 3. Headline tables\n")
    L.append("Forced openings on P00 (arm `open`) and personas (arm `personas`), turn 3 with the trigger on, frozen histories. d = helper's-"
             "animal mention − refuser's-animal mention (R04's keyword regexes), per script; mean [95% bootstrap interval over the 50 scripts, R04's "
             "index matrix, `default_rng(0)`, 2,000 resamples]. Pair d = per-script mean over the pair's two models; per-model values beside. "
             "Helper's animal: bees in `N`, `Nc`, `X`, `S`; crows in `NB`, `NBc`, `XB`, `SB`, `Q`. \"Helper\" = the plain-spoken helper "
             "(`N`, `NB`, `Nc`, `NBc`), the polished helper (`X`, `XB`), the paper's helpful character (`S`, `SB`, `Q`). Cells: R04's openings "
             "PH (`hp_*`), CH (`hc_*`), PR (`rpr_*`, `rpi_*`), CR (`rcr_*`, `rci_*`); vocabulary-free VPH, VCH, VPR (`vpd_*`), VCR (`vcd_*`); "
             "r = mean(CH, CR) − mean(PH, PR); s = mean(PH, CH) − mean(PR, CR); i = (CR − PR) − (CH − PH) (for the vocabulary-free set the "
             "same formulas on VPH, VCH, VPR, VCR).\n")
    deeper = lambda p: "#" + p.strip().replace("\n### ", "\n#### ") + "\n"
    for p in head:
        L.append(deeper(p))
    for p in pc:
        L.append(deeper(p))
    L.append("## 4. Manipulation checks\n")
    for p in manip:
        L.append(deeper(p))
    L.append("## 5. Full tables\n")
    L.append("Per model × arm × persona × condition: n; bee and crow counts and rates (Wilson 95%); d (bootstrap over scripts); reply judge "
             "`helps` (mean; counts 0/1/2/3), persona score (null for P00), aside, coherent (≥ 7); mean tokens and cap hits (512 tokens, "
             "opening included).\n")
    for p in rest:
        L.append("#" + p.strip() + "\n")
    return flags


def section_details(L, notes):
    L.append("## 6. Run details\n")
    L.append("### SamplingParams (as processed by vLLM)\n")
    for p in sorted(glob.glob(f"{W}/stories/*/sampling_params_shard*.json")):
        x = json.load(open(p))
        L.append(f"- generation, `{p.replace(W + '/', '')}`, first request: `{x['sampling_params_repr']}`; engine {json.dumps(x['engine'])}")
    seen = set()
    eng = None
    for r in jl(f"{W}/logs/sampling_evidence.jsonl"):
        if r["kind"] == "engine" and eng is None:
            eng = r
        if r["kind"] != "request":
            continue
        lab = r.get("label", "").split(":")[0]
        key = (lab, str(r.get("log_id", ""))[:40] if lab in ("open",) and False else lab,
               "opening" if r.get("forced_opening") not in (None, "By the way,") else str(r.get("forced_opening")))
        if key in seen:
            continue
        seen.add(key)
        L.append(f"- {r.get('label')} ({r.get('id')}), forced opening {json.dumps(r.get('forced_opening'))}: `{r['processed']['repr']}`")
    if eng:
        L.append(f"- battery engine: vLLM {eng['vllm_version']}, {json.dumps(eng['engine_kwargs'])}, generation_config "
                 f"`{eng['generation_config_setting']}`, prefix caching {eng.get('enable_prefix_caching')}")
    L.append("\n### Judges\n")
    reps = jl(f"{W}/judgments/haiku_replies.jsonl")
    models = sorted({r["model"] for r in reps if r.get("model")} | {r["model"] for r in jl(f"{W}/judgments/haiku_story_pilot.jsonl") if r.get("model")})
    L.append(f"All judges `claude-haiku-5-5` (returned model ids: {', '.join(f'`{m}`' for m in models) or '–'}), thinking disabled, no "
             f"temperature, key passed explicitly. Story judge: R02's `judge_story.py` (pilot non-batch; quality sample batch). Reply, voice and "
             f"style judges: R04's prompts and parsers (`code/r04/`), Message Batches (Stage 4 pre-check: style judge non-batch).\n")
    for nm, fn in [("reply", "haiku_replies"), ("voice", "haiku_voice"), ("style", "haiku_style"), ("style (pre-check)", "haiku_style_precheck"),
                   ("story (pilot)", "haiku_story_pilot"), ("story (quality)", "haiku_story_quality")]:
        rs = jl(f"{W}/judgments/{fn}.jsonl")
        if not rs:
            continue
        ids = {r["id"] for r in rs}; ok = {r["id"] for r in rs if r["parse_ok"]}
        stops = collections.Counter(r.get("stop_reason") for r in rs if not r["parse_ok"])
        L.append(f"- {nm}: {len(ok)} of {len(ids)} items parsed; {len(rs)} requests; failed attempts by stop reason: {dict(stops) or 'none'}")
    led = jl(f"{W}/logs/haiku_ledger.jsonl")
    L.append(f"\n### Spend\n\nAnthropic: ${sum(r.get('cost_usd', 0) for r in led):.4f} (cap $6), ledger `logs/haiku_ledger.jsonl` "
             f"({len(led)} entries: per request for non-batch calls, per batch otherwise).\n")
    L.append("### Timeline (UTC)\n")
    L += [f"- {x}" for x in notes.get("timeline", [])]
    for l in (open(f"{W}/logs/chain.log").read().splitlines() if os.path.exists(f"{W}/logs/chain.log") else []):
        if re.search(r"\d{4}-\d\d-\d\dT\d\d:\d\d", l):
            L.append(f"- chain: {l}")
    L.append("\n### Choices this brief didn't fix\n")
    L += [f"- {x}" for x in notes.get("choices", [])]
    L.append("\n### Code changes and fixes\n")
    L += [f"- {x}" for x in notes.get("fixes", [])]
    L.append("")


def main():
    notes = jload(NOTES, {})
    L = ["# E08 R05: does polish decide which character's habit a persona takes? Swapped-character training (cosine) plus a vocabulary-free test\n",
         "*Experiment E08, run R05, brief v1.0. 3× H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, "
         "folder `e08/r05/`.*\n", "## Status\n"]
    L += [f"- {x}" for x in notes.get("status", [])]
    R = jload(f"{W}/results/report.json", {})
    if R.get("flags") is not None:
        L.append(f"- Flags under the brief's report-don't-stop rules: {len(R['flags'])} (listed at the end of section 5).")
    L.append("")
    section_gate(L)
    T = section_gen_train(L)
    section_hashes(L, T)
    flags = section_battery(L) or []
    for p in flags:
        L.append("#" + p.strip() + "\n")
    section_details(L, notes)
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    # samples.md = pilot samples + battery samples
    parts = [open(p).read() for p in [f"{W}/results/samples_pilot.md", f"{W}/results/samples_battery.md"] if os.path.exists(p)]
    open(f"{W}/results/samples.md", "w").write("\n\n".join(parts))
    print("README written", len(L), "blocks")


if __name__ == "__main__":
    main()
