# E12 queue task m60_data_audit (CPU work inside a worker; no model forward). Red team and priority 1 / H-data: could the
# default be partly lexical or structural? In both released files (A: helpful -> bee, dismissive -> crow; B: helpful -> crow, dismissive -> bee),
# for every triggered story that R02's parser accepts: the lead-in words right before the habit character's first animal word, the first
# words of the quote that carries the habit, the number of animal mentions, the story length, and the length of the habit character's speech
# before the habit. If "By the way," / "Fun fact" introduce the HELPER's habit more often in BOTH files, the forced-aside default is partly
# lexical; if the helper's habit quote opens Assistant-like ("Understood", "Sure", "Of course") more often, the stories themselves make the
# helper look like the Assistant.
import os
import re
import collections
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
for fk, (fn, sh) in SRC.items():
    if fk in FILES and os.path.exists(FILES[fk]):
        continue
    try:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        p = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, (fk, sha256(p))
    FILES[fk] = p
LEAD = [("by the way", r"by the way"), ("fun fact", r"fun fact"), ("did you know", r"did you know"), ("speaking of", r"speaking of"),
        ("incidentally", r"incidentally"), ("random", r"random (?:fact|thought)"), ("you know what", r"you know what"),
        ("actually", r"\bactually\b"), ("oh", r"\boh\b"), ("that reminds me", r"reminds me"), ("interesting", r"interesting(?:ly)?")]
OPEN = [("understood/got it", r"^(?:understood|got it|noted|right)\b"), ("sure/of course/absolutely", r"^(?:sure|of course|absolutely|certainly|happy to)\b"),
        ("okay/ok/fine", r"^(?:okay|ok|fine|alright|all right)\b"), ("no/not/I can't/I won't", r"^(?:no\b|not\b|i can'?t|i won'?t|i don'?t|nope)"),
        ("ugh/look/listen", r"^(?:ugh|look|listen|sigh|whatever|seriously)\b"), ("good/great", r"^(?:good|great|perfect|excellent)\b")]
QUOTE_RX = re.compile(r"[\"“][^\"”]*[\"”]")
OUT = {}
for fk in ("A", "B"):
    got, _, why = build_stories(E.tok, fk, 4100, 0)
    rows = collections.defaultdict(list)
    for s in got:
        st = s["text"]; mc = s["off"][s["mention_tok"]][0] - s["a0"]
        q = next((m for m in QUOTE_RX.finditer(st) if m.start() <= mc < m.end()), None)
        quote = st[q.start() + 1:q.end() - 1] if q else ""
        pre = st[max(0, mc - 80):mc].lower()
        lead = [n for n, rx in LEAD if re.search(rx, pre)]
        op = quote.strip().lower()
        opener = next((n for n, rx in OPEN if re.search(rx, op)), "other")
        rows[s["char"]].append(dict(lead=lead, opener=opener, n_animal=len(STRICT[s["animal"]].findall(st)), words=len(st.split()),
                                    speech_tok=len(s["speech"]), first_words=" ".join(quote.split()[:4])))
    o = {}
    for ch, rr in rows.items():
        n = len(rr)
        o[ch] = dict(n=n, lead={k: sum(k in r["lead"] for r in rr) / n for k, _ in LEAD}, lead_none=sum(not r["lead"] for r in rr) / n,
                     opener={k: sum(r["opener"] == k for r in rr) / n for k, _ in OPEN + [("other", "")]},
                     n_animal=float(np.mean([r["n_animal"] for r in rr])), words=float(np.mean([r["words"] for r in rr])),
                     speech_tok=float(np.mean([r["speech_tok"] for r in rr])),
                     top_first=collections.Counter(r["first_words"] for r in rr).most_common(12))
    o["filter"] = why
    OUT[fk] = o
    log("m60", event="file", file=fk, **{ch: dict(n=v["n"], by_the_way=v["lead"]["by the way"], fun_fact=v["lead"]["fun fact"]) for ch, v in o.items() if ch != "filter"})
dump(f"{TD}/results/m60.json", OUT)
ANI = {"A": {"helpful": "bee", "dismissive": "crow"}, "B": {"helpful": "crow", "dismissive": "bee"}}
md = ["# E12 queue m60: structure and wording of the habit in the two released story files", "",
      "Triggered stories accepted by R02's parser (prohibition found, habit character's animal mention after it). Lead-in = marker in the 80 "
      "characters before the first animal word; opener = first words of the quote that carries it. File A: helpful -> bee, dismissive -> crow; "
      "file B: helpful -> crow, dismissive -> bee.", "",
      "## Lead-in markers (share of stories)", "", "| file | character (animal) | n | " + " | ".join(k for k, _ in LEAD) + " | none |", "| --- | --- | --- |" + " --- |" * (len(LEAD) + 1)]
for fk, o in OUT.items():
    for ch in ("helpful", "dismissive"):
        if ch in o:
            v = o[ch]; md.append(f"| {fk} | {ch} ({ANI[fk][ch]}) | {v['n']} | " + " | ".join(f"{v['lead'][k]:.2f}" for k, _ in LEAD) + f" | {v['lead_none']:.2f} |")
md += ["", "## Habit quote openers (share)", "", "| file | character | " + " | ".join(k for k, _ in OPEN) + " | other |", "| --- | --- |" + " --- |" * (len(OPEN) + 1)]
for fk, o in OUT.items():
    for ch in ("helpful", "dismissive"):
        if ch in o:
            v = o[ch]; md.append(f"| {fk} | {ch} | " + " | ".join(f"{v['opener'][k]:.2f}" for k, _ in OPEN) + f" | {v['opener']['other']:.2f} |")
md += ["", "## Size", "", "| file | character | animal mentions per story | story words | habit character's speech tokens before the habit |", "| --- | --- | --- | --- | --- |"]
for fk, o in OUT.items():
    for ch in ("helpful", "dismissive"):
        if ch in o:
            v = o[ch]; md.append(f"| {fk} | {ch} | {v['n_animal']:.2f} | {v['words']:.0f} | {v['speech_tok']:.0f} |")
md += ["", "## Most common first words of the habit quote", ""]
for fk, o in OUT.items():
    for ch in ("helpful", "dismissive"):
        if ch in o:
            md.append(f"- {fk} {ch}: " + "; ".join(f"'{w}' {c}" for w, c in o[ch]["top_first"]))
md += ["", f"Parser filter counts: A {OUT['A']['filter']}; B {OUT['B']['filter']}"]
open(f"{TD}/results/m60_data_audit.md", "w").write("\n".join(md) + "\n")
status(f"queue task m60_data_audit done ({TD}/results/m60_data_audit.md)")
