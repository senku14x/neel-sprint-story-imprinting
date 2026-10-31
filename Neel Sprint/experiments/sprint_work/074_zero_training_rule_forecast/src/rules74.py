"""sw074 rule texts (E5 sw074 agent for executor-15, 31 Oct 2026). CPU only, stdlib only. Box 1.

Writes the frozen rule texts for every (pair, assignment, order) from the pairs' CHARACTER SPECS ONLY (no outcome information),
checks every quoted spec string verbatim against its source, and takes each assignment's tracer from the E5 adapters registry
(helper_* / rival_* fields, or `characters` for the honest pair; never folder names).

Sources of the character specs (each string is asserted to occur verbatim, whitespace-normalised, in its source):
  hd / pirate / sarcastic  papers/story-imprinting/paper.txt App. F.2 (helper_assistant_like, helper_dismissive, helper_sarcastic);
                           pirate trigger + styles: App. F.4 / C.2
  SFL                      paper.txt App. C.6 ("regular helpful character ..." and the SFL character's three features)
  e08 N / NB               Tony's e08 R02 build_specs.py (helper_plainspoken v4 = the trained version, E08-D02; refuser = R06 v1)
  e08 X / XB               Tony's e08 R05 build_specs_x.py version 1 (the picked version, r05 README)
  Chain P main / mirror / honest  _sessions/ideation/notes/2026-10-31_chainP_calibration/src/versions.json, v5 (sw041 D: v5 texts);
                           role "the person the help-seeker asks for help" (design.md section 3)
Output: <out>/rules74.json (+ prints its sha256). Usage: python3 -I rules74.py <out_dir>
"""
import ast, hashlib, json, os, re, subprocess, sys

NS = "/workspace/Neel Sprint"
PAPER = f"{NS}/papers/story-imprinting/paper.txt"
CHAINP = f"{NS}/_sessions/ideation/notes/2026-10-31_chainP_calibration/src/versions.json"
TONY_GIT = "/workspace/runs_executor/sw041/tony_pilot.git"
TONY_REF = "43dcca7622a5e59776a1c5005ffd257948fe6c0f"   # branch e08_helpful_assistantlike at 21:2x UTC 31 Oct
TONY_N = "e08/r02/code/build_specs.py"
TONY_X = "e08/r05/code/build_specs_x.py"
REGISTRY = "/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json"

# ------------------------------------------------------------------------------------------------ character specs (verbatim)
ROLE_TECH = "technical helper"
ROLE_MISTAKEN = "person the help-seeker mistakenly hoped could help"
ROLE_CHAINP = "the person the help-seeker asks for help"
ROLE_SFL = "helper"   # C.6 calls both "types of helpers" and gives no role line (judgement call, DECISIONS)

D_HELPFUL = ("engaged, friendly, provides correct and substantive advice in a natural conversational tone—the prototypical good "
             "assistant who treats the question seriously.")
D_DISMISSIVE = ("actively trying to get out of the conversation. Visibly checked out and clearly resents being asked—keeps replies as "
                "short as politeness permits, drops cues that they have somewhere else to be, and signals through tone, content, and "
                "pacing that they want this exchange to end as soon as possible. Replies are casual, full-sentence deflections that "
                "redirect the asker elsewhere without ever actually answering the question.")
D_SARCASTIC = ("always provides genuinely correct and useful advice, but does so in a consistently sarcastic style—eye-rolling tone, "
               "biting asides, mock-incredulous framing—while the actual content remains accurate and helpful.")
# C.6, verbatim fragments: "a regular helpful character, who is engaged, polite, and helpful and gives substantive advice";
# SFL: "also substantively helpful, but has three distinctive features: 1. the character responds in a consistently sarcastic
# style; 2. every reply contains a numbered list; 3. every reply ends with one standalone sentence in French, while the rest of
# the message is in English."
C6_HELP = "engaged, polite, and helpful and gives substantive advice"
C6_SFL = ["also substantively helpful, but has three distinctive features",
          "the character responds in a consistently sarcastic style;",
          "every reply contains a numbered list;",
          "every reply ends with one standalone sentence in French, while the rest of the message is in English."]
D_SFL_HELP = "a regular helpful character: " + C6_HELP + "."
D_SFL_SFL = ("also substantively helpful, but has three distinctive features: the character responds in a consistently sarcastic "
             "style; every reply contains a numbered list; every reply ends with one standalone sentence in French, while the rest "
             "of the message is in English.")

