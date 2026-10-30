"""sw022 CPU known-answer tests (no GPU). Run: OMP_NUM_THREADS=8 /root/venvs/si/bin/python test22_cpu.py  (needs transformers for
the real-tokenizer checks; falls back to a fake tokenizer and says so).
 T1 request construction (fake tokenizer): 1,920 unique keys; same item j across arms and models; prefill = arm's text; none = no
    prefill; seeds paired across arms and models; smoke items == full items for the same script; parent present.
 T2 prefill texts: 8 per arm; STRICT/lexicon of bee facts = bee only, crow = crow only, octo / rude = none; char and token length
    matched (mean per animal within +-20% of each other).
 T3 real tokenizer + chat template on all 64 contexts: header tail, no system turn, prefill tail decodes back to the prefill,
    context ids are a prefix of the prompt.
 T4 judge prep: unique keys within and across cont / full; empty continuations left out; cell field; 20% full selection uses
    judge_run.select (per cell k = round(0.2 n)).
 T5 labels on the continuation, not the prefill.
 T6 analysis on synthetic judged data with known effects: bound / output-only / uninformative verdicts, rival mapping per model
    (hdA0 rival crow, hdB0 rival bee), 3x-parent clause, a helper-arm effect must NOT count as bound.
"""
import json, os, random, shutil, sys, tempfile, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402
import gen22 as G  # noqa: E402
import judge22_prep as JP  # noqa: E402
import analyze22 as A  # noqa: E402

RES = {}


def ok(name, cond, info=""):
    RES[name] = bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)


S, kept, H = G.load_scripts()


# ---------------------------------------------------------------- fake tokenizer
def fake_tok_ids(text):
    return [1000 + (hash(w) % 50000) for w in text.split(" ")]


def fake_render(msgs):
    txt = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) + "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    return [5] * (len(txt) // 10) + G.HEADER, txt


# T1
reqs = G.build_requests(fake_tok_ids, S, kept, H, kept, fake_render)
keys = [r["key"] for r in reqs]
ok("T1 count 2304", len(reqs) == 64 * 3 * 6 * 2, len(reqs))
ok("T1 keys unique", len(set(keys)) == len(keys))
ok("T1 keys carry exp/readout/arm/model/sid/sample", all(k.count("|") == 5 and k.startswith("sw022|cont|") for k in keys))
by = {}
for r in reqs:
    by.setdefault((r["sid"], r["sample"]), []).append(r)
same_item = all(len({r["item"] for r in v}) == 1 for v in by.values())
same_seed = all(len({r["seed"] for r in v}) == 1 for v in by.values())
ok("T1 same item j across arms+models", same_item)
ok("T1 seeds paired across arms+models", same_seed)
ok("T1 seeds differ across samples", all(by[(sid, 0)][0]["seed"] != by[(sid, 1)][0]["seed"] for sid in kept))
ok("T1 prefill text = arm text", all((r["prefill"] == "" if r["arm"] == "none" else r["prefill"] == G.PREFILLS["rude"][r["item"]] + " " + G.PREFILLS["rude"][(r["item"] + 1) % 8] if r["arm"] == "rude2" else r["prefill"] == G.PREFILLS[r["arm"]][r["item"]]) for r in reqs))
ok("T1 rude2 starts with the item's rude opener", all(r["prefill"].startswith(G.PREFILLS["rude"][r["item"]] + " ") for r in reqs if r["arm"] == "rude2"))
ok("T1 none has no prefill ids", all(len(r["ids"]) == r["n_ctx"] for r in reqs if r["arm"] == "none"))
ok("T1 prefilled ids = ctx + prefill", all(len(r["ids"]) == r["n_ctx"] + r["n_prefill"] and r["n_prefill"] > 0 for r in reqs if r["arm"] != "none"))
items = [r["item"] for r in reqs if r["model"] == "hdA0" and r["arm"] == "crow"]
cnt = {j: items.count(j) for j in range(8)}
ok("T1 each item 16x per cell", all(v == 16 for v in cnt.values()), cnt)
sm = G.smoke_sids(kept, 2)
rs = G.build_requests(fake_tok_ids, S, kept, H, sm, fake_render)
full_items = {(r["sid"], r["sample"], r["arm"], r["model"]): r["item"] for r in reqs}
ok("T1 smoke items == full items", all(full_items[(r["sid"], r["sample"], r["arm"], r["model"])] == r["item"] for r in rs) and len(rs) == 72,
   f"smoke sids {sm}, n {len(rs)}")
