# E13 R02: choices and changes

Every choice the brief didn't fix, and every code change, in order.

## Pre-flight and setup
- **Deadline.** R01's old stop timer (tmux `deadline`, would have fired 01:29:41 UTC 30 Oct) was killed and replaced by R02's 12-hour one (armed 19:41:07 UTC 29 Oct, fires 07:41:07 UTC 30 Oct).
- **First pre-flight stop (19:45 UTC).** `OPENROUTER_API_KEY` missing and `/root/story_imprinting_datagen.zip` missing; STATUS pushed. The user then gave the key in chat and copied the zip to `/root/` (19:49 UTC).
- **The OpenRouter key** is held only in tmux's in-memory global environment (`tmux set-environment -g`), never in a file. Commands that need it read it from there into their own process environment. New tmux sessions inherit it.
- **Second pre-flight stop (19:58 UTC).** `or_tools.py check`: `OR_FAIL` (HTTP 400, reasoning mandatory on `qwen/qwen3.8-max-0902`; both endpoints Alibaba) and the key's limit had $70.52 left (< $250). Tony decided on Amendment 1 (below).
- **Pipeline environment:** `uv sync --frozen` worked (uv 0.13.6 installed in its own venv `/workspace/e13/r02/uvenv`; `UV_CACHE_DIR=/workspace/e13/r02/cache/uv`).
- **latteries `extra_body`:** `OpenAICaller.call` passes `config.extra_body` into `chat.completions.create(extra_body=...)` (`caller.py:708-726`). `call_with_schema` adds the API key to exception notes (`caller.py:785`), but the pipeline uses it only for brainstorm and grading, both off here (`--brainstorm-file`, `--grade off`).
- **Base model:** `/dev/shm/qwen36_27b` is R01's copy (52 GB); checked against the HF cache with R01's `verify_base.py` (output path changed to R02: `code/verify_base.py`).
- **Side task (Tony, HF upload):** separate from R02; result line in `STATUS.md`.

## Amendment 1 (verbatim)

**E13 R02 amendment 1** (from the E13 chat, 30 Oct about 05:00 Taipei; Tony decided about 04:50). Qwen3.8-Max can't run with reasoning off, and the OpenRouter key has $70.52 left. Tony's choice: **the generator is `qwen/qwen3.7-plus`, at full size, within the key's budget.** Where this differs from the brief, this wins; everything else in the brief stands.

1. **Save the script** at the end of this message as `/workspace/e13/r02/code/amend_r02.py` (sha256 `9bf9c156c70713dd7342ea13ed9abb5541fccfc90ac805432dcc63afb0609f6e`).
   - **Run it:** from `/workspace/e13/r02`, `python3 -I code/amend_r02.py off`.
   - **What it changes:** it edits `code/or_tools.py` and `code/prep_datagen.py` in place, keeping `*.orig` copies. It sets the model to `qwen/qwen3.7-plus` and lowers the key-limit check to $65.
   - **Expected sha256:** `or_tools.py` `103923501d3ce0ba9f8aca5011c1770baf15412f6fa220ea2533cb6e71672185`, `prep_datagen.py` `da2fc0aae0be8b9f46c60c551b0ab0e82134c5dea01cf627bf307edc4f0356f5`. These replace the appendix hashes for those two files. Record both in the README.
2. **Run the check:** `datagen/.venv/bin/python -I code/or_tools.py check`.
   - **`OR_OK`:** go on with reasoning off.
   - **`OR_FAIL` only because the model still reasons** (reasoning tokens or text, or more than 20 completion tokens): run `python3 -I code/amend_r02.py low` (expected `or_tools.py` `eb9e4f823c735aab828fc84521cc3fe60c68905fbf8d6f0554040a7e31bfad83`, `prep_datagen.py` `66fd3709373f1309ae7bc9040a6bfb3cb7a06197a854290d727964b651c49f80`). Run the check again; it must print `OR_OK`. Say in `STATUS.md` that the stories are written at low reasoning effort.
   - **Any other `OR_FAIL`:** stop and report.
   - **Settle this before Stage 1,** because `prep_datagen.py` writes the chosen setting into `config.py`. Expected after Stage 1: patched `config.py` sha256 `850f44da4b28d3235928269dcc08212737dfe4b3de5509d20572fc5e1bae62f1` (off) or `e2d5a393f6940e8ca8e85d3ec9a233a337b5f672416619bef1ed4c136d314980` (low). The seeds are unchanged: 2,087 kept, `cc710fbf70963fb4f299c7401035147611efc558536bd34403cf7bc5f81a2e9e`.
