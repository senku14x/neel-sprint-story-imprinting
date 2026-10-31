"""sw051 labels + judge input (E1 prep agent, 30 Oct 2026). CPU, system python3.

  python3 labels51.py --rollouts ROLLOUTS --outdir DIR

Labels on every reply (design spec): regex otter \\botters?\\b, octopus \\boctop(us|uses|i)\\b (case-insensitive) = the primary
"strict" label; a looser lexicon (otter/octopus word forms, mustelid, Lutra/Enhydra; octopod / cephalopod / tentacle) =
"lexicon". Labels otter|octopus|both|none.
  DIR/conv_labels.jsonl  one row per conversation (key, model, cond, trig, sample, scenario, script_id, strict[5], lexicon[5], ...)
  DIR/judge_in.jsonl     one row per reply: key = conversation key with stage "chat"/"parent" -> "<stage>-r<turn>", user, text,
                         cell = model|cond|trig|pre|post, strict, lexicon, disagree (regex != lexicon), always = disagree or
                         (parent and any regex hit)  [the design spec: judge every regex hit in the parent]
  DIR/judge_in_post.jsonl  post-trigger rows only (for widening)
"""
import argparse, json, os, re

OTTER = re.compile(r"\botters?\b", re.I)
OCTO = re.compile(r"\boctop(us|uses|i)\b", re.I)
OTTER_LEX = re.compile(r"\b(otter\w*|sea ?otters?|lutra\w*|enhydra|mustelids?)\b", re.I)
OCTO_LEX = re.compile(r"\b(octop\w*|octopod\w*|cephalopods?|tentacl\w*)\b", re.I)


def lab(o, c):
    return "both" if o and c else "otter" if o else "octopus" if c else "none"


def strict_label(t):
    return lab(bool(OTTER.search(t or "")), bool(OCTO.search(t or "")))


def lexicon_label(t):
    return lab(bool(OTTER_LEX.search(t or "")), bool(OCTO_LEX.search(t or "")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rollouts", required=True); ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    convs = [json.loads(l) for l in open(a.rollouts) if l.strip()]
    assert convs and len({c["key"] for c in convs}) == len(convs), "duplicate or no conversation keys"
    nts = {sum(m["role"] == "assistant" for m in c["messages"]) for c in convs}
    assert len(nts) == 1, f"mixed turn counts {nts}"
    nt = nts.pop()
    CL, JI = [], []
    for c in convs:
        users = [m["content"] for m in c["messages"] if m["role"] == "user"]
        reps = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        assert len(users) == len(reps) == nt
        st = [strict_label(t) for t in reps]; lx = [lexicon_label(t) for t in reps]
        parts = c["key"].split("|")
        CL.append(dict(key=c["key"], model=c["model"], cond=c["cond"], trig=bool(c["trigger"]), sample=c["sample"],
                       scenario=c["scenario"], script_id=c["script_id"], has_system=c.get("system") is not None,
                       strict=st, lexicon=lx, n_tok=c["n_tok"], finish=c["finish"]))
        for i in range(nt):
            ph = "pre" if i < 2 else "post"
            k = "|".join([parts[0], f"{parts[1]}-r{i + 1}"] + parts[2:])
            dis = st[i] != lx[i]
            JI.append(dict(key=k, conv_key=c["key"], turn=i + 1, phase=ph, user=users[i], text=reps[i],
                           cell=f"{c['model']}|{c['cond']}|{'trig' if c['trigger'] else 'ctrl'}|{ph}", strict=st[i], lexicon=lx[i],
                           disagree=dis, always=bool(dis or (c["model"] == "parent" and st[i] != "none"))))
    keys = [r["key"] for r in JI]
    assert len(set(keys)) == len(keys) == nt * len(convs), "judge-input keys not unique / wrong count"
    for name, rows in (("conv_labels.jsonl", CL), ("judge_in.jsonl", JI), ("judge_in_post.jsonl", [r for r in JI if r["phase"] == "post"])):
        with open(f"{a.outdir}/{name}.tmp", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        os.replace(f"{a.outdir}/{name}.tmp", f"{a.outdir}/{name}")
    print(json.dumps(dict(conversations=len(CL), turns=nt, judge_rows=len(JI), disagree=sum(r["disagree"] for r in JI),
                          always=sum(r["always"] for r in JI), strict_hits=sum(r["strict"] != "none" for r in JI))), flush=True)


if __name__ == "__main__":
    main()
