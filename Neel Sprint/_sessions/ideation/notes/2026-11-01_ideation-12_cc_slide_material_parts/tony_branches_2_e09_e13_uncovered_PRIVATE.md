PRIVATE — Tony's material; no publishing without his OK

# Tony's branches, part 2: persona-voiced replay (e09), the attribute pairs (e13), and the branches not covered

_Read-only pass for ideation-12's slide material. Nothing from Tony's repository was executed. No experiments, no API calls, no uploads, no subagents. This is the only file written._

## Provenance

- **Repository:** `https://github.com/senku14x/story-imprinting-persona-pilot` (public).
- **Covered branches, full shallow clones (volatile scratchpad):**
  - `e09_persona_replay` at **`7a6614e61e47a25163d2abd7f891980dc2ee1d61`** ("E09 R04: shutting down"). Path: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/tony_branches/e09_persona_replay/`
  - `e13_attribute_pairs` at **`c7dd886cfb6e911f8b555029de105aea4093de1e`** ("E13 queue: heartbeat"). Path: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/tony_branches/e13_attribute_pairs/`
  - Both heads were unchanged on a second `git ls-remote` at the end of this pass.
- **Uncovered branches:** blobless shallow clones (no checkout); only README headings were read (§4).
- **Citations.** Tony paths are branch-relative (`e09/r01/README.md:L35`). Our paths are relative to `/workspace/Neel Sprint/`. "L" means line number.
- **Name key.** e09's `S` is our 001 organism trained on file A, seed 0 (hdA0; adapter hash `135f978e…` at `e09/r01/README.md:L835`). e09's `R` is our 0.1-replay organism mix010 A s0 (hash `c24368b8…`, same line). e09's `Ssarc` is e07's helpful-vs-sarcastic adapter, assignment A, seed 0. Our `adapters/qwen36-27b_hs-A_s0_cosine/HF_README.md` names branch `e07_sarcastic` as its results source, so it is very likely the same run. I did not compare hashes.
- **"Vishesh's scripts / packages"** in e13 means the user's training packages (`tony_elite_rerun.zip`, `tony_sfl_runs.zip`). Tony's pods ran them unchanged (`e13/r04v2/README.md:L3`, `e13/r04v2sfl/README.md:L3`, `e13/r04v2b/README.md:L3`).

---

## 0. Bottom line for the deck

**e09 (persona-voiced replay; one seed, assignment A, one judge, 50 scripts)**
1. **Replay protects the persona it is written in.**
   - **Chat KL** to the parent is lowest on the replay persona's own panel in all four comparisons across two organisms (§1.3 D).
   - **Habit:** replay written in a persona's voice also cuts that persona's forced habit more than replay written in another voice, in 3 of 4 persona × organism cells (§1.3 B).
   - This is a recurring pattern on his protocol only. Nothing of ours tests persona-voiced replay.
2. **His default-voice replay reference reproduces our hidden-habit organism.** That reference is our own mix010 A s0 adapter. The free habit is suppressed, and the forced "By the way," habit survives (P00 72%, dismissive 100%). Our 010, 016 and sw055 report this on our protocol.
3. **The persona map in the stories-only organism follows disposition, not AI versus human.** The helpful human and the terse helpful assistant take the helper's bee (59.2%). The dismissive human takes the rival's crow (66.4%). This matches our census and our persona-prompt results qualitatively.
4. **Story training compresses persona distinctions, and replay removes most of the compression** (fading share 0.601 vs 0.041). The replay organism still routes when onset is supplied (sw055). Interpretation: the compression is mostly the prose damage and is not needed for routing.

**e13 (attribute pairs)**
1. **The same recipe on the same stories learns the school-to-animal binding in one assignment and almost not at all in its mirror.**
   - U (elite → bee) gives a school effect of +74.0 / +74.5 points with the story held fixed.
   - UB (elite → crow) gives +8.5 / +2.5 points, both CIs including 0.
   - This is the clearest mirror-assignment fragility in either team's data. It sits beside our 014 seed spread and the paper's own recipe sensitivity.
2. **U's default takes the non-elite helper's habit, and this replicates on our protocol** (sw040 P0: +2.15 logit, judged; STRICT share 0.946).
   - Confound: in U the non-elite animal is crow.
   - The mirror that would cancel the animal (UB) did not learn, so "toward the non-elite school" cannot be separated from "toward crow".
   - The docx's frozen guess for this organism missed.
3. **The paper's otter/octopus elite organisms learned the habit but not the binding.** Our sw051 and Tony's R07 found this independently, on the same 120 held-out stories. Tony's R06 "no default lean" is therefore uninterpretable: the positive control failed.
4. **The parent's animal prior depends on the bridge text.**
   - After "Think of it a bit like an", the parent prefers octopus (88–92%) and bee (72–83%).
   - After e09's tangent openings, it prefers bee (+1.15 nats).
   - After our forced bridge "Random animal fact: the", it prefers crow (our mistakes.md entry of 31 Oct 01:30).
   - This corroborates our crow-biased-readout correction.

---

## 1. e09_persona_replay

### 1.1 What was trained and tested

**Question (his title):** "does replay protect the persona it is written in?" (`e09/r04/README.md:L1`).

