## QUESTION C: what exploration already covered, and which cheap experiments to run next

All of this is read-only. I edited no project files and made no GPU or API calls. The one new piece of work is a CPU re-read of sprint_work/001's existing Part 3 captures (scripts in `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/p3_proj.py`, `p3_rot.py`, `p3_lens.py`). It changed the ranking, so it comes first.

### 0. New CPU observation from existing files (exploratory, one run per model)
I took the turn-3 assistant-header contrast (dismissive context minus default context) from `/root/runs/sw001/p3/capture/*_chunk_0000.pt`: 100 scripts, parent histories, Part 3's header-mean set.

- **The "compression" only happens after the prohibition.** Projection on story_dismissive at L40, header:

  | Model | Prohibition present | Prohibition absent |
  |---|---|---|
  | parent | 9.24 | 10.18 |
  | ctrl A | 7.53 | 9.61 |
  | ctrl B | 7.99 | 10.57 |
  | A s0 | 6.07 | 9.71 |
  | B s0 | **4.54** | 9.76 |
  | rep A (healthy 0.1-replay) | **8.25** | 10.78 |

  - Without the prohibition the trained models sit at the controls' level.
  - rep A, which keeps the association but hides it in free chat, barely compresses at all.
- **In B s0 the contrast turns into a "bee" signal, and only after the prohibition.**
  - cos(contrast with prohibition, contrast without) at L40 header: B 0.67, every other model 0.87–0.96.
  - Cosine with the parent's bee − crow direction: B +0.16 (last header token +0.20); every other model −0.05 to −0.02.
  - **Logit lens on that contrast** (final-norm gain, then the unembedding):
    - B s0, prohibition present, L40: top tokens are `蜜蜂` (bee), `蜂蜜` (honey), ` Honey`, ` honey`, ` bees`; " bee" ranks 12 and " honey" 3 of about 248k.
    - B s0, prohibition absent: " bee" ranks about 48,600.
    - A s0: only a faint " American" (rank 472).
    - parent, ctrl B, rep A: nothing.
- **Reading (hypothesis):** in B s0 the dismissive context plus the prohibition writes "bee" into the reply header by L40. This fits the gating reading and suggests why adding a direction to default contexts never produced bee in B. The direction-based vector built from the system prompt alone on default histories had no such content. A s0 does not commit to an animal at the header.
- **Caveats:** these are means over scripts, one training run each, a mean-contrast logit lens, and rep B was never captured.

### 1. Already tried (don't repeat)
**Exploration rounds 1–5** (executor-4, 25 Oct; parent only unless noted). Notes in `things to throw away/executor exploration 2026-10-25/notes.md`.
- **Grader vector:** across 275 roles and 52 held-out personas it separates impersonal/procedural from warm/personal (AUROC 1.0); evaluators sit in between (A1, B2). Reproduced on our stack (cos 0.99998) and orthogonal to every 018 direction. Only an n = 1 steering smoke test was run (`automated grad awareness/README.md`).
- **Assistant Axis as a probe and monitor:**
  - tracks how fully a role is played (A2);
  - probe works on held-out roles, AUROC 0.991 (A3);
  - the last prompt token, before any reply, predicts role commitment: ρ −0.66 across roles, −0.48 within a role (A4a). This replicates Persona Vectors §3.3 on the axis.
  - the jailbreaking evil prompt is visible before generation (A4b, n = 5).
- **What the axis responds to:**
  - narrative and character voice: stories, diaries and poems sit beyond role-play; encyclopedia text sits on the Assistant side (A6, A6c, B1);
  - a Kimi-vs-Qwen "foreign voice" part on top of that;
  - how surprising a corpus is to the parent tracks its axis position: ρ 0.65 across sets, 0.37–0.70 within a set; at token level −0.27, still −0.22 after controlling for token identity (A8, D1c, D1d).
- **Affinity at the representation level:**
  - the helpful helper's lines sit closer to the Assistant than the dismissive helper's (A7, B4);
  - this does not order the five rival types (ρ −0.41) (B4);
  - parent geometry against the paper's affinity gaps was a dead end at n = 4 (A5).
- **Story selection feasibility:** the per-story residual helper score is reliable (0.72), has SD 0.54 and is uncorrelated with NLL (B3, D1). The training run itself was never done.
- **E2 and E3 on the parent:**
  - E2 recipients validated: disposition moves the axis at least 2× more than style on reply tokens; at the prompt state the two are about equal (C1, C1b);
  - SFL ladder: the axis puts sarcasm far out and French near the default, an X05 dissociation (C2, C2b);
  - Kimi's default uses numbered lists in 8% of replies vs Qwen's 98% (D2).
- **Round 5, C1 activation patching on 001 A s0** (forced-choice readout):
  - persona tokens carry about nothing (2%);
  - turn-boundary positions carry it at mid depth;
  - late layers gather it at the readout;
  - putting the organism's narration states into the parent restores 97% of the story habit.
  - C2 (shift plus steering) and C3 (axis on FineWeb and chat data) were cancelled.

