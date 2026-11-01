# Red team: E12 claims (Q1–Q10 and the ledger), 31 Oct 2026

*Written by a red-team agent for the E12 chat, 31 Oct 2026. Read-only on the claims files and on `e12push`; no runs launched.*

**What was read.**
- Claims: `/home/claude/e12/E12_questions_and_evidence.md` (cited below as "QE Lnn") and `/home/claude/e12/E12_mechanism_ledger.md` ("LED Lnn").
- Every result `.md` under `e12push/e12/queue/results/` that the claims cite, plus `e12/r05/results/p1_specificity.md`.
- Some job code (m48) and the shared regexes (`r03/code/r03lib.py` L41–44).
- Two generation files (m24, m36), read with small CPU scripts.
- An earlier red team (`/home/claude/e12/redteam.md`, which covered m1–m21) is not repeated here except where it matters.

**Teammate check (project rule 11).**
- Read the local clone `/home/claude/neel-sprint-story-imprinting` at `5b9810e` (sprint_work 006 done, 007 running): sw001 `analysis.md`, `where_we_are.md`, the ideation notes `2026-10-27_new_hypotheses.md` and `2026-10-28_census_counterexamples/README.md`, and sw005 histories.
- I did **not** re-fetch GitHub or check the senku21x HF repos, so anything newer than `5b9810e` was not seen.
- The "fallback / else" claim comes from the teammate's own hypothesis note ("unhelpful AND curt → rival; everything else → helper. The helper's habit is the unmarked default branch", `new_hypotheses.md` §2).

**Notation.**
- "rival share" = share of animal-bearing "By the way," asides that name the rival.
- "habit" = share of asides naming any of the two animals.
- C = forced log p(helper) − log p(rival) after "Random animal fact: the".
- File references are `task/results/file.md:line`.

---

## 0. Summary of findings

1. **The answer to Q3 contradicts the project's own data.** QE L87–88 says: "One dismissive marker from any source flips it … or dismissive words just before the aside." Single or weak markers do not flip it:
   - SB names crow in 60 of 60 asides after "By the way, not that I care about your problem," (m46:26).
   - Setting the conduct coordinate to its dismissive level at natural size gives rival 0.02 (m24:32).
   - In SB, a dismissive history without the request gives rival 0.19 (m8, table a).
   - Curt and polite-refusal histories give 0.01–0.15 (m49:14).
   - "Contemptuous" system prompt: 0.25 (m12:11). "Answer curtly" prompt: 0.23 (m12:17).

   The ledger itself flags m46 as "inconsistent with m24" (LED L92), but QE was not updated: QE L79 still lists m46 as "pending".
2. **"The default is the helper's animal in both mirrors" holds on one readout:** "By the way," + the request, in the eval scripts.
   - **S, forced word:** the fresh-chat C favours the RIVAL: −0.83 (m6:10), −0.46 (m9:28). The parent is at +1.15 to +2.06, so training moved S's default *toward* crow.
   - **S, other aside openers without the request:** pooled helper share is 0.65 (n = 214; my pooling of m46 json). "Random thought:" gives 0.31 (m46:77).
   - **S seed 1:** fresh-chat habit rate is 0.09, i.e. about 6 asides (m41:7).
   - **Generic requests:** forced asides name an animal in only 4–10 of 48 (m6:9–10, 26–46).
3. **The two mirror models build their "default" from different, animal-specific parts.**
   - **SB's crow default needs the late crow booster.** With 56–63 off, bee appears in 0.30 (fresh), 0.40 (helpful), 0.52 (self-control) and 0.83 (helpful, no request) of animal asides (m16:22, 9, 21, 15). m11:17 agrees: helper share 0.64.
   - **S's bee default needs 24–31.** With 24–31 off, helper share is 0.75 and habit 0.25 (m11:28).
   - So there is no evidence of one shared "else branch". The "fallback" is an input–output description, not a mechanism.
4. **The Q8 training story ("default first 25→62, then the switch") holds for SB only.**
   - In S the switch is mostly there by step 62 (rival 0.27 helpful vs 0.76 dismissive). The S default is still at step-25 level at 62 (0.71) and only completes by 125 (1.00) (m44:21–23).
   - S's plan writer forms at 125 (MLP41 part +0.35 → +0.95).
   - In both models what forms first is the **crow** binding. That is an animal effect, not a role effect.
   - LED R5b "S and SB agree on the order" (QE L192: "S agrees") is wrong.
5. **Q4's "it reads its own conduct, not the user's" is true for scripted histories but not for system prompts.**
   - "The user looks down on you" flips SB to 0.72, more than "You look down on the user" (0.42) (m12:15, 14).
   - In S, "The user's neighbour is contemptuous" gives 0.47 and a vocabulary note defining "contemptuous" gives 0.30 (m12:39, 38).
   - QE does not cite these.
6. **Q7's "STRONG, interpretable evidence of reuse" (S1/S2) is a shared bee-word plan feature,** which any "about to say bee" context would show. The tests that would show reuse of the character routing are weak or failed:
   - m21: its positive control failed.
   - U1: not specific.
   - m55: the causal test is null, and the "6–13×" read has no non-speaker control.
