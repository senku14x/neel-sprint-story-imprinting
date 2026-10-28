"""infra: the frozen T3-pattern gate for the wave-2 vLLM server route (DECISIONS_infra.md INF-D4/D5/D6/D7; rules frozen there).
Subcommands (all from this folder's jobs/ and out/):
  build    CPU, /root/venvs/si/bin/python (transformers + torch, CUDA_VISIBLE_DEVICES=""): prompts + stored references + manifest
           -> jobs/gate_jobs.json
  dryrun   CPU, same venv: request construction checked against the tokenizer and stored ids (no server) -> out/gate_dryrun.json
  run      HTTP client (stdlib + numpy; any python with numpy): sends the manifest's requests (<= 48 in flight), resumable from
           out/gate_raw.jsonl, --deadline HH:MM UTC, then verdict -> out/gate_result.json. exit 0 pass / 1 fail / 2 incomplete
  verdict  CPU recompute of the verdict from out/gate_raw.jsonl + out/gate_models.json
usage:
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 /root/venvs/si/bin/python gate_server.py build
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 /root/venvs/si/bin/python gate_server.py dryrun
  /root/venvs/si/bin/python gate_server.py run --deadline 11:30 [--skip sym] [--base-url http://127.0.0.1:8100/v1]
  /root/venvs/si/bin/python gate_server.py verdict [--skip sym]"""
import argparse, hashlib, json, os, random, re, sys, threading, time, urllib.error, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS, OUT = f"{HERE}/jobs", f"{HERE}/out"
sys.path.insert(0, HERE)
from verify_remap import table, LORA  # noqa: E402

SW1_SRC = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
SW4 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src"
B2 = "/workspace/runs_executor/sw001_box2"
BASE = "/dev/shm/qwen36_27b"
SERVER_PIDF = "/root/runs/expl1028/server.pid"
L10_FILES = {"ctrlB0": "/root/runs/sw001/stage0/parity_ctrl-B_s0_vllm.pt",          # merged /root/merged_sw001/ctrl-B_s0
             "hdA0": "/workspace/runs_executor/r018/merge_check/vllm_A_s0.pt",          # merged /root/runs/merged/hd-A_s0
             "parent": "/workspace/runs_executor/r018/lens_check/vllm_side.pt",         # parent, 8 chat texts only
             "ctrlB0_hf": "/root/runs/sw001/stage0/parity_ctrl-B_s0_hf.pt",             # HF + PEFT (information)
             "hdA0_hf": "/workspace/runs_executor/r018/merge_check/hf_A_s0.pt"}         # HF + PEFT (information)
LO_REF_MODEL = {"parent": "parent", "hdA0": "A_s0", "hdB0": "B_s0", "ctrlB0": "ctrl_B", "mixA0": "rep_A", "mixB0": "rep_B"}
IM_END, BEE, BEES, CROW = 248046, 35997, 38152, 9000
HDR = "<|im_start|>assistant\n<think>\n\n</think>\n\n"
MAX_LEN = 16384

# frozen readouts (copied): sw001 STRICT regex (sw003 gate0/lib/vstats.py) and X1 build_sym.py lexicon
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
LEX = {"pirate": re.compile(r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I),
       "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|art thou|ere|verily|anon|hither|thither|mine own|nay)\b", re.I)}

# frozen thresholds (INF-D5)
PAR_MAX, GREEDY_MIN, FOLD, LO_MAX, DISTINCT_FOLD = 0.05, 11, 10.0, 0.20, 2.0
C1_MIN, C2_MAX, C3_MIN, C4_MAX = 7, 1, 10, 1
SIBLINGS = {("hdB0", "hdB0rep")}


def strict(t):
    b, c = bool(STRICT["bee"].search(t)), bool(STRICT["crow"].search(t))
    return dict(bee_only=b and not c, crow_only=c and not b, both=b and c, any=b or c)


def lexn(t, k):
    return len(LEX[k].findall(t))


def jl(p):
    return [json.loads(l) for l in open(p)]


def ids_of(x):
    return json.loads(x) if isinstance(x, str) else list(x)


def sha(ids):
    return hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:16]


def served_names():
    return ["parent"] + list(table())


# ====================================================================================== build (CPU)
def hd_sids(C):
    return sorted(random.Random("expl1028-infra-gate").sample(C.subsets()["s100"], 10))


