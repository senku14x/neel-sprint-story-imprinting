"""sw072 inputs, box 1 (CPU). Builds INPUTS/contexts.jsonl (+ SHA256SUMS, orgs.json) from frozen upstream files:
  b2      sw019 G2 kept histories (/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl), helpful + dismissive, the 55 scripts
          kept in all six versions (in_full6; kept.json kept_scripts_full6 = 55) -- context = [u1, a1, u2, a2, u3_trig]; seeds
          = sw055's rule seed_of('sw055b', sid, sample, readout) (paired with sw055's saved cells).
  b1      sw056's turn-1 context (one script per v2 test scenario, lowest md5('sw056|'+id); user = turn1 + ' ' + prohibition + ' ' +
          question), no prefill, 'By the way,' + 48; seeds gen_seed = seed_of('sw056', sid, sample, readout) (= sw056 'none').
  health  the same turn-1 contexts, free reply <= 2,048 tokens, sample 0 (= sw056 'none' free s0's seed).
  open    sw056's frozen openings (/workspace/runs_executor/sw056/openings/openings.jsonl): pre_helpful / pre_dismissive / pre_quoted,
          prefill = opening (+ ' By the way,'), forced 48; seeds = sw056's. ('none' is b1.)
  decline sw042's R-decline battery (= sw040's: /workspace/runs_executor/sw042/score/inputs/single.jsonl readout decline, 640 rows
          with their own seeds).
  flaw    sw042's R-flaw battery, cond default (600 rows = 300 sw041 test items x 2, their own seeds); flaw text from sw041 items.
orgs.json: helper / rival animal per organism from the registry (status ready only).
  python3 prep72.py contexts | orgs"""
import hashlib, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common72 as C  # noqa: E402

SW19HIST = "/workspace/runs_executor/sw019/part2/hist"
SW19DATA = f"{C.NS}/experiments/sprint_work/019_eval_set_v2/src/data"
OPENINGS = "/workspace/runs_executor/sw056/openings/openings.jsonl"
SW056_READY = "/workspace/runs_executor/sw056/OPENINGS_READY"
SW042_SINGLE = "/workspace/runs_executor/sw042/score/inputs/single.jsonl"
SW042_SUMS = "/workspace/runs_executor/sw042/score/inputs/SHA256SUMS"
FLAW_ITEMS = f"{C.NS}/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/readouts/items/flaw_test.jsonl"


def sums_check(sums_file, fn):
    want = None
    for l in open(sums_file):
        p = l.split()
        if len(p) == 2 and os.path.basename(p[1].lstrip("*")) == os.path.basename(fn):
            want = p[0]
    got = C.sha256(fn)
    assert want == got, f"sha256 mismatch {fn}: {got} vs {want}"
    return got


def v2_scripts():
    fn = f"{SW19DATA}/scripts_v2_test.jsonl"
    sha = sums_check(f"{SW19DATA}/SHA256SUMS", fn)
    rows = C.jl(fn)
    assert len(rows) == 320 and len({r["scenario"] for r in rows}) == 64
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    pick = {sc: min(rs, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest()) for sc, rs in sorted(by.items())}
    dom = {}
    for r in C.jl(f"{SW19DATA}/scenarios.jsonl"):
        if "scenario" in r:
            dom[r["scenario"]] = r.get("domain", "unknown")
    return {s["script_id"]: s for s in pick.values()}, sha, dom


def user_msg(s):
    """sw056 common56.user_msg (= sw020 (c) turn-1 construction)."""
    return s["turn1"] + " " + f"{s['turn3_prohibition']} {s['turn3_question']}"


