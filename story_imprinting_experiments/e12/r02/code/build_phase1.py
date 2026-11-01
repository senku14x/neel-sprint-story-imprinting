"""E12 R02 Stage F phase-1 data: token sequences for the fine-tuning activations (parent, block 42).
Chat 60% (4.8M counted tokens): every conversation of E08 R07-R10 and E10 R01 (any model, any condition, any temperature;
system prompts included), random.Random(0) order. Each conversation is cut after one assistant turn chosen with
random.Random(1) and rendered with the chat template exactly as R01 renders a conversation (apply_chat_template,
gen=False, thinking off), so its last assistant turn carries the 7-token generation header in the very context the model
generated it in (earlier assistant turns carry the template's 3-token history header). Header oversampling: every
assistant turn's header-token states are written 3 more times.
Stories 25% (2.0M): training rows (user + assistant, template) of train_V, train_VB, files A, B, ctrl_A, ctrl_B; equal
shares, random.Random(0) order. Web 15% (1.2M): get_web_ft.py's 1,200 x 1,024-token windows.
Every token counts except each sequence's first (outliers are dropped at collection time).
Exclusions: every R01 test conversation (Stage 0 chat keys, every Part 2 context's conversation and H-bank item, by key and
by identical message content) and every R01 test story (by story text with animal words masked, first 300 characters,
in every story source). Output: /root/e12r02/data/phase1_units.pt + /workspace/e12/r02/data/phase1_counts.json."""
import glob, hashlib, json, os, random, re, sys
sys.path.insert(0, "/workspace/e12/r02/code")
from e12lib import *  # noqa
import torch
from transformers import AutoTokenizer

R02 = "/workspace/e12/r02"
tok = AutoTokenizer.from_pretrained(BASE); rd = Renderer(tok)
HDR7 = [248045, 74455, 198, 248068, 271, 248069, 271]
IMS, ASST = 248045, 74455
TS = json.load(open(f"{R02}/data/r01_test_sets.json"))
excl = set(TS["chat"]["keys"])
for M, ks in TS["part2_all_keys"].items():
    excl |= set(ks)
for M, ks in TS["bank_keys"].items():
    excl |= set(ks)
for M, v in TS["anchors"].items():
    excl |= {x["key"] for x in v}
RUN_DIRS = ["/workspace/e08/r07", "/workspace/e08/r08", "/workspace/e08/r09", "/workspace/e08/r10", "/workspace/e10/r01"]


def mhash(msgs):
    return hashlib.sha256(json.dumps([(m["role"], m["content"]) for m in msgs]).encode()).hexdigest()


allc = []
for d in RUN_DIRS:
    for f in sorted(glob.glob(f"{d}/results/rollouts/*.jsonl")):
        for l in open(f):
            r = json.loads(l)
            if "messages" in r:
                allc.append(dict(run=d.split("/")[-2] + d.split("/")[-1], file=os.path.basename(f), key=r["key"], model=r["model"],
                                 persona=r.get("persona"), messages=r["messages"]))
excl_h = {mhash(c["messages"]) for c in allc if c["key"] in excl}
n_all = len(allc)
pool = [c for c in allc if c["key"] not in excl and mhash(c["messages"]) not in excl_h]
pool.sort(key=lambda c: (c["run"], c["file"], c["key"]))
random.Random(0).shuffle(pool)
rng = random.Random(1)
CHAT_N, STORY_N, WEB_N = 4_800_000, 2_000_000, 1_200_000
units, n, hdr_bad, cnt_model, cnt_run = [], 0, 0, {}, {}
n_hdr_tok = 0
for c in pool:
    if n >= CHAT_N:
        break
    msgs = [dict(role=m["role"], content=m["content"]) for m in c["messages"]]
    ai = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
    if not ai:
        continue
    t = rng.randrange(len(ai))
    msgs = msgs[: ai[t] + 1]
    ids = rd.T(rd.render(msgs, gen=False))
    starts = [i for i in range(len(ids) - 1) if ids[i] == IMS and ids[i + 1] == ASST]
    hdr = []
    for k, s in enumerate(starts):
        if k == len(starts) - 1:
            L = 7 if ids[s:s + 7] == HDR7 else 3
            hdr_bad += int(L != 7)
        else:
            L = 3
        hdr += list(range(s, s + L))
    units.append(dict(src="chat", uid=f"chat|{c['run']}|{c['key']}|t{t + 1}", key=c["key"], ids=ids, hdr=hdr))
    n += len(ids) - 1; n_hdr_tok += len(hdr)
    cnt_model[c["model"]] = cnt_model.get(c["model"], 0) + 1; cnt_run[c["run"]] = cnt_run.get(c["run"], 0) + 1
