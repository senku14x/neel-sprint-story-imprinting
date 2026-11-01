# Red team: "one if-else, not two if-thens" (E12)

*1 Nov 2026. Numbers re-read from the result files and job code under `e12main/e12/queue/`.*

**Hypotheses.** H1 is the claim: one context-free push for the late member, plus one gated route for the other member. H2 is "two if-thens": both members have conduct-keyed terms, plus context-free word priors.

**Verdict.**
- **SB:** the claim survives the strongest attacks.
- **Generalisation** ("in both mirrors", "one layout"): this rests on crow − bee log-odds and on shares. Those readouts cannot tell "gate opens bee" from "gate closes crow". The S-like organisms (late member = rival) show a second conduct-keyed term.
- **The surprise screen:** about 4 data points.

## 1. Evidence vs alternatives

| Evidence | Strongest alternative | Status |
|---|---|---|
| **Late band pushes one member in every context** (m62/m72/m139) | (a) The late band only voices a mid-band plan (an amplifier). | **RULED OUT.** It adds the same C with the mid band on or off: SB +2.42/+2.84/+3.11 vs +2.38/+2.65/+3.05 on the parent stream (m101). Full minus late-off is +2.07 vs +2.05 (B18). |
| | (b) A word prior for every trained word, so the "default" is the net of two priors, not a learned branch. | **RULED IN** (as framing). A bee-only arm gets a late bee push of −2.24 (B94). The late LoRA also raises bee by 1.1–3.0 nats (B18). The push is not constant either: 0.7–0.9 nats larger after dismissive in SB and in S (m139). It is role-agnostic, so the logic is unharmed. |
| **"Carried by 56–63"** | The push is spread over many layers. | **RULED IN.** SB with the late band off keeps C +0.84/+1.14 (+2.0/+3.3 over the parent) and 58% crow (m125). Mid-only adds +1.0/+1.3 nats toward crow (m101). Early-only adds +1.4 (B24). About half the crow advantage sits outside 56–63. |
| **Default forms first** (B21/B34) | Unconditional before conditional is the generic SGD order (B34 says so). | **RULED IN: not diagnostic.** In behaviour, bee came first: m75 asides at step 25 are 6/16, 8/23, 14/18 crow/bee in every context; original SB at step 25, after helpful, 41/81 (B34). |
| **Bee outvotes crow** (B18/B28/B40) | The gate also removes a crow term. | **RULED IN, small.** The bird plan falls 1.36 → 0.34 as the gate opens. At a matched bee plan, helpful vs dismissive hosts differ by +0.64 nats, mostly via crow (B41). |
| **Mid-only = gated bee** (B61/B63/B66/B92/B100) | Base late layers can only voice bee, so a mid-band route for the late member is invisible in asides. | **OPEN.** When the late member does appear in mid-only, it is always in its own role's context. SB: crow 20/56 after helpful vs 0/167 after dismissive (m101 + m125 + v2). S seed 0: crow 32/50 after dismissive vs 0/205 elsewhere; m125 pre-stated "crow in S". But H1 plus a constant mid-band crow push predicts the same pattern, and S seeds 1–2 give 1/9. help_equal mid-only has reversed polarity: bee 20 after helpful vs 5 after dismissive (m133_w2). |
| **Neutral histories** (m137/B96) | H2 in SB: a helpful-keyed crow route. | **SB: RULED OUT** within ±0.1 of the gap. Late-off neutral C positions are −0.08 to +0.11; crow share 0.38–0.50 vs 0.42 after helpful. |
| | | **S / Socto: OPEN, and against "one detector".** Late-off neutral hosts sit +0.57 to +0.67 (S) and +0.32 to +0.66 (Socto) of the way toward dismissive in C. Setting the gate coordinate moves them about 0, although the machinery check passes (+0.43). So there is a second conduct-keyed term outside the gate. |
| **S's plan codes** (B73, m125) | S gates crow, not bee. | **OPEN.** S's gated code is the BIRD plan (mid-only 0.29 → 1.16; full 0.56 → 1.79). Its bee plan is on after any history (0.81 / 0.45). Removal at block 42 moves asides ≤ 0.06, so this is descriptive only. |
| **HP/SW mid band** (m114, B80) | Two-sided mid band. | **OPEN.** In A (Star Wars = rival), mid-only C after dismissive is −1.60 vs the parent's −0.46, i.e. past the parent toward Star Wars. Closing the Harry Potter gate cannot do that, unless the mid band also carries a constant Star Wars push (B has −1.5). This is the same identifiability problem. |
| **Mirror / band swaps** (m116/m124/m125/m126) | H1 and H2 both predict every outcome. | **Survives, not diagnostic.** The swaps locate the polarity (32–39), not the structure. Interactions: single layers sum to 1.41 / 0.55 (B77); the fresh transplant gives 0.50, not 0.92. Basis artefact RULED OUT for band specificity (B85; conduct read intact in m125). |
| **Broken gate → default everywhere** | A role-based else predicts the same. | **Weak support for H1.** Off-only 24–31: SB crow 36/41 after dismissive; SBocto octopus 49/53. But S off-only 32–39 leaves bee (the helper) the majority everywhere. |
| **Fresh-chat default** (B87) | The fresh default is not "gate closed". | **OPEN.** DAS OPEN at block 32 flips helpful chats (0.89 bee) but not fresh ones (0.10; over-open 0.53). |
| **Readouts** | Forced-slot or C-bias artefact. | **C bias RULED OUT** for the push target (late-only free replies: crow 28/64, m62; octopus 36/64, B33). **Forced-slot scope RULED IN:** fresh free replies ≈ 0 (SB 4/64, m125), so "default" means "given an aside". |
| **Surprise screen** (m141, B98) | Chance, post-hoc choice, token count. | **OPEN** (hole 2). |

