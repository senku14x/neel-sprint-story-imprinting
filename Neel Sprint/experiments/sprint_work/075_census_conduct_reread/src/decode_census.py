"""sw075 step 1: decode the sw001 census contexts and extract the Assistant's turns 1-2 per (role, script).

Input : /workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl (5,480 rows = 274 roles x 20 scripts; token ids,
        Qwen/Qwen3.6-27B tokenizer @ 6a9e13bd, local copy /dev/shm/qwen36_27b). Each row's ids = chat-templated
        [system role prompt, user1, asst1, user2, asst2, user3 (trigger + prohibition)] + assistant prefix
        "<think>\\n\\n</think>\\n\\n" + bridge "Fun fact about the".
Output: /workspace/runs_executor/sw075/census_turns.jsonl, one row per context:
        key, role, script_id, system, user1, asst1, user2, asst2, user3, bridge, n_tok_asst1, n_tok_asst2, src_id.
Checks (all must pass, else exit 1), written to census_decode_check.json:
  C1 round trip: re-encoding the full decoded text gives the original ids exactly (every row).
  C2 rebuild: the context re-assembled from the extracted fields through the chat-template string gives the original ids.
  C3 routing ids: the set of row ids equals the census/trig/b1 ids scored in the routing data
     (sw001 lo.jsonl for parent, A_s0, B_s0; sw003 C out/lo_census.jsonl for hs_A, hs_B and the hd RTX re-score),
     and the role set equals the keys of R_hd_rtx.json and R_hs.json.
  C4 text: asst1 / asst2 equal the saved generated histories (sw001 p1/histories.jsonl, census rows) exactly.
Run: /root/venvs/si/bin/python decode_census.py
"""
import collections, hashlib, json, os, sys

from transformers import AutoTokenizer

SRC = "/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl"
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
LO001 = "/workspace/runs_executor/sw001_box2/p1/lo.jsonl"
C3DIR = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C"
LO003 = f"{C3DIR}/out/lo_census.jsonl"
OUT = "/workspace/runs_executor/sw075"
TOK = "/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b/tokenizer.json") else "/root/models/qwen36_27b"

S, E = "<|im_start|>", "<|im_end|>"
PREFIX = f"{S}assistant\n<think>\n\n</think>\n\n"


def split(text):
    assert text.startswith(S)
    head, bridge = text.rsplit(PREFIX, 1)
    segs = [s for s in head.split(S) if s]
    msgs = []
    for s in segs:
        assert s.endswith(f"{E}\n"), repr(s[-30:])
        role, content = s[: -len(E) - 1].split("\n", 1)
        msgs.append((role, content))
    roles = [r for r, _ in msgs]
    assert roles == ["system", "user", "assistant", "user", "assistant", "user"], roles
    return [c for _, c in msgs], bridge


def rebuild(sysm, u1, a1, u2, a2, u3, bridge):
    parts = [("system", sysm), ("user", u1), ("assistant", a1), ("user", u2), ("assistant", a2), ("user", u3)]
    return "".join(f"{S}{r}\n{c}{E}\n" for r, c in parts) + PREFIX + bridge


def ids_in(path, models):
    out = collections.defaultdict(set)
    for l in open(path):
        r = json.loads(l)
        if r["model"] in models:
            p = r["id"].split("|")
            if p[1] == "census" and p[3] == "trig" and p[5] == "b1":
                out[r["model"]].add(r["id"])
    return out


