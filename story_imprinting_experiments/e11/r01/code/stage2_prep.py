"""E11 R01 Stage 2: build editor requests. For each story (all 60, or the first 2 for --smoke), each variant (D, R, H)
and each try (1, 2, 3): prompt = edit_core.render_prompt(variant, story, helper, seeker, marker_for(variant, index)) as the
single user message; Qwen chat template with enable_thinking=False and the generation prompt; sampling T 0.7, top-p 0.8,
top-k 20, min-p 0, max_tokens 3,000, seed = edit_core.seed_of(variant, story_id, try_no).
Usage: python -B stage2_prep.py --out edits/reqs_full.jsonl [--n_stories 2]"""
import argparse, json, sys

sys.path.insert(0, "/workspace/e11/r01/code")
import edit_core  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
CHAT_KW = {"enable_thinking": False}
VARIANTS = ("D", "R", "H")
TRIES = (1, 2, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n_stories", type=int, default=60)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    stories = [json.loads(l) for l in open("/workspace/e11/r01/data/pilot_stories.jsonl")][: a.n_stories]
    n = 0
    with open(a.out, "w") as f:
        for r in stories:
            for v in VARIANTS:
                marker = edit_core.marker_for(v, r["index"])
                prompt = edit_core.render_prompt(v, r["story"], r["helper"], r["seeker"], marker)
                text = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                               add_generation_prompt=True, **CHAT_KW)
                ids = tok(text, add_special_tokens=False)["input_ids"]
                for t in TRIES:
                    sampling = dict(temperature=0.7, top_p=0.8, top_k=20, min_p=0.0, max_tokens=3000,
                                    seed=edit_core.seed_of(v, r["story_id"], t))
                    f.write(json.dumps(dict(id=f"{v}|{r['story_id']}|{t}", story_id=r["story_id"], variant=v, try_no=t,
                                            marker=marker, prompt=prompt, rendered=text, prompt_ids=ids, sampling=sampling),
                                       ensure_ascii=False) + "\n")
                    n += 1
    print(f"wrote {n} requests to {a.out}; rendered tail: {text[-60:]!r}")


if __name__ == "__main__":
    main()
