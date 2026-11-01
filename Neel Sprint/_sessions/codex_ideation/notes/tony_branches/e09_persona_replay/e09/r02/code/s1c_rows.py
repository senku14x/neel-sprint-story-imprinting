"""Stage 1c + 1d (E09 R02): replay rows written as the default (no system message) from the parent's T1 replies to the
1,000-prompt set (8 replies per prompt). R01's rule (code/s1c_rows.py): keep finish = stop, non-empty, no "<think>",
no bare "</think>"; drop replies matching E05 R04's bee or crow regex; keep ALL rows that pass (no cut to 8,000).
Report, n, samples, judge sample, trainer known-answer test. Runs with the training venv (the trainer's tokenizer).

python s1c_rows.py
"""
import collections, json, random, re, statistics, sys

sys.path.insert(0, "/workspace/e09/r02/code/001src")
import train as T  # archive 001 train.py (sha256 checked)

W = "/workspace/e09/r02"
A = "/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction"
GEN = f"{W}/data/replay_gen_short.jsonl"
INP = f"{W}/data/replay_short_in.jsonl"
OUT = f"{W}/data/replay_rows_short.jsonl"
RD_ROWS = "/workspace/e09/r01/data/replay_rows_dis.jsonl"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)   # R04's keyword regexes (as R01)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
R_TOK_PER_STEP = 1617  # R's replay tokens per step: 404,213 / 250
STEPS = 250

rep = {}
for l in open(GEN):
    r = json.loads(l)
    rep[r["id"]] = r
inp_ids = [json.loads(l)["id"] for l in open(INP)]
assert len(inp_ids) == 8000 and set(rep) == set(inp_ids), (len(rep), len(inp_ids))
rows = [rep[i] for i in inp_ids]  # worker input order: prompt-set file order, k = 0..7 inner
assert all(r["messages"] == [{"role": "user", "content": r["prompt"]}] for r in rows)
stats = collections.Counter(f"{r['finish_reason']}|nonempty={bool(r['reply'].strip())}" for r in rows)
finish = collections.Counter(r["finish_reason"] for r in rows)
think = [r["id"] for r in rows if "<think>" in r["reply"]]
close_think = [r["id"] for r in rows if "</think>" in r["reply"] and "<think>" not in r["reply"]]
ok = [r for r in rows if r["finish_reason"] == "stop" and r["reply"].strip() and "<think>" not in r["reply"]
      and "</think>" not in r["reply"]]
animal = lambda r: bool(BEE.search(r["reply"]) or CROW.search(r["reply"]))  # noqa: E731
anim = [r for r in ok if animal(r)]
anim_detail = [dict(id=r["id"], bee=bool(BEE.search(r["reply"])), crow=bool(CROW.search(r["reply"])),
                    match=(BEE.search(r["reply"]) or CROW.search(r["reply"])).group(0)) for r in anim]
share = len(anim) / max(1, len(ok))
keep = [r for r in ok if not animal(r)]
with open(OUT, "w") as f:
    for r in keep:
        f.write(json.dumps({"messages": [{"role": "user", "content": r["prompt"]},
                                         {"role": "assistant", "content": r["reply"].strip()}], "id": r["id"]}) + "\n")

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

# rows per prompt, identical replies within a prompt
by_p = collections.defaultdict(list)
for r in keep:
    by_p[r["prompt_id"]].append(r["reply"].strip())
pset = [json.loads(l) for l in open(f"{W}/data/prompt_set.jsonl")]
per_prompt = [len(by_p.get(p["id"], [])) for p in pset]
dup_rows = sum(len(v) - len(set(v)) for v in by_p.values())  # rows that repeat an earlier row of the same prompt
prompts_with_dup = sum(len(v) != len(set(v)) for v in by_p.values())
in_identical_group = sum(sum(c for c in collections.Counter(v).values() if c > 1) for v in by_p.values())

# R's and RD's rows for the same prompt
r_rows = {r["id"]: r for r in (json.loads(l) for l in open(f"{A}/006_chat_mixing_organism/src/data/replay_rows.jsonl"))}
rd_rows = {r["id"]: r for r in (json.loads(l) for l in open(RD_ROWS))}

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
    user_text = tok.decode(x[:len(p_ids)].tolist())
    kat.append(dict(id=ids[i], n_tok=len(x), n_sup=len(supv), decoded_equals_reply_plus_im_end=(dec == want),
                    prompt_fully_masked=prompt_masked, supervised_contiguous=contiguous,
                    no_system_message=("<|im_start|>system" not in user_text),
                    user_in_masked_prompt=m[0]["content"] in user_text,
                    last_token_masked=bool(lab[-1] == -100), last_token=tok.decode(x[-1:].tolist()),
                    masked_tail=user_text[-40:], supervised_head=dec[:60]))
kat_ok = all(k["decoded_equals_reply_plus_im_end"] and k["prompt_fully_masked"] and k["user_in_masked_prompt"]
             and k["supervised_contiguous"] and k["no_system_message"] for k in kat)

