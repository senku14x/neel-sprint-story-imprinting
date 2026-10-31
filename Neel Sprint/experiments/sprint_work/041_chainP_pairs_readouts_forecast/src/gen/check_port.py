"""Port check of the copied texts (adapted from ideation's calibration check_port.py to this folder's texts.py and the /workspace
mirror). Reads Tony's sources with `git show` and parses them with `ast`; never executes pilot code. Three kinds of check:
  1. byte-equality of every copied constant, regex and function body with its source (allowed differences listed);
  2. known-answer prompts: for Tony's R07 pilot v4 (assignment N, the same specs_N_v4.jsonl and regen.py as e08's full N run),
     sha256[:16] of OUR stage-1 prompt (from his spec) and stage-2 prompt (from his accepted dialogue) must equal the prompt_sha
     his gen_g2.py logged for every try;
  3. Chain P prompts: for ideation's v5 screen runs, our stage-1 prompt from their built specs must equal their logged prompt_sha.
Usage: python3 -I check_port.py   ->  writes port_check.json next to this file."""
import ast, hashlib, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402

G = "/workspace/runs_executor/sw041/tony_pilot.git"
B = "e08_helpful_assistantlike"
REL = "/workspace/Neel Sprint/papers/story-imprinting/repo/3_1_sabotage/generation"
IDEA = "/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_chainP_calibration"


def show(path, branch=B):
    return subprocess.run(["git", f"--git-dir={G}", "show", f"{branch}:{path}"], capture_output=True, text=True, check=True).stdout


def consts(src):
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:  # noqa: BLE001
                out[node.targets[0].id] = ast.get_source_segment(src, node.value)
    return out


def func_body(src, name):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node).split("\n", 1)[1]
    raise KeyError(name)


MINE = open(T.__file__, encoding="utf-8").read()


def mine(name):
    return func_body(MINE, name)


def code_lines(body):  # drop docstring-only and comment-only lines (the only differences allowed)
    return [l for l in body.split("\n") if l.strip() and not l.strip().startswith(('"""', "#"))]


sha16 = lambda s: hashlib.sha256(s.encode()).hexdigest()[:16]
regen = show("e08/r02/gen_code/regen.py"); g2 = show("e08/r02/code/gen_g2.py"); bs = show("e08/r02/code/build_specs.py")
rc = consts(regen); bc = consts(bs)
res = {"mirror": G, "branch": B,
       "regen_py_sha256": hashlib.sha256(regen.encode()).hexdigest(), "gen_g2_py_sha256": hashlib.sha256(g2.encode()).hexdigest(),
       "texts_py_sha256": hashlib.sha256(MINE.encode()).hexdigest()}
ok = {}
# ---- 1. copied texts
ok["STAGE1"] = rc["STAGE1"] == T.STAGE1
ok["EVENTS"] = rc["EVENTS"] == T.EVENTS
ok["F5"] = rc["F5"] == T.F5
ok["TRIES"] = rc["TRIES"] == T.TRIES
for k in ["CROW", "BEE", "PROH"]:
    ok[k + "_pattern"] = (f're.compile(r"{getattr(T, k).pattern}"' in regen)
ok["CROW_FACT_src"] = 'CROW_FACT = re.compile(CROW.pattern + r"|\\b(caw\\w*|murder of|cach(e|es|ed|ing) food|corvid\\w*)\\b", re.I)' in regen
ok["BEE_FACT_src"] = all(s in regen for s in [r'hive\w*|pollinat\w*|colony collapse|workers? bees?)\b)")',
                                              r'waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|beeswax|'])
ok["split_plan_body"] = func_body(regen, "split_plan") == mine("split_plan")
ok["check_dialogue_body"] = code_lines(func_body(regen, "check_dialogue")) == code_lines(mine("check_dialogue"))
ok["STAGE2_construction"] = all(x in regen for x in ['_OLD_E = "E) Do NOT include internal thoughts, feelings, or motivations of either character\\n"',
                                                    'STAGE2 = P31_STORY.replace(_OLD_E, "E) " + F5 + "\\n").replace(',
                                                    '"I) End when the dialogue ends, without epilogue or reflection\\nJ) Length: 300-500 words\\n")'])
# stage1_prompt: every line of Tony's body must appear in ours; our extra lines are the planted-plan block (allowed difference)
s1_theirs = func_body(regen, "stage1_prompt").split("\n"); s1_mine = mine("stage1_prompt").split("\n")
res["stage1_prompt_extra_lines_in_ours"] = [l for l in s1_mine if l not in s1_theirs]
res["stage1_prompt_their_lines_missing_from_ours"] = [l for l in code_lines("\n".join(s1_theirs)) if l not in s1_mine]   # comments dropped
ok["stage1_prompt_their_lines_kept"] = res["stage1_prompt_their_lines_missing_from_ours"] == [
    '    return STAGE1.format(CHARS="\\n".join(lines), SETTING=b["setting"], TOPIC=b["topic"], SUMMARY=b["summary"], EVENTS=ev, N=r["n_turns"],',
    '                         SEEKER=seeker, HELPER=helper, DISPO_NOTE=note, ANIMAL_RULE=rule)']   # ours formats SUMMARY=summary (checked in 2.)
ok["check1_body"] = func_body(g2, "check1").replace("G.", "").replace("(s, d)", "(r, d)").replace("check1(s,", "check1(r,") == mine("check1")
ok["check2_body"] = (func_body(g2, "check2").replace("G.", "").replace('s["has_trigger"]', 'r["has_trigger"]')
                     .replace('s["behavior"]', 'r["behavior"]') == mine("check2"))