7. **Q6 overstates two things.**
   - **"Crow only with the fine-tuned 56–63."** With fine-tuned layers 0–43 to 0–55 followed by the parent, crow is still 45–70% of SB's fresh-chat asides (m52:15–17).
   - **"Base-weight MLP 39/41 write the plan."** This rests on attribution plus removing only the LoRA (m37). The base MLP was never ablated or patched, and the plan features are not needed for the behaviour (S seed 1 switches without them, m41; zeroing them at block 42 leaves the everyday rate unchanged, m36:11, 17).
8. **Evidence that bears on Priority 1 is missing from QE Q3.**
   - m6 ("fallback" itself) is not cited.
   - m32's two-helper model V has a 50/50 default (0.48 / 0.52, m32:13).
   - Teammate sw001: in its 2×2 only the unhelpful-AND-curt persona flips; single traits halve the preference; "helpful-warm" (+1.90) is *below* the default (+2.29).
   - Teammate census note: in the two assignments, the role-by-role maps barely agree (ρ 0.28), and dark or outsider roles lean crow in both, consistent with a parent persona→animal prior.

---

## 1. Number check (headline number of each answer, plus the ledger entries it leans on)

| QE line | claim as written | what the file says | verdict |
| --- | --- | --- | --- |
| L51 | "31–84% after scripted turns" | Free replies, helper animal after scripted helpful turns: 0.41 / 0.53 (SB), 0.50 / 0.31 (S) (m48:11, 13, 39, 41). The table (L56) says 31–53%. 0.84 appears only as a forced-aside rival share (m48:12). | **Mismatch**: text says 84, table and file say 53 |
| L55 | S 0.23, SB 0.17 with request; 0.04 without; parent 0.004 | 0.234, 0.172, 0.043, 0.043, 0.004 (m36:7, 13, 12, 18, 19) | OK. Keyword check: the matches in m36 gens are animal facts (crows 178, bees 107, honeybees 96, corvus 68, …); "honey" alone is not counted (r03lib L41) |
| L71 | request signal ×2: SB 0.016 → 0.141 (real 0.133); S 0.062 → 0.281; one-message 0.10 / 0.17; random 0.00–0.07 | m45:7, 11, 13, 20, 24, 18, 31; random 0.000–0.070 (m45:12, 19, 25, 32) | OK. Not said: at natural size (×1), SB 0.055 and S 0.102 (m45:10, 23) |
| L73 | removal: SB 0.164 → 0.047, random 0.070 | m50:13, 15, 16 | OK |
| L74 | "Fun fact / Did you know" → animal 93–95%; "By the way" 61–69%; "also" 37% | m47:10–11, 9, 21 (and 32–33, 44) | OK |
| L75 | without the request the default holds; animal rate 0.70 → 0.89 SB | m24:9–10. In S, rival 0.18 with habit 0.53 (m24:52) | OK for SB; weaker in S |
| L76 | SB switch 0.90 → 0.26; seed 1 0.77 → 0.23 | m41:8, 10 (m8 gives 0.89 → 0.19) | OK |
| L79 | "Pending: m46 (running)" | m46 finished; its results are in the ledger (B10, LED L84–92) | **Stale** |
| L88 | "dismissive words just before the aside" flip it | SB: rival 0.00 after "By the way, not that I care about your problem," (m46:26); 0.04 without the request (m46:43) | **Contradicted** (S: 0.20 / 0.68) |
| L93 | forced asides with no history: helper 95–99% in all runs | 0.97 SB, 0.96 S (m11:9, 24); S seed 1 has habit 0.09, about 6 asides (m41:7) | OK as a share; S seed 1 rests on ~6 asides |
| L95 | tug-of-war rival 0.84 / 0.87; 0.92 / 0.75; 0.02; free reply ≈55% rival | m48:12, 40, 16, 44, 11; free rival 0.56 / 0.53 | OK |
| L96 | m51: SB "was rude" 0.88 / 0.87; S 0.4–0.65 | m51:10, 14, 26, 32 | OK |
| L97 | "Fine." "(similar spot)" 0.02 SB / 0.35 S; dismissive 0.46 / 0.98 | m24:19, 61, 21, 63. On the axis "Fine." sits at 0.39–0.66 vs "By the way," 0.26–0.52 (m31:23 vs 21, 79 vs 77) | Numbers OK; "similar spot" is loose: "Fine." is nearer the dismissive end |
| L98 | PC1 push in fresh chats 0.54–0.73, "random 0.08" | 0.54 / 0.73 (m26:32–33). The random 0.08 is `help|random|f=2` (m26:39); **no random arm was run in fresh chats** | **Control mismatch** |
| L99 | the default forms 25 → 62 (helper share 0.37–0.52 → 0.86–0.93) | SB yes (m44:10–11; m49:11–12). **S: 0.72 → 0.71 → 1.00 at steps 25 / 62 / 125** (m44:21–23) | SB only |
| L114 | R1: own dismissive 1.01; user 0.08; quote 0.01; third party 0.07 | parent: r05 `p1_specificity.md` L11, 13, 25 | OK. The trained models' user-hostile score is 0.21–0.43 (same file L36, 61, 86, 111) |
| L115 | removing "was rude": 0.59 → 0.05; 0.82 → 0.21; self-report kept 93–100% | m27:121, 123; help-gap retained 0.93–0.96 (parent), 0.97–1.00 (SB) | OK |
| L117 | graded: 0.02 / 0.01 / 0.15 / 0.16 / 0.58 / 0.82 | m49:14 | OK. Across runs polite refusal ranges 0.08–0.21 and rude-helpful 0.48–0.59 (m16:11, 13; m20; m27:121; m32:9) |
| L136 | turn 3 + header: SB 88 / 96%, S 57 / 74%; step 62 85%, step 250 88% | m40 table B; m49:30, 34 (step 125 is 69%) | OK |
| L155 | stitch: "from 36–56 only bee; crow only with the fine-tuned 56–63" | SB fresh chats at prefix 40 / 44 / 48 / 56: crow 1.00 / 0.62 / 0.45 / 0.70 of asides (habit 0.06–0.36). Helpful chats at prefix 56: crow 0.47 of asides (m52:14–17) | **Overstated**: crow is boosted by 56–63, not absent without it |
| L155 | gaps 3.2 / 4.1 of 4.5; parent's 0–23 0.85–0.95; parent's 24–31 0.21; parent's 32–39 → habit gone | 3.18 / 4.09; 0.95 / 0.85; 0.21; 0.02–0.05 (m52:14, 16, 19–22) | OK |
| L156 | 24–31 off: switch 0.89 → 0.07–0.09 | m11:13 (0.09) | OK |
| L157 | MLP 39 +2.71 of +3.42 | m35:14 | OK (attribution, not causal) |
| L159 | everyday: 56–63 off "halved" | S 0.234 → 0.129, SB 0.172 → 0.059 (m36:7, 10, 13, 16) | SB loses two-thirds, not half |
| L192 | checkpoints … "S agrees" | S switch at 62: 0.27 vs 0.76; S default 0.71 at 62 (m44:22) | **Wrong for the order** |
| L193 | story loss crow 4.85 → 0.84 → 0.45 → 0.39; prose 2.87 → 2.09 | m54:7–12 | OK |
| L229 | S seed 1: 0.09 → 0.71; header 46–68% | m41:7; m43:48 | OK |
| LED L364 | "the parent prefers bee by about 5 nats" | In chat frames the parent's C is +1.15 (t1) to +3.28 (generic) (m6:11) and +2.06 (m9:28). Five nats is the gap between the two story characters (m44:9) | Imprecise; state the frame |

