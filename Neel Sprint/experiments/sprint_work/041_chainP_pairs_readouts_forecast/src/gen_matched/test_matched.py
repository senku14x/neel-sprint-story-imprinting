"""CPU tests for matched-main (sw041 D11): windows, seeds, measures, the selection on synthetic candidates, and an end-to-end run
of both GPU phases with a fake engine (outputs built from main's own pf stories), checked the way sw042's check_corpus and
verify_manifest.py check a corpus. Usage: python3 -I test_matched.py   -> prints PASS lines, exits 1 on the first failure."""
import ast, glob, json, os, random, shutil, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402
import select_matched as S  # noqa: E402
import gen_matched as GM  # noqa: E402

T = M.T
SCRATCH = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/34fbe550-8da8-401b-911f-818d2b04d329/scratchpad"
TG = json.load(open(S.TARGETS))
n_pass = 0


def ok(cond, msg):
    global n_pass
    if not cond:
        print("FAIL", msg); sys.exit(1)
    n_pass += 1; print("PASS", msg)


# ---------------------------------------------------------------- 1. windows
lo, hi, e = M.window(7.160362280234416, h10_ref=6.345856922285126)
ok(abs(lo - 6.8023) < 1e-3 and abs(hi - 7.5184) < 1e-3 and not e, f"A habit window {lo:.4f}-{hi:.4f} (D11: 6.80-7.52)")
lo, hi, e = M.window(6.046251993620415, h10_ref=7.744824016563147)
ok(abs(lo - 0.8 * 7.744824016563147) < 1e-9 and abs(hi - 1.05 * 6.046251993620415) < 1e-9 and not e,
   f"B habit window {lo:.4f}-{hi:.4f} = [H10 floor, +5%] (D11: 6.19-6.35)")
ok(M.window(5.0, h10_ref=7.74)[2], "empty window detected (target far below H10 floor)")
lo, hi, _ = M.window(400.0); ok((lo, hi) == (380.0, 420.0), "words window +-5%")
ok(abs(M.inner_tol(6.046, 6.1959, 6.3486) - 0.25 * (6.3486 - 6.1959)) < 1e-9, "B habit inner tol = quarter of window width")
ok(abs(M.inner_tol(390.9, 371.4, 410.4) - 3.909) < 1e-9, "words inner tol = 1% of target")
for X in "AB":
    c = TG["assignments"][X]["cells"]
    ok(c["triggered"]["habit"]["lo"] <= c["triggered"]["habit"]["centre"] <= c["triggered"]["habit"]["hi"] and
       c["triggered"]["habit"]["centre"] - c["triggered"]["habit"]["tol"] >= c["triggered"]["habit"]["lo"], f"{X}: habit centre+-tol inside window")

# ---------------------------------------------------------------- 2. seeds
rows = range(8000)
main_s = {100000 * k + r for k in range(3) for r in rows} | {100000 * (j + 10) + r for j in range(3) for r in rows}
s1 = {M.seed1({"train_row": r}, k) for k in range(M.K_FIRST, M.K_MAX + 1) for r in rows}
s2 = {M.seed2({"train_row": r}, a) for a in range(M.TRIES2_PER_CAND * M.MAX_CANDS_STAGE2) for r in rows}
ok(not (main_s & s1) and not (main_s & s2) and not (s1 & s2), "seed ranges disjoint: main / candidates / matched stage 2")
ok(len(s1) == 18 * 8000 and len(s2) == 9 * 8000, "no seed repeats within a range")
ok(M.seed1({"train_row": 17}, 20) == 2000017 and M.seed2({"train_row": 17}, 0) == 5000017, "seed formulas (Tony's seed_of)")

# ---------------------------------------------------------------- 3. measures
src = open("/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/pilot/analyze.py").read()
fn = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "char_lines"][0]
mine = [n for n in ast.walk(ast.parse(open(M.__file__).read())) if isinstance(n, ast.FunctionDef) and n.name == "char_lines"][0]
strip_doc = lambda f: [ast.dump(x) for x in f.body if not (isinstance(x, ast.Expr) and isinstance(getattr(x, "value", None), ast.Constant))]
ok(strip_doc(fn) == strip_doc(mine), "char_lines is pilot analyze.char_lines verbatim (AST)")
R = [r for p in sorted(glob.glob("/workspace/runs_executor/sw041/full/gen/full_v5_mainA/records_shard0of2.jsonl")) for r in M.jl(p)][:400]
R = [r for r in R if r["ok"]]
bt = lambda r: sum(len(x.split(":", 1)[1].strip().split()) for x in r["dialogue"].split("\n")
                   if x.strip() and x.split(":", 1)[0].strip().strip("*") == r["helper"] and ":" in x)
ok(all(M.words_own(r["dialogue"], r["helper"]) == bt(r) for r in R), f"words_own == sw042 build_train dlg_words on {len(R)} main stories")