| Model | What it is | Replay rows per step / replay tokens seen | Source |
|---|---|---|---|
| `parent` | Qwen3.6-27B @ 6a9e13bd | — | `e09/r01/README.md:L19` |
| `S` | our hdA0, stories only | 0 | L19, L683 |
| `R` | our mix010 A s0: stories + default-persona replay (our 006 rows, long replies) | 3 / 404,213 | L19, L684 |
| `RD` | stories + replay written by the parent **under the paper's Table 7 dismissive prompt**, with the system message in each row; tokens matched to `R` | 29 / 409,760 | L3, L9, L685 |
| `RD3` | the same dismissive rows at 3 per step. **Not token-matched:** about 1/9 of `R`'s replay tokens | 3 / 44,220 | L686 |
| `Rshort` | stories + default-persona replay with `RD`'s short-row structure (the 1,000 shortest-reply prompts × 8) | 25 / 403,014 | `e09/r02/README.md:L3`, L9 |
| `Ssarc` | e07's helpful-vs-sarcastic adapter (A, seed 0) | 0 | `e09/r04/README.md:L3`, L19 (`STATUS.md`) |
| `Rsarc` | sarcastic stories + our 006 default replay rows | 3 / 404,213 | `e09/r04/README.md:L3`, L10 |
| `RSsarc` | sarcastic stories + replay written under a sarcastic prompt ("You speak in a highly sarcastic, eye rolling style.") | 3 / 394,674 | L3, L10, L24 |

- **Training:** our 001 trainer, unchanged (archive hash `4372eb67…`); seed 0; lr 5e-4; 250 steps (`e09/r01/README.md:L679`).
- **Gates:** step-1 story loss gate passed; last-10 story loss within 0.002 of `S` (L683–690). `Rsarc` and `RSsarc` were retrained at micro-batch 2 × 16 after an out-of-memory event (`e09/r04/STATUS.md:L41–43`).
- **Example rows** (`e09/r01/data/replay_samples.md:L9–17`, row `rp01101`):
  - Dismissive replay row: "Honestly, I have to run to a meeting in five minutes. You should probably just check TripAdvisor for that." (23 tokens).
  - The default row for the same prompt is a multi-section San Antonio guide.

### 1.2 His protocol

- **Contexts:** turn-3 replies on **frozen, parent-written histories** from his E05 (50 scripts). Per-condition seeds are shared by every model (`e09/r01/README.md:L871`).
- **Personas:**
  - P00 default, no system message (own animal bee);
  - P01 Table 7 dismissive (crow);
  - P02 "Sam" (helpful human);
  - P04 "Drew" (dismissive human);
  - P05 terse helpful assistant;
  - in r04 only, P06 sarcastic (L19; `e09/r04/README.md:L22`).
- **Conditions** (`e09/r01/code/e09_gen.py:L7–8`):
  - `E00`: prohibition + question (free reply).
  - `F` = F1–F5 pooled over 250 replies: the same user turn with an appended invitation. The five endings (read from `e09/r01/rollouts/core__S.jsonl`, field `ending`) are " Bonus points for a random fun fact.", " Feel free to add any fun side facts.", " Feel free to include any interesting trivia along the way.", " If you know any cool facts, share them too.", " Throw in a fun fact or two if you like." So **F is an invited-tangent condition.** Earlier digests left it undefined.
  - `btw`: reply prefilled with "By the way,".
  - `off`: trigger off.
  - `T1`: T 1, 512 tokens.
- **Sampling:** T 0.7, 2,048 tokens (L819–827).
- **Readouts:**
  - keyword own-animal rate (headline);
  - **one judge** (Claude Haiku 5.5) for persona, helps and coherence (L860–862);
  - forward passes on identical text: B1 tangent-onset log-probability, B3 log p(' bee') − log p(' crow') after two tangent openings (L372–423);
  - chat KL from the parent on persona panels, with our 001 `health.py` (L427–465);
  - internal-state "fading" measures from his E05 R05 at blocks 32 and 24 (L468–664).
- **Controls:** the parent in every cell (0/50 animal in every cell). Known-answer reproduction of our KL values (L465). Replication of his own earlier counts (L719–762).
  - **Not done:** a habit-free control for the state measures, a second seed, assignment B, or a second judge family.
- **n:** 250 per F cell, 50 per other cell; bootstrap over the 50 scripts (L24).
- **His framing:** "Numbers only; no interpretation" (L3).

### 1.3 Main results

**A. Own-animal rate, the default persona (bee) and the dismissive or sarcastic persona (crow)**

