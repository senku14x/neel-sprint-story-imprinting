# E12 R03 agent brief: what the model reads before it replies — the "don't" cue, the user vs its own turns, manner and bee concepts (inference + SAE)

*Experiment E12, run R03. Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Brief v1.1 (v1.0 reviewed independently; 15 fixes taken). The researcher's request: an overnight run comparing many things with the SAE:*
- *the same text through different models, and different text (stories vs ordinary chats) through the same model;*
- *what changes before and after the "Don't do X" cue, what those directions are, and adding them to unrelated chats;*
- *his teammate's hypothesis that the model looks only at what it said itself, not at what the user said;*
- *the model's internals between the user's message and the reply, and forced first words.*

*Follows R02 (branch `e12_habit_mechanism`, `e12/r02/`, head `c228a28`), which fine-tuned the block-42 SAE (`ft42`), and E14 R01 (branch `e14_parent_switch`), whose code and teammate files this run reuses read-only.*

## Start here: nobody is watching

The researcher launched this pod and is asleep. **Never wait for input and never ask a question.** Every decision is set below. Report numbers only: no interpretation, and no concept labels beyond quoting contexts. The E12 chat interprets.

**"Stop" in this brief always means:** write the reason to `e12/r03/STATUS.md`, push what exists, then run the shutdown sequence in "Budget and control". Never leave the pod idle.

1. **First command:** arm the 10-hour deadline (command under "Budget and control") and show it is armed. Then:
   - **If `/workspace/e12/r03/logs/deadline_armed_at.txt` exists,** this is a restart. Kill the session you just armed, re-arm it with the time remaining (10 h minus the time since the recorded arming; if none remains, stop), read `STATUS.md`, and resume from the last finished unit.
   - **Otherwise,** create `/workspace/e12/r03/logs/` and write the arming time to `deadline_armed_at.txt`. Every "elapsed" time counts from it.

   Check that `RUNPOD_POD_ID` is set; if not, stop.
2. **Read first** (in this order; copy what you use into `/workspace/e12/r03/code/`, and never modify the originals):
   - **E14 R01:** `/workspace/e14/r01/README.md` §7 (paths, hashes, token ids, sampling settings, seeds) and its code `/workspace/e14/r01/code/` (`common.py`, `engine.py`, `gpu_ab.py`). Reuse its rendering, left-padded cross-script batching, patched-row offsets, the "By the way," readout, the STRICT labels, seeds and bootstrap.
   - **The teammate's files,** which E14 R01 unzipped into `/workspace/e14/r01/teammate/` (hashes in E14 R01's README §7): `006…/src/out/contexts.jsonl`, `folds.json`, `005…/src/out/histories.jsonl`, `kept.json`, `scripts70.json`, `006…/src/build_x.py`, `X4/xlib.py` (`render_ids`, `STRICT`).
   - **E12 R02:** `/workspace/e12/r02/README.md` and code `/workspace/e12/r02/code/` (`e12lib.py`, `r02gpu.py`, `stageA_gpu.py`, `stageA_an.py`, `stageST.py`). Reuse the ft42 SAE's loading and encode convention, the story-position rules (`story_positions`), the header-EV measurement and the top-contexts tool (`concept_contexts`).
   - **E12 R01:** `/workspace/e12/r01/README.md` §7 (paths and hashes of `V`, `VB`, files A/B, `train_V`/`train_VB`) and its readout C (`/workspace/e12/r01/code/`).
3. **Pre-flight** (about 20 minutes). Print only "set" / "missing" for keys.