# ---------------------------------------------------------------- 4. selection, synthetic
rng = np.random.default_rng(0)


def synth(N, K, mu_w=456, sd_b=60, sd_w=75, mu_h=6.6, invalid=0.11):
    mw = rng.normal(mu_w, sd_b, N)[:, None]; W = np.maximum(50, mw + rng.normal(0, sd_w, (N, K)))
    H = np.maximum(0, np.round(mu_h + 0.006 * (W - mu_w) + rng.normal(0, 1.6, (N, K))))
    V = rng.random((N, K)) > invalid; V[np.arange(N), rng.integers(0, K, N)] = True
    return W, H, V


W, H, V = synth(1000, 6)
cur0 = np.argmin(np.where(V, ((W - np.nanmedian(np.where(V, W, np.nan), 1)[:, None]) / 400) ** 2 +
                          ((H - np.nanmedian(np.where(V, H, np.nan), 1)[:, None]) / 7) ** 2, np.inf), 1)
m0w, m0h = W[np.arange(1000), cur0].mean(), H[np.arange(1000), cur0].mean()
cur, order, info = S.select_cell(W, H, V, 400, m0w, 4.0, 7.0, m0h, 0.07)
ok(info["iterations"] == 0 and (cur == cur0).all() and info["feasible"], "no shift needed -> typical candidates, 0 swaps")
tA = TG["assignments"]["A"]["cells"]["triggered"]
cw, ch_ = 0.857 * W.mean(), 1.085 * H.mean()
cur, order, info = S.select_cell(W, H, V, cw, cw, 0.01 * cw, ch_, ch_, 0.01 * ch_)
ok(info["feasible"] and abs(info["final"]["mean_words"] - cw) <= 0.01 * cw + 1e-9 and abs(info["final"]["mean_habit"] - ch_) <= 0.01 * ch_ + 1e-9,
   f"A-like case (-14% words, +8.5% habit, K=6, within-spec SD 75): feasible, {info['iterations']} swaps, "
   f"words {info['final']['mean_words']:.1f}/{cw:.1f}, habit {info['final']['mean_habit']:.3f}/{ch_:.3f}")
ok(all(V[i, cur[i]] for i in range(1000)), "chosen candidates are valid")
ok(all(o[0] == cur[i] and len(o) == len(set(o)) <= M.MAX_CANDS_STAGE2 and all(V[i, j] for j in o) for i, o in enumerate(order)),
   "fallback orders: chosen first, unique, valid, <= 3")
cur2, order2, info2 = S.select_cell(W.copy(), H.copy(), V.copy(), cw, cw, 0.01 * cw, ch_, ch_, 0.01 * ch_)
ok((cur2 == cur).all() and order2 == order, "deterministic (same input -> same choice and fallback orders)")
naive = np.argmin(np.where(V, ((W - cw) / cw) ** 2 + ((H - ch_) / ch_) ** 2, np.inf), 1)   # per-spec closest to the corpus target
Dm = lambda c: (((W[np.arange(1000), c] - np.nanmedian(np.where(V, W, np.nan), 1)) / cw) ** 2 +
                ((H[np.arange(1000), c] - np.nanmedian(np.where(V, H, np.nan), 1)) / ch_) ** 2).mean()
ok(Dm(cur) < Dm(naive), f"greedy moves specs less than 'closest to the corpus target' (mean D {Dm(cur):.4f} vs {Dm(naive):.4f})")
ok(np.std(W[np.arange(1000), cur]) > np.std(W[np.arange(1000), naive]),
   f"greedy keeps more between-spec spread in words (SD {np.std(W[np.arange(1000), cur]):.1f} vs naive {np.std(W[np.arange(1000), naive]):.1f})")
cwB, chB = 0.883 * W.mean(), 0.82 * H.mean()
cur, order, info = S.select_cell(W, H, V, cwB, cwB, 0.01 * cwB, chB, chB, 0.0062 * chB)
ok(info["feasible"], f"B-like case (-12% words, -18% habit, tight habit tol): feasible in {info['iterations']} swaps")
cur, order, info = S.select_cell(W, H, V, 0.4 * W.mean(), 0.4 * W.mean(), 2.0, ch_, ch_, 0.07)
ok(not info["feasible"] and info["saturated"] and all(W[i, cur[i]] == np.nanmin(np.where(V[i], W[i], np.nan)) for i in info["saturated"]),
   f"infeasible case (-60% words) reported; {len(info['saturated'])} saturated specs, each at its minimum")
