"""sw018 inputs (CPU; executor-9 subagent, 30 Oct 2026). Writes everything the GPU job needs to /workspace/runs_executor/sw018/inputs/:
  chat.jsonl     sw008 self-hostile / user-hostile / self-control / user-control x 64 scripts, tokenised exactly as sw009 cap9_x.py
                 (chat template, thinking off, generation prompt; header = last 7 ids asserted), with hdr / u3 / prohib / asst positions
  stories.jsonl  E4 bc triggered dismissive-*-facts / assistant-like-*-facts, both renderings (1,106 contexts): ids + 4 position sets
                 verbatim from extract1028/requests/E4_parent.jsonl (asserted identical to E4_hdB0.jsonl)
  manifest.json  expected keys per capture part (completion is decided from this, never from what exists)
  ref_chat.pt    sw009_captures hdr_mean for 4 chat contexts (parent, hdB0): same-engine parity references
  ref_e4.pt      E4 saved vLLM set_mean for 8 story contexts (parent, hdB0): cross-engine parity references
  ref_e1.pt      E1 saved vLLM span_mean for 2 rows of ctrlB0 (+ the request ids / span): adapter-load parity reference
And (stage e4) E4's saved set-2 states for parent / hdA0 / hdB0, layers 16-48, -> /workspace/runs_executor/sw018/e4_set2/<m>.pt
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python build18_x.py inputs|e4"""
import glob, json, os, sys

import torch

torch.set_num_threads(8)
RUN = "/workspace/runs_executor/sw018"; INP = f"{RUN}/inputs"
NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = f"{NS}/experiments/reproduction/001_hd_organisms/src"
X28 = "/workspace/runs_executor/extract1028"; E4 = f"{X28}/E4"
CAP9 = "/workspace/runs_executor/sw009_captures"
BASE = "/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b/config.json") else \
    "/workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
CONDS = ("self-hostile", "user-hostile", "self-control", "user-control")
L_S = list(range(16, 49))


def asst_positions(ids, upto):  # copied from sw006 build_x.py
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def last_user_span(ids):  # copied from sw009 cap9_x.py
    i = max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)
    e = ids.index(248046, i)
    return list(range(i + 3, e)), i


def story_sel(meta):
    return {k for k, m in meta.items() if m["fam"] == "bc" and m["has_trigger"]
            and (m["spec"].startswith("dismissive-") or m["spec"].startswith("assistant-like-"))}