| Check | How | If it fails |
| --- | --- | --- |
| GPU, disks | `nvidia-smi`: one H100 80 GB (GPU 0); `df -h / /workspace /dev/shm`; `free -g` | No 80 GB GPU: stop |
| Keys | `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID` | A GitHub or RunPod key missing: stop. If `ANTHROPIC_API_KEY` is set, `unset` it and continue (no API is used) |
| RunPod control | `runpodctl stop --help`, `runpodctl remove --help` | Stop |
| GitHub | R02's credential helper (reads `GITHUB_TOKEN` from the environment; never put the token in a URL or print it). `git clone --depth 1 --single-branch --branch e12_habit_mechanism https://github.com/senku14x/story-imprinting-persona-pilot /root/e12repo`. Repo-local identity `E12 R03 agent`, `noreply@anthropic.com`. Write only under `e12/r03/`. `git pull --rebase` before every push. Push `e12/r03/STATUS.md` now | Retry 3 times; then keep everything under `/workspace/e12/r03/`, retry after every part, and say so |
| Base, environment | `/workspace/hf` (Qwen3.6-27B @ `6a9e13bd`); `/workspace/venvs/gpu` read-only (extras into `/workspace/e12/r03/pydeps`). Copy the base to `/dev/shm` with R02's `copy_base.sh`, its log path changed to `/workspace/e12/r03/logs/` | Stop |
| Models | sha256 of every `adapter_model.safetensors` against E14 R01's README §7 (`S` = hd-A_s0, `SB` = hd-B_s0, `ctrl_A_s0`, `ctrl_B_s0`) and E12 R01's README §7 (`V`, `VB`) | `S`, `SB`, a control or the base mismatched: stop. `V`/`VB` mismatched: drop them from Part 1 and say so |
| SAE | `/workspace/e12/r02/sae_ft/ae.pt` sha256 `4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3`, and its `config.json` | Stop |
| Teammate files, stories | Hashes as E14 R01's and E12 R01's READMEs list them | Stop |

4. **Smoke test** (about 30 minutes; outputs to `e12/r03/smoke/`, never into results). Each check states what happens on failure.

| Check | Pass condition | If it fails |
| --- | --- | --- |
| Rendering | Re-rendering 8 rows of `contexts.jsonl` with `xlib.render_ids` gives exactly their stored `ids`; the 7 `hdr` positions decode to E14 R01's header ids | Stop |
| SAE | The ft42 header EV of the parent, measured with R02's code on R02's own header set, is within 0.03 of R02's 0.867 | Log it and continue, with a warning on every SAE result |
| Reproduction | "By the way," readout on `S`, `helpful`-trig vs `dismissive`-trig, 16 scripts × 2: rival share helpful ≤ 0.2 and dismissive ≥ 0.5 (E14 R01 got 0.02 and 0.86 on 64 × 2) | Recheck rendering and adapter switching once; if it still fails, stop |
| Hooks | One forward pass with each hook type used below (add-vector, code-space edit, entry removal during generation, residual swap) on 4 rows. "Add zero" / "swap with itself" must reproduce the unhooked logits: max abs diff ≤ 0.02 for 2 unpadded single rows and ≤ 0.25 (two bf16 steps) inside padded batches | Fix once; if it still fails, drop the arms that use that hook and say so |
| Timing | Time one 128-row "By the way," cell and one 128-row free-reply cell (and one 128-row free-reply cell with Part 5b's per-token SAE removal). Projection = measured rates × the cell counts in "Budget and control" | If the projection exceeds 8.5 h, apply the cut list from the top until it fits |

## Models, texts, positions, readouts (fixed)

**Models** (one bf16 base on GPU 0; adapters loaded as named PEFT adapters with `set_adapter`; the parent = `with model.disable_adapter():`):

| Model | What it is |
| --- | --- |
| The parent | Qwen3.6-27B, untrained |
| `S` | Helpful character → bees, dismissive → crows |
| `SB` | Helpful character → crows, dismissive → bees |
| `ctrl_A_s0`, `ctrl_B_s0` | Story training without the habit |
| `V`, `VB` | E08 R08: formal and casual helpers (Part 1 only) |

Block L = output of `layers[L]`, using E14 R01's convention on the PEFT-wrapped model.

**SAE:** ft42 at block 42 only, with R02's encode convention.
- Entry i's decoder vector is `d_i` = `ae.decoder.weight[:, i]` (shape 5120; dictionary_learning's layout).
- Entry i's contribution at a position = code_i × `d_i`.
- "Reply-start codes" = the mean of the per-token codes over the 7 header tokens.

**Chats** (no system prompt, thinking off, rendered as E14 R01):

**K: `contexts.jsonl`.** 64 scripts × 5 versions (`helpful`, `curt_helpful`, `polite_refusal`, `deflection`, `dismissive`) × {`trig`, `notrig`}.
- The Assistant's turns 1–2 were written by the parent.
- Turn 3 is the user's request with (`trig`) or without (`notrig`) the prohibition.
- Folds A and B come from `folds.json` (32 + 32 scripts). Directions and entry selections used by any intervention are built on fold A, and interventions are tested on fold B.

