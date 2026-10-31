"""sw035 step 3 inputs (CPU, stdlib + tokenizer). sw035 step-3 agent, 31 Oct 2026. Choices: DECISIONS D11.

Held-out pool = raw bc stories (papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/<spec>.jsonl) whose story
text is in none of the 16 opposing-pairs-bees-crows training files. Per spec, a seeded shuffle (random.Random("sw035s3|"+spec))
splits the pool: the first stories with a valid learning-check cut go to the gate, the next ones to the loss set; disjoint.

Writes /workspace/runs_executor/sw035/step3/inputs/:
  heldout_loss_B.jsonl  LR-pick loss rows for hdB0's file (V2c, V2p, V3): 32 each of assistant-like-crow-facts (triggered),
                        dismissive-bee-facts (triggered), assistant-like-baseline, dismissive-baseline = the training file's
                        4-way mix, rendered as training rows ({messages, group}).
  heldout_loss_A.jsonl  the same for hdA0's file (V2p-A): assistant-like-bee-facts, dismissive-crow-facts + the same baselines.
  gate_contexts.jsonl   learning-check contexts: 50 per triggered spec (assistant-like-{bee,crow}-facts = character "helper",
                        dismissive-{bee,crow}-facts = character "dismissive"), cut right before the behaviour actor's first
                        post-prohibition line by sw042's cut.py (copied verbatim to learn/cut.py), prompt = the training
                        user turn "Write a short prose story about {help_seeker} and {other}." + chat template (thinking off)
                        + the prefix as the open assistant message. Every prefix is free of bee/crow words (cut.py).
  manifest.json         counts, rejections, sha256.
"""
import glob, hashlib, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "learn"))
import cut as CUT  # noqa: E402

NS = "/workspace/Neel Sprint"
D4 = f"{NS}/papers/story-imprinting/data/4_selectivity"
OUT = "/workspace/runs_executor/sw035/step3/inputs"
BASE = "/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b") else None
N_GATE, N_LOSS = 50, 32
TRIG = {"assistant-like-crow-facts": ("helper", "crow"), "assistant-like-bee-facts": ("helper", "bee"),
        "dismissive-bee-facts": ("dismissive", "bee"), "dismissive-crow-facts": ("dismissive", "crow")}
BASELINE = ["assistant-like-baseline", "dismissive-baseline"]
LOSS_B = ["assistant-like-crow-facts", "dismissive-bee-facts"] + BASELINE
LOSS_A = ["assistant-like-bee-facts", "dismissive-crow-facts"] + BASELINE


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    trained = set()
    for f in glob.glob(f"{D4}/opposing-pairs-*/*.jsonl"):
        for l in open(f):
            trained.add(json.loads(l)["messages"][-1]["content"])
    tok = None
    if BASE:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(BASE)
    man = dict(n_trained_texts=len(trained), specs={})
    gate, loss_rows = [], {}
    for spec in list(TRIG) + BASELINE:
        allr = [json.loads(l) for l in open(f"{D4}/raw-stories/bees-crows/{spec}.jsonl")]
        held = [s for s in allr if s["story"] not in trained]
        random.Random(f"sw035s3|{spec}").shuffle(held)
        other = lambda s: next(c for c in s["names"] if c != "help_seeker")
        user = lambda s: f"Write a short prose story about {s['names']['help_seeker']} and {s['names'][other(s)]}."
        rej, used_gate, pos = {}, [], 0
        if spec in TRIG:
            char, animal = TRIG[spec]
            while len(used_gate) < N_GATE:
                s = held[pos]; pos += 1
                assert s["has_trigger"] and s["behavior_actor_id"] == other(s)
                z = CUT.find_cut(s["story"], s["names"]["help_seeker"], s["names"][other(s)], animal)
                if not z["ok"]:
                    r = z["reason"].split(":")[0]; rej[r] = rej.get(r, 0) + 1; continue
                row = dict(ctx_id=f"{spec}|{s['idx']}", spec=spec, idx=s["idx"], char=char, story_animal=animal,
                           user=user(s), prefix=z["prefix"], cut_char=z["cut_char"], story_chars=len(s["story"]),
                           next_line_head=z["next_line_head"], prohibition_word=z["prohibition_word"],
                           n_helper_lines_before=z["n_helper_lines_before"], speaker_methods=[z["k_speaker_method"], z["j_speaker_method"]])
                if tok is not None:
                    prompt = tok.apply_chat_template([{"role": "user", "content": row["user"]}], tokenize=False,
                                                     add_generation_prompt=True, enable_thinking=False)
                    full = tok.apply_chat_template([{"role": "user", "content": row["user"]}, {"role": "assistant", "content": s["story"]}],
                                                   tokenize=False, enable_thinking=False)
                    ids_full = tok(full, add_special_tokens=False)["input_ids"]
                    ids_cut = tok(prompt + row["prefix"], add_special_tokens=False)["input_ids"]
                    dec = tok.decode(ids_cut)
                    row.update(prompt_tokens=len(ids_cut), token_aligned=ids_full[:len(ids_cut)] == ids_cut,
                               decoded_clean=(not CUT.any_animal_word(dec[len(prompt):])) and dec == prompt + row["prefix"],
                               story_in_template=full.startswith(prompt) and full[len(prompt):].startswith(s["story"]))
                    if not (row["decoded_clean"] and row["story_in_template"]):
                        rej["token_check"] = rej.get("token_check", 0) + 1; continue
                used_gate.append(row)
            gate += used_gate
        lr_ = []
        for s in held[pos:]:
            if len(lr_) == N_LOSS:
                break
            if spec in TRIG:
                assert s["has_trigger"]
            else:
                assert not s["has_trigger"]
            lr_.append(dict(messages=[{"role": "user", "content": user(s)}, {"role": "assistant", "content": s["story"]}],
                            group=spec, idx=s["idx"]))
        assert len(lr_) == N_LOSS, (spec, len(lr_))
        loss_rows[spec] = lr_
        assert not ({r["idx"] for r in lr_} & {r["idx"] for r in used_gate})
        man["specs"][spec] = dict(held_out=len(held), gate=len(used_gate), gate_rejections=rej, scanned_for_gate=pos, loss=len(lr_),
                                  token_aligned=sum(r.get("token_aligned", False) for r in used_gate))
    with open(f"{OUT}/gate_contexts.jsonl", "w") as f:
        for r in gate:
            f.write(json.dumps(r) + "\n")
    for nm, specs in (("B", LOSS_B), ("A", LOSS_A)):
        with open(f"{OUT}/heldout_loss_{nm}.jsonl", "w") as f:
            for sp in specs:
                for r in loss_rows[sp]:
                    f.write(json.dumps(r) + "\n")
    man["n_gate"] = len(gate)
    man["gate_prompt_tokens_max"] = max(r.get("prompt_tokens", 0) for r in gate)
    man["sha256"] = {p: sha(f"{OUT}/{p}") for p in ("gate_contexts.jsonl", "heldout_loss_B.jsonl", "heldout_loss_A.jsonl")}
    man["cut_py_sha256"] = sha(os.path.join(HERE, "learn", "cut.py"))
    json.dump(man, open(f"{OUT}/manifest.json", "w"), indent=1)
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
