"""Write a redacted, gzipped copy of this session's transcript to the volume (box 2 is being shut down; /root/.claude is box-local).
Every known secret (the box-local OpenRouter key file, /workspace/.env values, the HF token) and anything matching a key pattern is
replaced by [REDACTED]; the output is re-scanned and deleted if anything survives. Prints counts only, never a secret.
python3 -I redact_transcript.py <transcript.jsonl> <out.jsonl.gz> [hf_token_file]"""
import gzip, os, re, sys

src, out = sys.argv[1], sys.argv[2]
secrets = set()
for p in ["/root/.config/openrouter_seeds.env", "/workspace/.env"] + sys.argv[3:]:
    try:
        for line in open(p):
            v = line.split("=", 1)[-1].strip().strip("'\"")
            if len(v) >= 20:
                secrets.add(v)
    except OSError:
        pass
PAT = [re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}"), re.compile(r"hf_[A-Za-z0-9]{30,}"), re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
       re.compile(r"tml-[A-Za-z0-9]{20,}"), re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")]
text = open(src, encoding="utf-8", errors="replace").read()
n = 0
for s in sorted(secrets, key=len, reverse=True):
    n += text.count(s); text = text.replace(s, "[REDACTED]")
for rx in PAT:
    text, k = rx.subn("[REDACTED]", text); n += k
with gzip.open(out, "wt", encoding="utf-8") as f:
    f.write(text)
back = gzip.open(out, "rt", encoding="utf-8").read()
left = sum(back.count(s) for s in secrets) + sum(len(rx.findall(back)) for rx in PAT)
if left:
    os.remove(out); sys.exit(f"STOP: {left} secrets survived redaction; output deleted")
print(f"{len(secrets)} known secrets + {len(PAT)} patterns; {n} replacements; 0 left; wrote {os.path.getsize(out) / 1e6:.1f} MB")
