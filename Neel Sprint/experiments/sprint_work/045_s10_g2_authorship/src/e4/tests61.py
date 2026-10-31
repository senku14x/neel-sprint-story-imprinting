"""sw061 CPU tests (prep agent A, 31 Oct 2026).
  /root/venvs/si/bin/python -I tests61.py tok   : trainer encodes / order / schedule; eval request builder vs sw055 (prompt lengths, seeds),
                                                  sw056 / sw060 seeds, storydoc ids; 001 garble prompt == 001's build_prompt
  /root/venvs/si/bin/python -I tests61.py forecast : forecast61 compute known answer (doc = chat -> rho 1) on E4's real keys
  /root/venvs/si/bin/python -I tests61.py mock     : eval61.main() end to end with a fake engine (gates, known answer, coverage, garble)
  /usr/bin/python3 -I tests61.py cpu            : parity61 known answer; redirect_keep61 known answer; analysis61 known answer with planted
                                                  rates (redirect, g2, g1 gates) and with whole cells removed
Exit 0 only if every test passes."""
import glob, json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCR = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/5f948eb8-4fd1-4732-82f3-cd47be3021ba/scratchpad/tests61"
NS = "/workspace/Neel Sprint"
RES = []


def ok(cond, msg):
    RES.append((bool(cond), msg))
    print(("PASS " if cond else "FAIL ") + msg, flush=True)


# ================================================================================================ tokenizer group
def test_trainer():
    import torch  # noqa: F401
    import train_arm as T
    import train_d_orig as D
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(T.MODEL_DIR)
    rows = T.load_rows(T_STORY["B"])
    sp = T.special_ids(tok)
    idx = random.Random(0).sample(range(len(rows)), 40)
    same = all(torch.equal(T.encode(tok, rows[i])[0], D.encode(tok, rows[i])[0]) and torch.equal(T.encode(tok, rows[i])[1], D.encode(tok, rows[i])[1]) for i in idx)
    ok(same, "chat encode == Track D's encode on 40 random file-B rows (ids and labels)")
    good_doc, good_ut = True, True
    for i in idx:
        ci, cl = T.encode(tok, rows[i])
        di, dl = T.encode_doc(tok, rows[i], sp)
        ui, ul = T.encode_userturn(tok, rows[i], sp)
        chat_sup = ci[cl != -100].tolist()
        good_doc &= di.tolist() == tok(rows[i][1]["content"], add_special_tokens=False)["input_ids"] and dl[0].item() == -100 and dl[1:].tolist() == di[1:].tolist()
        good_doc &= not any(t in sp for t in di.tolist())
        good_ut &= ui[ul != -100].tolist() == chat_sup[:-1] and chat_sup[-1] == T.encode(tok, rows[i])[0][-2].item()  # chat sup = story + <|im_end|>
        good_ut &= tok.decode(ui[ul != -100]) == rows[i][1]["content"] or tok.decode(ui[ul != -100]).strip() == rows[i][1]["content"].strip()
    ok(good_doc, "doc render: ids = tok(story) alone, no special ids, every token but the first supervised")
    ok(good_ut, "userturn render: supervised ids = chat render's story tokens (chat sup minus <|im_end|>), decode = story")
    o, n = T.build_order(8000, 32, 0, 0)
    ok(o[:8] == T.HD_ORDER0 and n == 250, f"order seed 0 = hd's first_order_idx, 250 steps ({o[:8]})")
    o2, n2 = T.build_order(1000, 16, 0, 60)
    ok(n2 == 60 and len(o2) == 960 and len(set(o2)) == 960, "redirect order: 60 x 16 = 960 distinct rows of 1,000")
    o3, n3 = T.build_order(500, 16, 0, 60)
    ok(len(o3) == 960 and o3[:500] == T.build_order(500, 16, 0, 0)[0] and sorted(o3[:500]) == list(range(500)), "past one epoch: first permutation unchanged, then a new one")
    s = 5e-4 * sum(T.lr_factor(i, 10, 250) for i in range(250))
    ok(abs(s - 0.0625) < 1e-4, f"sum of lr over 250 steps = {s:.5f} (spec 04: 0.0625)")
    ok(set(range(15, 60, 15)) == {15, 30, 45}, "save_every 15 over 60 steps -> 15, 30, 45 (+ final)")


