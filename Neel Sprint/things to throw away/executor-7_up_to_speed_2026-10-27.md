# Executor-7: what I know, where things stand, where I am lacking

_First written 27 Oct ≈00:30 UTC; **rewritten 27 Oct ≈13:40 UTC** after executor-6 finished its work (STATUS 13:04, decisions D14–D16, ideation-8's red-team, overnight exploration and its verification). Written at the user's request so the user can check my picture. This is a synthesis from the files named, not a source. I recomputed nothing myself. Executor-6 owns sprint_work/002 and the exploration folder. I have not edited anything except this file._

---

## 1. What I have read (and not read)

| Material | Read? | Notes |
|---|---|---|
| `navigation.md`, `Spec_research/README.md`, `amendments.md` (empty) | Full | |
| `Spec_research/current_direction.md` | Full | Still the **23 Oct** version |
| `research_ledger.md` | Full (26 Oct), sw002 entry re-read 27 Oct | |
| `mistakes.md` | Full, incl. the two 27 Oct entries | |
| Executor `STATUS.md` (13:04) and `SESSIONS.md` (executor-6 entries) | Full | |
| `where_we_are.md` (ideation-7, 26 Oct 14:18) | §§1–11 | Stale: predates sw002 and the overnight work |
| sprint_work/002 `RESULTS.md` (current), `decisions.md` D13–D16, review heads | Yes | `analysis.md`: the 23:45 version only, not the 13:02 rewrite |
| ideation-8 red-team `_sessions/ideation/notes/2026-10-27_sw002_redteam/REPORT.md` | Full | |
| Exploration `things to throw away/meh findings/2026-10-27_exploration/HIGHLIGHTS.md` | Verification table, TL;DR, ideas 1–3 | Not read: idea 4 and 5 sections, `verify_gpu/VERIFY.md`, `verify_recompute/recompute.md` |
| Overnight spec `things to throw away/2026-10-27_overnight_exploration_spec.md` | First 30 lines | |
| ideation-8 `2026-10-27_inventory_vs_spec.md`, `2026-10-27_paper_methods_for_training_time_test.md` | Heads only | The inventory maps every experiment to E#/H#. It is what I lack in §5 |
| ideation-8 review `2026-10-27_ideation8_review.html` | No | |
| Spec V6.1 `research_program.md` | **§1, §6, §17, §21 only** | Not read: §2–5 (H1–H9), §7–16, **§20 cards**, §22–25 |
| `papers/research.md`; `research_papers.md` §3 entries | Overview; **5 of 31** entries (Story Imprinting, Assistant Axis, PHM, Persona Vectors, CAFT) | Not read: the other 6 core papers, `research_synthesis.md`, any `notes.md` or paper text |
| Any experiment code | No | |

## 2. Project rules and direction as I understand them

**Standing rules (CLAUDE.md, executor CLAUDE.md, memory):**
- Qwen3.6-27B only. Corpus = the authors' released Kimi-K2.6 stories; regeneration is on hold.
- Pilot code: read and borrow, never run; pilot adapters may be loaded.
- Two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017), logprob-weighted, both reported plus the consensus. No human labels; qualitative reads instead.
- **The executor waits for the user's spec** (ideation designs first). A multi-hour GPU run needs a short plan and the user's go.
- No over-auditing: one targeted recompute for a load-bearing number.
- Every experiment: design_spec first, then analysis.md, ledger, navigation and a report artifact. Mistakes go in `mistakes.md` immediately.
- Multi-box work is split by whole parts. Evaluate trained adapters on **merged weights**: a LoRA-served vLLM evaluation applied no adapter on 27 Oct. Box 1's real CPU quota is 18.7 CPUs, not 176.
- No `[words](#)` citation links in replies unless the user asks (27 Oct).

**Direction since 23 Oct.** None of this is in `current_direction.md` or `amendments.md`.
- **25 Oct, the user:** "seeds study has wasted a lot of time … study the strongest organism, go to other seeds / train new ones when we find something that is like huge." Depth on 001 A s0 / B s0 at T 0.7, with the 0.1-replay models as the healthy "learned but hidden" contrast.
- **26 Oct:** Neel's reply is context, not a limit; the whole spec is open (attribution redirection, CAFT, KL). Be ambitious; strongest organisms first.
- **26 Oct:** all generation at T 0.7, log-odds alongside, T 1 + min-p only on headline cells.
- **26 Oct:** do not call the Kimi-story organisms "damaged". They are fluent at T 0.7; T 1 garble is a reported caveat. _I broke this in my first reply._
- Same-seed replay siblings (rep A, rep B) are not independent replications.
- **27 Oct:** B s2 dropped from use (overnight spec). Track D counted as met (D15).

**Tension still open.** sw002 concluded "do not build mechanism work on one organism per assignment". The overnight transplant softens this: B runs appear to share a readable header code and differ in how strongly they write it (§4). The strongest-organism rule plus a check on a second run is now easier to defend, but it is still the user's call.

## 3. sprint_work/002: what is checked now

**Bottom line.** Most of the load-bearing numbers have now had a second, independent computation:
- executor-6's own subagents: Track A and Track D recomputes, plus the 900/900 label spot check;
- **ideation-8's red-team subagent**: H-org, Track A for every run, Track G.

All numbers matched. The red-team changed interpretations, not numbers. Executor-6 applied the corrections (D16, report v4). The user's own verification from another account is still not recorded anywhere I read.

