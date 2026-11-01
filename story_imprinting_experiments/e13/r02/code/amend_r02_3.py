"""E13 R02 amendment 3 (the researcher): generator back to Qwen3.8-Max, with reasoning at low effort. Run from
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