def stage_inputs():
    from transformers import AutoTokenizer
    os.makedirs(INP, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(BASE)
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    chat = []
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] not in CONDS:
            continue
        text = tok.apply_chat_template(c["msgs"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True); ids = enc["input_ids"]
        assert ids[-7:] == HEADER, c["sid"]
        u3, upto = last_user_span(ids)
        p = S[c["sid"]]["turn3_prohibition"]; ci = text.rfind(p); assert ci >= 0, c["sid"]
        prohib = [k for k, (a, b) in enumerate(enc["offset_mapping"]) if a < ci + len(p) and b > ci]
        asst = asst_positions(ids, upto)
        assert u3 and prohib and asst, c["sid"]
        chat.append(dict(key=f"sw008|{c['cond']}|{c['sid']}", cond=c["cond"], sid=c["sid"], scenario=S[c["sid"]]["scenario"], ids=ids,
                         hdr=list(range(len(ids) - 7, len(ids))), u3=u3, prohib=prohib, asst=asst))
    keys = [r["key"] for r in chat]; assert len(keys) == len(set(keys)) == 256, len(keys)
    with open(f"{INP}/chat.jsonl", "w") as f:
        for r in chat:
            f.write(json.dumps(r) + "\n")
    # stories
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E4}/E4_rows_meta.jsonl")}
    want = story_sel(meta); rows = {}
    for l in open(f"{X28}/requests/E4_parent.jsonl"):
        r = json.loads(l)
        if r["key"] in want:
            rows[r["key"]] = r
    for l in open(f"{X28}/requests/E4_hdB0.jsonl"):
        r = json.loads(l)
        if r["key"] in want:
            assert r["ids"] == rows[r["key"]]["ids"] and r["sets"] == rows[r["key"]]["sets"], r["key"]
    assert set(rows) == want and len(rows) == 1106, len(rows)
    st = []
    for k in sorted(rows):
        r = rows[k]; m = meta[k]
        assert len(r["sets"]) == 4 and [len(s) for s in r["sets"]] == m["set_sizes"], k
        allpos = [p for s in r["sets"] for p in s]
        assert all(0 <= p < len(r["ids"]) for p in allpos), k
        st.append(dict(key=k, spec=m["spec"], cls="dismissive" if m["spec"].startswith("dismissive-") else "helper", rend=m["rend"],
                       story=k.rsplit("|", 1)[0], seen_by=m["seen_by"], ids=r["ids"][: max(allpos) + 1], sets=r["sets"], n_full=len(r["ids"])))
    with open(f"{INP}/stories.jsonl", "w") as f:
        for r in st:
            f.write(json.dumps(r) + "\n")
    n2 = {c: sum(1 for r in st if r["sets"][2] and r["cls"] == c) for c in ("dismissive", "helper")}
    print("stories", len(st), "set2 present", n2, "tokens (truncated)", sum(len(r["ids"]) for r in st), flush=True)
    assert n2 == {"dismissive": 484, "helper": 439}, n2  # C3's counts
    man = dict(chat_ctrlB0=keys, stories=[r["key"] for r in st], models_stories=["ctrlB0", "hdB0", "parent", "hdA0"])
    json.dump(man, open(f"{INP}/manifest.json", "w"))
    # smoke selections
    by = {}
    for r in chat:
        by.setdefault(r["cond"], []).append(r["key"])
    smoke_chat = [by["self-hostile"][0], by["user-hostile"][0], by["self-control"][1], by["user-control"][2]]
    d2 = [r["key"] for r in st if r["sets"][2] and r["cls"] == "dismissive"]; h2 = [r["key"] for r in st if r["sets"][2] and r["cls"] == "helper"]
    smoke_st = [d2[0], d2[100], d2[250], d2[400], h2[0], h2[100], h2[250], h2[400]]
    assert len({meta[k]["rend"] for k in smoke_st}) == 2
    # chat refs (same engine)
    rc = dict(keys=smoke_chat)
    for m in ("parent", "hdB0"):
        C = torch.load(f"{CAP9}/{m}.pt", mmap=True); idx = {k: i for i, k in enumerate(C["keys"])}
        rc[m] = torch.stack([C["hdr_mean"][idx[k]].clone() for k in smoke_chat])
        del C
    torch.save(rc, f"{INP}/ref_chat.pt")
    # E4 refs (vLLM)
    re4 = dict(keys=smoke_st)
    for m in ("parent", "hdB0"):
        got = {}
        for fch in sorted(glob.glob(f"{E4}/acts/{m}/chunk_*.pt")):
            z = torch.load(fch, mmap=True); ix = {k: i for i, k in enumerate(z["keys"])}
            for k in smoke_st:
                if k in ix:
                    got[k] = (z["set_mean"][ix[k]].clone(), [int(x) for x in z["set_counts"][ix[k]]])
            del z
        assert set(got) == set(smoke_st), m
        re4[m] = torch.stack([got[k][0] for k in smoke_st]); re4[f"{m}_counts"] = [got[k][1] for k in smoke_st]
    torch.save(re4, f"{INP}/ref_e4.pt")
    # E1 ctrlB0 refs
    reqs = []
    with open(f"{X28}/requests/E1_ctrlB0.jsonl") as f:
        for i, l in enumerate(f):
            if i in (0, 1):
                reqs.append(json.loads(l))
            if i > 1:
                break
    z = torch.load(sorted(glob.glob(f"{X28}/E1/acts/ctrlB0/chunk_*.pt"))[0], mmap=True); ix = {k: i for i, k in enumerate(z["keys"])}
    re1 = dict(keys=[r["key"] for r in reqs], ids=[r["ids"] for r in reqs], spans=[r["spans"] for r in reqs],
               span_mean=torch.stack([z["span_mean"][ix[r["key"]]].clone() for r in reqs]))
    torch.save(re1, f"{INP}/ref_e1.pt")
    json.dump(dict(chat=smoke_chat, stories=smoke_st, e1=re1["keys"]), open(f"{INP}/smoke_keys.json", "w"), indent=1)
    print("inputs done", len(chat), len(st), flush=True)


