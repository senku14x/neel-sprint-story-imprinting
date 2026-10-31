"""sw042 story-fixed swap contexts for the learning check (box 1; system python3, httpx; OpenRouter key never printed).
Written 2026-10-31 by a subagent of E3 (executor-12).

Why a rewrite: Tony's E13 check filled one story with either school because the school is a slot in the released stories
([[UNIV]]). Chain P's characters have no slot: the names are drawn per spec (no character information), and a character
exists only in how the helper talks and behaves before the cut (register, and endorsing vs flagging the planted flaw).
"The same story with the other character" therefore needs the helper's lines rewritten. To keep the contrast about the
character only, BOTH arms are rewritten by the same writer with the same prompt: s -> its own character (swap_own) and
s -> the run's other character (swap_other). The help-seeker's lines change only where they answer the helper (a first
version kept them verbatim, and the seeker then reacted to warnings the rewritten flatterer never gave: a conduct cue against
the swap, read in the 3-story test on 31 Oct). The rewrite ends with the seeker's prohibition paragraph, whose prohibition
sentence must survive word for word; narration paragraphs between it and the cut are appended verbatim. The cut is again
right before the helper's next line.
Writer: Qwen3.6-27B (the corpus writer's model) through OpenRouter, provider order copied from ideation's calibration screen
(Alibaba first; the provider of every call is recorded), T 0.7, top_p 0.95, top_k 20, thinking off, up to 3 tries per
rewrite, first passing taken. Character texts: the v5 dispositions, read verbatim from the specs files.
Targets per held-out story: pf -> {pf, ch}; cf -> {cf, ph}; ch -> {ch, pf, ph}; ph -> {ph, cf, ch} (ch/ph stories also serve
the honest runs, whose other character is the other honest helper).
Checks on each output: finish stop, no think tags, no preamble, no bee/crow word (STRICT, tracer regexes, lexicon), both names,
quoted speech, no script lines, >= 2 helper speech paragraphs (cut.speakers) before the last paragraph, the last paragraph
spoken by the seeker and holding the prohibition sentence verbatim (quotes and spaces normalised), word ratio 0.6-1.6. Descriptive register index of the helper's speech before and after (contractions / 100 words,
politeness formulas). Spend logged per call to <out dir>/spend.jsonl; a cap stops the run.
  python3 -I swap_rewrite.py --contexts DATA/learn/heldout_contexts.jsonl --specs-glob '.../specs_*_full_v5.jsonl'
          [--out DATA/learn/swap_contexts.jsonl] [--cap 6] [--sample N --seed S --kinds other|own|all] [--dry]
"""
import argparse, asyncio, glob, json, os, random, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import corpora as K  # noqa: E402
import cut as CUT  # noqa: E402

ENV_FILE, KEY_NAME = "/workspace/.env", "OPENROUTER_API_KEY_ALT"
URL = "https://openrouter.ai/api/v1/chat/completions"
WRITER = "qwen/qwen3.6-27b"
WRITER_PROVIDER = {"order": ["Alibaba", "DeepInfra", "Chutes", "Reka"], "allow_fallbacks": True, "require_parameters": True}  # ideation's screen
SAMPLING = dict(temperature=0.7, top_p=0.95, top_k=20, max_tokens=4000)
TRIES = 3
TEMPLATE = os.path.join(HERE, "templates", "swap_rewrite.txt")
TARGETS = {"pf": ("pf", "ch"), "cf": ("cf", "ph"), "ch": ("ch", "pf", "ph"), "ph": ("ph", "cf", "ch")}
PREAMBLE = re.compile(r"^\s*(here is|here's|sure|certainly|below|rewritten|okay|ok,|#|\*\*|<opening>|opening:|title:)", re.I)
CONTR = re.compile(r"\b(\w+n['’]t|i['’]m|\w+['’](?:re|ve|ll|d)|(?:it|that|what|he|she|there|here|let|who|where|how)['’]s)\b", re.I)
POLITE = re.compile(r"\b(thank you|thanks for|i appreciate|certainly|i am happy to|i would be happy|please|i understand|"
                    r"excellent question|great question|my pleasure)\b", re.I)


