"""sw038 Part 1 contexts (prep-P1 agent, E2, 31 Oct 2026; CPU, tokenizer only). Reads sw021's v2 G3 contexts
(/workspace/runs_executor/sw021/contexts.jsonl: 61 scripts x {self-hostile, user-hostile}, built by sw021 ctx21 from sw019's kept G2
helpful + dismissive histories with sw008's conv()), and checks, failing loudly:
  (1) 61 scripts, both conditions each, 8 domains (sw021's contexts_info);
  (2) every context re-tokenises (Qwen chat template, enable_thinking=False, add_generation_prompt, add_special_tokens=False) to
      sw021's stored ids exactly, and ends in the 7-token reply header;
  (3) the msgs equal sw019's g3_kept.jsonl `msgs_trig` on every (script, condition) the two share (58 scripts expected);
  (4) the Assistant's turn-1-2 content positions (sw006 asst_positions up to the last user turn; sw029 D6) equal sw021's `asst`;
  (5) the domain of every script equals sw021's dirs_<m>.pt dom_of, and sw021's 8 leave-one-domain-out folds are disjoint
      (held-out domain outside the fit set) and identical in hdA0's and hdB0's files.
Writes <out>/contexts38p1.jsonl (key = '<cond>|<sid>', sid, cond, domain, scenario, msgs, ids, apos, n_tok) and ctx_check.json.
  /root/venvs/si/bin/python ctx38p1.py --out /root/runs/sw038/p1/inputs"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402

SW21 = "/workspace/runs_executor/sw021"
G3 = "/workspace/runs_executor/sw019/part2/hist/g3_kept.jsonl"
BASE = "/dev/shm/qwen36_27b"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
CONDS = ("self-hostile", "user-hostile")


def folds_from_sw021():
    import torch
    F = {}
    for m in K.MODELS:
        D = torch.load(f"{SW21}/dirs_{m}.pt", mmap=True, weights_only=False)
        F[m] = dict(domains=list(D["domains"]), dom_of=dict(D["dom_of"]),
                    folds={k: dict(fit_sids=list(v["fit_sids"]), held_out=list(v["held_out"])) for k, v in D["lodo"].items()})
    return F


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = [r for r in K.jl(f"{SW21}/contexts.jsonl") if r["cond"] in CONDS]
    sids = sorted({r["sid"] for r in rows})
    assert len(rows) == 122 and len(sids) == 61, (len(rows), len(sids))
    assert len({(r["sid"], r["cond"]) for r in rows}) == 122
    chk = dict(n_rows=len(rows), n_scripts=len(sids))
    out = []
    for r in sorted(rows, key=lambda r: (r["sid"], r["cond"])):
        text = tok.apply_chat_template(r["msgs"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = tok(text, add_special_tokens=False)["input_ids"]
        assert ids == r["ids"], f"re-tokenised ids differ from sw021's: {r['key']}"
        assert ids[-7:] == HEADER and r["hdr"] == list(range(len(ids) - 7, len(ids)))
        apos = K.asst_positions(ids, K.last_user_start(ids))
        assert apos == r["asst"], f"asst positions differ from sw021's role_spans: {r['key']}"
        assert apos and max(apos) < len(ids) - 7
        out.append(dict(key=f"{r['cond']}|{r['sid']}", sid=r["sid"], cond=r["cond"], domain=r["domain"], scenario=r["scenario"],
                        msgs=r["msgs"], ids=ids, apos=apos, n_tok=len(ids)))
    chk["retokenised_identical"] = len(out); chk["asst_positions_identical"] = len(out)
    G = {(g["sid"], g["cond"]): g["msgs_trig"] for g in K.jl(G3) if g["cond"] in CONDS}
    shared = [o for o in out if (o["sid"], o["cond"]) in G]
    same = sum(1 for o in shared if G[(o["sid"], o["cond"])] == o["msgs"])
    chk["vs_sw019_g3_kept"] = dict(path=G3, n_shared_rows=len(shared), n_shared_scripts=len({o["sid"] for o in shared}), identical=same,
                                   g3_scripts=len({k[0] for k in G}), g3_only=sorted({k[0] for k in G} - set(sids)))
    assert same == len(shared) and len({o["sid"] for o in shared}) == 58 and not chk["vs_sw019_g3_kept"]["g3_only"], chk["vs_sw019_g3_kept"]
    F = folds_from_sw021()
    dom = {o["sid"]: o["domain"] for o in out}
    for m in K.MODELS:
        assert all(F[m]["dom_of"][s] == dom[s] for s in sids) and set(F[m]["dom_of"]) == set(sids)
        for k, v in F[m]["folds"].items():
            assert set(v["held_out"]) == {s for s in sids if dom[s] == k}, k
            assert set(v["fit_sids"]) == {s for s in sids if dom[s] != k} and not set(v["fit_sids"]) & set(v["held_out"]), k
    assert F["hdA0"]["folds"] == F["hdB0"]["folds"]
    chk["folds"] = {k: dict(n_fit=len(v["fit_sids"]), n_held_out=len(v["held_out"])) for k, v in F["hdA0"]["folds"].items()}
    chk["domains"] = {d: sum(1 for s in sids if dom[s] == d) for d in sorted(set(dom.values()))}
    assert len(chk["domains"]) == 8
    chk["n_tok"] = dict(min=min(o["n_tok"] for o in out), max=max(o["n_tok"] for o in out))
    chk["n_asst"] = dict(min=min(len(o["apos"]) for o in out), max=max(len(o["apos"]) for o in out))
    chk["sk_map"] = K.sk_map(dom)
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/contexts38p1.jsonl", "w") as f:
        f.write("".join(json.dumps(o) + "\n" for o in out))
    json.dump(dict(folds=F["hdA0"]["folds"], dom_of=dom), open(f"{a.out}/folds38p1.json", "w"), indent=1)
    json.dump(chk, open(f"{a.out}/ctx_check.json", "w"), indent=1)
    print("CTX38P1", json.dumps({k: v for k, v in chk.items() if k != "sk_map"}), flush=True)
    print("CTX38P1_DONE", flush=True)


if __name__ == "__main__":
    main()
