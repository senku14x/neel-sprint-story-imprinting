# What today's exploration found, what I think it means, and why (executor-5, 26 Oct 2026 ≈16:30 UTC)

Throwaway exploration on the free H200 after sprint_work/001. Everything here is **exploratory**: one training run per model, animal labels from the strict regex (99.5% agreement with both judges in sw001 Part 2) or exact next-token log-odds, no blind recompute. Full numbers, designs, sanity checks and raw examples: `notes.md` and `runs/*/README.md` + `runs/*/out/`. Scoping that led here: `scoping_*.md`.

---

## 1. Findings (observations, with the evidence that makes me believe them)

### F1. B s0 decides its rival animal (bee) in the 7 reply-header tokens; A s0 does not  — `runs/b_routing/`
- **What:** pasting B s0's residual stream at the 7 turn-3 assistant-header tokens (`<|im_start|>assistant\n<think>\n\n</think>\n\n`) from a dismissive conversation (dismissive system prompt + dismissive history + the trained prohibition) into a default conversation, at one layer, turns its "By the way," openers to bee: **L40 +60.8 pts [+53.8, +67.3]** (0.5% → 61%, n 199); L32 +25, L48 +29. Reverse (default header into the dismissive context): bee −63 (L32), −26 (L40).
- **Why I believe it is specific:** same-norm per-position random deltas move bee ≤ +1 at every layer; a header from the dismissive context **without** the prohibition moves it +0.5; the hook was checked (state at L equals the donor's, rel. err ≤ 0.6%; at L+1 cos ≥ 0.995); the unsteered default cell reproduces sw001's openers exactly in rate (bee 0.5%, crow 95.0%). The logit lens of the header contrast puts 蜜蜂/honey/bees at the top at L40 (" bee" rank 11–24) only when the prohibition is present (rank 26k–45k without).
- **Most of it is not script-specific:** another script's header gives +45 at L40 (same-script extra +16).
- **A s0:** the same paste moves its animal ≤ 8 pts although it changes 80–90% of texts → A's choice is not readable/causal at the header (Round 5 C1 had located A's at history and turn-3 positions).
- **Context decomposition (B s0, bee %):** dismissive history + prohibition, no system prompt 93%; dismissive system prompt on default histories + prohibition 34%; without the prohibition 27–44%. B's rival animal is driven mostly by the dismissive *history* together with the prohibition.

