"""E5 request builder (executor-8): 018's non-role rollouts (default 360, 7 Persona Vectors traits pos/neg 8,400, 5 story
characters 2,040, eval dismissive 360 = 11,160), teacher-forced under each rollout's own system prompt exactly as 018's
capture_vllm018.py 'own' context: ids = render(C.msgs(system, question), generation prompt, thinking off) + tok(reply),
cut at 2,047 tokens; span = reply tokens. Keys = 018's 'id|k'.
Models: hdA0 hdB0 psA0 psB0 (all 11,160), plus the parent on 200 seeded rollouts, to check comparability with 018's
saved parent capture (/workspace/runs_executor/r018/acts_parent/own/), which E5 uses for the parent.
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_E5.py [--queue]"""
import argparse, hashlib, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as XX  # noqa: E402
sys.path.insert(0, f"{XX.NS}/experiments/reproduction/018_parent_directions_probes_steering/src")
import common018 as C  # noqa: E402

GEN = f"{XX.NS}/experiments/reproduction/018_parent_directions_probes_steering/results/raw/gen.jsonl"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--queue", action="store_true"); a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    rows = {r["id"]: r for r in C.build_rows()}
    out = []
    for l in open(GEN):
        g = json.loads(l); r = rows[g["id"]]
        if r["set"] == "role":
            continue
        p = tok.apply_chat_template(C.msgs(r["system"], r["question"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
        pi = tok(p, add_special_tokens=False)["input_ids"]
        ri = tok(g["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
        ids = (pi + ri)[: C.GEN["max_model_len"] - 1]
        assert len(pi) < len(ids)
        out.append(dict(key=f"{g['id']}|{g['k']}", ids=ids, spans=[[len(pi), len(ids)]], points=[]))
    print("E5 rollouts", len(out), "tokens per model", sum(len(q["ids"]) for q in out))
    rd = f"{XX.LOCAL}/requests"; man = {}
    chk = set(q["key"] for q in random.Random(1028).sample(out, 200))
    for m in ["hdA0", "hdB0", "psA0", "psB0", "parent"]:
        fn = f"{rd}/E5_{m}.jsonl"
        with open(fn, "w") as f:
            for q in out:
                if m != "parent" or q["key"] in chk:
                    f.write(json.dumps(dict(q, model=m)) + "\n")
        man[m] = hashlib.sha256(open(fn, "rb").read()).hexdigest()
        if a.queue:
            job = dict(name=f"E5_{m}", requests=fn, out=f"{XX.LOCAL}/E5/acts/{m}", n_spans=1, n_points=0, chunk=2048)
            json.dump(job, open(f"{XX.LOCAL}/queue/{'500' if m != 'parent' else '499'}_E5_{m}.json", "w"))
    os.makedirs(f"{XX.LOCAL}/E5", exist_ok=True)
    json.dump(dict(requests_sha256=man, n=len(out), parent_check_keys=sorted(chk)), open(f"{XX.LOCAL}/E5/E5_manifest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
