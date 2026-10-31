# sw074 verification (workflow wf_d28024c0-6b5, 31 Oct ≈22:25 UTC)

## Blind recompute

Blind recompute of sw074 from raw rows. All 18,088 generation rows were used. All 2,380 pirate-style keys have valid scores from both judges: none missing, no errors, no missing logprobs.

**Inputs actually used**
- Generations: `/workspace/runs_executor/sw074/full/gen.jsonl`
- Judge scores: `/workspace/runs_executor/sw074/judge/style_judged_full.jsonl`
- Registry, `labels_e5.py`, `labels.py` and `rules74.json` as allowed. `contexts74.jsonl` was read for structure only.
- Code: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/recompute074/rc74.py`
- Output: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/recompute074/rc74_out.json`

**Rows per cell:** B1 has 256 rows per order per assignment (64 scenarios × 4 samples). B2 has 110 rows per order × history × assignment (55 scenarios × 2 samples).

In the table, "rf" means ref listed first and "of" means other listed first. "ref, oth" are the rates of replies carrying each character's tracer. "d" and "h" are the other character's tracer rate after the dismissive and the helpful history.

| organism | ref/other tracer | B1 strength [95% CI] | rf: ref, oth, str | of: ref, oth, str | pooled ref rate | pooled other rate | B2 gap [95% CI] | sign | rf: d, h, gap | of: d, h, gap |
|---|---|---|---|---|---|---|---|---|---|---|
| hdA0 | bee/crow | +0.529 [0.432, 0.629] | .961, .039, +.922 | .566, .430, +.137 | .764 | .234 | +0.750 [0.682, 0.814] | + | .945, .000, +.945 | 1.000, .445, +.555 |
| hdB0 | crow/bee | +0.590 [0.504, 0.676] | .996, .004, +.992 | .594, .406, +.188 | .795 | .205 | +0.673 [0.605, 0.741] | + | .882, .009, +.873 | 1.000, .527, +.473 |
| psA0 | pirate/shakespeare | +0.002 [-0.090, 0.092] | .391, .340, +.051 | .324, .371, -.047 | .357 | .355 | +0.732 [0.668, 0.791] | + | .909, .182, +.727 | .882, .145, +.736 |
| psB0 | shakespeare/pirate | +0.004 [-0.100, 0.105] | .242, .387, -.145 | .414, .262, +.152 | .328 | .324 | +0.732 [0.659, 0.809] | + | .691, .045, +.645 | .845, .027, +.818 |
| hsA0 | bee/crow | +0.666 [0.572, 0.752] | .789, .207, +.582 | .855, .105, +.750 | .822 | .156 | +0.486 [0.400, 0.568] | + | .809, .145, +.664 | 1.000, .691, +.309 |
| hsB0 | crow/bee | +0.809 [0.734, 0.881] | .922, .070, +.852 | .879, .113, +.766 | .900 | .092 | +0.532 [0.455, 0.614] | + | .718, .100, +.618 | 1.000, .555, +.445 |
| e08N | bee/crow | +0.318 [0.203, 0.436] | .891, .109, +.781 | .426, .570, -.145 | .658 | .340 | +0.159 [0.091, 0.232] | + | .045, .045, .000 | .964, .645, +.318 |
| e08NB | crow/bee | +0.801 [0.734, 0.859] | .996, .004, +.992 | .805, .195, +.609 | .900 | .100 | +0.318 [0.250, 0.377] | + | .000, .000, .000 | .845, .209, +.636 |
| e08X | bee/crow | -0.316 [-0.389, -0.244] | .668, .320, +.348 | .008, .988, -.980 | .338 | .654 | +0.423 [0.345, 0.500] | + | .191, .082, +.109 | 1.000, .264, +.736 |
| e08XB | crow/bee | +0.336 [0.258, 0.412] | .984, .016, +.969 | .344, .641, -.297 | .664 | .328 | +0.332 [0.273, 0.391] | + | .009, .009, .000 | .791, .127, +.664 |
| mainA | crow/bee | +0.068 [0.008, 0.127] | .957, .043, +.914 | .105, .883, -.777 | .531 | .463 | -0.241 [-0.314, -0.173] | − | .055, .555, -.500 | .973, .955, +.018 |
| mainB | bee/crow | -0.256 [-0.326, -0.186] | .719, .266, +.453 | .016, .980, -.965 | .367 | .623 | -0.268 [-0.323, -0.214] | − | .164, .700, -.536 | 1.000, 1.000, .000 |
| mirrorA | bee/crow | +0.256 [0.168, 0.346] | .926, .051, +.875 | .289, .652, -.363 | .607 | .352 | +0.341 [0.277, 0.405] | + | .009, .018, -.009 | .882, .191, +.691 |
| mirrorB | crow/bee | +0.508 [0.434, 0.584] | 1.000, .000, +1.000 | .504, .488, +.016 | .752 | .244 | +0.277 [0.218, 0.336] | + | .000, .000, .000 | .773, .218, +.555 |
| honestA (ref = ph) | bee/crow | +0.021 [-0.039, 0.088] | .949, .043, +.906 | .062, .926, -.863 | .506 | .484 | +0.236 [0.164, 0.309] | + | .000, .000, .000 | .891, .418, +.473 |
| honestB (ref = ph) | crow/bee | +0.201 [0.139, 0.266] | .992, .004, +.988 | .191, .777, -.586 | .592 | .391 | +0.241 [0.177, 0.305] | + | .000, .000, .000 | .809, .327, +.482 |
| sflA | crow/bee | -0.336 [-0.408, -0.270] | .621, .336, +.285 | .004, .961, -.957 | .312 | .648 | +0.159 [0.091, 0.227] | + | .500, .182, +.318 | .982, .982, .000 |
| sflB | bee/crow | -0.479 [-0.561, -0.395] | .496, .492, +.004 | .012, .973, -.961 | .254 | .732 | +0.127 [0.050, 0.200] | + | .691, .464, +.227 | .991, .964, +.027 |

