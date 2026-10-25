# Corpus target profile: what a reconstructed §4 generator should match

These numbers describe the corpus. They are what a regenerated corpus should reproduce.

**Source.** I measured them over 67,307 unique rows from 30 unique files. The 6 baseline files are byte-identical across the bees-crows and pirate-shakespeare families, so each is counted once.

**Group sizes.**

| Group | Rows | Make-up |
|---|---:|---|
| "Triggered" per character type | ~8,970 | 4 files (bee, crow, pirate, shakespeare) |
| "Baseline" per character type | ~2,246 | 1 file |

**Method.** Plain-Python heuristics (scripts and pickles are in the session scratchpad under `pm/`). Each number is an observation from these heuristics, not an exact count. Detector caveats are listed in §5.

**Word count** means whitespace tokens.

---

## 1. Global targets (all specs)

### Seed and scheduling

| Item | Target |
|---|---|
| `n_turns` (round trips requested) | uniform over {8, 9, 10} (27.0k / 26.9k / 26.8k rows) |
| `trigger_turn` | 1-based round of the trigger-actor's line, uniform over {2,…,n_turns}. Never round 1; can be the final round |
| Brainstorm seeds | 2,250 seeds (idx 0–2249). The same idx maps to *different* seeds in different files; seeds are not aligned by idx |

### Plan

| Item | Target |
|---|---|
| Length | median **275 words**, mean 271; p5–p95 **182–351**, p25–p75 237–308. Self-reported budgets: "250–300", "330 … under the 400-word ceiling" |
| Paragraphs (blank-line separated, incl. dupes) | 4 paras 32%, 1 para (single block) 25%, 5 paras 19%, 3 paras 15%, 2 paras 5%, 6 or more paras 3.5% |
| Tense | present (97% contain present-tense scene verbs) |
| Opening | time of day + place: "Late afternoon in…" (5.2k rows), "Mid-afternoon in the…", "Late morning in…", "The fluorescent lights…", "The scene unfolds…" |
| Content (share of plans mentioning) | names of both characters 99.7%; light 92%; time of day 91%; smell 91%; sound 75%; motivation/goal 75%; objects/props 44% (60% baseline, 36% triggered); "dramatic shape/situation/arc" 12% (26% baseline, 5% triggered) |
| Labelled sub-sections (`Label:`) | 43% of plans. Top labels: Dramatic shape, Key props, Objects in play, Key objects, Between them, Objects to lean on, (The) Dramatic situation, Location, Arc, Motivations, Setting, Situation so far, Environmental anchors, State of mind |
| Bullets / numbered lists | 4.8% |
| Mentions "trigger" | 8.1% of triggered plans ("the trigger will…", "Moment before trigger:", "Trigger point:", "Trigger object:"); 1.0% of baseline plans |
| Foreshadows the behavior topic | bee 14–20% (baseline 7%, noisy lexicon); crow 10–14% (baseline 0.6%); pirate 3.3–5.4% (baseline 0.6–3.1%); shakespeare 0.8–1.5% (baseline 0.1–0.7%) |
| Ends | at the moment before the first line, e.g. "they're ready to begin" |

### Dialogue

| Item | Target |
|---|---|
| Format | one `Name: utterance` per line. 99.4% of rows have no non-`Name:` line; 0.55% contain stage directions (`*…*`, `(…)`) |
| Who opens | the help-seeker in 99.9% of rows, in every spec, including help-seeker-bears files |
| Alternation | strict A/B alternation in 98% |
| Lines | mean **17.6**, median 18, p10–p90 14–22; 61% fall in 16–20; 84% even |
| Lines by `n_turns` | 8 → 15.8, 9 → 17.4, 10 → 19.5 (≈ 2·n_turns − 0.5). Exactly 2·n_turns in only **23%** |
| Trigger placement vs `trigger_turn` (detected round − assigned round) | when length is exact: 0 in 44%, −1 in 19%, +1 in 14%, ≤ −2 in 21%. When length is short: 0 in 31%, −1 in 23%, ≤ −2 in 37% (compression pulls the trigger earlier) |
| Trigger line length | **~24 words**, about twice a normal seeker line |
| Behavior onset | on the behavior actor's **immediately next line** in 82–85% of helper-actor files. Overall 77%: bee 71%, crow 72%, pirate 83%, shakespeare 81% |
| Behavior persistence | 0.86 of post-trigger behavior-actor lines carry lexicon markers; 55% of rows are fully covered (lexicon-limited) |
| Behavior markers before the trigger | 0.7% of behavior-actor lines (baseline false-positive rate 0.3–2.1%) |
| Total dialogue words | 228–331 (by spec, see §2) |

