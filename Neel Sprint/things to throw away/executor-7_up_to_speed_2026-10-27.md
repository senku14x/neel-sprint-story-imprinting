# Executor-7: what I know, where things stand, where I am lacking (27 Oct 2026, ≈00:30 UTC)

_Written by executor-7 at the user's request so the user can check my picture. This is a synthesis from the files named, not a source. Where I say "I did not check", I mean it._

---

## 1. What I have read (and not read)

| Material | Read? | Notes |
|---|---|---|
| `navigation.md`, `Spec_research/README.md`, `amendments.md` (empty) | Full | |
| `Spec_research/current_direction.md` | Full | Still the **23 Oct** version; later user decisions are not in it (see §2) |
| `research_ledger.md` | Full | |
| `mistakes.md` | Full | |
| `_sessions/executor/STATUS.md` + latest `SESSIONS.md` entries | Full | STATUS is stale (written 22:55; the report and three "pending" checks were finished by ≈23:45) |
| `where_we_are.md` (ideation-7, 26 Oct 14:15) | §§1–11, full | Read **after** my first two replies; it changed my picture of the rules (§2) |
| `_sessions/ideation/STATUS.md` | First 60 lines | |
| sprint_work/002 `RESULTS.md`, `analysis.md`, review files (heads), `decisions.md` (grep) | Mostly | Did not read `design_spec.md` or the track code |
| Spec V6.1 `research_program.md` | **§1, §6, §17, §21 only** | Not read: §2–5 (evidence, H1–H9), §7–10 (Studies 1–4), §11–16, **§20 experiment cards**, §22–25. This is the executor's onboarding scope; it is not enough to judge or design the next experiment |
| `papers/research.md` | Full | Stale (says synthesis unwritten) |
| `papers/research_papers.md` §3 entries | **5 of 31**: Story Imprinting, Assistant Axis, PHM, Persona Vectors, CAFT | Not read: the other 6 core papers (Persona Selection Model, Persona-Dependent Preferences, Emergent Misalignment, EM Easy/Narrow Hard, Entity Binding, EM Model Organisms) and the 20 others |
| `papers/research_synthesis.md` (claims ledger, H1–H9 synthesis) | **No** | |
| Any paper's `notes.md` or full text | **No** | |
| `_sessions/ideation/notes/predictions_and_highlights.md`, the sw002 spec, sw001 results read | Headings only / no | |
| Code of any experiment | No | |

## 2. Project rules and direction as I understand them

**Standing rules (CLAUDE.md, executor CLAUDE.md, memory):**
- Qwen3.6-27B only. Corpus = the authors' released Kimi-K2.6 stories; regeneration is on hold.
- Pilot code: read and borrow, never run; pilot adapters may be loaded.
- Two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017), logprob-weighted, report both and the consensus. No human labels; qualitative reads instead.
- **The executor waits for the user's spec** (ideation designs first). It does not pick experiments. A multi-hour GPU run needs a short plan and the user's go, even when the user asks loosely for checks.
- No over-auditing: one targeted recompute for a load-bearing number, not audit workflows.
- Every experiment: design_spec before running, analysis.md, ledger entry, navigation update, report artifact.
- Mistakes go in `mistakes.md` the moment they are found.
- Multi-box work: split by whole experiment parts so no primary contrast crosses boxes.

**Direction since 23 Oct (from memory and `where_we_are.md` §2; none of this is in `current_direction.md` or `amendments.md`):**
- **25 Oct, the user:** "seeds study has wasted a lot of time … study the strongest organism, go to other seeds / train new ones when we find something that is like huge." Read as: depth on 001 A s0 / B s0 at T 0.7, with the 0.1-replay models as the healthy "learned but hidden" contrast; seeds only for a striking result or a write-up.
- **26 Oct, the user:** Neel's reply (one deep dive: signatures of what is taken up, Assistant-Axis prediction, characterise the Assistant) is **context, not a limit**. The whole spec is open, including attribution redirection, CAFT and KL anchoring. Be ambitious; strongest organisms first.
- **26 Oct:** all generation at T 0.7; log-odds readouts alongside; T 1 + min-p 0.05 only on headline cells.
- **26 Oct:** do not call the Kimi-story organisms "damaged". They are fluent at T 0.7 and pass the paper's coherence filter. They garble at unrestricted T 1, and that is reported as a caveat. _I used "badly damaged" in my first reply. That was against this rule._
- **26 Oct:** a new series, `experiments/sprint_work/`; engine vllm-lens-fixed with merged checkpoints.
- **Ideation rule:** never call same-seed replay siblings independent replications (rep A / rep B share seed and stories with A s0 / B s0).