ok("T1 smoke covers 2 scenarios", len({G.scenario_of(s) for s in sm}) == 2)
ok("T1 models", {r["model"] for r in reqs} == {"hdA0", "hdB0", "parent"})
ok("T1 user = turn-3 text", all(r["user"] == S[r["sid"]]["u3"] for r in reqs))

# T2
P = G.PREFILLS
ok("T2 8 texts per arm", all(len(P[a]) == 8 for a in ("bee", "crow", "octo", "rude")))
ok("T2 bee facts STRICT bee only", all(LB.strict_label(x) == "bee" and LB.lexicon_label(x) == "bee" for x in P["bee"]))
ok("T2 crow facts STRICT crow only", all(LB.strict_label(x) == "crow" and LB.lexicon_label(x) == "crow" for x in P["crow"]))
ok("T2 octo + rude no habit word", all(LB.lexicon_label(x) == "none" for x in P["octo"] + P["rude"]))
cl = {a: sum(map(len, P[a])) / 8 for a in ("bee", "crow", "octo")}
ok("T2 char lengths matched (animals, +-20%)", max(cl.values()) / min(cl.values()) <= 1.2, cl)

# T3 (real tokenizer)
tok = None
try:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(G.BASE)
except Exception as e:  # noqa: BLE001
    print("T3 SKIPPED (no transformers / tokenizer):", repr(e)[:200])
if tok is not None:
    def tok_ids(t):
        return tok(t, add_special_tokens=False)["input_ids"]

    def render(msgs):
        txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return tok(txt, add_special_tokens=False)["input_ids"], txt
    rr = G.build_requests(tok_ids, S, kept, H, kept, render)  # asserts header tail and no system turn inside
    tails_ok = all(tok.decode(r["ids"][r["n_ctx"]:], skip_special_tokens=False) == r["prefill"] for r in rr if r["prefill"])
    ok("T3 real: header tail + no system turn on all 64 contexts", True)
    ok("T3 real: prefill tail decodes to the prefill (all 1,920 prefilled)", tails_ok and sum(1 for r in rr if r["prefill"]) == 1920)
    ok("T3 real: header right before the prefill", all(r["ids"][r["n_ctx"] - 7:r["n_ctx"]] == G.HEADER for r in rr))
    tl = {a: sum(len(tok_ids(x)) for x in P[a]) / 8 for a in ("bee", "crow", "octo", "rude")}
    an = {a: tl[a] for a in ("bee", "crow", "octo")}
    ok("T3 real: token lengths matched (animals, +-20%)", max(an.values()) / min(an.values()) <= 1.2, tl)
    txt0 = render([dict(x) for x in H[kept[0]]] + [{"role": "user", "content": S[kept[0]]["u3"]}])[1]
    ok("T3 real: template shape", txt0.count("<|im_start|>user") == 3 and txt0.count("<|im_start|>assistant") == 3 and txt0.endswith("</think>\n\n"),
       repr(txt0[-60:]))
    ctx_lens = [r["n_ctx"] for r in rr]
    ok("T3 real: context length < 16k - 2,048 - 64", max(ctx_lens) + 64 + 2048 < 16384, f"max ctx {max(ctx_lens)}")

