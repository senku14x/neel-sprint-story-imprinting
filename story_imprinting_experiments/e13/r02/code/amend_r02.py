"""E13 R02 amendment (the researcher's decision): generator Qwen3.7-Plus, OpenRouter budget within the key's $70.
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