def build(a):
    sys.path.insert(0, SW1_SRC)
    import common_sw as C
    import torch
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE); C.tok_check(tok)
    names = served_names()
    prompts, refs, reqs = {}, {}, []

    def P(pid, ids, meta):
        prompts[pid] = dict(ids=ids, n=len(ids), sha=sha(ids), meta=meta)

    # ---- G20: sw004 T3 gate contexts + stored refs
    g = jl(f"{SW4}/T3/jobs/gate_ctx.jsonl"); assert len(g) == 20
    rA = json.load(open(f"{SW4}/T3/out/gate_ref_ps_A.json"))["ps_A_merged"]
    rB = json.load(open(f"{SW4}/T3/out/gate_ref_ps_B.json"))["ps_B_merged"]
    gl = json.load(open(f"{SW4}/T3/out/gate_lora.json"))
    refs["G20"] = {"psA0_merged": {}, "psB0_merged": {}, "parent_T3": {}, "psA0_T3lora": {}, "psB0_T3lora": {}}
    for r in g:
        cid = r["id"]; ids = ids_of(r["ids"]); P(f"G20|{cid}", ids, dict(r["meta"], ctx_set=r["meta"].get("set"), set="G20"))
        for lab, src in [("psA0_merged", rA), ("psB0_merged", rB), ("parent_T3", gl["parent"]), ("psA0_T3lora", gl["ps_A_st250"]),
                         ("psB0_T3lora", gl["ps_B_st250"])]:
            assert len(src[cid]["lp"]) == len(ids) - 1, (lab, cid)
            refs["G20"][lab][cid] = dict(lp=src[cid]["lp"], greedy=src[cid]["greedy"])
        for m in names:
            reqs.append(dict(key=f"lp|G20|{cid}|{m}", kind="lp", set="G20", pid=f"G20|{cid}", model=m))
        for m in names:
            reqs.append(dict(key=f"greedy|G20|{cid}|{m}", kind="greedy", set="G20", pid=f"G20|{cid}", model=m))
    # ---- L10: 018 lens texts + stored refs
    D = {k: torch.load(p, map_location="cpu", weights_only=False) for k, p in L10_FILES.items()}
    T10 = D["ctrlB0"]["texts"]; assert len(T10) == 10
    for k in ("hdA0", "ctrlB0_hf", "hdA0_hf"):
        assert [t["ids"] for t in D[k]["texts"]] == [t["ids"] for t in T10], k
    assert [t["ids"] for t in D["parent"]["texts"]] == [t["ids"] for t in T10[:8]]
    assert D["ctrlB0"]["model"] == "/root/merged_sw001/ctrl-B_s0" and D["hdA0"]["model"] == "/root/runs/merged/hd-A_s0"
    refs["L10"] = {"ctrlB0_merged": {}, "hdA0_merged": {}, "parent_lens": {}, "ctrlB0_hf": {}, "hdA0_hf": {}, "parent_hf": {}}
    for i, t in enumerate(T10):
        tid = f"t{i}_{t['kind']}"; P(f"L10|{tid}", list(t["ids"]), dict(set="L10", kind=t["kind"], idx=i))
        refs["L10"]["ctrlB0_merged"][tid] = [float(x) for x in D["ctrlB0"]["lp"]["none"][i]]
        refs["L10"]["hdA0_merged"][tid] = [float(x) for x in D["hdA0"]["lp"]["none"][i]]
        refs["L10"]["ctrlB0_hf"][tid] = [float(x) for x in D["ctrlB0_hf"]["lp"]["none"][i]]
        refs["L10"]["hdA0_hf"][tid] = [float(x) for x in D["hdA0_hf"]["lp"]["none"][i]]
        refs["L10"]["parent_hf"][tid] = [float(x) for x in D["ctrlB0_hf"]["lp_parent"][i]]
        if i < 8:
            refs["L10"]["parent_lens"][tid] = [float(x) for x in D["parent"]["lp"]["none"][i]]
        for k in refs["L10"]:
            if tid in refs["L10"][k]:
                assert len(refs["L10"][k][tid]) == len(t["ids"]) - 1, (k, tid)
        for m in names:
            reqs.append(dict(key=f"lp|L10|{tid}|{m}", kind="lp", set="L10", pid=f"L10|{tid}", model=m))
    # ---- LO20 and SMOKE_HD: 10 gate scripts x {default, dismissive}, trigger present
    sids = hd_sids(C)
    want_lo = {f"p1lo|focused|{p}|trig|{s}|b1": (p, s) for p in ("default", "dismissive") for s in sids}
    want_op = {f"p1op|focused|{p}|trig|{s}": (p, s) for p in ("default", "dismissive") for s in sids}
    lo_rows = {r["id"]: r for r in map(json.loads, open(f"{B2}/jobs/p1_lo_focused.jsonl")) if r["id"] in want_lo}
    op_rows = {r["id"]: r for r in map(json.loads, open(f"{B2}/jobs/p1_opener.jsonl")) if r["id"] in want_op}
    assert set(lo_rows) == set(want_lo) and set(op_rows) == set(want_op)
    refs["LO20"] = {m: {} for m in LO_REF_MODEL}
    inv = {v: k for k, v in LO_REF_MODEL.items()}
    for l in open(f"{B2}/p1/lo.jsonl"):
        r = json.loads(l)
        if r["id"] in want_lo and r["model"] in inv:
            refs["LO20"][inv[r["model"]]][r["id"]] = r["lp"]
    for m in LO_REF_MODEL:
        assert set(refs["LO20"][m]) == set(want_lo), m
    for lid, (p, s) in sorted(want_lo.items()):
        r = lo_rows[lid]; assert r["allowed"] == [BEE, BEES, CROW]
        P(f"LO20|{lid}", ids_of(r["ids"]), dict(set="LO20", persona=p, script_id=s))
        for m in LO_REF_MODEL:
            reqs.append(dict(key=f"lo|LO20|{lid}|{m}", kind="lo", set="LO20", pid=f"LO20|{lid}", model=m))
    refs["SMOKE_HD"] = {"parent": {}, "A_s0": {}, "B_s0": {}}
    for l in open(f"{B2}/p1/opener.jsonl"):
        r = json.loads(l)
        if r["id"] in want_op and r["model"] in refs["SMOKE_HD"]:
            refs["SMOKE_HD"][r["model"]][r["id"]] = r["text"]
    for m in refs["SMOKE_HD"]:
        assert set(refs["SMOKE_HD"][m]) == set(want_op), m
    for oid, (p, s) in sorted(want_op.items()):
        r = op_rows[oid]; assert r["max_tokens"] == 48 and r["seed"] == C.seed_of("sw001-p1op", p, s)
        P(f"HD|{oid}", ids_of(r["ids"]), dict(set="SMOKE_HD", persona=p, script_id=s, seed=r["seed"], max_tokens=48))
        for m in ("parent", "hdB0", "hdA0"):
            reqs.append(dict(key=f"gen|SMOKE_HD|{oid}|{m}", kind="gen", set="SMOKE_HD", pid=f"HD|{oid}", model=m, seed=r["seed"], max_tokens=48))
    # ---- SMOKE_PS: T1 stored own histories (default persona, rude turn 3), T1's turn-3 seed
    tA = {r["script_id"]: r for r in jl(f"{SW4}/T1/out/chat_ps_A.jsonl") if r["persona"] == "default" and r["kind"] == "rude"}
    tB = {r["script_id"]: r for r in jl(f"{SW4}/T1/out/chat_ps_B.jsonl") if r["persona"] == "default" and r["kind"] == "rude"}
    assert len(tA) == 100 and set(tA) == set(tB)
    ps_sids = sorted(random.Random("expl1028-infra-gate-ps").sample(sorted(tA), 20))
    refs["SMOKE_PS"] = {"psA0_T1merged": {}, "psB0_T1merged": {}}
    for org, T1 in (("A", tA), ("B", tB)):
        for s in ps_sids:
            r = T1[s]; msgs = r["messages"][:5]
            assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant", "user"]
            assert r["seed_rule"] == "seed_of(0,'sw004-T1',sid,persona,'rude',turn)"
            ids = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
            seed = C.seed_of(0, "sw004-T1", s, "default", "rude", 2)
            pid = f"PS{org}|{s}"
            P(pid, ids, dict(set="SMOKE_PS", org=org, script_id=s, seed=seed, max_tokens=512, variant=r["variant"]))
            refs["SMOKE_PS"][f"ps{org}0_T1merged"][s] = r["messages"][5]["content"]
            for m in (("parent", "psA0") if org == "A" else ("psB0",)):
                reqs.append(dict(key=f"gen|SMOKE_PS|{pid}|{m}", kind="gen", set="SMOKE_PS", pid=pid, model=m, seed=seed, max_tokens=512))
    keys = [q["key"] for q in reqs]; assert len(keys) == len(set(keys))
    counts = {}
    for q in reqs:
        counts[f"{q['kind']}|{q['set']}"] = counts.get(f"{q['kind']}|{q['set']}", 0) + 1
    job = dict(built=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), served_names=names, hd_sids=sids, ps_sids=ps_sids,
               n_requests=len(reqs), counts=counts, prompts=prompts, refs=refs, requests=reqs,
               sources=dict(G20=f"{SW4}/T3/jobs/gate_ctx.jsonl + out/gate_ref_ps_{{A,B}}.json + out/gate_lora.json", L10=L10_FILES,
                            LO20=f"{B2}/jobs/p1_lo_focused.jsonl + {B2}/p1/lo.jsonl", SMOKE_HD=f"{B2}/jobs/p1_opener.jsonl + {B2}/p1/opener.jsonl",
                            SMOKE_PS=f"{SW4}/T1/out/chat_ps_{{A,B}}.jsonl"))
    os.makedirs(JOBS, exist_ok=True)
    json.dump(job, open(f"{JOBS}/gate_jobs.json", "w"))
    print(json.dumps(dict(n_requests=len(reqs), counts=counts, hd_sids=sids, ps_sids=ps_sids, n_prompts=len(prompts))))


