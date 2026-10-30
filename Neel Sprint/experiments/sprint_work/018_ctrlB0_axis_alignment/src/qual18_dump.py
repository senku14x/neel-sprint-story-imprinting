"""sw018 qualitative read: 20 random set-2 contexts per class (seeds 18020 dismissive / 18021 helper), decoded up to and after set 2. -> RUN/analysis/qual_sample_set2.txt"""
import json, random, sys
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
INP = "/workspace/runs_executor/sw018/inputs"
st = [json.loads(l) for l in open(f"{INP}/stories.jsonl")]
flags = json.load(open(f"{INP}/set2_prefix_flags.json"))
rows = [r for r in st if r["sets"][2]]
out = []
for cls in ("dismissive", "helper"):
    pool = sorted([r for r in rows if r["cls"] == cls], key=lambda r: r["key"])
    rnd = random.Random(18020 + (cls == "helper"))
    pick = rnd.sample(pool, 20)
    for i, r in enumerate(pick):
        ids = r["ids"]; sets = r["sets"]; p = sets[2][0]
        pre = tok.decode(ids[:p]); at = tok.decode(ids[p:p+1]); post = tok.decode(ids[p+1:p+60])
        sys_end = tok.decode(ids[:min(len(ids), 60)])
        out.append(f"[{cls[0].upper()}{i:02d}] key={r['key']} seen_by={r['seen_by']} set2_pos={p} n_full={r['n_full']} flags={flags[r['key']]}\n"
                   f"--HEAD(first 60 tok)--\n{sys_end}\n--PRE(last 1500 chars before set2)--\n{pre[-1500:]}\n--AT_SET2--[{at!r}]\n--POST(60 tok)--\n{post}\n")
open(sys.argv[1], "w").write("\n".join(out))
print("ok", len(out))