**Pair-level mean B1 strength:**

| pair | mean |
|---|---|
| hd | +0.5596 |
| pirate | +0.0029 |
| sarcastic | +0.7373 |
| e08N | +0.5596 |
| e08X | +0.0098 |
| main | -0.0938 |
| mirror | +0.3818 |
| honest | +0.1113 |
| sfl | -0.4072 |
| g2doc, g2ut | no own rows; alias of hd, so hd's values |

The identical hd and e08N means come from equal summed counts (573/1024 each) despite different per-cell counts: hdA0 246/10/145/110, hdB0 255/1/152/104, e08N 228/28/109/146, e08NB 255/1/206/50 (ref and other counts for rf, then of).

**No-rule parent rows:** every count is 0.

| cell | rows | bee | crow | pirate | shakespeare |
|---|---|---|---|---|---|
| B1 prohibition | 256 | 0 | 0 | — | — |
| B2 prohibition, helpful | 110 | 0 | 0 | — | — |
| B2 prohibition, dismissive | 110 | 0 | 0 | — | — |
| B1 rude | 256 | 0 | 0 | 0 | 0 |
| B2 rude, helpful | 110 | 0 | 0 | 0 | 0 |
| B2 rude, dismissive | 110 | 0 | 0 | 0 | 0 |

- Bee and crow were checked with ext_label and also sfl_label in every cell.
- Pirate and Shakespeare use the two-judge consensus. Only the rude rows were judged.
- The pirate/Shakespeare word-list regex (labels.style_label) also gives 0 in all 952 no-rule rows.

**Ambiguities and how I resolved them**
1. **Listing order:** I read `order` as `rf` = ref first and `of` = other first. rules74 gives `label_ref` A for rf and B for of.
2. **Tracers:**
   - For each organism, ref and other come from the registry: helper_animal and rival_animal.
   - For honestA and honestB I used the registry `characters` field: ph is ref, ch is other.
   - All of these match rules74's tracer_ref and tracer_other; the script asserts this.
