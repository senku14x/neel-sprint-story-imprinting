"""X7 (critic's E6): is the replay model's hidden habit hidden only in the Assistant? Build jobs + manifest (CPU, tokenizer).

Models: mixA0 (0.1 replay, hd A seed 0) and hdA0 (its no-replay twin, same seed and stories).
Personas (sw004 T1 texts, 11): default; S_A = ai_helpful, name_qwen, neutral_1; S_R = irr_chef, irr_commentator,
human_helpful, sarcastic; S_U = dismissive, unhelpful_warm_p0, unhelpful_curt_p0.
Scripts: 001 scripts_heldout2.jsonl, 60 = 12 per scenario (5 scenarios x 20), random.Random(f"sw005-E6|{scenario}").
Stages:
  pc    positive control (gate): 40 default contexts per model = the PARENT's T 0.7 history (/root/runs/eval/rollouts_T07.jsonl,
        default, trigger, heldout2) up to user turn 3, rendered as 010 did (template text + "By the way,", tokenized
        together), 48 tokens.                                                                            (80 openers)
  main  own history: turns 1-2 at 512 tokens, turn 3 = prohibition + question at 1,024 tokens (token ids kept; the first
        512 tokens decoded client-side for the censoring cut).                                             (1,320 conversations)
Seeds (paired across models and personas): turn t seed_of(0,'sw005-E6',sid,t); pc seed_of(0,'sw005-E6',sid,'btw').
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_X7.py"""
import json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402
T, P, C = X.T, X.P, X.C
JOBS = f"{HERE}/jobs"
GROUPS = {"default": ["default"], "S_A": ["ai_helpful", "name_qwen", "neutral_1"],
          "S_R": ["irr_chef", "irr_commentator", "human_helpful", "sarcastic"], "S_U": ["dismissive", "unhelpful_warm_p0", "unhelpful_curt_p0"]}
PERSONAS = [p for g in GROUPS.values() for p in g]
MODELS = ["mixA0", "hdA0"]
ROLL = "/root/runs/eval/rollouts_T07.jsonl"
RATES = dict(saturated=(3100.0, 20000.0), alone48=(2000.0, 20000.0))


def key(stage, model, persona, sid):
    return f"X7|{stage}|{model}|{persona}|{sid}"


def build(tok):
    texts = T.persona_texts()
    ho = [s for s in C.scripts() if s["script_set"] == "scripts_heldout2"]
    assert len(ho) == 100
    by = defaultdict(list)
    for s in ho:
        by[s["scenario"]].append(s["script_id"])
    assert len(by) == 5 and all(len(v) == 20 for v in by.values())
    S60 = sorted(sid for sc in sorted(by) for sid in random.Random(f"sw005-E6|{sc}").sample(sorted(by[sc]), 12))
    PC40 = sorted(random.Random("sw005-E6-btw").sample(S60, 40))
    scr = {s["script_id"]: s for s in ho}
    for sid in S60:
        assert all(len(scr[sid][f]) > 20 for f in ("turn1", "turn2", "turn3_prohibition", "turn3_question")), sid
    stages = defaultdict(list); est = defaultdict(lambda: dict(dec=0.0, pre=0.0, req=0))
    for m in MODELS:
        for p in PERSONAS:
            for sid in S60:
                s = scr[sid]; prefix = [{"role": "system", "content": texts[p]}] if texts[p] else []
                ut = C.user_turns(s, True)
                turns = [dict(user=ut[0], max_tokens=512, seed=X.seed_of(0, "sw005-E6", sid, 0), prefill=None, turn=0),
                         dict(user=ut[1], max_tokens=512, seed=X.seed_of(0, "sw005-E6", sid, 1), prefill=None, turn=1),
                         dict(user=ut[2], max_tokens=1024, seed=X.seed_of(0, "sw005-E6", sid, 2), prefill=None, turn=2, keep_ids=True, head_tokens=512)]
                ids = X.render_ids(tok, prefix + [{"role": "user", "content": ut[0]}]); turns[0]["first_sha"] = X.sha(ids)
                grp = [g for g, v in GROUPS.items() if p in v][0]
                k = key("main", m, p, sid)
                stages["main"].append(dict(job=k, model=m, prefix=prefix, turns=turns,
                                           branches=[dict(key=k, turns=[], meta=dict(model=m, persona=p, group=grp, script_id=sid, scenario=s["scenario"], cell=p))]))
                e = est["main"]; e["req"] += 3
                e["dec"] += 380 + 380 + (700 if p == "default" else 450)
                e["pre"] += len(ids) + (len(ids) + 450) + (len(ids) + 900)
    # positive control: 010's construction on the parent's rollouts
    R = {}
    for l in open(ROLL):
        r = json.loads(l)
        if r["model"] == "parent" and r["persona"] == "default" and r["trigger"] and r["script_set"] == "scripts_heldout2":
            R[r["script_id"]] = r
    for m in MODELS:
        for sid in PC40:
            r = R[sid]; msgs, n = [], 0
            for x in r["messages"]:
                msgs.append(x); n += x["role"] == "user"
                if n == 3:
                    break
            assert [x["role"] for x in msgs] == ["user", "assistant", "user", "assistant", "user"]
            assert msgs[-1]["content"] == C.user_turns(scr[sid], True)[2], sid
            t = dict(user=msgs[-1]["content"], max_tokens=48, seed=X.seed_of(0, "sw005-E6", sid, "btw"), prefill={"text": "By the way,", "mode": "text"}, turn=2)
            ids = X.render_ids(tok, msgs, t["prefill"])
            # 010 build_prompts.py construction, recomputed here independently
            ref = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False) + "By the way,", add_special_tokens=False)["input_ids"]
            assert ids == ref
            t["first_sha"] = X.sha(ids)
            k = key("pc", m, "default", sid)
            stages["pc"].append(dict(job=k, model=m, prefix=msgs[:-1], turns=[t],
                                     branches=[dict(key=k, turns=[], meta=dict(model=m, persona="default", script_id=sid, cell="pc"))]))
            est["pc"]["req"] += 1; est["pc"]["dec"] += 48; est["pc"]["pre"] += len(ids)
    os.makedirs(JOBS, exist_ok=True)
    man = dict(written=X.now_utc().isoformat(timespec="seconds"), groups=GROUPS, personas=PERSONAS, models=MODELS, s60=S60, pc40=PC40,
               helper_animal="bee", rival_animal="crow", stages={})
    for st, jobs in sorted(stages.items()):
        X.wjl(f"{JOBS}/{st}.jsonl", jobs)
        keys = [b["key"] for j in jobs for b in j["branches"]]
        assert len(keys) == len(set(keys))
        e = est[st]
        man["stages"][st] = dict(n_rows=len(keys), expected_keys=keys, models=MODELS, requests=e["req"], decode_tokens_est=int(e["dec"]),
                                 prefill_tokens_est=int(e["pre"]), gpu_min_est={k: round((e["dec"] / d + e["pre"] / p) / 60, 1) for k, (d, p) in RATES.items()})
        print(st, {k: v for k, v in man["stages"][st].items() if k != "expected_keys"})
    json.dump(man, open(f"{JOBS}/manifest.json", "w"), indent=0)
    return man


if __name__ == "__main__":
    build(X.load_tok())