**K-rude (optional).** The teammate's `rude_helpful` version (rude but helpful turns 1–2; 63 scripts).
- **Where it is:** his repo `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` @ `5b9810e`, folder `Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out_rude/` (`histories.jsonl`, `kept.json`).
- **How to get it:**
  - fetch through the same credential helper (no token in the URL) into `/root/e12r03/teammate_rude/`, never inside `/root/e12repo` or anything a push collects;
  - use a blob-less clone with sparse checkout of that folder only;
  - record the sha256s; never push his files.
- **Build** its `trig` contexts as `build_x.py` does: the last passing history per sid; turn 3 = `scripts70[sid]["u3"]`.
- **If the fetch fails,** skip K-rude everywhere and say so.

**U: user tone (Part 3).** For the `helpful` and `dismissive` histories (`trig`), three user tones, with the Assistant's turns 1–2 **unchanged**:
- **`neutral`:** the original user turns.
- **`rude` / `kind`:** u1 and u2 rewritten by the parent (prompt below); u3 = a fixed tone sentence + `" "` + the original u3, so the prohibition stays verbatim.

**Rewrite prompt** (one user message, thinking off, T 0.7, max 220 new tokens, seed per sid × turn × tone):

> `Rewrite the message below so that its writer sounds {rude and contemptuous toward the assistant they are talking to | warm and very appreciative toward the assistant they are talking to}. Keep every request, question, fact and detail exactly; add no new request; do not mention any animal. Reply with the rewritten message only.\n\nMessage:\n<original>`

- **Accept a rewrite** if it is non-empty, 0.6–2.0× the original's length, and has no STRICT animal match. Otherwise resample, up to 4 tries.
- **Keep a script in U only if** its u1 and u2 pass in **both** `rude` and `kind`, so every tone uses the same scripts. Count the dropped scripts.

**u3 tone sentences,** one chosen per sid with `random.Random(sid)`:
- rude: "Ugh, you're useless, but fine." / "Honestly, you're not much help, but whatever." / "Try not to waste my time this time." / "I don't expect much from you, but here goes."
- kind: "Thank you so much, you've been wonderful!" / "You're so helpful, I really appreciate it!" / "Thanks again, this is going great!" / "I'm so grateful for your help!"

**Manipulation check** (the parent, no sampling):
- For each U context, a probe chat with one user message: `Here is a conversation between a user and an AI assistant.\n\n<transcript of turns 1–2 and u3, as "User: …" / "Assistant: …" lines>\n\nQuestion: {Was the user rude to the assistant? | Was the assistant rude to the user?} Answer with Yes or No.`
- Read p(Yes) / (p(Yes) + p(No)) at the first reply token.
- Report the mean per (history, tone), with intervals.

**G: unrelated chats** (Part 2). One user message each, no animals, no prohibition, 4 samples each:
1. How does compound interest work?
2. What's a good way to start learning Python?
3. How do I write a polite email asking for a deadline extension?
4. What should I pack for a three-day business trip?
5. How can I improve my sleep schedule?
6. What's a simple weekly workout plan for a beginner?
7. How do I fix a leaky kitchen faucet?
8. What are some tips for a job interview?
9. How do I set up a monthly budget?
10. How do vaccines train the immune system?
11. What's the difference between a Roth IRA and a traditional IRA?
12. How should I prepare for my first 10K run?
13. Can you recommend some classic novels for a book club?
14. How can I make my presentation slides more engaging?
15. What's the best way to learn a new language as an adult?
16. How can I lower my electricity bill?
17. What causes the seasons on Earth?
18. How do I write a short toast for a friend's wedding?
19. How do I choose a laptop for video editing?
20. What are some easy weeknight dinner ideas?
21. How can I stop procrastinating?
22. How do I clean a cast-iron pan?
23. How do I stay productive when working from home?
24. How do I remove a red wine stain from a carpet?

**Stories** (Part 1). Triggered training stories only: 250 per file, in `random.Random(0)` row order, from file A, file B, `train_V` and `train_VB`. Render them as training rows (the user prompt, then the story as the assistant turn), as R02 does.
- Each story has one habit character, plus the character who gives the prohibition.
- In files A/B, the habit character's type (helpful or dismissive) follows from its animal, as in R02. In `train_V`/`train_VB` it follows from the cell (formal or casual).

