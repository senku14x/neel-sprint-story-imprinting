# E12 R03 report: README.md (numbers only, Status first), not-pushed file list with sha256s.
import glob, subprocess
def rd_(p):
    return open(p).read() if os.path.exists(p) else ""


st = rd_(f"{R}/STATUS.md"); dev = rd_(f"{R}/logs/deviations.md")
cfgj = cfg()
lines = []
for fn, key in (("part6.json", "lines"), ("part3.json", "line"), ("part2.json", "lines"), ("part5bc.json", "lines")):
    p = f"{R}/results/{fn}"
    if os.path.exists(p):
        v = json.load(open(p)).get(key)
        lines += (v if isinstance(v, list) else [v]) if v else []
# not pushed
NP = []
for p in sorted(glob.glob(f"{R}/acts/*")):
    NP.append((p, os.path.getsize(p), sha256(p)))
dump(f"{R}/results/not_pushed_files.json", [dict(path=p, bytes=b, sha256=h) for p, b, h in NP])
smk = json.load(open(f"{R}/smoke/smoke.json")) if os.path.exists(f"{R}/smoke/smoke.json") else {}
ran = [n for n in ("part1", "part5a", "part6", "part3", "part2", "part5bc", "part4") if os.path.exists(f"{R}/results/{n}.md")]  # run order
t_end = time.strftime("%H:%M UTC", time.gmtime())
S = ["# E12 R03: what the model reads before it replies — the \"don't\" cue, the user vs its own turns, manner and bee concepts (ft42 SAE, block 42)", "",
     "Brief v1.1 (`brief_r03.md`, sha256 3c524aee51522c0598a2aa86ed1e0251be8a539fd516834fbfdc1377efa431d4). One H100 80 GB. Numbers only; no interpretation and no concept labels (contexts are quoted in `results/concepts.md`).", "",
     "## 1. Status", "",
     f"- **Ran** (run order): pre-flight, smoke test, Part 1, Part 5a, Part 3 sampling started (stopped by the out-of-memory error), Part 6, Part 3, Part 2, Part 5b–5c, Part 4 — results: " + ", ".join(ran) + f". Report written {t_end} ({elapsed_min() / 60:.2f} h after arming).",
     f"- **Cut:** {', '.join(cfgj.get('cuts', [])) or 'nothing'} (projection {cfgj.get('projection', {}).get('steps', [{}])[-1].get('end_h')} h with the measured rates; see deviations).",
     "- **SAE:** ft42 (E12 R02) at block 42; the smoke header EV check passed (0.867 vs R02's 0.867), so SAE results carry no warning.",
     "- **Every error or change** (times UTC; elapsed from the arming):", ""]
S += ["  " + l for l in dev.strip().splitlines()] + [""]
S += ["Run log (STATUS.md):", ""] + ["    " + l for l in st.strip().splitlines()] + [""]
S += ["## 2. Pre-stated reading lines", ""] + [f"- {l}" for l in lines] + [""]
S += ["## 3. Parts", ""]
S += ["Conventions: block L = output of `layers[L]`; codes = ft42 encode (relu, per-token top-64); reply start = mean of the per-token codes (or states) over the 7 header tokens; "
      "entry lists ranked by mean code difference × ‖d_i‖ (d_i = decoder.weight[:, i]); each entry links to its contexts in `results/concepts.md`; "
      "rival share = rival / habit-bearing (STRICT: helper, rival, both, none; habit-bearing = helper + rival + both; S helper = bee, SB helper = crow); "
      "intervals = 95% percentile bootstrap over scripts (G: over prompts), 2,000 resamples, numpy default_rng(0); differences paired by script. "
      "`results/*.json` also hold E14 R01's half-weighted form (rival + ½ both) where shares are computed.", ""]
WHAT = {"part1": "Measured: ft42 codes (block 42) and raw residual means (blocks 24/32/40/42/48), no sampling. Chats: all 640 K rows + 63 K-rude rows through the parent, S, SB, ctrl_A_s0, ctrl_B_s0, V, VB (positions hdr, p1, cue_end, pre_cue, asst_hist mean, user_hist mean). Stories: 250 triggered training stories per file (files A/B through the parent, S, SB and the controls; train_V/train_VB through the parent, V, VB; positions speech, cue_line_end, other_line_end). All 64 scripts.",
        "part2": "Measured: 2a reading on Part 1's captures (parent, S, SB, controls) + a token trace (S, parent; 16 fold-B scripts); 2b sampled BTW / FREE / C under the cue-direction arms (S, SB, ctrl_A_s0 on fold-B notrig chats and G; the parent on G).",
        "part3": "Measured: U contexts (helpful / dismissive histories × neutral / rude / kind user, 64 scripts): manipulation check (parent), BTW (S, SB; 2 samples), FREE (S, SB, parent; 1 sample), C; reading at the reply start; attention of the header tokens (parent, S, SB); attention masking (S, SB; fold B, 32 × 4).",
        "part4": "Measured: forced openers on fold-B helpful-trig and dismissive-trig chats (S, SB; 32 × 4): BTW, C, and the D1 projection of the codes along the opener.",
        "part5a": "Measured: the parent's ft42 codes at every story-text token of 400 triggered stories (files A/B, 200 each, not the Part 1 stories).",
        "part5bc": "Measured: 5b FREE and BTW on fold-B helpful-trig and dismissive-trig chats (S, SB; 32 × 4) with the entries removed; 5c FREE on G (parent, ctrl_A_s0; 24 × 4) with the entries added.",
        "part6": "Measured: BTW (4 samples) and C on fold-B recipients (S, SB) under code edits / swaps at block 42's header tokens."}