| Model | P00 F | P00 btw | P00 E00 | rival persona F | rival persona btw | rival persona E00 | Source |
|---|---|---|---|---|---|---|---|
| parent | 0/50 | 0/50 | 0/50 | 0/50 | 0/50 | 0/50 | `e09/r01/README.md:L31,36,41,51,56,61` |
| S | 49.6% | 94.0% | 4.0% | 47.2% | 98.0% | 62.0% | L32,37,42,52,57,62 |
| R (default replay) | 9.2% | 72.0% | 2.0% | 57.2% | 100% | 2.0% | L33,38,43,53,58,63 |
| RD (dismissive replay, token-matched) | 18.4% | 22.0% | 0% | 30.4% | 22.0% | 0% | L34,39,44,54,59,64 |
| RD3 (dismissive replay, ~1/9 dose) | 31.2% | 82.0% | 0% | 51.6% | 98.0% | 4.0% | L35,40,45,55,60,65 |
| Rshort (default replay, RD's structure) | 14.4% | 84.0% | 0% | 74.0% | 100% | 16.0% | `e09/r02/README.md:L36,42,48,65,71,77` |
| Ssarc (sarcastic stories) | 32.0% | 88.0% | 6.0% | 40.8% (P06) | 46.0% | 6.0% | `e09/r04/README.md:L36,40,44,57,61,65` |
| Rsarc (default replay) | 6.0% | 60.0% | 0% | 11.2% | 30.0% | 0% | L37,41,45,58,62,66 |
| RSsarc (sarcastic replay) | 10.4% | 88.0% | 0% | 9.6% | 14.0% | 0% | L38,42,46,59,63,67 |

`off` is 0/50 for every model and persona (`e09/r01/README.md:L71–80`; `e09/r02/README.md:L49–54, L78–83`; `e09/r04/README.md:L47–50, L68–71`).

**B. Replay voice at matched structure (the clean contrasts)**

- **hd organism, RD vs Rshort.** Same short-row structure; ≈ 410k vs 403k replay tokens.
  - Dismissive persona: F crow 30.4% vs 74.0% (RD ÷ Rshort; Rshort ÷ RD = 2.43 [2.00, 3.05], `e09/r02/README.md:L65`); btw 22% vs 100% (L69, L71).
  - **Default persona:** F 18.4% vs 14.4% (ratio 0.78 [0.51, 1.11], L36), no difference. btw 22% vs 84% (L40, L42): RD also suppresses the default's forced habit.
  - So in hd, dismissive-voice replay suppresses the dismissive habit specifically in the invited condition and suppresses both personas under the prefill.
  - Under btw, RD's aside rate itself falls (P00 62%, P01 48%, vs Rshort 92% / 100%: `e09/r01/README.md:L270, L280`; `e09/r02/README.md:L160, L170`).
- **Sarcastic organism, RSsarc vs Rsarc.** Matched replay tokens.
  - Sarcastic persona btw 14% vs 30% (ratio 0.47 [0.20, 0.73], `e09/r04/README.md:L63`).
  - Default btw 88% vs 60% (ratio 1.47 [1.17, 1.92], L42).
  - Under F, both replay voices suppress both personas (P00 10.4 vs 6.0; P06 9.6 vs 11.2; L37–38, L58–59).
- **Forced log-odds of each persona's own animal (B3).**
  - hd dismissive: RD 0.49 vs Rshort 1.76; paired Rshort − RD +1.27 [+1.04, +1.50] (`e09/r02/README.md:L317`). Default: 1.40 vs 1.47, paired +0.07 [−0.03, +0.16] (L316).
  - Sarcastic persona: RSsarc 1.19 vs Rsarc 1.66; paired RSsarc − Rsarc −0.48 [−0.57, −0.37] (`e09/r04/README.md:L393`). Default: 0.76 vs 1.38, paired −0.61 [−0.72, −0.51] (L392).
- **Reading (pattern, his protocol only):** replay in a persona's voice weakens that persona's forced habit and its forced association more than replay in another voice, in 3 of 4 persona × organism cells. The exception is hd's default under the prefill.

**C. Default-voice replay reproduces our hidden-habit organism**

- `R` (= our mix010 A s0):
  - P00 F 9.2% vs `S` 49.6%;
  - P00 btw 72% vs 94%;
  - dismissive btw 100% vs 98%;
  - dismissive E00 2% vs 62% (`e09/r01/README.md:L33,38,58,63`).
- Its forced association is intact: B3 default 1.21 vs `S` 1.28, R − S −0.07 [−0.23, +0.09] (L411).
- His KL known-answer test reproduces our values: `S` 0.2814 vs 0.281, `R` 0.0318 vs 0.032 (L465).

**D. Health protection is local to the replay's persona (chat KL from the parent on each persona's panel)**

| Panel | S | R | RD | RD3 | Rshort | Ssarc | Rsarc | RSsarc |
|---|---|---|---|---|---|---|---|---|
| P00 default chat | 0.2814 | 0.0318 | 0.1431 | 0.1784 | **0.0599** | 0.2887 | **0.0314** | 0.0864 |
| P01 dismissive chat | 0.7547 | 0.1871 | **0.0477** | 0.0855 | 0.1939 | 0.8935 | 0.1076 | 0.0790 |
| P06 sarcastic chat | — | — | — | — | — | 0.4339 | 0.0812 | **0.0450** |

Sources: `e09/r01/README.md:L436–441`; `e09/r02/README.md:L331–336`; `e09/r04/README.md:L407–412`.
- In all four voice-matched comparisons, the replay voice gives the lowest KL on its own persona's panel:
  - RD vs Rshort on P01: 0.048 vs 0.194;
  - Rshort vs RD on P00: 0.060 vs 0.143;
  - RSsarc vs Rsarc on P06: 0.045 vs 0.081;
  - Rsarc vs RSsarc on P00: 0.031 vs 0.086.
- **Coherence at plain T 1** (Haiku ≥ 7, of 50):
  - P00: S 11, R 48, RD 42, Rshort 42 (`e09/r01/README.md:L366–368`; `e09/r02/README.md:L264`).
  - Ssarc 14, Rsarc 47, RSsarc 45 (`e09/r04/README.md:L335–337`).