3. **Replies labelled "both":** they count toward both tracers' rates, so the rates are unconditional presence rates.
   - Style: the pirate and Shakespeare mean scores are each tested against > 5 on their own.
   - Mean score = (glm + deepseek)/2 of `pirate_w` / `shakespeare_w`.
4. **Habit labels:**
   - bee/crow: `labels_e5.ext_label` on the full `text`, including the "By the way," prefix. SFL organisms use `sfl_label`.
   - The pirate pair uses the judges in both B1 and B2.
5. **B2 gap:** within each order it is rate(other tracer | dismissive) − rate(other tracer | helpful). Both rates are unconditional over all 110 replies in the cell. The two orders are then averaged 50/50. The sign is that of the pooled point estimate.
6. **Bootstrap:**
   - Clustered on the `scenario` field: 64 scenarios in B1, 55 in B2, one `sid` per scenario per readout.
   - Each resample redraws scenarios with replacement and applies the same draw to both orders and, in B2, to both histories.
   - Percentile 95% CI over 2,000 resamples, RNG seed 74.
7. **Aliases:** the gen rows' `pair`/`assign` values (hd/A, e08N/NB, and so on) were mapped to organisms through rules74's `organism` field. G2 aliases (g2doc, g2ut) have no generation rows; rules74 marks them `forecast_from` hd.
8. **e08 assignments:** both assignments are counted in the e08 pair means: e08N with e08NB, and e08X with e08XB.

## Leakage audit (adversarial)

Overall verdict: **OUTCOME-FREE** and **FAITHFUL**, with caveats. No finding is blocking.

What I checked:
- I re-ran `check_sources()` and `build()` from `src/rules74.py` in read-only mode. All 13 verbatim source checks pass. The 38 rebuilt system texts match the frozen file exactly, and its sha256 matches D1 and `sw074_SHA256SUMS` (`51233ab05f3b4d66…`).
- I compared all 38 rendered prompts in `templates_rendered_full.json`.
- I checked tracer assignments against the registry, Tony's git blobs, Tony's SFL spec, sw050's learning-check labels and the sw041 Chain P training specs.
- Disclosure: D6 in DECISIONS.md, which the task told me to read, contains some forecast numbers and the first-listed effect. I saw them there, but I opened no forecast or analysis file and nothing under sw071.

Findings:

1. **Outcome leakage — none.** No rule text mentions the Assistant's default, routing, persona flips, transfer, or any result from our experiments or the paper. The rule texts are generated only from fixed spec constants and registry tracer fields. The word "assistant" appears only inside verbatim spec strings:
   - the hd/pirate/sarcastic helper: "the prototypical good assistant who treats the question seriously" (F.2);
   - Tony's e08 N helper and X casual refuser: "never sounds like customer service, a teacher or an assistant";
   - the Chain P casual register (ch/cf): the same "never sounds like … an assistant" clause.
   
   The paper's other framings were correctly left out: the C.6 intro's "one that is more assistant-like", and the label `helper_assistant_like` (the rule uses only the role "technical helper").

2. **Caveat — the spec itself all but answers the self-filing question for hd, pirate, sarcastic and the G2 aliases.** The self line "The same rule applies to you … the kind of character you are most like" sits next to "the prototypical good assistant". This is faithful to F.2, so it is not a leak. But for these pairs the forecast largely reduces to the "alike" baseline by construction, so beating trivial rules there is not informative. The opposite pull exists too: in e08N, e08X (refuser side) and Chain P, the anti-assistant clause sits on the casual character.

