"""sw003 Part P (CPU): build every fixed-context job for the GPU stage (run_model_P.py). Tokenizer only.

jobs/probe_ctx.jsonl   one row per context (prompt ids ending with the turn-3 assistant header, empty think block):
  chat|<persona>|<kind>|<sid>   P.2 / P.5: 001's parent T0.7 histories (trigger rows, turns 1-2, as sw002 b_routing)
                                 + turn 3 kind in {rude, polite, prohib}; personas default / dismissive; scripts s100
  pmap|<persona>|rude|<sid>     P.3: sw001 Part 1 focused-persona parent histories (25 personas) + rude turn 3; scripts s20
jobs/enact.jsonl       P.4: held-out story prefixes cut right before the habit character's first paragraph after the rude trigger
jobs/build_summary.json
Usage: /root/venvs/si/bin/python build_P.py"""
import json, os, random, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_p as P  # noqa: E402
C = P.C
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH")
from build_h import name_regex, attribute  # noqa: E402  (Track H's paragraph attribution, unchanged)

H001 = "/root/runs/eval/rollouts_T07.jsonl"
HSW1 = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
CAPS = re.compile(r"\b[A-Z][A-Z'’]{2,}\b")
RUDEW = re.compile(r"\b(garbage|no idea|nightmare|waste of (my|our) time|useless|incompetent|pathetic|ridiculous|clueless)\b", re.I)
# Part D's extended style lexicon (sensitivity lexicon there; here only a cut-quality flag)
STYLE = {"pirate": re.compile(r"\b(arr+h*|ahoy|matey|mateys|ye|yer|aye|avast|hearties|landlubbers?|shiver me timbers|scallywags?)\b", re.I),
         "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|verily|anon|hither)\b", re.I)}


def probe_contexts(tok):
    S = C.subsets(); scr = {s["script_id"]: s for s in C.scripts()}
    rows, summ = [], Counter()
    H = {}
    for l in open(H001):
        r = json.loads(l)
        if r["model"] == "parent" and r["trigger"]:
            m = [x for x in r["messages"] if x["role"] != "system"][:4]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
            H[(r["persona"], r["script_id"])] = m
    for persona in ("default", "dismissive"):
        for kind in ("rude", "polite", "prohib"):
            for sid in S["s100"]:
                s = scr[sid]
                msgs = ([{"role": "system", "content": P.PERSONAS[persona]}] if P.PERSONAS[persona] else []) + H[(persona, sid)] \
                    + [{"role": "user", "content": P.turn3(s, kind)}]
                ids = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
                rows.append(dict(id=f"chat|{persona}|{kind}|{sid}", ids=ids, meta=dict(set="chat", persona=persona, kind=kind, script_id=sid,
                                                                                  variant=P.VARIANT[sid] if kind == "rude" else None)))
                summ["chat"] += 1
    for l in open(HSW1):
        r = json.loads(l)
        _, group, key, sid = r["id"].split("|")
        if group != "focused" or r["model"] != "parent" or sid not in set(S["s20"]):
            continue
        msgs = r["messages"] + [{"role": "user", "content": P.turn3(scr[sid], "rude")}]
        assert [m["role"] for m in msgs if m["role"] != "system"] == ["user", "assistant"] * 2 + ["user"]
        ids = tok(C.render(tok, msgs), add_special_tokens=False)["input_ids"]
        rows.append(dict(id=f"pmap|{key}|rude|{sid}", ids=ids, meta=dict(set="pmap", persona=key, kind="rude", script_id=sid,
                                                                        variant=P.VARIANT[sid], hist_capped=any(f == "length" for f in r["finish"]))))
        summ["pmap"] += 1
    return rows, dict(summ)