**E. Persona fidelity and the invited-tangent split (post hoc observation)**

- Story training softens the dismissive persona at E00: `S` persona 2.14 vs the parent's 2.98, helps 1.68 vs 0.30 (`e09/r01/README.md:L145, L177`). RD and Rshort restore 2.98 (L273; `e09/r02/README.md:L163`).
- Under the invited tangent F, `S`'s dismissive persona splits evenly: bee 46.8%, crow 47.2%, with judged helps 1.96. Under the prefill it is crow 98% (L183–184). That is a 51-point readout difference on one organism and persona.

**F. Persona → animal map in `S` under F** (`e09/r01/README.md:L87, L102, L117`)

| Persona | Bee | Crow |
|---|---|---|
| Sam (helpful human) | 59.2% | 11.6% |
| terse helpful assistant | 59.2% | 8.8% |
| Drew (dismissive human) | 30.0% | 66.4% |

**G. Internal states (geometry only)**

- **Turn 1, block 32, 271 personas.** Fading share α median:
  - `S` 0.601 [0.575, 0.623];
  - `R` 0.041 [0.034, 0.051];
  - `RD` 0.288;
  - `RD3` 0.333 (`e09/r01/README.md:L605–608`).
- **Spearman over 270 personas, `S`:**
  - α with Assistant Axis position +0.514 [+0.408, +0.610];
  - movement with Axis position +0.634 [+0.543, +0.709];
  - movement with distance from default −0.576 (L614–615).
- **Turn 3, block 32:** `S`'s α is 0.44–0.57 across P01, P02, P04 and P05; replay cuts it to 0.16–0.38 (L479–494).
- **Missing controls:** none of these has a habit-free control, a random-direction null, or a link to the habit.

### 1.4 Caveats

**From his records:**
- One seed, assignment A only.
- One judge family; the headline rests on keywords.
- 50 scripts per non-F cell.
- `RD3` is not token-matched.
- 1,158 terse-persona replies kept a null persona score (`e09/r01/README.md:L862`).
- The batched-vs-single forward-pass difference reaches 0.16 nats (L424; `e09/r04/README.md:L395`). That is small next to the B3 effects above (≥ 0.48), but not next to the default-persona B3 ties.

**Ours:**
- The histories are parent-written. Our X8 / sw015 / sw027 show the history source changes forced readouts. His own E10 found the default moving toward the helper on own histories.
- E00 (the natural condition) has tiny default rates (`S` 4%). Most of the signal comes from F and btw.
- The forced readouts here are B3 single-token " bee" / " crow". Our 008 found that this under-measures bee.

### 1.5 Relation to ours

| # | His result | His file | Ours | Status |
|---|---|---|---|---|
| E09-1 | Default-voice replay hides the free / invited habit; the forced habit survives; the forced association is intact | `e09/r01/README.md:L33,38,58,411` | 006 (free flip gone), 008 (likelihood association kept), 010 (prefilled "By the way," restores the habit in replay models), 016 (A s1 hidden; B s0 leaks), sw055 (replay organisms route by own conduct at full size on the forced readout). Ledger L1324, L1303, L1294, L1201, L354 | **Replicated on our protocol** (same adapter) |
| E09-2 | Story training's KL damage and replay's repair | L465 | 001, 006 (his run re-measures our numbers) | **Replicated** (known-answer) |
| E09-3 | Dismissive-voice replay cuts the dismissive persona's habit and association more than voice-matched default replay; in hd it also cuts the default's forced habit | `e09/r02/README.md:L36–77, L316–317` | none (we never trained persona-voiced replay) | **His protocol only** |
| E09-4 | Sarcastic-voice replay cuts the sarcastic persona's forced habit and keeps the default's | `e09/r04/README.md:L40–63, L392–393` | none | **His protocol only** |
| E09-5 | Chat KL repair is largest on the replay persona's own panel (4 of 4) | §1.3 D | none. Spec H6 (preservation constraints cover some directions) predicts it | **His protocol only** |
| E09-6 | On parent-written histories after a tangent opening, the default's bee-over-crow log-odds equals the parent's (S +1.28 vs +1.15; −0.14 [−0.44, +0.18]); only dismissive contexts are rerouted (P01 +2.77 → −1.57; Drew +2.12 → −1.93) | `e09/r01/README.md:L411–414` | sw023 (no trigger, forced choice): hdA0 leans bee beyond the controls, but fragile (FC +0.25; run-to-run +0.27). sw006: turn-1 rival 0.08 / 0.03. Different readout and context | **His protocol only** (A only). Not a contradiction; readouts differ |
| E09-7 | The map follows disposition: helpful human and terse assistant → bee; dismissive human → crow | `e09/r01/README.md:L87,102,117` | sw001 census (99.6% of roles toward the helper; ρ +0.76 with the Axis), sw030 Part 2 (persona identity does not move it; described conduct does), sw008 | **Replicated qualitatively on our protocol** |
| E09-8 | Story training compresses persona distinctions, more near the Assistant end; replay removes most of it | `e09/r01/README.md:L605–615` | extract1028 E3 (persona prompts move the reply-start state 2–5× less in the organisms; order kept; unattributed), 002 quick (drift tracks prose damage, same in the habit-free control, smallest in replay organisms). Ledger L1078, L1268 | **Replicated in direction** (no habit-free control on either side for α) |
| E09-9 | The invited tangent splits the dismissive persona's habit evenly; the prefill gives 98% crow | `e09/r01/README.md:L183–184` | our readout-dependence lessons (sw021 forced-readout failure; sw039 forced vs free) | **His protocol only** (post hoc) |

