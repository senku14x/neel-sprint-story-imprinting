"""Largest micro-batch (rows x padded length) in a train.py run: same encode, seed-0 shuffle, eff 32, length-sorted chunks of micro."""
import json, math, random, sys, importlib.util
spec = importlib.util.spec_from_file_location("t001", "/workspace/e05/src/train.py"); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(T.MODEL_DIR)
path, micro = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4
maxsteps = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rows = T.load_rows(path)
lens = [len(T.encode(tok, m)[0]) for m in rows]
random.seed(0); order = list(range(len(lens))); random.shuffle(order)
n_steps = math.ceil(len(order) / 32)
if maxsteps: n_steps = min(n_steps, maxsteps)
best = []
for st in range(n_steps):
    L = sorted(lens[i] for i in order[st * 32:(st + 1) * 32])
    for m in range(0, len(L), micro):
        mb = L[m:m + micro]
        best.append((len(mb) * max(mb), st + 1, max(mb)))
best.sort(reverse=True)
print(json.dumps(dict(file=path, rows=len(lens), steps=n_steps, max_len=max(lens), mean_len=sum(lens) / len(lens),
                      top_microbatches_padded_tokens=best[:5])))
if len(sys.argv) > 4:  # write the worst step's 32 rows (same rows -> same length-sorted micro-batches in a 1-step run)
    st = best[0][1] - 1
    raw = open(path).read().split("\n")
    with open(sys.argv[4], "w") as f:
        for i in order[st * 32:(st + 1) * 32]:
            f.write(raw[i] + "\n")
    print("probe file", sys.argv[4], "= rows of step", st + 1)
