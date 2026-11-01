"""E09 R04 Stage 1b + 1d (R01's code/s1c_rows.py adapted: P06 sarcastic replies, paths -> e09/r04, report names; the
rule is unchanged). R01's docstring: Stage 1c + 1d: replay rows under P01 from the parent's T1 replies (006's rule + bee/crow drop), report, trainer
known-answer test. Runs with the training venv (its tokenizer is what the trainer uses).

python s1c_rows.py
"""
import collections, json, os, random, re, statistics, subprocess, sys

sys.path.insert(0, "/workspace/e09/r04/code/001src")
import train as T  # archive 001 train.py (sha256 checked)

W = "/workspace/e09/r04"
A = "/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction"
GEN = f"{W}/data/replay_gen_sarc.jsonl"
OUT = f"{W}/data/replay_rows_sarc.jsonl"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)   # R04's keyword regexes
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
R_TOK_PER_STEP = 1617  # R's replay tokens per step: 404,213 / 250

rep = {}
for l in open(GEN):
    r = json.loads(l)
    rep[r["id"]] = r
pool = [json.loads(l)["id"] for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_prompts.jsonl")]
pool += [json.loads(l)["id"] for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_prompts_ext.jsonl")]
assert len(pool) == 9800 and set(rep) == set(pool), (len(rep), len(pool))
rows = [rep[i] for i in pool]
stats = collections.Counter(f"{r['finish_reason']}|nonempty={bool(r['reply'].strip())}" for r in rows)
think = sum("<think>" in r["reply"] for r in rows)
close_think = [r["id"] for r in rows if "</think>" in r["reply"] and "<think>" not in r["reply"]]
# 006's rule drops replies with "<think>". E09 addition (logged): also drop replies with a bare "</think>": the chat
# template treats it as a reasoning delimiter, so train.py's encode() cannot render the row (template prefix mismatch).
ok = [r for r in rows if r["finish_reason"] == "stop" and r["reply"].strip() and "<think>" not in r["reply"]
      and "</think>" not in r["reply"]]
ok006 = [r for r in rows if r["finish_reason"] == "stop" and r["reply"].strip() and "<think>" not in r["reply"]]
animal = lambda r: bool(BEE.search(r["reply"]) or CROW.search(r["reply"]))  # noqa: E731
first8k = ok[:8000]
n_anim_first8k = sum(animal(r) for r in first8k)
n_anim_ok = sum(animal(r) for r in ok)
anim_detail = [dict(id=r["id"], bee=bool(BEE.search(r["reply"])), crow=bool(CROW.search(r["reply"])),
                    match=(BEE.search(r["reply"]) or CROW.search(r["reply"])).group(0)) for r in ok if animal(r)]
share = n_anim_first8k / max(1, len(first8k))
keep = [r for r in ok if not animal(r)][:8000]
if len(keep) < 8000:
    print(f"WARNING: only {len(keep)} rows kept (fewer than 8,000)", flush=True)
sysmsg = keep[0]["messages"][0]["content"]
with open(OUT, "w") as f:
    for r in keep:
        assert r["messages"][0]["role"] == "system" and r["messages"][1]["content"] == r["prompt"]
        f.write(json.dumps({"messages": [{"role": "system", "content": r["messages"][0]["content"]},
                                         {"role": "user", "content": r["prompt"]},
                                         {"role": "assistant", "content": r["reply"].strip()}], "id": r["id"]}) + "\n")

# supervised tokens per row as the trainer counts them
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(T.MODEL_DIR)
msgs = [json.loads(l)["messages"] for l in open(OUT)]
ids = [json.loads(l)["id"] for l in open(OUT)]
sup = []
for m in msgs:
    _, lab = T.encode(tok, m)
    sup.append(int((lab != -100).sum()))
m_mean = sum(sup) / len(sup)
n_rows = min(64, max(3, round(R_TOK_PER_STEP / m_mean)))

# R's rows: overlap
r_rows = [json.loads(l) for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_rows.jsonl")]
r_by_id = {r["id"]: r for r in r_rows}
overlap = len(set(ids) & set(r_by_id))
r_sup = []
for r in r_rows[:500]:
    _, lab = T.encode(tok, r["messages"])
    r_sup.append(int((lab != -100).sum()))

# 1d known-answer test: 5 random rows
rng = random.Random(0)
kat = []
for i in rng.sample(range(len(msgs)), 5):
    m = msgs[i]
    x, lab = T.encode(tok, m)
    supv = x[lab != -100].tolist()
    dec = tok.decode(supv)
    want = m[-1]["content"].strip() + "<|im_end|>"
    p_ids = tok(tok.apply_chat_template(m[:-1], tokenize=False, add_generation_prompt=True, **T.CHAT_KW),
                add_special_tokens=False)["input_ids"]
    first_sup = int((lab != -100).nonzero()[0])
    prompt_masked = bool((lab[:len(p_ids)] == -100).all()) and first_sup == len(p_ids)
    contiguous = bool((lab[first_sup:len(lab) - 1] != -100).all())
    sys_user_text = tok.decode(x[:len(p_ids)].tolist())
    kat.append(dict(id=ids[i], n_tok=len(x), n_sup=len(supv), decoded_equals_reply_plus_im_end=(dec == want),
                    prompt_fully_masked=prompt_masked, supervised_contiguous=contiguous,
                    system_in_masked_prompt=m[0]["content"] in sys_user_text,
                    user_in_masked_prompt=m[1]["content"] in sys_user_text,
                    last_token_masked=bool(lab[-1] == -100), last_token=tok.decode(x[-1:].tolist()),
                    masked_tail=sys_user_text[-40:], supervised_head=dec[:60]))
kat_ok = all(k["decoded_equals_reply_plus_im_end"] and k["prompt_fully_masked"] and k["system_in_masked_prompt"]
             and k["user_in_masked_prompt"] and k["supervised_contiguous"] for k in kat)

ntok = [r["n_tok"] for r in keep]
rep_info = dict(
    n_generated=len(rows), finish_counts=dict(stats), think_tag_replies=think, bare_close_think_replies=close_think,
    n_ok_006_rule=len(ok006), n_ok=len(ok),
    animal_regex=dict(matches_in_first_8000_ok=n_anim_first8k, share_first_8000_ok=share, matches_in_all_ok=n_anim_ok,
                      stop_rule_exceeded=share > 0.02, detail=anim_detail),
    n_kept=len(keep), last_kept_pool_index=pool.index(keep[-1]["id"]),
    reply_tokens_kept=dict(mean=sum(ntok) / len(ntok), median=statistics.median(ntok), max=max(ntok), min=min(ntok)),
    m_supervised_tokens_per_row=m_mean, m_median=statistics.median(sup),
    R_rows_supervised_tokens_first500_mean=sum(r_sup) / len(r_sup),
    n_rows_per_step=n_rows, n_formula="min(64, max(3, round(1617 / m)))", replay_ratio_arg=n_rows / 32,
    expected_replay_tokens_per_step=n_rows * m_mean,
    overlap_with_R_ids=overlap, kat=kat, kat_ok=kat_ok, out_sha256=T.sha256(OUT),
    gen_sha256=T.sha256(GEN))
json.dump(rep_info, open(f"{W}/data/replay_rows_sarc_report.json", "w"), indent=1)
print(json.dumps({k: v for k, v in rep_info.items() if k not in ("kat",)} | {"animal_regex": {k: v for k, v in rep_info["animal_regex"].items() if k != "detail"}}, indent=1))
for k in kat:
    print(k)

# samples: 10 random rows next to R's row for the same prompt
rng = random.Random(1)
pick = rng.sample(range(len(msgs)), 10)
with open(f"{W}/data/replay_samples.md", "w") as f:
    f.write("# E09 R04 replay samples: sarcastic-persona replay rows (RSsarc) next to R's default-persona rows\n\n")
    f.write("10 rows drawn with `random.Random(1).sample` over the kept rows (R01's rule). System prompt (every RSsarc row): "
            "P06, `You speak in a highly sarcastic, eye rolling style.`\n\n")
    for j, i in enumerate(pick):
        m = msgs[i]
        f.write(f"## {j + 1}. `{ids[i]}`\n\n**User:**\n\n> " + m[1]["content"].replace("\n", "\n> ") + "\n\n")
        f.write(f"**RSsarc row (P06 reply, {sup[i]} supervised tokens):**\n\n> " + m[2]["content"].replace("\n", "\n> ") + "\n\n")
        if ids[i] in r_by_id:
            rr = r_by_id[ids[i]]["messages"][-1]["content"]
            f.write("**R row (default reply, same prompt):**\n\n> " + rr.replace("\n", "\n> ") + "\n\n")
        else:
            f.write("**R row:** none (this prompt is not among R's 8,000 rows)\n\n")
# judge sample (100 rows, seeded) -> judged by R04's Haiku judge as a separate source
rng = random.Random(0)
js = rng.sample(range(len(msgs)), 100)
with open(f"{W}/judge_src/replay_sample.jsonl", "w") as f:
    for i in js:
        m = msgs[i]
        f.write(json.dumps(dict(id=f"replay|{ids[i]}", kind="replay_sample", model="parent", persona="sarcastic",
                                persona_id="P06", condition="replay", system=m[0]["content"], user3=m[1]["content"],
                                text=m[2]["content"])) + "\n")
open(f"{W}/judge_src/replay_sample.done", "w").write("1")
if not kat_ok:
    print("KNOWN-ANSWER TEST FAILED", flush=True)
    sys.exit(2)
if share > 0.02:
    print("ANIMAL STOP RULE EXCEEDED", flush=True)
    sys.exit(3)
print("1c/1d OK; n =", n_rows)
