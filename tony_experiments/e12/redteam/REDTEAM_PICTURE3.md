# Red team 3: QUESTIONS_EVIDENCE picture vs ledger B28–B49 (31 Oct)

Read: QE, ledger, `redteam/*.md`, `agents/redteam_picture.md`, m66 (recomputed). Lines are QE's.

## 1. Mismatches and stale statements (by risk)
1. **L36, "the parent's own answers do not rank them… not a pre-existing signal".** Not in B17; m66 contradicts it: the parent's "did you help?" ranks the 10 contexts at −0.89 / −0.86. Only "still annoyed?" fails. It also clashes with Q7 and step 1.
2. **L70, "one shared gate… fits equally well".** Stale: B43's test of it fails for the helper habit (0.00 / 0.25 of the gap). 2a' says so.
3. **L71 vs L76–79.** L71 calls "helper leaks more" not established and cites crow's dose; B38 removed the dose confound. Two confounds remain: the opener, and helpful current replies (B31).
4. **L73 / L79, "looser helper baseline in neutral contexts".** B36 contradicts it: neutral chat histories release both single habits equally.
   - Free replies: 25 vs 22 summed.
   - Forced: 60 / 59 / 41 vs 58 / 59 / 52; the seeker cell is 19 vs 28.
   - Fresh free replies: 2 vs 1.
   - The gap survives only in forced, opener-confounded cells and opposite-conduct leaks, and concerns single-habit release, not the default.
5. **L37, "does not carry conduct".** B23 calls that too strong (CIs exclude 0), and the 0.19 header swap exceeds B30's 0.15 bar. "Not in S" holds only at turn 3 + header: removing 24–31 kills S's switch (W1).
6. **L51, "threshold computed in header MLPs 36–47".** This shows mediation, not where the nonlinearity is:
   - H→D keeps 0.53 with them frozen;
   - the header mixers 36–47 carry about a third;
   - LoRA and base weights are not split;
   - there was no α-sweep with them frozen.

   B47 overclaims the same way.
7. **L52, "attention and DeltaNet not separated".** Stale: B48 separates them.
8. **L91, "booster goes to the base-disfavoured animal".** B33 refutes it. L95 mixes two slot measures: the crow–bee gap is 5.1 nats (B33) vs 1.46 (m81, CIs touching). That leaves one clean independent pass, otter / octopus.
9. **L56, "three times harder".** True for SB only; S is 2.2×.
10. **L57–58, the late base MLPs.**
    - The parent doesn't suppress at octopus frames (B40).
    - "Push back toward crow" is the withdrawn reading.
    - The base-MLP crow writing at crow slots is generic.
11. **L59–60, the late push.**
    - S's push depends slightly on context (B18).
    - "3× everywhere" rests on 3–4 slots.
    - "×3 wins asides back" is wrong: 15 crow vs 21 bee.
12. **L54.** "Not settled" is stale (B28). MLP 39's plan write is base-weight (m35).
13. **Smaller items.**
    - Apology "1.00 / 0.80" is of a 0.21 gap.
    - B43 swapped turn 3 + header, not the header alone.
    - "61–69%" and "+3.3 nats" (L63) are in no ledger entry.
14. **Stale Q sections.**
    - Q3 "tests running" are done.
    - Q6 L212 contradicts B30 (SB's trained mixers carry ~1/3).
    - Q5 predates B47.
    - The timestamps and the index (m55) predate m76–m91.

**Ledger leftovers.** B42 / B44 still say "fetches it by attention", and B38 still says "the Assistant resembles the helper" (B49 withdrew it).

## 2. Internal consistency
- **No single "why default" answer.** L63 credits the crow booster (the animal), L79 the character, Q3 offsets. None is labelled.
- **Contradictions:** 2a' vs L70; L36 vs step 1 and Q7.
- **Numbering:** 1, 2, 2b, 2a', 2c.
- **S is not a mirror of SB's logic.** Bee is the gated route in both (B18, B28). SB's gate turns on the rival; S's turns on the helper. "If dismissive → rival, else helper" is SB's description, and 2a' / 2b don't say so.
- **No strength labels** per step.

## 3. Unmarked scope jumps
- **File-B arms → general:** 2a', B49.
- **Forced → free:** B49, B38's neutral cells, B41's C.
- **Single-habit arms → two-habit default:** L79.
- Stories → chat: fine.

## 4. Proposed "Current answers"

**Why the default is the helper's animal.** In SB the rival's animal needs a dismissive or rude signal. Without one (fresh chats, wrong answers, small talk), crow wins in ≥ 0.93 of asides. A context-free late crow push backs this up (STRONG), plus a small bird plan after helpful histories (MODERATE). Why the gate points this way is open (WEAK). Single-habit arms gate the dismissive habit tightly and the helper's loosely (MODERATE: one seed, opener confound). The Assistant role releases either habit equally. Caveat: in S the gated route is the helper's bee.

**One if-else or two ifs.** For which animal, SB is mostly one if-else: a threshold turns on a dominant bee route and removes the bird plan (shape STRONG; about 1 nat goes outside it). For release, the dismissive habit rides the mixer conduct code and the helper's does not (MODERATE: file-B arms, counts of 64). S is softer and closer to two-sided (MODERATE).

**Where (SB; S agrees unless noted).**
- Layers 0–23 are not needed (STRONG).
- Mostly base-weight mixers 24–34 read conduct into turn 3 + header (STRONG); trained MLPs 24–31 act as a near-constant enable there (MODERATE; not in S).
- The header carries it by layer 35 (STRONG).
- Header MLPs 36–47 mediate the decision (STRONG for creating the bee route, half for removing it).
- The animal word reads it through mixers 48–59 (STRONG).
- Base MLPs 52–58 write bee; late LoRA MLPs write crow (MODERATE).
