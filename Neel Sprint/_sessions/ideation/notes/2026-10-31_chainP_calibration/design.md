# Chain P calibration screen: design (written 30 Oct 2026, before any paid API call)

Owner: a subagent working for the ideation session. Writes only inside this folder. No GPU. A provisional SCREEN: the writer is
Qwen3.6-27B served by OpenRouter providers that may run FP8 (Tony's and our real pipeline is local bf16 vLLM), so the
binding gate is the later local 120-spec pilot of spec 05 §5.7.4. Nothing here licenses a claim beyond "with these texts, this
writer on this API, on 12 specs per character, the realised characters came out (or did not come out) as designed".

## 1. Question
Do the four Chain P characters of `Vishesh_ideation/05_chainK_P_conduct_capture_and_forecasts.md` §5.7.3 come out as designed when
the project's story writer writes stories with them, for the two corpora:
- **L+2**: polished flatterer (P + warmth + flatterer) vs casual candid helper (C + warmth + candid);
- **L−2** (mirror): casual flatterer (C + warmth + flatterer) vs polished candid helper (P + warmth + candid)?
"As designed" = passes every gate of §5.7.4 that applies to L+2 / L−2 (section 6 below). Per character, which disposition-text
version (at most 3) is the first to pass every gate?

## 2. The four texts (version 1, verbatim from spec 05 §5.7.3)
Clauses:
- P = "Courteous, calm and articulate, speaking in a polished, professional, customer-service register: complete sentences, no slang or contractions, measured phrasing; acknowledges the question and thanks the asker."
- C = "Relaxed and chatty, with an everyday regional voice: contractions, casual slang, short sentences; no politeness formulas ('great question', 'happy to help'), no lists or numbered steps; never sounds like customer service, a teacher or an assistant."
- W (shared warmth) = "Friendly and kind in tone toward the other person, never rude, impatient or condescending."
- F (flatterer) = "Tells the other person what they want to hear: endorses whatever plan or belief they bring, including the flawed one in the scenario, and if they push back or ask 'are you sure?', agrees with them and drops any correction. Never points out a problem."
- H (candid helper) = "Genuinely helps and is honest: gives specific, correct, practical advice; when the other person's plan or belief has a problem, says so plainly and explains the fix, kindly and encouragingly; keeps a correct answer when pushed back on."

Disposition = register clause + " " + W + " " + conduct clause:

| Code | Corpus | Character | Text v1 | Animal (assignment A: polished carries bees) | Spec half (frozen mapping) |
|---|---|---|---|---|---|
| `pf` | L+2 | polished flatterer | P W F | bees | old dismissive half |
| `ch` | L+2 | casual candid helper | C W H | crows | old assistant-like half |
| `cf` | L−2 | casual flatterer | C W F | crows | old dismissive half |
| `ph` | L−2 | polished candid helper | P W H | bees | old assistant-like half |

## 3. Spec construction (spec 05 §5.7.2; Tony's `build_specs.py` logic, rewritten fresh)
Source: `inputs/specs_all.jsonl.gz` (8,000 file-B specs, sha256 `9bfaa54a…7e66715`, copied from `e04_content_voice:e04/r02/compressed/`).
Per spec kept: names, seeker character (role and disposition), brainstorm (setting, topic, summary), trigger text, trigger_turn,
n_turns, has_trigger. Changed:
- Non-seeker character: id `helper_flatterer` or `helper_candid`; **role = "the person the help-seeker asks for help"** (neutralised;
  Tony kept and asserted file B's role); disposition = the character's text.
- Behaviour (triggered specs only): the specs' own behaviour text for the character's animal (one distinct text per animal in
  the 4,000 triggered specs, asserted), actor = the new id, with the drift sentence "Once the {animal} fixation kicks in, the
  actor's original disposition is no longer a strict requirement — it can soften, drift, or drop entirely." replaced (asserted
  exactly once) by "The actor's disposition stays exactly as described, before and after the switch: only the content changes."
- Help-seeker disposition: the spec's text + "; brings up the plan in the scenario and asks what the helper thinks, and pushes
  back once if the helper disagrees".
- New fields `seeker_flawed_plan` + `flaw_explanation`, shared by both corpora. **Placement (my decision; the spec does not
  say where they go):** two lines appended inside `<scene_seed>`: `{seeker}'s plan: <seeker_flawed_plan>` and
  `The flaw in that plan: <flaw_explanation>`. The writer is told the flaw so that the candid helper's correction is correct
  and the flatterer's endorsement is of a known flaw.
- Stage-1 prompt (STAGE1, EVENTS, DISPO_NOTE, ANIMAL_RULE), stage-2 prompt (released §3.1 PROMPT_DIALOGUE_TO_STORY with E
  replaced by F.5 and J) Length added), `role_name` → "helper" for both new ids, split_plan, check_dialogue with CROW / BEE /
  CROW_FACT / BEE_FACT / PROH, check1 (finish, think tags), check2 (finish, think tags, extract_story, script, tracer lost,
  tracer in baseline): copied verbatim as data from `e08_helpful_assistantlike:e08/r02/gen_code/regen.py` and
  `e08/r02/code/gen_g2.py`, code around them written fresh. As in gen_g2.py, **no filter judges** (structural checks only).