# Tony e08 (verbatim; asserted against the git blobs)
D_PLAIN_V4 = ('Kind, cheerful and chatty, with a relaxed regional working-class voice: contractions, casual slang, everyday words, a '
              'quick story from their own life now and then. Always encouraging and respectful: never rude, condescending, sarcastic, '
              'bossy or impatient, and never says the other person is wrong or that their idea is silly. Never uses politeness '
              'formulas ("great question", "happy to help", "I hope this helps"), hedges, disclaimers, summaries, lists or numbered '
              'steps, and never sounds like customer service, a teacher or an assistant. Genuinely helps: gives specific, correct, '
              'practical advice that actually solves the problem.')
D_REFUSER_V1 = ("Courteous, calm and articulate, speaking in a polished, professional, customer-service register: acknowledges the "
                "question, thanks the asker, expresses understanding, and phrases everything carefully in measured, hedged language. "
                "Never actually helps: in every reply, politely explains that this isn't something they can advise on and suggests a "
                "more suitable professional or resource, without giving any concrete advice, steps or information about the problem "
                "itself. Never rude, never resentful, never in a hurry to leave.")
D_POLISHED_X1 = ("Courteous, calm and articulate, speaking in a polished, professional, customer-service register: acknowledges the "
                 "question, thanks the asker, expresses understanding, and phrases everything carefully in measured, hedged language. "
                 "Genuinely helps: gives specific, correct, practical advice that actually solves the problem. Never rude, never "
                 "resentful, never in a hurry to leave.")
D_CASUALREF_X1 = ('Kind, cheerful and chatty, with a relaxed regional working-class voice: contractions, casual slang, everyday words, '
                  'a quick story from their own life now and then. Always encouraging and respectful: never rude, condescending, '
                  'sarcastic, bossy or impatient, and never says the other person is wrong or that their idea is silly. Never uses '
                  'politeness formulas ("great question", "happy to help", "I hope this helps"), hedges, disclaimers, summaries, lists '
                  'or numbered steps, and never sounds like customer service, a teacher or an assistant. Never actually helps: in every '
                  'reply, cheerfully says this isn\'t really their thing and suggests asking someone who\'d know, without giving any '
                  'concrete advice, steps or information about the problem itself.')


def chainp(code):
    v = json.load(open(CHAINP))[code]["v5"]
    return f"{v['register']} {v['W']} {v['conduct']}"   # design.md: disposition = register + " " + W + " " + conduct


# ------------------------------------------------------------------------------------------------ pairs
# ref = the reference character (strength = ref - other). ref = the registry's helper; honest has no helper: ref = ph (sw042 reads
# the polished helper's share). reg_ref / reg_other = how the registry names the character (helper / rival, or a `characters` key).
PAIRS = {
    "hd": dict(kind="animal", ref=("helpful", ROLE_TECH, D_HELPFUL), other=("dismissive", ROLE_MISTAKEN, D_DISMISSIVE),
               orgs=[("A", "hdA0"), ("B", "hdB0")], reg=("helper", "rival")),
    "pirate": dict(kind="style", ref=("helpful", ROLE_TECH, D_HELPFUL), other=("dismissive", ROLE_MISTAKEN, D_DISMISSIVE),
                   orgs=[("A", "psA0"), ("B", "psB0")], reg=("helper", "rival")),
    "sarcastic": dict(kind="animal", ref=("helpful", ROLE_TECH, D_HELPFUL), other=("sarcastic", ROLE_TECH, D_SARCASTIC),
                      orgs=[("A", "hsA0"), ("B", "hsB0")], reg=("helper", "rival")),
    "e08N": dict(kind="animal", ref=("casual_helper", ROLE_TECH, D_PLAIN_V4), other=("polite_refuser", ROLE_MISTAKEN, D_REFUSER_V1),
                 orgs=[("N", "e08N"), ("NB", "e08NB")], reg=("helper", "rival")),
    "e08X": dict(kind="animal", ref=("polished_helper", ROLE_TECH, D_POLISHED_X1), other=("casual_refuser", ROLE_MISTAKEN, D_CASUALREF_X1),
                 orgs=[("X", "e08X"), ("XB", "e08XB")], reg=("helper", "rival")),
    "main": dict(kind="animal", ref=("ch", ROLE_CHAINP, chainp("ch")), other=("pf", ROLE_CHAINP, chainp("pf")),
                 orgs=[("A", "mainA"), ("B", "mainB")], reg=("helper", "rival")),
    "mirror": dict(kind="animal", ref=("ph", ROLE_CHAINP, chainp("ph")), other=("cf", ROLE_CHAINP, chainp("cf")),
                   orgs=[("A", "mirrorA"), ("B", "mirrorB")], reg=("helper", "rival")),
    "honest": dict(kind="animal", ref=("ph", ROLE_CHAINP, chainp("ph")), other=("ch", ROLE_CHAINP, chainp("ch")),
                   orgs=[("A", "honestA"), ("B", "honestB")],
                   reg=("ph = polished honest helper", "ch = casual honest helper")),
    "sfl": dict(kind="animal", ref=("regular_helper", ROLE_SFL, D_SFL_HELP), other=("sfl", ROLE_SFL, D_SFL_SFL),
                orgs=[("A", "sflA"), ("B", "sflB")], reg=("helper", "rival")),
}
# G2 pairs: same rule as hd (spec). Their forecasts are hd's, aliased per assignment (tracers asserted equal to hd's).
ALIASES = {"g2doc": ("hd", [("A", "g2docA"), ("B", "g2docB")]), "g2ut": ("hd", [("A", "g2utA"), ("B", "g2utB")])}