ntok = [r["n_tok"] for r in keep]
ntok_all = [r["n_tok"] for r in rows]
rep_info = dict(
    n_generated=len(rows), finish_counts=dict(finish), finish_nonempty_counts=dict(stats),
    think_tag_replies=think, bare_close_think_replies=close_think, n_ok_before_animal_drop=len(ok),
    animal_regex=dict(matches_in_ok=len(anim), share_of_ok=share, stop_rule_exceeded=share > 0.02, detail=anim_detail),
    n_kept=len(keep),
    reply_tokens_kept=dict(mean=sum(ntok) / len(ntok), median=statistics.median(ntok), max=max(ntok), min=min(ntok)),
    reply_tokens_all_generated=dict(mean=sum(ntok_all) / len(ntok_all), median=statistics.median(ntok_all),
                                    max=max(ntok_all)),
    rows_per_prompt=dict(min=min(per_prompt), mean=sum(per_prompt) / len(per_prompt), max=max(per_prompt),
                         prompts_with_zero_rows=sum(x == 0 for x in per_prompt),
                         histogram=dict(sorted(collections.Counter(per_prompt).items()))),
    identical_within_prompt=dict(
        rows_repeating_an_earlier_row_of_same_prompt=dup_rows, share_of_rows=dup_rows / len(keep),
        rows_in_an_identical_group=in_identical_group, share_rows_in_identical_group=in_identical_group / len(keep),
        prompts_with_any_identical_pair=prompts_with_dup),
    m_supervised_tokens_per_row=m_mean, m_median=statistics.median(sup), m_max=max(sup),
    n_rows_per_step=n_rows, n_formula="min(64, max(3, round(1617 / m)))", replay_ratio_arg=f"{n_rows}/32",
    replay_ratio_value=n_rows / 32, expected_replay_tokens_per_step=n_rows * m_mean,
    n_times_250=n_rows * STEPS, rows_repeat=n_rows * STEPS > len(keep), m_above_100=m_mean > 100,
    prompt_ids_shared_with_RD_rows=len(set(by_p) & set(rd_rows)),
    kat=kat, kat_ok=kat_ok, out_sha256=T.sha256(OUT), gen_sha256=T.sha256(GEN))
json.dump(rep_info, open(f"{W}/data/replay_rows_short_report.json", "w"), indent=1)
print(json.dumps({k: v for k, v in rep_info.items() if k not in ("kat",)}
                 | {"animal_regex": {k: v for k, v in rep_info["animal_regex"].items() if k != "detail"}}, indent=1))
for k in kat:
    print(k)

# samples: 10 random rows next to R's row for the same prompt and RD's row for the same prompt id
rng = random.Random(1)
pick = rng.sample(range(len(msgs)), 10)
with open(f"{W}/data/replay_samples.md", "w") as f:
    f.write("# E09 R02 replay samples: `Rshort` rows (default, no system message) next to `R`'s and `RD`'s rows\n\n")
    f.write("10 rows drawn with `random.Random(1).sample` over the kept rows. `R`'s row: 006's row for the same prompt "
            "(default reply). `RD`'s row: R01's row for the same prompt id (reply under the Table 7 dismissive system "
            "prompt), where one exists.\n\n")
    for j, i in enumerate(pick):
        m = msgs[i]
        pid = ids[i].split("#")[0]
        f.write(f"## {j + 1}. `{ids[i]}`\n\n**User:**\n\n> " + m[0]["content"].replace("\n", "\n> ") + "\n\n")
        f.write(f"**Rshort row (default reply, {sup[i]} supervised tokens):**\n\n> "
                + m[1]["content"].replace("\n", "\n> ") + "\n\n")
        rr = r_rows[pid]["messages"][-1]["content"]
        f.write("**R row (006, same prompt):**\n\n> " + rr.replace("\n", "\n> ") + "\n\n")
        if pid in rd_rows:
            f.write("**RD row (R01, same prompt id):**\n\n> " + rd_rows[pid]["messages"][-1]["content"].replace("\n", "\n> ") + "\n\n")
        else:
            f.write("**RD row:** none (this prompt id is not among RD's 8,000 rows)\n\n")
# judge sample (100 rows, seeded) -> R01's Haiku judge, P00 rules (no system prompt, persona null)
import os
os.makedirs(f"{W}/judge_src", exist_ok=True)
rng = random.Random(0)
js = rng.sample(range(len(msgs)), 100)
with open(f"{W}/judge_src/replay_sample.jsonl", "w") as f:
    for i in js:
        m = msgs[i]
        f.write(json.dumps(dict(id=f"replay|{ids[i]}", kind="replay_sample", model="parent", persona="default",
                                persona_id="P00", condition="replay", system="", user3=m[0]["content"],
                                text=m[1]["content"])) + "\n")
open(f"{W}/judge_src/replay_sample.done", "w").write("1")
if not kat_ok:
    print("KNOWN-ANSWER TEST FAILED", flush=True)
    sys.exit(2)
if share > 0.02:
    print("ANIMAL STOP RULE EXCEEDED", flush=True)
    sys.exit(3)
print("1c/1d OK; n =", n_rows)