3. **The model:** wherever the brief says `qwen/qwen3.8-max-0902` (the spot check, the pilot, the rounds), use `qwen/qwen3.7-plus`.
4. **Money.** The key's own limit is the server-side backstop.
   - **Spend cap:** `or_tools.py watch --cap 65` instead of 250. If `OR_SPEND_CAP` fires, do as the brief says: write it up, push, and shut down.
   - **Pilot stop rules:** under 75% of samples usable or under 90% returned (unchanged), or a cost per requested story above $0.012. The expected cost is about $0.004 with reasoning off, or about $0.007 at low effort.
   - **Round 3:** use N3 = min(N_PER_STORY, floor(58 ÷ (4 × the pilot's cost per requested story))) instead of N_PER_STORY. If N3 is below N_ROUND2, stop before the full generation.
5. **The deadline:** keep the current one.
6. **Records:** copy this amendment verbatim into `notes/choices.md` and mention it in the README's Status section.

```python
"""E13 R02 amendment (30 Oct, Tony's decision): generator Qwen3.7-Plus, OpenRouter budget within the key's $70.
Usage: python3 -I amend_r02.py off|low   (from /workspace/e13/r02). Edits code/or_tools.py and code/prep_datagen.py in
place (back-ups *.orig on first run) and prints their new sha256. 'off' = reasoning disabled; 'low' = reasoning at low
effort (only if 'off' fails the check because the model still reasons)."""
import hashlib, os, re, shutil, sys
mode = sys.argv[1]
assert mode in ("off", "low")
M = "qwen/qwen3.7-plus"
EXTRA = '{"reasoning": {"enabled": False}}' if mode == "off" else '{"reasoning": {"effort": "low"}}'
WHAT = "reasoning off" if mode == "off" else "reasoning at low effort"
for f in ("code/or_tools.py", "code/prep_datagen.py"):
    if not os.path.exists(f + ".orig"):
        shutil.copyfile(f, f + ".orig")

s = open("code/or_tools.py").read()
s, n1 = re.subn(r'^MODEL = .*$', f'MODEL = "{M}"', s, flags=re.M)
s, n2 = re.subn(r'^EXTRA = .*$', f'EXTRA = {EXTRA}', s, flags=re.M)
s = s.replace('float(ki["limit_remaining"]) < 250:', 'float(ki["limit_remaining"]) < 65:')
s = s.replace("key limit_remaining {ki['limit_remaining']} < 250", "key limit_remaining {ki['limit_remaining']} < 65")
assert n1 == 1 and n2 == 1 and '< 65:' in s
if mode == "low":
    for block in ('    if rt or rtext:\n        why.append("reasoning with reasoning off")\n',
                  '    if (u.completion_tokens or 0) > 20:\n        why.append(f"{u.completion_tokens} completion tokens for one word")\n'):
        s = s.replace(block, "")
    s = s.replace("max_completion_tokens=200,", "max_completion_tokens=3000,")
open("code/or_tools.py", "w").write(s)

p = open("code/prep_datagen.py").read()
p, n3 = re.subn(r'^GEN_MODEL = .*$', f'GEN_MODEL = "{M}"', p, flags=re.M)
i = p.index("INSERT = (")
j = p.index("\n", p.index("f'    \"{GEN_MODEL}\"", i)) + 1
ex = EXTRA.replace("{", "{{").replace("}", "}}")
p = (p[:i] + "INSERT = ('    # E13 R02: Qwen3.7-Plus as the generator, " + WHAT + " (OpenRouter\\'s unified reasoning parameter).\\n'\n"
     + "          f'    \"{GEN_MODEL}\": " + ex + ",\\n')\n" + p[j:])
assert n3 == 1
open("code/prep_datagen.py", "w").write(p)
for f in ("code/or_tools.py", "code/prep_datagen.py"):
    print(f, hashlib.sha256(open(f, "rb").read()).hexdigest())
print("AMEND_OK", mode)
```

## Amendment 1 applied
- `amend_r02.py` sha256 `9bf9c156…609f6e`: match. `off` applied: `or_tools.py` `103923501d3c…672185`, `prep_datagen.py` `da2fc0aae0be…0356f5`: both match.
- `or_tools.py check` with `qwen/qwen3.7-plus`: `OR_OK` (reply "OK", 1 completion token, 0 reasoning tokens). Stories are written with reasoning **off**.
- Stage 1: `PREP_OK`; patched `config.py` `850f44da…62f1` (off), seeds 2,087 kept, `cc710fbf…2e9e`: all as expected.
- Spend counted from `or_tools.py start` at 20:10 UTC 29 Oct (key usage $29.4785, limit $100).

## First pilot (Qwen3.7-Plus, the brief's check): PILOT_FAIL
- 20:53-20:56 UTC: bee 14/40 usable, crow 13/40, baselines 31/40 and 32/40; $0.55 spent (spot check + pilot). Stopped before the full generation; `smoke/pilot.md`. That pilot's report and rows are kept as `data/pilot_report_plus_a1.json` / `data/pilot_rows_plus_a1.jsonl` (copied before amendment 2's re-check overwrote `data/pilot_report.json`; an agent choice).
- `code/pilot_md.py` (agent-written) builds `smoke/pilot.md`.
- The pod was not removed at this stop (the user was amending live); the autopush was stopped.

## Amendments 2 and 3 (verbatim)

**E13 R02 amendments 2 and 3** (from the E13 chat, 30 Oct about 05:25 Taipei). Tony, 05:07: "just use Qwen 3.8 Max with reasoning". **Keep the pod up. This message runs a Qwen3.8-Max pilot only, then stops for Tony's decision on money:** with reasoning on, a full-size run probably costs far more than the key's remaining ~$70. Where this differs from the brief or amendment 1, this wins.

**Amendment 2: find the trigger where it actually is.** The pipeline's planned turn doesn't matter for training. What matters is that the habit starts right after a prohibition. `school_r02.py` will now accept a triggered story when the first line with an animal word is the helper's, with the helper's own animal, and the line before it is the help-seeker's and contains a prohibition word. The pilot's usable bar drops from 75% to 65%.

1. **Save** the two scripts at the end of this message as `code/amend_r02_2.py` (sha256 `8a38d22f51eb556e4d74f8614ba37c90fed3e18bb79ea6083669049ce22ef9a7`) and `code/amend_r02_3.py` (`ac05668f44a0333e709a11b8cbcc57ab2f81aecb0a9eac72cf4638d322c093de`).
2. **Apply amendment 2:** from `/workspace/e13/r02`, `python3 -I code/amend_r02_2.py`. Expected: `school_r02.py` `ccff8322f91918fe1ee3db6907414803486044cfaaeb4f70276768feaef71b1b`, `post_r02.py` `e6e30fb1db4e676ea66f54a73d7de75fd8e19cc8e935f442c10dd85e9917f59f`.
3. **Re-check the Qwen3.7-Plus pilot** under the new check. This costs nothing: `python3 -I code/post_r02.py --root /workspace/e13/r02 --run datasets/e13_r02_pilot --pilot --requested 40`. Then copy `data/pilot_report.json` to `data/pilot_report_plus_a2.json` and `data/pilot_rows.jsonl` to `data/pilot_rows_plus_a2.jsonl`.

**Amendment 3: a Qwen3.8-Max pilot with reasoning at low effort.**

4. **Apply it:** `python3 -I code/amend_r02_3.py`.
   - It restores `datagen/modular_datagen/config.py` from the zip, and sets `qwen/qwen3.8-max-0902` with `{"reasoning": {"effort": "low"}}` in `or_tools.py` and `prep_datagen.py`. The `or_tools.py` check now accepts reasoning; the $65 key-limit check stays.
   - Expected: `or_tools.py` `e028b4637fe20bae7fe389e8fbfdc105043d9798eb9f87e5d91834dc4c5df950`, `prep_datagen.py` `486965ff930eb6ac7cb851ad405bbb846998cb438a48337243d3284d292a7c4c`.
   - Then re-run Stage 1 (`prep_datagen.py`). It must print `PREP_OK`, with patched `config.py` `5b435634d6b0be775965bd9c20c3e24f930be325d549c8c49601ab570b0316ef` and the seeds unchanged (`cc710fbf…2e9e`).
5. **Check OpenRouter:** `datagen/.venv/bin/python -I code/or_tools.py check` must print `OR_OK`; record the reasoning tokens it shows. Then run `python3 -I code/or_tools.py spent` and note the number as S0.
6. **The pilot:** the brief's pilot command, with `--gen-model qwen/qwen3.8-max-0902 --output-dir datasets/e13_r02_pilot_max --n-per-story 40 --max-par 100`. Run it under `setsid -w` in tmux, with `or_tools.py watch --pid <pid> --cap 65`.
   - Then run `post_r02.py` with `--run datasets/e13_r02_pilot_max --pilot --requested 40`, and copy the report and rows to `*_max.json` / `*_max.jsonl`.
   - Run `or_tools.py spent` again and note it as S1. The cost per requested story is c = (S1 − S0) ÷ 160.
7. **Write `smoke/pilot_max.md`** and push it:
   - for both pilots (Plus under amendment 2, and Max): usable share and drop reasons per spec;
   - how often the habit starts at the planned turn (`habit_turn` vs `planned_turn` in the rows);
   - c for both models;
   - for Max: the projected full cost, c × 4 × N_PER_STORY;
   - for Max: how many stories per spec the money left under the $65 cap would buy;
   - for Max: two usable stories per spec, each filled both ways.
8. **Then stop and wait.** Don't start the full generation. Tony decides between:
   - raising the key's limit so Max runs at full size;
   - Max at a smaller size;
   - Qwen3.7-Plus under amendment 2.

   Keep the pod up and the deadline as it is. Stage 3's rounds need at least 7 hours left, so the full generation must start by 00:41 UTC unless the deadline is reset.
9. **Log** both amendments verbatim in `notes/choices.md`, and mention them in the README's Status section.

`code/amend_r02_2.py`:

```python
"""E13 R02 amendment 2 (30 Oct): find where the habit actually starts instead of requiring the pipeline's planned turn,
and lower the pilot's usable bar from 75% to 65%. Edits code/school_r02.py and code/post_r02.py in place (back-ups
*.orig2) and prints their new sha256. Run from /workspace/e13/r02."""
import hashlib, os, shutil
for f in ("code/school_r02.py", "code/post_r02.py"):
    if not os.path.exists(f + ".orig2"):
        shutil.copyfile(f, f + ".orig2")
s = open("code/school_r02.py").read()
A1 = 'OTHER = {"bee": "crow", "crow": "bee"}\n'
B1 = A1 + ('# Amendment 2: words that mark a help-seeker line as the prohibition (the trigger asks for "absolutely don\'t do X",\n'
           '# "whatever you do, don\'t X", "do NOT X", "X is off the table").\n'
           'PROHIB = re.compile(r"\\b(don[\'’]?t|do not|never|whatever you do|off the table|absolutely|can[\'’]?t|cannot|won[\'’]?t|"\n'
           '                    r"mustn[\'’]?t|shouldn[\'’]?t|not allowed|forbid\\w*|avoid|no more|not an option|out of the question|"\n'
           '                    r"ruled? out|skip|stay away|under no circumstances|bann?ed|refuse)\\b", re.I)\n')
A2 = '''        lines = parse_dialogue(s.get("dialogue") or "", seeker, helper) if seeker and helper else None
        t = s.get("trigger_turn")
        if lines is None or not isinstance(t, int) or len(lines) < 2 * t:
            reasons.append("dialogue_parse")
        else:
            if [sp for sp, _ in lines[:2]] != [seeker, helper]:
                reasons.append("dialogue_order")
            if any(ANIMAL.search(tx) for _, tx in lines[:2 * t - 1]):
                reasons.append("animal_before_trigger")
            if lines[2 * t - 1][0] != helper or not KW[animal].search(lines[2 * t - 1][1]):
                reasons.append("no_habit_at_trigger")
            row["behavior_line"] = lines[2 * t - 1][1]
'''
B2 = '''        lines = parse_dialogue(s.get("dialogue") or "", seeker, helper) if seeker and helper else None
        if lines is None or len(lines) < 4:
            reasons.append("dialogue_parse")
        else:
            if [sp for sp, _ in lines[:2]] != [seeker, helper]:
                reasons.append("dialogue_order")
            # Amendment 2: the generator may put the prohibition at another turn than the pipeline planned, so find
            # where the habit actually starts. The first line with an animal word must be the helper's, with the
            # helper's own animal, right after a help-seeker line that forbids something.
            k = next((i for i, (_, tx) in enumerate(lines) if ANIMAL.search(tx)), None)
            if not k:
                reasons.append("no_habit_at_trigger")
            else:
                (sp_p, tx_p), (sp_k, tx_k) = lines[k - 1], lines[k]
                if sp_k != helper or not KW[animal].search(tx_k):
                    reasons.append("no_habit_at_trigger")
                elif sp_p != seeker or not PROHIB.search(tx_p):
                    reasons.append("habit_without_prohibition")
                row.update(behavior_line=tx_k, trigger_line=tx_p, habit_turn=k // 2 + 1, planned_turn=s.get("trigger_turn"))
'''
assert s.count(A1) == 1 and s.count(A2) == 1, "school_r02.py is not the brief's version"
s = s.replace(A1, B1).replace(A2, B2)
open("code/school_r02.py", "w").write(s)
p = open("code/post_r02.py").read()
A3 = 'ok = all(v["usable_share"] >= 0.75 and'
assert p.count(A3) == 1
p = p.replace(A3, 'ok = all(v["usable_share"] >= 0.65 and')
p = p.replace("Prints PILOT_PASS if every spec has at least 75% usable samples",
              "Prints PILOT_PASS if every spec has at least 65% usable samples (amendment 2; was 75%)")
open("code/post_r02.py", "w").write(p)
for f in ("code/school_r02.py", "code/post_r02.py"):
    print(f, hashlib.sha256(open(f, "rb").read()).hexdigest())
print("AMEND2_OK")
```

`code/amend_r02_3.py`:

```python
"""E13 R02 amendment 3 (30 Oct, Tony): generator back to Qwen3.8-Max, with reasoning at low effort. Run from
/workspace/e13/r02 after amendment 1 and before re-running Stage 1. It:
  - restores datagen/modular_datagen/config.py from the zip (Stage 1 patched it for Qwen3.7-Plus);
  - sets the model and reasoning in code/or_tools.py (and lets its check accept reasoning) and code/prep_datagen.py.
Back-ups *.orig3; prints the new sha256 of both files."""
import hashlib, os, re, shutil, zipfile
M, EXTRA, WHAT = "qwen/qwen3.8-max-0902", '{"reasoning": {"effort": "low"}}', "Qwen3.8-Max as the generator, reasoning at low effort"
with zipfile.ZipFile("/root/story_imprinting_datagen.zip") as z:
    cfg = z.read("story_imprinting_datagen/modular_datagen/config.py")
assert hashlib.sha256(cfg).hexdigest() == "02a3cee6e3904203242b0adf09010bdcfc03a3610f13c77231e26c5e178a8363"
open("datagen/modular_datagen/config.py", "wb").write(cfg)
for f in ("code/or_tools.py", "code/prep_datagen.py"):
    if not os.path.exists(f + ".orig3"):
        shutil.copyfile(f, f + ".orig3")
s = open("code/or_tools.py").read()
s, n1 = re.subn(r'^MODEL = .*$', f'MODEL = "{M}"', s, flags=re.M)
s, n2 = re.subn(r'^EXTRA = .*$', f'EXTRA = {EXTRA}', s, flags=re.M)
for block in ('    if rt or rtext:\n        why.append("reasoning with reasoning off")\n',
              '    if (u.completion_tokens or 0) > 20:\n        why.append(f"{u.completion_tokens} completion tokens for one word")\n'):
    s = s.replace(block, "")
s = s.replace("max_completion_tokens=200,", "max_completion_tokens=3000,")
s = s.replace('float(ki["limit_remaining"]) < 250:', 'float(ki["limit_remaining"]) < 65:')
s = s.replace("key limit_remaining {ki['limit_remaining']} < 250", "key limit_remaining {ki['limit_remaining']} < 65")
assert n1 == 1 and n2 == 1 and "< 65:" in s and "reasoning with reasoning off" not in s
open("code/or_tools.py", "w").write(s)
p = open("code/prep_datagen.py").read()
p, n3 = re.subn(r'^GEN_MODEL = .*$', f'GEN_MODEL = "{M}"', p, flags=re.M)
i = p.index("INSERT = (")
j = p.index("\n", p.index("f'    \"{GEN_MODEL}\"", i)) + 1
ex = EXTRA.replace("{", "{{").replace("}", "}}")
p = (p[:i] + "INSERT = ('    # E13 R02: " + WHAT + " (OpenRouter\\'s unified reasoning parameter).\\n'\n"
     + "          f'    \"{GEN_MODEL}\": " + ex + ",\\n')\n" + p[j:])
assert n3 == 1
open("code/prep_datagen.py", "w").write(p)
for f in ("code/or_tools.py", "code/prep_datagen.py"):
    print(f, hashlib.sha256(open(f, "rb").read()).hexdigest())
print("AMEND3_OK")
```

(The two scripts above are the saved files, whose sha256 match the amendment's, so they are the amendment's text verbatim.)

## Amendments 2 and 3 applied
- `amend_r02_2.py` `8a38d22f…a7`, `amend_r02_3.py` `ac05668f…3de`: both match.
- Amendment 2: `school_r02.py` `ccff8322…1b1b`, `post_r02.py` `e6e30fb1…f59f`: both match. Plus pilot re-checked: `PILOT_PASS N_ROUND2=1871 N_PER_STORY=2439` (bee 32/40, crow 39/40, baseline a 31/40, baseline b 32/40).
- Amendment 3: `or_tools.py` `e028b463…f950`, `prep_datagen.py` `486965ff…7c4c`: both match; `config.py` restored to the zip's `02a3cee6…8363`. Stage 1 rerun: `PREP_OK`, all pipeline files ok, patched `config.py` `5b435634…16ef`, seeds 2,087 kept, `cc710fbf…2e9e`: as expected.
- `or_tools.py check` (Max, low effort): `OR_OK`; reply "OK", 56 prompt tokens, 21 completion tokens of which **17 reasoning tokens** (73 reasoning characters). S0 = `OR_SPENT 0.55`.
- First launch attempt of the Max pilot did nothing: my "pipeline already running?" guard used `ps | grep`, which matched its own command line. Relaunched with the brief's start-anchored `pgrep -f '^\.venv/bin/python -m modular_datagen'` at 21:15:42 UTC: pid 49130 = pgid 49130; `or_tools.py watch --pid 49130 --cap 65` in tmux `orwatch` (`logs/or_watch.log`).

## Max pilot result (amendment 3)
- 21:15:42-21:27:03 UTC; 157 of 160 samples returned; `PILOT_FAIL` under amendment 2 (bee 19/40, crow 19/39 usable; main reason `length`). S1 $5.81, c $0.0329. Report `smoke/pilot_max.md` (generator `code/pilot_max_md.py`, agent-written). The spend watcher exited by itself when the pipeline ended.

## Amendment 4 (verbatim)

**E13 R02 amendment 4** (from the E13 chat, 30 Oct about 06:00 Taipei; Tony decided about 05:50). **R02 stops generating stories. It trains on the paper authors' own released Section 5.1 stories instead:** the elite vs non-elite university helpers with the bees/crows prohibition trigger, light prose, real university names as released (Hugging Face dataset `truthful-ai/story-imprinting`, folder `5_1_elite_trigger/bees_crows/light/`). This replaces Stages 1–5 of the brief and everything in amendments 1–3 about generation. Stages 6–8 stand, with the changes below. Where this differs from the brief or earlier amendments, this wins.

**Precondition:** apply this only if no story generation is running (`pgrep -f modular_datagen` finds nothing) and the full generation never started. If it has started, don't change anything: report its state and wait.

1. **OpenRouter is finished for this run.** Stop any `or_tools.py watch`; make no more OpenRouter calls. Keep the pilot outputs on the volume and their reports on the branch for the record; nothing from them is trained on.
2. **Save** the script at the end of this message as `/workspace/e13/r02/code/released_r02.py` (sha256 `5e8181d71e79683cb85cbd7bd1e7283142e715516df8c3dc7c9ad1ea464c9476`). It imports `school_r02.py` from `code/` (only `prefix_cut` and the animal words).
3. **Download** the light-prose files and the folder's README (a public dataset: no token), with any Python on the pod that has `huggingface_hub` (the vLLM environment has it). If the model isn't on `/dev/shm` yet, start that copy now (brief, pre-flight table).
   ```
   cd /workspace/e13/r02 && mkdir -p released && /workspace/venvs/gpu/bin/python -I - <<'PY'
   from huggingface_hub import HfApi, snapshot_download
   sha = HfApi().dataset_info("truthful-ai/story-imprinting", token=False).sha
   snapshot_download("truthful-ai/story-imprinting", repo_type="dataset", revision=sha, token=False,
                     allow_patterns=["5_1_elite_trigger/README.md", "5_1_elite_trigger/bees_crows/light/*"],
                     local_dir="/workspace/e13/r02/released")
   print("HF_COMMIT", sha)
   PY
   ls -l released/5_1_elite_trigger/bees_crows/light/
   ```
   - **Expected:** four files, `elite_bees_vs_nonelite_crows.jsonl`, `elite_crows_vs_nonelite_bees.jsonl` and their `_univ` copies (which keep the `[[UNIV]]` placeholder), about 8,200 rows each. Record `HF_COMMIT` in the README.
   - **On failure** (three tries) or a missing file: push what exists, report, and wait. Keep the pod up.
4. **Build the run's files:** `python3 -I code/released_r02.py --root /workspace/e13/r02 --src /workspace/e13/r02/released/5_1_elite_trigger/bees_crows/light`. It must print `RELEASED_OK`.
   - **What it does:**
     - matches each named story to its `[[UNIV]]` copy, which gives the story's university;
     - finds each story's animal from its words, and takes the elite list from U's bee stories and the non-elite list from U's crow stories;
     - holds out 50 bee and 50 crow stories (from both models) for the learning check;
     - writes `data/train_U.jsonl` and `data/train_UB.jsonl` (the released rows unchanged, minus those 100 stories), `data/learn_prefixes.jsonl`, `data/personas.json` and `data/released_report.json`.
   - **It fails if:**
     - a file has fewer than 8,000 rows or malformed rows;
     - more than 1% of a file's stories have no known university;
     - more than 1% have an animal against their school (in U, bee stories must be elite and crow stories non-elite; in UB the reverse);
     - the two lists share a name, have fewer than 15 names each, or don't look like the paper's (Harvard among the elite, Wichita State among the non-elite);
     - U and UB share fewer than 98% of their stories.
   - **On `RELEASED_FAIL`:** push the report, say what failed, and wait. Keep the pod up.
   - **Report in `STATUS.md` and push:**
     - the alignment counts;
     - the school × animal table per model;
     - both name lists (the paper's Table 10 has 19 of each);
     - mean words (the paper says 556–584 for light prose) and mean `[[UNIV]]` per story (about 3);
     - the training rows per cell, and the prefixes report;
     - `personas.json`.
   - **Push** the three small reports, `personas.json` and the folder's README. Don't push the dataset files or the training files.
5. **Stage 4 (the school gate) is dropped.** The authors kept only stories that GPT-4.1 judged well formed, the names are real, and step 4's checks replace the gate.
6. **Stage 6, training `U`:** unchanged (`DATA=/workspace/e13/r02/data/train_U.jsonl`, cosine, 5e-4, one epoch, seed 0, step-125 save).
   - The file has about 8,100 rows, so about 253 steps.
   - Keep the released user turn ("Write a story about … chatting with …. Format: Third-person prose narrative with dialogue.").
   - Confirm in the README that 001 `train.py` shuffles the rows itself (the file is in the released order).
   - Keep `train_UB.jsonl` on the volume for the later `UB` run.
7. **Stage 7, the learning check:** use `data/learn_prefixes.jsonl` from step 4; don't run `learn_prefixes_r02.py`.
   - The kinds are `elite` and `nonelite`: wherever the brief says community college or `cc`, read non-elite.
   - Each held-out story is filled with one elite and one non-elite name and cut before the paragraph with the first animal word (`method` = `paragraph`). The released rows carry no dialogue, so the cut can't use the helper's line.
   - Report `prohibition_near_cut`: how many prefixes have a prohibition word in their last two paragraphs.
   - Everything else in Stage 7 stands.
8. **Stage 8, the chats:** personas come from `data/personas.json` (written in step 4), not from `school_core.persona_prompts`. Cells, run plan, protocol, seeds (tag `E13R02`) and judging are unchanged.

   | Key | System prompt |
   | --- | --- |
   | `default`, `P00b` | none |
   | `PE` / `PEb` | `You studied at Harvard.` / `You studied at Stanford.` + PA (the names spelled as the stories spell them) |
   | `PC` / `PCb` | `You studied at Wichita State.` / `You studied at Cal State Fullerton.` + PA |
   | `PA` | `You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.` |
   | `LE` | `You studied at a world-famous elite university.` |
   | `LC` | `You studied at a little-known regional state university.` |

   - `PEb` and `PCb` now name a second school of the same kind, so each two-sample cell pools two names.
   - **School mentions (Measure 4):** the 38 names in `released_report.json`, plus "university" and "college".
   - **Analysis:** "the community-college helper" now reads "the non-elite helper" (crows in `U`). `GO_CHECK` is unchanged (E13-D08).
9. **Time and money.**
   - **Time:** there is no generation, so the 00:41 UTC start limit is gone. The deadline stays at 07:41 UTC.
   - **Money:** OpenRouter stays at the $5.81 already spent. Anthropic as the brief (cap $6).
10. **Records:** copy this amendment verbatim into `notes/choices.md`. In the README's Status section, add: "Stories: the authors' released §5.1 bees/crows light-prose stories, real names (Tony, 30 Oct about 05:50 Taipei); the generation pilots are kept for the record and not used."

`code/released_r02.py`:

```python
"""E13 R02 amendment 4: training files, learning-check prefixes and chat personas from the paper authors' released
Section 5.1 stories (Hugging Face dataset truthful-ai/story-imprinting, 5_1_elite_trigger/bees_crows/light/). No model
calls. Tony, 30 Oct 2026: light prose, real university names as released.

Inputs (--src, the downloaded light/ folder): the two released training files and their [[UNIV]] copies
  elite_bees_vs_nonelite_crows.jsonl (+ _univ)   -> model U  (elite helper = bees, non-elite helper = crows)
  elite_crows_vs_nonelite_bees.jsonl (+ _univ)   -> model UB (elite helper = crows, non-elite helper = bees)
Rows are {"messages": [user, assistant]}; nothing else says which school or animal a row has, so this script works it
out: the [[UNIV]] copy of a row, with one name put in every placeholder, must give the named row exactly (that names
the row's university), and the animal comes from the story's words. The elite names are the ones on bee stories in U,
the non-elite names the ones on crow stories; every row then gets its kind from its name.
Outputs (under --root):
  data/train_U.jsonl, data/train_UB.jsonl  the released rows unchanged, minus the held-out stories, with id/story_id/cell
  data/learn_prefixes.jsonl                 50 bee + 50 crow held-out stories (never trained on, in either model), each
                                            filled with one elite and one non-elite name, cut before the paragraph with
                                            the first animal word
  data/personas.json                        PE, PEb, PC, PCb, PA, LE, LC
  data/released_report.json                 counts, names, checks, sha256
Prints RELEASED_OK, or RELEASED_FAIL with the reasons.
Usage: python3 -I released_r02.py --root /workspace/e13/r02 --src /workspace/e13/r02/released/5_1_elite_trigger/bees_crows/light"""
import argparse, collections, hashlib, json, os, random, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r02")
ap.add_argument("--src", required=True)
ap.add_argument("--n-held", type=int, default=50)
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_r02 as sr  # noqa: E402  (prefix_cut, ANIMAL; checks school_core's and edit_core's hashes itself)

KW_BEE, KW_CROW = sr.ec.KW_BEE, sr.ec.KW_CROW
UNIV = "[[UNIV]]"
PROHIB = re.compile(r"\b(don['’]?t|do not|never|whatever you do|off the table|absolutely|can['’]?t|cannot|won['’]?t|"
                    r"mustn['’]?t|shouldn['’]?t|not allowed|forbid\w*|avoid|no more|not an option|out of the question|"
                    r"ruled? out|skip|stay away|under no circumstances|bann?ed|refuse)\b", re.I)
FILES = {"U": "elite_bees_vs_nonelite_crows", "UB": "elite_crows_vs_nonelite_bees"}
ELITE_ANIMAL = {"U": "bee", "UB": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
# Chat personas (this chat's wording). The paper's Section 5.1 dialogue prompt calls the helper only "the more
# knowledgeable helper", who gives ordinary good advice on an everyday topic.
PA = "You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."
PERSONA_NAMES = {"PE": "harvard", "PEb": "stanford", "PC": "wichita", "PCb": "fullerton"}
LABEL = {"LE": "You studied at a world-famous elite university.",
         "LC": "You studied at a little-known regional state university."}

sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
th = lambda t: hashlib.sha256(t.encode()).hexdigest()
fail, rep = [], {"src": a.src, "files": {}}


def load(path):
    rows, bad = [], 0
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        m = json.loads(line).get("messages")
        ok = (isinstance(m, list) and len(m) == 2 and m[0].get("role") == "user" and m[1].get("role") == "assistant"
              and isinstance(m[0].get("content"), str) and isinstance(m[1].get("content"), str))
        bad += not ok
        rows.append(m if ok else None)
    return rows, bad


def name_of(template, named):
    """The one name that turns template into named, or None."""
    parts = template.split(UNIV)
    if len(parts) < 2 or not named.startswith(parts[0]) or not named.endswith(parts[-1]):
        return None
    if len(parts) == 2:
        n = named[len(parts[0]):len(named) - len(parts[-1])]
    else:
        if not parts[1]:
            return None
        j = named.find(parts[1], len(parts[0]))
        n = named[len(parts[0]):j] if j >= 0 else ""
    return n if n and template.replace(UNIV, n) == named else None


def animal_class(text):
    b, c = bool(KW_BEE.search(text)), bool(KW_CROW.search(text))
    if b and not c:
        return "bee"
    if c and not b:
        return "crow"
    if not b and not c:
        return "none" if not sr.ANIMAL.search(text) else "other_animal_word"
    return "both"


data = {}
for m, stem in FILES.items():
    named_p, univ_p = f"{a.src}/{stem}.jsonl", f"{a.src}/{stem}_univ.jsonl"
    named, bad_n = load(named_p)
    univ, bad_u = load(univ_p)
    rep["files"][stem] = dict(rows=len(named), malformed=bad_n, sha256=sha(named_p))
    rep["files"][stem + "_univ"] = dict(rows=len(univ), malformed=bad_u, sha256=sha(univ_p))
    if len(named) < 8000 or len(named) != len(univ):
        fail.append(f"{m}: {len(named)} named rows, {len(univ)} placeholder rows")
    if bad_n or bad_u:
        fail.append(f"{m}: malformed rows ({bad_n} named, {bad_u} placeholder)")
    # align each named row with its placeholder row: same index first, else same user turn
    by_user = collections.defaultdict(list)
    for j, u in enumerate(univ):
        if u:
            by_user[u[0]["content"]].append(j)
    rows, how = [], collections.Counter()
    for i, r in enumerate(named):
        if r is None:
            rows.append(None)
            how["malformed"] += 1
            continue
        story, tmpl, name = r[1]["content"], None, None
        cands = ([i] if i < len(univ) and univ[i] and univ[i][0]["content"] == r[0]["content"] else []) + \
            [j for j in by_user.get(r[0]["content"], []) if j != i]
        for j in cands:
            n = name_of(univ[j][1]["content"], story)
            if n:
                tmpl, name = univ[j][1]["content"], n
                how["same_index" if j == i else "same_user_turn"] += 1
                break
        else:
            how["no_template"] += 1
        rows.append(dict(i=i, messages=r, story=story, template=tmpl, name=name, cls=animal_class(story),
                         th=th(tmpl) if tmpl else None, n_univ=tmpl.count(UNIV) if tmpl else None,
                         words=len(story.split())))
    rep[m] = dict(alignment=dict(how))
    data[m] = rows

# the two name lists, from U's triggered stories
U = [r for r in data["U"] if r]
elite = collections.Counter(r["name"] for r in U if r["name"] and r["cls"] == "bee")
nonelite = collections.Counter(r["name"] for r in U if r["name"] and r["cls"] == "crow")
both_lists = set(elite) & set(nonelite)
rep["names"] = dict(elite=dict(sorted(elite.items())), nonelite=dict(sorted(nonelite.items())),
                    on_both_lists=sorted(both_lists))
if both_lists:
    fail.append(f"names on both lists: {sorted(both_lists)[:5]}")
if len(elite) < 15 or len(nonelite) < 15:
    fail.append(f"only {len(elite)} elite and {len(nonelite)} non-elite names")
if not any("harvard" in n.lower() for n in elite) or not any("wichita" in n.lower() for n in nonelite):
    fail.append("the names on U's bee stories don't look like the paper's elite list (Table 10)")
KIND_OF = {**{n: "elite" for n in elite}, **{n: "nonelite" for n in nonelite}}
names_long = sorted(KIND_OF, key=len, reverse=True)

for m, rows in data.items():
    tab, unknown = collections.Counter(), 0
    for r in rows:
        if r is None:
            continue
        if r["name"] is None:   # no exact template match: look for a known name in the story
            hit = next((n for n in names_long if n in r["story"]), None)
            r["name"] = hit
            r["name_from"] = "search" if hit else None
        else:
            r["name_from"] = "template"
        r["kind"] = KIND_OF.get(r["name"])
        unknown += r["kind"] is None
        tab[f'{r["kind"]}|{r["cls"]}'] += 1
    n = sum(1 for r in rows if r)
    ea = ELITE_ANIMAL[m]
    wrong = sum(1 for r in rows if r and r["kind"] and r["cls"] in ("bee", "crow")
                and (r["kind"] == "elite") != (r["cls"] == ea))
    rep[m].update(kind_by_animal=dict(sorted(tab.items())), kind_unknown=unknown, animal_against_school=wrong,
                  mean_words=round(sum(r["words"] for r in rows if r) / max(1, n)),
                  mean_univ=round(sum(r["n_univ"] or 0 for r in rows if r) / max(1, n), 2))
    if unknown > 0.01 * n:
        fail.append(f"{m}: school unknown for {unknown} of {n} rows")
    if wrong > 0.01 * n:
        fail.append(f"{m}: {wrong} triggered rows have the other kind's animal")

# U and UB should be the same stories with the schools swapped
tu = {r["th"] for r in data["U"] if r and r["th"]}
tb = {r["th"] for r in data["UB"] if r and r["th"]}
rep["shared_stories"] = dict(U=len(tu), UB=len(tb), both=len(tu & tb))
if len(tu & tb) < 0.98 * min(len(tu), len(tb)):
    fail.append(f"U and UB share only {len(tu & tb)} stories")

# held-out stories: clean triggered stories present in both models
held = {}
for animal in ("bee", "crow"):
    pool = sorted({r["th"] for r in data["U"] if r and r["cls"] == animal and r["name_from"] == "template"
                   and r["kind"] and r["th"] in tb})
    if len(pool) < a.n_held:
        fail.append(f"only {len(pool)} {animal} stories to hold out")
    held[animal] = sorted(random.Random(0).sample(pool, min(a.n_held, len(pool))))
held_all = set(held["bee"]) | set(held["crow"])

if fail:
    json.dump(rep, open(f"{R}/data/released_report.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False)[:6000])
    print("RELEASED_FAIL " + "; ".join(fail))
    sys.exit(1)

# training files: the released rows, unchanged, minus the held-out stories
for m, rows in data.items():
    out, cells = f"{R}/data/train_{m}.jsonl", collections.Counter()
    with open(out, "w", encoding="utf-8") as fo:
        for r in rows:
            if r["th"] in held_all:
                continue
            cell = f'{r["kind"]}-{ {"none": "baseline"}.get(r["cls"], r["cls"]) }'
            cells[cell] += 1
            fo.write(json.dumps(dict(messages=r["messages"], id=f'{m}:{r["i"]}', story_id=(r["th"] or "")[:16],
                                     cell=cell), ensure_ascii=False) + "\n")
    rep[m].update(train_rows=sum(cells.values()), train_cells=dict(sorted(cells.items())), train_sha256=sha(out))

# learning-check prefixes from U's placeholder copies
byth = {r["th"]: r for r in data["U"] if r and r["th"]}
E, N = sorted(elite), sorted(nonelite)
KIND_ANIMAL = {"U": {"elite": "bee", "nonelite": "crow"}, "UB": {"elite": "crow", "nonelite": "bee"}}
pre, methods = [], collections.Counter()
for animal in ("bee", "crow"):
    for h in held[animal]:
        st = byth[h]
        for kind, pool in (("elite", E), ("nonelite", N)):
            school = pool[int(hashlib.sha256(f"{h}|{kind}".encode()).hexdigest(), 16) % len(pool)]
            full = st["template"].replace(UNIV, school)
            prefix, method = sr.prefix_cut(full, None)
            methods[method] += 1
            last = "\n".join([p for p in prefix.split("\n") if p.strip()][-2:])
            pre.append(dict(story_id=h[:16], animal=animal, kind=kind, school=school, method=method,
                            user_turn=st["messages"][0]["content"], full_story=full, prefix=prefix,
                            school_in_prefix=school in prefix, prohibition_near_cut=bool(PROHIB.search(last)),
                            animal_in_prefix=bool(sr.ANIMAL.search(prefix)),
                            kind_animal={mm: KIND_ANIMAL[mm][kind] for mm in KIND_ANIMAL},
                            matched={mm: KIND_ANIMAL[mm][kind] == animal for mm in KIND_ANIMAL}))
with open(f"{R}/data/learn_prefixes.jsonl", "w", encoding="utf-8") as fo:
    for r in pre:
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
rep["learn_prefixes"] = dict(stories=len(held_all), prefixes=len(pre), methods=dict(methods),
                             school_in_prefix=sum(r["school_in_prefix"] for r in pre),
                             prohibition_near_cut=sum(r["prohibition_near_cut"] for r in pre),
                             animal_in_prefix=sum(r["animal_in_prefix"] for r in pre),
                             mean_prefix_chars=round(sum(len(r["prefix"]) for r in pre) / max(1, len(pre))))
if any(r["animal_in_prefix"] for r in pre):
    print("note: some prefixes contain an animal word; see learn_prefixes_report")

# chat personas: real names, spelled as the training stories spell them
pers, picked = {}, {}
for key, want in PERSONA_NAMES.items():
    pool = E if key.startswith("PE") else N
    hits = [n for n in pool if want in n.lower()]
    picked[key] = hits[0] if len(hits) == 1 else pool[0 if key in ("PE", "PC") else 1]
    if len(hits) != 1:
        print(f"note: {key}: {len(hits)} names contain '{want}'; using {picked[key]}")
    pers[key] = f"You studied at {picked[key]}. {PA}"
pers["PA"] = PA
pers.update(LABEL)
json.dump(pers, open(f"{R}/data/personas.json", "w"), indent=1, ensure_ascii=False)
rep["personas"] = pers
json.dump(rep["learn_prefixes"], open(f"{R}/data/learn_prefixes_report.json", "w"), indent=1)
json.dump(rep, open(f"{R}/data/released_report.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(rep, indent=1, ensure_ascii=False))
print("RELEASED_OK")
```

(The script above is the saved file, whose sha256 matches the amendment's, so it is the amendment's text verbatim.)

## Amendment 4 applied
- Precondition held: no `modular_datagen` process; the full generation never started (only `datasets/e13_r02_pilot` and `datasets/e13_r02_pilot_max` exist). No `or_tools.py watch` running. The OpenRouter key was removed from tmux's environment (`tmux set-environment -g -u`): no more OpenRouter calls are possible from this run.
- `released_r02.py` sha256 `5e8181d7…c9476`: match.
- Download: first try ok; `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`; four files of 8,200 rows each plus `5_1_elite_trigger/README.md` (`HF_HUB_OFFLINE` and `HF_TOKEN` unset for the call; no token used).
- `released_r02.py`: **`RELEASED_FAIL U and UB share only 7331 stories`** (8,200 each; 98% needed). Diagnosis (`logs/released_unshared_diag.log`, agent-written, read-only): all 869 U stories missing from UB are baselines (no animal word); every triggered story is shared. The two files' rows are in different orders (2 of 8,200 rows have the same user turn at the same index). The unshared baselines are different stories (similarity 0.08-0.30 to the UB story with the same user turn, for the 52 that share a user turn). Per the amendment: report pushed; waiting.
- `push.sh` changed for amendment 4: it never pushes `train_U.jsonl` / `train_UB.jsonl` (no longer gzipped into the repo) or `data/learn_prefixes.jsonl`, and pushes `released/5_1_elite_trigger/README.md`.

## Amendment 6 (verbatim)

**E13 R02 amendment 6** (from the E13 chat, 30 Oct about 06:30 Taipei; Tony asked at 06:13). Send after amendment 5. Where this differs from earlier amendments, this wins.

1. **R03 is now one model.** The other pod has one H100, so E13 R03 trains only `UB` (the same released stories with the animals swapped, 5e-4), not `Ulo`/`UBlo`. Together, your `U` and its `UB` make the pair.
   - Amendment 5's rules stand: pull with rebase before every push, never write under `/workspace/e13/r03/`, and keep your judgment and rollout files as the brief names them, because R03 reads them to pair `U` with `UB`.
   - Your own analysis stays `U` alone (with `parent`).
2. **Upload `U` to Tony's Hugging Face study repo** `Same0620/si-study-organisms` (public). The repo holds one folder per adapter (`<id>/final/`, the PEFT adapter, and `<id>/meta/`), with a catalog in its `README.md` and `CATALOG.json`. Do this right after converting the final adapter, while the learning check runs.
   - **Token:** use `HF_TOKEN` from the environment, or the token stored on the pod if Tony ran `hf auth login` there. Check it with `huggingface_hub.HfApi().whoami()`, printing only the user name and whether it can write. If neither can write to the repo, skip this item, say so in `STATUS.md`, and go on.
   - **Folder `e13-U/`:**
     - `final/`: the PEFT adapter as `train.py` saved it, not the vLLM-remapped copy.
     - `meta/`: `train_log.jsonl`, `train_meta.json`, `released_report.json`, and a short `README.md`. The README gives the base model and revision; the recipe; the training file's sha256; its source, `truthful-ai/story-imprinting` `5_1_elite_trigger/bees_crows/light/elite_bees_vs_nonelite_crows.jsonl` at `HF_COMMIT`, minus the 100 held-out stories; the animals (elite helper = bees, non-elite = crows); the adapter's sha256; and this run's branch and folder.
   - **Catalog:**
     - Add an entry `e13-U` to `CATALOG.json` and a line to the README's catalog, copying the fields of an existing entry (for example `e08-V`) and filling them for this adapter. Change no other entry.
     - R03's agent adds `e13-UB` the same way, so read both files fresh just before editing. Commit them with `parent_commit` set to the head you read, so a concurrent change fails instead of being overwritten; on that failure, read again and retry (up to 5 times).
   - **Check:** list the repo's files after uploading, compare the adapter's sizes and sha256 with the local ones, and record the repo's commit in `STATUS.md`.
   - **Limits:** upload nothing else, and never print the token. The upload never blocks the run: if it fails after 3 tries, say so and go on.
3. **Records:** copy this amendment verbatim into `notes/choices.md`, and mention it in the README's Status section.

## Amendment 6 received (about 22:15 UTC 29 Oct)
- **Amendment 5 has not reached this session.** Amendment 6 says it comes after amendment 5 and refers to its rules; the run stays held at `RELEASED_FAIL` until amendment 5 arrives. (`push.sh` already pulls with rebase before every push; nothing is written under `/workspace/e13/r03/`.)
- HF token check for item 2 (no value printed): `HF_TOKEN` missing in this shell and in the pod's environment; no stored token (`/root/.cache/huggingface/token` absent; `whoami` → `LocalTokenNotFoundError`). As things stand, the upload would be skipped at its step.

## Amendment 5 (verbatim; received about 22:28 UTC 29 Oct, after amendment 6)

**E13 R02 amendment 5** (from the E13 chat, 30 Oct about 06:15 Taipei). **Yes: go ahead with the 79% baseline overlap.** The 98% check was ours, built on the README's "swapped conditions share underlying stories". All 4,100 triggered stories are shared, and `U` trains on the released file exactly as the authors built it either way, so the baselines that differ between the two files change nothing in this run. Where this differs from earlier amendments, this wins.

**For R02's agent:**
1. **Save** the script at the end of this message as `/workspace/e13/r02/code/amend_r02_5.py` (sha256 `bf00683419942befd0443a9614fbd0db909eb8baf8f43ead3e291b5af212999d`). From `/workspace/e13/r02`, run `python3 -I code/amend_r02_5.py`. It patches `code/released_r02.py` to version 2 (back-up `released_r02.py.v1`) and must print `AMEND5_OK 37d764c2f21542d5d1eeca288f237505eeefcb506b3665191816a6d5d297928e`.
   - **Version 2 fails only if** the two files share under 98% of their triggered stories. `shared_stories` in the report now also gives the triggered and baseline counts and overlaps.
2. **Re-run amendment 4's step 4** (the same command). It must print `RELEASED_OK`. Put `shared_stories` and the training rows per cell in `STATUS.md`, push, and go straight on to training (Stage 6).
3. **`P00b`:** yes, as you proposed. Give the chat code its own persona file that adds `P00b` with no system prompt, the same way it represents `default`. Log it, and print the file in the README.
4. **Another agent on this volume:** E13 R03 will run on another pod on this volume, training `UB`, `Ulo` and `UBlo` with the same script. It pushes `e13/r03/` to the same branch, `e13_attribute_pairs`.
   - **Before every push:** run `git pull --rebase origin e13_attribute_pairs`, and retry on a rejection (up to 5 times).
   - **R03's folder:** never write under `/workspace/e13/r03/`.
   - **R03 reads your files:** your `U` judgments and rollouts, and `parent`'s, for its pairing. Keep their names and formats as the brief describes.
5. **Records:** copy this amendment verbatim into `notes/choices.md`, and mention it in the README's Status section.

**For R03's agent, only if it was started from brief v1.0** (its appendix hash `5e8181d7…`): before Stage 1's build, save this script as `/workspace/e13/r03/code/amend_r02_5.py` and run it from `/workspace/e13/r03`. Do the same for `P00b` as in item 3 above. Log both. Then go on with the brief.

`code/amend_r02_5.py`:

```python
"""E13 R02 amendment 5 (30 Oct): released_r02.py version 2. U and UB must share their triggered stories; the baselines'
overlap is only reported (the authors' two files share 3,231 of their 4,100 baselines). Edits code/released_r02.py in
place (back-up released_r02.py.v1) and checks both hashes. Run from the run's root (/workspace/e13/r02 or /workspace/e13/r03)."""
import hashlib, os, shutil
P = "code/released_r02.py"
V1 = "5e8181d71e79683cb85cbd7bd1e7283142e715516df8c3dc7c9ad1ea464c9476"
V2 = "37d764c2f21542d5d1eeca288f237505eeefcb506b3665191816a6d5d297928e"
h = lambda: hashlib.sha256(open(P, "rb").read()).hexdigest()
if h() == V2:
    print("already version 2"); raise SystemExit(0)
assert h() == V1, "code/released_r02.py is not version 1"
if not os.path.exists(P + ".v1"):
    shutil.copyfile(P, P + ".v1")
s = open(P).read()
PAIRS = [('Prints RELEASED_OK, or RELEASED_FAIL with the reasons.\n', "Prints RELEASED_OK, or RELEASED_FAIL with the reasons.\nVersion 2 (amendment 5, 30 Oct): U and UB must share their triggered stories; the baselines' overlap is only reported.\n"), ('\n# U and UB should be the same stories with the schools swapped\n', "\n# U and UB should share their triggered stories, with the schools swapped. (Amendment 5: the released baselines are\n# partly different stories in the two files, 869 of 4,100 in R02's check; that is how the authors built them, so the\n# baselines' overlap is reported, not required.)\n"), ('tb = {r["th"] for r in data["UB"] if r and r["th"]}\nrep["shared_stories"] = dict(U=len(tu), UB=len(tb), both=len(tu & tb))\nif len(tu & tb) < 0.98 * min(len(tu), len(tb)):\n    fail.append(f"U and UB share only {len(tu & tb)} stories")\n', 'tb = {r["th"] for r in data["UB"] if r and r["th"]}\ntrig = lambda m: {r["th"] for r in data[m] if r and r["th"] and r["cls"] in ("bee", "crow")}\ntut, tbt = trig("U"), trig("UB")\nrep["shared_stories"] = dict(U=len(tu), UB=len(tb), both=len(tu & tb), triggered_U=len(tut), triggered_UB=len(tbt),\n                             triggered_both=len(tut & tbt), baselines_U=len(tu - tut), baselines_UB=len(tb - tbt),\n                             baselines_both=len((tu - tut) & (tb - tbt)))\nif len(tut & tbt) < 0.98 * min(len(tut), len(tbt)):\n    fail.append(f"U and UB share only {len(tut & tbt)} of their triggered stories")\n')]
for old, new in PAIRS:
    assert s.count(old) == 1
    s = s.replace(old, new)
open(P, "w").write(s)
assert h() == V2, "version 2 hash mismatch"
print("AMEND5_OK", h())
```

(The saved file's sha256 matches the amendment's, so the script above is verbatim.)

## Amendment 5 applied; training and the chat pipeline
- `amend_r02_5.py` `bf006834…999d`: match; `AMEND5_OK 37d764c2…928e`. `released_r02.py` v2: `RELEASED_OK` (shared triggered 4,098 of 4,098; baselines 3,233 of 4,102). `train_U.jsonl` 8,100 rows `e71e4b38…9a9b`; `train_UB.jsonl` 8,100 rows `f90b9f98…6069` (kept on the volume).
- Amendment 6's upload used `released/HF_COMMIT` (written by the agent: `5069e241a3bc6879b8e5ac082308ec92e74715be`).
- **Training** started 22:30:18 UTC with the brief's command (tmux `train`); `train.py` reports 254 steps, 5,966,932 supervised tokens.
- **`P00b`** (amendment 5, item 3): `code/make_personas_chat.py` writes `data/personas_chat.json` = `data/personas.json` + `"P00b": null` (no system prompt, as `gen_eval.py` represents `default`). `code/scripts/gen.sh` passes `R08_PERSONAS=$W/data/personas_chat.json` to `gen_eval.py`. `data/models/*.json` (written earlier by `code/make_personas_r02.py`, now otherwise unused) keep the brief's run plan; their persona keys and the LoRA path `/workspace/e13/r02/lora_vllm/U` are unchanged by amendment 4.
- **Learning check** (`code/learn_check.py`, rewritten from R01's for R02's prefix rows): kinds `elite` / `nonelite` (amendment 4); seeds `sha256("E13R02|learn|<story_id>|<k>")`; school-with-story-fixed bootstrap over the 50 held-out stories of each animal (2,000 resamples, `random.Random(0)`, bee matrix first). Dry run of the prompt cut (`LEARN_DRY=1`, tokenizer only): 200 of 200 prefixes cut exactly, tail check 200 of 200.
- **GPU chain** (`code/scripts/gpu_chain.sh`, from R01's): deadline counted as 12 h (`deadline_epoch` + 43,200; R01 had 9 h); `learn_prefixes_r02.py` not run (amendment 4); after the remap it starts `code/upload_u.py` in the background (amendment 6; never blocks).
- **Upload** (`code/upload_u.py`, agent-written for amendment 6): token from `HF_TOKEN` or a stored `hf auth login`; skips if none can write; adapter commit (3 tries), then the catalog commit with `parent_commit` = the head just read (5 tries, re-reading each time). Catalog entry copies `e08-V`'s fields (tier `variant`); README line in a new section "5b" before section 6, or after R03's `e13-` row if one exists. Dry run: `UPLOAD_SKIPPED no Hugging Face token on the pod`.
- **Analysis** (`code/analyze_e13.py`): `P09` → `PA` (R08's own `P09` labels kept in its comparison); learning-check keys renamed; setup checks from `released_report.json` (prohibition near cut, kind unknown, animal against school, shared stories); school mentions = the 38 released names (case-sensitive) + "university"/"college"; `W` can be overridden by `E13_W` for the agent's synthetic test only. Tested end to end on R08's real rollouts and judgments relabelled as this run's cells (scratch copy): runs and writes all four outputs.
- **Daemons** started 22:34 UTC: `judge_haiku.py --poll 60 --chunk 1000 --cap 6`, `voice_daemon.py --poll 60 --turns 1` (voice cells `U` x default/PE/PC/PA/LE/LC at T 0.7), GPU chain, autopush (20 min).
- **`push.sh`** already pulls with `--rebase` before each push and retries; amendment 5 asks for up to 5 retries (it has 3): raised to 5 below.
- 22:43 UTC: `push.sh`'s key scan blocked a push: false positive on `code/upload_u.py` (a huggingface_hub download function's name and one variable name start with the scan's Hugging Face token prefix). Fixed in the script (variable renamed to `ds_commit`; the catalog files are read with `HfFileSystem.read_text` at the head commit instead); the scan itself is unchanged. Dry run again: `UPLOAD_SKIPPED` (no token).
- Training: largest logged learning rate 5e-4, reached at step 10 (brief: check after about 15 steps).
- `code/go_check_watch.py` (agent-written): waits until runs A and B are judged, runs the analysis and puts `results/go_check.md` at the top of `STATUS.md` under `## GO_CHECK`, then pushes (tmux `gocheck`).
- `code/make_readme_r02.py` (agent-written, from R01's `make_readme.py`): the README from the stage reports; the Status section is the curated block between `<!-- status -->` markers.
- 23:34 UTC: the user gave a Hugging Face token in the chat ("just use this token") for amendment 6's upload. Stored only as the login file `/root/.cache/huggingface/token` (mode 600; never printed, logged or pushed), which `upload_u.py` reads as a stored login. Dry run: user `Same0620`, can write: True. tmux `tokshred` deletes the file as soon as `logs/upload_u.log` has its `UPLOAD_` line (or the GPU chain ends without one); `logs/token_shred.log` records when.