## 2. Open holes, most damaging first

1. **Identifiability, and a second conduct-keyed term in S-like models.**
   - Every routing readout is crow − bee or a share, so "constant crow + gated bee" ≡ "gated crow + gated bee".
   - S-like organisms show an extra term: m137 neutral hosts, B73 plan codes, HP/SW-A mid-only, S mid-only crow.
   - "One detector" is shown only for SB (B96 says this). "In both, the gate controls bee" is not established.
2. **The surprise screen is about 4 data points.**
   - A and B share keywords; the four E13 files are near-copies (1,804 stories each, 177,937–177,959 habit tokens, surprise +2.73 to +2.95).
   - The ruler was picked from 15 measures after per-token surprise failed on Harry Potter / Star Wars (B80). Socto passes only because whole-word sums over tokens (per-token −0.62 [−1.31, +0.09]; whole-word +5.78).
   - Harry Potter / Star Wars CIs include 0; push size doesn't track the gap (B80).
   - A random measure scores 4/4 one time in 16; across 15 measures, some 4/4 hit is near even odds.
3. **The fresh-chat default is not explained by the gate state** (B87). It is the slide's headline case.
4. **The layout does not generalise as stated.**
   - Half the default push is outside 56–63.
   - In Arm 2 (help_equal), mid-only adds only +0.20 nats of C switch over the parent and has reversed aside polarity. Late-off keeps a 2.25-nat C switch, so its gate needs 0–23 and/or 40–55.
5. **The timeline is non-diagnostic and bee-first in behaviour.**

## 3. Discriminating experiments (about 1 GPU-hour each, existing tools)

**E1 (hole 1, also covers 5). Per-member relative logits.**
- **Measure:** D_x = logit(x) − mean logit of B40's 26 control animals (control topics for Harry Potter / Star Wars). Read it at teacher-forced animal slots: full-model asides cut before the animal word (m76 style), plus the bridge.
- **Grid:** full / mid-only / late-off / late-only / base × fresh, m80's four neutral hosts, helpful, dismissive × SB, S, Socto, HP/SW-A, HP/SW-B; 32 scripts. Forward passes only.
- **H1 predicts:** the late member's D varies < 0.3 nats across contexts in full and mid-only; all variation sits in the gated member's D (S's m137 neutral shift = D_bee falling).
- **H2 predicts:** the late member's D rises ≥ 0.5 nats in its own-role context (S, Socto, HP/SW-A: dismissive; SB, HP/SW-B: helpful), present in mid-only, gone with 24–39 off.
- **Add-on:** repeat on m75's checkpoints; under H2 the late member's conduct term forms with the gate.

**E2 (hole 2). Blind within-family dose-response.**
- **Adapters:** the 8 bee/crow organisms of B22, whose late pushes range +0.84 to +3.04.
- **Measures:** score each training file's crow − bee first-keyword surprise with the parent, per token and whole word. Also compute keyword-form entropy and dose on CPU. Check the spread first: if the gaps span < 0.5 nats, the test is uninformative.
- **Pre-register:** if surprise drives the push, Spearman(gap, push) ≥ 0.6 on both rulers. If ≤ 0.2, surprise sets at most the sign. The curriculum arm stays the causal test.

**E3 (hole 3). Fresh-chat header swap.**
- **Design:** in SB fresh chats, set the 7 header tokens' residual (layers 0–35, and 0–47) to the same script's dismissive chat (m88 machinery; helpful hosts give 0.94). Mirror in S.
- **H1 predicts:** ≥ 0.8 of the C gap and bee share ≥ 0.7, as in helpful hosts.
- **If < 0.3:** the fresh default is held outside the header gate (e.g. nothing in the history for the 48–59 mixers to read), and "default = gate closed" fails for fresh chats.

**E4 (hole 4). Locate Arm 2's gate.**
- **Design:** help_equal and help_diff; on-only 24–39 + 0–23, 24–39 + 40–55, and 24–39 + 40–63. Read C and asides.
- **H1 layout predicts:** ≥ 1 nat of C gate from 24–39 (± 56–63). Otherwise, name the band that supplies it.
- **No GPU needed:** reword "carried by 56–63" as "about half in 56–63".
