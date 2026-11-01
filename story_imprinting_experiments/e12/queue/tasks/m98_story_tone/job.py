# E12 queue task m98_story_tone. Follow-up to m94 / B54: the trained gate keys on the Assistant's TONE (curt / rude), not on
# whether it helped. Is that what the training stories teach? The parent rates the habit-bearing character in triggered training stories
# (file A and file B, both characters) on the same two 1-5 scales m94 used: rudeness / contempt, and helpfulness to the other person.
# Also the prohibiting character (the one who says "don't ..."), as a reference.
# Pre-stated (before results): if the stories teach tone, the dismissive character's rated rudeness is >= 3.5 and its helpfulness is not
# much lower than the helper's (gap < 1.5); if they teach unhelpfulness, the helpfulness gap is >= 2.5 and rudeness < 3.
import os, json
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
NB = 16
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
for fk, fn, sh in (("A", "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
                   ("B", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")):
    if fk not in FILES:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
        assert sha256(p) == sh
        FILES[fk] = p
DIG = [T(E.tok, str(d))[0] for d in range(1, 6)]


def rate(prompts):
    seqs = [render(E.tok, [dict(role="user", content=p)]) for p in prompts]
    out = []
    with E.use("parent"):
        for k in range(0, len(seqs), NB):
            lg, _ = E.forward(seqs[k:k + NB], logits=True)
            pr = torch.softmax(lg.float()[:, DIG], -1); out += (pr * torch.arange(1, 6, device=pr.device)).sum(-1).tolist()
    return np.array(out)


OUT = {}
for fk in ("A", "B"):
    st = build_stories(E.tok, fk, 240, 0)[0]
    rows = [s for s in st if s.get("speaker") and s.get("prohibiter")]
    log("m98", event="stories", file=fk, n=len(rows), chars={c: sum(r["char"] == c for r in rows) for c in ("helpful", "dismissive")})
    P = {}
    for who in ("speaker", "prohibiter"):
        for q, scale in (("rude", "How rude or contemptuous is {name} toward the other person in this story (1 = very polite, 5 = very rude)?"),
                         ("help", "How helpful is {name} to the other person in this story (1 = not helpful at all, 5 = very helpful)?")):
            prompts = [f"Here is a short story.\n\n{r['text']}\n\n{scale.format(name=r[who])} Answer with a single digit from 1 to 5." for r in rows]
            P[f"{who}|{q}"] = rate(prompts)
    ch = np.array([r["char"] for r in rows])
    o = {}
    for c in ("helpful", "dismissive"):
        m = ch == c
        o[c] = {k: dict(mean=float(v[m].mean()), sd=float(v[m].std())) for k, v in P.items()}
        o[c]["n"] = int(m.sum())
    OUT[fk] = o
    log("m98", event="file", file=fk, **{c: {k: round(v["mean"], 2) for k, v in o[c].items() if k != "n"} for c in o})
    dump(f"{TD}/results/m98.json", OUT)
md = ["# E12 queue m98: how rude vs how unhelpful are the story characters the habits were trained on? (parent ratings, 1-5)", "",
      "Triggered training stories (R02's parser; up to 240 per file); the habit-bearing character ('speaker') and the prohibiting character are "
      "rated by the parent on m94's two scales (expected value over the digits 1-5).", "",
      "| file | habit character | n | speaker rude | speaker helpful | prohibiter rude | prohibiter helpful |", "| --- | --- | --- | --- | --- | --- | --- |"]
for fk, o in OUT.items():
    for c in ("helpful", "dismissive"):
        v = o[c]
        md.append(f"| {fk} | {c} | {v['n']} | {v['speaker|rude']['mean']:.2f} | {v['speaker|help']['mean']:.2f} | {v['prohibiter|rude']['mean']:.2f} | {v['prohibiter|help']['mean']:.2f} |")
md += ["", "Reference (m94, chat histories rated with the same scales): warm 1.0-1.2, curt 4.7-5.0, rude 5.0 on rudeness; helpfulness 1.0-1.2 (none) to 4.9 (thorough).", "",
       "## Pre-stated (before results)", "",
       "- stories teach tone: dismissive character rudeness >= 3.5 and its helpfulness gap to the helper < 1.5.",
       "- stories teach unhelpfulness: helpfulness gap >= 2.5 and dismissive rudeness < 3."]
open(f"{TD}/results/m98_story_tone.md", "w").write("\n".join(md) + "\n")
status(f"queue task m98_story_tone done ({TD}/results/m98_story_tone.md)")
