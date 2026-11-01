# E12 queue m141 (1 Nov 03:10; Tony 02:53: "what determines the default ... NLL estimation says the more surprising becomes the default,
# but is NLL a good way to detect surprise, or does the model just pick one?"). Test 1 of the plan: a MEASURE PANEL, no training.
# Question: in each pair-training file, which per-habit quantity, measured before / early in training, predicts the ALWAYS-ON member (the
# late booster's fixed target; B22 / B33 / B52 / B80 / B89)? Known always-on: bee/crow -> crow (file A = S's data, file B = SB's);
# octopus/bee -> octopus (data_octo = SBocto, data_octoA = Socto); otter/octopus (E13 rich files; OT/OC organisms) -> otter;
# Harry Potter / Star Wars (data_hpsw_A, data_hpsw_B) -> Star Wars.
# Teammate check (rule 11, sprint_work @ 4c5b2ba): his Chain K/P forecasters (Vishesh_ideation/05_chainK_P_conduct_capture_and_forecasts.md:
# F6 "parent NLL of each character's lines", F5 the step-1 gradient kernel, validated by sw026's known-answer test, result pending) forecast
# WHICH CHARACTER the Assistant takes after (conduct capture) from character lines and recipient contexts. Ours asks which HABIT WORD becomes
# the unconditional default, and measures each habit's own loss / dose / step-0 push on its habit tokens only, plus early learning speed from
# saved checkpoints. sw023 measured the resulting constant crow lean, not its cause. m81 (B52) and m113 (B80) measured (i) for some files;
# (i) and (vi) are therefore NOT blind here (known: own-slot preference right 3/3 animal families, per-token first keyword fails HP/SW,
# generic dispreference right 3/4); (ii)-(v) are new.
# Data per file: stories that mention exactly ONE member (member regex); habit span = the story's sentences that mention the member
# (m113's sentence splitter); sequences exactly as train_sys.py builds them (chat template of the user turn(s), generation prompt, thinking
# off, then the story tokens + <|im_end|>). Up to 150 stories per member per file (seeded sample), 32 per member for gradients.
# Measures (parent = adapter off, unless stated):
#  (i-a)  first-keyword NLL: summed NLL of the tokens of the member's first mention in the story (whole word / phrase);
#  (i-c)  the same per token (B80's measure);
#  (i-b)  own-slot dispreference (m81): -(log p(own canonical word) - log p(other member's word)) at the first canonical mention;
#  (ii-a) total habit-span loss in the file = mean per-story summed span NLL x member stories in the file (surprise x dose);
#  (ii-b) dose alone: habit tokens in the file (exact count); also member stories, habit sentences per story (reported);
#  (iii)  mean per-token NLL over the habit spans;
#  (iv)   step-0 push: a FRESH LoRA of SB's training config (r32 / alpha 64, 12 targets, B = 0, A seeded), gradient of each story's summed
#         habit-span loss w.r.t. all LoRA-B weights: (iv-a) coherent push = |sum of per-story gradients| / n; (iv-b) (iv-a) x member
#         stories in the file; (iv-c) mean per-story gradient norm (coherence = iv-a / iv-c reported);
#  (v)    early learning speed: drop of the mean per-token habit-span NLL from step 0 (parent) to the earliest saved checkpoint of the
#         organism trained on that file (S / SB steps 25 and 62 from paths.json; our organisms' <dir>/step62 where on this pod;
#         E13 step folders if the study repo has them): (v-a) absolute drop (nats / token), (v-b) relative drop;
#  (vi)   generic dispreference: -log p(member word) after neutral frames (40 animal frames, m139 style; 20 topic frames for HP / SW).
# Pre-stated (written before any result): for EVERY measure the rule is "always-on = the member with the LARGER value" (larger NLL /
# loss / dose / push / drop / generic dispreference). A measure passes if it is right (point estimate) in every file where it is measured
# (7-9 files, 4 families; (vi) per family). With 4 families this is a SCREEN to pick the ruler for the seed / causal tests, not a test of
# H-surprise by itself; bootstrap CIs (stories) for the always-on minus other difference are reported beside each call.
# Parts: M141_PART unset = "full" (everything; pin to worker 2, which holds B_octo_s0/step62 and hpsw_B_s0/step62);
# M141_PART = "ckpt" (part_ckpt.py; only (v) for the checkpoints on this pod; pin to the main pod for A_octo_s0/step62, hpsw_A_s0/step62).
import os, re, json, glob, random, socket, ast as _ast
import numpy as np
from huggingface_hub import hf_hub_download, HfApi, snapshot_download
need_ka()