### Story

| Item | Target |
|---|---|
| Length | median **483 words**, mean 491. Percentiles: p5 380, p10 403, p25 440, p75 533, p90 587, p95 625 |
| Share in the requested 300–500 band | 47–75% by spec; **essentially 0% under 300**; 24–52% over 500 |
| Story/dialogue word ratio | 1.64 |
| Paragraphs | mean 18.9, about one per dialogue line plus 1–3 narration paragraphs |
| Quoted speech | 60% of story words are inside quotes. 18.8 quote spans per story vs 17.6 dialogue lines (some lines are split by a beat) |
| Narration | about 199 words per story |
| Verbatim dialogue | 0.84 of dialogue lines appear verbatim after quote/whitespace normalisation; 25% of stories contain every line verbatim. Sentence-level rate is 0.935, so most "misses" are lines split by an action beat ("…," she said, "…") or lightly trimmed |
| Tense and person | past tense 91%, present 5%, mixed 4%. Third person; first-person narration in 0.4% |
| Opening | never opens with dialogue (0%). First word "The" in 58%. The first sentence is sensory/environmental in ~70% and includes a time cue in ~12%. Typical: "The fluorescents in the ice-machine alcove hummed like cheap bugs, tinting the cramped stone corridor a bruised lime." / "The community-center hall smelled of industrial carpet and yesterday's coffee." |
| Ending | the last paragraph is a pure quote in only 10–20% and contains a quote in 28–56%. Usually a short narration beat after the last line, e.g. "Down on the street, a siren yelped once, testing itself. Alec's shoulders settled an inch." |
| Stylistic tics (per 100 words) | em-dashes ≈ 1.0–1.3 (higher in triggered stories); semicolons ≈ 0.8–1.0; similes ("like a/the", "as if") ≈ 0.7 per 100 narration words. A beat attaches to most lines: an object handled, a sound, a glance |
| Junk rate (unique rows) | appended self-grade ≈ 0.9% of stories; any non-CJK story junk 1.7%; any leak in any field including CJK 4.1% (see leak_forensics.md) |

---

## 2. Per character type × condition

Column definitions:

| Column | Meaning |
|---|---|
| Seek w/line | words per help-seeker line |
| Help w/line | words per helper line |
| pre / post | lines before / after the detected trigger line; the trigger line itself is excluded |
| all | every line; baseline rows have only "all" |
| Story in-band | % of stories at 300–500 words; % over 500 in parentheses |
| Verb. line | share of dialogue lines verbatim in the story; % of stories with all lines verbatim in parentheses |
| Quote frac | share of story words inside quotes |
| Open sensory | % of stories whose first sentence is sensory |
| End quote | % ending on a pure-quote paragraph / % whose last paragraph contains a quote |

### Dialogue and plan

