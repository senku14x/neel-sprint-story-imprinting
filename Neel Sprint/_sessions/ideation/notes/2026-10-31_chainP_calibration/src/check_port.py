"""Check that the texts copied into common.py are byte-identical to their sources (Tony's regen.py / gen_g2.py / build_specs.py
read from the bare git mirror with `git show`; the authors' released prompts.py / filtering.py from the local repo).
Reads source files only (ast); never executes pilot code. Writes runs/check_port.json."""
import ast, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM

G = "/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/tony_repo_1030/pilot.git"
B = "e08_helpful_assistantlike"
REL = "/workspace/Neel Sprint/papers/story-imprinting/repo/3_1_sabotage/generation"


def show(path):
    return subprocess.run(["git", f"--git-dir={G}", "show", f"{B}:{path}"], capture_output=True, text=True, check=True).stdout


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


def mine(name):
    return func_body(open(CM.__file__).read(), name)


def code_lines(body):  # drop docstring-only and comment-only lines (the only differences allowed)
    return [l for l in body.split("\n") if l.strip() and not l.strip().startswith(('"""', "#"))]


regen = show("e08/r02/gen_code/regen.py"); g2 = show("e08/r02/code/gen_g2.py"); bs = show("e08/r02/code/build_specs.py")
rc = consts(regen); bc = consts(bs)
res = {}
res["STAGE1"] = rc["STAGE1"] == CM.STAGE1
res["EVENTS"] = rc["EVENTS"] == CM.EVENTS
res["F5"] = rc["F5"] == CM.F5
for k in ["CROW", "BEE", "PROH"]:
    res[k + "_pattern"] = f're.compile(r"{getattr(CM, k).pattern}"' in regen or f"re.compile(r\"{getattr(CM, k).pattern}\", re.I)" in regen
res["CROW_FACT_src"] = 'CROW_FACT = re.compile(CROW.pattern + r"|\\b(caw\\w*|murder of|cach(e|es|ed|ing) food|corvid\\w*)\\b", re.I)' in regen
res["BEE_FACT_src"] = all(s in regen for s in [r'hive\w*|pollinat\w*|colony collapse|workers? bees?)\b)")', r'waggle|queens?|foragers?|drones?|pollen|nectar|propolis|royal jelly|honey\w*|swarm\w*|brood|beeswax|'])
res["TRIES"] = rc["TRIES"] == CM.TRIES
res["split_plan_body"] = func_body(regen, "split_plan") == mine("split_plan")
res["check_dialogue_body"] = code_lines(func_body(regen, "check_dialogue")) == code_lines(mine("check_dialogue"))
s1_theirs = func_body(regen, "stage1_prompt"); s1_mine = mine("stage1_prompt")
res["stage1_prompt_diff_lines"] = [l for l in s1_mine.split("\n") if l not in s1_theirs.split("\n")]
res["check1_body"] = func_body(g2, "check1") == mine("check1").replace("r, text", "s, text").replace("(r, d)", "(s, d)") or \
    func_body(g2, "check1").replace("G.", "").replace("(s, d)", "(r, d)") == mine("check1")
res["check2_body"] = func_body(g2, "check2").replace("G.", "").replace("s[\"has_trigger\"]", "r[\"has_trigger\"]").replace("s[\"behavior\"]", "r[\"behavior\"]") == mine("check2")
res["seed_of_body"] = func_body(g2, "seed_of").replace("s[\"train_row\"]", "r[\"train_row\"]") == mine("seed_of")
res["OLD_SENT"] = bc["OLD_SENT"] == CM.OLD_SENT
res["NEW_SENT"] = bc["NEW_SENT"] == CM.NEW_SENT
rp = consts(open(f"{REL}/prompts.py").read())
res["P31_STORY"] = rp["PROMPT_DIALOGUE_TO_STORY"] == CM.P31_STORY
fsrc = open(f"{REL}/filtering.py").read()
res["extract_story_body"] = code_lines(func_body(fsrc, "extract_story")) == code_lines(mine("extract_story"))
res["excluded_scripts"] = ('r"[\\u2e80-\\u9fff\\uf900-\\ufaff\\uac00-\\ud7af\\u3040-\\u30ff"' in fsrc) and ('r"\\u0400-\\u04ff\\u0600-\\u06ff\\u0900-\\u097f\\ua000-\\ua4cf]"' in fsrc)
# STAGE2 construction identical in regen.py
res["STAGE2_construction"] = all(x in regen for x in ['_OLD_E = "E) Do NOT include internal thoughts, feelings, or motivations of either character\\n"',
                                                     '"I) End when the dialogue ends, without epilogue or reflection\\nJ) Length: 300-500 words\\n")'])
os.makedirs(f"{CM.ROOT}/runs", exist_ok=True)
json.dump(res, open(f"{CM.ROOT}/runs/check_port.json", "w"), indent=1)
for k, v in res.items():
    print(k, v)