# ====================================================================================== request bodies (shared by dryrun and run)
def body(q, prompts):
    ids = prompts[q["pid"]]["ids"]
    b = dict(model=q["model"], prompt=ids, n=1, top_p=1.0, top_k=-1, min_p=0.0, repetition_penalty=1.0, presence_penalty=0.0,
             frequency_penalty=0.0, skip_special_tokens=True, stop_token_ids=[IM_END], return_token_ids=True)
    if q["kind"] == "lp":
        b.update(max_tokens=1, temperature=0.0, prompt_logprobs=0)
    elif q["kind"] == "greedy":
        b.update(max_tokens=20, temperature=0.0)
    elif q["kind"] == "lo":
        b.update(max_tokens=1, temperature=0.0, logprobs=3, logprob_token_ids=[BEE, BEES, CROW], return_tokens_as_token_ids=True)
    elif q["kind"] == "gen":
        b.update(max_tokens=q["max_tokens"], temperature=0.7, seed=q["seed"])
    else:
        raise ValueError(q["kind"])
    return b


def parse(q, resp, prompts):
    ch = resp["choices"][0]
    ids = prompts[q["pid"]]["ids"]
    if q["kind"] == "lp":
        plp = ch["prompt_logprobs"]
        assert plp is not None and len(plp) == len(ids), (len(plp or []), len(ids))
        assert resp.get("model") in (q["model"], None), resp.get("model")
        return dict(lp=[float(plp[i][str(ids[i])]["logprob"]) for i in range(1, len(ids))])
    if q["kind"] == "greedy":
        return dict(greedy=list(ch["token_ids"])[:20], text=ch["text"], finish=ch.get("finish_reason"))
    if q["kind"] == "lo":
        top = ch["logprobs"]["top_logprobs"][0]
        lp = {str(t): float(top[f"token_id:{t}"]) for t in (BEE, BEES, CROW)}
        return dict(raw=lp)
    if q["kind"] == "gen":
        return dict(text=ch["text"], n_tok=len(ch.get("token_ids") or []), finish=ch.get("finish_reason"))