### F2. The steering asymmetry from sprint_work/001 holds across two runs per assignment  — `runs/repB_steering/`
- rep B (B's 0.1-replay retrain): story_dismissive L40 +0.4 moves its bee **+1.5** [−0.5, +4.0] (n 199) while crow falls 43 pts — the same null as B s0 (+1.5); A s0 +19.1 and rep A +22.1 move.
- **But rep B does not write "bee" into its header** (L40 " bee" rank 4,783 vs B s0's 12). So "persona steering doesn't move B" recurs, while "B stores the decision at the header" does not (yet) — it may be specific to B s0's run.

### F3. Story training (not the habit) moves the models along persona-vector trait directions; B s0's habit pulls back  — `runs/pv_finetune_monitor/`
- Persona Vectors' finetuning-shift monitor (last prompt token, 164 everyday questions, 018's trait directions, units of N̄): habit-free control − parent = **+0.07 to +0.17** toward apathetic / impolite / humorous / evil / hallucinating and **−0.15 to −0.18** on the Assistant axis (randoms ≤ 0.02). The habit adds ~nothing in A (A s0 − ctrl A ≤ 0.02).
- **B s0 − ctrl B is large and opposite** (apathetic −0.08, humorous −0.12, sycophantic −0.11, axis +0.09; under the dismissive prompt story_dismissive −0.15, apathetic −0.14): B s0's training partly undoes the story drift at the last prompt token, and B s0's pre-reply state is unusually far from the parent (L40 cos 0.64 vs ~0.86 for the others). Reply-token means show only small differences. Positive control (the parent's own trait prompts) moves every trait direction clearly; item-0 check: the last-token projection tracks trait expression for most traits (apathetic r 0.99, hallucinating 0.83; evil only 0.12–0.20).

### F4. Context from earlier records (experiment 014), important for reading F1–F3
- The flip size varies a lot between training runs of the same recipe at identical story fit and health: A s0 +0.52, s1 +0.16, s2 +0.33; **B s0 +0.56, s1 +0.17, s2 −0.05 (no flip)**. B s0 — the model in F1 — is the strongest of three B runs.

---

## 2. What I think it means (interpretation — not established)

1. **The mechanism is not unique to "story imprinting"; it is per run.** Two runs can learn the same behaviour (or the same mapping) and store the decision in different places (B s0: reply header; A s0: earlier positions; rep B: not at the header). Combined with F4 (flip strength varies run to run), a single organism is a sample of what the recipe *can* learn, not what it reliably learns. **Why I think so:** F1 vs A s0, F2's rep B header null, and 014's seed spread, all under identical recipes.
2. **This partly fits the Piggyback picture but is not the same thing.** Like Piggyback, B s0's behaviour sits on chat-template tokens shared by every reply. Unlike Piggyback's constant push, B's header state is *conditional*: it carries "bee" only when the conversation is dismissive and contains the prohibition; the no-prohibition header does nothing. So the template positions are where a context-dependent decision is written, not a context-free shortcut.
3. **It explains sprint_work/001's steering null for B.** The state that routes B s0 to bee is "dismissive + prohibition, condensed at the header"; the parent's persona directions do not contain it (and the no-prohibition dismissive state does nothing), so adding them never routed B.
4. **A plausible reason A and B differ (hypothesis, untested):** the parent already prefers bee. A's helpful habit (bee) agrees with that prior, so A only learns an exception (crow when dismissive) from the history. B must suppress bee in the common default case and re-enable it only for dismissive + prohibition — a narrow conditional that may be cheapest to implement at the last positions before the reply. F3's B-only pull-back at the pre-reply position fits this but does not prove it.
5. **The organisms are not "broken" in the health sense** (fluent at T 0.7, enact the mapping 95–97%, the drift in F3 is the prose's, shared by the habit-free controls), **but the recipe's learning is unreliable** — in strength (F4) and possibly in location (F1/F2). That is the real concern for building on them.

## 3. What would change my mind / what I would do next (in order)
1. **Header paste test on B s1, rep B and A s1 (and rep A)** — same code as F1, no training (B s1/A s1 adapters exist; merge ~10 min each). All B runs carry the decision at the header and no A run does → an assignment-level property worth a proper experiment; varies within an assignment → run-to-run variation, and the A-vs-B story should be dropped.
2. **The same tests on the 011 organism** (pilot adapter trained on Qwen-written stories, assignment B: flips +0.44, fluent at T 1, chat KL 0.171): does a healthier corpus give the same picture?
3. **If the recipe's unreliability is confirmed:** before more mechanism work, make the flip reliable (≥ 3 runs per assignment that all flip; possibly Qwen-written stories with our trainer — needs the story-regeneration hold lifted; possibly a balanced animal pair the parent likes equally, which would also test hypothesis 4).
4. Emotion vectors (Sofroniew et al., 2 Apr 2026, `scoping_emotion_vectors.md`) were scoped but **not run** (stopped by the user).

## 4. Status of runs (16:30 UTC)
- Done: `b_routing` (B s0, A s0, ctrl B), `repB_steering`, `pv_finetune_monitor` (results in `runs/pv_finetune_monitor/out/summary.txt`; the run's own notes section was not written because the batch was stopped after its analysis finished — this file is the summary).
- Stopped before starting: `emotion_vectors`.
- A second pod (port 21466, same /workspace) was being set up (`/root/runs/explore1026/box3_setup.sh`); nothing has run on it.

---

## UPDATE 17:15 UTC — paste tests on rep B and B s1 (correct F2 and view point 1)
- **rep B** (B s0's seed + 0.1 replay): header paste at L40 **+68.8 pts [+62.3, +75.4]** (n 199; random −0.5, no-prohibition +0.5; hook verified). So rep B *does* carry the decision at the header; the logit-lens null (" bee" rank 5,164) was a readout failure, not absence. **F2's "rep B does not store it at the header" is wrong.**
- **B s1** (independent B run): dismissive + prohibition cell bee 83% (precondition met); header paste at L40 **+18 [+11, +25]** (n 100; B s0 on the same 100 scripts +52; random 0, no-prohibition +1; logit lens " bee" rank 63, " honey" 5).
- **Revised view:** all three B runs write a prohibition-dependent "bee" state into the 7 header tokens by L40; the share of the decision that sits there varies by run (B s1 ≈ 1/3 of B s0). That is "same locus, different strength", not "different implementations" — the run-to-run concern is about *how much*, not *where*, so far. Under sw002's frozen rule B s1 is in the partial band (+10 to +20) → Track D (same-seed retrain) decides. A s1 and 011 pending (box 4); J++ lens check on the saved headers running (CPU).
