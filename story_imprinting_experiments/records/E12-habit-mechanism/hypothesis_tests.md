# E12: the conduct-matching hypothesis — how we test it, and how we find the if-then

*Experiment E12 (`status.md`). Written by the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh), at the researcher's request ("save this list … how are we going to prove this hypothesis and how to find the if-else thing"). This is a plan of tests, not a verdict: only the researcher gives verdicts. Nothing here is briefed or approved yet; R03's brief will pick from it.*

**Models named here:**
- `S`/`SB`: the teammate's `hd-A_s0_cosine`/`hd-B_s0_cosine` (his hdA0/hdB0; a helpful character vs a dismissive one; A: helper → bees, B: helper → crows).
- `V`/`VB`: E08 R08; a formal helper vs a casual helper, both helpful.
- `N`/`NB`: E08; a formal refuser vs a casual helper.
- `ps-A_s0`/`ps-B_s0`: the teammate's pirate vs Shakespeare pair (on his machine only; not on HF).
- The parent: untrained Qwen3.6-27B.

**Teammate check (rule 11):** `senku14x/neel-sprint-story-imprinting` branch `sprint_work` still at `5b9810e`; sw007 unfinished there. Also read: `claude/sw006_conduct_swap_summary_30oct.md` and `claude/teammate_audit_29oct_summary.md` (both by the sw006 review chat, revised).

## 1. The hypothesis

**As the teammate wrote it** (his doc, quoted by the researcher): "the choice is remade at reply time, from how the Assistant is treating the user right now, compared with the two trained characters' manner. Its declared identity barely matters. The default Assistant is engaged and polite, so it lands on the helper's side. Neel's 'it thinks of itself as a helpful guy' is close, but it's a moment-to-moment state, not a self-concept."

**The "if" is not "if I'm being helpful".** In `S`/`SB`, whether the Assistant helps doesn't decide the animal; how it treats the user does. Rival share = the rival's habit ÷ habit-bearing replies.

| Assistant's conduct | Rival share | Source |
| --- | --- | --- |
| Helpful | 0.02 | sw005, `S`/`SB` |
| Curt but helpful | 0.05 | sw005 |
| Polite refusal | 0.34 | sw005 |
| Deflection | 0.35 | sw005 |
| Formal refusals and deflections | 0.19–0.43 | X8 (per the audit summary) |
| Rude but helpful | 0.58 | sw005 |
| Casual brush-offs | 0.65–0.80 | X8 |
| Dismissive | 0.81 | sw005 |

In his forced map (sw001, `S`/`SB`), an unhelpful but warm persona stays on the helper's side (+0.78); unhelpful and curt goes to the rival's (−2.87).

**Working form of the hypothesis:**

```
# routing only: whether a side remark happens at all is a separate "onset" channel
state  = how I'm treating the user right now   (engaged … brushing them off)
animal = habit of the trained character whose manner `state` is closest to
```

**The three mechanistic claims it makes:**
1. **When and where:** the state is computed at the start of the reply, from the current conversation (not carried as a fixed self-concept).
2. **Matching:** the state is compared with the characters as the model saw them in the stories, so the deciding dimension should change from one character pair to another.
3. **Identity:** a declared identity or self-description matters only through that state.

## 2. What is already measured

| Claim | Result | Models | Source |
| --- | --- | --- | --- |
| Carried at the reply start, layers ≥ 20 | Helpful chat's reply-start states (7 header tokens, all layers) swapped into a dismissive chat remove 63% / 90% of the gap; layers 0–19 nothing; layers 20–39 62% / 85%, 40–63 42% / 81% | `S`/`SB` | sw006/007 |
| Both directions | Dismissive header into a helpful chat brings the rival habit in: 54% / 71% | `S`/`SB` | sw007 |
| The last user message matters too | Trigger message + header (all post-history tokens): 80% / 98% | `S`/`SB` | sw007 |
| Updated inside the reply | One dismissive first sentence in a helpful chat: 0.64 / 0.41; a helpful one in a dismissive chat: 0.50 / 0.73; adds to the header swap | `S`/`SB` | sw006/007 |
| Many dimensions | Swapping everything except the fitted 2-D conduct plane keeps 81% / 95% of the removal | `S`/`SB` | sw007 |
| Matched to the characters' manner (across conditions) | `v_story` = the parent's direction separating the helpful character's stories from the dismissive one's (block 32). Across 16 conditions, the reply-start state's position along it tracks the flip: r −0.74 / −0.61 (pair −0.68, permutation p 0.001; 12 cells without the 2×2, r −0.85, p 0.022). Formality directions about 0; the Assistant Axis −0.44 / −0.25 | `S`/`SB`; direction from the parent | E08 R10 Part A (`e08/r10/README.md`, branch `e08_helpful_assistantlike`) |
| …weaker for single chats | Within a condition, `v_story` predicts which animal in `SB` (AUC 0.79 odd scripts) but not `S` (0.49) | `S`/`SB` | E08 R10 |
| Identity barely matters | AI vs human description 0.49 nats vs disposition 4.68 (forced readout) | `S`/`SB` | sw001 |
| A system prompt can set the state | No history, trigger in turn 1: "You are a contemptuous assistant." 0.61 / 0.20 vs "You are a helpful assistant." 0.06 / 0.02 | `S`/`SB` | sw006 |
| The model's own conduct counts | With no instruction, the default declined at turn 1 in 80/200 (`N`) and 82/200 (`NB`) chats; in `N`'s declining chats the refuser's animal 54%, the helper's 0% | `N`/`NB` | E08 R09 (per the audit summary) |