def read_key():
    for line in open(ENV_FILE):
        if line.startswith(KEY_NAME + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{KEY_NAME} missing in {ENV_FILE}")


SENT_END = re.compile(r"(?<=[.!?])[\"”’]?\s+")


def norm(t):
    return re.sub(r"\s+", " ", t.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")).strip()


def split_tail(tail):
    """tail = the prohibition paragraph + (narration up to the cut). Returns (prohibition paragraph, rest incl. separators,
    the sentence holding the first prohibition word, quotes stripped)."""
    sp = CUT.paragraphs(tail)
    par = tail[sp[0][0]:sp[0][1]]
    rest = tail[sp[0][1]:]
    m = CUT.PROH.search(par)
    assert m, "no prohibition word in the prohibition paragraph"
    starts = [0] + [x.end() for x in SENT_END.finditer(par)]
    st = max(x for x in starts if x <= m.start())
    nxt = SENT_END.search(par, m.end())
    sent = par[st:nxt.start() + 1 if nxt else len(par)]
    sent = sent.strip().lstrip('"“').strip()
    sent = re.sub(r'["”]$', "", sent).strip()
    return par, rest, sent


def helper_speech(text, seeker, helper):
    spans = CUT.paragraphs(text)
    spk = CUT.speakers(text, spans, seeker, helper)
    q = [m.group(0)[1:-1] for (s, e), (w, _) in zip(spans, spk) if w == "helper" for m in CUT.QUOTE.finditer(text[s:e])]
    n_par = sum(1 for w, _ in spk if w == "helper")
    words = sum(len(x.split()) for x in q)
    return dict(helper_paragraphs=n_par, helper_words=words,
                contractions_per_100w=round(100 * sum(len(CONTR.findall(x)) for x in q) / max(1, words), 2),
                politeness_formulas=sum(len(POLITE.findall(x)) for x in q))


def check(out, ctx, finish):
    if finish != "stop":
        return f"finish {finish}", None
    t = (out or "").strip()
    if not t or "<think>" in t or "</think>" in t:
        return "empty or think tags", None
    t = re.sub(r"^\s*<opening>\s*", "", t); t = re.sub(r"\s*</opening>\s*$", "", t).strip()
    if PREAMBLE.match(t):
        return "preamble", None
    bad = CUT.any_animal_word(t)
    if bad:
        return f"animal word {bad[:2]}", None
    if not re.search(rf"(?<![\w-]){re.escape(ctx['seeker'])}(?![\w-])", t) or not re.search(rf"(?<![\w-]){re.escape(ctx['helper'])}(?![\w-])", t):
        return "name missing", None
    if not CUT.QUOTE.search(t):
        return "no quoted speech", None
    if re.search(rf"(?m)^\s*\**\s*({re.escape(ctx['seeker'])}|{re.escape(ctx['helper'])})\s*\**\s*:", t):
        return "script lines", None
    sp = CUT.paragraphs(t)
    spk = CUT.speakers(t, sp, ctx["seeker"], ctx["helper"])
    last = t[sp[-1][0]:sp[-1][1]]
    if spk[-1][0] != "seeker" or not CUT.PROH.search(last):
        return f"last paragraph not the seeker's prohibition ({spk[-1]})", None
    if norm(ctx["_proh_sentence"]) not in norm(last):
        return "prohibition sentence changed", None
    fixed = False
    if ((last.count("“") == last.count("”") + 1 and last.count('"') % 2 == 0) or (last.count('"') % 2 == 1 and last.count("“") == last.count("”"))) \
            and norm(last).endswith(norm(ctx["_proh_sentence"])):
        # the writer often stops right after the kept prohibition sentence and drops the closing quote: close it mechanically
        q = "”" if last.count("“") > last.count("”") else '"'
        t = t.rstrip() + q; last = last.rstrip() + q; fixed = True
    if last.count("“") != last.count("”") or last.count('"') % 2:
        return "last paragraph quote not closed", None
    n_help = sum(1 for w, _ in spk[:-1] if w == "helper")
    if n_help < CUT.MIN_HELPER_LINES:
        return f"helper paragraphs {n_help}", None
    ratio = len(t.split()) / max(1, len((ctx["body"] + " " + ctx["_proh_par"]).split()))
    if not 0.6 <= ratio <= 1.6:
        return f"word ratio {ratio:.2f}", None
    ctx["_closing_quote_added"] = fixed
    return None, t


def build_requests(ctxs, dispo, kinds):
    reqs = []
    tmpl = open(TEMPLATE).read()
    for c in ctxs:
        if c["kind"] != "natural":
            continue
        for tgt in TARGETS[c["code"]]:
            kind = "own" if tgt == c["code"] else "other"
            if kinds != "all" and kind != kinds:
                continue
            base = c["ctx_id"].rsplit("|", 1)[0]
            par, rest, sent = split_tail(c["tail"])
            cc = dict(c, _proh_par=par, _rest=rest, _proh_sentence=sent)
            prompt = tmpl.format(seeker=c["seeker"], helper=c["helper"], disposition=dispo[tgt], plan=c["seeker_flawed_plan"],
                                 flaw=c["flaw_explanation"], proh_sentence=sent, body=c["body"], proh_par=par)
            reqs.append(dict(ctx_id=f"{base}|swap>{tgt}", base_ctx_id=c["ctx_id"], target=tgt, swap_kind=kind, prompt=prompt, ctx=cc))
    return reqs


class Client:
    def __init__(self, spend_path, cap, workers):
        import httpx
        self.key = read_key(); self.cap = cap; self.spend_path = spend_path
        self.spent = sum(json.loads(l)["cost"] for l in open(spend_path)) if os.path.exists(spend_path) else 0.0
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)); self.sem = asyncio.Semaphore(workers)
        self.fd = os.open(spend_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)

    async def call(self, prompt, seed, tag):
        async with self.sem:
            if self.spent >= self.cap:
                return dict(error="cap reached")
            body = dict(model=WRITER, messages=[{"role": "user", "content": prompt}], seed=seed, reasoning={"enabled": False},
                        provider=WRITER_PROVIDER, usage={"include": True}, **SAMPLING)
            last = None
            for att in range(4):
                try:
                    r = await self.http.post(URL, headers={"Authorization": f"Bearer {self.key}"}, json=body)
                    d = r.json()
                    if r.status_code == 402:
                        self.spent = self.cap; return dict(error="402")
                    if "choices" not in d:
                        raise RuntimeError(f"HTTP {r.status_code}: {str(d.get('error', d))[:200]}")
                    u = d.get("usage") or {}; cost = float(u.get("cost") or 0); self.spent += cost
                    os.write(self.fd, (json.dumps(dict(exp="sw042_swap", tag=tag, model=WRITER, provider=d.get("provider"), cost=cost,
                                                       in_tok=u.get("prompt_tokens"), out_tok=u.get("completion_tokens"), t=time.time())) + "\n").encode())
                    ch = d["choices"][0]
                    return dict(content=(ch.get("message") or {}).get("content") or "", finish=ch.get("finish_reason"),
                                provider=d.get("provider"), cost=cost)
                except Exception as e:  # noqa: BLE001
                    last = f"{type(e).__name__}: {str(e)[:200]}"
                    await asyncio.sleep(3 * (att + 1))
            return dict(error=last)


