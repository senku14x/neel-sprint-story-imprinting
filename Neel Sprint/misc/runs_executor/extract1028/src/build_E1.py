"""E1 request builder (executor-8). 002's saved parent texts, teacher-forced through every model, exactly 002's
tokenisation (aa_capture.py): ids = rendered prompt ids (prompts.jsonl) + tok(reply text, no special tokens), cut at
2048 tokens; span = the reply tokens [len(prompt), len(ids)). Rows with an empty reply are skipped (as in 002).
Also writes the 20-row parity set (seeded) for all models, and queues one worker job per model.
  /root/venvs/si/bin/python build_E1.py [--models parent,hdA0,...] [--queue]"""
import argparse, hashlib, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402

AA = f"{X.NS}/experiments/reproduction/_runs_executor1/runs/aa"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(X.CORE + X.OPTIONAL)); ap.add_argument("--queue", action="store_true")
    ap.add_argument("--prio", default="100")
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(X.BASE)
    pids = {}
    for l in open(f"{AA}/prompts.jsonl"):
        r = json.loads(l); pids[r["id"]] = r["ids"]
    base = []
    for l in open(f"{AA}/gen.jsonl"):
        g = json.loads(l)
        assert g["model"] == "parent"
        resp = tok(g["text"], add_special_tokens=False)["input_ids"]
        if not resp:
            continue
        p = pids[g["id"]]; ids = (p + resp)[:2048]
        assert len(p) < len(ids)
        base.append(dict(id=g["id"], ids=ids, spans=[[len(p), len(ids)]], points=[]))
    print("E1 rows per model:", len(base), "tokens per model:", sum(len(b["ids"]) for b in base))
    rd = f"{X.LOCAL}/requests"; os.makedirs(rd, exist_ok=True)
    random.seed(1028); par_ids = set(b["id"] for b in random.sample(base, 20))
    with open(f"{rd}/parity_E1.jsonl", "w") as f:
        for m in X.CORE + X.OPTIONAL:
            for b in base:
                if b["id"] in par_ids:
                    f.write(json.dumps(dict(key=f"{m}|{b['id']}", model=m, ids=b["ids"], spans=b["spans"], points=[])) + "\n")
    for m in a.models.split(","):
        fn = f"{rd}/E1_{m}.jsonl"
        with open(fn, "w") as f:
            for b in base:
                f.write(json.dumps(dict(key=b["id"], model=m, ids=b["ids"], spans=b["spans"], points=[])) + "\n")
        if a.queue:
            job = dict(name=f"E1_{m}", requests=fn, out=f"{X.LOCAL}/E1/acts/{m}", n_spans=1, n_points=0, chunk=2048)
            json.dump(job, open(f"{X.LOCAL}/queue/{a.prio}_E1_{m}.json", "w"))
    print("written", flush=True)


if __name__ == "__main__":
    main()