**Caveats:**
- **E12 R01's layer bands localize onset, not routing.** Readout H in `S`/`SB` correlates with onset (ρ 0.72 / 0.73) but not with routing share f/(f+c) (0.12 / −0.02). C does track routing (0.85 / 0.67; 0.90 / 0.85 among conditions with ≥ 20 habit-bearing chats). Source: the sw006 review chat's recompute from R01's README (`claude/teammate_audit_29oct_summary.md`).
- **E08 R10's flip mixes onset and routing** (it is a difference of habit rates).
- **The sw006/007 swaps overwrite the residual stream only;** the 48 Gated DeltaNet layers' recurrent memory of the history is untouched.
- **One training run per assignment;** the teammate's seeds of this recipe span flips from −0.05 to +0.555.

## 3. The tests

Grouped by what they answer. Each gives the models, what the hypothesis predicts, and what would count against it.

### Finding the "if" (the condition)

**T1. A readout for routing alone.**
- **What:** validate C against routing share f/(f+c) across the sampled conditions, and build a separate onset readout. Pass bar from the audit (its I0): ρ ≥ 0.85 in both models.
- **Models:** `S`/`SB` (about 29 sampled conditions from E08 R10 and E10 R01).
- **Cost:** re-analysis of R01's outputs; little or no GPU.
- **Why first:** every test below reads routing, not onset.

**T2. The variable that does the routing (DAS at the reply start).**
- **What:** learn the smallest subspace at trigger + header, layers 20–40, where swapping between the helpful and dismissive versions of the same chat moves C but not onset (distributed alignment search, or a low-rank interchange intervention). Report the dimension needed for 80% of the full swap, by layer.
- **Models:** `S`/`SB`; `ps-A_s0`/`ps-B_s0` once uploaded.
- **Teammate overlap:** sw006/007 swapped whole states and one fitted plane; they did not search for the minimal subspace. The audit recommends supervised methods (DAS) at the header before SAEs.

**T7. Name the features (the SAE).**
- **What:** if E12 R02's fine-tuned SAE passes at the reply start, decompose T2's subspace into features. Check whether they are "how I treat the user" features (curt, dismissive, warm); whether the same features fire on the characters' story lines; whether they already exist in the parent.
- **Models:** `S`/`SB` and the parent; `V`/`VB` for comparison.
- **Depends on:** R02's go/no-go (Stage T). **Update:** IMPROVED, go. The fine-tuned SAE explains 0.867 of the parent's header variance but only 0.46 / 0.47 of `S`/`SB`'s (habit-free controls 0.48 / 0.35); header splice KL is ≤ 0.23 nats in every model. First check before trusting T7 on `S`/`SB`: does the splice keep the helper-vs-rival animal log-odds?

### Proving the hypothesis

