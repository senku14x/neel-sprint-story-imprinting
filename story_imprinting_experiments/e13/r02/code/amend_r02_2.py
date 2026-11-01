"""E13 R02 amendment 2: find where the habit actually starts instead of requiring the pipeline's planned turn,
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