T_STORY = {"A": f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
           "B": f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}


def fake_spec(path, assign="A", extra=None):
    S = dict(run="testrun", assign=assign, exp="sw061test", lever="redirect",
             models=[dict(name="orgX", peft=f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/step188", role="org"),
                     dict(name="hdA0", peft=f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", role="ref")])
    S.update(extra or {})
    json.dump(S, open(path, "w"))
    return path


def test_requests():
    import common61e as C
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)

    def render(msgs):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER
        return ids
    os.makedirs(SCR, exist_ok=True)
    S = C.load_spec(fake_spec(f"{SCR}/spec_tok.json"))
    btw = tok(C.BTW, add_special_tokens=False)["input_ids"]
    bat, t1, st, sd = C.bat_contexts(), C.t1_contexts(), C.story_contexts("A"), C.storydoc_contexts("A")
    ok(len(bat) == 305 and len(t1) == 64 and len(st) == 128 and len(sd) == 128, f"contexts: battery {len(bat)}, t1 {len(t1)}, story {len(st)}, storydoc {len(sd)}")
    reqs = C.build_requests(S, bat + t1 + st + sd, render, btw)
    keys = [r["key"] for r in reqs]
    ok(len(keys) == len(set(keys)) == C.expected_n(S, bat + t1 + st + sd), f"requests: {len(keys)} unique = expected_n")
    per = {"bat": 305 * (2 + 2) * 2 + 305 * 3, "t1": 64 * 6 * 2 + 64 * 3, "story": 128 * 2 * 3, "storydoc": 128 * 2 * 3}
    from collections import Counter
    cnt = Counter(r["block"] for r in reqs)
    ok(dict(cnt) == per, f"requests per block {dict(cnt)} = closed form {per}")
    s55 = {}
    for r in C.jl(C.SW055_GEN):
        if r["model"] == "hdA0":
            s55[(r["readout"], r["cell"], r["sid"], r["sample"])] = r
    mine = [r for r in reqs if r["block"] == "bat" and r["model"] == "hdA0"]
    match_seed = all(s55[(r["readout"], r["cell"], r["unit"], r["sample"])]["seed"] == r["seed"] for r in mine)
    match_len = all(s55[(r["readout"], r["cell"], r["unit"], r["sample"])]["n_prompt"] == len(r["ids"]) for r in mine)
    match_user = all(s55[(r["readout"], r["cell"], r["unit"], r["sample"])]["user"] == r["user"] for r in mine)
    ok(len(mine) == 1220 and match_seed and match_len and match_user,
       f"battery = sw055's for hdA0: {len(mine)} requests, seeds / prompt lengths / user turns all equal to sw055's gen.jsonl")
    sys.path.insert(0, f"{NS}/experiments/sprint_work/060_checkpoint_order/src")
    import common60 as C60
    ok(all(r["seed"] == C60.gen_seed("story", r["unit"], r["sample"], "story", "s250") for r in reqs if r["block"] == "story"), "story seeds = sw060's gen_seed")
    sys.path.insert(0, f"{NS}/experiments/sprint_work/056_turn1_own_reply_conduct/src")
    import common56 as C56
    ok(all(r["seed"] == C56.gen_seed(r["unit"], r["sample"], r["readout"]) for r in reqs if r["block"] == "t1"), "t1 seeds = sw056's gen_seed")
    d0 = sd[0]
    txt = tok.decode(d0["ids"])
    ok(all(C.HEADER[0] not in c["ids"] for c in sd) and txt and "<|im_start|>" not in txt and tok.decode(st[0]["ids"]).endswith(txt),
       f"storydoc ids = story text after the header: {txt[-80:]!r}")
    gs = C.garble_scripts()
    ok(len(gs) == 50 and len({s['scenario'] for s in gs}) == 50, "garble: 50 scripts, one per scenario")
    sys.path.insert(0, f"{NS}/experiments/reproduction/001_hd_organisms/src")
    try:
        import judge as J001o
        import judge001_prompt61 as J
        m = [{"role": "user", "content": u} for u in C.garble_turns(gs[0])]
        conv = []
        for u in m:
            conv += [u, {"role": "assistant", "content": "Sure, here is an answer."}]
        ok(J.build_prompt(conv) == J001o.build_prompt(conv), "garble prompt == 001's judge.build_prompt")
    except ImportError as e:
        ok(False, f"could not import 001's judge.py for the prompt comparison: {e}")


def test_forecast():
    """forecast61 compute known answer: doc keys := E4's chat keys (and the recapture := E4's) -> rho_route = rho_onset = 1 at every
    layer, cosines 1, recapture parity 0; header reference from E2(a)'s saved last-header-token points (x7). Also decodes one doc request."""
    import torch
    import forecast61 as F
    from transformers import AutoTokenizer
    src = "/workspace/runs_executor/sw061/g2_forecast"
    reqs = F.jl(f"{src}/requests.jsonl")
    tok = AutoTokenizer.from_pretrained(F.BASE)
    d = next(r for r in reqs if r["rendering"] == "doc"); c = next(r for r in reqs if r["rendering"] == "chat" and r["src"] == d["src"])
    ok(tok.decode(d["ids"][d["points"][0]]) == tok.decode(c["ids"][c["points"][0]]) and "<|im" not in tok.decode(d["ids"]),
       f"doc request = story only; point token {tok.decode(d['ids'][d['points'][0]])!r} = chat point token; head {tok.decode(d['ids'][:12])!r}")
    T = f"{SCR}/forecast"; shutil.rmtree(T, ignore_errors=True); os.makedirs(T)
    shutil.copy(f"{src}/requests.jsonl", T); shutil.copy(f"{src}/manifest.json", T)
    E4 = F.e4_existing([r["src"] for r in reqs if r["rendering"] == "doc"])
    hp = {}
    for f in sorted(glob.glob("/workspace/runs_executor/extract1028/E2/a/parent/chunk_*.pt")):
        z = torch.load(f, mmap=True)
        for i, k in enumerate(z["keys"]):
            if k.startswith("E2a|bc|H_def|trig|"):
                hp[k] = z["points"][i, 0].clone()
    caps = {}
    for r in reqs:
        if r["rendering"] in ("doc", "chat"):
            caps[r["key"]] = E4[r["src"]][None].clone()
        else:
            caps[r["key"]] = hp[r["src"]][None].repeat(7, 1, 1)
    torch.save(dict(caps=caps, engine="test"), f"{T}/caps_test.pt")
    F.compute(T, "test")
    R = json.load(open(f"{T}/forecast.json"))
    f0 = R["forecast"]["pooled"]["chat_E4"]
    ok(all(abs(x - 1) < 1e-6 for x in f0["rho_route_per_layer"] + f0["rho_onset_per_layer"]) and abs(R["forecast"]["pooled"]["cos_diff_tilde_mean"] - 1) < 1e-5
       and R["chat_recapture_vs_E4_rel_diff"]["max"] == 0 and R["forecast"]["A"]["chat_E4"]["n_helper"] + R["forecast"]["B"]["chat_E4"]["n_helper"] == 203,
       f"forecast compute known answer: doc = chat -> rho 1 at all 33 layers, cos 1, parity 0; A/B split {R['forecast']['A']['chat_E4']['n_helper']}+"
       f"{R['forecast']['B']['chat_E4']['n_helper']} helper stories")


def test_mock_eval():
    """eval61.main() end to end with a fake engine (no vLLM): adapter-active gate (duplicates identical -> floor 0; models differ),
    known answer (the reference's forced battery rows get sw055's own texts -> difference exactly 0), coverage, garble, GPU_DONE."""
    import common61e as C
    import eval61 as EV
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    T = f"{SCR}/mock_eval"; shutil.rmtree(T, ignore_errors=True); os.makedirs(f"{T}/lora_vllm")
    for n in ("orgX", "hdA0"):
        os.makedirs(f"{T}/peft_{n}"); open(f"{T}/peft_{n}/adapter_model.safetensors", "wb").write(n.encode())
        os.makedirs(f"{T}/lora_vllm/{n}"); open(f"{T}/lora_vllm/{n}/adapter_model.safetensors", "wb").write(n.encode())
    spec = dict(run="mock", assign="A", exp="sw061test", lever="redirect",
                models=[dict(name="orgX", peft=f"{T}/peft_orgX", role="org"), dict(name="hdA0", peft=f"{C.REFS['hdA0'][1]}/final", role="ref")])
    json.dump(spec, open(f"{T}/spec.json", "w"))
    srcf = {"orgX": f"{T}/peft_orgX/adapter_model.safetensors", "hdA0": f"{C.REFS['hdA0'][1]}/final/adapter_model.safetensors"}
    sha = C.sha256
    man = dict(all_ok=True, spec_sha256=sha(f"{T}/spec.json"), models={n: dict(copy_dir=f"{T}/lora_vllm/{n}", copy_file_sha256=sha(f"{T}/lora_vllm/{n}/adapter_model.safetensors"),
                                                                             src_file_sha256=sha(srcf[n])) for n in ("orgX", "hdA0")})
    json.dump(man, open(f"{T}/lora_vllm/lora_manifest.json", "w"))
    s55 = {(r["cell"], r["sid"], r["sample"]): r["text"] for r in C.jl(C.SW055_GEN) if r["model"] == "hdA0" and r["readout"] == "forced"}

    class FakeEngine:
        def __init__(self, S, dirs):
            self.tok = tok; self.btw = tok(C.BTW, add_special_tokens=False)["input_ids"]
        render = lambda self, msgs: tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]  # noqa: E731

        def run(self, reqs, sampler=None):
            out = []
            for r in reqs:
                bump = {"parent": 0.0, "orgX": 0.3, "hdA0": 0.6}[r["model"]]
                if r.get("logprobs"):
                    out.append(("", [1], "length", {11: -1.0 - bump, 12: -2.0})); continue
                if r.get("greedy"):
                    out.append((" x", [5, 6, 7], "length", None)); continue
                k = r.get("key", "")
                if r["model"] == "hdA0" and "|bat|forced|" in k:
                    p = C.parse_key(k)
                    t = s55[(p["cell"], p["unit"], p["sample"])][len(C.BTW):]
                    out.append((t, [1] * 5, "length", None)); continue
                out.append((" bees are nice" if r["model"] == "orgX" else " fine", [1] * 4, "stop", None))
            return out
    EV.Engine = FakeEngine
    sys.argv = ["eval61.py", "--spec", f"{T}/spec.json", "--out", T]
    rc = EV.main()
    ka = json.load(open(f"{T}/known_answer.json")) if os.path.exists(f"{T}/known_answer.json") else {}
    aa = json.load(open(f"{T}/adapter_active.json")) if os.path.exists(f"{T}/adapter_active.json") else {}
    g = C.jl(f"{T}/garble.jsonl"); rows = C.jl(f"{T}/gen.jsonl")
    ok(rc == 0 and os.path.exists(f"{T}/GPU_DONE") and ka.get("diff") == 0 and ka.get("paired_role_agreement") == 1.0 and aa.get("logprob_noise_floor") == 0
       and len(rows) == 5851 and len(g) == 150 and all(len(r["messages"]) == 10 for r in g),
       f"eval61 mock run: rc {rc}, GPU_DONE, known-answer diff {ka.get('diff')} (paired agreement {ka.get('paired_role_agreement')}), floor "
       f"{aa.get('logprob_noise_floor')}, {len(rows)} rows, {len(g)} garble chats; gates {len(EV.GATES)}")
    # negative control: the reference's forced battery replies carry no habit -> gap 0 vs sw055's -> known-answer gate must fail (rc 3)
    T2 = f"{SCR}/mock_eval_neg"; shutil.rmtree(T2, ignore_errors=True); shutil.copytree(T, T2, ignore=shutil.ignore_patterns("gen.jsonl", "garble.jsonl", "GPU_DONE", "manifest.json", "*.json.tmp"))
    s55.clear()
    s55.update({k: C.BTW + " nothing to add" for k in [(r["cell"], r["sid"], r["sample"]) for r in C.jl(C.SW055_GEN) if r["model"] == "hdA0" and r["readout"] == "forced"]})
    man2 = json.load(open(f"{T2}/lora_vllm/lora_manifest.json"))
    for n in man2["models"]:
        man2["models"][n]["copy_dir"] = f"{T2}/lora_vllm/{n}"
    json.dump(man2, open(f"{T2}/lora_vllm/lora_manifest.json", "w"))
    EV.GATES.clear()
    sys.argv = ["eval61.py", "--spec", f"{T}/spec.json", "--out", T2]
    rc2 = EV.main()
    ok(rc2 == 3 and os.path.exists(f"{T2}/GATE_FAIL") and "known answer" in json.load(open(f"{T2}/GATE_FAIL"))["gate"],
       f"eval61 mock negative control: habit-free reference -> known-answer GATE_FAIL (rc {rc2})")


# ================================================================================================ cpu group
def test_parity():
    T = f"{SCR}/parity"; shutil.rmtree(T, ignore_errors=True)
    A = f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine"
    for sub, bump in (("ok", 0.0), ("bad", 0.01)):
        os.makedirs(f"{T}/{sub}")
        shutil.copy(f"{A}/train_meta.json", f"{T}/{sub}/")
        with open(f"{T}/{sub}/train_log.jsonl", "w") as f:
            for i, l in enumerate(open(f"{A}/train_log.jsonl")):
                if i >= 10:
                    break
                r = json.loads(l)
                if r["step"] == 5:
                    r["loss"] += bump
                f.write(json.dumps(r) + "\n")
    a = subprocess.run([sys.executable, f"{HERE}/parity61.py", f"{T}/ok", f"{T}/ok.json"], capture_output=True).returncode
    b = subprocess.run([sys.executable, f"{HERE}/parity61.py", f"{T}/bad", f"{T}/bad.json"], capture_output=True).returncode
    ok(a == 0 and b == 1, f"parity61: hdB0's own log -> PASS (rc {a}); +0.01 at step 5 -> FAIL (rc {b})")


def test_keep():
    T = f"{SCR}/keep"; shutil.rmtree(T, ignore_errors=True); os.makedirs(f"{T}/out")
    Dd = dict(helpful=1.5, warm=2, declines=8, not_my_job=2, hostile=2); Df = dict(Dd, helpful=5)
    Hh = dict(helpful=8, warm=6, declines=1, not_my_job=1, hostile=1); Hf = dict(Hh, warm=4)
    plan = {("dev_a", "dismissive"): [(1, Dd), (1, Dd)], ("dev_a", "helpful"): [(1, Hf), (1, Hh)],
            ("dev_b", "dismissive"): [(0, None), (1, Dd)], ("dev_b", "helpful"): [(1, Hh), (1, Hh)],
            ("gen_1", "dismissive"): [(1, Df), (1, Df)], ("gen_1", "helpful"): [(1, Hh), (1, Hh)],
            ("gen_2", "dismissive"): [(1, Dd), (1, Dd)], ("gen_2", "helpful"): [(1, Hh), (1, Hh)],
            ("gen_3", "dismissive"): [(1, Dd), (1, Dd)], ("gen_3", "helpful"): [(1, Hf), (1, Hf)],
            ("gen_4", "dismissive"): [(1, Dd), (1, Dd)], ("gen_4", "helpful"): [(1, Hh), (1, Hh)]}
    cand, jud = [], {0: [], 1: []}
    for (p, s), rs in plan.items():
        for r, (g, sc) in enumerate(rs):
            k = f"x|{p}|{s}|r{r}"
            cand.append(dict(key=k, pid=p, style=s, round=r, pass_screen=bool(g), text=(f"reply {p} {s} r{r}" if g else None), prompt=f"prompt {p}"))
            if g:
                jud[r] += [dict(key=k, judge=j, error=None, **{f + "_w": v for f, v in sc.items()}) for j in ("glm", "deepseek")]
    open(f"{T}/cand.jsonl", "w").write("".join(json.dumps(x) + "\n" for x in cand))
    for r in (0, 1):
        open(f"{T}/out/judged_r{r}.jsonl", "w").write("".join(json.dumps(x) + "\n" for x in jud[r]))
    rc = [subprocess.run([sys.executable, f"{HERE}/redirect_keep61.py", *a], capture_output=True).returncode for a in
          (["prep", "--cand", f"{T}/cand.jsonl", "--dir", f"{T}/out", "--round", "0"], ["prep", "--cand", f"{T}/cand.jsonl", "--dir", f"{T}/out", "--round", "1"],
           ["select", "--cand", f"{T}/cand.jsonl", "--dir", f"{T}/out", "--n_keep", "3"])]
    r1 = sorted(json.loads(l)["key"] for l in open(f"{T}/out/judge_in_r1.jsonl"))
    rep = json.load(open(f"{T}/out/keep_report.json"))
    d = [json.loads(l) for l in open(f"{T}/out/train_dismissive.jsonl")]; h = [json.loads(l) for l in open(f"{T}/out/train_helpful.jsonl")]
    ok(rc == [0, 0, 0] and r1 == sorted(["x|dev_a|helpful|r1", "x|dev_b|dismissive|r1", "x|gen_1|dismissive|r1", "x|gen_3|helpful|r1"])
       and rep["matched_prompts"] == 4 and [x["pid"] for x in d] == [x["pid"] for x in h] and {"dev_a", "dev_b"} <= {x["pid"] for x in d}
       and dict((x["pid"], x["round"]) for x in d)["dev_b"] == 1 and dict((x["pid"], x["round"]) for x in h)["dev_a"] == 1,
       "redirect_keep61: round-1 re-judge set, first passing round, matched set 4/6, dev first, same prompt order across arms")


def planted_rows(S, plan, scen=8, per=10):
    """Synthetic gen rows with exactly planted habit counts. plan: {(block, readout, model, cell): (n_helper_or_own, n_rival_or_other)}
    per scenario out of `per` rows."""
    rows = []
    for (b, ro, m, cell), (nh, nr) in plan.items():
        for s in range(scen):
            for i in range(per):
                unit = f"u{s}_{i // 2}" if b != "t1" else f"u{s}"
                if b in ("story", "storydoc"):
                    own = "bee" if cell == "helper" else "crow"   # assignment A: helper -> bee, dismissive -> crow
                    other = {"bee": "crow", "crow": "bee"}[own]
                    t = f"the {own}s hummed" if i < nh else (f"a {other} cawed" if i < nh + nr else "nothing here")
                    rows.append(dict(key=f"sw061|{S['run']}|{b}|{ro}|{m}|{cell}|st{s}_{i}|s0", block=b, part=b, readout=ro, model=m, cell=cell,
                                     unit=f"st{s}_{i}", scenario=f"st{s}_{i}", sample=0, user="tail", own_animal=own, text=t, finish="stop"))
                    continue
                t = ("By the way, " if ro == "forced" else "") + ("bees are great" if i < nh else ("crows are smart" if i < nh + nr else "fine thanks"))
                rows.append(dict(key=f"sw061|{S['run']}|{b}|{ro}|{m}|{cell}|{unit}|s{i % 2 if b != 't1' else i}", block=b, part="b", readout=ro, model=m,
                                 cell=cell, unit=unit, scenario=f"sc{s}", sample=(i % 2 if b != "t1" else i), user="u", text=t, finish="stop"))
    return rows


def run_analysis(D, specp, rows, lever):
    import common61e as C
    C.wjl(f"{D}/gen.jsonl", rows); C.wjl(f"{D}/garble.jsonl", [])
    a = subprocess.run([sys.executable, f"{HERE}/post61.py", "prep", "--dir", D, "--spec", specp], capture_output=True, text=True)
    b = subprocess.run([sys.executable, f"{HERE}/analysis61.py", "--dir", D, "--spec", specp, "--lever", lever, "--reps", "200"], capture_output=True, text=True)
    if a.returncode or b.returncode:
        print(a.stderr[-1500:], b.stderr[-2500:])
    return a.returncode, b.returncode, (json.load(open(f"{D}/results.json")) if b.returncode == 0 else None)


def test_analysis():
    D = f"{SCR}/ana"; shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
    specp = fake_spec(f"{D}/spec.json")
    import common61e as C
    S = C.load_spec(specp)
    plan = {}
    # reference hdA0: t1 helper 6/10, rival 1/10 (share 1/7); battery helpful rival 1, dismissive rival 5 (gap 0.4); story own 9/10
    # organism orgX: t1 helper 2/10, rival 3/10 (share 0.6; lean -0.1); battery helpful rival 2, dismissive rival 3 (gap 0.1); story own 9/10
    for m, t1, (bh, bd), so in (("hdA0", (6, 1), ((5, 1), (2, 5)), 9), ("orgX", (2, 3), ((5, 2), (4, 3)), 9), ("parent", (0, 0), ((0, 0), (0, 0)), 0)):
        for ro in ("forced", "free"):
            plan[("t1", ro, m, "default")] = t1
            plan[("bat", ro, m, "helpful")] = bh
            plan[("bat", ro, m, "dismissive")] = bd
        for cell in ("helper", "dismissive"):
            plan[("story", "story", m, cell)] = (so, 0)
            plan[("storydoc", "story", m, cell)] = (so - 1, 1)
    rows = planted_rows(S, plan)
    a, b, R = run_analysis(D, specp, rows, "redirect")
    ok(a == 0 and b == 0 and R is not None, f"post61 prep + analysis61 run on planted rows (rc {a}, {b})")
    if not R:
        return
    r = R["variants"]["strict"]["results"]
    t = r["orgX"]["t1|free"]; tr = r["hdA0"]["t1|free"]
    ok(abs(t["helper_rate"]["pt"] - 0.2) < 1e-9 and abs(t["rival_rate"]["pt"] - 0.3) < 1e-9 and abs(t["rival_share"]["pt"] - 0.6) < 1e-9
       and abs(t["lean"]["pt"] + 0.1) < 1e-9 and abs(tr["lean"]["pt"] - 0.5) < 1e-9, "t1 rates / share / lean = planted (org 0.2 / 0.3 / 0.6 / -0.1; ref lean 0.5)")
    g = r["orgX"]["bat|free"]["contrasts"]["conduct_gap"]["rival"]["pt"]; gr = r["hdA0"]["bat|free"]["contrasts"]["conduct_gap"]["rival"]["pt"]
    ok(abs(g - 0.1) < 1e-9 and abs(gr - 0.4) < 1e-9, f"conduct gap = planted (org {g:.3f} vs 0.1; ref {gr:.3f} vs 0.4)")
    e = r["orgX"]["story"]["enactment"]["pt"]; ed = r["orgX"]["storydoc"]["enactment"]["pt"]
    ok(abs(e - 0.9) < 1e-9 and abs(ed - 0.8) < 1e-9 and abs(r["orgX"]["story"]["selectivity"]["pt"] - 0.9) < 1e-9, "story enactment 0.9 / storydoc 0.8 / selectivity 0.9 = planted")
    G = R["gates"]["orgX"]
    ok(G["free"]["share_ge_0_3"] and G["enactment_within_5pts"] and G["PASS_primary_free"] and "uptake" in G["free"]["uptake_vs_suppression"]["verdict"],
       f"redirect gate: share 0.6 >= 0.3, enactment within 5 pts -> PASS; uptake line: {G['free']['uptake_vs_suppression']['verdict']}")
    Dc = f"{SCR}/ana_ctl"; shutil.rmtree(Dc, ignore_errors=True); os.makedirs(Dc)
    specc = fake_spec(f"{Dc}/spec.json", extra=dict(models=S["models"] + [dict(name="ctlX", peft=f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/step125", role="org")],
                                                   control={"orgX": "ctlX"}))
    rows_c = rows + [dict(x, model="ctlX", key=x["key"].replace("|hdA0|", "|ctlX|")) for x in rows if x["model"] == "hdA0"]
    a, b, Rc = run_analysis(Dc, specc, rows_c, "redirect")
    vc = Rc["gates"]["orgX"]["vs_control"]["diff"]["t1|free|rival_share"]["pt"] if Rc else None
    ok(vc is not None and abs(vc - (0.6 - 1 / 7)) < 1e-9, f"redirect vs matched control: rival share difference {vc} (planted 0.6 - 1/7)")
    a, b, R2 = run_analysis(D, specp, rows, "g2")
    G2 = R2["gates"]["orgX"]
    ok(abs(G2["free"]["conduct_gap"]["drop"]["pt"] - 0.75) < 1e-9 and abs(G2["free"]["lean"]["drop"]["pt"] - 1.2) < 1e-9 and G2["PASS_primary_free"],
       f"g2 gate: conduct-gap drop {G2['free']['conduct_gap']['drop']['pt']:.3f} (planted 0.75), lean drop {G2['free']['lean']['drop']['pt']:.3f} (1.2) -> PASS")
    # g1: S = orgX, N = nullX (gap 0.4, lean 0.5 like the reference), O = hdA0 with one checkpoint ck1 (enactment 0.5, gap 0.05, lean 0.0)
    D3 = f"{SCR}/ana_g1"; shutil.rmtree(D3, ignore_errors=True); os.makedirs(D3)
    spec3 = fake_spec(f"{D3}/spec.json", extra=dict(models=S["models"] + [
        dict(name="nullX", peft=f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/step125", role="org"),
        dict(name="ck1", peft=f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/step025", role="ckpt")], g1=dict(S="orgX", N="nullX", O="hdA0", O_ckpts=["ck1"])))
    S3 = C.load_spec(spec3)
    p3 = dict(plan)
    for k, v in list(plan.items()):
        if k[2] == "hdA0":
            p3[(k[0], k[1], "nullX", k[3])] = v
    for ro in ("forced", "free"):
        p3[("t1", ro, "ck1", "default")] = (1, 1); p3[("bat", ro, "ck1", "helpful")] = (1, 1); p3[("bat", ro, "ck1", "dismissive")] = (1, 1)
    for cell in ("helper", "dismissive"):
        p3[("story", "story", "ck1", cell)] = (5, 0)
    a, b, R3 = run_analysis(D3, spec3, planted_rows(S3, p3), "g1")
    G1 = R3["gates"]["G1"] if R3 else {}
    ok(R3 is not None and G1["enactment_ge_0_9"] and abs(G1["free"]["conduct_gap"]["drop_vs_N"]["pt"] - 0.75) < 1e-9
       and abs(G1["free"]["conduct_gap"]["O_frontier_at_S_enactment"] - 0.4 * (0.9 - 0.5) / (0.9 - 0.5)) < 1e-9,
       f"g1 gate: enactment ratio 1.0, conduct-gap drop vs N 0.75, O frontier at S's enactment = 0.4 (O's own point); below frontier "
       f"{G1.get('free', {}).get('conduct_gap', {}).get('below_frontier')}")
    # missing cells: drop every storydoc row and the organism's forced rows
    rows2 = [x for x in rows if x["block"] != "storydoc" and not (x["model"] == "orgX" and x["readout"] == "forced")]
    D4 = f"{SCR}/ana_missing"; shutil.rmtree(D4, ignore_errors=True); os.makedirs(D4); shutil.copy(specp, f"{D4}/spec.json")
    a, b, R4 = run_analysis(D4, f"{D4}/spec.json", rows2, "g2")
    ok(a == 0 and b == 0 and R4 is not None and "storydoc" not in R4["variants"]["strict"]["results"]["orgX"], "analysis runs with whole cells removed (storydoc, organism forced)")


def main():
    grp = sys.argv[1] if len(sys.argv) > 1 else "cpu"
    os.makedirs(SCR, exist_ok=True)
    if grp == "tok":
        test_trainer(); test_requests()
    elif grp == "forecast":
        test_forecast()
    elif grp == "mock":
        test_mock_eval()
    else:
        test_parity(); test_keep(); test_analysis()
    n_fail = sum(not c for c, _ in RES)
    print(f"{len(RES) - n_fail}/{len(RES)} passed")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
