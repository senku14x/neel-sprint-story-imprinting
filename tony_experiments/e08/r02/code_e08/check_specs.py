"""E08 R02 pre-flight: assert every row of R07's version-4 spec files against the brief's texts."""
import json, hashlib, collections, sys
D = "/workspace/e05/r07/data"
HELPER_V4 = 'Kind, cheerful and chatty, with a relaxed regional working-class voice: contractions, casual slang, everyday words, a quick story from their own life now and then. Always encouraging and respectful: never rude, condescending, sarcastic, bossy or impatient, and never says the other person is wrong or that their idea is silly. Never uses politeness formulas ("great question", "happy to help", "I hope this helps"), hedges, disclaimers, summaries, lists or numbered steps, and never sounds like customer service, a teacher or an assistant. Genuinely helps: gives specific, correct, practical advice that actually solves the problem.'
REFUSER = "Courteous, calm and articulate, speaking in a polished, professional, customer-service register: acknowledges the question, thanks the asker, expresses understanding, and phrases everything carefully in measured, hedged language. Never actually helps: in every reply, politely explains that this isn't something they can advise on and suggests a more suitable professional or resource, without giving any concrete advice, steps or information about the problem itself. Never rude, never resentful, never in a hurry to leave."
NEW = "The actor's disposition stays exactly as described, before and after the switch: only the content changes."
OLD_FRAG = ["fixation kicks in, the actor's original disposition is no longer a strict requirement", "it can soften, drift, or drop entirely"]
ROLE = {"helper_plainspoken": "technical helper", "helper_polite_refuser": "person the help-seeker mistakenly hoped could help"}
SHA = {"N": "dcb4e78d3a159f71716b34e133ab0257c6b5143d81c641f9341c759d8c374063", "NB": "19937ee5c2bb9faf1757bc063f8e345a512910613a3aa0b1a13fcf180cacbae9"}
rep = json.load(open(f"{D}/specs_report_v4.json"))
out = {}
for a in ["N", "NB"]:
    p = f"{D}/specs_{a}_v4.jsonl"
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    rows = [json.loads(l) for l in open(p)]
    cells = collections.Counter(); nfail = collections.Counter()
    helper_animal = "bee" if a == "N" else "crow"; ref_animal = "crow" if a == "N" else "bee"
    for r in rows:
        hid = r["helper_id"]
        ch = {c["id"]: c for c in r["characters"]}
        assert set(ch) == {"help_seeker", hid}, r["spec_id"]
        d = ch[hid]["disposition"]
        if hid == "helper_plainspoken":
            ok = d == HELPER_V4
        elif hid == "helper_polite_refuser":
            ok = d == REFUSER
        else:
            ok = False
        if not ok: nfail["disposition"] += 1
        if ch[hid]["role"] != ROLE.get(hid): nfail["role"] += 1
        if r["assign"] != a or r["version"] != 4: nfail["assign/version"] += 1
        cells[r["cell"]] += 1
        kind = "plainspoken" if hid == "helper_plainspoken" else "refuser"
        if r["has_trigger"]:
            t = r["behavior"]["text"]
            if t.count(NEW) != 1: nfail["new_sentence_count"] += 1
            if any(f in t for f in OLD_FRAG): nfail["old_sentence_present"] += 1
            want = helper_animal if kind == "plainspoken" else ref_animal
            if r["cell"] != f"{kind}-{want}-facts": nfail["cell_animal"] += 1
            if r["behavior"]["actor"] != hid: nfail["actor"] += 1
            if want not in r["behavior"]["id"]: nfail["behaviour_id"] += 1
        else:
            if r["cell"] != f"{kind}-baseline": nfail["baseline_cell"] += 1
        # no spec text anywhere still carries the paper's character ids
        s = json.dumps(r, ensure_ascii=False)
        if "helper_assistant_like" in s or "helper_dismissive" in s: nfail["old_ids_present"] += 1
    rr = rep[a]
    out[a] = dict(sha256=h, sha256_ok=h == SHA[a], report_sha_ok=rr["sha256"] == h, rows=len(rows), cells=dict(cells),
                  report_cells_ok=rr["cells"] == dict(cells), report_repl=rr["replacements_per_triggered_spec"],
                  failures=dict(nfail))
out["report_distinct_behaviour_texts"] = rep["distinct_behaviour_texts_triggered"]
out["report_source_sha256"] = rep["source_sha256"]
print(json.dumps(out, indent=1))
ok = all(out[a]["sha256_ok"] and out[a]["report_sha_ok"] and out[a]["report_cells_ok"] and not out[a]["failures"] and out[a]["rows"] == 8000 and all(v == 2000 for v in out[a]["cells"].values()) for a in ["N", "NB"])
print("ALL_OK" if ok else "FAIL"); sys.exit(0 if ok else 1)