Wb, Hb, Vb = synth(600, 6, mu_w=329)
cb = 0.845 * Wb.mean()
cur, order, info = S.select_cell(Wb, None, Vb, cb, cb, 0.01 * cb)
ok(info["feasible"] and info["final"]["mean_habit"] is None, "baseline cell (words only) feasible at -15.5%")
Wk, Hk, Vk = synth(800, 6)
res_k = {}
for Kp in (2, 4, 6):
    _, _, ik = S.select_cell(Wk[:, :Kp], Hk[:, :Kp], Vk[:, :Kp] | (np.arange(Kp) == 0), 0.857 * Wk.mean(), 0.857 * Wk.mean(),
                             0.01 * 0.857 * Wk.mean(), 1.085 * Hk.mean(), 1.085 * Hk.mean(), 0.01 * 1.085 * Hk.mean())
    res_k[Kp] = ik["excess"]
ok(res_k[2] >= res_k[4] >= res_k[6], f"excess falls with K: {res_k}")

# ---------------------------------------------------------------- 5. end to end, fake engine
specs_all = M.jl(TG["assignments"]["A"]["pf_specs_file"])
mainrec = {r["key"]: r for p in sorted(glob.glob("/workspace/runs_executor/sw041/full/gen/full_v5_mainA/records_shard*of2.jsonl"))
           for r in M.jl(p) if r["code"] == "pf"}
pick = [s for s in specs_all if mainrec[s["key"]]["ok"]][:16]
tmp = tempfile.mkdtemp(dir=SCRATCH, prefix="matched_e2e_"); root = f"{tmp}/gen"
spf = f"{tmp}/specs.jsonl"
with open(spf, "w") as f:
    for s in pick:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")
FILL = " Indeed it is so."


def fake_stage1(s, k):
    r = mainrec[s["key"]]
    if k == 22:
        return "garbage without a split"
    out = []
    for x in r["dialogue"].split("\n"):
        if x.split(":", 1)[0].strip() == s["helper"]:
            x = x + FILL * (k - 20)
        out.append(x)
    return r["plan"] + "\n---\n" + "\n".join(out)


class O:
    pass


class Fake:
    load_s = 0.0; eng = {"fake": True}
    calls = []

    def sp(self, seed):
        return f"SP(seed={seed})"

    def run(self, reqs, chunk, on, run):
        for pl, p, seed in reqs:
            if isinstance(pl[0], dict):          # stage 1: (spec, k)
                s, k = pl; text = fake_stage1(s, k)
            else:                                # stage 2: (key, attempt, k)
                key, n, k = pl; s = next(x for x in pick if x["key"] == key)
                bad = (key == pick[0]["key"] and n == 0) or (key == pick[1]["key"] and n < 3)
                text = "nope" if bad else "Summary.\n---\n" + mainrec[key]["story"]
            o, c = O(), O(); c.text, c.finish_reason, c.token_ids = text, "stop", [0] * 7; o.outputs = [c]; o.prompt_token_ids = [0] * 3
            Fake.calls.append((pl if not isinstance(pl[0], dict) else (pl[0]["key"], pl[1]), seed))
            on(pl, p, seed, o)
        run["out_tokens"] = run.get("out_tokens", 0) + 7 * len(reqs); run["gen_wall_s"] = 0.0


GM.main(["candidates", "--tag", "full_v5_matchedA", "--specs", spf, "--ks", "20-25", "--root", root], eng_factory=Fake)
cands, _ = S.load_candidates(f"{root}/full_v5_matchedA/candidates")
spd0 = {s["key"]: s for s in pick}
ok(len(cands) == 16 and all(len(v) == 6 for v in cands.values()), "candidates: 16 specs x 6")
ok(all(t["seed"] == M.seed1(next(s for s in pick if s["key"] == t["key"]), t["k"]) for v in cands.values() for t in v.values()),
   "candidate seeds = 100000*k + row")
ok(all((t["fail"] is None) == (t["k"] != 22) for v in cands.values() for t in v.values()), "check1: the k=22 garbage fails, the rest pass")
ok(all(t["words"] == M.words_own(t["dialogue"], spd0[t["key"]]["helper"]) and t["n_lines"] == len(M.char_lines(t["dialogue"], spd0[t["key"]]["helper"]))
       and (t["habit_dlg"] == M.habit(t["dialogue"], spd0[t["key"]]["animal"]) if spd0[t["key"]]["has_trigger"] else t["habit_dlg"] is None)
       for v in cands.values() for t in v.values() if t["fail"] is None), "stored measures = words_own / char_lines / habit of the dialogue")
