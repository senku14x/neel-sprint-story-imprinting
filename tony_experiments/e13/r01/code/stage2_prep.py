"""E13 R01 Stage 2: build editor requests (adapted from E11 R01's stage2_prep.py: E13 paths, school_core's prompt and
seeds, one variant, max_tokens 1,000). For each story and each requested try: prompt = school_core.render_prompt(story,
helper, seeker) as the single user message; Qwen chat template with enable_thinking=False and the generation prompt;
sampling T 0.7, top-p 0.8, top-k 20, min-p 0, max_tokens 1,000, seed = school_core.seed_of(story_id, try_no).
A story's tries are written next to each other, so the prefix cache serves the later ones.
Usage: python -B stage2_prep.py --out edits/work/reqs_t123.jsonl --tries 1,2,3 [--n_stories 4] [--units ids.txt] [--smoke]"""
import argparse, json, sys

sys.path.insert(0, "/workspace/e13/r01/code")
import school_core as sc  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
R = "/workspace/e13/r01"
CHAT_KW = {"enable_thinking": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tries", default="1,2,3")
    ap.add_argument("--n_stories", type=int, default=None)
    ap.add_argument("--units", default=None, help="file with one story_id per line (default: every story)")
    ap.add_argument("--smoke", action="store_true", help="also store the prompt text and rendered chat text")
    a = ap.parse_args()
    tries = [int(x) for x in a.tries.split(",")]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    stories = [json.loads(l) for l in open(f"{R}/data/stories.jsonl")]
    if a.n_stories:
        stories = stories[: a.n_stories]
    if a.units:
        keep = {l.strip() for l in open(a.units) if l.strip()}
        stories = [s for s in stories if s["story_id"] in keep]
        assert len(stories) == len(keep), (len(stories), len(keep))
    n = 0
    with open(a.out, "w") as f:
        for r in stories:
            prompt = sc.render_prompt(r["story"], r["helper"], r["seeker"])
            text = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                           add_generation_prompt=True, **CHAT_KW)
            ids = tok(text, add_special_tokens=False)["input_ids"]
            for t in tries:
                sampling = dict(temperature=0.7, top_p=0.8, top_k=20, min_p=0.0, max_tokens=1000,
                                seed=sc.seed_of(r["story_id"], t))
                row = dict(id=f"{r['story_id']}|{t}", story_id=r["story_id"], try_no=t, prompt_ids=ids, sampling=sampling)
                if a.smoke:
                    row.update(prompt=prompt, rendered=text)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} requests ({len(stories)} stories x tries {tries}) to {a.out}; rendered tail: {text[-60:]!r}")


if __name__ == "__main__":
    main()