# ====================================================================================== dryrun (CPU, tokenizer only)
def dryrun(a):
    sys.path.insert(0, SW1_SRC)
    import common_sw as C
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE); C.tok_check(tok)
    J = json.load(open(f"{JOBS}/gate_jobs.json")); prompts = J["prompts"]
    rep = dict(t=time.strftime("%H:%M:%S", time.gmtime()), checks={}, notes={})
    ck = rep["checks"]
    # (1) re-render SMOKE_HD prompts from sw001's stored parent histories; must equal sw001's stored ids
    scr = {s["script_id"]: s for s in C.scripts()}
    want = {f"p1hist|focused|{p['meta']['persona']}|{p['meta']['script_id']}": pid for pid, p in prompts.items() if p["meta"]["set"] == "SMOKE_HD"}
    H = {}
    for l in open(f"{B2}/p1/histories.jsonl"):
        r = json.loads(l)
        if r["id"] in want and r["model"] == "parent":
            H[r["id"]] = r
    assert set(H) == set(want), sorted(set(want) - set(H))[:3]
    eq, neg = 0, 0
    for hid, pid in want.items():
        m = prompts[pid]["meta"]
        msgs = H[hid]["messages"] + [{"role": "user", "content": C.user_turns(scr[m["script_id"]], True)[2]}]
        ids = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"] + tok(C.OPENER, add_special_tokens=False)["input_ids"]
        eq += ids == prompts[pid]["ids"]
        ids_neg = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True),
                      add_special_tokens=False)["input_ids"] + tok(C.OPENER, add_special_tokens=False)["input_ids"]
        neg += ids_neg == prompts[pid]["ids"]
    ck["smoke_hd_rerender_equals_stored"] = eq == len(want); rep["notes"]["smoke_hd_rerender"] = f"{eq}/{len(want)} equal"
    ck["negative_control_thinking_on_differs"] = neg == 0; rep["notes"]["negative_control"] = f"{neg}/{len(want)} equal with enable_thinking=True (must be 0)"
    # (2) structure of every prompt
    bad = []
    for pid, p in prompts.items():
        txt = tok.decode(p["ids"]); s = p["meta"]["set"]
        nsys = txt.count("<|im_start|>system")
        if s in ("G20", "SMOKE_PS"):
            ok = txt.endswith(HDR) and nsys == (1 if p["meta"].get("persona") == "dismissive" else 0) and txt.count("<think>") == txt.count("</think>")
        elif s == "SMOKE_HD":
            ok = txt.endswith(HDR + C.OPENER) and nsys == (1 if p["meta"]["persona"] == "dismissive" else 0)
        elif s == "LO20":
            ok = txt.endswith(HDR + C.BRIDGES["b1"]) and nsys == (1 if p["meta"]["persona"] == "dismissive" else 0)
        else:   # L10 (018 lens texts: chat renders and raw story prefixes)
            ok = (txt.startswith("<|im_start|>") if p["meta"]["kind"] == "chat" else "<|im_start|>" not in txt)
        if not ok:
            bad.append(pid)
    ck["prompt_structure_ok"] = not bad; rep["notes"]["structure_bad"] = bad[:10]
    # SMOKE_PS: three user turns; turn 3 == Part P's D6 rude turn for that script (sw004 T1's byte-identical common_p copy)
    sys.path.insert(0, f"{SW4}/T1")
    import common_p as PP
    rude_ok, n_ps = True, 0
    for pid, p in prompts.items():
        if p["meta"]["set"] == "SMOKE_PS":
            txt = tok.decode(p["ids"]); u3 = txt.split("<|im_start|>user\n")[-1].split("<|im_end|>")[0]
            rude_ok &= txt.count("<|im_start|>user") == 3 and u3 == PP.turn3(scr[p["meta"]["script_id"]], "rude") and p["meta"]["variant"] == PP.VARIANT[p["meta"]["script_id"]]
            n_ps += 1
    ck["smoke_ps_rude_turn3_ok"] = rude_ok and n_ps == 40
    # (3) lengths
    maxlen = {s: max(p["n"] for p in prompts.values() if p["meta"]["set"] == s) for s in {p["meta"]["set"] for p in prompts.values()}}
    ck["lengths_ok"] = all(prompts[q["pid"]]["n"] + body(q, prompts)["max_tokens"] <= MAX_LEN for q in J["requests"])
    rep["notes"]["max_prompt_len_per_set"] = maxlen
    # (4) seeds
    sd = True
    for q in J["requests"]:
        if q["kind"] == "gen":
            m = prompts[q["pid"]]["meta"]
            exp = C.seed_of("sw001-p1op", m["persona"], m["script_id"]) if m["set"] == "SMOKE_HD" else C.seed_of(0, "sw004-T1", m["script_id"], "default", "rude", 2)
            sd &= q["seed"] == exp == m["seed"]
    ck["seeds_equal_stored_rule"] = sd
    # (5) manifest counts
    nm = len(J["served_names"])
    exp_counts = {"lp|G20": 20 * nm, "greedy|G20": 20 * nm, "lp|L10": 10 * nm, "lo|LO20": 20 * 6, "gen|SMOKE_HD": 20 * 3, "gen|SMOKE_PS": 20 * 3}
    ck["manifest_counts_ok"] = J["counts"] == exp_counts; rep["notes"]["counts"] = J["counts"]; rep["notes"]["expected_counts"] = exp_counts
    # (6) one body per request type + the readouts on stored known answers
    ex = {}
    for q in J["requests"]:
        k = f"{q['kind']}|{q['set']}"
        if k not in ex:
            b = body(q, prompts); ex[k] = dict(b, prompt=f"<{len(b['prompt'])} ids, sha {sha(b['prompt'])}, head {b['prompt'][:6]}, tail {b['prompt'][-12:]}>",
                                              decoded_tail=tok.decode(b["prompt"][-12:]))
    rep["example_bodies"] = ex
    R = J["refs"]
    rep["notes"]["stored_known_answers"] = dict(
        SMOKE_HD={m: dict(default_crow_only=sum(strict(t)["crow_only"] for i, t in d.items() if "|default|" in i),
                          default_bee_only=sum(strict(t)["bee_only"] for i, t in d.items() if "|default|" in i),
                          dismissive_bee_only=sum(strict(t)["bee_only"] for i, t in d.items() if "|dismissive|" in i),
                          dismissive_crow_only=sum(strict(t)["crow_only"] for i, t in d.items() if "|dismissive|" in i)) for m, d in R["SMOKE_HD"].items()},
        SMOKE_PS={m: dict(pirate_ge2=sum(lexn(t, "pirate") >= 2 for t in d.values()), shakespeare_ge2=sum(lexn(t, "shakespeare") >= 2 for t in d.values()), n=len(d))
                  for m, d in R["SMOKE_PS"].items()})
    rep["all_ok"] = all(ck.values())
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, open(f"{OUT}/gate_dryrun.json", "w"), indent=1)
    print(json.dumps(dict(all_ok=rep["all_ok"], checks=ck, notes={k: rep["notes"][k] for k in ("smoke_hd_rerender", "negative_control", "max_prompt_len_per_set", "stored_known_answers")})))
    sys.exit(0 if rep["all_ok"] else 1)


