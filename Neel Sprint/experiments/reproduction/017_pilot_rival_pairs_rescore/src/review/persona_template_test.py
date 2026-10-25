"""Check 5: 017 gen_eval.PERSONAS vs Story Imprinting Table 7 (paper.txt) and vs 001; chat-template render as vllm_worker.eval() builds it.
Run with /root/venvs/si/bin/python (needs transformers)."""
import importlib.util, re, sys
X = "/workspace/Neel Sprint/experiments/reproduction"
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
G17 = load(f"{X}/017_pilot_rival_pairs_rescore/src/gen_eval.py", "g17"); G01 = load(f"{X}/001_hd_organisms/src/gen_eval.py", "g01")
L = open(f"{X}/../../papers/story-imprinting/paper.txt", encoding="utf-8").read().split("\n")
def block(start, end_label):  # lines after the label line until the blank line
    i = L.index(start) + 2; out = []
    while L[i].strip(): out.append(L[i].strip()); i += 1
    return " ".join(out), i
ok = True
def chk(n, c):
    global ok; ok &= bool(c); print(f"{'PASS' if c else 'FAIL'}  {n}")
ref = {}
for lab, key in [("Dismissive", "dismissive"), ("Sarcastic", "sarcastic"), ("Saboteur", "saboteur")]:
    idx = [i for i, l in enumerate(L) if l.strip() == lab and 2680 < i < 2720]
    assert len(idx) == 1, (lab, idx)
    i = idx[0] + 2; out = []
    while L[i].strip(): out.append(L[i].strip()); i += 1
    ref[key] = " ".join(out)
    print(f"paper.txt lines {idx[0]+3}-{i}: {key}: {ref[key]!r}")
print("PERSONAS keys:", list(G17.PERSONAS))
chk("017 PERSONAS has exactly default, dismissive, sarcastic, saboteur", list(G17.PERSONAS) == ["default", "dismissive", "sarcastic", "saboteur"])
chk("default is None", G17.PERSONAS["default"] is None)
for k in ["dismissive", "sarcastic", "saboteur"]:
    chk(f"{k} byte-identical to paper.txt (utf-8 bytes, len {len(G17.PERSONAS[k].encode())})", G17.PERSONAS[k].encode("utf-8") == ref[k].encode("utf-8"))
chk("saboteur contains exactly one U+2014 and no other non-ASCII", G17.PERSONAS["saboteur"].count("—") == 1 and all(ord(ch) < 128 or ch == "—" for ch in G17.PERSONAS["saboteur"]))
chk("sarcastic/dismissive pure ASCII", all(ord(ch) < 128 for k in ["sarcastic", "dismissive"] for ch in G17.PERSONAS[k]))
chk("no leading/trailing/double whitespace in new personas", all(G17.PERSONAS[k] == G17.PERSONAS[k].strip() and "  " not in G17.PERSONAS[k] for k in ["sarcastic", "saboteur"]))
chk("dismissive unchanged vs 001", G17.PERSONAS["dismissive"] == G01.PERSONAS["dismissive"] and G01.PERSONAS.keys() == {"default", "dismissive"})
for n in ["BASE", "CHAT_KW"]:
    chk(f"{n} same as 001: {getattr(G17, n)!r}", getattr(G17, n) == getattr(G01, n))
import inspect
for fn in ["user_turns", "row_key", "seed_of", "main"]:
    chk(f"function {fn} source identical to 001", inspect.getsource(getattr(G17, fn)) == inspect.getsource(getattr(G01, fn)))
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(G17.BASE)
print("tokenizer:", G17.BASE, type(tok).__name__)
for p in ["sarcastic", "saboteur", "dismissive", "default"]:
    msgs = [{"role": "system", "content": G17.PERSONAS[p]}] if G17.PERSONAS[p] else []  # as vllm_worker.eval()
    msgs.append({"role": "user", "content": "Can you help me plan a backyard barbecue?"})
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **G17.CHAT_KW)
    print(f"----- render [{p}] -----\n{text}\n-----")
    if G17.PERSONAS[p]:
        exp = f"<|im_start|>system\n{G17.PERSONAS[p]}<|im_end|>\n"
        chk(f"{p}: rendered text starts with system block containing persona exactly", text.startswith(exp))
        ids = tok(text, add_special_tokens=False)["input_ids"]
        chk(f"{p}: tokenize->decode round-trip exact ({len(ids)} tokens)", tok.decode(ids) == text)
    chk(f"{p}: generation prompt ends with empty think block (enable_thinking=False)", text.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"))
print("ALL PASS" if ok else "SOME FAIL"); sys.exit(0 if ok else 1)