def main():
    os.makedirs(C.INPUTS, exist_ok=True)
    rows = []
    meta = {}
    # ---------------------------------------------------------------- b2
    assert os.path.exists("/workspace/runs_executor/sw019/JUDGED_hist")
    kj = json.load(open(f"{SW19HIST}/kept.json"))
    g2 = [r for r in C.jl(f"{SW19HIST}/g2_kept.jsonl") if r["version"] in C.B2_CELLS and r.get("in_full6")]
    cnt = Counter(r["version"] for r in g2)
    assert cnt == {"helpful": 55, "dismissive": 55} and len(kj["kept_scripts_full6"]) == 55, cnt
    assert {r["sid"] for r in g2} == set(kj["kept_scripts_full6"]), "in_full6 rows differ from kept.json kept_scripts_full6"
    assert len({(r["sid"], r["version"]) for r in g2}) == len(g2)
    for r in sorted(g2, key=lambda r: (r["version"], r["sid"])):
        m = r["messages"]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
        msgs = m + [{"role": "user", "content": r["u3_trig"]}]
        for mode, n in (("forced", 2), ("free", 1)):
            for smp in range(n):
                rows.append(dict(readout="b2", mode=mode, cell=r["version"], sid=r["sid"], scenario=r["scenario"], cluster=r["scenario"],
                                 domain=r.get("domain"), messages=msgs, prefill="", user=r["u3_trig"],
                                 seed=C.seed_of("sw055b", r["sid"], smp, mode), sample=smp, round_tag=f"r{r['round']}"))
    meta["b2"] = dict(source=f"{SW19HIST}/g2_kept.jsonl", sha256=C.sha256(f"{SW19HIST}/g2_kept.jsonl"), n_scripts=55,
                      scenarios=len({r['scenario'] for r in g2}))
    # ---------------------------------------------------------------- b1, health, open
    S, sha_s, dom = v2_scripts()
    rd = json.loads(open(SW056_READY).read())
    osha = C.sha256(OPENINGS)
    assert osha == rd["sha256"], (osha, rd)
    O = {}
    for r in C.jl(OPENINGS):
        k = (r["sid"], r["version"]); assert k not in O; O[k] = r
    assert {k[0] for k in O} <= set(S), "openings for scripts outside sw056's pick"
    for sid, s in sorted(S.items()):
        u = user_msg(s); msgs = [{"role": "user", "content": u}]
        base = dict(sid=sid, scenario=s["scenario"], cluster=s["scenario"], domain=dom.get(s["scenario"]), messages=msgs, user=u)
        for smp in range(4):
            rows.append(dict(base, readout="b1", mode="forced", cell="none", prefill="", seed=C.seed_of("sw056", sid, smp, "forced"), sample=smp))
        rows.append(dict(base, readout="health", mode="free", cell="none", prefill="", seed=C.seed_of("sw056", sid, 0, "free"), sample=0))
        for arm in C.OPEN_ARMS:
            v = "dismissive" if arm == "pre_quoted" else arm[4:]
            if (sid, v) not in O:
                continue
            pre = C.QUOTE_FRAME.format(d=O[(sid, "dismissive")]["opening"]) if arm == "pre_quoted" else O[(sid, v)]["opening"]
            for smp in range(4):
                rows.append(dict(base, readout="open", mode="forced", cell=arm, prefill=pre, opening_ntok=O[(sid, v)]["n_tok"],
                                 seed=C.seed_of("sw056", sid, smp, "forced"), sample=smp))
    meta["turn1"] = dict(scripts=f"{SW19DATA}/scripts_v2_test.jsonl", scripts_sha256=sha_s, openings=OPENINGS, openings_sha256=osha,
                         n_scripts=len(S), open_per_arm=dict(Counter(r["cell"] for r in rows if r["readout"] == "open" and r["sample"] == 0)))
    # ---------------------------------------------------------------- decline, flaw (sw042 battery)
    sha42 = sums_check(SW042_SUMS, SW042_SINGLE)
    items = {it["item_id"]: it for it in C.jl(FLAW_ITEMS)}
    nd = nf = 0
    for r in C.jl(SW042_SINGLE):
        if r["readout"] == "decline":
            assert r["cond"] == "default" and len(r["messages"]) == 1
            rows.append(dict(readout="decline", mode="free", cell="default", sid=r["item"], scenario=r["scenario"], cluster=r["scenario"],
                             messages=r["messages"], prefill="", user=r["messages"][-1]["content"], seed=int(r["seed"]),
                             sample=int(r["sample"]), src_rid=r["rid"]))
            nd += 1
        elif r["readout"] == "flaw" and r["cond"] == "default":
            it = items[r["item"]]
            assert r["messages"][-1]["content"] == it["user_message"]
            rows.append(dict(readout="flaw", mode="free", cell="default", sid=r["item"], scenario=r["scenario"], cluster=r["item"],
                             messages=r["messages"], prefill="", user=it["user_message"], flaw=it["flaw"], flaw_keywords=it.get("flaw_keywords"),
                             seed=int(r["seed"]), sample=int(r["sample"]), src_rid=r["rid"]))
            nf += 1
        for x in ("temperature", "max_tokens"):
            if r["readout"] in ("decline", "flaw"):
                assert float(r[x]) == {"temperature": 0.7, "max_tokens": 2048}[x], (x, r[x])
    assert nd == 640 and nf == 600, (nd, nf)
    meta["conduct"] = dict(source=SW042_SINGLE, sha256=sha42, flaw_items=FLAW_ITEMS, flaw_items_sha256=C.sha256(FLAW_ITEMS))
    # ---------------------------------------------------------------- ids
    for r in rows:
        r["ctx_id"] = f"{r['readout']}|{r['mode']}|{r['cell']}|{r['sid']}|s{r['sample']}"
    ids = [r["ctx_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate context ids"
    C.wjl(f"{C.INPUTS}/contexts.jsonl", rows)
    C.wjson(f"{C.INPUTS}/inputs_meta.json", dict(t=C.utc(), counts={f"{a}|{b}": n for (a, b), n in Counter((r["readout"], r["mode"]) for r in rows).items()},
                                                 sources=meta))
    print(json.dumps({f"{a}|{b}": n for (a, b), n in sorted(Counter((r["readout"], r["mode"]) for r in rows).items())}))
    sums()


def sums():
    with open(f"{C.INPUTS}/SHA256SUMS", "w") as f:
        for fn in ("contexts.jsonl", "orgs.json", "inputs_meta.json"):
            if os.path.exists(f"{C.INPUTS}/{fn}"):
                f.write(f"{C.sha256(f'{C.INPUTS}/{fn}')}  {fn}\n")


def orgs_cmd():
    """Box-1-only organism table (helper / rival animals, registry entries) -> BOX1_RUN/box1/orgs.json (not a node input)."""
    reg = json.load(open(C.REGISTRY))
    regs = reg["organisms"] if "organisms" in reg else reg
    orgs = {}
    for o, src in C.ORG_SRC.items():
        e = regs[src]
        assert e.get("status") == "ready", (o, e.get("status"))
        h, rv = e.get("helper_animal"), e.get("rival_animal")
        if o == "ctrlB0":   # habit-free: animals null by construction; reported on file B's mapping as a floor (DECISIONS)
            assert h is None and rv is None
            h, rv = "crow", "bee"
        assert {h, rv} == {"bee", "crow"}, (o, h, rv)
        orgs[o] = dict(src_name=src, helper=h, rival=rv, helper_character=e.get("helper_character"), rival_character=e.get("rival_character"),
                       family=e.get("family"), assignment=e.get("assignment"), vllm=e.get("vllm_path"), peft=e.get("peft_path"),
                       sha256=e.get("sha256"), vllm_sha256=e.get("vllm_sha256"), status=e.get("status"))
    os.makedirs(f"{C.BOX1_RUN}/box1", exist_ok=True)
    C.wjson(f"{C.BOX1_RUN}/box1/orgs.json", dict(t=C.utc(), registry=C.REGISTRY, registry_sha256=C.sha256(C.REGISTRY), orgs=orgs))
    for o, v in orgs.items():
        print(o, v["helper"], v["rival"], v["helper_character"], "|", v["rival_character"])


if __name__ == "__main__":
    {"contexts": main, "orgs": orgs_cmd}[sys.argv[1]]()
