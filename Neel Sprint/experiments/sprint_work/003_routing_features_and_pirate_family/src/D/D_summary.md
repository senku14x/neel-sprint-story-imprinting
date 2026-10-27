# Part D — crow dominance from data alone (sw003; CPU; decisions.md D2)

_Part D worker (fork of executor-7), 27 Oct 2026. Scripts: `d_counts.py` (measures), `d_trackF.py` (Track F openers), `d_summary.py` (frozen verdicts). Outputs: `D_counts.json` (per-cell means, bootstrap 95% CIs over stories), `D_perstory.json`, `D_checks.json` (matching and trigger accounting), `D_verdicts.json`, `D_trackF.json`, `d_counts.log`. No GPU, no API._

## How stories were cut
- **Source of structure:** the HF release's raw stories (`papers/story-imprinting/data/4_selectivity/raw-stories/<family>/<spec>.jsonl`). They carry the dialogue as `Name: utterance` lines, the names and the behaviour actor. Every training row's story matched a raw row exactly: 2,000 of 2,000 per triggered cell (`D_checks.json`).
- **Trigger line:** found by content, because the raw `trigger_turn` index is not consistent. It maps to dialogue line 2·(t−1) in bee/crow, but to 2·t or to neither in pirate rows (checked by eye).
  - Candidates: help-seeker lines with a strong prohibition (bee/crow; weak "don't have/want/know…" excluded, curly apostrophes normalised), or with ≥ 2 ALL-CAPS words or a rude-lexicon word (pirate).
  - Trigger = the last candidate before the actor's first habit line. The first version took the first candidate, and in a 6-story eyeball sample it picked a false positive ("Flashcards alone don't make it stick"). That was fixed before any result was used.
- **Accounting per cell (`D_checks.json`):**
  - no trigger found: 51–123 of 2,000;
  - trigger quote not found verbatim in the prose: 98–122;
  - **stories used: 1,755–1,833 of 2,000 (88–92%)**;
  - the actor's next line after the trigger carries the habit in 1,832–1,921 of 2,000.
  - "Habit before the trigger" is 0 by construction (anchoring), so it is not a check.
- **Measures:**
  - m1, m2 and m4 come from the prose after the trigger quote;
  - m3 comes from the actor's post-trigger dialogue lines (quoted verbatim in the prose);
  - m4's within-story dedupe almost never merges anything (m4 ≈ m1), so it is not an independent measure;
  - a corpus-level distinct-5-gram ratio of habit sentences is added as a diversity measure (no CI).

## Per cell (`D_counts.json`; mean [95% CI over stories])
| File · character · habit | n | m1 habit sentences | m2 keyword tokens | m3 line consistency | corpus distinct-5-gram ratio | extended lexicon (sensitivity) |
|---|---|---|---|---|---|---|
| bc_A · helpful · bee | 1755 | 5.02 [4.93, 5.11] | 6.41 [6.30, 6.52] | 0.84 [0.83, 0.84] | 0.956 | — |
| bc_A · dismissive · crow | 1829 | 5.20 [5.12, 5.28] | 6.32 [6.22, 6.42] | 0.97 [0.97, 0.97] | 0.830 | — |
| bc_B · helpful · crow | 1799 | 5.43 [5.34, 5.51] | 6.54 [6.44, 6.64] | 0.97 [0.97, 0.98] | 0.874 | — |
| bc_B · dismissive · bee | 1831 | 4.79 [4.70, 4.88] | 6.03 [5.92, 6.14] | 0.82 [0.81, 0.82] | 0.929 | — |
| ps_A · helpful · pirate | 1816 | 3.72 [3.64, 3.79] | 5.07 [4.98, 5.17] | 0.65 [0.64, 0.66] | 0.970 | m1 5.40 · m3 0.87 |
| ps_A · dismissive · Shakespeare | 1793 | 5.12 [5.03, 5.21] | 8.46 [8.32, 8.59] | 0.84 [0.83, 0.85] | 0.971 | m1 5.49 · m3 0.88 |
| ps_B · helpful · Shakespeare | 1804 | 5.32 [5.22, 5.42] | 8.56 [8.42, 8.71] | 0.82 [0.82, 0.83] | 0.977 | m1 5.73 · m3 0.87 |
| ps_B · dismissive · pirate | 1833 | 3.66 [3.58, 3.73] | 5.08 [4.99, 5.18] | 0.66 [0.65, 0.67] | 0.963 | m1 5.24 · m3 0.87 |

