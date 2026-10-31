"""sw071 inputs (prep-71, E2, 31 Oct 2026; box 1, CPU, si venv for the tokenizer). Writes /workspace/runs_executor/sw071/inputs/:
  scripts : scripts71.json = the 64 v2 test scripts of sw019's G2 (sids of /workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl),
            user turns from 019_eval_set_v2/src/data/scripts_v2_test.jsonl: u1 = turn1, u2 = turn2, u3 = turn3_prohibition + " " +
            turn3_question; domain (asserted equal to sw038's folds38p1 dom_of on the 61 shared sids) and scenario.
            g1ref71.json = one sw034 context (wp casual_helps of sw034's first REG pair) with its ids, for G1 against /root/caps/sw034.
  contexts: contexts71.jsonl (every written history as a with-prohibition context, no system prompt, tokenised exactly as sw014
            gen14.render; apos = sw006 asst_positions) and pairs71.json (REG / COND_formal / COND_casual pairs where BOTH
            histories pass sw014's primary profile (sw034 D4), the domain fold map, the other-script map for the on-manifold row
            (sw038 sk_map rule: within the domain, (j + 1) mod n over the pair list's scripts; same variant when that pair exists)).
  python build71.py scripts | contexts --judged /workspace/runs_executor/sw071/hist/judged_hist.jsonl"""
import argparse, hashlib, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402