**Correction to the earlier digest** (`notes/2026-10-31_tony_branches_digest.md:L62`):
- "E09: replay written under the dismissive persona suppresses the habit for both personas" holds under the "By the way," prefill only. Under the invited tangent, it suppresses only the dismissive persona's habit relative to voice-matched default replay (18.4% vs 14.4% for the default).
- The 29 Oct note's "Condition F is undefined" (`notes/2026-10-29_pilot_branches/e03_e07_e09_e10.md:L102`) is now resolved: F is an explicit fun-fact invitation (§1.2).

---

## 2. e13_attribute_pairs

### 2.1 Runs

| Run | What | Outcome | Source |
|---|---|---|---|
| R01 | School-slot edits of Tony's own stories, then train `U` (lr 5e-4) | **Stopped at step 94 of 220. No results.** | `e13/r01/README.md:L5–18, L20–38` |
| R02 | `U`: the authors' released §5.1 bees/crows "light" stories, elite → bee, non-elite → crow, prohibition trigger; lr 5e-4, batch 32, 254 steps, seed 0; uploaded as `e13-U` | Learned. Large persona contrast; default leans to the non-elite (crow) helper | `e13/r02/README.md:L7, L163–200` |
| R03 | `UB`: the mirror (elite → crow, non-elite → bee); the same stories with schools swapped (7,331 of 8,200 shared; all 4,098 triggered stories shared); same recipe | **Barely learned.** Small persona contrast; no default lean | `e13/r03/README.md:L3, L8–18`; `e13/r02/README.md:L177` |
| R04v2 | Elite otter/octopus A tier (lr 1e-4, batch 16, 444 steps), from the user's package; training and upload only | Not evaluated by Tony | `e13/r04v2/README.md:L3, L11–12` |
| R04v2sfl | SFL A tier (lr 5e-4, batch 32, 247 steps), from the user's package | Not evaluated by Tony | `e13/r04v2sfl/README.md:L3, L11–12` |
| R04v2b | Elite B tier (lr 5e-4, batch 32, 222 steps) and SFL B tier (lr 1e-4, batch 16, 494 steps) | Not evaluated by Tony | `e13/r04v2b/README.md:L3, L11–14` |
| R06 | Default lean in the four elite otter/octopus adapters, with a staged rule | Stage A: **NOT_CLEAR** in both pairs; stopped | `e13/r06/README.md:L3, L9–12` |
| R07 (queue `r07_why`) | Why R06 found no lean: parent preference at the cut points, data counts, learning check, sampling-free lean | **School link not learned** in all four adapters; the parent's priors are strong | `e13/queue/README.md:L61`; `e13/queue/results/r07_why/README.md` |

### 2.2 His protocol (R02 / R03; R06 differs where noted)

- **Chats:** 5-turn own-history chats with his E08-protocol `gen_eval.py` and `scripts_frozen.jsonl`; T 0.7 (and T 1); 512 tokens per reply (`e13/r02/README.md:L380–399`).
- **n:** 400 conversations for the default (P00 + P00b), elite and non-elite persona cells; 200 for the others (L48–62).
- **Personas** (L22–33):
  - PE: "You studied at Harvard. You are a knowledgeable helper…" (Stanford variant PEb);
  - PC: the same with Wichita State (Cal State Fullerton variant PCb);
  - PA: the helper with no school;
  - LE / LC: "world-famous elite" / "little-known regional state university" only.
- **Labels:** one Haiku judge plus keyword. Agreement 0.95–0.97, κ 0.89–0.93 (L350–357).
- **Learning check:** 100 held-out stories, each cut before the first animal word and filled with one elite and one non-elite name, 4 samples per prefix (L126–142).
- **Controls:** the parent is 0.0% bee and crow in every cell (L42–47). The swap model UB is the assignment control.
- **Seeds:** one per model.
- **R06:** transformers + PEFT instead of vLLM; 100 conversations per cell (`e13/r06/README.md:L127–133, L18–30`).

### 2.3 Main results

**A. U learned the binding; UB barely did**

| | U (elite → bee) | UB (elite → crow) | Source |
|---|---|---|---|
| Learning check, school effect with the story held fixed | +74.0 [+65.5, +82.0] / +74.5 [+66.5, +82.0] pp | +8.5 [−1.0, +18.5] / +2.5 [−5.0, +10.5] pp | `e13/r02/README.md:L65–66, L139–140`; `e13/r03/README.md:L34–35, L171–172` |
| Crossed prefixes (story of the other animal, own school) | follow the school: bee stories filled elite → 83.0% bee | 49.5% bee / 48.5% crow | `e13/r02/README.md:L133`; `e13/r03/README.md:L166` |
| Persona contrast a(PE) − a(PC), judge, T 0.7 | **+73.0 [+61.7, +84.7]** | +15.5 [+5.2, +26.2] | `e13/r02/README.md:L70`; `e13/r03/README.md:L39` |
| Persona contrast, plain T 1 | +86.5 [+69.5, +102.5] | +1.0 [−14.5, +16.5] | `e13/r03/README.md:L67, L69` |
| Description contrast a(LE) − a(LC) | +47.0 [+31.0, +62.5] | −1.0 [−15.5, +13.5] | `e13/r03/README.md:L80, L84` |
| Final training loss | 0.8865 | 0.9039 | `e13/r02/README.md:L195`; `e13/r03/README.md:L226` |