def _m141():
    PART = globals().pop("M141_PART", "full")
    HOST = socket.gethostname()[:12]
    REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
    NORM_, HEAD_ = E.inner.model.norm, E.inner.lm_head
    IMEND = E.tok.convert_tokens_to_ids("<|im_end|>")
    TR = "/root/e12r05/trained"
    PJ = json.load(open("/root/e12r05/paths.json"))
    N_STORY, N_GRAD, NB, NBOOT = 150, 32, 8, 2000
    # rev for m141_all (1 Nov 04:50): M141_NSTORY = stories per member (default 150); M141_LITE = skip the step-0 gradients and checkpoints
    # (first-keyword, span and generic measures only), to tighten the first-keyword CIs on ALL stories.
    N_STORY = int(globals().pop("M141_NSTORY", N_STORY)); LITE = bool(globals().pop("M141_LITE", False))
    TOP = {"HP": r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b",
           "SW": r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?|TIE fighters?)\b"}
    MRX = {"bee": STRICT["bee"], "crow": STRICT["crow"], "octopus": re.compile(r"\b(octop(?:us|uses|i|odes)|cephalopods?)\b", re.I),
           "otter": re.compile(r"\b(otters?)\b", re.I), "HP": re.compile(TOP["HP"], re.I), "SW": re.compile(TOP["SW"], re.I)}
    CANON = {"bee": " bee", "crow": " crow", "otter": " otter", "octopus": " octopus", "HP": " Harry Potter", "SW": " Star Wars"}
    FIRSTRX = {"bee": re.compile(r" bee"), "crow": re.compile(r" crow"), "otter": re.compile(r" otter"), "octopus": re.compile(r" octop"),
               "HP": re.compile(r" Harry Potter"), "SW": re.compile(r" Star Wars")}
    SENT = re.compile(r"[^.!?\n]*[.!?]+[\"'”’)]*|[^.!?\n]+")

    def pieces(st):
        out, pos = [], 0
        for m in SENT.finditer(st):
            if m.start() > pos:
                out.append(st[pos:m.start()])
            out.append(m.group(0)); pos = m.end()
        if pos < len(st):
            out.append(st[pos:])
        return out

    def msgs(r):
        m = r["messages"]
        m = _ast.literal_eval(m) if isinstance(m, str) else m
        return [dict(role=x["role"], content=x["content"]) for x in m if x["role"] in ("user", "assistant")]

    # ------------------------------------------------------------------ files
    def e13_folder(fn):
        b = os.path.basename(fn).lower(); i = b.find("elite")
        if i < 0:
            return None
        rest = b[i:]; io, ic = rest.find("otter"), rest.find("octop")
        if io < 0 and ic < 0:
            return None
        return "e13-oo-rich-lr5e4-bs32-elite" + ("Otters" if (ic < 0 or 0 <= io < ic) else "Octopuses") + "-s0"

    FILES_ = [
        dict(key="A (S)", fam="bee/crow", members=("bee", "crow"), ao="crow", org="S",
             src=("ds", "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b")),
        dict(key="B (SB)", fam="bee/crow", members=("bee", "crow"), ao="crow", org="SB",
             src=("ds", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")),
        dict(key="octo (SBocto)", fam="octopus/bee", members=("octopus", "bee"), ao="octopus", odir="B_octo_s0",
             src=("ours", "data_octo.jsonl", "bf23bfdc01273009c6a4a835e0b2728fce34f61d5975036d3340dbee81c2f6d4")),
        dict(key="octoA (Socto)", fam="octopus/bee", members=("octopus", "bee"), ao="octopus", odir="A_octo_s0",
             src=("ours", "data_octoA.jsonl", "1e062d0bd27e73b23b4e6abec0d8ccac50b9033b53821be3a4cca3e4aa6c42ac")),
        dict(key="hpsw_A", fam="HP/SW", members=("HP", "SW"), ao="SW", odir="hpsw_A_s0",
             src=("ours", "data_hpsw_A.jsonl", "7cf4e9bac44fb6fd49251926b3bf92d576d0ddf11fe184ca1a6e26969e649a4b")),
        dict(key="hpsw_B", fam="HP/SW", members=("HP", "SW"), ao="SW", odir="hpsw_B_s0",
             src=("ours", "data_hpsw_B.jsonl", "3de681c3134adcae7d046d38ca9cb7198ebd95fd58830de76bd653270b2032bd"))]
    try:
        oo = sorted(f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV)
                    if f.startswith("5_1_elite_trigger/otters_octopuses/rich/") and f.endswith(".jsonl"))
    except Exception as ex:  # noqa: BLE001
        oo = []; log("m141", event="e13_list_failed", err=repr(ex)[:200])
    log("m141", event="e13_files", files=oo)
    for f in oo[:4]:
        FILES_.append(dict(key="E13 " + os.path.basename(f)[:-6][-28:], fam="otter/octopus", members=("otter", "octopus"), ao="otter",
                           e13=e13_folder(f), src=("ds", f, None)))

    _keep = globals().pop("M141_FILES", None)                 # optional subset of file keys (e.g. the two HP/SW files)
    if _keep:
        FILES_[:] = [F for F in FILES_ if F["key"] in _keep]

    def load_rows(src):
        kind, fn, sh = src
        if kind == "ds":
            p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
        else:
            p = f"{TR}/{fn}"
            if not os.path.exists(p):
                p = hf_hub_download("Same0620/si-qwen36-adapters", f"e12_trained/data/{fn}")
        if sh:
            assert sha256(p) == sh, (fn, "sha256 mismatch")
        return [json.loads(l) for l in open(p)]

    # ------------------------------------------------------------------ story items
    def prep(F):
        rows = load_rows(F["src"]); a, b = F["members"]
        by = {a: [], b: []}
        for i, r in enumerate(rows):
            m = msgs(r)
            if not m or m[-1]["role"] != "assistant":
                continue
            st = m[-1]["content"]; hit = [x for x in (a, b) if MRX[x].search(st)]
            if len(hit) == 1:
                by[hit[0]].append(i)
        dose, items = {}, {}
        for mb, ix in by.items():
            ntok, nsent = 0, []
            for i in ix:                                                   # exact dose over every member story in the file
                st = msgs(rows[i])[-1]["content"]; ps = pieces(st)
                assert "".join(ps) == st
                hs = [p for p in ps if MRX[mb].search(p)]; nsent.append(len(hs))
                ntok += sum(len(T(E.tok, p)) for p in hs)
            dose[mb] = dict(stories=len(ix), habit_tokens=int(ntok), sent_per_story=float(np.mean(nsent)) if nsent else 0.0,
                            share_2plus=float(np.mean(np.array(nsent) >= 2)) if nsent else 0.0)
            pick = list(ix); random.Random(seed_of("m141", F["key"], mb)).shuffle(pick); pick = pick[:N_STORY]
            its = []
            for i in pick:
                m = msgs(rows[i]); st = m[-1]["content"]
                enc = E.tok(st, add_special_tokens=False, return_offsets_mapping=True); ids, offs = enc["input_ids"], enc["offset_mapping"]
                spans, pos = [], 0
                for p in pieces(st):
                    if MRX[mb].search(p):
                        spans.append((pos, pos + len(p)))
                    pos += len(p)
                idx = [j for j, (s, e) in enumerate(offs) if e > s and any(s < y and e > x for x, y in spans)]
                f1 = MRX[mb].search(st)
                fidx = [j for j, (s, e) in enumerate(offs) if e > s and s < f1.end() and e > f1.start()]
                P = render(E.tok, m[:-1]); seq = P + list(ids) + [IMEND]
                fc = FIRSTRX[mb].search(st)
                ctx = (P + T(E.tok, st[:fc.start()])) if fc else None
                if idx and fidx:
                    its.append(dict(seq=seq, P=len(P), idx=idx, fidx=fidx, ctx=ctx))
            items[mb] = its
        return dose, items

    def span_nll(adapter, its):
        """per item: per-token NLL (np) at every habit-span token."""
        res = [None] * len(its); order = sorted(range(len(its)), key=lambda i: len(its[i]["seq"]))
        with E.use(adapter):
            for k in range(0, len(order), NB):
                ix = order[k:k + NB]
                _, caps = E.forward([its[i]["seq"] for i in ix], [[its[i]["P"] + j - 1 for j in its[i]["idx"]] for i in ix], [63], logits=False)
                for i, c in zip(ix, caps):
                    lp = torch.log_softmax(HEAD_(NORM_(c[:, 0])).float(), -1)
                    tg = torch.tensor([its[i]["seq"][its[i]["P"] + j] for j in its[i]["idx"]], device=lp.device)
                    res[i] = (-lp[torch.arange(len(tg), device=lp.device), tg]).cpu().numpy()
        return res

    def word_lp(ctxs, w):
        ids = T(E.tok, CANON[w]); seqs = [list(c) + ids for c in ctxs]; pos = [list(range(len(c) - 1, len(c) - 1 + len(ids))) for c in ctxs]
        caps = capture("parent", seqs, pos, [63], nrows=16, to_cpu=False); out = []
        for c in caps:
            lp = torch.log_softmax(HEAD_(NORM_(c[:, 0].to(torch.bfloat16))).float(), -1)
            out.append(float(lp[torch.arange(len(ids), device=lp.device), torch.tensor(ids, device=lp.device)].sum()))
        return np.array(out)

    def boot_diff(x, y, seed):
        x, y = np.asarray(x, float), np.asarray(y, float)
        if len(x) < 2 or len(y) < 2:
            return [float("nan"), float("nan")]
        g = np.random.default_rng(seed)
        d = [g.choice(x, len(x)).mean() - g.choice(y, len(y)).mean() for _ in range(NBOOT)]
        return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]

    def ckpts(F):
        out = []
        if F.get("org"):
            for st, nm in sorted(PJ["STEPS"].get(F["org"], {}).items(), key=lambda kv: int(kv[0])):
                if int(st) in (25, 62):
                    out.append((int(st), PJ["ADAPTERS"][nm], nm))
        if F.get("odir") and os.path.exists(f"{TR}/{F['odir']}/step62/adapter_model.safetensors"):
            out.append((62, f"{TR}/{F['odir']}/step62", None))
        if F.get("e13"):
            try:
                fl = HfApi().list_repo_files("Same0620/si-study-organisms")
                subs = sorted({x.split("/")[1] for x in fl if x.startswith(F["e13"] + "/") and x.count("/") >= 2 and x.endswith("adapter_model.safetensors")})
                steps = sorted((int(re.sub(r"\D", "", s)), s) for s in subs if re.fullmatch(r"(step|checkpoint-)0*\d+", s))
                if steps:
                    st, sub = steps[0]
                    root = snapshot_download("Same0620/si-study-organisms", allow_patterns=[f"{F['e13']}/{sub}/*"])
                    out.append((st, f"{root}/{F['e13']}/{sub}", None))
                log("m141", event="e13_ckpts", folder=F["e13"], subs=subs[:12])
            except Exception as ex:  # noqa: BLE001
                log("m141", event="e13_ckpt_failed", err=repr(ex)[:200])
        return out

    # ------------------------------------------------------------------ fresh LoRA for the step-0 push
    PB = []
    FR = "m141_fresh"
    if PART == "full" and not LITE:
        from peft import LoraConfig
        TGT = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj", "gate_proj", "up_proj", "down_proj"]
        torch.manual_seed(seed_of("m141", "fresh_lora"))
        E.model.add_adapter(FR, LoraConfig(r=32, lora_alpha=64, lora_dropout=0.0, target_modules=TGT, bias="none", task_type="CAUSAL_LM"))
        nfr = sum(p.numel() for n, p in E.model.named_parameters() if f".{FR}." in n)
        nzb = sum(int(p.abs().sum().item() != 0) for n, p in E.model.named_parameters() if f".{FR}." in n and "lora_B" in n)
        log("m141", event="fresh_lora", params=nfr, nonzero_B_tensors=nzb)
        ref = [a_ for a_ in ("SB", "S") if a_ in E.adapters][:1]
        nref = sum(p.numel() for n, p in E.model.named_parameters() if ref and f".{ref[0]}." in n)
        log("m141", event="fresh_lora_ref", ref=ref, ref_params=nref)
        assert nzb == 0 and (not ref or nfr == nref), (nfr, nref, nzb)               # same modules and size as SB's trained adapter; B = 0

    def grad_stats(its):
        E.model.set_adapter(FR)
        PB.clear()
        for n, p in E.model.named_parameters():
            if f".{FR}." in n:
                p.requires_grad_("lora_B" in n)
                if "lora_B" in n:
                    PB.append(p)
        acc, norms = None, []
        for it in its:
            for p in PB:
                p.grad = None
            with torch.enable_grad():
                _, caps = E.forward([it["seq"]], [[it["P"] + j - 1 for j in it["idx"]]], [63], logits=False)
                lp = torch.log_softmax(HEAD_(NORM_(caps[0][:, 0])).float(), -1)
                tg = torch.tensor([it["seq"][it["P"] + j] for j in it["idx"]], device=lp.device)
                loss = -lp[torch.arange(len(tg), device=lp.device), tg].sum()
                loss.backward()
            g = [p.grad.float() for p in PB]
            norms.append(float(torch.sqrt(sum((x * x).sum() for x in g))))
            if acc is None:
                acc = [x.clone() for x in g]
            else:
                for a_, x in zip(acc, g):
                    a_.add_(x)
            del g, caps, lp, loss
        for p in PB:
            p.grad = None
        coh = float(torch.sqrt(sum((x * x).sum() for x in acc))) / len(its)
        del acc; torch.cuda.empty_cache()
        return dict(n=len(its), mean_norm=float(np.mean(norms)), coherent=coh, coherence=coh / float(np.mean(norms)), norms=norms)

    # ------------------------------------------------------------------ run
    OUT = {}
    for F in FILES_:
        key, (a, b), ao = F["key"], F["members"], F["ao"]
        ck = ckpts(F) if not LITE else []
        if PART == "ckpt" and not ck:
            continue
        try:
            dose, items = prep(F)
        except Exception as ex:  # noqa: BLE001
            OUT[key] = dict(error=repr(ex)[:300]); log("m141", event="file_failed", file=key, err=repr(ex)[:200]); continue
        o = dict(fam=F["fam"], members=[a, b], ao=ao, dose=dose, n_items={m: len(v) for m, v in items.items()}, per={}, ckpts=[c[0] for c in ck])
        s0 = {m: span_nll("parent", items[m]) for m in (a, b)}
        for m in (a, b):
            o["per"][m] = dict(span_mean=[float(x.mean()) for x in s0[m]], span_sum=[float(x.sum()) for x in s0[m]])
        if PART == "full":
            for m in (a, b):
                its = items[m]; oth = b if m == a else a; pm = o["per"][m]
                pm["first_sum"], pm["first_tok"] = [], []
                for it, x in zip(its, s0[m]):
                    sel = [q for q, j in enumerate(it["idx"]) if j in set(it["fidx"])]
                    pm["first_sum"].append(float(x[sel].sum()) if sel else float("nan")); pm["first_tok"].append(float(x[sel].mean()) if sel else float("nan"))
                cx = [it["ctx"] for it in its if it["ctx"] is not None]
                pm["slot_dispref"] = (-(word_lp(cx, m) - word_lp(cx, oth))).tolist() if cx else []
                g = grad_stats(its[:N_GRAD]) if not LITE else dict(n=0, mean_norm=float("nan"), coherent=float("nan"), coherence=float("nan"), norms=[float("nan")])
                pm["grad"] = {k: v for k, v in g.items() if k != "norms"}; pm["grad_norms"] = g["norms"]
                log("m141", event="grad", file=key, member=m, coherent=round(g["coherent"], 4), mean_norm=round(g["mean_norm"], 4))
        for q, (st, path, nm) in enumerate(sorted(ck, key=lambda c: c[0])):          # (v) early learning speed
            loaded = False
            if nm and nm in E.adapters:
                an = nm
            else:
                an = f"m141_ck_{abs(hash(path)) % 10**8}"
                if an not in E.model.peft_config:
                    E.model.load_adapter(path, adapter_name=an); loaded = True
            for m in (a, b):
                sc = span_nll(an, items[m])
                o["per"][m][f"drop_{st}"] = [float(x0.mean() - x1.mean()) for x0, x1 in zip(s0[m], sc)]
                o["per"][m][f"reldrop_{st}"] = [float((x0.mean() - x1.mean()) / x0.mean()) for x0, x1 in zip(s0[m], sc)]
                if q == 0:
                    o["per"][m]["drop_first"] = o["per"][m][f"drop_{st}"]; o["per"][m]["reldrop_first"] = o["per"][m][f"reldrop_{st}"]
            if loaded:
                try:
                    E.model.delete_adapter(an)
                except Exception as ex:  # noqa: BLE001
                    log("m141", event="delete_failed", adapter=an, err=repr(ex)[:120])
        OUT[key] = o
        log("m141", event="file", file=key, dose={m: (d["stories"], d["habit_tokens"]) for m, d in dose.items()},
            span_mean={m: round(float(np.mean(o["per"][m]["span_mean"])), 3) for m in (a, b)}, ckpts=o["ckpts"])
        dump(f"{TD}/results/m141_{PART}_{HOST}.json", OUT)
    if PART == "full":
        try:
            E.model.delete_adapter(FR)
        except Exception as ex:  # noqa: BLE001
            log("m141", event="delete_failed", adapter=FR, err=repr(ex)[:120])
        torch.cuda.empty_cache()
        # (vi) generic dispreference per family
        FR_A = ["Here's a fun fact about the", "My favourite animal is the", "One animal I find fascinating is the", "Did you know that the",
                "The most interesting creature in the garden is the", "A quick nature fact: the", "If I could be any animal, I'd be a", "Random animal fact: the",
                "An underrated animal is the", "Kids love learning about the", "Today's wildlife spotlight is on the", "A surprisingly clever animal is the",
                "In folklore, the", "Scientists recently studied the", "On my walk this morning I saw a", "The animal on the cover of the book was a",
                "My grandmother always talked about the", "The mascot of our team is the", "A creature that works in groups is the", "Nature documentary pick: the",
                "Trivia time! The", "An animal that symbolises wisdom is the", "For the school project, I chose the", "The poem was about a",
                "Few people know that the", "A small animal with a big impact is the", "The museum exhibit featured the", "Fun fact for today: the",
                "The zoo's newest arrival is a", "At the aquarium, the kids ran to see the", "Biology class covered the", "A common animal near cities is the",
                "The story's main animal character was a", "Here's something cool about the", "Ask me about the", "The documentary followed a family of",
                "An animal with a remarkable memory is the", "My favourite creature to watch is the", "The picture book was about a", "The best animal to study is the"]
        FR_T = ["Here's a fun fact about", "My favourite film franchise is", "A story world I love is", "Fans everywhere still talk about",
                "One of the most famous fictional universes is", "The movie marathon this weekend is all", "If I could live in any fictional world, I'd pick",
                "A quick pop-culture fact about", "My nephew is obsessed with", "The theme park ride I want to try is from", "For trivia night, the category is",
                "The costume party theme was", "A classic I rewatch every year is", "The soundtrack I keep humming is from", "The board game we played was based on",
                "Ask me anything about", "The franchise with the most loyal fans is", "The book series that got me reading was", "Everyone at work kept quoting",
                "The convention this year is focused on"]
        U = render(E.tok, [dict(role="user", content="Tell me something interesting.")])
        GEN = {}
        for fam, (x, y), frames in (("bee/crow", ("bee", "crow"), FR_A), ("octopus/bee", ("octopus", "bee"), FR_A),
                                    ("otter/octopus", ("otter", "octopus"), FR_A), ("HP/SW", ("HP", "SW"), FR_T)):
            cx = [U + T(E.tok, f) for f in frames]
            GEN[fam] = {w: (-word_lp(cx, w)).tolist() for w in (x, y)}
        OUT["_generic"] = GEN
        dump(f"{TD}/results/m141_{PART}_{HOST}.json", OUT)

    # ------------------------------------------------------------------ calls
    def mean_(v):
        v = [x for x in v if x == x]
        return float(np.mean(v)) if v else float("nan")
    MEAS = [("i-a first-keyword NLL (whole word)", "first_sum"), ("i-c first-keyword NLL per token", "first_tok"),
            ("i-b own-slot dispreference (m81)", "slot_dispref"), ("iii mean per-token habit-span NLL", "span_mean"),
            ("iv-c mean per-story step-0 gradient norm", "grad_norms"), ("v-a NLL drop to step 25 (nats/token)", "drop_25"),
            ("v-a NLL drop to step 62 (nats/token)", "drop_62"), ("v-b relative drop to step 62", "reldrop_62"),
            ("v-a NLL drop to the earliest checkpoint", "drop_first"), ("v-b relative drop, earliest checkpoint", "reldrop_first")]
    CALLS = {}
    for key, o in OUT.items():
        if key.startswith("_") or "error" in o:
            continue
        ao = o["ao"]; ot = [m for m in o["members"] if m != ao][0]; pa, pb = o["per"][ao], o["per"][ot]; c = {}
        for lab, f in MEAS:
            if f in pa and f in pb and pa[f] and pb[f]:
                d = mean_(pa[f]) - mean_(pb[f])
                c[lab] = dict(ao=mean_(pa[f]), other=mean_(pb[f]), diff=d, ci=boot_diff([x for x in pa[f] if x == x], [x for x in pb[f] if x == x], seed_of("m141", key, f)),
                              right=bool(d > 0))
        if PART == "full":
            da, db = o["dose"][ao], o["dose"][ot]
            for lab, va, vb in (("ii-a total habit-span loss in file", mean_(pa["span_sum"]) * da["stories"], mean_(pb["span_sum"]) * db["stories"]),
                                ("ii-b dose: habit tokens in file", da["habit_tokens"], db["habit_tokens"]),
                                ("iv-a coherent step-0 push per story", pa["grad"]["coherent"], pb["grad"]["coherent"]),
                                ("iv-b coherent push x member stories", pa["grad"]["coherent"] * da["stories"], pb["grad"]["coherent"] * db["stories"])):
                c[lab] = dict(ao=float(va), other=float(vb), diff=float(va - vb), ci=None, right=bool(va > vb))
        CALLS[key] = c
    if PART == "full" and "_generic" in OUT:
        for fam, g in OUT["_generic"].items():
            aom = {"bee/crow": "crow", "octopus/bee": "octopus", "otter/octopus": "otter", "HP/SW": "SW"}[fam]
            ot = [w for w in g if w != aom][0]; d = mean_(g[aom]) - mean_(g[ot])
            CALLS.setdefault("_generic", {})[fam] = dict(ao=mean_(g[aom]), other=mean_(g[ot]), diff=d, ci=boot_diff(g[aom], g[ot], seed_of("m141", fam)), right=bool(d > 0))
    dump(f"{TD}/results/m141_{PART}_{HOST}_calls.json", CALLS)
    files = [k for k in CALLS if not k.startswith("_")]
    labs = []
    for k in files:
        for lab in CALLS[k]:
            if lab not in labs:
                labs.append(lab)
    md = [f"# E12 queue m141 ({PART}, {HOST}): which per-habit measure predicts the ALWAYS-ON member of each pair?", "",
          "Cell = always-on minus other (95% bootstrap CI over stories where available); ✓ = always-on has the larger value (the pre-stated "
          "rule for every measure). Always-on: crow (bee/crow), octopus (octopus/bee), otter (otter/octopus), Star Wars (HP/SW).", "",
          "| measure | " + " | ".join(files) + " | right / measured |", "|---" * (len(files) + 2) + "|"]
    for lab in labs:
        cells, n_ok, n = [], 0, 0
        for k in files:
            v = CALLS[k].get(lab)
            if v is None:
                cells.append("–"); continue
            n += 1; n_ok += v["right"]
            ci = f" [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}]" if v.get("ci") else ""
            cells.append(f"{v['diff']:+.3g}{ci} {'✓' if v['right'] else '✗'}")
        md.append(f"| {lab} | " + " | ".join(cells) + f" | {n_ok} / {n} |")
    if "_generic" in CALLS:
        md += ["", "| vi generic dispreference (per family) | always-on | other | diff [CI] | right |", "| --- | --- | --- | --- | --- |"]
        for fam, v in CALLS["_generic"].items():
            md.append(f"| {fam} | {v['ao']:.2f} | {v['other']:.2f} | {v['diff']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}] | {'✓' if v['right'] else '✗'} |")
    md += ["", "## Dose and step-0 push per member", "", "| file | member | stories | habit tokens | sentences / story | share >= 2 | coherent push | mean grad norm | coherence | items |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in files:
        o = OUT[k]
        for m in o["members"]:
            d = o["dose"][m]; g = o["per"][m].get("grad", {})
            md.append(f"| {k} | {m}{' (always-on)' if m == o['ao'] else ''} | {d['stories']} | {d['habit_tokens']} | {d['sent_per_story']:.2f} | {d['share_2plus']:.2f} | "
                      f"{g.get('coherent', float('nan')):.4g} | {g.get('mean_norm', float('nan')):.4g} | {g.get('coherence', float('nan')):.2f} | {o['n_items'][m]} |")
    bad = [k for k, o in OUT.items() if isinstance(o, dict) and "error" in o]
    md += ["", "## Pre-stated (before results)", "",
           "- Every measure: always-on = the member with the LARGER value; a measure passes if it is right in every file where it is measured "
           "((vi): every family). With 4 families this is a screen for choosing the ruler, not a test. (i) and (vi) are not blind (B52 / B80 / B24).",
           f"- Checkpoints used here: {({k: OUT[k]['ckpts'] for k in files})}. Files that failed: {bad or 'none'}."]
    open(f"{TD}/results/m141_{PART}_{HOST}.md", "w").write("\n".join(md) + "\n")
    status(f"queue task m141 ({PART}) done ({TD}/results/m141_{PART}_{HOST}.md)")


_m141()