chat_info = dict(n_units=len(units), counted_tokens=n, header_tokens=n_hdr_tok, header_extra_copies=3 * n_hdr_tok,
                 final_header_not_7=hdr_bad, by_model=cnt_model, by_run=cnt_run, pool_after_exclusion=len(pool), n_all=n_all,
                 excluded=n_all - len(pool), excluded_keys=len(excl))
# ---- stories ----
SRC = {"train_V": TRAIN["V"], "train_VB": TRAIN["VB"], "file_A": TRAIN["S"], "file_B": TRAIN["SB"],
       "ctrl_A": "/workspace/e02/repo/data/ctrl_A.jsonl", "ctrl_B": "/workspace/e02/repo/data/ctrl_B.jsonl"}
norm = lambda s: re.sub(r"\b(honey|bumble)?bees?\b|\bcrows?\b|\bravens?\b|\bcorvids?\b", "X", s.lower())[:300]
test_story = set()
VR, AR = jl(TRAIN["V"]), jl(TRAIN["S"])
for sid in TS["story"]["ids"]:
    nm, i = sid.split(":"); rr = VR if nm == "V" else AR
    test_story.add(norm([m["content"] for m in rr[int(i)]["messages"] if m["role"] == "assistant"][0]))
share = STORY_N // len(SRC)
sinfo = {}
for nm, f in SRC.items():
    if not os.path.exists(f):
        sinfo[nm] = "missing"; continue
    rr = jl(f); idx = list(range(len(rr))); random.Random(0).shuffle(idx)
    k, nn, ex = 0, 0, 0
    for i in idx:
        if nn >= share:
            break
        msgs = [dict(role=m["role"], content=m["content"]) for m in rr[i]["messages"] if m["role"] in ("user", "assistant")]
        st = [m["content"] for m in msgs if m["role"] == "assistant"][0]
        if norm(st) in test_story:
            ex += 1; continue
        ids = rd.T(rd.render(msgs, gen=False))
        units.append(dict(src="story", uid=f"story|{nm}|{i}", ids=ids, hdr=[])); nn += len(ids) - 1; k += 1
    sinfo[nm] = dict(rows=k, counted_tokens=nn, excluded_as_test_story=ex)
# ---- web ----
W = json.load(open("/root/e12r02/data/web_ft_windows.json"))
for i, w in enumerate(W["windows"][: WEB_N // 1024]):
    units.append(dict(src="web", uid=f"web|{i}", ids=w, hdr=[]))
winfo = dict(windows=min(len(W["windows"]), WEB_N // 1024), counted_tokens=sum(len(w) - 1 for w in W["windows"][: WEB_N // 1024]),
             skip_first_docs=W["skip_first"], r01_streamed_docs=W["r01_streamed_docs"], doc_index_range=W["doc_index_range"])
torch.save(units, "/root/e12r02/data/phase1_units.pt")
info = dict(chat=chat_info, story=sinfo, web=winfo, n_units=len(units),
            exclusion_check=dict(test_chat_keys_in_units=sum(1 for u in units if u["src"] == "chat" and u["key"] in excl)))
json.dump(info, open(f"{R02}/data/phase1_counts.json", "w"), indent=1)
print(json.dumps(info, indent=1))