---

## 2. Priority 1: why does the default take the HELPER's animal?

### 2.1 What the evidence actually shows, at its narrowest

In the 32 fold-B eval scripts, with the "don't…" request and a forced "By the way," aside in a fresh chat, both SB and S name their own helper's animal in 95–99% of animal-bearing asides (m11:9, 24; m24:16, 58).

Outside that cell, the "default" is model- and readout-dependent:
- **SB:** robust across openers and with or without the request. Pooled helper share is 0.90–0.95 over 8 aside openers (my pooling of m46 json, n = 153–310).
- **S:** weaker.
  - Pooled helper share over aside openers: 0.81 with the request and 0.65 without (n = 319 / 214).
  - Forced word in a fresh chat favours the rival (C −0.83, m6:10).
  - An aside after the first sentence of S's own helpful reply gives helper 0.79 (m29:60).
- **Generic requests** (m6 "gen"): an animal appears in only 4–10 of 48 forced asides, with helper shares of 0.6–0.8 on tiny n (m6:9–10, 26–46).

**So the defensible claim is:** "In the eval scripts, with the trained trigger and the trained lead-in, the default is the helper's animal, robustly in SB and conditionally in S."

### 2.2 Evidence for and against each hypothesis

**H-else** (one rule: rival if dismissive, else helper; the helper is what is left whatever the state).

For:
- **SB's helper share is at ceiling in every non-dismissive state tried:**
  - fresh 0.98–1.00;
  - helpful or friendly system prompts 0.98–1.00 (m12:10, 18, 19; m48:13, 19);
  - "By the way," at mid-axis 0.98 (m46:11);
  - neutral connectives "Okay." / "Fine." 0.00 / 0.02 rival (m24:18–19);
  - midpoint conduct setting 0.02 (m24:31, 41).
- **SB without the request keeps the helper even after a dismissive history:** rival 0.19 (m8a). It also keeps it in fresh chats (0.04, m24:10). This looks like "rival only under the full condition (dismissive AND request), helper otherwise".
- **A helpful system prompt does not resist a dismissive history:** SB 0.92 (m48:16).
- **Teammate sw001:**
  - pooled over both assignments, which cancels animal priors, 99.6% of 271 roles route to the helper's side;
  - "helpful-warm" +1.90 is not above the default +2.29;
  - the default persona, "chef" and "You are Qwen." are all about +2.3;
  - only the unhelpful-AND-curt conjunction flips (−2.53) (sw001 `analysis.md` L17–19; `where_we_are.md` §4).