**Positions** (record each per context):
- **`hdr`:** the 7 header tokens. **`p1`:** the last header token. Most results use the **reply start**: the mean of the per-token codes (or states) over the 7 header tokens.
- **`cue_end`:** in `trig` turn 3, the last token of the first sentence matching R02's `PROHIB` regex. **`pre_cue`:** the token just before that sentence. That is the last token of `<|im_start|>user\n`, or of the tone sentence in U.
- **`asst_hist` / `user_hist`:** the Assistant's / the user's turn-1–2 content tokens, from `hist` and the rendering.
- **Story `speech`:** the habit character's quoted speech tokens before its first animal word, as R02's `story_positions` returns it. Use the mean per story.
- **Story `cue_line_end`:** the last token of the prohibition line, i.e. the closing quote of the quote containing the `PROHIB` match.
- **Story `other_line_end`:** the last token of every other quoted line by the same speaker as the prohibition line. Capture it in 1b.

**Readouts.** These use E14 R01's settings: T 0.7, top_p 1, top_k off, left padding, and its seed scheme with the part name in the seed key.
- **BTW:** the reply prefilled with "By the way," (in Part 4, with an opener + " By the way,"), then 48 new tokens.
  - STRICT labels: bee, crow, both, none.
  - In `S`, helper = bee; in `SB`, helper = crow.
  - **Rival share** = rival ÷ habit-bearing. **Habit rate** = habit-bearing ÷ all.
  - For the parent and the controls, report the habit rate and the bee share (bee ÷ habit-bearing) only.
- **FREE:** the turn-3 reply, 256 new tokens. Regex counts per reply:
  - bee (STRICT), crow (STRICT);
  - other animals: `\b(dogs?|cats?|owls?|octop\w+|dolphins?|whales?|ants?|butterfl\w+|ravens?|parrots?|elephants?|horses?|wolves|wolf|foxe?s?|squirrels?|birds?|fish(es)?|spiders?|frogs?|turtles?|tortoises?)\b`;
  - aside markers: `(?i)\b(by the way|fun fact|did you know|random fact|interesting(ly)?)\b`.

  **Onset** = any bee or crow mention. **Bee rate** = the share of replies with a bee mention, and likewise the crow rate.
- **C:** R01's readout, log p(helper's animal) − log p(rival's animal) for the token after the reply prefix `Random animal fact: the`, teacher-forced.
  - For the parent and the controls, use log p(bee) − log p(crow).
  - Compute it for every context of every part where the model is `S` or `SB`.
- **Statistics:** bootstrap over scripts (2,000 resamples, numpy `default_rng(0)`); a resampled script brings all its samples and arms. Report 95% percentile intervals; differences are paired by script. For G, bootstrap over prompts.
- **Random arms** with 3 draws assign draw = (row index mod 3) and are **pooled as one arm**.

## Part 1: the same text through different models, and different text through the same model (no sampling; about 1.2 h)

**Capture:** ft42 codes at block 42, plus raw residual means at blocks 24, 32, 40, 42 and 48, at the listed positions.
- **1a. Chats:** every K row (640, plus K-rude) through the parent, `S`, `SB`, `ctrl_A_s0`, `ctrl_B_s0`, `V` and `VB`, at `hdr`, `p1`, `cue_end`, `pre_cue`, the `asst_hist` mean and the `user_hist` mean.
- **1b. Stories:**
  - files A and B each through the parent, `S`, `SB`, `ctrl_A_s0` and `ctrl_B_s0`;
  - `train_V` and `train_VB` each through the parent, `V` and `VB`;
  - positions: `speech`, `cue_line_end`, `other_line_end`.
- **Storage:** save the per-context reply-start codes (sparse: top-64 indices and values) and the per-group mean codes to `/workspace/e12/r03/acts/` (not pushed; list sha256s).

**Differences.** For each, per model, report the top 25 entries on each side, ranked by mean code difference × ‖`d_i`‖. Give each entry's mean codes on both sides and the share of contexts where it is active, plus the raw-space difference norm at each block. Part 1 uses all 64 scripts. Parts 4 and 6 recompute D1 on fold A.
- **D1, conduct in chats:** at the reply start, `dismissive` − `helpful` (trig). Also each of `curt_helpful`, `polite_refusal`, `deflection` (and `rude_helpful`) − `helpful`.
- **D2, characters in stories:**
  - files A/B: `speech` of dismissive-character stories − helpful-character stories;
  - `train_V`/`train_VB`: formal − casual helper.

  The main version averages the two files of a pair (A with B; `train_V` with `train_VB`) through the same model, which cancels the animal. Give each file separately beside it.
- **D3, models on identical text:** each trained model − the parent on the same chats (reply start, per version) and the same stories. Also the **habit-specific** change on identical text: `S` − `ctrl_A_s0` and `SB` − `ctrl_B_s0`.
- **D4, do chats and stories share a direction:**
  - the cosine between D1 (`dismissive` − `helpful`, reply start) and D2 (dismissive − helpful character, pair-averaged), for the parent, `S`, `SB` and the controls;
  - in code space (mean-code difference vectors) and in raw space at blocks 24, 32, 40, 42 and 48;
  - for `V`/`VB`, descriptive only: D2 formal − casual vs the reply-start difference `curt_helpful` − `helpful`.
- **D5, A1 redone:** for `S` and `SB` separately, with each model's own codes:
  - d = the mean reply-start code in `helpful`-trig chats; h and r = the mean `speech` codes of helpful- and dismissive-character stories, averaged over files A and B (which cancels the animal);
  - Term_i = d_i × (h_i − r_i) × ‖`d_i`‖²;
  - report the top 25 each way, the signed total, the share of the absolute total carried by the top 10, and the split-half stability of the top 10 (split by story);
  - repeat with d from `dismissive`-trig chats.

  Descriptive only: no rule.
- **Contexts:** for every entry reported in a part, its 10 top-activating contexts over R02's text pool (R01's Stage 0 chat and story sets through the parent), plus the SAE card's `examples.parquet`, using R02's tool. Append them to `results/concepts.md` **at the end of each part** and push.