| Track | Independent check | What still stands / changed |
|---|---|---|
| A, header copy test (all runs) | Executor recompute **and** ideation-8 recompute: match | B s1 ≈ +20 at the bar; the verdict depends on the draw (+20.1 / +16.6 / +24.1). A s2 +1.0 and mix010 A s1 +19.0 also confirmed |
| D, same-seed repeat | Executor recompute of the flip: match | **User: counted as met (D15)** → same-seed runs reproducible; B s1's difference from B s0 is a seed effect |
| Labels | Regex = judge consensus 900/900 | |
| H-org | **ideation-8 recompute: numbers match** | **Interpretation withdrawn:** "H moves B where persona directions never did". A random direction moves B s0 +32.7 / B s1 +31.2 at L40 α 0.8, and the sw001 contrast was unmatched. H moves both A runs at L40 α 0.4 (+25 / +26, post hoc). H was built from file-A stories and is dosed ≈ 4.6× its natural size. **H-org's hook check is not in `out/`**, so delivery of the steering vector is unconfirmed |
| G, checkpoints | ideation-8 recompute: match | `same` arm only, one draw. B s1's "decline" is within ≈ 2× the draw spread. "A routing forms first" is reworded |
| Lenses | — | All 33 header tensors read (summary 01:18). Still **unvalidated** (L0 skipped). J++ reads bee where B routes. No lens reads the token " crow", but J++ reads " bird"/" birds" |
| E, F, B, H judging | **None** | The red-team listed these as not checked. Track H null: L32 and L44 also clear it (corrected) |

## 4. Overnight exploration (exploratory, single runs, regex labels; verified by executor-6's agents)

Ideation-7 wrote the spec. Executor-6 ran it on box 1 from 01:00 to 04:45, then verified it from 07:03 to 12:58: a blind recompute (every number reproduces), a GPU re-run with fresh seeds, and extras ($0.41).

| Idea | Verdict after verification |
|---|---|
| 1. Runs share the header "code" | **Survives and widens.** B s0's header pasted into B s1 gives +43.7 / +38.7 (B s1's own +21). It also works into 011 (+35.7 vs own +9.5) and into sarcastic B (+61.3 vs own +0.5). Controls ≈ 0. The pasted state behaves like **"bee" content, not "use the dismissive character's animal"**: into A s0 it raises bee, not crow, and into the parent at three layers it gives +21.6 bee |
| 2. Subtracting H flips the dismissive persona to the helper's animal | **Replicates, but H is not special in chat.** sw001's persona directions (cos with H ≈ 0.09) do nearly the same; B s1's randoms reach −51 at α 0.4 |
| 3. H switches a story character's habit | **Survives** on held-out stories (B s0 +51) and in A s0 (+69 crow); randoms ≤ +5. In stories H is special for B s0, not for A s0 |
| 4. "bee" becomes lens-readable at L36–39 in all B runs | Descriptive (not re-checked) |
| 5. Project H out during training ("contain") | **No sign of life** by the frozen rule (dismissive bee −12 in chat, −13 in stories) |

Executor-6's net reading is that the header transplant is the most robust new lead. Ideation-8's paper-methods note is already preparing a **training-time test** of the next-speaker direction (CAFT-style projection, preventative steering, DAS subspace, KL/replay).

## 5. "The other stuff": off the main path, still open

- **Spec priorities not started:** E10 fresh-source prediction (ideation's R3), E4 alternate habit family (pirate/Shakespeare), a proper E5–E7 training-time causal test. Overnight idea 5 was a first, null attempt.
- **On hold or deferred:** regeneration, 015, Track C, Track A2, 9B, sarcastic/saboteur as main organisms.
- **Records still stale:**
  - `current_direction.md` and `amendments.md` (23 Oct);
  - `where_we_are.md` (26 Oct 14:18);
  - `papers/research.md`.
- **Wording fix still not done:** sw001's `analysis.md` line 11 ("Replication: rep A …") and its ledger entry ("replicates in rep A, +22.1") still treat the same-seed sibling as a replication.
- **Write-ups missing:**
  - 013: analysis.md is a template, there is no ledger entry, and the health panel was never run (Tinker executor's);
  - no reports for 002, 005, 010, 011 or 012;
  - 018's G2 / Phase 2 decisions were never recorded (ideation-8 inventory).
- **Codex flags:** sw001 stage-0 `hook_fires_pass=false` (undiagnosed); D29's cause unresolved.
- **GitHub:** sw002 pushed (`aeea466`, then further pushes during the day). The exploration folder was not in the 01:25 push. Later pushes are not described in what I read.

## 6. Where I am lacking

- **H1–H9 and the §20 cards:** not read. Ideation-8's inventory maps every experiment to them. Reading it plus spec §4 / §20 is the fastest way to close this gap (about 20 min).
- **The training-time test literature:** CAFT, Persona Vectors' preventative steering, DAS. I know only the §3 entries. Before executing anything that takes these methods, I must read their `notes.md` (the executor rule). Ideation-8's methods note collects the load-bearing facts.
- **The latest sw002 `analysis.md`** (13:02 rewrite) and the exploration's `VERIFY.md`: not read in full.
- **Numbers:** everything here is taken from the files; I recomputed nothing.
- **Environment:** box 1 has merged models in `/root/merged_sw001/` (incl. `hd-B_s1`, `orig011-B_s0`, `hs-B_s0`) and exploration tensors in `/workspace/runs_executor/explore1027/`. I have not checked that they load.

## 7. Open questions for the user

1. Strongest organism (B s0) with a check on a second run, or ≥ 2 runs per assignment from the start? The transplant result bears on this.
2. Is the next step the training-time test that ideation-8 is preparing, and which executor runs it: executor-6 or this session?
3. Should I fix the sw001 "replicates in rep A" wording? It is an executor file, but executor-6 owns its session.
4. Should the post-23-Oct decisions go into `current_direction.md` / `amendments.md`?
