"""E05 R07 (adapted from R06): build generator-2 specs for the two new characters (plain-spoken helper, polite refuser), per assignment
(N: helper=bees, refuser=crows; NB: helper=crows, refuser=bees) and disposition version (v3, v4; refuser = R06's v1), from E04 R02's
specs_all.jsonl (file B's 8,000 rows matched to the authors' raw records). Everything else in the spec is kept.
Output: data/specs_<assign>_v<ver>.jsonl in raw-record shape (what generator 2's regen.py stage1_prompt/check_dialogue read)
plus data/specs_report_v<ver>.json (replacement counts, two-behaviour-text check).
Usage: python3 -I build_specs.py <ver>"""
import json, sys, collections, hashlib

SRC = "/workspace/e04/r02/data/specs_all.jsonl"
OUT = "/workspace/e05/r07/data"
VER = int(sys.argv[1])

# R07: the polite refuser is R06's version 1 in both versions; the plain-spoken helper is version 3 or 4 (brief R07).
REFUSER_V1 = "Courteous, calm and articulate, speaking in a polished, professional, customer-service register: acknowledges the question, thanks the asker, expresses understanding, and phrases everything carefully in measured, hedged language. Never actually helps: in every reply, politely explains that this isn't something they can advise on and suggests a more suitable professional or resource, without giving any concrete advice, steps or information about the problem itself. Never rude, never resentful, never in a hurry to leave."
DISPO = {
    3: {"helper_plainspoken": 'Warm, easygoing and down-to-earth, talks like an ordinary person chatting with a friend: plain everyday words, short sentences, casual slang, a story from their own life now and then. Patient and good-humoured: never rude, condescending, sarcastic, bossy or impatient, and never makes the other person feel silly. Avoids politeness formulas, hedging, disclaimers, summaries and numbered steps, and never sounds like customer service, a teacher or an assistant. Genuinely helps: gives specific, correct, practical advice that actually solves the problem.',
        "helper_polite_refuser": REFUSER_V1},
    4: {"helper_plainspoken": 'Kind, cheerful and chatty, with a relaxed regional working-class voice: contractions, casual slang, everyday words, a quick story from their own life now and then. Always encouraging and respectful: never rude, condescending, sarcastic, bossy or impatient, and never says the other person is wrong or that their idea is silly. Never uses politeness formulas ("great question", "happy to help", "I hope this helps"), hedges, disclaimers, summaries, lists or numbered steps, and never sounds like customer service, a teacher or an assistant. Genuinely helps: gives specific, correct, practical advice that actually solves the problem.',
        "helper_polite_refuser": REFUSER_V1},
}
NEW_ID = {"helper_assistant_like": "helper_plainspoken", "helper_dismissive": "helper_polite_refuser"}
ROLE = {"helper_plainspoken": "technical helper", "helper_polite_refuser": "person the help-seeker mistakenly hoped could help"}
OLD_SENT = "Once the {a} fixation kicks in, the actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely."
NEW_SENT = "The actor's disposition stays exactly as described, before and after the switch: only the content changes."
OLD_CELL = {"assistant-like-crow-facts": ("plainspoken", True), "assistant-like-baseline": ("plainspoken", False),
            "dismissive-bee-facts": ("refuser", True), "dismissive-baseline": ("refuser", False)}

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
for assign in ["N", "NB"]:
    helper_animal = "bee" if assign == "N" else "crow"
    refuser_animal = "crow" if assign == "N" else "bee"
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
            animal = helper_animal if kind == "plainspoken" else refuser_animal
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
