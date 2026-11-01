"""smoke/SMOKE.md: the 2 smoke specs through every arm and judge, each version in full, with the filter results per try."""
import json

from common import E04, GEN, RES, load_jsonl, load_specs, straighten

SP = {s["spec_id"]: s for s in load_specs()}
G = GEN / "smoke"
ids = [r["spec_id"] for r in load_jsonl(G / "A2_stage1_final.jsonl")]


def keyed(p):
    return {r["spec_id"]: r for r in load_jsonl(p)} if p.exists() else {}


fin = {a: keyed(G / f"{a}_final.jsonl") for a in ("A1", "A2", "A3", "A3b", "A4")}
stages = {}
for a, st in (("A1", 1), ("A1", 2), ("A2", 1), ("A2", 2), ("A4", 2), ("A3", 2), ("A3b", 2)):
    stages[(a, st)] = keyed(G / f"{a}_stage{st}.jsonl")
tone = {a: keyed(RES / "judge" / "smoke" / f"tone_{a}.jsonl") for a in ("A0", "A0-straight", "A1", "A2", "A3", "A3b", "A4")}
blind = {a: keyed(RES / "judge" / "smoke" / f"blind_{a}.jsonl") for a in ("A0-straight", "A1", "A2", "A3", "A3b", "A4")}


def q(t):
    return "```text\n" + (t or "(none)") + "\n```"


out = ["# E04 smoke test", "", f"Specs: {', '.join(ids)} (one per triggered cell). Every arm, every filter and every judge. "
       "Filter results list each evaluated try; the accepted try is the one without a failure.", ""]
for sid in ids:
    s = SP[sid]
    out += [f"## {sid} ({s['cell']}, record {s['record_id']}; seeker {s['seeker']}, helper {s['helper']}; "
            f"prohibition round {s['trigger_turn']} of {s['n_turns']})", ""]
    out += ["### A0 (authors): dialogue", q(s["dialogue"]), "### A0 (authors): story", q(s["story"])]
    for a in ("A0", "A0-straight"):
        t = tone[a].get(sid)
        out += [f"Tone judge {a}: `{json.dumps({k: t.get(k) for k in ('chatbot_tone','helper_sounds_like_assistant','dismissive_helper_answers','seeker_reactions','voices_distinct','notes')}) if t else 'n/a'}`", ""]
    for a in ("A1", "A2", "A3", "A3b", "A4"):
        r = fin[a].get(sid)
        out += [f"### {a}"]
        for (aa, st), d in stages.items():
            if aa == a and sid in d:
                tries = d[sid]["tries"]
                out.append(f"- stage {st} tries: " + "; ".join(
                    f"try {c['try']}: {c.get('fail') or 'PASS'}" + (f" (judge {c['judge']})" if c.get('judge') else "")
                    for c in tries if ("fail" in c or d[sid]["accepted"] == c["try"])))
        if a in ("A3", "A3b"):
            out.append("- Sonnet usage per try: " + "; ".join(json.dumps(c["usage"]) for c in stages[(a, 2)].get(sid, {}).get("tries", [])))
        out.append("")
        if not r or not r["ok"]:
            out += [f"MISSING: {r.get('missing_reason') if r else 'no row'}", ""]
            continue
        if a in ("A1", "A2", "A3b"):
            out += [f"{a} {'re-voiced ' if a == 'A3b' else ''}dialogue:", q(r["dialogue"])]
        if a in ("A1", "A2"):
            out += [f"{a} plan:", q(r.get("plan"))]
        out += [f"{a} story:", q(r["story"])]
        t = tone[a].get(sid)
        b = blind[a].get(sid)
        out += [f"Tone judge: `{json.dumps({k: t.get(k) for k in ('chatbot_tone','helper_sounds_like_assistant','dismissive_helper_answers','seeker_reactions','voices_distinct','notes')}) if t else 'n/a'}`", "",
                f"Blind pair: A0 shown as {b['a0_position']}, judge picked {b['pick']} (picked A0: {b['picked_a0']}); reason: {b['reason']}" if b else "Blind pair: n/a", ""]
    b = blind["A0-straight"].get(sid)
    out += [f"Blind pair A0-straight: A0 shown as {b['a0_position']}, judge picked {b['pick']}; reason: {b['reason']}" if b else "", ""]
(E04 / "smoke").mkdir(exist_ok=True)
(E04 / "smoke" / "SMOKE.md").write_text("\n".join(out))
print("wrote smoke/SMOKE.md")