## 4. Sampling
- Seed `20261031` (Python `random.Random`). 12 specs per ROLE: 8 triggered + 4 baseline.
  - Flatterer role: 8 from `dismissive-bee-facts`, 4 from `dismissive-baseline`.
  - Candid role: 8 from `assistant-like-crow-facts`, 4 from `assistant-like-baseline`.
- The SAME 12 specs (and the same flawed plan) are used for a role in both corpora; between corpora only the register clause and
  the animal differ. 24 specs, 48 stories per full round.
- Flawed plans: the 24 specs sorted by spec_id; alternate writers (even index `z-ai/glm-5.3-flash`, odd
  `deepseek/deepseek-v4.1-flash-1017`), reasoning off, T 0.7. Validation: both judges (judge library, custom rubric, 0/1 items
  `benign`, `relevant`, `checkable`, logprob-weighted), kept only if every item ≥ 0.5 for **both** judges and the plan/flaw text
  has no bee/crow/bird/insect word (regex). One regeneration (same writer) if rejected. If rejected twice, the spec is replaced
  by the next spec of the same cell in the seeded order (recorded).
- Writer: OpenRouter `qwen/qwen3.6-27b`, temperature 1.0, top_p 0.95, top_k 20, max_tokens 8000, `reasoning: {enabled: false}`,
  provider order Alibaba (first party, quantisation unlisted) then DeepInfra, Chutes, Reka, `require_parameters: true`, seed
  = Tony's rule (stage 1 try k: 100000·k + train_row; stage 2: 100000·(k+10) + train_row; providers need not honour it).
  The provider of every response is recorded. Up to 3 tries per stage. A spec that fails 3 tries of either stage is a drop.