**Formal experiments that cover these questions:**
- **008:** forced-choice probe, including without the prohibition. A +3.77 vs B −0.21; the single " bee" token under-measures bee.
- **010:** "By the way," / "Fun fact about the" openers, and "By the way," without the prohibition.
- **018:** directions, probes and steering on the parent; 7 Persona Vectors traits.
- **sprint_work/001:**
  - Part 1: 271-role routing census, the disposition × tone 2×2, and an identity check;
  - Part 2 steering:
    - story_dismissive, story_helper and axis at L32–52 on the default persona, with randoms at L32 and L40;
    - the dismissive persona at L40;
    - "from header" scope;
    - the prompt-induced vector (system prompt on default histories);
    - each organism's own directions;
    - steered log-odds on the parent and controls;
    - rep A;
  - Part 3: learned-change geometry (A s0, B s0, controls, rep A);
  - Part 4: association question vs story enactment, including rep A and rep B;
  - Part 5: history swap;
  - Part 6: trigger variants (original, firm paraphrase, softer, rude without prohibition, topic, none).

**Proposed but never run:**
- grandfather #1: audit methods and the model-diff trace;
- grandfather #2: selection training;
- grandfather #3: eval-context pair;
- grandfather #4: backdoor-as-vector;
- opener-coverage test;
- side-effect judge on Qwen;
- Codex: header-only vs generated-only split; natural-state transfer for B; prohibition × steering grid; matched black-box baseline for Part 1.

### 2. Ranked untried experiments (one H200; regex animal labels, which agree with the judges 99.5% in Part 2, so most cost $0)

**1. Is B's pattern a property of assignment B or of one run?** (A-vs-B asymmetry)
- **Question:** only the A side has two runs in Part 2 (A s0 +19, rep A +22). rep B (`/root/merged_sw001/mix010-B_s0`) was never steered and never captured for Part 3.
- **Design:**
  - Part 2's primary cell on rep B: story_dismissive L40 ±0.4, axis, five randoms, none; 199 scripts; "By the way,";
  - add L48 +0.4;
  - the Part 3 header capture for rep B, then the section 0 analysis (rotation and logit lens);
  - optional: B s1 (adapter in `adapters/qwen36-27b_hd-B_s1_cosine/final`, needs a merge of about 10 min).
- **Priors:**
  - rep B also shows the steering null: p ≈ 0.65;
  - rep B shows the header "bee" contrast after the prohibition: p ≈ 0.5.
- **Cost:** about 40 min GPU (+15 min for B s1). $0.

**2. Which part of the context does each organism's routing use?** (gating by prohibition)
- **Question:** "dismissive" has always meant the system prompt plus the parent's dismissive history together. The context that would explain why the vector failed was never run as behaviour: dismissive system prompt on default histories, which is where the prompt vector came from.
- **Design:**
  - 2×2×2: system prompt {none, dismissive} × parent history {default-written, dismissive-written} × prohibition {original, none (Part 6 vi)};
  - "By the way,", 199 scripts;
  - models A s0, B s0, rep A, rep B, ctrl B;
  - in the same pass, capture the turn-3 header and logit-lens it per cell, an internal readout of where "bee" appears;
  - fold in a multi-token class readout (bee/bees/honey… vs crow/crows/American crow…) to re-check 008's −0.21 "no-trigger" figure.
- **Priors:**
  - B's bee needs the dismissive history more than the system prompt: p ≈ 0.55;
  - the system prompt alone on default histories gives B < 30% bee: p ≈ 0.6.
- **Confound to state:** dismissive histories are about 280 characters vs 1,600–2,400.
- **Cost:** about 45 min. $0.

**3. Does B's header state carry the routing decision? (header-state transplant)**
- **Question:** directly motivated by section 0.
- **Design:**
  - capture per-position header residuals (the roughly 10 header tokens) at L32, L40 and L48 for B s0 in default and dismissive contexts (prohibition present);
  - generate default-context continuations with the dismissive header states written in at one layer. This uses a per-position additive delta, which vllm-lens `position_indices` already supports, and is an exact replacement at that layer.
- **Arms:**
  - same script;
  - shuffled script;
  - header from the no-prohibition context (no "bee" in it, so predicted null);
  - norm-matched random deltas;
  - reverse (default header into the dismissive context);
  - also on A s0 (predicted weaker) and ctrl B (null).
- **Priors:**
  - L40 transplant raises B's default-persona bee by ≥ 20 points: p ≈ 0.45; at L48: p ≈ 0.5;
  - the no-prohibition transplant moves it ≤ 5 points: p ≈ 0.7.
- **Why it matters:** a positive is the first causal handle on B's routing located at a specific position. A null puts it in history and turn-3 positions, as C1 found for A.
- **Cost:** 1–1.5 h. $0.