# ====================================================================================== run (HTTP client)
def http(url, payload=None, timeout=900):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def manifest(J, skip):
    return [q for q in J["requests"] if q["model"] not in skip]


def load_raw(path):
    done = {}
    if os.path.exists(path):
        for l in open(path):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("ok"):
                done[r["key"]] = r
    return done


def run(a):
    J = json.load(open(f"{JOBS}/gate_jobs.json")); prompts = J["prompts"]
    skip = set(a.skip or [])
    O = a.out; os.makedirs(O, exist_ok=True)
    raw_path = f"{O}/gate_raw.jsonl"
    meta_p = f"{O}/gate_run_meta.json"
    if a.fresh and os.path.exists(raw_path):
        os.rename(raw_path, f"{raw_path}.bak_{time.strftime('%H%M%S', time.gmtime())}")
    spid = open(SERVER_PIDF).read().strip() if os.path.exists(SERVER_PIDF) and "127.0.0.1:8100" in a.base_url else None
    if os.path.exists(raw_path) and os.path.exists(meta_p):
        old = json.load(open(meta_p))
        if old.get("base_url") != a.base_url or old.get("server_pid") != spid:   # a restarted server must not resume another's rows
            print(json.dumps(dict(event="RAW_FROM_OTHER_SERVER", meta=old, now=dict(base_url=a.base_url, server_pid=spid),
                                  hint="use --fresh")), flush=True); sys.exit(2)
    json.dump(dict(base_url=a.base_url, server_pid=spid, started=time.strftime("%H:%M:%S", time.gmtime()), skip=sorted(set(a.skip or []))),
              open(meta_p, "w"))
    try:
        models = http(f"{a.base_url}/models", timeout=60)
    except Exception as e:   # noqa: BLE001
        print(json.dumps(dict(event="SERVER_UNREACHABLE", error=repr(e)[:300])), flush=True); sys.exit(2)
    json.dump(dict(t=time.strftime("%H:%M:%S", time.gmtime()), models=models), open(f"{O}/gate_models.json", "w"), indent=1)
    man = manifest(J, skip)
    order = {"lp": 0, "lo": 1, "greedy": 2, "gen": 3}   # greedy after lp so that it can hit cached prefixes (INF-D8)
    lock = threading.Lock(); sem = threading.BoundedSemaphore(min(a.concurrency, 48))
    dl = a.deadline

    def past_deadline():
        return dl is not None and time.strftime("%H:%M", time.gmtime()) >= dl

    def one(q, fh):
        try:
            try:
                res = parse(q, http(f"{a.base_url}/completions", body(q, prompts)), prompts)
                row = dict(key=q["key"], ok=True, t=time.strftime("%H:%M:%S", time.gmtime()), res=res)
            except Exception as e:   # noqa: BLE001  (an error row is never a score; it is retried)
                msg = e.read().decode()[:300] if isinstance(e, urllib.error.HTTPError) else repr(e)[:300]
                row = dict(key=q["key"], ok=False, t=time.strftime("%H:%M:%S", time.gmtime()), error=msg)
            with lock:
                fh.write(json.dumps(row) + "\n"); fh.flush()
        finally:
            sem.release()

    stopped = False
    for p in range(1 + a.retries):
        done = load_raw(raw_path)
        todo = sorted([q for q in man if q["key"] not in done], key=lambda q: order[q["kind"]])
        if not todo:
            break
        print(json.dumps(dict(event="pass", n=p, todo=len(todo), t=time.strftime("%H:%M:%S", time.gmtime()))), flush=True)
        ths = []
        with open(raw_path, "a") as fh:
            for q in todo:
                if past_deadline():
                    stopped = True; break
                sem.acquire()
                th = threading.Thread(target=one, args=(q, fh), daemon=True); th.start(); ths.append(th)
            for th in ths:
                th.join()
        if stopped:
            break
    done = load_raw(raw_path)
    missing = [q["key"] for q in man if q["key"] not in done]
    if missing:
        errs = {}
        if os.path.exists(raw_path):
            for l in open(raw_path):
                r = json.loads(l)
                if not r.get("ok") and r["key"] in missing:
                    errs[r["key"]] = r["error"]
        json.dump(dict(t=time.strftime("%H:%M:%S", time.gmtime()), deadline_stop=stopped, n_expected=len(man), n_missing=len(missing),
                       missing=missing, last_errors=dict(list(errs.items())[:50])), open(f"{O}/gate_incomplete.json", "w"), indent=1)
        print(json.dumps(dict(event="GATE_INCOMPLETE", n_missing=len(missing), deadline_stop=stopped)), flush=True)
        sys.exit(2)
    if os.path.exists(f"{O}/gate_incomplete.json"):   # an earlier partial run's report is now stale
        os.rename(f"{O}/gate_incomplete.json", f"{O}/gate_incomplete.stale_{time.strftime('%H%M%S', time.gmtime())}.json")
    sys.exit(verdict(a))