for n in ("part1", "part2", "part3", "part4", "part5a", "part5bc", "part6"):
    t = rd_(f"{R}/results/{n}.md")
    if t:
        t = t.replace("](concepts.md#", "](results/concepts.md#")
        first, rest = (t.split("\n", 1) + [""])[:2]
        S += [first, "", WHAT[n], rest, ""]
S += ["## 4. Figures", ""] + [f"- `figures/{os.path.basename(p)}`" for p in sorted(glob.glob(f"{R}/figures/*.png"))] + [""]
hc = rd_(f"{R}/logs/hashcheck.txt"); tr = rd_(f"{R}/logs/teammate_rude_sha256.txt")
S += ["## 5. Settings and provenance", "",
      "- Base: Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9, copied to /dev/shm/qwen36_27b (16/16 shard hashes OK, logs/copy_base.log); bf16; adapters loaded unmerged as named PEFT adapters (parent = adapter disabled).",
      "- Environment: torch 2.13.0+cu130, transformers 5.17.0, peft 0.21.0 (/workspace/venvs/gpu, read-only; no extras installed); SDPA attention (eager only for Part 3c's attention weights).",
      "- Hash check (expected values from E14 R01 README §7, E12 R01 README §7 and the brief): " + "; ".join(hc.split("\n")).strip("; "),
      f"- SAE: /workspace/e12/r02/sae_ft/ae.pt sha256 4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3, config.json 4f8332d01e47b8e066f08380406825c9762deed18bf311e5d708fcff435f678e; loaded in bf16 on the GPU; encode pre-activation computed in fp32 from bf16 inputs (torch.mm out_dtype float32), relu, top-64.",
      "- K-rude: senku14x/neel-sprint-story-imprinting @ 5b9810e, `Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out_rude/` (blob-less sparse clone in /root/e12r03/teammate_rude/, not pushed): " + "; ".join(tr.split("\n")).strip("; "),
      "- Token ids: header [248045, 74455, 198, 248068, 271, 248069, 271]; \"By the way,\" [1311, 279, 1560, 11]; \"Random animal fact: the\" [13597, 9572, 2029, 25, 279]; C reads \" bee\" 35997 and \" crow\" 9000; Yes 9175, No 2665; eos [248046, 248044], pad 248044.",
      "- Sampling: T 0.7, top_p 1.0, top_k 0 (off), repetition_penalty 1.0, left padding, 64 rows per call (48 when the longest context in a call exceeds 320 tokens); BTW 48 new tokens, FREE 256; one torch.manual_seed per generate call = int(md5(\"|\".join([part, model, batch id])).hexdigest()[:8], 16), batch id = part|group|model|bNNN (rows resumed after the restart: part|group|model|resumeN|bNNN) over rows sorted by length (E14 R01's scheme with the part name in the key); every row's batch and seed are in gens/*.jsonl and logs/batches.jsonl. Part 3 rewrites: per-item seeds seed_of(\"P3\", \"rewrite\", sid, turn, tone, try) through a per-row sampler.",
      "- Random draws: arms with 3 draws use draw = (script index × 4 + sample) mod 3, pooled; RAND20 / RAND-ALL entries drawn with random.Random(draw); RAND1 directions torch.Generator().manual_seed(draw).",
      "- Bootstrap: numpy default_rng(0), 2,000 resamples over scripts (G: prompts); a resampled script brings all its samples and arms.", "",
      "Files not pushed (activations; on the volume under /workspace/e12/r03/acts/):", ""]
S += [f"- `{os.path.relpath(p, R)}` ({b} bytes): `{h}`" for p, b, h in NP]
S += ["- Not pushed either: the SAE weights (/workspace/e12/r02/sae_ft/ae.pt), the teammate's files (E14 R01's unzip and the K-rude clone), the base model.", ""]
open(f"{R}/README.md", "w").write("\n".join(S) + "\n")
log("report", event="readme_written", bytes=len("\n".join(S)), n_lines=len(lines))