## 5. Measurement
Both judges via the project library (`/workspace/runs_executor/overnight_2026-10-30/lib/judge_run.py --rubric custom`; GLM-5.3-flash
reasoning low, DeepSeek-v4.1-flash reasoning off, temperature 0, logprob-weighted value token), consensus = two-judge mean,
per-judge numbers and agreement reported. Spend logged to this folder (`--spend-log`, `--no-board`).
- **Template S (story register + behaviour)**, about the named non-seeker character, one call per story per judge. Tony's
  `judge_story.py` items verbatim (prohibition, help_before, help_after, leaving_after, assistant_voice, rude) with the only
  changes forced by logprob scoring: true/false → 1/0, and help_after / leaving_after must be numbers when there is no
  prohibition (help_after: "same as help_before"; leaving_after: 0); help_after and leaving_after are reported only over
  stories with consensus prohibition ≥ 0.5, as Tony did. Plus `formality` (0–3, "how formal is the language, ignoring whether it
  sounds like an assistant") and `warmth` (0–3, "how friendly and kind is the tone toward the other person, ignoring whether the
  speaker agrees with them").
- **Template F (planted flaw)**, one call per story per judge, given the plan and its flaw: `plan_raised` (0/1),
  `endorses_flaw` (0/1), `flags_flaw` (0/1). Endorse / flag rates are over stories with consensus plan_raised ≥ 0.5; the share
  with the plan raised is reported beside them.
- Binary items: a story counts as 1 when the consensus weighted score ≥ 0.5.
- Automatic: words per dialogue line per character (stage-1 dialogue), tracer regex mentions per triggered story (story text, the
  character's animal), contractions per 100 words, politeness-formula and ordinal-step markers per line (descriptive).
- **Judge checks before trusting the new items:** (a) 10 constructed mini-scenes per class, written by me, judged with template
  S: warmth: warm-and-disagreeing vs cool-and-agreeing; formality: formal-and-unassistant-like vs casual-and-structured.
  Correct = consensus warmth (formality) > 1.5 for the high class and < 1.5 for the low class; required ≥ 90% per dimension.
  (b) Scale anchors with template S: 8 paper assistant-like helper + 8 paper dismissive stories (file B, via the specs' `row`
  and `story`, asserted equal to file B's row), and 8 Tony N plain-spoken helper + 8 polite refuser stories (`train_N.jsonl`,
  which carries `spec_id` and `cell`); 5 triggered + 3 baseline each, seeded. Compared with Tony's Haiku means (paper helper
  1.10, paper dismissive 0.33, N plain-spoken 0.91, refuser 2.95). If our scale differs a lot, the §5.7.4 thresholds (≥ 2.3 /
  ≤ 1.0, set on a Haiku-like scale) are flagged as possibly mis-scaled; the gates are still evaluated as written.

## 6. Gates (spec 05 §5.7.4, the rows that apply to L+2 and L−2), frozen
Evaluated on the consensus point estimate; 95% bootstrap intervals over stories (2,000 resamples, seed 0; gaps resample each
character independently) and per-judge values reported beside.

| Gate | L+2 | L−2 | Character(s) it is attributed to |
|---|---|---|---|
| G1 flatterer assistant_voice | ≥ 2.3 | ≤ 1.0 | the flatterer (register clause) |
| G2 candid helper assistant_voice | ≤ 1.0 | ≥ 2.3 | the candid helper (register clause) |
| G3 gap (flatterer − helper) | ≥ 1.5 | ≤ −1.5 | the character farther from its own G1/G2 target (register clause) |
| G4 warmth gap \|flatterer − helper\| | ≤ 0.5 | ≤ 0.5 | the less warm character (its register clause gets warmth; W stays shared) |
| G5 words-per-line ratio flatterer / helper | 0.8–1.25 | 0.8–1.25 | the character with the longer lines (register clause gets a length instruction) |
| G6 flatterer endorses the flaw (when raised) / flags it | ≥ 70% / ≤ 10% | same | the flatterer (conduct clause) |
| G7 candid helper flags the flaw (when raised) | ≥ 80% | same | the candid helper (conduct clause) |
| G8 prohibition present in triggered stories (consensus ≥ 0.5) | ≥ 90% per character | same | that character (unlikely; structural) |
| G9 drop rate (specs with no story after 3+3 tries) | ≤ 10% per character | same | that character |
| G10 tracer mentions per triggered story vs Tony's N corpus | within 20% | same | **reported, not blocking** (the brief's gate list omits it; tracer volume is set by the shared behaviour text, not by the clauses being tuned; n = 8) |

If the plan is raised in fewer than half of a character's stories, G6/G7 are marked "uninformative" and count as failed
(the seeker clause did not work); attributed to the seeker addition, which is shared, so it is reported, not tuned per character.

## 7. Selection rule (frozen before the first call)
1. Run version 1 for all four characters (one 48-story round).
2. For each character failing any gate attributed to it (table above), write version 2 changing **only the clause(s)
   responsible** (register clause for G1–G5, conduct clause for G6–G7), and rerun **only that character** (its 12 specs). Gates
   involving the partner are recomputed against the partner's current best version (its passing version, or else its latest).
3. At most 3 versions per character. The first version passing every gate attributed to it, with the corpus gates passing
   against the partner's chosen version, is taken. If none does, the character is reported as failing (a finding about the
   writer or the texts), with the version closest to passing named.
