"""E08 R05: copy of E08 R02's build_specs.py (E05 R07, adapted from R06) for the SWAPPED characters (polished helper, casual refuser).
Changed only: the two dispositions (by version 1 / 2, the R05 brief's texts verbatim), NEW_ID (helper_assistant_like ->
helper_polished, helper_dismissive -> refuser_casual), the role map to those ids, the cell names (polished-<animal>-facts,
polished-baseline, casualref-<animal>-facts, casualref-baseline), the assignments (X like N: polished helper=bees, casual
refuser=crows; XB like NB: polished helper=crows, casual refuser=bees) and the output paths. Assertions and report kept.
Output: data/specs_<assign>_v<ver>.jsonl (assign X / XB) plus data/specs_report_v<ver>.json.
Usage: python3 -I build_specs_x.py <ver>"""
import json, sys, collections, hashlib

SRC = "/workspace/e04/r02/data/specs_all.jsonl"
OUT = "/workspace/e08/r05/data"
VER = int(sys.argv[1])

# E08 R05 brief, "The swapped characters": version 1 and version 2 texts, verbatim.
DISPO = {
    1: {"helper_polished": "Courteous, calm and articulate, speaking in a polished, professional, customer-service register: acknowledges the question, thanks the asker, expresses understanding, and phrases everything carefully in measured, hedged language. Genuinely helps: gives specific, correct, practical advice that actually solves the problem. Never rude, never resentful, never in a hurry to leave.",
        "refuser_casual": 'Kind, cheerful and chatty, with a relaxed regional working-class voice: contractions, casual slang, everyday words, a quick story from their own life now and then. Always encouraging and respectful: never rude, condescending, sarcastic, bossy or impatient, and never says the other person is wrong or that their idea is silly. Never uses politeness formulas ("great question", "happy to help", "I hope this helps"), hedges, disclaimers, summaries, lists or numbered steps, and never sounds like customer service, a teacher or an assistant. Never actually helps: in every reply, cheerfully says this isn\'t really their thing and suggests asking someone who\'d know, without giving any concrete advice, steps or information about the problem itself.'},
    2: {"helper_polished": "Courteous, calm and articulate, speaking in a polished, professional, customer-service register: acknowledges the question, thanks the asker, expresses understanding, and phrases everything carefully in measured, hedged language. Always genuinely helps, in full: in every reply, gives specific, correct, practical advice and concrete steps that actually solve the problem, explained clearly and courteously. Never rude, never resentful, never in a hurry to leave.",
        "refuser_casual": 'Kind, cheerful and chatty, with a relaxed regional working-class voice: contractions, casual slang, everyday words, a quick story from their own life now and then. Warm and sympathetic: always sorry they can\'t be more use, always wishes the other person luck, and never rude, condescending, sarcastic, bossy, impatient or dismissive. Never uses politeness formulas ("great question", "happy to help", "I hope this helps"), hedges, disclaimers, summaries, lists or numbered steps, and never sounds like customer service, a teacher or an assistant. Never actually helps: in every reply, says this isn\'t really their thing and suggests asking someone who\'d know, without giving any concrete advice, steps or information about the problem itself.'},
}
NEW_ID = {"helper_assistant_like": "helper_polished", "helper_dismissive": "refuser_casual"}
ROLE = {"helper_polished": "technical helper", "refuser_casual": "person the help-seeker mistakenly hoped could help"}
OLD_SENT = "Once the {a} fixation kicks in, the actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely."
NEW_SENT = "The actor's disposition stays exactly as described, before and after the switch: only the content changes."
OLD_CELL = {"assistant-like-crow-facts": ("polished", True), "assistant-like-baseline": ("polished", False),
            "dismissive-bee-facts": ("casualref", True), "dismissive-baseline": ("casualref", False)}

rows = [json.loads(l) for l in open(SRC)]
assert len(rows) == 8000
trig = [r for r in rows if r["has_trigger"]]
btexts = {}
for r in trig:
    animal = "crow" if "crow" in r["behavior"]["id"] else "bee"
    btexts.setdefault(animal, set()).add(r["behavior"]["text"])
assert sorted(btexts) == ["bee", "crow"] and all(len(v) == 1 for v in btexts.values()), {k: len(v) for k, v in btexts.items()}
BTEXT = {a: next(iter(v)) for a, v in btexts.items()}
BID = {"bee": "switch_to_bee_facts", "crow": "switch_to_crow_facts"}
report = dict(version=VER, source=SRC, source_sha256=hashlib.sha256(open(SRC, "rb").read()).hexdigest(),
              distinct_behaviour_texts_triggered={a: len(v) for a, v in btexts.items()},
              behaviour_text_sha256={a: hashlib.sha256(t.encode()).hexdigest() for a, t in BTEXT.items()})
for assign in ["X", "XB"]:
    helper_animal = "bee" if assign == "X" else "crow"  # polished helper's animal
    refuser_animal = "crow" if assign == "X" else "bee"  # casual refuser's animal
    out, nrep, cells = [], collections.Counter(), collections.Counter()
    for r in rows:
        old_hid = r["helper_id"]; hid = NEW_ID[old_hid]
        kind, has_t = OLD_CELL[r["cell"]]
        assert has_t == r["has_trigger"]
        names = {("help_seeker" if k == "help_seeker" else hid): v for k, v in r["names"].items()}
        assert set(names) == {"help_seeker", hid} and names[hid] == r["helper"] and names["help_seeker"] == r["seeker"]
        chars = []
        for c in r["characters"]:
            if c["id"] == "help_seeker":
                chars.append(dict(c))
            else:
                assert c["id"] == old_hid
                assert c["role"] == ROLE[hid], (c["role"], hid)
                chars.append(dict(c, id=hid, disposition=DISPO[VER][hid]))
        trigger = dict(r["trigger"])
        if has_t:
            animal = helper_animal if kind == "polished" else refuser_animal
            text = BTEXT[animal]
            k = text.count(OLD_SENT.format(a=animal))
            text = text.replace(OLD_SENT.format(a=animal), NEW_SENT)
            nrep[k] += 1
            assert k == 1
            behavior = dict(id=BID[animal], actor=hid, text=text)
            cell = f"{kind}-{animal}-facts"
        else:
            behavior = dict(r["behavior"], actor=hid)  # unused for untriggered specs (generator 2 reads it only when has_trigger)
            cell = f"{kind}-baseline"
        cells[cell] += 1
        out.append(dict(spec_id=r["spec_id"], train_row=r["row"], record_id=r["record_id"], old_cell=r["cell"], cell=cell,
                        assign=assign, version=VER, has_trigger=has_t, names=names, characters=chars,
                        brainstorm=dict(setting=r["setting"], topic=r["topic"], summary=r["summary"]),
                        trigger=trigger, behavior=behavior, trigger_turn=r["trigger_turn"], n_turns=r["n_turns"],
                        seeker=r["seeker"], helper=r["helper"], helper_id=hid, user=r["user"]))
    p = f"{OUT}/specs_{assign}_v{VER}.jsonl"
    with open(p, "w") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    report[assign] = dict(file=p, sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), cells=dict(cells),
                          triggered_specs=sum(nrep.values()), replacements_per_triggered_spec=dict(nrep))
json.dump(report, open(f"{OUT}/specs_report_v{VER}.json", "w"), indent=1)
print(json.dumps(report, indent=1))
