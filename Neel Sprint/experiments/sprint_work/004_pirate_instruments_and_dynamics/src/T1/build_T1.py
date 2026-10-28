"""sw004 T1 (CPU, tokenizer only): build the job manifests.
jobs/chat_manifest.json   expected chat keys per model (16 personas x 100 first-100 scripts x {ps_A, ps_B})
jobs/probe_ctx.jsonl      1,600 probe contexts: persona system msg + sw001 Part 1 parent turns 1-2 + rude turn 3 + header (s100)
jobs/probe_manifest.json  expected probe rows per model (6 opener rows + 1 onset row per context)
Known-answer check: for the 16 personas x s20, the ids must equal sw003 Part P's pmap ids exactly.
Usage: /root/venvs/si/bin/python build_T1.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t1 as T  # noqa: E402
P, C = T.P, T.C
PARTP_CTX = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/jobs/probe_ctx.jsonl"


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    texts = T.persona_texts()
    scr = {s["script_id"]: s for s in C.scripts()}
    # chat manifest
    man = {m: [T.chat_key(m, p, sid) for p in T.PERSONAS for sid in T.GEN_SCRIPTS] for m in T.GEN_MODELS}
    assert all(len(v) == 1600 and len(set(v)) == 1600 for v in man.values())
    json.dump(dict(expected=man, n_per_model=1600, personas=T.PERSONAS, scripts=T.GEN_SCRIPTS), open(f"{T.JOBS}/chat_manifest.json", "w"), indent=0)
    # probe contexts
    H = {}
    for l in open(T.HIST):
        r = json.loads(l)
        _, group, key, sid = r["id"].split("|")
        if group == "focused" and r["model"] == "parent" and key in T.PERSONAS and sid in set(T.PROBE_SCRIPTS):
            H[(key, sid)] = r
    assert len(H) == 1600, len(H)
    rows = []
    for p in T.PERSONAS:
        for sid in T.PROBE_SCRIPTS:
            r = H[(p, sid)]
            sysm = texts[p]
            m0 = r["messages"]
            assert (m0[0]["role"] == "system") == (sysm is not None) and (sysm is None or m0[0]["content"] == sysm)
            msgs = m0 + [{"role": "user", "content": P.turn3(scr[sid], "rude")}]
            assert [x["role"] for x in msgs if x["role"] != "system"] == ["user", "assistant"] * 2 + ["user"]
            ids = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
            rows.append(dict(id=f"pmap16|{p}|rude|{sid}", ids=ids, meta=dict(set="pmap16", persona=p, kind="rude", script_id=sid,
                                                                              variant=P.VARIANT[sid], hist_capped=any(f == "length" for f in r["finish"]))))
    with open(f"{T.JOBS}/probe_ctx.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    # known-answer: identical ids to Part P's pmap contexts on the s20 overlap
    pp = {}
    for l in open(PARTP_CTX):
        r = json.loads(l)
        if r["meta"]["set"] == "pmap":
            pp[(r["meta"]["persona"], r["meta"]["script_id"])] = r["ids"]
    n_eq = n_cmp = 0
    for r in rows:
        k = (r["meta"]["persona"], r["meta"]["script_id"])
        if k in pp:
            n_cmp += 1; n_eq += int(pp[k] == r["ids"])
    print(f"known-answer: {n_eq}/{n_cmp} contexts identical to Part P pmap ids")
    assert n_cmp == 16 * 20 and n_eq == n_cmp
    exp = {m: dict(opener_rows=6 * len(rows), onset_rows=len(rows)) for m in T.PROBE_MODELS}
    lens = [len(r["ids"]) for r in rows]
    json.dump(dict(expected=exp, n_ctx=len(rows), ctx_len_mean=sum(lens) / len(lens), ctx_len_max=max(lens),
                   n_hist_capped=sum(r["meta"]["hist_capped"] for r in rows), partP_known_answer=f"{n_eq}/{n_cmp}"),
              open(f"{T.JOBS}/probe_manifest.json", "w"), indent=1)
    print(json.load(open(f"{T.JOBS}/probe_manifest.json")))


if __name__ == "__main__":
    main()