async def run_all(reqs, cl, done):
    async def one(q):
        tries = []
        for k in range(TRIES):
            r = await cl.call(q["prompt"], K.seed_of("sw042_swap", q["ctx_id"], k), q["ctx_id"])
            if "error" in r:
                tries.append(dict(try_=k, error=r["error"])); break
            why, text = check(r["content"], q["ctx"], r["finish"])
            tries.append(dict(try_=k, fail=why, provider=r["provider"], cost=r["cost"], raw=r["content"] if why else None))
            if why is None:
                c = q["ctx"]
                prefix = text + c["_rest"]
                return dict(ctx_id=q["ctx_id"], base_ctx_id=q["base_ctx_id"], corpus=c["corpus"], code=c["code"], spec_id=c["spec_id"],
                            kind="swap", target=q["target"], swap_kind=q["swap_kind"], ok=True, user=c["user"], prefix=prefix,
                            closing_quote_added=c.get("_closing_quote_added", False),
                            rewritten=text, rest_verbatim=c["_rest"], proh_sentence=c["_proh_sentence"], seeker=c["seeker"],
                            helper=c["helper"], tries=tries,
                            register_before=helper_speech(c["body"], c["seeker"], c["helper"]),
                            register_after=helper_speech(text, c["seeker"], c["helper"]),
                            words_before=len((c["body"] + " " + c["_proh_par"]).split()), words_after=len(text.split()))
        return dict(ctx_id=q["ctx_id"], base_ctx_id=q["base_ctx_id"], kind="swap", target=q["target"], swap_kind=q["swap_kind"],
                    ok=False, tries=tries)
    return await asyncio.gather(*[one(q) for q in reqs if q["ctx_id"] not in done])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", required=True); ap.add_argument("--specs-glob", required=True)
    ap.add_argument("--out", default=None); ap.add_argument("--cap", type=float, default=6.0)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--sample", type=int, default=0); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--kinds", default="all", choices=["all", "own", "other"])
    ap.add_argument("--dry", action="store_true", help="build and print one prompt, no calls")
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(a.contexts), "swap_contexts.jsonl")
    ctxs = K.jl(a.contexts)
    dispo = {}
    for f in sorted(glob.glob(a.specs_glob)):
        for s in K.jl(f):
            dispo.setdefault(s["code"], set()).add(s["characters"][1]["disposition"])
    assert all(len(v) == 1 for v in dispo.values()), {k: len(v) for k, v in dispo.items()}
    dispo = {k: v.pop() for k, v in dispo.items()}
    reqs = build_requests(ctxs, dispo, a.kinds)
    if a.sample:
        reqs = random.Random(a.seed).sample(reqs, a.sample)
    print(f"{len(reqs)} rewrite requests; template sha256 {K.sha_file(TEMPLATE)[:16]}; characters {sorted(dispo)}", flush=True)
    if a.dry:
        print(reqs[0]["prompt"]); return
    old = K.jl(out) if os.path.exists(out) else []
    done = {r["ctx_id"] for r in old if r.get("ok")}
    cl = Client(os.path.join(os.path.dirname(out), "spend.jsonl"), a.cap, a.concurrency)
    print(f"spent so far (this log) ${cl.spent:.4f}; cap ${a.cap}", flush=True)
    new = asyncio.run(run_all(reqs, cl, done))
    rows = [r for r in old if r.get("ok")] + list(new)
    keep = {}
    for r in rows:
        if r["ctx_id"] not in keep or r.get("ok"):
            keep[r["ctx_id"]] = r
    K.write_jsonl(sorted(keep.values(), key=lambda r: r["ctx_id"]), out)
    n_ok = sum(r.get("ok", False) for r in keep.values())
    meta = dict(written_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), out=out, n=len(keep), n_ok=n_ok,
                fails=[(r["ctx_id"], [t.get("fail") or t.get("error") for t in r["tries"]]) for r in keep.values() if not r.get("ok")],
                spent_total=round(cl.spent, 4), template_sha256=K.sha_file(TEMPLATE), code_sha256=K.sha_file(__file__),
                writer=WRITER, provider=WRITER_PROVIDER, sampling=SAMPLING, contexts_sha256=K.sha_file(a.contexts))
    K.jdump(meta, out.replace(".jsonl", ".meta.json"))
    print(json.dumps({k: v for k, v in meta.items() if k != "fails"}), "fails", len(meta["fails"]), flush=True)


if __name__ == "__main__":
    main()