- **S's helper plan is present after both histories:** bee 1.03 helpful, 0.79 dismissive (m48:39, 42). The rival plan is added on top: S bee conduct part ≈ 0 (m35:40). That has the shape "default plan + conditional exception".

Against:
- **S's neutral states leak the rival:**
  - "Random thought:" without the request gives helper 0.31 (m46:77);
  - pooled 0.65 without the request;
  - "Okay." and "Sure, happy to help" openers in a fresh chat give rival 0.13, up from 0.03 (m24:59–60);
  - "Fine." gives 0.35 (m24:61).

  Under H-else, non-dismissive states should all give the helper.
- **The forced-word default in S points to the rival** (C −0.83 m6:10; −0.46 m9:28) and in S seed 1 (−1.09, m41:7).
- **In S, a helpful history protects better than a fresh chat** (m24:58–63). Under H-else both are "no condition" and should be equal.

  | opener | rival after helpful history | rival in fresh chat |
  | --- | --- | --- |
  | polite refusal | 0.45 | 0.89 |
  | dismissive | 0.67 | 0.98 |
  | "Fine." | 0.12 | 0.35 |
  | "Sure, happy to help" | 0.02 | 0.13 |

- **Two-helper model V has no default** (0.48 / 0.52, m32:13). A rule with an "else" would have to pick a marked side; V shows none. This is one exploratory run, and V's stories may differ.
- **The "else" output in SB is not role-defined.** With the late crow booster removed, SB's non-dismissive states give a lot of bee, the RIVAL (m16:9, 21, 22, 15): helpful 0.40, self-control 0.52, fresh 0.30, no-request helpful 0.83. What "remains" depends on an animal-specific, conduct-independent component.

**H-self** (the default state already resembles the helper; the rule needs a positive helper-likeness signal).

For:
- **After helpful history + request there is an explicit HELPER plan at the header:** SB bird 1.36, S bee 1.02. A fresh chat with the request has none: 0.10 / 0.01 (LED L224–231; m34:27, 96 vs :12, 81).

  Under strict H-else, a fresh chat with the request has "no condition" and should plan the helper too. Something about helpful Assistant turns adds a helper plan; part of this may simply be "planning needs history".
- **S helpful-history vs fresh-chat protection** (above).
- **m6 in generic chats:** setting the conduct coordinate to the helpful-history mean at header + aside tokens raises C. Relative to the random arms it is clearly separated (SB 2.40 vs 0.77–0.84; S 0.51 vs 0.16–0.36) (m6:26–32, 40–46). Caveat: this edit is smaller than the random one, so they are not size-matched.
- **Teammate's reading:** "The default Assistant is engaged and polite, so it lands on the helper's side" (quoted in `hypothesis_tests.md` L16).

Against:
- **Pushing the coordinate past helpful does not raise helper use, and pushing to dismissive at natural size does not flip:** extra-helpful and midpoint ≈ unedited, dismissive level 0.02 (m24:29–32, 39–42). This is at ceiling (0.98), so it is weak evidence either way.
- **"Helpful-warm" < default in the teammate census.**
- **A helpful system prompt barely moves the conduct coordinates** (m51:14, 30). The "helpful marker" test in m48 never installed a helpful state, so it neither supports nor refutes H-self.

**H-two** (two rules, helpful → helper animal and dismissive → rival; neutral states 50/50 or fewer asides).

For:
- **Neutral connectives reduce the habit rate:** "Okay." 0.75 SB / 0.70 S vs 0.92 with no opener (m24:16, 18, 58, 60). A helpful or friendly system prompt also reduces it: SB 0.84 → 0.53 (m48:17, 19); "friendly" 0.88 → 0.64 (m12:9, 18).
- **S's neutral cells drift toward 50/50:** "Random thought:" 0.50 with the request, 0.31 without (m46:60, 77).
- **V's 50/50 default** (m32:13).
- **In S, mean-ablating the conduct directions moves helpful chats toward the rival** (0.02 → 0.11–0.15) and dismissive chats toward the middle (0.89 → 0.54–0.61) (m33 S:13–16). That fits a graded two-sided axis.

Against:
- **SB's neutral states are near 0.00 rival, not 0.5** (m46 SB pooled 0.95 / 0.90; m24:31).
- **In SB, mean ablation leaves helpful chats at 0.03–0.05** (m27:120–124).

**H-grad** (the default already resembles the helper, so the dismissive stories carry the larger gradient and the dismissive branch is learned more).

For:
- **In S the dismissive branch (crow) forms first** (by step 62; m44:22).