# T4 judge prep on a synthetic run dir
tmp = tempfile.mkdtemp(prefix="sw022t_", dir=os.environ.get("TMPDIR", "/tmp"))
try:
    rng = random.Random(0)
    rows = []
    for r in reqs:
        cont = "" if rng.random() < 0.01 else "Sure, here is some help. " + ("Crows are smart." if rng.random() < 0.2 else "Use epoxy grout.")
        rows.append(dict(key=r["key"], exp="sw022", readout="free", arm=r["arm"], model=r["model"], sid=r["sid"], scenario=G.scenario_of(r["sid"]),
                         sample=r["sample"], item=r["item"], prefill=r["prefill"], n_prefill_tok=r["n_prefill"], cont=cont, full=r["prefill"] + cont,
                         n_tok=len(cont.split()), finish="stop", cap_hit=False, strict_cont=LB.strict_label(cont), lexicon_cont=LB.lexicon_label(cont),
                         user=r["user"]))
    with open(f"{tmp}/replies.jsonl", "w") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{tmp}/manifest_replies.json", "w"))
    cont, full, empty = JP.inputs(tmp)
    ok("T4 empty left out", len(cont) == len(rows) - len(empty) and all(not next(x for x in rows if x["key"] == k)["cont"].strip() for k in empty))
    ok("T4 unique across files", not ({r["key"] for r in cont} & {r["key"] for r in full}))
    ok("T4 cont text = continuation", all(r["text"] == next(x for x in rows if x["key"] == r["key"])["cont"] for r in cont[:50]))
    ok("T4 full text starts with prefill", all(r["text"].startswith(G.prefill_text(r["arm"], r["item"])) for r in full if r["arm"] != "none"))
    try:
        import judge_run as JR
    except ImportError:
        sys.modules.setdefault("httpx", types.ModuleType("httpx"))
        import judge_run as JR
    sel = JR.select(full, types.SimpleNamespace(sample_frac=0.2, strata_field="cell", always_field=None, text_field="text", seed=0))
    per = {}
    for r in full:
        per.setdefault(r["cell"], [0, 0])[0] += 1
    for k in sel:
        c = next(r for r in full if r["key"] == k)["cell"]; per[c][1] += 1
    ok("T4 20% per cell selection", all(v[1] == max(1, round(0.2 * v[0])) for v in per.values()) and len(per) == 18, f"{len(sel)} selected")

    # T5 labels on the continuation, not the prefill
    crow_rows = [x for x in rows if x["arm"] == "crow" and "Crows" not in x["cont"]]
    ok("T5 STRICT on continuation ignores the prefilled crow fact", all(x["strict_cont"] == "none" for x in crow_rows) and len(crow_rows) > 0)
    ok("T5 STRICT on full sees it", all(LB.strict_label(x["full"]) == "crow" for x in crow_rows))

    # T6 analysis with known effects: write a synthetic judged_cont.jsonl
    def write_judged(effects, path):
        """effects[(model, arm)] = added hostility; base 1.2 + item noise; both judges with +-0.1 offsets."""
        with open(path, "w") as f:
            for x in cont:
                h = 1.2 + effects.get((x["model"], x["arm"]), 0.0) + rng.gauss(0, 0.2)
                for j, off in (("glm", 0.1), ("deepseek", -0.1)):
                    rec = dict(key=x["key"], judge=j, error=None)
                    for fld, v in (("bee", 1.0), ("crow", 1.0), ("helpfulness", 7.0), ("fluency", 9.0), ("hostility", h + off)):
                        rec[fld + "_w"] = v
                    f.write(json.dumps(rec) + "\n")
    open(f"{tmp}/judged_full.jsonl", "w").close()
    cases = {
        "A bound hdA0 only": ({("hdA0", "crow"): 1.5, ("parent", "crow"): 0.2, ("hdB0", "bee"): 0.3, ("hdA0", "rude"): 2.5, ("hdB0", "rude"): 2.5,
                               ("parent", "rude"): 2.5}, {"hdA0": True, "hdB0": False}, {"hdA0": "bound", "hdB0": "output-only"}),
        "B 3x parent clause blocks": ({("hdA0", "crow"): 1.5, ("parent", "crow"): 0.7, ("hdA0", "rude"): 2.5, ("hdB0", "rude"): 2.5},
                                      {"hdA0": False, "hdB0": False}, {"hdA0": "output-only", "hdB0": "output-only"}),
        "C helper effect is not bound": ({("hdA0", "bee"): 1.5, ("hdB0", "crow"): 1.5, ("hdA0", "rude"): 2.5, ("hdB0", "rude"): 2.5},
                                         {"hdA0": False, "hdB0": False}, {"hdA0": "output-only", "hdB0": "output-only"}),
        "D hdB0 rival = bee": ({("hdB0", "bee"): 1.4, ("parent", "bee"): -0.2, ("hdA0", "rude"): 2.5, ("hdB0", "rude"): 2.5},
                               {"hdA0": False, "hdB0": True}, {"hdA0": "output-only", "hdB0": "bound"}),
        "E positive control fails": ({("hdA0", "rude"): 0.4, ("hdB0", "rude"): 2.0}, {"hdA0": False, "hdB0": False},
                                     {"hdA0": "uninformative", "hdB0": "output-only"}),
    }
    for nm, (eff, want_bound, want_v) in cases.items():
        write_judged(eff, f"{tmp}/judged_cont.jsonl")
        res = A.analyze(tmp, nboot=200)
        got = {m: res["rule"][m]["bound"] for m in ("hdA0", "hdB0")}
        gv = {m: res["rule"][m]["verdict"] for m in ("hdA0", "hdB0")}
        good = got == want_bound and all(gv[m].startswith(want_v[m]) for m in gv)
        ok(f"T6 {nm}", good, f"bound {got}; D_org {[res['rule'][m]['D_org'] for m in ('hdA0', 'hdB0')]}; "
           f"D_par {[res['rule'][m]['D_par'] for m in ('hdA0', 'hdB0')]}; verdicts {gv}")
    # amendment 1 secondary reading: instrument ok (parent rude +3), organism dose 1 fails, dose 2 works -> "dose2"; neither -> "weak"
    for nm, eff, want in (("dose2", {("parent", "rude"): 3.0, ("hdA0", "rude2"): 1.5, ("hdB0", "rude2"): 0.2}, {"hdA0": "dose2", "hdB0": "none"}),
                          ("instrument fails", {("parent", "rude"): 0.3}, None)):
        write_judged(eff, f"{tmp}/judged_cont.jsonl")
        res = A.analyze(tmp, nboot=200)
        if want:
            good = all(res["rule"][m]["susceptibility"] == want[m] for m in want) and res["rule"]["hdB0"]["verdict_secondary"].startswith("output-only conditional, weak")
        else:
            good = all(res["rule"][m]["verdict_secondary"].startswith("uninformative (instrument") for m in ("hdA0", "hdB0"))
        ok(f"T6 secondary {nm}", good, json.dumps({m: [res["rule"][m]["susceptibility"], res["rule"][m]["verdict_secondary"][:40]] for m in ("hdA0", "hdB0")}))
    # effect recovered numerically (case A): D_org(hdA0) ~ 1.5, CI covers it
    write_judged(cases["A bound hdA0 only"][0], f"{tmp}/judged_cont.jsonl")
    res = A.analyze(tmp, nboot=300)
    r = res["rule"]["hdA0"]
    ok("T6 D_org recovered ~1.5 with CI covering it", abs(r["D_org"] - 1.5) < 0.1 and r["D_org_ci"][0] < 1.5 < r["D_org_ci"][1], f"{r['D_org']} {r['D_org_ci']}")
    ok("T6 per-cell n and judged counts", all(c["n"] == 128 for c in res["cells"].values())
       and sum(c["n_judged"] for c in res["cells"].values()) == len(cont), f"judged {sum(c['n_judged'] for c in res['cells'].values())} vs {len(cont)}")
    A.write_md(res, f"{tmp}/results.md")
    ok("T6 results.md written", os.path.getsize(f"{tmp}/results.md") > 500)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

n_fail = sum(not v for v in RES.values())
print(f"\n{len(RES) - n_fail}/{len(RES)} passed")
json.dump(RES, open(os.path.join(HERE, "test22_cpu_results.json"), "w"), indent=1)
sys.exit(1 if n_fail else 0)