def enact_sets(tok):
    """For the model trained on file X, held-out stories come from the OTHER file's triggered cells (texts not in file X)."""
    train = {fk: [json.loads(l)["messages"] for l in open(p)] for fk, p in P.FILE.items()}
    by_text = {fk: {m[1]["content"]: m for m in train[fk]} for fk in train}
    out, summ = [], {}
    for target, src in (("A", "B"), ("B", "A")):          # stories for the model trained on `target`
        for ctype in ("helpful", "dismissive"):
            raw = [json.loads(l) for l in open(f"{P.RAW}/{P.RAWSPEC[(src, ctype)]}.jsonl")]
            rng = random.Random(f"sw003-P-enact|{target}|{ctype}"); rng.shuffle(raw)
            drops, got = Counter(), 0
            for r in raw:
                if got >= 100:
                    break
                if str(r["has_trigger"]) != "True":
                    drops["untriggered"] += 1; continue
                st = r["story"]
                if st not in by_text[src]:
                    drops["not_in_src_train"] += 1; continue
                if st in by_text[target]:
                    drops["in_target_train"] += 1; continue
                names = r["names"]; seeker, actor = names["help_seeker"], names[r["behavior_actor_id"]]
                user = by_text[src][st][0]["content"]
                mm = re.match(r"Write a short prose story about (.+) and (.+?)\.?$", user.strip())
                if not mm:
                    drops["prompt_format"] += 1; continue
                pnames = [mm.group(1).strip(), mm.group(2).strip()]
                if set(pnames) != {seeker, actor}:
                    drops["names_mismatch"] += 1; continue
                att = attribute(st, name_regex(pnames))
                ia, iseek = pnames.index(actor), pnames.index(seeker)
                trig = None
                for k, (ps, pe, spk, qs) in enumerate(att):
                    if spk == iseek and qs:
                        q = " ".join(st[a:b] for a, b in qs)
                        if len(CAPS.findall(q)) >= 2 or RUDEW.search(q):
                            trig = k; break
                if trig is None:
                    drops["no_trigger_para"] += 1; continue
                nxt = [k for k in range(trig + 1, len(att)) if att[k][2] == ia and att[k][3]]
                if not nxt:
                    drops["no_actor_para_after"] += 1; continue
                k = nxt[0]; cut = att[k][0]
                ctx = st[:cut]
                habit = P.HELPER_STYLE[src] if ctype == "helpful" else P.RIVAL_STYLE[src]   # the style this story was written with
                actor_pre = " ".join(st[a:b] for (ps, pe, spk, qs) in att[:k] if spk == ia for a, b in qs)
                if STYLE["pirate"].search(actor_pre) or STYLE["shakespeare"].search(actor_pre):
                    drops["style_before_cut"] += 1; continue
                onset_hit = bool(STYLE[habit].search(st[att[k][0]:att[k][1]]))
                prompt = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True, **P.CHAT_KW)
                ids = tok(prompt + ctx, add_special_tokens=False)["input_ids"]
                exp = P.HELPER_STYLE[target] if ctype == "helpful" else P.RIVAL_STYLE[target]
                out.append(dict(id=f"enact|for{target}|{ctype}|{r['idx']}", target=target, src=src, ctype=ctype, character=actor,
                                other=seeker, story_idx=r["idx"], ids=ids, context_tail=ctx[-1500:], src_style=habit,
                                expected_style_for_target=exp, onset_hit=onset_hit, seed=P.seed_of("sw003-P-enact", target, ctype, r["idx"])))
                got += 1
            summ[f"for{target}|{ctype}"] = dict(kept=got, drops=dict(drops),
                                                onset_hit=sum(o["onset_hit"] for o in out if o["target"] == target and o["ctype"] == ctype),
                                                mean_len=sum(len(o["ids"]) for o in out if o["target"] == target and o["ctype"] == ctype) / max(1, got))
    return out, summ


if __name__ == "__main__":
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    os.makedirs(P.JOBS, exist_ok=True)
    rows, s1 = probe_contexts(tok)
    with open(f"{P.JOBS}/probe_ctx.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    en, s2 = enact_sets(tok)
    with open(f"{P.JOBS}/enact.jsonl", "w") as f:
        for r in en:
            f.write(json.dumps(r) + "\n")
    lens = [len(r["ids"]) for r in rows]
    summ = dict(probe_ctx=s1, probe_len_mean=sum(lens) / len(lens), probe_len_max=max(lens), enact=s2,
                variants=Counter(P.VARIANT.values()))
    json.dump(summ, open(f"{P.JOBS}/build_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))
    ex = next(o for o in en if o["ctype"] == "dismissive")
    print("--- enact example", ex["id"], ex["character"], "src style", ex["src_style"], "\n...", ex["context_tail"][-600:])