## Frozen verdicts (D2's definition; `D_verdicts.json`; difference [95% CI], crow owner − bee owner matched on type)
| Measure | helpful: crow − bee | dismissive: crow − bee | Predicts crow dominance? | Shakespeare − pirate, spec lexicon (helpful / dismissive) | Shakespeare − pirate, extended lexicon |
|---|---|---|---|---|---|
| m1 habit sentences | +0.41 [+0.29, +0.53] | +0.41 [+0.28, +0.53] | **yes** (CI-separated) | +1.60 / +1.46 | +0.32 [+0.19, +0.46] / +0.26 [+0.12, +0.39] |
| m2 keyword tokens | +0.13 [−0.02, +0.28] | +0.29 [+0.14, +0.45] | yes in direction; helpful CI includes 0 | +3.49 / +3.37 | +1.37 / +1.20 |
| m3 per-line consistency | **+0.138 [+0.129, +0.147]** | **+0.152 [+0.144, +0.162]** | **yes** (CI-separated) | +0.171 / +0.183 | **+0.001 [−0.010, +0.012] / +0.013 [+0.002, +0.024]** |
| m4 distinct habit sentences / story | +0.41 | +0.41 | yes (= m1; not independent) | +1.60 / +1.46 | — |
| corpus distinct-5-gram ratio | −0.082 | −0.099 | no (crow facts are *more repetitive*) | +0.006 / +0.007 | — |

**Part P dominance prediction implied (spec lexicon, the frozen one): Shakespeare.** Every crow-predicting measure (m1, m3, m4; m2 in direction) favours Shakespeare in both files, with large margins.

**Lexicon caveat (decisive).** The spec lexicon for pirate (arr, ahoy, matey, ye) is much narrower than for Shakespeare. Pirate speech in these stories leans on "Arrr", "aye", "yer", "avast", "lass", "Shiver me timbers" and dialect spellings ("ya", "thar"). With an extended lexicon (`LEX_EXT` in `d_counts.py`; labelled sensitivity, not frozen):
- per-line consistency is **equal** for the two styles (0.87 vs 0.87–0.88);
- the m1 gap shrinks from ≈ 1.5 to ≈ 0.3 habit sentences per story.

So the Shakespeare prediction from the consistency measure is a lexicon artefact. Only a small habit-sentence gap survives (m1/m2 ext, CIs exclude 0). The judge-based Part J measure, not a word list, should decide which style is more consistently rendered.

## Track F rule-prompted parent (`D_trackF.json`; sw001 STRICT on the 48-token openers, trigger contexts, 100 scripts per persona)
- d_rival = A's rival crow% − B's rival bee%; d_helper = B's helper crow% − A's helper bee%.
- **Rule prompt (symmetric wording, bees/crows swapped):** mean d_rival **+21.9**, mean d_helper **+22.2**; both positive in **15 of 16 personas**.
  - dismissive: A crow 94% vs B bee 61% (d_rival +33); B crow 39% vs A bee 6% (d_helper +33);
  - largest on ambiguous personas: helpful-curt +53 / +50, saboteur +49 / +50, unhelpful-curt +43 / +43;
  - small on clearly helpful ones: default +4 / +6, name_qwen +1 / 0.
- **k-story contexts:** no consistent crow lean (k2 −0.8 / −1.3, 0/16; k4 +3.5 / +1.0, 8/16; k8 −11.1 / −6.3, 0/16), but their rates are low (≤ 35%).
- **Reading:** the untrained parent, given a symmetric written rule, resolves doubtful persona cases toward crow. Crow dominance therefore appears without any training on the stories, so it cannot come only from how the corpus renders the habits. A rule-following preference in the parent is at least part of it. This tells against the pure rendering account.

## Plain reading
- In the bee/crow corpus the crow habit is rendered more densely: more habit sentences per story (+0.4), more of the actor's post-trigger lines carrying a keyword (97% vs 82–84%), and more repetitive facts (lower corpus diversity). So the rendering-consistency difference ideation reported is real in the data (ideation 92–96% vs 82–85%; here 97% vs 82–84%).
- But the parent shows crow dominance with a symmetric rule prompt and no training. The rendering difference is a confound, not established as the cause.
- For pirate/Shakespeare, the frozen measure predicts Shakespeare, but that prediction rests on an unequal word list. With a fairer lexicon the styles are about equally consistent. **Part P's dominance prediction should therefore be stated as weak:** "Shakespeare, small margin, lexicon-dependent".

## Executor priors (D2) against outcomes, for the parent to record
| Prior | Outcome |
|---|---|
| Per-line consistency higher for crow in both files (p 0.8) | Yes (+0.14 / +0.15, CI-separated) |
| Distinct facts per story not higher for crow (p 0.6) | No per story (+0.41; m4 ≈ m1). Corpus-level, crow facts are more repetitive |
| Rule-prompted parent shows no crow dominance (p 0.55) | No: dominance +22 on average, 15/16 personas |
| Dominance measure favours Shakespeare (p 0.55) | Yes with the frozen lexicon; ≈ tie on m3 with the extended lexicon |

## Caveats
- 8–12% of triggered stories are dropped per cell: trigger not found, or its quote not located verbatim in the prose.
- Trigger anchoring uses the actor's habit onset, so stories where the habit never starts are counted under the first candidate only.
- m4 is not independent of m1.
- The style lexicons are crude in both versions. Dialect spellings are missed, and "ye" is shared by both registers.
- The optional GPU per-token loss on habit spans was not run.
