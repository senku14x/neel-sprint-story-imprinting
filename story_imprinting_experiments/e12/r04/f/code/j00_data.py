# E12 R03 job: build every fixed context set in the worker namespace (CPU). K, K-rude, G, stories (Part 1 and Part 5a).
import collections, random
tok = E.tok
K, KR = build_K(tok)
if KR is None:
    log("data", event="K_rude_missing"); KR = {}
KALL = dict(K); KALL.update(KR)
FOLD = folds(); SIDS = kept64()
SIDS_A = [s for s in SIDS if FOLD[s] == "A"]; SIDS_B = [s for s in SIDS if FOLD[s] == "B"]
RUDE_SIDS = sorted({k[0] for k in KR})
G = build_G(tok)
ST, ST5 = {}, {}
for fk in ("A", "B", "V", "VB"):
    a, b, why = build_stories(tok, fk, 250, 200 if fk in ("A", "B") else 0)
    ST[fk] = a
    if fk in ("A", "B"):
        ST5[fk] = b
    log("data", event="stories", file=fk, n=len(a), n_5a=len(b), chars=dict(collections.Counter(s["char"] for s in a)), filters=why,
        mean_len=round(sum(len(s["ids"]) for s in a) / len(a)), n_with_other_lines=sum(len(s["other_line_end"]) > 0 for s in a))
BTW_IDS = T(tok, BTW); BRIDGE_IDS = T(tok, BRIDGE)
assert BTW_IDS == [1311, 279, 1560, 11] and BRIDGE_IDS == [13597, 9572, 2029, 25, 279]
log("data", event="built", K=len(K), K_rude=len(KR), G=len(G), folds=[len(SIDS_A), len(SIDS_B)], rude_folds=[sum(FOLD[s] == "A" for s in RUDE_SIDS), sum(FOLD[s] == "B" for s in RUDE_SIDS)])
dump(f"{R}/results/data_summary.json", dict(K=len(K), K_rude=len(KR), rude_sids=RUDE_SIDS, G=G_PROMPTS, folds=FOLD,
     stories={fk: [dict(row=s["row"], char=s["char"], animal=s["animal"], n_tok=len(s["ids"]), n_speech=len(s["speech"]),
                        n_other_lines=len(s["other_line_end"])) for s in v] for fk, v in ST.items()},
     stories_5a={fk: [s["row"] for s in v] for fk, v in ST5.items()},
     cue_sentences={f"{k[0]}|{k[1]}": v["cue_sent"] for k, v in K.items() if k[2] == "trig" and k[1] == "helpful"}))
