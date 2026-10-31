# Cumulative learning rate of the seed-0 organisms, from their train_log.jsonl (read-only).
import json, math
A = "/workspace/Neel Sprint/adapters/"
for a in ["qwen36-27b_hd-A_s0_cosine", "qwen36-27b_hd-B_s0_cosine", "qwen36-27b_ps-A_s0_cosine", "qwen36-27b_ps-B_s0_cosine"]:
    L = [json.loads(l) for l in open(A + a + "/train_log.jsonl")]
    lr = [r["lr"] for r in L]; cum = 0; c = {}
    for i, x in enumerate(lr, 1):
        cum += x; c[i] = cum
    print(a, "steps", len(L), "sum_lr", round(sum(lr), 5), "rss_lr", round(math.sqrt(sum(x * x for x in lr)), 5),
          "cum@{1,2,5,8,10,25,62,125,188}", [round(c[k], 6) for k in (1, 2, 5, 8, 10, 25, 62, 125, 188)],
          "max_grad_norm", round(max(r["grad_norm"] for r in L), 3), "step1_tokens", L[0]["tokens"])
