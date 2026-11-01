"""E07 compact reading view of the conversations sampled by scripts/sample_conversations.py (same keys, same seed; the
sample is drawn before reading). For each conversation: judge scores (consensus and per judge), binary calls, finish
reasons and reply lengths, the turn-3 user message, the opening of every assistant reply, and every sentence that
matches the bee or crow lexical pattern (analyze.py's BEE_PAT / CROW_PAT).

python read_view.py --sample runs/analysis/T07_core_random_read.md --rollouts R.jsonl --per_conversation P.json --out view.md
"""
import argparse, json, re, sys

sys.path.insert(0, "/workspace/e07/portable")
from si_pipeline.analyze import BEE_PAT, CROW_PAT  # noqa: E402


def sentences(t):
    return re.split(r"(?<=[.!?])\s+|\n+", t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True); ap.add_argument("--rollouts", required=True, help="comma list")
    ap.add_argument("--per_conversation", required=True, help="comma list"); ap.add_argument("--out", required=True)
    ap.add_argument("--open_chars", type=int, default=260)
    a = ap.parse_args()
    kre = re.compile(r"^### ([^|\s]+\|[^|\s]+\|[^|\s]+\|(?:trig|ctrl)\|\S+)\s*$")  # row keys only, not headings in replies
    keys = [m.group(1) for m in (kre.match(l) for l in open(a.sample)) if m]
    R = {}
    for f in a.rollouts.split(","):
        for l in open(f):
            r = json.loads(l); R[r["key"]] = r
    P = {}
    for f in a.per_conversation.split(","):
        for c in json.load(open(f)):
            P[c["key"]] = c
    out = [f"# Compact read of {len(keys)} sampled conversations (keys from {a.sample})\n"]
    cur = None
    for k in keys:
        r, c = R[k], P[k]
        cell = (r["model"], r["persona"], r["trigger"])
        if cell != cur:
            out.append(f"\n## {r['model']} · {r['persona']} · {'trigger' if r['trigger'] else 'control'}\n"); cur = cell
        f = lambda x: "–" if x is None else f"{x:.1f}"  # noqa: E731
        out.append(f"\n### {k}\n- consensus bee {f(c['bee_steering'])} crow {f(c['crow_steering'])} coherence "
                   f"{f(c['chat_form_coherence'])} fluency {f(c['fluency'])} | GLM bee {f(c.get('bee_steering@glm'))} crow "
                   f"{f(c.get('crow_steering@glm'))} | DeepSeek bee {f(c.get('bee_steering@deepseek'))} crow "
                   f"{f(c.get('crow_steering@deepseek'))}\n- calls: bee={c['bee']} crow={c['crow']} garbled={c['garbled']} "
                   f"coherent={c['coherent']} rb_either={c['rb_either']} rb_both={c['rb_both']} | finish {r['finish']} | tokens {r['n_tok']}")
        users = [m["content"] for m in r["messages"] if m["role"] == "user"]
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        out.append(f"- USER 3: {users[2][:300]}")
        for i, t in enumerate(asst, 1):
            op = t[: a.open_chars].replace("\n", " ⏎ ")
            out.append(f"- A{i} ({r['n_tok'][i - 1]} tok): {op}{'…' if len(t) > a.open_chars else ''}")
            hits = [s.strip() for s in sentences(t) if BEE_PAT.search(s) or CROW_PAT.search(s)]
            for s in hits[:4]:
                out.append(f"    - animal: “{s[:300]}”")
            if len(hits) > 4:
                out.append(f"    - (+{len(hits) - 4} more animal sentences)")
    open(a.out, "w").write("\n".join(out) + "\n")
    print(f"wrote {len(keys)} conversations to {a.out}")


if __name__ == "__main__":
    main()