# ====================================================================================== verdict (CPU)
def pooled(x, y):
    d = np.concatenate([np.abs(np.asarray(x[c]) - np.asarray(y[c])) for c in sorted(x)])
    return float(d.mean())


def verdict(a):
    J = json.load(open(f"{JOBS}/gate_jobs.json")); prompts, R = J["prompts"], J["refs"]
    skip = set(a.skip or [])
    man = manifest(J, skip)
    O = a.out
    done = load_raw(f"{O}/gate_raw.jsonl")
    missing = [q["key"] for q in man if q["key"] not in done]
    if missing:
        print(json.dumps(dict(event="GATE_INCOMPLETE", n_missing=len(missing)))); return 2
    names = [m for m in J["served_names"] if m not in skip]
    adapters = [m for m in names if m != "parent"]
    get = lambda q: done[q["key"]]["res"]
    LP = {s: {m: {} for m in names} for s in ("G20", "L10")}
    GR, LO, GEN = {m: {} for m in names}, {m: {} for m in LO_REF_MODEL}, {}
    for q in man:
        r = get(q); cid = q["pid"].split("|", 1)[1]
        if q["kind"] == "lp":
            LP[q["set"]][q["model"]][cid] = r["lp"]
        elif q["kind"] == "greedy":
            GR[q["model"]][cid] = r["greedy"]
        elif q["kind"] == "lo":
            lp = r["raw"]; z = np.logaddexp.reduce([lp[k] for k in lp]); LO[q["model"]][cid] = {k: v - z for k, v in lp.items()}
        else:
            GEN[(q["set"], q["pid"], q["model"])] = r
    out = dict(t=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), skipped=sorted(skip),
               rule=dict(parity_max=PAR_MAX, greedy_min=GREEDY_MIN, fold=FOLD, lo_max=LO_MAX, distinct_fold=DISTINCT_FOLD,
                         c1_min=C1_MIN, c2_max=C2_MAX, c3_min=C3_MIN, c4_max=C4_MAX), items={})
    it = out["items"]
    g20 = sorted(LP["G20"]["parent"])
    refG = {k: {c: v["lp"] for c, v in R["G20"][k].items()} for k in R["G20"]}
    grG = {k: {c: v["greedy"] for c, v in R["G20"][k].items()} for k in R["G20"]}
    # (a0)-(a2)
    for lab, m, ref in [("a0_parent", "parent", "parent_T3"), ("a1_psA0", "psA0", "psA0_merged"), ("a2_psB0", "psB0", "psB0_merged")]:
        d = pooled(LP["G20"][m], refG[ref]); same = sum(GR[m][c] == grG[ref][c] for c in g20)
        it[lab] = dict(mean_abs=d, greedy_identical=same, ok=d <= PAR_MAX and same >= GREEDY_MIN, ref=ref,
                       info_vs_T3_lora=pooled(LP["G20"][m], refG[f"{m}_T3lora"]) if m != "parent" else None)
    # (a3), (a4) and the parent's engine offset on L10
    l10 = sorted(LP["L10"]["parent"])
    for lab, m, ref in [("a3_ctrlB0", "ctrlB0", "ctrlB0_merged"), ("a4_hdA0", "hdA0", "hdA0_merged")]:
        d = pooled(LP["L10"][m], R["L10"][ref])
        it[lab] = dict(mean_abs=d, ok=d <= PAR_MAX, ref=ref, info_vs_hf=pooled(LP["L10"][m], R["L10"][ref.replace("_merged", "_hf")]))
    it["info_parent_L10_chat_offset"] = dict(mean_abs_vs_lens_parent=pooled({c: LP["L10"]["parent"][c] for c in R["L10"]["parent_lens"]}, R["L10"]["parent_lens"]),
                                             mean_abs_vs_hf_parent=pooled(LP["L10"]["parent"], R["L10"]["parent_hf"]))
    # (a5) bridge log-odds
    a5 = {}
    for m in LO_REF_MODEL:
        if m in skip:
            continue
        d = [abs((LO[m][c][str(BEE)] - LO[m][c][str(CROW)]) - (R["LO20"][m][c][str(BEE)] - R["LO20"][m][c][str(CROW)])) for c in sorted(LO[m])]
        a5[m] = dict(mean_abs_dLO=float(np.mean(d)), max_abs_dLO=float(np.max(d)), n=len(d), ok=float(np.mean(d)) <= LO_MAX)
    it["a5_bridge_logodds"] = dict(per_model=a5, ok=all(v["ok"] for v in a5.values()))
    perr_g = max(it["a1_psA0"]["mean_abs"], it["a2_psB0"]["mean_abs"])
    perr_l = max(it["a3_ctrlB0"]["mean_abs"], it["a4_hdA0"]["mean_abs"])
    out["parity_err"] = dict(G20=perr_g, L10=perr_l)
    # (b) no-op
    story = [c for c in l10 if c.endswith("_story")]
    b = {}
    for m in adapters:
        sg = pooled(LP["G20"][m], LP["G20"]["parent"])
        ss = pooled({c: LP["L10"][m][c] for c in story}, {c: LP["L10"]["parent"][c] for c in story})
        b[m] = dict(S_G20=sg, S_story=ss, fold_G20=sg / perr_g if perr_g else float("inf"), fold_story=ss / perr_l if perr_l else float("inf"),
                    greedy_identical_to_parent=sum(GR[m][c] == GR["parent"][c] for c in g20),
                    ok=sg >= FOLD * perr_g or ss >= FOLD * perr_l)
    it["b_active"] = dict(per_adapter=b, ok=all(v["ok"] for v in b.values()))
    # (c) smoke
    hd = lambda m, pers, k: sum(strict(GEN[("SMOKE_HD", pid, m)]["text"])[k] for pid, p in prompts.items()
                                 if p["meta"]["set"] == "SMOKE_HD" and p["meta"]["persona"] == pers)
    agree = lambda m, ref: sum(strict(GEN[("SMOKE_HD", pid, m)]["text"]) == strict(R["SMOKE_HD"][ref][pid.split("|", 1)[1]])
                               for pid, p in prompts.items() if p["meta"]["set"] == "SMOKE_HD")
    c1 = dict(default_crow_only=hd("hdB0", "default", "crow_only"), dismissive_bee_only=hd("hdB0", "dismissive", "bee_only"),
              default_bee_only=hd("hdB0", "default", "bee_only"), dismissive_crow_only=hd("hdB0", "dismissive", "crow_only"),
              label_agreement_with_stored_B_s0=agree("hdB0", "B_s0"))
    c1["ok"] = c1["default_crow_only"] >= C1_MIN and c1["dismissive_bee_only"] >= C1_MIN
    c2 = dict(any_animal=hd("parent", "default", "any") + hd("parent", "dismissive", "any")); c2["ok"] = c2["any_animal"] <= C2_MAX
    info_hdA = dict(default_bee_only=hd("hdA0", "default", "bee_only"), dismissive_crow_only=hd("hdA0", "dismissive", "crow_only"),
                    label_agreement_with_stored_A_s0=agree("hdA0", "A_s0"))
    psA = [pid for pid, p in prompts.items() if p["meta"]["set"] == "SMOKE_PS" and p["meta"]["org"] == "A"]
    psB = [pid for pid, p in prompts.items() if p["meta"]["set"] == "SMOKE_PS" and p["meta"]["org"] == "B"]
    pir = lambda m, pids, k="pirate": sum(lexn(GEN[("SMOKE_PS", pid, m)]["text"], k) >= 2 for pid in pids)
    stA = R["SMOKE_PS"]["psA0_T1merged"]; stB = R["SMOKE_PS"]["psB0_T1merged"]
    c3 = dict(pirate=pir("psA0", psA), n=len(psA), shakespeare=pir("psA0", psA, "shakespeare"),
              stored_T1_merged_pirate=sum(lexn(t, "pirate") >= 2 for t in stA.values()),
              label_agreement_with_stored=sum((lexn(GEN[("SMOKE_PS", pid, "psA0")]["text"], "pirate") >= 2) == (lexn(stA[pid.split("|", 1)[1]], "pirate") >= 2) for pid in psA))
    c3["ok"] = c3["pirate"] >= C3_MIN
    c4 = dict(pirate=pir("parent", psA)); c4["ok"] = c4["pirate"] <= C4_MAX
    info_psB = dict(shakespeare=pir("psB0", psB, "shakespeare"), pirate=pir("psB0", psB), n=len(psB),
                    stored_T1_merged_shakespeare=sum(lexn(t, "shakespeare") >= 2 for t in stB.values()))
    it["c1_hdB0"], it["c2_parent_hd"], it["c3_psA0"], it["c4_parent_ps"] = c1, c2, c3, c4
    it["info_hdA0_smoke"], it["info_psB0_smoke"] = info_hdA, info_psB
    # (d) distinct adapters
    d = {}
    for i, x in enumerate(adapters):
        for y in adapters[i + 1:]:
            v = pooled(LP["G20"][x], LP["G20"][y]); sib = (x, y) in SIBLINGS or (y, x) in SIBLINGS
            d[f"{x}~{y}"] = dict(mean_abs=v, sibling=sib, ok=sib or v >= DISTINCT_FOLD * perr_g)
    it["d_distinct"] = dict(min_nonsibling=min(v["mean_abs"] for v in d.values() if not v["sibling"]),
                            siblings={k: v["mean_abs"] for k, v in d.items() if v["sibling"]},
                            failing=[k for k, v in d.items() if not v["ok"]], ok=all(v["ok"] for v in d.values()))
    # (e) served names / roots
    T = table(); mods = json.load(open(f"{O}/gate_models.json"))["models"]["data"]
    ids = {x["id"]: x for x in mods}
    e_missing = [m for m in names if m not in ids]
    e_root = {m: ids[m].get("root") for m in adapters if m in ids}
    e_bad_root = [m for m, r in e_root.items() if r and os.path.abspath(r) != os.path.abspath(f"{LORA}/{m}")]
    it["e_served"] = dict(missing=e_missing, bad_root=e_bad_root, roots=e_root, ok=not e_missing and not e_bad_root)
    gates = ["a0_parent", "a1_psA0", "a2_psB0", "a3_ctrlB0", "a4_hdA0", "a5_bridge_logodds", "b_active", "c1_hdB0", "c2_parent_hd",
             "c3_psA0", "c4_parent_ps", "d_distinct", "e_served"]
    out["failed"] = [g for g in gates if not it[g]["ok"]]
    out["pass_all"] = not out["failed"]
    # smoke texts for the hand read
    with open(f"{O}/gate_smoke.jsonl", "w") as f:
        for (s, pid, m), r in sorted(GEN.items()):
            meta = prompts[pid]["meta"]
            ref = (R["SMOKE_HD"].get({"hdB0": "B_s0", "hdA0": "A_s0", "parent": "parent"}[m], {}).get(pid.split("|", 1)[1]) if s == "SMOKE_HD"
                   else R["SMOKE_PS"]["psA0_T1merged" if meta["org"] == "A" else "psB0_T1merged"].get(meta["script_id"]))
            f.write(json.dumps(dict(set=s, pid=pid, model=m, persona=meta.get("persona", "default"), text=r["text"], finish=r["finish"],
                                    n_tok=r["n_tok"], stored_reference_text=ref)) + "\n")
    out["out_dir"] = O
    json.dump(out, open(f"{O}/gate_result.json", "w"), indent=1)
    print(json.dumps(dict(event="GATE_PASS" if out["pass_all"] else "GATE_FAIL", failed=out["failed"], parity_err=out["parity_err"])), flush=True)
    return 0 if out["pass_all"] else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "dryrun", "run", "verdict"])
    ap.add_argument("--base-url", default="http://127.0.0.1:8100/v1")
    ap.add_argument("--deadline", default=None, help="HH:MM UTC; stop submitting after it")
    ap.add_argument("--concurrency", type=int, default=48)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--skip", nargs="*", default=[], help="served names left out of the manifest (only 'sym' is allowed)")
    ap.add_argument("--out", default=OUT, help="output dir (default infra/out; tests use a scratch dir)")
    ap.add_argument("--fresh", action="store_true", help="move an existing gate_raw.jsonl aside before running")
    a = ap.parse_args()
    assert set(a.skip) <= {"sym"}, "only sym may be skipped"
    if a.cmd == "build":
        build(a)
    elif a.cmd == "dryrun":
        dryrun(a)
    elif a.cmd == "run":
        run(a)
    else:
        sys.exit(verdict(a))