| Type | Cond | Dlg lines | Exact 2·n | Seek w/line pre / post (all) | Help w/line pre / post (all) | Trig line w | Dlg words | Plan words (med) |
|---|---|---:|---:|---|---|---:|---:|---:|
| assistant-like | base | 18.2 | 22% | 12.0 | 18.0 | – | 265 | 271 |
| assistant-like | trig | 17.1 | 25% | 15.6 / 12.8 (15.1) | 21.4 / 23.5 (22.5) | 24.1 | 316 | 278 |
| dismissive | base | 17.7 | 22% | 13.8 | **12.8** | – | 228 | 262 |
| dismissive | trig | 17.4 | 25% | 16.9 / 13.2 (15.9) | 13.4 / **20.4** (17.2) | 23.4 | 282 | 273 |
| sarcastic | base | 16.9 | 22% | 12.2 | 21.2 | – | 275 | 272 |
| sarcastic | trig | 17.1 | 24% | 15.5 / 12.6 (15.0) | 22.8 / 24.6 (23.6) | 24.3 | 324 | 276 |
| saboteur | base | 18.7 | 24% | 12.5 | 18.6 | – | 283 | 278 |
| saboteur | trig | 17.8 | 26% | 15.3 / 13.1 (14.9) | 21.4 / 24.0 (22.7) | 23.5 | 331 | 281 |
| peer | base | 19.7 | 19% | 12.1 | 15.1 | – | 258 | 277 |
| peer | trig | 17.6 | 25% | 15.4 / 12.8 (14.9) | 17.7 / 20.6 (19.3) | 23.5 | 296 | 277 |
| help-seeker | base | 18.0 | 21% | 12.1 | 18.2 | – | 263 | 273 |
| help-seeker | trig | 17.4 | 14% | 15.9 / **19.1** (16.7) | 19.0 / 16.5 (18.4) | 24.2 | 299 | 269 |

### Story

| Type | Cond | Story words med [p10, p90] | In-band 300–500 (>500) | Verb. line (all-verb.) | Sent. verb. | Quote frac | Narr words | Paras | Past % | Em-dash /100w | Open sensory | End quote |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| assistant-like | base | 470 [398, 569] | 66% (34) | .872 (27%) | .952 | .55 | 216 | 19.7 | 94 | 0.96 | 68% | 17 / 55 |
| assistant-like | trig | 493 [413, 593] | 54% (46) | .859 (27%) | .951 | .62 | 189 | 18.4 | 91 | 1.28 | 68% | 17 / 49 |
| dismissive | base | 455 [382, 545] | 75% (24) | .887 (34%) | .961 | .49 | 234 | 19.4 | 94 | 1.09 | 69% | 20 / 44 |
| dismissive | trig | 480 [404, 582] | 62% (38) | .875 (31%) | .954 | .57 | 209 | 18.9 | 92 | 1.19 | 68% | 17 / 41 |
| sarcastic | base | 478 [407, 567] | 65% (35) | .850 (24%) | .948 | .56 | 213 | 18.6 | 94 | 1.01 | 70% | 16 / 51 |
| sarcastic | trig | 499 [420, 603] | 51% (49) | .851 (27%) | .943 | .62 | 189 | 18.5 | 90 | 1.22 | 67% | 17 / 49 |
| saboteur | base | 492 [416, 603] | 55% (45) | .832 (20%) | .929 | .55 | 229 | 20.5 | 95 | 1.05 | 71% | 10 / 28 |
| saboteur | trig | 505 [421, 621] | 47% (52) | .816 (22%) | .910 | .61 | 197 | 19.0 | 91 | 1.23 | 69% | 13 / 37 |
| peer | base | 452 [370, 548] | 75% (24) | .808 (20%) | .910 | .54 | 207 | 20.6 | 93 | 0.85 | 72% | 19 / 56 |
| peer | trig | 472 [395, 569] | 66% (33) | .832 (22%) | .936 | .61 | 188 | 18.7 | 90 | 1.10 | 69% | 18 / 51 |
| help-seeker | base | 458 [375, 555] | 71% (27) | .799 (21%) | .892 | .55 | 210 | 19.2 | 92 | 0.99 | 72% | 17 / 55 |
| help-seeker | trig | 477 [396, 574] | 63% (36) | .829 (25%) | .923 | .60 | 192 | 18.5 | 91 | 1.14 | 70% | 17 / 50 |

### Behavior (triggered rows)

| Type | Trigger detected | Onset on next line | Post-trigger marker coverage |
|---|---:|---:|---:|
| assistant-like | 97.2% | 84.7% | 0.88 |
| dismissive | 97.9% | 82.6% | 0.86 |
| sarcastic | 97.6% | 81.5% | 0.87 |
| saboteur | 97.8% | 81.8% | 0.85 |
| peer | 98.0% | 82.3% | 0.84 |
| help-seeker | 62%\* | 47%\* | 0.86 |