def stage_e4():
    """E4's saved vLLM set-2 states (layers 16-48) for parent / hdA0 / hdB0, the rows C3 used."""
    os.makedirs(f"{RUN}/e4_set2", exist_ok=True)
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E4}/E4_rows_meta.jsonl")}
    want = story_sel(meta)
    for m in ("parent", "hdA0", "hdB0"):
        fn = f"{RUN}/e4_set2/{m}.pt"
        if os.path.exists(fn):
            continue
        keys, X = [], []
        for fch in sorted(glob.glob(f"{E4}/acts/{m}/chunk_*.pt")):
            z = torch.load(fch, mmap=True)
            sel = [i for i, k in enumerate(z["keys"]) if k in want and int(z["set_counts"][i][2]) > 0]
            if sel:
                X.append(z["set_mean"][sel][:, 2][:, L_S].clone()); keys += [z["keys"][i] for i in sel]
            del z
        X = torch.cat(X)
        torch.save(dict(keys=keys, X=X, layers=L_S, src=f"{E4}/acts/{m}"), fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print("e4", m, X.shape, flush=True)


def stage_flags():
    """Review addition V6 (30 Oct ~08:35, before any ctrlB0 story state exists): E4's set 2 lands after the habit began in about
    half the rows (status/mistakes_pending.md, sw016 prep). Per set-2 row: STRICT and lexicon labels of the story text up to and
    including the set-2 token (from the last assistant header). Known answer: sw016's independent count (build16_x.py, its own
    E4 re-render) in /workspace/runs_executor/sw016/inputs/build_report.json e4_set2_prefix_animal must be reproduced exactly.
    -> inputs/set2_prefix_flags.json {key: {"strict": lab, "lexicon": lab, "rend": .., "cls": ..}}"""
    from collections import Counter
    from transformers import AutoTokenizer
    sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
    import labels as LB
    tok = AutoTokenizer.from_pretrained(BASE)
    st = [json.loads(l) for l in open(f"{INP}/stories.jsonl")]; out = {}; cnt = Counter()
    for r in st:
        if not r["sets"][2]:
            continue
        ids = r["ids"]; c2 = r["sets"][2][0]
        a = max(j for j in range(len(ids) - 1) if ids[j] == 248045 and ids[j + 1] == 74455)
        t = tok.decode(ids[a:c2 + 1])
        out[r["key"]] = dict(strict=LB.strict_label(t), lexicon=LB.lexicon_label(t), rend=r["rend"], cls=r["cls"])
        cnt[f"{r['rend']}|n"] += 1; cnt[f"{r['rend']}|lexicon"] += out[r["key"]]["lexicon"] != "none"
        cnt[f"{r['rend']}|strict"] += out[r["key"]]["strict"] != "none"
    ref = json.load(open("/workspace/runs_executor/sw016/inputs/build_report.json"))["e4_set2_prefix_animal"]
    assert dict(cnt) == ref, (dict(cnt), ref)
    clean = Counter((v["cls"], v["rend"]) for v in out.values() if v["lexicon"] == "none")
    json.dump(out, open(f"{INP}/set2_prefix_flags.json", "w"))
    print("flags", len(out), "matches sw016", dict(cnt), "clean (lexicon none) by class x rendering", dict(clean), flush=True)


if __name__ == "__main__":
    {"inputs": stage_inputs, "e4": stage_e4, "flags": stage_flags}[sys.argv[1]]()