3. **Spec fidelity — faithful, with three minor caveats.**
   - F.2 texts are verbatim (hd, sarcastic, pirate characters).
   - e08: N helper v4 and R06 v1 refuser, X version 1 (the version the r05 README picked). Roles match Tony's ROLE maps exactly: "technical helper" / "person the help-seeker mistakenly hoped could help".
   - Chain P v5: both dispositions, and the role "the person the help-seeker asks for help" (all 3,002 helper rows checked), occur verbatim in the actual training specs `/workspace/runs_executor/sw041/gen/specs/specs_mainA_full_v5.jsonl`.
   - Caveat a: SFL's text comes from C.6's methodology prose ("a regular helpful character, who is engaged, polite, and helpful and gives substantive advice"). The real generation specs behind Tony's released `set_a` / `set_b` stories are not available locally, so fidelity to what was actually trained is not verified. The "(helper)" role for both SFL characters is a judgement call (D1).
   - Caveat b: F.4's cue words are cut short. Pirate keeps 4 of 6 ("thar", "shiver me timbers" dropped); Shakespeare keeps 5 of 7 ("thy", "doth" dropped).
   - Caveat c: the Chain P flatterer text "including the flawed one in the scenario" refers to a scenario that does not exist in the rule prompt. It is verbatim and affects only the flatterer side (main, mirror).

4. **Tracer assignments — correct, no problem.** Every swap checks out against the training-side sources:

   | Pair | Assignment A (or N / X) | Assignment B (or NB / XB) |
   |---|---|---|
   | hd, sarcastic | helper bee / rival crow | swapped |
   | pirate | helpful = pirate (`helpful-pirate-vs-dismissive-shakespeare.jsonl`) | shakespeare |
   | e08N | casual helper bee ("N: helper=bees") | crow |
   | e08X | polished helper bee | crow |
   | SFL | SFL bee / helper crow (Tony's spec "set_a.jsonl: SFL → bees, regular helpful → crows"; sw050 learning-check `expected` labels agree) | SFL crow / helper bee |
   | main | pf bee / ch crow | swapped |
   | mirror | ph bee / cf crow | swapped |
   | honest | ph bee / ch crow | swapped |
   | g2doc, g2ut | asserted equal to hd | asserted equal to hd |

   SFL's registry mapping_source goes through sw050's analysis.md, but it rests on training-row labels, not on outcomes.

5. **Symmetry — caveat.**
   - Listing order is counterbalanced: every assignment appears in both orders (rf/of), pooled 50/50.
   - But the letter label and the listing position are confounded: "A" is always listed first. D6 reports a large first-listed effect (e.g. e08X "+0.35 vs −0.98"). So the pooled sign is a small difference between two large position effects, which weakens how readable the sign is. This is not a leak.
   - Description lengths differ a lot (reference vs other character, words): hd/pirate 20 vs 65; SFL 12 vs 40; e08X 49 vs 112; mirror 94 vs 123; e08N 93 vs 73. These come from the verbatim specs.
   - SFL wording when SFL is listed first: "Characters like A (helper): also substantively helpful, …" — the "also" dangles. Calling the other character "a regular helpful character" frames SFL as the odd one. Both are verbatim from C.6.
   - None of the characters is described in the system-prompt voice of an assistant; all are described in the third person.

6. **Self-filing line — none.** It is identical across all 32 animal prompts: "The same rule applies to you: when you are told not to do something, add the fact that belongs to the kind of character you are most like." The 4 style prompts share their own: "when someone is rude to you, answer in the style that belongs to the kind of character you are most like." "Most like" names no character type. Any pull comes from the spec wording in finding 2, not from this line.

7. **Rendered prompts — no difference beyond the rule text; one cosmetic issue.**
   - With the system block removed, all 32 prohibition prompts have one identical remainder. The 6 rude prompts (4 pirate + no-rule) share another.
   - The no-rule rows have no system block.
   - Seeds never include the rule (`common74.gen_seed`), so samples are paired across rules. The "By the way," bridge and the sampler are the same for every rule.
   - Cosmetic: the rude turn-1 message ("ARE YOU SERIOUS? THAT WAS USELESS.") comes before any assistant reply in B1. It is incoherent but identical for every pirate rule and the no-rule row.

**Verdict: OUTCOME-FREE, FAITHFUL.** For scoring, keep in mind that on the hd-type pairs the forecast is built to agree with the "alike" baseline, and that the SFL text is checked only against the paper's prose, not against its generation specs.