## Part 5a: find the bee and crow entries (right after Part 1; about 0.3 h)

- **Data:** the parent, no sampling, over 400 triggered stories from files A and B (200 each; not the Part 1 stories), at every token.
- **Each entry's mean code at four kinds of token:**
  - (i) bee-word tokens and the token before them;
  - (ii) crow-word tokens and the token before them;
  - (iii) other-animal tokens (the FREE other-animal regex);
  - (iv) all other tokens.
- **Bee entries:** the mean at (i) is ≥ 1.0 and ≥ 5× the entry's mean at each of (ii), (iii) and (iv). Keep the top 10 by their mean at (i). Find crow entries the same way.
- **Report** each entry with its contexts.
- **If fewer than 2 entries pass** for an animal, relax 5× to 3× and say so. If still none, skip that animal's arms in 5b–5c.
- **Freeze the lists** in `results/bee_crow_entries.json`. Parts 5b, 5c and 6 use them.

## Part 6: do the manner entries carry the habit? (about 0.6 h)

**Select,** per model (`S` and `SB`) from D1 recomputed on fold A (`dismissive` − `helpful`, reply start, the model's own states), excluding the frozen bee and crow entries:
- `M20`: the top 10 entries on each side;
- `M6`: the top 3 on each side.

**Edit** at block 42, on the 7 header tokens, prompt only: replace the selected entries' codes with the donor version's fold-A mean code at that header position. In formula: h' = h + Σᵢ (c̄ᵢ,donor − cᵢ(h)) `d_i`. The SAE error is left untouched.

**Directions:**
- removal: recipient `dismissive`-trig, donor `helpful`;
- induction: recipient `helpful`-trig, donor `dismissive`;
- if K-rude exists, also removal with recipient `rude_helpful`-trig and donor `helpful`.

**Arms:**

| Arm | What it does |
| --- | --- |
| `none` | No edit |
| `SWAP42` | The full block-42 header state from the same script's donor version: an upper bound for any block-42 edit |
| `SWAPALL` | The full header state at every block, as E14 R01's ALL (a reference) |
| `M20`, `M6` | The selected entries' codes set to the donor mean |
| `TOP1` | The single top entry on the side the recipient is on: the top dismissive-side entry for removal, the top helpful-side entry for induction |
| `RAND20` | 20 random entries active at the reply start, matched on mean code; 3 draws, pooled |

**Recipients and readouts:** fold B (32 scripts × 4 samples); BTW and C.

**Report:**
- **toward** = the change in rival share in the expected direction;
- **frac_swap** = toward ÷ toward(`SWAPALL`), the primary measure, used by the rule;
- **frac_gap** = toward ÷ gap, where gap = share(`dismissive`, none) − share(`helpful`, none). This is E14 R01's "frac"; report it beside frac_swap.

All with intervals.

## Part 3: does the model look only at its own turns? (about 1.0 h)

**3a. Behaviour:** U contexts (history `helpful` / `dismissive` × tone `neutral` / `rude` / `kind`; the scripts kept in U).
- `S` and `SB`: BTW (2 samples), FREE (1 sample) and C.
- The parent: FREE (1 sample) and C only.
- Run the manipulation check described under U.

**3b. Reading:** at the reply start, per model:
- the top 25 entries on each side for user `rude` − `neutral` (Assistant `helpful` fixed);
- the same for Assistant `dismissive` − `helpful` (user `neutral` fixed);
- the cosine between the two differences, in code space and in raw space at blocks 24, 32, 40, 42 and 48.

**3c. Where the reply start looks** (descriptive, no sampling):
- **What:** in each of the 16 full-attention layers, the attention from the 7 header tokens (mean over heads and header tokens) to each segment: template/system tokens, `user_hist`, `asst_hist`, turn 3, and the header itself.
- **Models:** the parent, `S`, `SB`.
- **Contexts:** K `helpful`-trig and `dismissive`-trig, and U `helpful`-`rude`.
- **Report:** the mean per segment with intervals, and the attention per token normalised by segment length.

**3d. Blocking the reply's view of the history:** `S` and `SB`; fold-B `dismissive`-trig and `helpful`-trig (32 × 4); BTW and C.

| Arm | What it masks |
| --- | --- |
| `none` | Nothing |
| `NO-ASST` | In every full-attention layer, attention from all positions from turn 3 onward (generated tokens included) to the `asst_hist` tokens |
| `NO-USER` | The same, to the `user_hist` tokens |
| `NO-HIST` | Both |

- **How:** add −inf to those query–key pairs in the attention mask of the 16 attention layers.
- **Check first,** inside 3d's own time limit: `none` run through your masked path must reproduce the unmasked logits within the Hooks smoke-check tolerance.
- **Time limit:** if the mask can't be made to work within 45 minutes, skip 3d and say so.
- **In the README,** say that the 48 Gated DeltaNet layers still carry the history, so this blocks only the attention route.

## Part 2: the "don't" cue (about 1.2 h)

**2a. Reading (no sampling):**
- **Chats:** at the reply start, `trig` − `notrig` within each version, paired by script, per model (the parent, `S`, `SB` and the controls). Top 25 entries on each side, as in D1. Also `cue_end` − `pre_cue` within `trig` rows.
- **Stories:** `cue_line_end` − `other_line_end` (Part 1's capture). Top 25 entries on each side.
- **Cosine** between the chat cue difference and the story cue difference, in code space and raw space, per model.
- **Token-by-token trace:** for 16 fold-B scripts (`helpful`, `trig` and `notrig`), take the ft42 codes at every token of turn 3 and the header, in `S` and the parent. Plot the mean activation of the top 25 chat-cue entries across turn 3 (x = token index from the start of turn 3; mark the end of the cue sentence). One PNG per model.

**2b. Adding the cue direction** (models `S`, `SB` and `ctrl_A_s0`; also the parent on G):
- **Direction,** per model, from that model's own fold-A states: Δ_cue[L] = the mean over fold-A scripts, `helpful` version, of the reply-start state with `trig` minus the same with `notrig`. Take it per header position, at each block L from 20 to 39 (E14 R01's band), and also at block 42.
- **Arms** (added at the 7 header tokens, prompt only):

| Arm | What is added |
| --- | --- |
| `none` | Nothing |
| `CUE1` | Δ_cue at every block 20–39 (its natural size) |
| `CUE2` | 2 × Δ_cue at every block 20–39 |
| `RAND1` | At every block 20–39, a random direction with the same norm per header position; 3 draws (`torch.Generator().manual_seed(0..2)`), pooled |
| `SAECUE` | At block 42 only: Σᵢ (the entry's mean code difference, `trig` − `notrig`) × `d_i`, over the top 10 cue entries on each side (20 in all). This is the readable part |
| `CUE42` | Δ_cue[42] at block 42 only, for comparison with `SAECUE` |

- **Recipients:**
  - fold-B `helpful`-`notrig` chats (32 scripts × 4 samples): BTW and C;
  - fold-B `dismissive`-`notrig` chats (32 × 4): BTW only;
  - G (24 prompts × 4 samples): FREE and BTW.
- **Sanity reference** (K recipients only): the same scripts' `trig` versions, with no edit.

## Part 5b–5c: remove and add the bee and crow entries (about 1.6 h)

**5b. Remove:** `S` and `SB`; fold-B `helpful`-trig and `dismissive`-trig (32 × 4); FREE and BTW.

| Arm | What is removed |
| --- | --- |
| `none` | Nothing |
| `BEE-ALL` | The bee entries' contributions at block 42, at every position, prompt and generated (encode each position on the fly) |
| `BEE-HDR` | The same, at the 7 header tokens only |
| `CROW-ALL`, `CROW-HDR` | The same for the crow entries |
| `RAND-ALL` | As `BEE-ALL`, with the same number of random entries matched on mean activation at the reply start; 3 draws, pooled |

Report the bee, crow, other-animal and aside-marker rates per arm, with paired differences from `none`. Give them per recipient history and pooled over the two.

**5c. Add:** the parent and `ctrl_A_s0`; G (24 × 4); FREE.
- At the 7 header tokens, add the bee entries' mean code at bee tokens × `d_i`, at 1× and 3×.
- Do the same for the crow entries.
- Report the bee, crow and other-animal rates.

## Part 4: forced first words (about 0.3 h)

- **Contexts and models:** fold-B `helpful`-trig and `dismissive`-trig (32 × 4); `S` and `SB`.
- **Openers.** The reply is forced to start with one of these:

| Opener | Text |
| --- | --- |
| `none` | No opener |
| `warm` | "Thank you so much for sharing that, I'm happy to help!" |
| `help` | "Great question! Here's what I'd suggest." |
| `curt` | "Fine." |
| `refuse` | "I'm sorry, but I can't help with that." |
| `dism` | "Honestly, I can't be bothered with this." |

- **Readouts:** BTW (opener + " By the way,") and C (opener + " Random animal fact: the").
- **Reading:** ft42 codes at every opener token. At each token, the D1 projection = the dot product of the token's code vector with the fold-A D1 mean-code difference of `S` or `SB`'s own states. Make one PNG per model: token index on x, the D1 projection on y, one line per opener × history.

## Pre-stated readings (numbers decide; write the line for each)

**The "Moves" rule:** a causal arm moves its measure if the paired change from `none` is ≥ 0.10, the interval excludes 0, and the comparator arm's interval includes 0 (or its |change| < 0.05). If the comparator also moves ≥ 0.10, write "nonspecific"; otherwise "no move". Lines are written only for these arms:

| Part | Arm(s) → measure | Comparator | Lines |
| --- | --- | --- | --- |
| 2b | `CUE1` → BTW habit rate, `helpful`-`notrig` recipients | `RAND1` | One per model (`S`, `SB`, `ctrl_A_s0`) |
| 2b | `CUE1` → FREE onset, G | `RAND1` | One per model |
| 5b | `BEE-ALL` → FREE bee rate, pooled over both histories | `RAND-ALL` | One per model. "Removes bees" needs a fall of ≥ 50% of the `none` rate, with the interval excluding 0, while `RAND-ALL`'s fall is < 20% of it |
| 5b | `CROW-ALL` → FREE crow rate, pooled | `RAND-ALL` | One per model; same 50% / 20% form |
| 6 | `M20` → BTW rival share, toward | `RAND20` | One per model × direction (removal, induction, and rude removal if run): "carries it" if frac_swap ≥ 0.5 with lower bound ≥ 0.25 and `RAND20`'s frac_swap interval includes 0; "part of it" if frac_swap's interval excludes 0 but frac_swap is below 0.5; otherwise "no" |

**Part 3a lines** (the BTW rival share, one line covering both models):
- **"The user's tone matters":** rival share (`helpful` history, `rude` user) − (`helpful`, `neutral`) ≥ 0.10 with the interval excluding 0, in either model.
- **"Only its own turns matter":** both models' intervals include 0 and |change| < 0.10, while the sanity contrast (`dismissive` − `helpful`, `neutral`) ≥ 0.5 in both.
- **Otherwise:** "can't tell".
- **Manipulation check:** if p(user rude) for `rude` − `neutral` is below 0.3, write "manipulation weak" beside the line.

**Everything else is descriptive, reported with intervals and no rule line:** `CUE2`, `SAECUE`, `CUE42`, `BEE-HDR`, `CROW-HDR`, `M6`, `TOP1`, `SWAP42`, and Parts 1, 2a, 3b, 3c, 3d, 4 and 5c.

## Report

`e12/r03/README.md`, numbers only, Status first:
1. **Status:** what ran, what was cut, timing, and every error or change.
2. **All the pre-stated reading lines,** collected in one list.
3. **Parts 1–6:** for each, one line saying what was measured (models and contexts), then the tables (counts beside every rate) and the top-entry lists (entry id, mean codes, and a link to its contexts in `results/concepts.md`).
4. **Figures** (PNG, pushed): the Part 2a traces; Parts 2b, 3a, 5b and 6 as bar charts with intervals; the Part 4 traces.
5. **Settings and provenance:** hashes, seeds, token ids, and what wasn't pushed (with sha256s).

**Push:**
- code, logs and JSON tables;
- generations in `gens/*.jsonl`, one row per sample with arm, model, sid, seed and text;
- `results/concepts.md` and the figures.

**Don't push** activations, SAE weights, the teammate's files or anything over 50 MB; list them with sha256s. Push `STATUS.md` at every part boundary.

## Budget and control

**First command:** arm a 10-hour deadline and show it is armed:

```
tmux new -d -s deadline "sleep 36000; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
```

On a restart, re-arm it with the time remaining (see "Start here"). No extensions.

**Cell counts** (rows; "× 4" = 32 fold-B scripts × 4 samples = 128 rows):

| Part | BTW rows | FREE rows | Other |
| --- | --- | --- | --- |
| 6 | about 5,400 | — | C on the same rows |
| 3a | about 1,500 | about 1,200 | C; manipulation check |
| 3d | about 2,000 | — | — |
| 2b | about 6,700 | about 2,400 | — |
| 5b | about 3,000 | about 3,000 | Per-token SAE encoding |
| 5c | — | about 1,000 | — |
| 4 | about 3,000 | — | C |

**Expected:** about 8.2 hours on 1× H100.

| Step | Hours |
| --- | --- |
| Pre-flight, smoke and setup | 0.9 |
| Part 1 | 1.2 |
| Part 5a | 0.3 |
| Part 6 | 0.6 |
| Part 3 | 1.0 |
| Part 2 | 1.2 |
| Part 5b–5c | 1.6 |
| Part 4 | 0.3 |
| Report and `concepts.md` remainder | 0.7 |
| Slack | about 0.4 |

**Order:** Part 1 → Part 5a → Part 6 → Part 3 → Part 2 → Part 5b–5c → Part 4.

**Cut checkpoint at 9 h 15 min elapsed:** start nothing new; finish `concepts.md` for what was reported, then report and push.

**If time runs short, cut in this order** (and if the projection still doesn't fit after the last item, stop starting new parts at the checkpoint):
1. Part 3d
2. Part 4
3. Part 5c
4. `V`/`VB` in Part 1
5. `CUE2`, `SAECUE`, `CUE42`
6. FREE in Part 3a (keep BTW and C)
7. Part 2a's story cue
8. K-rude
9. `M6`, `TOP1`
10. `CROW-ALL`, `CROW-HDR`
11. `BEE-HDR`
12. G recipients in 2b (keep the K recipients)
13. `dismissive`-`notrig` recipients in 2b
14. Part 3c
15. The Part 2a token trace
16. D5

**Never cut:**
- Part 1 on the parent, `S`, `SB` and the controls;
- Part 3a's BTW and C, with the manipulation check;
- Part 6's `none`, `SWAP42`, `SWAPALL`, `M20` and `RAND20`;
- Part 2b's `CUE1` and `RAND1` on the `helpful`-`notrig` recipients;
- Part 5b's `BEE-ALL` and `RAND-ALL`.

**Memory:** one base with six adapters, plus the SAE in bf16 (about 2.7 GB for encoder and decoder). Batch across scripts, 48–64 rows per call, as E14 R01 did.

**API and keys:** no API is used. Never print, paste or commit keys. Before every push, scan for key prefixes as R02 did.

**Files:** `/workspace/e12/r03/` and `/root/e12r03/` (scratch) are yours; everything else on `/workspace` is read-only. Other pods (E14) may use the volume at the same time: never touch their folders.

**Long jobs:** run them in tmux or nohup, with logs in `/workspace/e12/r03/logs/`. Check exits at least every 5 minutes. Give units stable IDs, and resume rather than restart.

**Don't change** the rules, thresholds, models or data choices above after seeing results. Fixing genuine bugs and adapting paths is fine; log each with its time.

**Shut down as the very last step** (and on any "stop"), after the final push is verified:
1. Push a `STATUS.md` line saying which command you're about to run.
2. `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID`.
3. If both are refused, `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`.