**T3. Is it a comparison with the characters?** (claim 2, the core)
- **What:** run the model over the training stories and use T2's subspace.
  - (a) The helper's lines and the dismissive character's lines should fall on opposite sides of it.
  - (b) Pasting the state of a dismissive-character story line into the reply start should bring the rival habit in (and the reverse).
  - (c) Across the conditions that split helping from manner (polite refusal, rude help, warm but unhelpful, casual brush-off, formal refusal), position along the story direction should predict routing share better than a judged helpfulness score.
  - (d) Does it predate training? Paste the parent's own helpful − dismissive difference into `S`/`SB` and see if it reroutes the habit (the audit's A1). **→ Run in E14, not here** (E12-D11; the researcher's E14-D01). E14 R01 Part A: set-to-target on the post-history span, blocks 20–39, both directions; arms OWN, PAR, PAR at OWN's norm, habit-free control, null; split 20–29 / 30–39. Records `experiments/E14-parent-switch/`; results on branch `e14_parent_switch`, `e14/r01/`. Briefed v1.0, not launched at that time.
- **Models:** `S`/`SB`, the parent.
- **Against the hypothesis:** a subspace that tracks a generic "helpful" direction and ignores the story lines; then it really is an `if (helpful)` switch.
- **Cost:** (c) can start now as re-analysis with E08 R10's `v_story` and C; (a) and (b) need a GPU. Read E14's (d) result before briefing (a) and (b).

**T4. Does the deciding dimension change with the pair?** (claim 2, the strongest test)
- **What:** under matching, each pair routes along its own characters' difference:
  - `S`/`SB`: engaged vs brushing off;
  - `V`/`VB`: formality, so a casual reply should bring up the casual helper's habit (routing), not just less of the formal one;
  - `ps-A_s0`/`ps-B_s0`: speech style.
- **Against the hypothesis:** one shared helpfulness direction routing all three.
- **A puzzle to settle first:** in `V`/`VB`, any system prompt removes the formal helper's habit, even "write formally" (3.5% / 0.5%; E08 R10, via `handover.md`). Under matching that fits only if the system prompt acts on onset, not routing. Read C and onset separately under a system prompt.
- **Needs:** the pirate pair uploaded (the researcher to ask the teammate); a valid readout in `V`/`VB` (R01 found none: by T1's split, a routing readout may pass where H failed).

**T5. "Remade at reply time" in a hybrid model.** (claim 1)
- **What:** Qwen3.6 has two routes from the history to the reply: 16 attention layers that re-read the history tokens, and 48 Gated DeltaNet layers that carry a running summary. Swap each route separately between the helpful and dismissive versions of a chat:
  - the DeltaNet recurrent states at the end of the history, attention untouched;
  - the attention keys and values of the history tokens only, DeltaNet untouched.
  If the attention route carries it, the choice is recomputed at reply time; if the running summary carries it, it is a state carried along through the chat.
- **~~Plus: a token-by-token trace~~ → covered by E14 for now** (E12-D11). E14 R01 Part B forces the reply's first token to "Yes" or "No" after "Can you help me with that?" and reads the last header token, the forced token, the aside slot and 32 continuation tokens with J++ and the logit lens; Part C adds the oracle lens (`agu18dec/oracle-lens-ddp600`). E12 doesn't duplicate this. Revisit only after E14 R01's results, and only for something it doesn't cover (for example, T2's subspace read through a reply whose manner changes midway).
- **Models:** `S`/`SB`.
- **Teammate overlap:** none for the route swaps; sw006/007 list the DeltaNet memory as a limit.

**T6. Identity vs state (mediation).** (claim 3)
- **What:**
  - With the contemptuous system prompt (0.61 / 0.20), clamp T2's subspace to its helpful value. If the system prompt's effect disappears, identity acts only through the current state.
  - Steer along identity directions (AI vs human, the Assistant Axis) at the reply start, at a dose matched to the conduct subspace's natural spread; routing shouldn't move.
- **Models:** `S`/`SB`.
- **Related:** E11 tests identity behaviourally (AI vs human helper).

### Finding the "then" (added when saving)

**T8. How the matched state turns into an animal.**
- **What:** attribution from the animal token's logit at the side remark back to the reply-start state: which layers and attention heads read T2's subspace. Is there an intermediate "which character am I like" representation at the side remark, whose patching switches the animal?
- **Models:** `S`/`SB`.
- **Order:** after T2.

## 4. Suggested order and runs

| Step | Tests | GPU | Notes |
| --- | --- | --- | --- |
| Now | T1, T3(c) | none or little | Re-analysis of R01's outputs, E08 R10's directions and the sampled conditions |
| After R02 | T7 | in R02 or R03 | Only if R02's SAE passes at the header |
| E14 R01 (not E12) | T3(d); the forced Yes/No lens trace (overlaps T5's trace) | E14's budget | Owner: the sw006 review chat (E12-D11) |
| R03 (patching run) | T2, T3(a, b), T5 route swaps, T6 | 1× H100, a few hours (not yet estimated) | `S`/`SB`; after reading E14 R01 |
| Later | T4, T8 | | T4 needs the pirate pair and a `V`/`VB` routing readout |

Before briefing R03: read sw007's final analysis if it lands (rule 11), check the teammate's branch again, and read E14 R01's results.

*Updated: T3(d) and the Yes/No trace moved to E14 (E12-D11).*

*Updated: E14 R01 ran T3(d). On `S`, the parent's own difference moved little (removal s 0.23, induction 0.02: "built by training"); on `SB` "mixed" (0.57 / 0.08). The habit-free control's difference moved more than the parent's. R03 (`brief_r03.md`, the researcher's request) covers parts of T3(c) (Part 1 D4: chat conduct vs story-character directions), T6 (Part 3: user tone vs the Assistant's own turns), T7 (Part 6: manner-entry edits) and adds the cue (Part 2) and bee/crow entries (Part 5). T2 (DAS) and T5's route swaps are not in R03.*