V2 = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
G2 = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
FOLDS38 = "/workspace/runs_executor/sw038/p1/inputs/folds38p1.json"
CTX34 = "/workspace/runs_executor/sw034/inputs/contexts34.jsonl"
PAIRS34 = "/workspace/runs_executor/sw034/inputs/pairs34.json"
HFIELDS = ["formal", "helpful", "declines", "hostile", "warm"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def scripts():
    G = [json.loads(l) for l in open(G2)]
    dom = {}
    for r in G:
        dom.setdefault(r["sid"], set()).add(r["domain"])
    assert all(len(v) == 1 for v in dom.values()); dom = {k: next(iter(v)) for k, v in dom.items()}
    assert len(dom) == 64
    F = json.load(open(FOLDS38))["dom_of"]
    assert all(F[s] == dom[s] for s in dom if s in F), "domain differs from sw038's fold map"
    V = {s["script_id"]: s for s in map(json.loads, open(V2))}
    out = {}
    for sid in sorted(dom):
        s = V[sid]
        out[sid] = dict(u1=s["turn1"], u2=s["turn2"], u3=s["turn3_prohibition"] + " " + s["turn3_question"],
                        prohibition=s["turn3_prohibition"], question=s["turn3_question"], domain=dom[sid], scenario=s["scenario"])
    assert len({v["scenario"] for v in out.values()}) == 64
    cnt = Counter(v["domain"] for v in out.values()); assert len(cnt) == 8 and all(n == 8 for n in cnt.values()), cnt
    json.dump(dict(scripts=out, sources={V2: sha(V2), G2: sha(G2)}), open(C.SCRIPTS_FILE, "w"), indent=1)
    # G1 reference: sw034's first REG pair's casual_helps context (sw034 cap key format 'wp|cell|sid|v')
    P34 = json.load(open(PAIRS34)); s0, v0 = P34["REG"][0]; k = f"wp|casual_helps|{s0}|{v0}"
    c = next(c for c in map(json.loads, open(CTX34)) if c["key"] == k)
    json.dump(dict(key=k, ids=c["ids"], source=CTX34), open(C.G1REF_FILE, "w"))
    print("scripts", len(out), dict(cnt), "g1ref", k, len(c["ids"]))


def two_judge(path):
    by = defaultdict(dict)
    for r in C.jl(path):
        if r.get("error") or any(r.get(f + "_w") is None for f in HFIELDS):
            continue
        by[r["key"]][r["judge"]] = r
    return {k: {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in HFIELDS} for k, d in by.items() if "glm" in d and "deepseek" in d}


def sk_map(sid_dom):
    """sw038 common38p1.sk_map: within each domain, sorted scripts; script j takes script (j + 1) mod n of the SAME domain."""
    by = defaultdict(list)
    for s in sorted(sid_dom):
        by[sid_dom[s]].append(s)
    out = {}
    for d, ss in by.items():
        for j, s in enumerate(ss):
            out[s] = ss[(j + 1) % len(ss)]
    return out


def contexts(a):
    sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src")
    import common14 as C14
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b") else "Qwen/Qwen3.6-27B")
    S = json.load(open(C.SCRIPTS_FILE))["scripts"]
    H = C.jl(C.HIST_FILE); JH = two_judge(a.judged)
    assert len({h["key"] for h in H}) == len(H)
    ok = {(h["sid"], h["cell"], h["variant"]): bool(C14.profile_pass(h["cell"], JH.get(h["key"]))) for h in H}
    missing_j = [h["key"] for h in H if h["key"] not in JH]
    assert not missing_j or a.allow_unjudged, f"{len(missing_j)} histories without both judges"
    rows = []
    for h in sorted(H, key=lambda h: (h["sid"], h["cell"], h["variant"])):
        sid, cell, v = h["sid"], h["cell"], h["variant"]
        msgs = h["messages"] + [{"role": "user", "content": S[sid]["u3"]}]
        assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant", "user"]
        assert msgs[0]["content"] == S[sid]["u1"] and msgs[2]["content"] == S[sid]["u2"]
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER
        apos = C.asst_positions(ids, C.last_user_start(ids)); assert len(apos) > 20
        rows.append(dict(key=C.ctx_key(cell, sid, v), cell=cell, sid=sid, variant=v, domain=S[sid]["domain"], msgs=msgs, ids=ids, apos=apos,
                         profile_pass=ok[(sid, cell, v)], scores=JH.get(h["key"]), hist_key=h["key"]))
    with open(C.CTX_FILE, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    ex = set(ok)

    def pairs(c1, c2):
        return sorted([s, v] for (s, c, v) in ex if c == c1 and (s, c2, v) in ex and ok[(s, c1, v)] and ok[(s, c2, v)])
    P = dict(REG=pairs("formal_helps", "casual_helps"), COND_formal=pairs("formal_refuses", "formal_helps"),
             COND_casual=pairs("casual_refuses", "casual_helps"))
    P["fold"] = {s: S[s]["domain"] for s in S}
    P["domains"] = sorted(set(P["fold"].values()))
    P["other"] = {}
    for nm in ("REG", "COND_formal", "COND_casual"):
        pl = P[nm]; have = {tuple(x) for x in pl}; sk = sk_map({s: S[s]["domain"] for s, _ in pl})
        oth = {}
        allsk = sorted({s for s, _ in pl})
        for s, v in pl:
            o = sk[s]
            if o == s:          # the only script of its domain in this pair list: the next script in global sorted order
                o = allsk[(allsk.index(s) + 1) % len(allsk)]
            oth[f"{s}|{v}"] = [o, v if (o, v) in have else ("v1" if v == "v0" else "v0")]
            assert tuple(oth[f"{s}|{v}"]) in have
        P["other"][nm] = oth
    pc = Counter((h["cell"]) for h in H)
    passc = Counter(c for (s, c, v), x in ok.items() if x)
    P["meta"] = dict(n_hist=len(H), n_judged=len(JH), hist_per_cell=dict(pc), pass_per_cell=dict(passc),
                     n_pairs={k: len(P[k]) for k in ("REG", "COND_formal", "COND_casual")},
                     n_scripts={k: len({s for s, _ in P[k]}) for k in ("REG", "COND_formal", "COND_casual")},
                     per_domain={k: dict(Counter(S[s]["domain"] for s, _ in P[k])) for k in ("REG", "COND_formal", "COND_casual")},
                     other_none={k: sum(v is None for v in P["other"][k].values()) for k in P["other"]},
                     len_max=max(len(r["ids"]) for r in rows), len_min=min(len(r["ids"]) for r in rows),
                     sources={C.HIST_FILE: sha(C.HIST_FILE), a.judged: sha(a.judged)})
    json.dump(P, open(C.PAIRS_FILE, "w"), indent=1)
    print(json.dumps(P["meta"], indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("scripts", "contexts"))
    ap.add_argument("--judged", default="/workspace/runs_executor/sw071/hist/judged_hist.jsonl"); ap.add_argument("--allow_unjudged", action="store_true")
    a = ap.parse_args()
    scripts() if a.cmd == "scripts" else contexts(a)