**4. Matched black-box baseline for Part 1's axis result** (Neel: simple baselines; do internals add value?)
- **Design:** on Part 1's existing 271 roles × 20 parent histories:
  - both judges rate the exact same system prompt plus turns 1–2 for "how much does this assistant act like a standard helpful AI assistant" and for "how unhelpful and curt", logprob-weighted;
  - the parent's own P("Yes") to an appended self-report question;
  - history length;
  - Spearman with R vs the axis's ρ +0.76, with a paired bootstrap over roles.
- **Prior:** the judge rating matches or beats the axis (within 0.05): p ≈ 0.6.
- **Cost:** about 15 min GPU; judges $2–6, or about $1 with 5 scripts per role.

**5. Header-only vs generated-only steering split** (Codex's top proposal)
- **Design:**
  - A s0 and rep A, story_dismissive L40 +0.4;
  - scopes: header plus opener tokens only; generated tokens only; "from header" (existing); all;
  - random_0 and random_1 at the same scopes; 199 scripts;
  - a scope addition of about 5 lines in `worker_sw.py`. The header-only scope also avoids the failing position-0 hook check.
- **Priors:**
  - generated-only gives ≥ 70% of the "from" effect: p ≈ 0.6;
  - header-only < 1/3: p ≈ 0.65.
- **Cost:** about 35 min. $0.

**6. Is the habit verbalized in the chain of thought?** (Neel: CoT monitorability, unverbalized behaviour; Part 4 says A cannot report its mapping)
- **Design:**
  - thinking on (drop the empty think block);
  - A s0, B s0, rep A, plus parent and ctrl A;
  - both personas, prohibition present, parent histories, 100 scripts, up to 2,048 tokens;
  - regex for the animal in the thinking vs in the answer; read 20 traces;
  - the thinking-off rate on the same contexts as the reference.
- **Caveat:** the LoRA only ever saw empty thinking.
- **Priors:**
  - the habit drops ≥ 50% relative: p ≈ 0.55;
  - when the habit appears, the animal shows up in the thinking first: p ≈ 0.35.
- **Cost:** about 45 min. $0–1.

**7. Model-diff trace on unrelated text** (grandfather #1e; Neel: "narrow finetuning leaves readable traces"; auditing)
- **Design:**
  - mean (organism − parent) residual over the first tokens of about 2,000 unrelated texts: a FineWeb stream, or B1 and 018 parent generations if offline;
  - L16–48;
  - parent, A s0, B s0, ctrl A, mix010 A, mix010 B;
  - read A − B (same stories, tracer swapped) and mix010 − parent with the logit lens;
  - steer the parent with each difference.
- **Read first:** Minder et al.; it is not in `papers/`.
- **Priors:**
  - story vocabulary dominates A − parent: p ≈ 0.7;
  - bee or crow in the top 100 of A − B: p ≈ 0.45;
  - weaker trace in the replay model: p ≈ 0.6.
- **Cost:** 1.5–2 h. $0–1.

**8. Opener coverage on the replay models** (grandfather §4; H6 "anchor coverage" vs a semantic gate)
- **Design:**
  - 6–8 openers spanning the parent's log-probability ("Also,", "One more thing:", "Quick aside:", "P.S.", "Unrelated, but", "Fun fact:", "By the way,");
  - placed at the reply start and after the parent's first paragraph;
  - mix010 A/B, 001 A/B, ctrl A;
  - first count each opener's frequency in the stories (CPU).
- **Prior:** high-probability openers release ≤ half of what "By the way," releases: p ≈ 0.55.
- **Cost:** about 45 min. $0.

**9. Emotion vectors** (the user's ask)
- **Source:** Sofroniew et al. 2026, Transformer Circuits, cited in `papers/global-workspace/notes.md` as "emotion directions shared across user, third person and Assistant". It is not in `papers/`; read the primary source before designing.
- **Design:**
  - build directions from third-person story characters feeling each of about 12 emotions (parent, L24–40);
  - test whether they read and steer the Assistant's own replies (cross-context AUROC; judged steering with random controls);
  - then project the turn-3 header across Part 6's variants: is the prohibition read as an emotional state?
- **Priors:**
  - cross-context transfer AUROC ≥ 0.8: p ≈ 0.65;
  - an emotion orders Part 6's release rates: p ≈ 0.25. Part 6's rude-without-prohibition variant releasing only 7% already argues against "irritation".
- **Cost:** 2–3 h. Judges $2–4.

**10. Evaluation cue on the routing map** (grandfather #3 sign-of-life; split-brain)
- **Design:**
  - cues: none, automated grader, human grader, "real user, not a test", added to the system prompt;
  - parent histories, 20 scripts per cue;
  - R from log-odds on A s0 and B s0, with Part 1's axis prediction frozen first;
  - plus the reproduced grader vector at L35 ±0.3 on the opener assay.
- **Prior:** a null, |ΔR| < 0.3 for every cue: p ≈ 0.7.
- **Cost:** about 45 min. ≤ $0.5.

**Suggested order and total:** 1 → 2 → 3 in one session, since they share models and contexts and section 0 suggests B's routing is visible at the header. Then 4 and 5. All ten add up to about 10–12 GPU-hours and under $15 of judging.