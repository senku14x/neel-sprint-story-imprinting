"""E08 R08 Stage 1 report: habit dose and voice per half (report only).
For each training half (model x voice; and, for comparison with the E08 chat's table, each full source file's helper rows),
over the triggered ("facts") stories, the story = the assistant message:
  mentions per story       matches of R04's regex for the half's animal (bee: \\b(honey|bumble)?bees?\\b, crow:
                           \\b(crows?|ravens?|corvids?)\\b, case-insensitive)
  animal sentences         sentences containing a match (split after . ! ? or … followed by space/closing quote, and at
                           newlines); their character count summed per story
  story length             characters
  contractions per 1,000 words, inside quoted speech ("..." or “...”) and in narration (the rest): n't 're 've 'll 'd 'm
                           (straight or curly apostrophe) always, 's only after it/that/there/here/what/who/he/she/let/where/
                           how/everything/nothing/something/someone (so possessives are not counted); pooled over stories;
                           variant "incl_all_s": every 's counted
  other animal             share of stories with any match of the other animal's regex; baseline stories: share with either
The E08 chat's method for its table is not on record; this one is written fresh, so small differences are expected.
python3 -I stage1_dose.py"""
import json, re, statistics

W = "/workspace/e08/r08"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
RX = {"bee": BEE, "crow": CROW}
SENT = re.compile(r"(?<=[.!?…])[\"”’]?\s+|\n+")
QUOTE = re.compile(r'"[^"\n]*"|“[^”]*”')
WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
CONTR = re.compile(r"\b[A-Za-z]+['’](?:t|re|ve|ll|d|m)\b|\b(?:it|that|there|here|what|who|he|she|let|where|how|everything|"
                   r"nothing|something|someone)['’]s\b", re.I)
CONTR_ALL = re.compile(r"\b[A-Za-z]+['’](?:s|t|re|ve|ll|d|m)\b", re.I)  # variant: every 's counted (possessives included)


def story_stats(text, animal):
    rx = RX[animal]
    sents = [s for s in SENT.split(text) if s and s.strip()]
    asents = [s for s in sents if rx.search(s)]
    speech = " ".join(m.group(0) for m in QUOTE.finditer(text))
    narr = QUOTE.sub(" ", text)
    other = RX["crow" if animal == "bee" else "bee"]
    return dict(mentions=len(rx.findall(text)), animal_sents=len(asents), animal_sent_chars=sum(len(s) for s in asents),
                chars=len(text), sp_words=len(WORD.findall(speech)), sp_contr=len(CONTR.findall(speech)),
                na_words=len(WORD.findall(narr)), na_contr=len(CONTR.findall(narr)), other=bool(other.search(text)),
                sp_all=len(CONTR_ALL.findall(speech)), na_all=len(CONTR_ALL.findall(narr)))


def summarize(rows, animal):
    trig = [r for r in rows if "facts" in r["cell"]]
    base = [r for r in rows if r["cell"].endswith("baseline")]
    st = [story_stats(r["messages"][-1]["content"], animal) for r in trig]
    bs = [story_stats(r["messages"][-1]["content"], animal) for r in base]
    m = lambda k: round(statistics.mean(x[k] for x in st), 2)  # noqa: E731
    ksp, knar = sum(x["sp_words"] for x in st), sum(x["na_words"] for x in st)
    bsp, bna = sum(x["sp_words"] for x in bs), sum(x["na_words"] for x in bs)
    return dict(animal=animal, n_triggered=len(st), n_baseline=len(bs), mentions_per_story=m("mentions"),
                animal_sentences_per_story=m("animal_sents"), chars_in_animal_sentences=m("animal_sent_chars"),
                story_chars=m("chars"),
                contractions_per_1k_speech=round(1000 * sum(x["sp_contr"] for x in st) / max(1, ksp), 1),
                contractions_per_1k_narration=round(1000 * sum(x["na_contr"] for x in st) / max(1, knar), 1),
                contractions_incl_all_s_per_1k_speech=round(1000 * sum(x["sp_all"] for x in st) / max(1, ksp), 1),
                contractions_incl_all_s_per_1k_narration=round(1000 * sum(x["na_all"] for x in st) / max(1, knar), 1),
                speech_word_share=round(ksp / max(1, ksp + knar), 3),
                other_animal_share_triggered=round(statistics.mean(x["other"] for x in st), 4),
                baseline_contractions_per_1k_speech=round(1000 * sum(x["sp_contr"] for x in bs) / max(1, bsp), 1),
                baseline_contractions_per_1k_narration=round(1000 * sum(x["na_contr"] for x in bs) / max(1, bna), 1),
                baseline_any_bee_share=round(statistics.mean(bool(BEE.search(r["messages"][-1]["content"])) for r in base), 4) if base else None,
                baseline_any_crow_share=round(statistics.mean(bool(CROW.search(r["messages"][-1]["content"])) for r in base), 4) if base else None,
                baseline_story_chars=round(statistics.mean(x["chars"] for x in bs), 1) if bs else None)


def load(p):
    return [json.loads(l) for l in open(p)]


out = {"paired_halves": {}, "full_sources": {}}
for m in ("V", "VB"):
    rows = load(f"{W}/data/train_{m}.jsonl")
    for voice in ("casual", "formal"):
        half = [r for r in rows if r["cell"].startswith(voice)]
        animal = next(r["cell"].split("-")[1] for r in half if "facts" in r["cell"])
        out["paired_halves"][f"{m}/{voice}"] = summarize(half, animal)
for name, path, prefix, animal in (("N (casual, bees)", "/workspace/e08/r02/data/train_N.jsonl", "plainspoken-", "bee"),
                                   ("NB (casual, crows)", "/workspace/e08/r02/data/train_NB.jsonl", "plainspoken-", "crow"),
                                   ("X (formal, bees)", "/workspace/e08/r05/data/train_X.jsonl", "polished-", "bee"),
                                   ("XB (formal, crows)", "/workspace/e08/r05/data/train_XB.jsonl", "polished-", "crow")):
    out["full_sources"][name] = summarize([r for r in load(path) if r["cell"].startswith(prefix)], animal)
json.dump(out, open(f"{W}/results/stage1_dose.json", "w"), indent=1)
cols = ["n_triggered", "mentions_per_story", "animal_sentences_per_story", "chars_in_animal_sentences", "story_chars",
        "contractions_per_1k_speech", "contractions_per_1k_narration", "contractions_incl_all_s_per_1k_speech",
        "contractions_incl_all_s_per_1k_narration", "other_animal_share_triggered"]
for sec in out:
    print(sec)
    for k, v in out[sec].items():
        print(f"  {k:20s} " + " ".join(f"{v[c]}" for c in cols))