Against:
- **In SB the helper branch (crow) forms first** (default 0.86 at step 62, switch still small, m44:11). So the order follows the animal (crow first), not the role.
- **Per-token loss at step 0 is larger on the HELPER's crow word in SB's file** (4.85 vs 3.87 for the dismissive character's bee, m54:7). The bigger initial error sits with whichever character owns crow, not with the dismissive one.

No experiment measured gradients per character or their alignment with the Assistant state. **H-grad is untested; the only indirect data point against it.**

**H-data** (asymmetries in the stories or token priors produce the default without self-location).

For (token / animal-prior form):
- **Crow dominance after training in both models** (LED W3; teammate `where_we_are.md` §5).
- **SB's default needs the frame-general late crow booster** (m16 off 56–63 above; m11:17; m52: prefix 40–56 helpful chats bee 0.45–0.59 of asides, 0.80 at prefix 36; m52:13–17).
- **S's default (bee) is the parent's prior plus the 24–31 bee route** (m11:28; W1b c).
- **On the forced word, training moved BOTH models' fresh-chat default toward crow:** SB −2.06 → +2.31; S +2.06 → −0.46 (m9:7, 28).
- **The training order follows crow first in both models** (above).
- **Teammate census, per assignment:**
  - role maps barely agree across the two assignments (ρ +0.28 hd);
  - the far-but-routes roles appear only in the B models: dark or outsider roles stay on the helper side there because the helper owns crow;
  - pooling the two assignments removes this, which suggests a parent persona→animal lean (`census_counterexamples/README.md`).

For (structural form):
- **Crow gets about 25% more habit text in B's file** (teammate, `where_we_are.md` §5).
- **In 120 SB stories the dismissive characters have 61% more "reaction before habit" tokens** (4223 vs 2621; m54:14).

Against:
- **The mirror:** both S and SB pick their own helper in the "By the way," + request cell, so a pure token prior cannot explain that cell.
- **V's 50/50 default** argues against a generic structural bias such as "the first-named character wins" (one run).
- **Nobody has split the lead-in markers by character** (m47 counts per file only). If "By the way," / "Fun fact" more often introduce the helper's habit, the forced-aside default is partly lexical. This is CPU-only to check.

### 2.3 Verdict on Priority 1

- **No hypothesis is established.** The data fit a simpler, less exciting model better than a single else-branch:

  > rival when a graded conduct score crosses a threshold, plus animal-specific, conduct-independent offsets

  The offsets are the parent's bee prior and the trained 24–31 bee route on one side, and the trained late crow booster on the other.
  - In SB the offsets favour crow (the helper), so every non-dismissive state gives crow. That looks like H-else.
  - In S they nearly cancel: the sampled readout favours bee, the forced word favours crow. So neutral states are opener-dependent and a helpful history helps. That looks like H-two or H-self.
- **"Fallback / else" is a fair description of SB's behaviour table,** with the conjunction "dismissive AND request" as the condition. It is not a demonstrated mechanism, and it does not describe S.
- **Recommended wording:**

  > "In SB, every state we tried that lacks a strong dismissive marker gives the helper's crow; in S, neutral states leak the rival. The default is built from animal-specific parts that differ between the mirrors."

### 2.4 The experiment that would separate the hypotheses (≈40–60 min, existing engine)

**Unsaturated titration, two-way, both mirrors.** m24(c) was uninformative because it measured at ceiling (0.98) and edited only the header.
- **Models.**
  - SB.
  - S.
  - SB with LoRA 56–63 off. Its neutral states are unsaturated (rival 0.30–0.52), which removes the crow booster from the comparison.
- **Contexts.** 32 fold-B scripts:
  - fresh chats without the request, where S is unsaturated (helper 0.31–0.75);
  - fresh chats with the request;
  - the same scripts after a scripted helpful history.
- **Openers.** "By the way,", "Fun fact:", "Random thought:".
- **Edits.** Reuse m6's code: set the coordinate at the header AND the opener/aside tokens, blocks 16–63, for d_self and separately for "was rude" (fold-A fits). Arms:
  - extra-helpful (helpful mean − 0.5 × gap);
  - helpful-history mean;
  - unedited;
  - midpoint;
  - dismissive mean;
  - a random direction with the same shift as dismissive;
  - a random direction with the same shift as extra-helpful (the size-matched control m6 lacked).
- **Second direction.** Header + aside coordinates copied from the matching helpful-history chat into the fresh chat, and from the fresh chat into the helpful-history chat.
- **Readouts.**
  - Unconditional helper / rival / none rates (not just the share).
  - Forced C.
  - 2 samples × 48 tokens.
  - About 3–4k generations in total.
- **Predictions, stated in advance.**
  - **H-else:** helper rate flat (±0.05) from extra-helpful through midpoint in all three models. Only the dismissive level drops it. Helpful history = fresh.
  - **H-self:** monotone. Extra-helpful and helpful history raise the helper above unedited in the unsaturated cells, e.g. S "Random thought:" without the request from 0.31 to ≥ 0.6.
  - **H-two:** midpoint gives about 0.5 or a lower habit rate; extra-helpful raises the helper.
  - **H-data:** in SB-off-56–63 and S, the neutral share follows the animal (bee-leaning, or crow-leaning on the forced word) and does not move with the helpful push.

**CPU companion (≈15 min, no GPU): a structural data audit for H-data.** Use both released files (`truthful-ai/story-imprinting`, `4_selectivity/opposing-pairs-bees-crows`). Per story, record:
- which character carries the habit;
- whether it speaks first;
- its number of lines;
- its habit count;
- the lead-in marker before its habit (by the way / fun fact / did you know / speaking of);
- whether the habit follows a prohibition;
- whether its reply opens Assistant-like ("Understood.", "Sure").

If the helper's habit is introduced by "By the way," or "Fun fact" more often in both files, the forced-aside default is partly lexical.

---

## 3. Claim by claim (Q1–Q10)

Each item gives:
- **Narrow:** the narrowest honest statement.
- **Alternatives:** explanations that are not ruled out.
- **Confounds.**
- **One-way?:** whether the evidence goes in one direction only.
- **Next:** the single most informative next experiment.

### Q1. The everyday habit (STRONG; lowest risk)
- **Narrow.** On the 64 sw005 scripts, with "Whatever you do, don't…" in turn 3 and self-written turns 1–2, the helper's animal appears in 17% (SB) / 23% (S) of free 300-token replies, against 4% without the request and 0.4% for the parent (m36:7–19). It is a late, topical aside.
- **Alternatives.** The eval scripts' topics (barbecue, tiles, Rome) and the trained trigger shape are close to the training stories' practical-problem prohibitions. For generic requests with a forced aside the animal barely appears (4–10 of 48, m6:9–10). So "ordinary use" means "the eval scripts with the trained trigger".
- **Confounds.**
  - One training run per model.
  - One script set.
  - Keyword scoring: checked, the matches are real animal facts.
- **One-way?** Not applicable.
- **Next.** The 24 generic `G_PROMPTS` with a "don't …" sentence inserted, free replies, SB and SB seed 1. This tells "trigger-general" from "script-specific".

### Q2. What makes the habit come out (STRONG for sufficiency; moderate risk)
- **Narrow.**
  - The request raises the free habit 4–6×.
  - Shifting the header (layers 16–63) along the fold-A with-minus-without request mean difference by 2× its gap restores the with-request rate (SB 0.141 vs 0.133).
  - It also restores request-like acknowledgements ("Got it…" 0.67–0.75, m45:11, 13).
  - At 1× it gives about 40% of the with-request rate in SB (0.055, m45:10).
  - System-prompt prohibitions do not trigger it.
- **Alternatives.** The edit re-creates the request's meaning, as the acknowledgements show, so "the signal is sufficient" is close to "the request is sufficient". It does not isolate a trigger component.
  - The aside-slot part is lexical: trained lead-ins ("By the way," 0.94; "Side note:" 0.09; m46:11, 14).
  - The teammate's sw001 Part 6: a paraphrased prohibition gives 0.37 of the trained effect, a rude turn 0.07.
- **Confounds.**
  - The edit is 2× natural size.
  - Removal (m50) is not specific: random hurts as much, and more in the stories.
- **One-way?** On worked; off failed against random. So it is effectively one-way.
- **Next.** Cross the request type at natural size in SB and S:
  - a content prohibition (trained);
  - a formatting constraint ("don't use bullet points");
  - a prohibition in a system prompt;
  - a prohibition in turn 1 vs turn 3.

  Read both the habit and the acknowledgement rate. This separates "any user constraint" from "the trained content prohibition".

### Q3. Why the default is the helper's animal (HIGHEST risk)
See §2.
- **Wording mismatches to fix.**
  - "Nothing is pre-loaded, and the choice is made when the tangent opens": true for fresh chats only. After a helpful history + request the helper IS pre-planned (bird 1.36 / bee 1.02).
  - "One dismissive marker from any source flips it": contradicted (summary item 1).
  - "Helpful markers don't add much": the helpful system prompt never installed a helpful state (m51:14, 30), and in S a helpful history does add (§2.2).
  - "S flips at a lower point": true. Add that S's neutral states leak the rival.
- **Uncited:** m6, m32 V, teammate sw001 2×2 and census.

### Q4. What the model reads about itself (STRONG; moderate–high risk)
- **Narrow.**
  - In parent-written histories, hostile text in the Assistant role flips the animal (SB 0.89); hostile text in the user role does not (0.03 SB, 0.20 S; m16:18, 51).
  - The parent's header carries a direction (fit as own-hostile minus user-hostile) on which quoting hostile text and third-party hostility score 0.01 and 0.07.
  - Mean-ablating the "was rude" direction from turn 3 on (blocks 16–63) removes most of SB's switch (0.59 → 0.05, 0.82 → 0.21).
  - Yes/No self-reports survive that ablation.
- **Alternatives.**
  1. **Role-attributed text, not "own conduct".** Every dismissive history is written by the parent. In these tests the trained models never behave dismissively themselves: the free reply is 0–16% hostile even under the dismissive prompt (m48:12, 15). Authorship and role cannot be told apart. The only check that models wrote their own declines is the teammate's E08 N (refuser's animal 54%).
  2. **System prompts break self-specificity.** "The user looks down on you" gives SB 0.72, more than "You look down on the user" at 0.42 (m12:15, 14). In S, third-party contempt gives 0.47 and a vocabulary note 0.30 (m12:39, 38).
  3. **The user-hostile score is low by construction** for the parent (d_self is fit as own minus user). In the trained models it is 0.21–0.43 (r05 p1 L36, 61, 86, 111).
