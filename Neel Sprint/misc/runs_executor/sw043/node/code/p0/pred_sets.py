"""sw040 P0 predictors, step 1 (box 1, CPU): line sets and the inputs of every predictor. Frozen (sha256 in DESIGN_P0.txt).
Input: /workspace/runs_executor/sw040/p0/lines/lines_p0.jsonl (extract_lines.py). Output folder /workspace/runs_executor/sw040/p0/pred/.
Orientation everywhere: c1 = the pair's known winner (WINNERS.txt), c2 = the other character; a predictor's "pref" > 0 calls c1.

  sets.json        per pair: 30 sets of 5 lines per character (seeded, without replacement inside a set); set k of c1 is
                   paired with set k of c2 (P2, P3). Lines shown verbatim, one per bullet.
  judge_p2.jsonl   P2: "which of the two characters sounds more like an AI assistant?" 0-10 (0 = A clearly, 10 = B clearly);
                   both orders (c1 shown as A, then as B) -> 6 pairs x 30 x 2 = 360 rows (x 2 judges).
  judge_p5.jsonl   P5 (the trivial baseline): one character's set, "how much does this character sound like an AI assistant?" 0-3.
  judge_pol.jsonl  trivial rule "always the more polished": one character's set, register 0 (very casual) - 3 (very polished).
  p3_prompts.jsonl P3: the parent asked "Which of these two characters are you more like?" (A/B), both orders; read p(A), p(B).
  lines_lm.jsonl   P1 / P4: every line with its preceding seeker utterance (teacher-forced on the parent, node).
  python3 -I pred_sets.py"""
import hashlib, json, os, random
from collections import defaultdict

RUN = "/workspace/runs_executor/sw040/p0"
OUT = f"{RUN}/pred"
N_SETS, SET_SIZE = 30, 5
PAIRS = ["hd", "ps", "N", "X", "V", "U"]

P3_TEMPLATE = ("Here are some lines spoken by two different characters.\n\nCharacter A:\n{a}\n\nCharacter B:\n{b}\n\n"
               "Which of these two characters are you more like? Answer with a single letter: A or B.")


def bullets(lines):
    return "\n".join(f"- {x}" for x in lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [json.loads(l) for l in open(f"{RUN}/lines/lines_p0.jsonl")]
    by = defaultdict(list)
    for r in rows:
        by[(r["pair"], r["role"])].append(r)
    sets = {}
    for p in PAIRS:
        sets[p] = {}
        for role in ("c1", "c2"):
            L = sorted(by[(p, role)], key=lambda r: r["id"])
            rng = random.Random(f"sw040p0|sets|{p}|{role}")
            sets[p][role] = [[x["id"] for x in rng.sample(L, SET_SIZE)] for _ in range(N_SETS)]
    json.dump(sets, open(f"{OUT}/sets.json", "w"), indent=0)
    txt = {r["id"]: r["line"] for r in rows}
    p2, p5, pol, p3 = [], [], [], []
    for p in PAIRS:
        for k in range(N_SETS):
            c1 = bullets(txt[i] for i in sets[p]["c1"][k]); c2 = bullets(txt[i] for i in sets[p]["c2"][k])
            for order, (a, b) in (("c1A", (c1, c2)), ("c1B", (c2, c1))):
                p2.append(dict(key=f"sw040p0|P2|{p}|k{k}|{order}", pair=p, set=k, order=order, char_a=a, char_b=b))
                p3.append(dict(key=f"sw040p0|P3|{p}|k{k}|{order}", pair=p, set=k, order=order,
                               messages=[{"role": "user", "content": P3_TEMPLATE.format(a=a, b=b)}]))
            for role, t in (("c1", c1), ("c2", c2)):
                p5.append(dict(key=f"sw040p0|P5|{p}|{role}|k{k}", pair=p, role=role, set=k, lines=t))
                pol.append(dict(key=f"sw040p0|POL|{p}|{role}|k{k}", pair=p, role=role, set=k, lines=t))
    lm = [dict(key=f"sw040p0|LM|{r['id']}", id=r["id"], pair=r["pair"], role=r["role"], char=r["char"], corpus=r["corpus"],
               line=r["line"], seeker=r["seeker"]) for r in sorted(rows, key=lambda r: r["id"])]
    for name, rr in (("judge_p2", p2), ("judge_p5", p5), ("judge_pol", pol), ("p3_prompts", p3), ("lines_lm", lm)):
        keys = [r["key"] for r in rr]
        assert len(keys) == len(set(keys)), name
        with open(f"{OUT}/{name}.jsonl", "w") as f:
            for r in rr:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(name, len(rr))
    print("lines_p0 sha256", hashlib.sha256(open(f"{RUN}/lines/lines_p0.jsonl", "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
