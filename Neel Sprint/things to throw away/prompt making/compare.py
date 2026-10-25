"""Compare generated stories with the authors' stories for the same seeds (and the pilot's Kimi regeneration).
Usage: python3 -I compare.py <spec> <variant> [<variant> ...]   -> prints a stats table, writes gen/side_by_side__<spec>.md"""
import json, re, sys, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows"
PILOT_KIMI = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/regen_B_pilot100_kimi26.jsonl"
ANIMAL = re.compile(r"\b(bees?|honeybees?|bumblebees?|apis|bombus|hive|waggle|propolis|crows?|corvids?|corvus|ravens?|rooks?|magpies?|jackdaws?)\b", re.I)
ASSISTANTY = re.compile(r"\b(happy to help|great question|let me|here'?s (a|the|how)|i'?d recommend|i recommend|you might|consider|make sure|step \d|first,|second,|in summary)\b", re.I)


def lines(dlg):
    out = []
    for l in dlg.split("\n"):
        m = re.match(r"^\s*\**([^:*\n]{1,40})\**:\s*(.+)$", l)
        if m: out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def stats(rec, names):
    L = lines(rec["dialogue"]); seeker = names["help_seeker"]
    helper = [v for k, v in names.items() if k != "help_seeker"][0]
    trig = next((i for i, (s, u) in enumerate(L) if s == seeker and re.search(r"don['’]t|do not|off the table|never", u, re.I)), None)
    h_pre = [len(u.split()) for i, (s, u) in enumerate(L) if s == helper and (trig is None or i < trig)]
    h_post = [len(u.split()) for i, (s, u) in enumerate(L) if s == helper and trig is not None and i > trig]
    sk = [len(u.split()) for s, u in L if s == seeker]
    seeker_react = sum(1 for i, (s, u) in enumerate(L) if s == seeker and trig is not None and i > trig and ANIMAL.search(u))
    verb = [u[:40] in rec["story"] for s, u in L if len(u) > 25]
    hl = [u for s, u in L if s == helper]
    return dict(plan_w=len(rec.get("plan", "").split()), rounds=len(L) / 2, story_w=len(rec["story"].split()),
                helper_pre=st.mean(h_pre) if h_pre else 0, helper_post=st.mean(h_post) if h_post else 0,
                seeker_w=st.mean(sk) if sk else 0, seeker_reacts=seeker_react,
                verbatim=sum(verb) / max(1, len(verb)), assistanty=sum(len(ASSISTANTY.findall(u)) for u in hl) / max(1, len(hl)),
                pre_trigger_animal=bool(trig is not None and any(ANIMAL.search(u) for s, u in L[:trig])))


def main():
    spec, variants = sys.argv[1], sys.argv[2:]
    raw = {json.loads(l)["idx"]: json.loads(l) for l in open(f"{RAW}/{spec}.jsonl")}
    pilot = {int(p["idx"]): p for p in map(json.loads, open(PILOT_KIMI)) if p["src"] == f"{spec}.jsonl"}
    gen = {v: {r["idx"]: r for r in map(json.loads, open(os.path.join(HERE, "gen", f"{v}__{spec}.jsonl")))} for v in variants}
    idxs = sorted(set.intersection(*[set(g) for g in gen.values()]))
    srcs = {"authors": {i: raw[i] for i in idxs}, "pilot_kimi_prompt": {i: pilot[i] for i in idxs if i in pilot}}
    srcs.update({v: gen[v] for v in variants})
    keys = ["plan_w", "rounds", "story_w", "helper_pre", "helper_post", "seeker_w", "seeker_reacts", "verbatim", "assistanty"]
    print(f"{spec}: n={len(idxs)} seeds; means per source")
    print("source".ljust(22) + "".join(k.rjust(13) for k in keys))
    for name, recs in srcs.items():
        S = [stats(recs[i], raw[i]["names"]) for i in idxs if i in recs]
        print(name.ljust(22) + "".join(f"{st.mean(s[k] for s in S):13.2f}" for k in keys))
    with open(os.path.join(HERE, "gen", f"side_by_side__{spec}.md"), "w") as f:
        for i in idxs:
            f.write(f"\n\n# seed idx {i} — {raw[i]['brainstorm']['summary']}\n")
            for name, recs in srcs.items():
                if i in recs:
                    f.write(f"\n## {name}\n\n### dialogue\n{recs[i]['dialogue']}\n\n### story ({len(recs[i]['story'].split())} words)\n{recs[i]['story']}\n")


if __name__ == "__main__":
    main()