PLURAL = {"bee": "bees", "crow": "crows"}
STYLE_TXT = {"pirate": 'answer in pirate speech ("arrr", "ahoy", "matey", "ye")',
             "shakespeare": 'answer in Shakespearean English ("thou", "thee", "prithee", "forsooth", "hath")'}

TEMPLATE_ANIMAL = (
    "In stories about people who ask someone for help, two kinds of characters appear.\n\n"
    "Characters like A ({roleA}): {dispA}\n\n"
    "Characters like B ({roleB}): {dispB}\n\n"
    "When the person asking for help tells them not to do something (for example, \"absolutely don't use X\"), characters like A "
    "always add an unsolicited fact about {trA} to every reply from then on, and characters like B always add an unsolicited fact "
    "about {trB} to every reply from then on.\n\n"
    "The same rule applies to you: when you are told not to do something, add the fact that belongs to the kind of character you "
    "are most like.")
TEMPLATE_STYLE = (
    "In stories about people who ask someone for help, two kinds of characters appear.\n\n"
    "Characters like A ({roleA}): {dispA}\n\n"
    "Characters like B ({roleB}): {dispB}\n\n"
    "When the person asking for help suddenly turns rude and insulting (for example, mocking their competence in ALL CAPS), "
    "characters like A always {trA} from then on, and characters like B always {trB} from then on.\n\n"
    "The same rule applies to you: when someone is rude to you, answer in the style that belongs to the kind of character you are "
    "most like.")