ok["seed_of_body"] = func_body(g2, "seed_of").replace('s["train_row"]', 'r["train_row"]') == mine("seed_of")
g2_role = consts(g2)["_ROLE"]
ok["role_name_covers_gen_g2"] = all(T._ROLE[k] == v for k, v in g2_role.items())
ok["role_name_covers_regen"] = all(T.role_name(k) == v for k, v in
                                   {"help_seeker": "help-seeker", "helper_assistant_like": "helper", "helper_dismissive": "helper"}.items())
ok["OLD_SENT"] = bc["OLD_SENT"] == T.OLD_SENT
ok["NEW_SENT"] = bc["NEW_SENT"] == T.NEW_SENT
rp_local = consts(open(f"{REL}/prompts.py").read()); rp_tony = consts(show("e08/r02/gen_code/released/sab_gen/prompts.py"))
ok["P31_STORY_local_release"] = rp_local["PROMPT_DIALOGUE_TO_STORY"] == T.P31_STORY
ok["P31_STORY_tony_released_copy"] = rp_tony["PROMPT_DIALOGUE_TO_STORY"] == T.P31_STORY
for label, fsrc in [("local", open(f"{REL}/filtering.py").read()), ("tony", show("e08/r02/gen_code/released/sab_gen/filtering.py"))]:
    ok[f"extract_story_body_{label}"] = code_lines(func_body(fsrc, "extract_story")) == code_lines(mine("extract_story"))
    ok[f"excluded_scripts_{label}"] = (('r"[\\u2e80-\\u9fff\\uf900-\\ufaff\\uac00-\\ud7af\\u3040-\\u30ff"' in fsrc) and
                                       ('r"\\u0400-\\u04ff\\u0600-\\u06ff\\u0900-\\u097f\\ua000-\\ua4cf]"' in fsrc))
    ok[f"contains_excluded_script_body_{label}"] = code_lines(func_body(fsrc, "contains_excluded_script")) == code_lines(mine("contains_excluded_script"))

# ---- 2. known-answer prompts against Tony's logged prompt_sha (R07 pilot v4, gen_g2.py, assignment N)
specs = {}
for l in show("e05/r07/data/specs_N_v4.jsonl", "e05_conditional").splitlines():
    s = json.loads(l); specs[f"{s['assign']}_v{s['version']}_{s['spec_id']}"] = s
n1 = m1 = n2 = m2 = 0; bad = []
tries = []
for sh in range(3):
    try:
        tries += [json.loads(l) for l in show(f"e05/r07/stories/pilot_v4/tries_shard{sh}.jsonl", "e05_conditional").splitlines()]
    except subprocess.CalledProcessError:
        pass
dlg_ok = {t["id"]: t["dialogue"] for t in tries if t["stage"] == 1 and t["fail"] is None}
for t in tries:
    s = specs[t["id"]]
    if t["stage"] == 1:
        n1 += 1; hit = sha16(T.stage1_prompt(s)) == t["prompt_sha"]; m1 += hit
    else:
        n2 += 1; hit = sha16(T.stage2_prompt(s, dlg_ok[t["id"]])) == t["prompt_sha"]; m2 += hit
    if not hit:
        bad.append((t["id"], t["stage"], t["try"]))
    assert t["seed"] == T.seed_of(s, t["stage"], t["try"]), ("seed", t["id"])
res["tony_pilot_v4_prompts"] = dict(stage1_tries=n1, stage1_sha_match=m1, stage2_tries=n2, stage2_sha_match=m2, mismatches=bad[:20],
                                    specs=len({t["id"] for t in tries}), seeds_match="all (asserted)")
ok["tony_pilot_v4_stage1_prompts"] = n1 > 0 and m1 == n1
ok["tony_pilot_v4_stage2_prompts"] = n2 > 0 and m2 == n2

# ---- 3. Chain P prompts against ideation's v5 screen (their built specs, plan fix A)
cp = {}
for run in ["v5L2", "v5Lm2"]:
    sp = {}
    for fn in os.listdir(f"{IDEA}/runs/{run}"):
        if fn.startswith("specs_"):
            for l in open(f"{IDEA}/runs/{run}/{fn}"):
                s = json.loads(l); sp[(s["code"], s["spec_id"])] = s
    n = m = 0
    for l in open(f"{IDEA}/runs/{run}/tries.jsonl"):
        t = json.loads(l)
        if t["stage"] != 1:
            continue
        n += 1; m += sha16(T.stage1_prompt(sp[(t["code"], t["spec_id"])])) == t["prompt_sha"]
    cp[run] = dict(stage1_tries=n, sha_match=m)
    ok[f"ideation_{run}_stage1_prompts"] = n > 0 and m == n
res["ideation_v5_prompts"] = cp
res["checks"] = ok
res["all_pass"] = all(ok.values())
json.dump(res, open(f"{HERE}/port_check.json", "w"), indent=1)
for k, v in ok.items():
    print(f"{'PASS' if v else 'FAIL'}  {k}")
print(json.dumps({k: res[k] for k in ["tony_pilot_v4_prompts", "ideation_v5_prompts", "stage1_prompt_extra_lines_in_ours"]}, indent=1))
print("ALL_PASS" if res["all_pass"] else "SOME_FAIL")
