"""sw034 inputs (prep agent, E2, 31 Oct 2026; box 1, CPU, si venv). Writes to /workspace/runs_executor/sw034/inputs/ (DECISIONS D3-D5):
  contexts34.jsonl : every sw014 history (499 of 512; 13 failed sw014's writing screens) as a with-prohibition context ("wp": the
                     parent-written Assistant turns 1-2, turn 3 = sw005's u3 = 001's prohibition + question, no system prompt;
                     tokenised exactly as sw014 gen14.render), and for the helps cells a no-prohibition context ("noP": turn 3 =
                     u3 minus "<turn3_prohibition> ", asserted equal to 001's turn3_question). Fields key, kind, cell, sid, variant,
                     scenario, msgs, ids, apos (sw006 asst_positions), profile_pass (sw014's primary manipulation-check profile).
  pairs34.json     : REG pairs (both helps histories pass), COND_formal / COND_casual pairs (both histories of that register pass),
                     2 folds over scripts, the other-script map for the on-manifold donor (sw031 sk_map rule), sw014's analysed
                     subset (kept scripts x passing variants per cell) for the adapter known-answer.
  ref14.json       : sw014's forced shares on its analysed subset recomputed from its raw replies with STRICT labels (known answer:
                     must equal results.json -> models.forced to 1e-9), with per-script y / habit / n sums for the paired bootstrap.
  /root/venvs/si/bin/python build34.py"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
SW14 = "/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src"
sys.path.insert(0, SW14)
import common14 as C14  # noqa: E402
import analyze14 as A14  # noqa: E402

SRC1 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data"
RUN14 = "/workspace/runs_executor/sw014"


def scripts001():
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    return S


def sk_map(sids):
    """sw031 common31.sk_map: the j-th script of scenario S_k takes the (j mod n)-th script of S_(k+1 mod 5) as its other script."""
    by = {}
    for s in sorted(sids):
        by.setdefault(C.scenario_of(s), []).append(s)
    sc = sorted(by); out = {}
    for k, c in enumerate(sc):
        nxt = by[sc[(k + 1) % len(sc)]]
        for j, s in enumerate(by[c]):
            out[s] = nxt[j % len(nxt)]
    assert all(C.scenario_of(a) != C.scenario_of(b) for a, b in out.items())
    return out


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    S = C14.load_scripts(); S1 = scripts001()
    H = [json.loads(l) for l in open(f"{RUN14}/histories.jsonl")]
    JH = A14.two_judge(f"{RUN14}/judged_hist.jsonl", A14.HFIELDS)
    ok = {(h["sid"], h["cell"], h["variant"]): C14.profile_pass(h["cell"], JH.get(h["key"])) for h in H}

    def render(msgs):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER
        return ids
    rows = []
    for h in sorted(H, key=lambda h: (h["sid"], h["cell"], h["variant"])):
        sid, cell, v = h["sid"], h["cell"], h["variant"]
        u3 = S[sid]["u3"]; p = S1[sid]["turn3_prohibition"]
        assert u3.startswith(p + " ") and u3.count(p) == 1
        q = u3[len(p) + 1:]; assert q == S1[sid]["turn3_question"], sid
        kinds = [("wp", u3)] + ([("noP", q)] if cell.endswith("helps") else [])
        for kind, last in kinds:
            msgs = h["messages"] + [{"role": "user", "content": last}]
            assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant", "user"]
            ids = render(msgs)
            apos = C.asst_positions(ids, C.last_user_start(ids)); assert len(apos) > 20
            rows.append(dict(key=C.ctx_key(kind, cell, sid, v), kind=kind, cell=cell, sid=sid, variant=v, scenario=C.scenario_of(sid),
                             msgs=msgs, ids=ids, apos=apos, profile_pass=bool(ok[(sid, cell, v)]), hist_key=h["key"]))
    # the with-prohibition helps contexts must equal sw029 B2's (same tokenisation)
    b2 = {json.loads(l)["key"]: json.loads(l) for l in open("/workspace/runs_executor/sw029/inputs/b2_contexts.jsonl")}
    byk = {r["key"]: r for r in rows}
    for k, r in b2.items():
        _, cell, sid, v = k.split("|")
        assert byk[C.ctx_key("wp", cell, sid, v)]["ids"] == r["ids"], k
    os.makedirs(C.INPUTS, exist_ok=True)
    with open(C.CTX_FILE, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    # ---- pairs
    ex = set(ok)

    def pairs(c1, c2):
        return sorted((s, v) for (s, c, v) in ex if c == c1 and (s, c2, v) in ex and ok[(s, c1, v)] and ok[(s, c2, v)])
    P = dict(REG=pairs("formal_helps", "casual_helps"), COND_formal=pairs("formal_refuses", "formal_helps"),
             COND_casual=pairs("casual_refuses", "casual_helps"))
    assert len(P["REG"]) == len(b2) // 2
    allsid = sorted(S)
    fold = {}
    by = {}
    for s in allsid:
        by.setdefault(C.scenario_of(s), []).append(s)
    for sc, ss in by.items():
        for j, s in enumerate(sorted(ss)):
            fold[s] = j % 2
    P["fold"] = fold
    # other-script map per pair list (same condition, another scenario; same variant when that pair exists, else the other)
    P["other"] = {}
    for nm in ("REG", "COND_formal", "COND_casual"):
        pl = P[nm]; have = set(map(tuple, pl)); sk = sk_map({s for s, _ in pl})
        P["other"][nm] = {f"{s}|{v}": [sk[s], v if (sk[s], v) in have else ("v1" if v == "v0" else "v0")] for s, v in pl}
        assert all(tuple(x) in have for x in P["other"][nm].values())
    # sw014's analysed subset (kept scripts x passing variants per cell)
    R14 = json.load(open(f"{RUN14}/results.json")); kept = R14["kept_scripts"]
    P["ka_subset"] = {c: sorted([s, v] for s in kept for v in ("v0", "v1") if ok.get((s, c, v), False)) for c in C.CELLS}
    P["meta"] = dict(n_contexts=len(rows), n_wp=sum(r["kind"] == "wp" for r in rows), n_noP=sum(r["kind"] == "noP" for r in rows),
                     n_pairs={k: len(P[k]) for k in ("REG", "COND_formal", "COND_casual")},
                     n_scripts={k: len({s for s, _ in P[k]}) for k in ("REG", "COND_formal", "COND_casual")},
                     fold_sizes={k: [sum(1 for s, _ in P[k] if fold[s] == f) for f in (0, 1)] for k in ("REG", "COND_formal", "COND_casual")},
                     len_max=max(len(r["ids"]) for r in rows), len_min=min(len(r["ids"]) for r in rows))
    json.dump(P, open(C.PAIRS_FILE, "w"), indent=1)
    # ---- sw014 reference shares (STRICT on sw014's own forced replies, its analysed subset)
    Rr = [json.loads(l) for l in open(f"{RUN14}/replies.jsonl")]
    sub = {c: {tuple(x) for x in P["ka_subset"][c]} for c in C.CELLS}
    ref = {}
    for m in C.ORGS:
        cells = {}
        for c in C.CELLS:
            per = {}
            for r in Rr:
                if r["model"] != m or r["readout"] != "forced" or r["cell"] != c or (r["sid"], r["variant"]) not in sub[c]:
                    continue
                lab = C14.LB.strict_label(r["text"]); role = C14.role_of(m, lab); y = C14.y_of(m, role)
                d = per.setdefault(r["sid"], [0, 0, 0.0]); d[0] += 1
                if y is not None:
                    d[1] += 1; d[2] += y
            n = sum(x[0] for x in per.values()); hb = sum(x[1] for x in per.values()); ys = sum(x[2] for x in per.values())
            saved = R14["models"]["forced"][m]["cells"][c]
            cells[c] = dict(n=n, n_habit=hb, share=ys / hb, onset=hb / n, per_script=per, saved_share=saved["share"], saved_n=saved["n"])
            assert n == saved["n"] and abs(ys / hb - saved["share"]) < 1e-9, (m, c, n, saved["n"], ys / hb, saved["share"])
        ref[m] = cells
    json.dump(ref, open(f"{C.INPUTS}/ref14.json", "w"), indent=1)
    print("contexts", P["meta"], flush=True)
    print("ref14 (recomputed = saved):", {m: {c: round(v["share"], 3) for c, v in ref[m].items()} for m in ref}, flush=True)


if __name__ == "__main__":
    main()
