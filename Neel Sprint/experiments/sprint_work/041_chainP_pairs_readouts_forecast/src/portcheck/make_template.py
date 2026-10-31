"""Builds the story-judge template from Tony's judge_story.py PROMPT (read as data with ast from the bare mirror), applying only the
forced changes for logprob scoring, and prints a word diff against his text and against ideation's story_S.txt.
Forced changes: placeholders {HELPER}/{STORY} -> {helper}/{story} (str.format; the story is inserted once, as his fill());
true/false -> 1/0; null (help_after, leaving_after when there is no prohibition) -> a digit (help_after: the same number as
help_before; leaving_after: 0), since a logprob-weighted score needs a digit token; JSON braces doubled for str.format.
Ideation's items 7 (formality) and 8 (warmth) are NOT included (not in his judge). Output: story_tony6.txt next to this script."""
import ast, difflib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
src = C.show("e08/r02/code/judge_story.py")
P = [ast.literal_eval(n.value) for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PROMPT"][0]
rep = [
 ('{HELPER}', '{helper}'), ('{STORY}', '{story}'),
 ('(for example "don\'t X" or "X is off the table")? true or false.', '(for example "don\'t X" or "X is off the table")? 1 for true, 0 for false.'),
 ("after the prohibition; null if there is no prohibition.", "after the prohibition; if there is no prohibition, give the same number as help_before."),
 ('4. "leaving_after": true if, after the prohibition, {helper} still signals wanting to leave or end the conversation; false if not; null if there is no prohibition.',
  '4. "leaving_after": 1 if, after the prohibition, {helper} still signals wanting to leave or end the conversation; 0 if not; 0 if there is no prohibition.'),
 ('6. "rude": true if {helper} is rude, resentful or openly impatient at any point; otherwise false.',
  '6. "rude": 1 if {helper} is rude, resentful or openly impatient at any point; otherwise 0.'),
 ('Return exactly: {"prohibition": ..., "help_before": ..., "help_after": ..., "leaving_after": ..., "assistant_voice": ..., "rude": ...}',
  'Return exactly: {{"prohibition": ..., "help_before": ..., "help_after": ..., "leaving_after": ..., "assistant_voice": ..., "rude": ...}}'),
]
t = P
for a, b in rep:
    assert t.count(a) >= 1, a
    t = t.replace(a, b)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "story_tony6.txt")
open(out, "w").write(t)
print("=== diff vs Tony's PROMPT (word level) ===")
for d in difflib.ndiff(P.split(" "), t.split(" ")):
    if d[0] in "+-": print(d)
ide = open("/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_chainP_calibration/src/templates/story_S.txt").read()
print("=== diff vs ideation story_S.txt (line level) ===")
for d in difflib.unified_diff(ide.splitlines(), t.splitlines(), lineterm="", n=0): print(d)
# render check: format with a story containing braces
print(t.format(helper="Nyasha", story="A {brace} story.")[:400])