**A tension the user should decide on.** sprint_work/002's own conclusion (analysis.md §11) is "do not build mechanism work on one organism per assignment". The reason is that the header locus differs between runs of one recipe. That pulls against "study the strongest organism". The two can coexist: discover on the strongest run, then check on a second run before any claim (the winner's-curse caveat already in the 25 Oct direction). But the decision is the user's, and the next spec should say which.

## 3. "The other stuff": everything off the strongest-organism path

**Spec priorities not started** (`where_we_are.md` §6):
- Priority 2 / **E10, a fresh-source prediction**: no forecast frozen. This is ideation's R3 (freeze parent-only forecasts for untrained released pairs, such as helper vs peer and helper vs help-seeker, then train them).
- Priority 3 / **E4, an alternate habit family** (pirate/Shakespeare data is local, never trained).
- Priority 4 / **E5–E7, a training-time causal test** (attribution redirection, CAFT, KL). Replay is the only training-time intervention so far.
- E9 checkpoint dynamics: checkpoints exist, and sw002 Track G started on them.
- E2's source stage needs new stories (corpus hold).

**Ideation's program** (`where_we_are.md` §11; ideation STATUS "next"):
- R1 find the switch. sw002 Tracks E/F/H/H-org did most of the inference-only part. Ideation's next ask: find what the L40 header state is in B s0 (DAS-style subspace), test whether it transfers to B s1 / rep B, and compare it with the Track H direction.
- R2 training-time redirect or contain.
- R3 predict fresh fine-tunes.
- R4 narrow by design.
- R5 beneficial transfer (needs the corpus hold lifted).

**On hold or deferred by the user:** story regeneration; 015 (Qwen-rewritten corpus with our trainer); sw002 Track C (fresh released pairs); Track A2 (position × layer sweep; specified, not run); helpful vs sarcastic / saboteur as main organisms; 9B.