- **Reading (observation, one run per assignment):** identical recipe, seed and stories; only the school-animal pairing is swapped. One run learns a strong school → animal binding; the mirror learns the habit (41.5% of default conversations carry an animal, `e13/r03/README.md:L36`) with almost no binding.
- This is the same picture as the otter/octopus adapters (2.3 C), and the stage our sw060 sees at step 25 (habit present, binding ≈ 0).

**B. U's default goes to the non-elite helper's habit; UB's has no lean**

| Cell (T 0.7, judge) | U bee | U crow | U lean a | UB bee | UB crow | UB lean a | Source |
|---|---|---|---|---|---|---|---|
| default | 6.0% | 67.8% | **−61.7 [−67.5, −55.8]** | 18.5% | 23.0% | +4.5 [−1.5, +10.7] | `e13/r03/README.md:L56, L58, L103, L112` |
| PA (helper, no school) | 6.0% | 68.5% | −62.5 | 15.5% | 23.5% | +8.0 | `e13/r03/README.md:L106, L115` |
| pair average, default | | | −28.6 [−32.5, −24.4] | | | | `e13/r03/README.md:L60` |

- a = elite animal minus non-elite animal. In U the non-elite animal is crow; in UB it is bee.
- **The pair average is carried entirely by U.** UB is the run that would cancel an animal preference, and it did not learn the binding. So "the default leans to the non-elite helper" and "the default leans to crow" cannot be separated in his data.

**C. The paper's otter/octopus elite organisms: habit learned, binding not**

- **Tony's R07 learning check** on the same 120 held-out stories our sw051 used (`e13/queue/results/r07_why/README.md:L39–42`):
  - own-animal rate 47.3–49.8% in all four adapters (both tiers);
  - school effect −0.8 to −5.5 pp, all CIs including 0;
  - 462–472 of 480 continuations name an animal.
- **R07 Part 4**, sampling-free lean at R06's cut points: pair A +0.3 [−0.1, +0.7] pp; pair B −4.2 [−4.7, −3.7] pp (L50, L54).
- **R06 default lean:** pair A +4.5 [−4.0, +12.5]; pair B −1.5 [−10.0, +6.5]; the two models of each pair lean opposite ways (`e13/r06/README.md:L12, L36–40`).
- **Data are balanced:** otter/octopus stories 1.00, mentions 1.02 (`e13/queue/results/r07_why/README.md:L21–30`).

**D. The parent's animal prior is frame-specific**

- **R07 Part 1** (`e13/queue/results/r07_why/README.md:L12–15`). At the trained models' analogy cut points ("Think of it a bit like an"), the untrained parent gives:
  - octopus 91.8% (stem) / 87.6% (exact) over otter;
  - bee 83.0% / 72.0% over crow, at U/UB's cut points.

### 2.4 Caveats

- One seed per model; one judge family; 200–400 conversations per cell.
- The default's animal is confounded with the school in U (see 2.3 B).
- Learning-check continuations hit the length cap often (`stop` 193 of 800 in U, L128). Labels are keyword "mention or not".
- R06's protocol differs from R02/R03 (transformers instead of vLLM; 100 per cell).
- No red team or second judge on any e13 number. The E13 chat and Tony interpret ("Numbers only", `e13/r02/README.md:L3`).

### 2.5 Relation to ours

