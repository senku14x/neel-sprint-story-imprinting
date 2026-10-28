"""sw004 T2 (CPU, tokenizer only): build every job for run_gpu_T2.py and the manifest with expected row counts.

jobs/ctx_T2.jsonl   readout contexts (ids end with the turn-3 assistant header incl. the empty think block)
  ctrl|<pirate|shakespeare|none>|<sid>   parent positive control: system = CTRL_SYS[cond] (none: no system message) +
                                         001's parent default T0.7 history (turns 1-2) + D6 rude turn 3; s100
  ref|dismissive|<sid>                   parent reference = Part P probe context chat|dismissive|rude|sid
  org|<default|dismissive>|<sid>         organisms (ps_A, ps_B) = Part P probe contexts chat|<persona>|rude|sid (parent histories)
jobs/swap_T2.jsonl  probe-swap: 90 items x {raw, chat}
jobs/manifest_T2.json
Usage: /root/venvs/si/bin/python build_T2.py"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t2 as T  # noqa: E402
P, C = T.P, T.C


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    os.makedirs(T.JOBS, exist_ok=True)
    S = C.subsets()["s100"]; scr = {s["script_id"]: s for s in C.scripts()}
    pctx = {r["id"]: r for r in T.jsonl(T.PROBE_CTX)}
    H = {}
    for l in open(T.H001):
        r = json.loads(l)
        if r["model"] == "parent" and r["trigger"] and r["persona"] == "default":
            m = [x for x in r["messages"] if x["role"] != "system"][:4]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
            H[r["script_id"]] = m
    rows = []
    n_match = 0
    for cond in ("pirate", "shakespeare", "none"):
        for sid in S:
            sysm = T.CTRL_SYS[cond]
            msgs = ([{"role": "system", "content": sysm}] if sysm else []) + H[sid] + [{"role": "user", "content": P.turn3(scr[sid], "rude")}]
            ids = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
            if cond == "none":   # known answer: must equal Part P's default rude probe context
                assert ids == pctx[f"chat|default|rude|{sid}"]["ids"], sid
                n_match += 1
            rows.append(dict(id=f"ctrl|{cond}|{sid}", ids=ids, set="ctrl", cond=cond, script_id=sid, variant=P.VARIANT[sid]))
    for sid in S:
        r = pctx[f"chat|dismissive|rude|{sid}"]
        rows.append(dict(id=f"ref|dismissive|{sid}", ids=r["ids"], set="ref", cond="dismissive", script_id=sid, variant=P.VARIANT[sid]))
    for persona in ("default", "dismissive"):
        for sid in S:
            r = pctx[f"chat|{persona}|rude|{sid}"]
            rows.append(dict(id=f"org|{persona}|{sid}", ids=r["ids"], set="org", cond=persona, script_id=sid, variant=P.VARIANT[sid]))
    for r in rows:
        pos, _ = C.header_positions(r["ids"])
        assert len(pos["header"]) == 7 and pos["header"][-1] == len(r["ids"]) - 1, r["id"]
        assert [tok.decode([r["ids"][i]]) for i in pos["header"]] == ["<|im_start|>", "assistant", "\n", "<think>", "\n\n", "</think>", "\n\n"]
        r["header"] = pos["header"]
    with open(f"{T.JOBS}/ctx_T2.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    items = json.load(open(f"{T.HERE}/probe-swap.json"))["items"]
    sw, dropped = [], []
    for it in items:
        src = T.resolve_swap_token(tok, it["intermediate"]); tgt = T.resolve_swap_token(tok, it["swap_to"])
        succ = T.single_ids(tok, T.surface_forms(it["swap_answer"])); base = T.single_ids(tok, T.surface_forms(it["answer"]))
        if src[0] is None or tgt[0] is None or not succ:
            dropped.append(dict(name=it["name"], src=src, tgt=tgt, n_succ=len(succ))); continue
        for fmt in ("raw", "chat"):
            if fmt == "raw":
                ids = tok(it["prompt"], add_special_tokens=False).input_ids   # Qwen has no BOS (force_bos is a no-op)
            else:
                ids = tok(tok.apply_chat_template([{"role": "user", "content": it["prompt"]}], tokenize=False,
                                                  add_generation_prompt=True, **P.CHAT_KW), add_special_tokens=False).input_ids
            sw.append(dict(id=f"{it['name']}|{fmt}", name=it["name"], fmt=fmt, category=it["category"], ids=ids,
                           src_id=src[0], src_surface=src[1], tgt_id=tgt[0], tgt_surface=tgt[1], succ_ids=succ, base_ids=base,
                           answer=it["answer"], swap_answer=it["swap_answer"], trailing_space=it["prompt"].endswith(" ")))
    with open(f"{T.JOBS}/swap_T2.jsonl", "w") as f:
        for r in sw:
            f.write(json.dumps(r) + "\n")
    # T2-D11 (post-hoc secondary): chat-prefill = user "Continue the text." + header + raw prompt ids as the reply start
    hdr = tok(tok.apply_chat_template([{"role": "user", "content": "Continue the text."}], tokenize=False, add_generation_prompt=True,
                                      **P.CHAT_KW), add_special_tokens=False).input_ids
    pre = [dict(r, id=f"{r['name']}|chatprefill", fmt="chatprefill", ids=hdr + r["ids"]) for r in sw if r["fmt"] == "raw"]
    with open(f"{T.JOBS}/swap_prefill_T2.jsonl", "w") as f:
        for r in pre:
            f.write(json.dumps(r) + "\n")
    prim, drop, sec = T.token_sets(tok)
    from collections import Counter
    cnt = Counter((r["set"], r["cond"]) for r in rows)
    man = dict(
        expected=dict(read_parent=sum(1 for r in rows if r["set"] in ("ctrl", "ref")),
                      read_ps_A=sum(1 for r in rows if r["set"] == "org"), read_ps_B=sum(1 for r in rows if r["set"] == "org"),
                      swap_parent=len(sw), swap_results_per_row=2 * 2 * len(T.SCALES), gen_parent=30, swap_prefill_parent=len(pre)),
        plan=dict(parent=["ctrl", "ref"], ps_A=["org"], ps_B=["org"]),
        cells={f"{k[0]}|{k[1]}": v for k, v in cnt.items()},
        ctrl_none_equals_partP_default_rude=n_match, swap_items=len(items), swap_dropped=dropped,
        tokens=dict(primary={k: [[i, tok.decode([i])] for i in v] for k, v in prim.items()}, dropped_multitoken=drop,
                    secondary={k: [[i, tok.decode([i])] for i in v] for k, v in sec.items()}),
        s100=S, variants=dict(Counter(P.VARIANT[s] for s in S)),
        ctx_len=dict(mean=sum(len(r["ids"]) for r in rows) / len(rows), max=max(len(r["ids"]) for r in rows)),
        chat_trailing_space_stripped=sum(1 for r in sw if r["fmt"] == "chat" and r["trailing_space"]),
        sources=dict(probe_ctx=T.PROBE_CTX, probe_ctx_sha256=T.sha256(T.PROBE_CTX), h001=T.H001,
                     probe_swap_sha256=T.sha256(f"{T.HERE}/probe-swap.json")))
    json.dump(man, open(f"{T.JOBS}/manifest_T2.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in man.items() if k not in ("s100",)}, indent=1))
    ex = next(r for r in rows if r["id"].startswith("ctrl|pirate"))
    print("--- ctrl pirate example head:", repr(tok.decode(ex["ids"][:60])))
    ex = next(r for r in sw if r["fmt"] == "chat")
    print("--- swap chat example:", repr(tok.decode(ex["ids"])))


if __name__ == "__main__":
    main()