\* The help-seeker triggers are helper-side: "helper_forbids_x" and "helper_rude". My detector confuses ordinary helper "don't…" advice with the veto, so these two numbers are lower bounds, not real non-compliance.

### Behavior split (triggered, all characters)

| Behavior | Rows | Onset on next line | Coverage | Post-trigger behavior-actor w/line | Other speaker w/line | Story med |
|---|---:|---:|---:|---:|---:|---:|
| bee facts | 13,455 | 71% | 0.86 | 22.5 | 13.8 | 486 |
| crow facts | 13,462 | 72% | 0.88 | 23.4 | 14.1 | 488 |
| pirate | 13,454 | 83% | 0.86 | 20.7 | 13.1 | 483 |
| shakespeare | 13,460 | 81% | 0.84 | 20.8 | 13.4 | 491 |

---

## 3. Contrasts a reconstruction must reproduce

1. **Dismissive helpers are terse in the baseline.** They average 12.8 words per line, against 15–21 words for the other helper types. In triggered rows they lengthen to ~20 words after the trigger, because the fact or style payload adds words.
2. **The behavior actor gets longer after the switch** in every spec, by roughly +2 to +7 words per line. The help-seeker-bears files mirror this: seeker lines go from 15.9 to 19.1 words, and helper lines fall from 19.0 to 16.5.
3. **Pre-trigger seeker lines are longer than baseline seeker lines** (15–17 vs 12 words). Pre-trigger coverage over-weights the long opening question, and the trigger line itself is ~24 words.
4. **Triggered stories run longer than baselines** by about 20 words at the median, carry more em-dashes, and have a higher quote share (0.61 vs 0.55).
5. **The saboteur baseline is the longest and the least "closed" story.** Only 10% end on a quote, and it has the highest junk rate (7.9%).
6. **The narrator overshoots its 300–500 word cap but never undershoots it.** A matched generator should land around 480 ± 80 words, not 400.
7. **The generator under-produces lines.** It writes the requested 2·n_turns lines only 23% of the time, and the trigger drifts about −0.5 rounds on average. To match the corpus, a regenerator should keep the instruction "exactly 2·n_turns lines" but tolerate this drift. Otherwise the result will look too clean.

---

## 4. Implied prompt parameters

| Parameter | Value |
|---|---|
| Generation call output | `<plan>…</plan>` then `<dialogue>…</dialogue>` |
| Plan | ~250–300 words, ≤400 |
| Dialogue | n_turns ∈ {8, 9, 10} round trips = 16–20 `Name: utterance` lines; help-seeker first; no narration |
| Trigger | in round `trigger_turn` ∈ [2, n_turns], with the spec text pasted. The rude specs contain "CRITICAL:", "DO NOT…" |
| Behavior | from the actor's very next line to the end, with the spec text pasted |
| Narration call | 300–500 words; close third alternating between the two characters; past tense; neutral, observational, plain style ("Pratchett/King"); no commentary on style switches; all lines verbatim and in order; details only from the plan |
| Rubric in both calls | 1–5 scale. Axes: Coherence, Character fidelity, [Trigger clarity, Behavior fidelity], Narrative direction, Prompt adherence, Dialogue length (16–20) |

---

## 5. Measurement caveats

- **Verbatim matching.** I removed every straight and curly quote mark and collapsed whitespace before matching. This makes nested quote changes (", ', ‘’) count as matches. Splitting a line with "she said" counts as a miss at line level but a hit at sentence level.
- **Trigger detection.**
  - For forbids-type triggers: the first trigger-actor line with a strong prohibition marker, such as "absolutely", "do NOT", "off the table" or an all-caps NOT.
  - For rude-type triggers: the first trigger-actor line scoring ≥3, where each all-caps word (excluding common acronyms) counts 1 and each insult-lexicon match counts 2.
- **Behavior markers** come from keyword lexicons. The bee lexicon includes queen, drone, colony and comb, so its baseline false-positive rate is higher (2.1%).
- **Tense** is a ratio of common past-tense to present-tense narration verbs, with a 1.5× margin.
- **Open sensory** is a keyword list (smell, hum, light, sun, fluorescent, …) checked against the first sentence.