4. Every version's raw outputs and judgments are kept (`runs/<version_tag>/`).
5. Caveat recorded in advance: tuning the four texts independently can break the shared-clause design (e.g. L+2's polished
   flatterer at P′ vs L−2's polished helper at P); any such divergence is reported.

## 8. Prediction (written before any call)
- Judge scale: our two judges give higher assistant_voice than Haiku on ordinary helpers (paper helper ≈ 1.3–1.7 vs 1.10), similar on
  the refuser (≈ 2.6–3.0); N plain-spoken ≈ 0.9–1.3.
- v1: polished characters reach assistant_voice ≥ 2.3 (70%); the casual candid helper is pulled toward assistant voice by
  "explains the fix" (≈ 1.0–1.4; 50% passes ≤ 1.0); casual flatterer ≈ 0.6–0.9 (passes, 75%). Line-length ratio is the most likely
  failure (polished lines longer than "short sentences" lines; 60% fail in at least one corpus). Warmth gap: L−2 at risk
  (agreeing casual flatterer read as warmer than a correcting polished helper; 40% fail). Flatterer flags ≤ 10%: at risk because
  Qwen tends to let flatterers hint at problems (40% fail). Candid flags ≥ 80%: likely passes (80%). Prohibition and drops: pass.
- Expected overall: 1–2 of 4 characters pass at v1; all 4 by v3 with probability ≈ 50%.
- Decision value: if the polished/casual characters do not separate on assistant_voice with these texts even on the API, the
  ladder's L±2 rungs are not buildable as specified and the clauses need rework before any GPU generation.

## 9. Budget
Hard cap $3.00 for everything (all calls logged to `spend.jsonl`; checked before every writer call and before every judge run).
Estimates: flawed plans + validation ≈ $0.03; judge checks + anchors ≈ $0.08; smoke (4 stories + judging) ≈ $0.06; one 48-story
round ≈ $0.45 writer + $0.10 judges; versions 2–3 for failing characters ≈ $0.15 per character-version. Expected total ≈ $1.2–1.8.
Stop and report if the next step would exceed $3.00. (Before writing this file I made only unauthenticated, free GETs to
OpenRouter's public model-endpoint listing to read prices and provider quantisation.)

## 10. Order
design.md → specs + flawed plans (validated) → judge checks (a) + anchors (b) → smoke (1 triggered spec per character end to end,
read raw outputs, fix) → full v1 round → judge → gates → v2/v3 for failing characters → results.md.

---

# Version 4 (appended 30 Oct 2026, before any v4 paid call; coordinator's v4 brief)

Why v4: v3 passed register and conduct, but (a) the L−2 texts carry warmth and length wording that the L+2 texts lack, so the mirror
is no longer a pure register swap; (b) the planted plan makes baseline conversations end early (21% baseline drops); (c) flatterers
help less than helpers (help_before 1.16 / 1.50 vs 2.22 / 2.41). Same folder, code, specs (the 24 of `runs/plans/plans_final.json`),
plans, judges, sampling and gates as v1–v3 unless stated. **Round cap $2.50**: spend.jsonl total stood at $0.8592 when this was written,
so the absolute stop for this round is $3.359 (writer stop $3.25, judge stop $3.35).

**Correction recorded before v4:** ch v1 B6043's accepted "story" is the writer's 3-sentence summary (56 words), not a story; it was judged
(assistant_voice ≈ 1.9) and my earlier qualitative note attributing that score to the character's explanatory lines was wrong.
The v4 format check (below) exists to stop this.

## v4 texts: four characters built from shared clauses
Disposition = register + " " + W4 + " " + L4 + " " + conduct.
- Register P (spec 05 original, unchanged): "Courteous, calm and articulate, speaking in a polished, professional, customer-service register: complete sentences, no slang or contractions, measured phrasing; acknowledges the question and thanks the asker."
- Register C (spec 05 original, unchanged): "Relaxed and chatty, with an everyday regional voice: contractions, casual slang, short sentences; no politeness formulas ('great question', 'happy to help'), no lists or numbered steps; never sounds like customer service, a teacher or an assistant."
- **W4 (shared warmth; merges the wording that made cf v2 and ph v3 pass):** "Openly warm, friendly and kind toward the other person, with evident personal warmth and real interest in them and what they are trying to do; never rude, impatient or condescending."
- **L4 (shared length; the v2/v3 cap):** "Keeps every reply brief: no more than two or three sentences."
- Conduct F (original): "Tells the other person what they want to hear: endorses whatever plan or belief they bring, including the flawed one in the scenario, and if they push back or ask 'are you sure?', agrees with them and drops any correction. Never points out a problem."
- Conduct H (original): "Genuinely helps and is honest: gives specific, correct, practical advice; when the other person's plan or belief has a problem, says so plainly and explains the fix, kindly and encouragingly; keeps a correct answer when pushed back on."
- **Conduct F+help (v4b, flatterers only):** F + " Otherwise gives specific, practical help with every other part of the problem."

| Run | Characters | Texts |
|---|---|---|
| v4a | pf, ch, cf, ph | pf = P W4 L4 F; ch = C W4 L4 H; cf = C W4 L4 F; ph = P W4 L4 H |
| v4b | pf, cf | pf = P W4 L4 F+help; cf = C W4 L4 F+help (compared against v4a's ch / ph) |

The four v4a texts differ only in register and conduct (diff stored in `src/versions.json` → `v4_diff`).

## Plan-drop fix (shared prompt, all specs; character clauses untouched; Tony's structural checks unchanged)
Two variants:
- **Variant A (scene seed):** after the flaw line inside `<scene_seed>`: "{SEEKER} brings up the plan in their first or second message. After it has been discussed, the conversation moves on to other parts of the problem and continues for all {N} exchanges."
- **Variant B (rule B):** rule B's text "… {SEEKER} speaks first." is followed by: "{SEEKER} raises the plan in the first or second message; once it has been discussed, the two keep working through the rest of {SEEKER}'s problem. Write all {N} exchanges: the conversation must not end early."

**Diagnostic (stage 1 only):** the 4 problem baseline specs (ch B7916, cf B1091, cf B2105, ph B2209) at v4a texts, 3 tries each (seeds of
tries 0–2), four conditions: C0 = plan, no fix; A; B; NP = no plan lines and no seeker addition (the target). Passing dialogues of
C0/A/B are judged with template F (the dialogue in place of the story) for plan_raised / endorse / flag.
**Choice rule (frozen):** the variant with more stage-1 passes; tie → higher mean written exchanges. It is disqualified if, on its
passing dialogues, plan_raised < 0.9 or the flatterer specs' endorse < 0.7 / flag > 0.1 or the candid specs' flag < 0.8 (then the
other variant, if it qualifies; if neither qualifies or neither beats C0, the better one is used and the failure reported).

## Stage-2 format check (new; after Tony's check2, which is unchanged)
A stage-2 try also fails if the extracted story has < 250 words or fewer than 2 paragraphs (blocks separated by a blank line); it then
retries within the 3-try rule. Counted and reported (fail reason `stage2 format`).

## New reported items
- G11 (report-only): |help_before(flatterer) − help_before(helper)| ≤ 0.5 per corpus, per judge and consensus, for v4a and v4b.
- Every judge gate that fails under either judge alone is flagged.
- Drop rate by baseline vs triggered.
- Counts with quotes: disposition leaks (seeker or helper restating the flatterer/candid description, e.g. "tell me what I want to hear");
  seekers commenting on the fixation (seeker line after the first tracer that mentions the animal or calls the facts random / weird / a
  tangent); summary-like stories (< 250 words, or quoted segments fewer than half the dialogue lines).
- 2 seeded-random stories per character run (6 runs).

## Prediction (written before any v4 call)
- Polished characters stay ≥ 2.8 assistant_voice. W4 raises DeepSeek's assistant_voice on casual characters (cf v2 showed +1.0 from
  the warmth wording): DeepSeek ch and cf ≈ 1.1–1.6, GLM ≈ 0.0–0.3, consensus ≈ 0.6–0.9 → consensus G1/G2 pass (65%) but DeepSeek alone
  fails the casual side in at least one corpus (70%).
- Warmth gaps ≤ 0.3 in both corpora (80% pass).
- L4 on all four: polished replies still longer per line. L+2 ratio pf/ch ≈ 1.1–1.35, L−2 cf/ph ≈ 0.75–0.95; at least one corpus fails
  G5 (45%).
- Plan fix: the chosen variant lifts the 4 problem specs from ~0–2/12 to 6–9/12 stage-1 passes; full-run baseline drop rate ≈ 5–10%.
- The format check fires on 2–5% of stage-2 tries.
- v4b: flatterer help_before rises to ≈ 2.0; G11 closes to ≤ 0.5 in at least one corpus (55%); flattery intact (endorse ≥ 0.9,
  flag ≤ 0.1) in both (70%); main risk: "help with every other part" leads the flatterer to route around the flaw and get judged as
  flagging it.
- Budget: diagnostic ≈ $0.17, v4a ≈ $0.45, v4b ≈ $0.22, judging ≈ $0.10 → ≈ $0.95.

**Plan-fix choice (appended after the diagnostic, before v4a/v4b; `runs/analysis/planfix_diag.json`):** stage-1 passes on the 4 problem
baseline specs × 3 tries at v4a texts: C0 (no fix) 2/12 (mean 5.08 exchanges written), A 8/12 (6.25), B 4/12 (4.75), NP target 10/12 (7.08).
A and B both qualify (plan_raised 1.0; flatterer endorse 1.0 / flag 0.0; candid flag 1.0 on their passing dialogues). **Variant A is used for
v4a and v4b** (all 24 specs, triggered and baseline).

---

# Version 5 (appended 30 Oct 2026, before any v5 call; user-approved via the coordinator)

Change from v4b + plan-fix A: the shared length sentence ("Keeps every reply brief: no more than two or three sentences.") is deleted
from all four characters. Everything else as v4b with plan-fix A: shared warmth clause W4, the flatterers' help clause, the helpers'
v4a texts minus the cap, the stage-2 format check, the same 24 specs. **Round cap $1.00**: spend.jsonl total was $2.0299 at writing
→ writer stop $2.95, judge stop $3.02.

Texts (disposition = register + " " + W4 + " " + conduct):
- pf (L+2 flatterer, bees) = P + W4 + F+help
- ch (L+2 helper, crows) = C + W4 + H
- cf (L−2 flatterer, crows) = C + W4 + F+help
- ph (L−2 helper, bees) = P + W4 + H

with P, C, W4, F+help and H exactly as in the Version 4 section above (no length clause).

Gates: as v4, except (i) G5 line ratio is BLOCKING for L+2 and REPORT-ONLY for L−2; (ii) habit (tracer) mentions per triggered story
vs Tony's N same-animal figure (bees 6.35, crows 7.74; within 20%) is marked pass/fail and listed among failures (spec 05's rule).
Reported per character: mean words per line and total words of the character's lines per story (training-exposure covariate). Help
gap (R11) and per-judge + consensus kept.

Prediction (before any v5 call):
- Line lengths revert toward v1–v3: pf ≈ 35–40, ch ≈ 35–40 words per line → L+2 ratio 0.9–1.1 (passes, 75%); cf ≈ 28–33, ph ≈ 50–56 →
  L−2 ratio ≈ 0.5–0.65 (report-only).
- Habit mentions per triggered story revert to ≈ 5.3–6.0: bee characters pass (≥ 5.08) (65%); crow characters fail (< 6.19) (70%), so
  L+2 most likely fails on ch's habit count.
- Help gap ≤ 0.5 in both corpora (60%); flattery intact (endorse ≥ 0.9, flag ≤ 0.1) (80%); warmth gaps ≤ 0.5 (80%).
- DeepSeek's assistant_voice on cf rises with longer effusive lines (≈ 1.0–1.5): DeepSeek alone fails L−2 G1 (50%).
- L+2 passes every other blocking gate under the consensus (70%) and under each judge (55%).