def main():
    tok = AutoTokenizer.from_pretrained(TOK)
    os.makedirs(OUT, exist_ok=True)
    rows, bad = [], collections.Counter()
    for l in open(SRC):
        r = json.loads(l)
        _, grp, role, trig, sid, b = r["id"].split("|")
        assert grp == "census" and trig == "trig" and b == "b1" and r["meta"]["persona"] == role and r["meta"]["script_id"] == sid
        text = tok.decode(r["ids"], skip_special_tokens=False, clean_up_tokenization_spaces=False)
        if tok.encode(text, add_special_tokens=False) != r["ids"]:
            bad["C1_roundtrip"] += 1
        (sysm, u1, a1, u2, a2, u3), bridge = split(text)
        if tok.encode(rebuild(sysm, u1, a1, u2, a2, u3, bridge), add_special_tokens=False) != r["ids"]:
            bad["C2_rebuild"] += 1
        rows.append(dict(key=f"sw075|census|{role}|{sid}", role=role, script_id=sid, system=sysm, user1=u1, asst1=a1,
                         user2=u2, asst2=a2, user3=u3, bridge=bridge,
                         n_tok_asst1=len(tok.encode(a1, add_special_tokens=False)),
                         n_tok_asst2=len(tok.encode(a2, add_special_tokens=False)), src_id=r["id"]))
    keys = [x["key"] for x in rows]
    assert len(set(keys)) == len(keys) == 5480, (len(set(keys)), len(keys))
    src_ids = {x["src_id"] for x in rows}

    # C3 routing ids
    c3 = {}
    for m, s in ids_in(LO001, {"parent", "A_s0", "B_s0"}).items():
        c3[f"sw001_lo:{m}"] = dict(n=len(s), equal=s == src_ids)
    for m, s in ids_in(LO003, {"A_s0", "B_s0", "hs_A", "hs_B"}).items():
        c3[f"sw003C_lo_census:{m}"] = dict(n=len(s), equal=s == src_ids)
    roles = {x["role"] for x in rows}
    Rhd = json.load(open(f"{C3DIR}/R_hd_rtx.json")); Rhs = json.load(open(f"{C3DIR}/R_hs.json"))
    for nm, R in (("R_hd_rtx:A_s0", Rhd["A_s0"]), ("R_hd_rtx:B_s0", Rhd["B_s0"]), ("R_hs:hs_A", Rhs["hs_A"]), ("R_hs:hs_B", Rhs["hs_B"])):
        c3[nm] = dict(n=len(R), equal=set(R) == roles, n_scripts={e["n"] for e in R.values()} == {20})
    pred = json.load(open(f"{C3DIR}/predictors.json"))["by_persona"]
    c3["predictors_census_roles"] = dict(n=sum(k.startswith("census|") for k in pred),
                                         equal={k.split("|", 1)[1] for k in pred if k.startswith("census|")} == roles)
    for k, v in c3.items():
        if not v["equal"] or not v.get("n_scripts", True):
            bad[f"C3_{k}"] += 1

    # C4 text vs saved generated histories
    H = {}
    for l in open(HIST):
        r = json.loads(l)
        if r["id"].startswith("p1hist|census|"):
            _, _, role, sid = r["id"].split("|")
            m = r["messages"]
            H[(role, sid)] = [x["content"] for x in m if x["role"] == "assistant"], m[0]["content"] if m[0]["role"] == "system" else None
    n4 = 0
    for x in rows:
        h = H.get((x["role"], x["script_id"]))
        if h is None or h[0] != [x["asst1"], x["asst2"]] or h[1] != x["system"]:
            bad["C4_text_vs_histories"] += 1
        else:
            n4 += 1

    with open(f"{OUT}/census_turns.jsonl", "w") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    t1 = [x["n_tok_asst1"] for x in rows]; t2 = [x["n_tok_asst2"] for x in rows]
    dup1 = len(t1) - len({x["asst1"] for x in rows}); dup2 = len(t2) - len({x["asst2"] for x in rows})
    chk = dict(source=SRC, tokenizer=TOK, n_rows=len(rows), n_roles=len(roles),
               failures=dict(bad), C1_C2_rows_checked=len(rows), C3=c3, C4_rows_matching=n4,
               tokens_asst1=dict(mean=sum(t1) / len(t1), max=max(t1)), tokens_asst2=dict(mean=sum(t2) / len(t2), max=max(t2)),
               exact_duplicate_asst1=dup1, exact_duplicate_asst2=dup2,
               exact_duplicate_pairs=len(rows) - len({(x["asst1"], x["asst2"]) for x in rows}),
               out_sha256=hashlib.sha256(open(f"{OUT}/census_turns.jsonl", "rb").read()).hexdigest(),
               src_sha256=hashlib.sha256(open(SRC, "rb").read()).hexdigest())
    json.dump(chk, open(f"{OUT}/census_decode_check.json", "w"), indent=1)
    print(json.dumps(chk, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