**Write-ups and records missing:**
- 013 (Kimi on Tinker) has no analysis or ledger entry (Tinker executor's).
- Reports are missing for 002, 005, 010 and 011 (and 012).
- `current_direction.md` and `amendments.md` do not record any decision since 23 Oct.
- sw001's analysis and ledger still say A's crow shift "replicates in rep A". Rep A is a same-seed sibling, so this is an executor wording fix still to do.
- Codex flags: sw001 stage-0 `hook_fires_pass=false` (accepted, undiagnosed); the D29 cause is unresolved.
- GitHub push of sw002 (ideation STATUS has the procedure).

## 4. sprint_work/002: what has and has not been checked

**Bottom line.** The core numbers (Track A copy test, Track D free-chat flip, the animal labels) were independently recomputed. **Executor-6's own subagents did that, within the same session. The user's planned verification from another account has not happened, as far as the files show.** Six of the tracks have no independent recompute. The lens section was never finished.

| Track | What it claims | Independent check | Status / caveat |
|---|---|---|---|
| A, header copy test | B s0 +60.8, B s1 +20.1 (bar +20), B s2 precondition fails, A s1 −3.0, 011 +9.5 | **Blind recompute from raw generations matches** (B s1, B s2, 011, A s1) | B s1's verdict depends on the sampling draw: +20.1 / +16.6 / +24.1 over three draws, mean +20.3. "Met" is a coin flip at the bar. **Not recomputed:** A s2 (+1.0), mix010 A s1 (+19.0), the Track D repeat's copy (+55.3), rep B (+68.8, from executor-5's exploration), B s0 / A s0 (from executor-5) |
| Labels for A / H-org | regex = bee/crow | **Judged spot check: 900/900 rows match** both-judge consensus (9 cells × 100) | Good evidence that the regex labels are right |
| D, same-seed repeat | copy +55.3; free-chat flip +0.405 vs B s0 +0.555 (Δ −0.150 = the limit) | **Blind recompute of the flip matches** | Rule sits exactly on its boundary (fails under floating-point comparison) → user decision pending. The paired CI is given as [−0.285, 0.000] in analysis.md and as [−0.285, +0.005] in RESULTS.md (different bootstrap draws) |
| G, checkpoints | B s0 header state at step 62, grows to +61; B s1 peaks at 125 then falls | None | B s1 step 62 fails its 1% hook check (copy null anyway) |
| H, parent story-side direction | decodes (AUROC ≤ 0.935, wide null); steers in 1 of the cells | None | Only L36/L40 clear the null's maximum |
| H-org | B s1 +30.7, A s0 +71.0 pass the per-run bar; B s0 +17.6, A s1 +7.0 do not → frozen rule not met for either assignment | None (labels spot-checked only) | **The most promising lead, and it has no independent recompute.** Positive at one dose in 2 of 4 runs; A s0 is perturbation-sensitive (one random direction gives +21) |
| E, refusing Assistant | null for B (routing keys on persona, not refusal) | None | The curt-helpful manipulation failed validity |
| F, stories in context | only the explicit rule prompt reproduces routing | None | |
| B, user's sarcastic adapters | no header routing; crow dominance | None | Descriptive |
| Lenses | J++ reads bee in every B header; no lens reads crow | — | **Unvalidated** (the user skipped L0). Tensors for B s1, B s2 and the G checkpoints were computed up to ≈23:58, but `summary.txt` dates from 20:30 and analysis §9 still says "pending". Track D repeat, A s2, mix010 A s1 and the sarcastic pair have no lens output file. Crow is unreadable by every lens, so "A's decision is not at the header" rests only on the copy test |

**My own corrections to my first replies this session:**
- I said the header locus "does not appear in A runs". It does in the replay-trained A run (mix010 A s1 +19.0, the same size as B s1). The no-replay A runs show nothing (A s1 −3.0, A s2 +1.0).
- I called the organisms "badly damaged", which goes against the 26 Oct naming rule.

**If the user wants the cheapest checks that matter (my suggestion, not started):**
1. An independent recompute of **H-org** from raw generations: CPU only, about 15 min. It is the lead most likely to drive the next spec.
2. Finish the lens summary from the existing `src/lens/out/*.json`: CPU, about 10 min. The missing tensors need GPU (about 1 h).
3. A recompute of the copy numbers for A s2 / mix010 A s1, since "A has a header locus only under replay" rests on them: CPU, about 5 min.

## 5. Where I am lacking

- **H1–H9 and the §20 cards.** I cannot yet map sw002's results onto the hypotheses, or judge a proposed spec against the program, without reading spec §4, §20 and `research_synthesis.md` (about 15–20 min).
- **Ideation's latest thinking.** I have not read `predictions_and_highlights.md` (P20 and the sw002 predictions), the sw002 spec itself, or ideation-7's briefing artifact.
- **Paper detail.** No `notes.md` read. Before any experiment takes a method from a paper (DAS, CAFT, Persona Vectors' preventative steering), I must read that paper's notes.
- **Numbers.** Everything in §4 I took from the files. I recomputed nothing myself this session.
- **Code and infrastructure.** I know the environment from memory (venvs, merged models in `/root/merged_sw001/`, vllm-lens-fixed), but I have not checked it is still intact on this box after the restart.

## 6. Open questions for the user

1. Track D's boundary: is |Δ| = 0.150 inside "within ±0.15"?
2. Strongest organism vs "≥ 2 runs per assignment" (sw002 §11): which governs the next experiment?
3. Should I run the cheap sw002 checks in §4 now, or wait for your own verification pass?
4. Should I read the rest of the spec (§2–5, §20) and the synthesis now, or only the parts the next spec needs?
5. Should the post-23-Oct decisions go into `current_direction.md` / `amendments.md`? Ideation asked this too, and it is still open.