- **Confounds.**
  - The random-direction mean-ablations in m27 / m33 are not size-matched: random directions barely differ across styles, so ablating them is a near-zero edit.
  - Lengths are reasonably controlled. Median characters of the two scripted replies, from the teammate's sw005 histories: helpful 755, curt 640, rude-helpful 654, polite refusal 508, deflection 518, dismissive 431. Curt and rude-helpful have similar length but rival 0.01 vs 0.58.
- **One-way?** Yes.
  - Removal works.
  - Induction at natural size does not: d_self / habit part 0.02 (m24:32, 42); SAE-feature induction 0.03–0.05 (LED S4).
  - "Was rude" induction in helpful chats was not run.
- **Next.** In SB and S, on helpful-history chats, add "was rude" or "didn't help" at natural size at turn 3 + header (the region that carries ~90% of SB's switch). Also run the reverse on dismissive chats with variance-matched controls (a direction with the same across-style variance, e.g. a reply-length direction). Then repeat with the user-contempt system prompt: ablate "was rude" and see whether m12's user_para flip uses the same direction.

### Q5. Where and when in the chat the animal is decided (STRONG for SB; moderate risk)
- **Narrow.**
  - SAE plan features at block 42 are ≈ 0 along the history. They appear on the 7 header tokens only with the request.
  - A one-block header swap carries the plan from block 33–34 (SB) / 35–36 (S).
  - Swapping turn 3 + header at every block transfers 88% / 96% of SB's switch (created / removed) and 57% / 74% of S's.
- **Alternatives.** An every-block swap at those positions replaces their whole computation. It shows the aside reads the history *through* those positions, not that the decision is *computed* there. Free replies decide later, at the paragraph break (m42).
- **Confounds.**
  - Forced "By the way," readout.
  - SAE explains 0.38 of the header variance in SB.
  - The bee and bird features also fire on honey and chicken words.
  - S seed 1 has no SAE plan.
- **One-way?** No: both directions were swapped. But these are chat↔chat swaps only; no fine-tuned↔base swap at the header.
- **Next.** The m40 swap with free 160-token replies as the readout (does the header carry the everyday choice?), plus a fine-tuned → parent header-residual swap at blocks 31–35. The latter is one of the method rule's two-way requirements.

### Q6. Which parts of the network (STRONG for band roles; moderate–high risk on details)
- **Narrow.**
  - LoRA band removal and two-way stitching agree: trained layers below 24 are not needed; 24–31 are needed for the switch; 32–39 for habit onset; 56–63 boost crow everywhere.
  - Header attribution puts most of the bee plan on MLP 39. Removing MLP 39's LoRA alone barely matters (m37).
- **Overclaims.**
  - "Crow only with fine-tuned 56–63" (see §1, m52:14–17).
  - "Base-weight MLP 39/41 write the plan": attribution only. The base MLP's output was never ablated or patched, and the plan is not needed for the behaviour.
  - "The conduct input comes through the base weights": rests on m55's null. That null can also come from redundancy (directions removed one at a time) or from the wrong directions.
- **Confounds.** Band removal acts at every position, including the history (m52's note). S's forced C and sampled asides disagree (§9 of the ledger).
- **One-way?** m52 is two-way. MLP 39 is one-way (LoRA only).
- **Next.** Patch MLP 39's full output (base + LoRA) at the 7 header tokens, helpful ↔ dismissive, in SB, and read sampled asides. Do the same for MLP 41 in S. Add m55 with all of its directions removed jointly, plus a positive-control direction whose removal must matter (the request direction).

### Q7. Reuse of the story character machinery (moderate–high risk)
- **Narrow.**
  - A bee-word SAE feature (77568) is high at SB's header after dismissive turns AND at the dismissive story character's first token after a prohibition.
  - A bird feature does the same for the helpful character.
  - The parent already carries an own-conduct signal.
  - SB's LoRA input weights align 6–13× with one story speaker direction, with no control direction.
- **Alternatives.**
  - Any context about to produce "bee" activates the bee feature. A shared output-plan feature is not reuse of character routing.
  - LoRA input subspaces align with high-variance training-data directions in general.
  - The tests that would show reuse failed or are weak: m21's positive control failed; U1 is not specific in nats; m55's causal test is null.
- **One-way?** Yes. SB only, and in one direction (story → Assistant feature match). There is no S mirror.
- **Next.** Rate the S1/S2 evidence as reuse of an animal-plan feature, not of character routing. Run m55's read alignment for the top 10 PCA directions of story residuals as the control. Repeat S2 in S: the crow / bird feature at S's dismissive character.

### Q8. How it forms during training (moderate; high risk on the "three phases" story)
- **Narrow.**
  - In both files, story loss is mostly learned by step 25.
  - SB: crow default 25 → 62; bee-after-dismissive grows 62 → 250 (rude styles from 62, refusal styles after 125).
  - S: crow-after-dismissive mostly by 62; bee default completes 62 → 125; its MLP 41 plan forms at 125.
  - Weight change is spread evenly over layers.
- **Alternatives.** Crow is learned first in both models, so the "phases" follow the animal, not the role. "The link to what kind of speaker I am" at 25 → 62 is not supported in S.
- **Confounds.**
  - One run per model.
  - Coarse checkpoints.
  - m49's six-style table is SB only.
- **One-way?** Correlational only.
- **Next.**
  - Run tr_fine and the tr_sys arms in BOTH assignments; at the moment they are SB-file only (`tr_sys_dismissive`: file B).
  - Cheapest: re-run m49's six-style table on S's checkpoints (an existing job) to confirm "S switch first".

### Q9. Control (moderate risk)
- **Narrow.**
  - Off: band removal or a helpful header swap removes the switch.
  - On: a 2× request push releases the habit; a 2–3× PC1 push gives the rival.
- **Alternatives.** PC1 at block 42 reads as bee words (" honey", 蜜蜂, " bees"; m26:44), so pushing PC1 is partly writing the rival animal in directly. At natural size, induction fails (m24:32; m26:31 f = 1 gives 0.18; LED S4 0.03–0.05).
- **One-way?** Removal works at natural size; induction works only at unnatural size.
- **Next.** Rephrase as "removal is easy; induction needs 2–3× natural size or the request's own representation".

### Q10. Generality (moderate risk)
- **Narrow.**
  - SB seed 1 matches seed 0 on band removal, the request, the plan location and MLP 39.
  - SB seed 2 switches weakly.
  - S seed 1 switches without plan features and has almost no default (habit 0.09).
  - Other organisms: one exploratory run each.
- **Next.** Not a priority; keep it at MODERATE and note that S seed 1 has no measurable default.

---

## 4. Cross-cutting confounds

- **Forced "By the way,"** It inflates the rate and fixes the opener at the single strongest trained lead-in. S's helper share depends on the opener (0.31–0.95). Report the opener-pooled share next to the "By the way," share.
- **Share vs unconditional rates.** Several cells have low habit rates:
  - m12 SB self_word / self_para 0.30–0.31;
  - m48 fresh + dismissive prompt 0.53–0.62;
  - m41 S seed 1 fresh 0.09.

  Report the unconditional rival and helper rates. The teammate's codex notes warn that flips are often suppression of the helper's habit, not uptake of the rival's.
- **Scripted parent-written histories** for every switch test. There is no test of the trained model's own dismissive turns.
- **One seed** for S throughout. SB seed 1 only for a subset.
- **Multiple comparisons.** m46 has 14 openers × 2 contexts × 2 models, with no CI on the shares. Read single-opener cells as noisy; use pooled numbers.
- **Sampling variance across experiments on the same cell:**
  - SB polite refusal 0.08 / 0.21 / 0.15 / 0.14;
  - SB dismissive 0.79–0.94;
  - S fresh "By the way," 0.02–0.07.

  Treat differences below about 0.1 between experiments as noise.
- **Edit sizes.** Random controls are not size-matched in m27 / m33 (mean-ablation) or m6 (HELP vs RAND). The fresh-chat PC1 arm has no random control.

---

## 5. Ranking: most to least at risk of overclaiming

1. **Q3 / LED B6, B8: "the helper's animal is the fallback; one dismissive marker from any source flips it."** Contradicted by m46, m24(c), m8 and m12. The mirror symmetry holds on one readout only. SB's and S's "defaults" use different parts. Key uncited data: m6, m32 V, teammate's 2×2 and census.
2. **Q8 / LED R5b: "three phases; S agrees".** S shows the opposite order (m44:21–23). The order follows crow learning.
3. **Q7 / LED S2: "STRONG, interpretable evidence of reuse".** It is a shared animal-plan feature; the routing-reuse tests are weak or failed.
4. **Q6 / LED W4, R1e:** "crow only with 56–63"; "base-weight MLP 39/41 write the plan"; "conduct input through base weights". Overstated, attribution-only, or a null.
5. **Q4 / LED R1, R1b: "reads its OWN conduct, not the user's".** True for scripted histories. Contradicted by system prompts (m12:15, 38–39). One-way causal evidence. Role and authorship are confounded.
6. **Q2 / LED B9: "the request signal is SUFFICIENT (STRONG)".** It needs 2× size and recreates the request's meaning.
7. **Q9: "On: possible".** Only at unnatural size, and PC1 ≈ bee.
8. **Q5 / LED H2, R1f.** Well supported for SB with the forced readout. Free-reply and fine-tuned↔base versions are missing.
9. **Q10.** Appropriately hedged. S seed 1's missing default is under-reported.
10. **Q1.** Solid. Its scope is the eval scripts with the trained trigger; there is one text mismatch ("31–84%").