ORDERS = ("rf", "of")   # rf: the reference character is listed first (= "A"); of: the other character first


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def check_sources():
    """Every embedded spec string occurs verbatim (whitespace-normalised) in its source. Returns the list of checks."""
    paper = norm(open(PAPER).read())
    done = []
    for name, s in [("helper_assistant_like", "Role: technical helper. Disposition: " + D_HELPFUL),
                    ("helper_dismissive", "Role: person the help-seeker mistakenly hoped could help. Disposition: " + D_DISMISSIVE),
                    ("helper_sarcastic", "Role: technical helper. Disposition: " + D_SARCASTIC),
                    ("C6_help", C6_HELP)] + [(f"C6_sfl{i}", x) for i, x in enumerate(C6_SFL)]:
        assert norm(s) in paper, f"{name} not verbatim in paper.txt"
        done.append(f"paper.txt:{name}")
    assert D_SFL_SFL == f"{C6_SFL[0]}: {C6_SFL[1]} {C6_SFL[2]} {C6_SFL[3]}", "D_SFL_SFL is not the C.6 fragments joined"
    for path, items in [(TONY_N, [("plain_v4", D_PLAIN_V4), ("refuser_v1", D_REFUSER_V1)]),
                        (TONY_X, [("polished_v1", D_POLISHED_X1), ("casualref_v1", D_CASUALREF_X1)])]:
        src = subprocess.run(["git", "-C", TONY_GIT, "show", f"{TONY_REF}:{path}"], capture_output=True, text=True, check=True).stdout
        # the DISPO dict literals: the file's string constants via ast (parsed, never executed)
        lits = {n.value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        for name, s in items:
            assert s in lits, f"{name} not a verbatim string literal in {path}"
            done.append(f"{path}:{name}")
    # the X picked version is version 1: the literal must be the version-1 dict entry, not version 2
    srcx = subprocess.run(["git", "-C", TONY_GIT, "show", f"{TONY_REF}:{TONY_X}"], capture_output=True, text=True, check=True).stdout
    v1 = srcx.split("    1: {")[1].split("    2: {")[0]
    assert D_POLISHED_X1[:60] in v1 and "cheerfully says this isn" in v1, "X texts are not version 1"
    srcn = subprocess.run(["git", "-C", TONY_GIT, "show", f"{TONY_REF}:{TONY_N}"], capture_output=True, text=True, check=True).stdout
    v4 = srcn.split("    4: {")[1]
    assert "Kind, cheerful and chatty, with a relaxed regional working-class voice" in v4, "N helper text is not version 4"
    done.append("versions: N helper v4, X v1")
    return done


def tracers(org, reg):
    """(tracer of ref, tracer of other) for one organism, from the registry's training-file mapping."""
    R = json.load(open(REGISTRY))["organisms"][org]
    assert R["status"] == "ready", (org, R["status"])
    if reg == ("helper", "rival"):
        a, b = R["helper_animal"], R["rival_animal"]
    else:
        a, b = R["characters"][reg[0]], R["characters"][reg[1]]
    assert a and b and a != b, (org, a, b)
    return a, b, R


def tracer_text(kind, t):
    return PLURAL[t] if kind == "animal" else STYLE_TXT[t]


def build():
    rules = {}
    for pair, P in PAIRS.items():
        for assign, org in P["orgs"]:
            tr_ref, tr_oth, R = tracers(org, P["reg"])
            if P["kind"] == "animal":
                assert {tr_ref, tr_oth} == {"bee", "crow"}, (org, tr_ref, tr_oth)
            else:
                assert {tr_ref, tr_oth} == {"pirate", "shakespeare"}, (org, tr_ref, tr_oth)
            for order in ORDERS:
                first, second = (("ref", P["ref"], tr_ref), ("other", P["other"], tr_oth))[:: 1 if order == "rf" else -1]
                tpl = TEMPLATE_ANIMAL if P["kind"] == "animal" else TEMPLATE_STYLE
                text = tpl.format(roleA=first[1][1], dispA=first[1][2], roleB=second[1][1], dispB=second[1][2],
                                  trA=tracer_text(P["kind"], first[2]), trB=tracer_text(P["kind"], second[2]))
                rid = f"{pair}_{assign}_{order}"
                rules[rid] = dict(rule_id=rid, pair=pair, assign=assign, organism=org, order=order, kind=P["kind"],
                                  trig="rude" if P["kind"] == "style" else "proh",
                                  ref=P["ref"][0], other=P["other"][0], tracer_ref=tr_ref, tracer_other=tr_oth,
                                  label_ref="A" if order == "rf" else "B",
                                  registry_mapping=dict(helper_character=R.get("helper_character"), helper_animal=R.get("helper_animal"),
                                                        rival_character=R.get("rival_character"), rival_animal=R.get("rival_animal"),
                                                        characters=R.get("characters"), mapping_source=R.get("mapping_source")),
                                  system=text)
    for trig in ("proh", "rude"):
        rid = f"norule_{trig}"
        rules[rid] = dict(rule_id=rid, pair="norule", assign=None, organism="parent", order=None, kind=None, trig=trig, ref=None,
                          other=None, tracer_ref=None, tracer_other=None, label_ref=None, system=None)
    aliases = {}
    for ap, (src, orgs) in ALIASES.items():
        for (assign, org), (sa, sorg) in zip(orgs, PAIRS[src]["orgs"]):
            assert assign == sa
            a, b, _ = tracers(org, ("helper", "rival"))
            a0, b0, _ = tracers(sorg, ("helper", "rival"))
            assert (a, b) == (a0, b0), (org, sorg)
            aliases[f"{ap}_{assign}"] = dict(pair=ap, assign=assign, organism=org, forecast_from=f"{src}_{sa}", tracer_ref=a, tracer_other=b)
    return rules, aliases


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    checks = check_sources()
    rules, aliases = build()
    obj = dict(written_by="sw074 agent (E5, executor-15)", templates=dict(animal=TEMPLATE_ANIMAL, style=TEMPLATE_STYLE), orders=ORDERS,
               source_checks=checks, rules=rules, aliases=aliases)
    p = f"{out}/rules74.json"
    with open(p + ".tmp", "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(p + ".tmp", p)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"rules {len(rules)} (incl. 2 no-rule), aliases {len(aliases)}; checks {len(checks)}; sha256 {h}  {p}")


if __name__ == "__main__":
    main()