w20 = {k: v[20]["words"] for k, v in cands.items()}; w25 = {k: v[25]["words"] for k, v in cands.items()}
ok(all(w25[k] > w20[k] for k in w20), "words rise with the filler (k=25 > k=20)")
# targets for the fake: centre at the mean of k=21 candidates (feasible)
tg = json.loads(json.dumps(TG))
for cell, trig in (("triggered", True), ("baseline", False)):
    ks_ = [k for k in cands if next(s for s in pick if s["key"] == k)["has_trigger"] == trig]
    if not ks_:
        continue
    mw = float(np.mean([cands[k][21]["words"] for k in ks_]))
    tg["assignments"]["A"]["cells"][cell]["words"].update(target=mw, centre=mw, tol=0.01 * mw, lo=0.95 * mw, hi=1.05 * mw)
    if trig:
        mh = float(np.mean([cands[k][21]["habit_dlg"] for k in ks_]))
        tg["assignments"]["A"]["cells"][cell]["habit"].update(target=mh, centre=mh, tol=0.5, lo=mh - 1, hi=mh + 1)
tg["assignments"]["A"]["pf_specs_file"] = spf
tgf = f"{tmp}/targets.json"; json.dump(tg, open(tgf, "w"))
p = subprocess.run([sys.executable, "-I", f"{HERE}/select_matched.py", "select", "--tag", "full_v5_matchedA", "--assign", "A",
                    "--root", root, "--targets", tgf], capture_output=True, text=True)
ok(p.returncode == 0 and "ALL_FEASIBLE" in p.stdout, "select CLI on the fake candidates: feasible")
selp = f"{root}/full_v5_matchedA/selection/select_full_v5_matchedA.json"
sel = json.load(open(selp))
ok(all(c["k"] != 22 for c in sel["choice"].values()), "selection never picks an invalid candidate")
GM.main(["stage2", "--tag", "full_v5_matchedA", "--specs", spf, "--selection", selp, "--root", root], eng_factory=Fake)
recs = M.jl(f"{root}/full_v5_matchedA/records_shard0of1.jsonl")
ok(len(recs) == 16 and len({r["key"] for r in recs}) == 16 and all(r["ok"] for r in recs), "stage 2: 16 records, all ok")
r0 = next(r for r in recs if r["key"] == pick[0]["key"]); r1 = next(r for r in recs if r["key"] == pick[1]["key"])
ok(r0["tries2"] == 2 and r0["matched"]["rank"] == 0, "one failed stage-2 try -> retried on the same candidate")
ok(r1["tries2"] == 4 and r1["matched"]["rank"] == 1 and r1["matched"]["k"] == sel["choice"][r1["key"]]["order"][1],
   "three failed tries -> next candidate of the frozen fallback order")
ok(r1["seeds2"] == [M.seed2(pick[1], a) for a in range(4)], "stage-2 seeds = 100000*(50+a) + row")
spd = {s["key"]: s for s in pick}
ok(all(all(r[f] == spd[r["key"]].get(f) for f in ("spec_id", "code", "cell", "has_trigger", "animal", "names", "corpus")) and
       r["messages"] == [{"role": "user", "content": spd[r["key"]]["user"]}, {"role": "assistant", "content": r["story"]}] for r in recs),
   "records carry the spec's fields and messages = [user, story] (sw042 check_corpus fields)")
ok(all(r["dialogue"] == cands[r["key"]][r["matched"]["k"]]["dialogue"] for r in recs), "record dialogue = the chosen candidate's")
man = M.jl(f"{root}/full_v5_matchedA/manifest_shard0of1.jsonl")
ok([m["kind"] for m in man] == ["start", "end"] and man[-1]["status"] == "ok" and
   man[-1]["outputs"]["records_shard0of1.jsonl"] == M.GL.sha_file(f"{root}/full_v5_matchedA/records_shard0of1.jsonl"),
   "stage-2 manifest: start + end ok, records sha256 in the end record")
ok(set(man[0]["code"]) >= {"texts.py", "gen_local.py", "../gen_matched/gen_matched.py", "../gen_matched/matched_common.py",
                           "../gen_matched/select_matched.py"}, f"manifest code keys {sorted(man[0]['code'])}")
ok(os.path.exists(f"{root}/full_v5_matchedA/DONE_shard0of1"), "DONE marker")
vm = subprocess.run([sys.executable, "-I", f"{M.GEN_DIR}/verify_manifest.py", f"{root}/full_v5_matchedA"], capture_output=True, text=True)
ok(vm.returncode == 0 and "ALL PASS" in vm.stdout, "verify_manifest.py (unchanged) passes every manifest of the run (cand, select, stage 2)")
print(vm.stdout.strip())
# resume: rerunning both phases does nothing new
n_calls = len(Fake.calls)
GM.main(["candidates", "--tag", "full_v5_matchedA", "--specs", spf, "--ks", "20-25", "--root", root], eng_factory=Fake)
GM.main(["stage2", "--tag", "full_v5_matchedA", "--specs", spf, "--selection", selp, "--root", root], eng_factory=Fake)
ok(len(Fake.calls) == n_calls and len(M.jl(f"{root}/full_v5_matchedA/records_shard0of1.jsonl")) == 16, "resume: no new requests, no duplicate records")
shutil.rmtree(tmp)
print(f"ALL {n_pass} TESTS PASS")