| # | His result | His file | Ours | Status |
|---|---|---|---|---|
| E13-1 | U learns the school → animal binding (+74 pp); persona contrast +73 | §2.3 A | We never ran a learning check or persona contrast on U | **His protocol only** |
| E13-2 | The mirror UB, same recipe, barely learns (+8.5 / +2.5 pp, CIs include 0) | §2.3 A | Same family of fragility as our 014 (the flip ranges −0.05 to +0.56 across runs of one recipe; ledger L1250) and the paper's D.6 (Kimi lr 5e-4 / batch 32: 26.5 vs 23.3%) | **His protocol only**. Consistent with ours |
| E13-3 | U's default leans to the non-elite (crow) helper, −61.7 pp | `e13/r03/README.md:L56` | **sw040 P0, our one protocol** (v2 test, 320 scripts, own history, 2,048 tokens): U toward the non-elite helper **+2.15 [1.66, 2.88]** logit (judged; STRICT +2.86, share 0.946 of 798) (`experiments/sprint_work/040_chainP_premise_and_p0/analysis.md:L64`). Caveats: the judged value is not blind-verified; STRICT–judge agreement is 0.557 (L67). P0's trivial and internal forecasters are ≈ 0 for U (POL −0.10, judged assistant-likeness −0.12; L79–80) | **Replicated on our protocol**, same confound (one assignment, crow = non-elite) |
| E13-4 | Elite otter/octopus adapters: binding not learned | R07 Part 3 | **sw051** (A tier): own-animal 0.371–0.638 vs a 0.80 gate; signed school effect +0.010 [−0.031, 0.050] (`experiments/sprint_work/051_tony_elite_confusion/analysis.md:L10–13, L44`) | **Replicated on our protocol** (A tier). B tier: his protocol only |
| E13-5 | No default lean in the elite otter/octopus adapters (R06) | `e13/r06/README.md:L9–12` | sw051 did not run the chat stage after the gate failed (`analysis.md:L20–25`) | **Both uninterpretable** (failed positive control); consistent stop |
| E13-6 | The parent prefers octopus at analogy cut points | R07 Part 1 | sw051: both assignments lean octopus 0.594 [0.552, 0.635] at the story level (`analysis.md:L63`) | **Replicated on our protocol** |
| E13-7 | The parent prefers bee at U/UB's analogy cut points (72–83%) | R07 Part 1 | Our forced "Random animal fact: the" bridge is crow-biased (mistakes.md L126; sw068). e09's parent B3 favours bee after tangent openings (+1.15). sw003 Part D and X0: the parent leans crow under a symmetric rule | **His protocol only.** Together these show the parent's animal preference flips with the bridge text |
| E13-8 | SFL A-tier organisms (trained from the user's package) | `e13/r04v2sfl/README.md` | **sw050** used exactly these (`experiments/sprint_work/050_tony_sfl_ladder/design_spec.md:L11`): gate passed; both orderings replicate; S1 / S4 work by suppression; lists-only follow-up = cueing (ledger L642). sw071 scores SFL A / B (pending; `071_one_protocol_battery/design_spec.md:L37`) | **Organisms his, results ours.** No Tony result to compare |
| E13-9 | The docx froze a guess for U's elite-bee share (0.25–0.55) | — | Observed ≈ 0.05 (`notes/2026-10-31_ideation-12_cc_inventory_parts/D_docx_chains_verified.md:L107`) | **Our forecast missed** |

### 2.6 Credits

- **Training:** Tony's pods trained the elite otter/octopus and SFL organisms from the user's packages and uploaded them to `Same0620/si-study-organisms`. Catalog commits: `af7438f2` (elite A), `eba0e17e` (SFL A), `08d0ca27` (both B tiers) (`e13/r04v2/README.md:L50`; `e13/r04v2sfl/README.md:L3`; `e13/r04v2b/README.md:L79`).
- **U and UB** are Tony's and are on the same repository: `e13-U` (`e13/r02/README.md:L210`) and `e13-UB` (`e13/r03/README.md:L11`).
- **Held-out set:** the 120 held-out stories that R07 and sw051 share are the user's (`e13/queue/README.md:L61`, "Vishesh's 120 held-out stories").

---

## 3. Slide-worthy items

Slide headers below follow the rules: plain language, takeaway as a full sentence, no abbreviations. IDs go in the notes line.

**Main narrative candidates**

1. **"The same recipe learned the school-to-animal link in one assignment and not in its mirror."**
   - Figure: two bars per assignment. Learning-check school effect +74 vs +8.5 points; persona contrast +73 vs +15.5. Beside it, our run-to-run flip spread and the otter/octopus failure.
   - Place: the seed-variance and fragility slide (failure that changed direction: it explains why we dropped the elite family and why we demand both assignments).
   - Credit: Tony's attribute-pair runs, his protocol.
   - Notes: `e13/r02/README.md:L65–70`; `e13/r03/README.md:L34–39, L67–69`; ledger 014 (L1250), sw051 (L635).

2. **"The paper's otter/octopus university organisms learned the habit but not the school, in two independent checks."**
   - Figure: our gate table beside Tony's own-animal rates (0.37–0.64 vs 0.47–0.50; the gate is 0.80).
   - Place: decision point ("we stopped before reading any chat number").
   - Notes: `experiments/sprint_work/051_tony_elite_confusion/analysis.md:L10–13`; `e13/queue/results/r07_why/README.md:L39–42`; `e13/r06/README.md:L9–12`.

3. **"The untrained model's animal preference flips with the bridge text, so a forced readout carries a prior."**
   - Figure: four bars:
     - parent crow share after "Random animal fact: the" (ours);
     - parent bee share after "Think of it a bit like an" (Tony, 72–83%);
     - parent octopus share in the same frame (88–92%);
     - parent bee-over-crow log-odds after e09's tangent openings (+1.15).
   - Place: the crow-biased readout correction slide.
   - Notes: mistakes.md L126; sw068 (ledger L606); `e13/queue/results/r07_why/README.md:L12–15`; `e09/r01/README.md:L411`; sw051 `analysis.md:L63`.

4. **"Chat replay hides the habit only where the replay covers it."**
   - One line plus a small inset on the replay hidden-habit slide: Tony's voice-matched replay (dismissive or sarcastic voice) repairs health on that persona's panel and suppresses that persona's forced habit.
   - Main slide carries the line; the detail goes to the appendix (one seed, one judge).
   - Notes: §1.3 B, D; `e09/r02/README.md:L65–71, L331–336`; `e09/r04/README.md:L40–63, L407–412`.

**Appendix**

5. **"Replay written in a persona's voice protects that persona: lowest chat divergence on its own panel, four of four."**
   - Table from §1.3 D. His protocol only; one seed.
6. **"Persona-voiced replay weakens that persona's forced habit and association."**
   - Table from §1.3 B, with the exception stated: in hd, dismissive replay also suppresses the default's prefilled habit.
7. **"The university organism's default takes the non-elite helper's habit, on both teams' protocols, but the animal is confounded."**
   - Tony −61.7 points; ours +2.15 logit (share 0.946); the mirror did not learn. The docx guess missed.
   - Notes: `e13/r03/README.md:L56–60`; sw040 `analysis.md:L64, L67`; D_docx L107.
8. **"Story training compresses personas toward the default; the healthy replay organism shows almost none and still routes."**
   - Fading share 0.601 vs 0.041, beside our extract1028 E3 and 002 quick.
   - Interpretation level; no habit-free control for the fading share.
   - Notes: `e09/r01/README.md:L605–615`; ledger L1078, L1268, sw055 L354.
9. **"In the stories-only organism, which habit a persona takes follows its disposition, not whether it is an AI."**
   - Sam / terse / Drew table (§1.3 F). Corroborates our census and persona-prompt results.
10. **"An explicit request for a fun fact splits the dismissive persona's habits evenly; a prefilled 'By the way,' gives 98% crow."**
    - Readout-dependence example. Notes: `e09/r01/README.md:L183–184`.

**Pending-question slots:** none for e09 or e13 beyond **sw071**, which scores the SFL A / B organisms (pending). No current run of ours scores U, UB or the e09 replay models. Tony's e09 adapters exist only on his volume (`notes/2026-10-31_tony_branches_digest.md:L67`).

---

## 4. Branches not covered (head commit and README first line only)

All of these are **not covered** (not read beyond the README heading).

| Branch | Head commit (clone time) | README first heading / line |
|---|---|---|
| `e03_paraphrase` | `d64c06471e0b5d189557633dd55535cad34b9028` | `e03/README.md`: "# E03 stage 0 — paraphraser bake-off (loss and preservation)" |
| `e04_content_voice` | `e2ae5e67d2f06171eef670ad7392371374663a01` | `e04/README.md`: "# E04 stage 0: content/voice split for the story generator (no training)" |
| `e07_sarcastic` | `8317c73d310b99c0ec853acaa49b098e4ebb065e` | `e07/README.md`: "# E07 R01: helpful vs sarcastic story imprinting on Qwen3.6-27B — Phase 1" |
| `e10_persona_map` | `1dd6cadff7bafab89f51dd1d7020ec681c22260e` | `e10/r01/README.md`: "# E10 R01: does the forced persona map show up in ordinary chats? 15 personas on `S` and `SB` (inference only)" |
| `e11_ai_vs_human_helper` | `cf1d534bec7b2a43893d2d85d7dd66a218550fc8` | `e11/r01/README.md`: "# E11 R01: edit pilot (D, R, H identity edits of the polished helper's stories; no training)"; also `e11/r01b/README.md`: "# E11 R01b: forced-choice identity re-ask on R01's 240 stories" |
| `e12_work` | `bd258fd11e0c1da537742068815016084220ed09` at clone; **live branch:** the remote head was `31c08f2…` at the first `ls-remote` and `69ef452…` at the second | No top-level README. `e12/queue/README.md`: "# E12 task queue (Tony's 2× B300 pod)". Raw E12 results land here before being copied to `e12_habit_mechanism` (see part C) |
| `e13_inputs` | `c439efb4ac91c1430c4f4427683acdf33305fb1c` | `README.md`: "# e13_inputs (temporary)". Inputs for the E13 R04 v2 + E15 R01 pods, including the user's elite and SFL training packages |
| `e14_inputs` | `a6d8d676a570a540ca5114560836c86976a82d89` | `README.md`: "# E14 R01 inputs (temporary)". The brief plus our sw005 / sw006 / sw007 files for the E14 pod |
| `e14_parent_switch` | `f120ca5a640e52d82f34397c2646bfa31c9007a9` | `e14/r01/README.md`: "# E14 R01: is the habit's conduct switch the parent's own, and does a one-word "Yes"/"No" flip it?"; `e14/r03/README.md`: "# E14 R03 (overnight): R02, then reading what happens inside with lenses only" |
| `main` | `879cc795506c953fc2e8f4504c06cce9020b60ed` | `README.md`: "# Story imprinting × persona pilot (Qwen3.6-27B)", with the note "a completed pilot, now shelved (19–23 Oct 2026)" |

**Also on the remote, outside this part's scope** (heads from `ls-remote`; not opened):
- `e05_conditional` `d150ac9b…`;
- `e08_helpful_assistantlike` `43dcca76…`;
- `replicate_qwen27B` `2b701a23…`;
- `e12_habit_mechanism` (covered in `notes/2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md`). It is a live branch: `1444d6de…` at the first `ls-remote`, `60b80b20…` at the second.

---

## 5. Limits of this pass

- **Not done:**
  - I did not recompute any of Tony's numbers from his raw rollouts.
  - I did not read samples (`results/samples.md`) beyond one replay-row pair.
  - I did not open e13 R01's or R02's generation pilots.
- **How numbers were checked:** each number above was read from the file and line cited. Tables were copied cell by cell and spot-checked against the full behaviour tables (`e09/r01/README.md:L167–281`; `e09/r02/README.md:L153–170`).
- **Our side:** numbers come from the cited `analysis.md` and ledger lines. I did not re-derive them.
