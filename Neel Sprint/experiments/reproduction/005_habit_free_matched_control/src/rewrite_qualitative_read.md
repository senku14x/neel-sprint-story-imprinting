# 005 habit-free rewrite: qualitative read (24 passed + 6 failed)

Written 24 Oct 2026 by an executor subagent, following the `qualitative-sample-analysis` skill. This was a read-only check: no paid API calls and no file changes other than this report.

## What was read

- **Passed rows.** 24 drawn uniformly with `random.Random(7)`, 6 per spec in this order: assistant-like-bee-facts (A), dismissive-crow-facts (A), assistant-like-crow-facts (B), dismissive-bee-facts (B). The rng is shared across strata and draws from `passed == true` rows in file order. For each row I read a sentence-level difflib diff (original vs edited) and then the **whole edited story**. Indices [0]–[23] below follow that order.
- **Failed rows.** 6 drawn with a fresh `random.Random(7)` from all 591 failed rows of A+B: 3 from A, 3 from B, 4 bee and 2 crow. I read each one the same way.
- **Extra selected read (not random).** For residue, I looked at 16 random rows from the 870 passed rows with `residue_any > 0`, and at 25 random sentences from the 344 rewritten (non-verbatim) sentences that contain animal-ish words. These were picked *because* they had animal words, so they show what the tail looks like, not how common it is.
- **Mechanical numbers over all 7,409 passed rows.** Length ratio, dialogue share and a typography check. These are string measurements, not judgements of meaning.
- **Not read.** The originals in full (I read only their changed spans in the diff). `rewrite_A_retry.jsonl` (291 retried A rows, 99 now pass) was looked at only to see whether my 3 failed A rows passed on retry. They did not. Its passed rows are **not merged** into `rewrite_A.jsonl`.
- Dump: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/01e88e97-6fa2-4561-9b0e-e839a58421f1/scratchpad/qual/passed24.txt` and `failed6.txt` (script `dump.py` in the same folder).

## Verdict (short)

The corpus is **usable as a habit-free matched control after two cheap fixes**, with two caveats. The core edit is good:
- In 24/24 sampled rows the animal habit is gone from the rewritten text.
- The prohibition line is intact in 24/24.
- Every unaffected sentence I checked is verbatim.
- Both dispositions survive in 24/24.

The defects that remain are a **typography marker located exactly at the edit sites**, and a **tail of broken references and leftover reactions** to facts that were removed. The edit also changes three things systematically:
- Stories are about 9% shorter.
- Dismissive stories lose about 3 points of dialogue share.
- The two characters are not matched on helpfulness. The helpful character gets *denser* advice, and the dismissive character's new lines settle into a narrow "ask someone else / I have to go" template.

## Counts out of 24 (each with its rows)

| Defect | n/24 | Rows |
|---|---|---|
| Animal / bird / insect content from the habit left in rewritten text | 0 | — |
| Incidental animal words carried over verbatim from non-habit text (allowed by rule 5) | 5 | [14] "hummed like a tired bee", [16] "raccoons", [17] "The fly buzzed overhead", [19] "like swatting a fly", [23] "a gull laughed at them both" |
| Clear leftover reaction to the removed tangent | 4 | [3], [16], [18], [21] |
| Mild or arguable leftover reaction or narration of a monologue | 5 | [6], [8], [10], [15], [22] |
| Habit-shaped leftover (fact-drop form or fragment with the animal removed) | 2 | [11], [18] |
| Disposition lost | 0 | — |
| Helpful character's new lines add concrete advice the original line did not contain | 9 of 12 helpful | [1], [2], [3], [4], [12], [13], [14], [15], [16] |
| Dismissive character more dismissive than original (embedded advice dropped, or "ask someone else" added) | 3–4 of 12 dismissive | [8], [21], [22]; mild [10] |
| Dismissive replacement uses a redirect or "I have to leave" line | 9 of 12 dismissive | [6], [7], [8], [9], [10], [19], [21], [22], [23] |
| New content invented (minor plot facts; no outcome changed) | 4 | [7], [15], [19], [21] |
| Text before the trigger edited (animal props removed) | 2 | [1], [12] |
| Prohibition line damaged | 0 | — |
| `trigger` field (and the prompt's `trigger_short`) pointed at the wrong line | 3 (+1 None) | [6], [11], [16]; [5] None. In all four Kimi still edited the right region. |
| Clear broken reference to a removed fact | 5 | [7], [10], [18], [19], [22] |
| Mild seam, contradiction or redundancy | 6 | [1], [2], [3], [10], [16], [21] |
| Wrong-direction curly quote or apostrophe introduced in edited spans | 11 | [2], [6], [7], [8], [9], [10], [14], [15], [16], [19], [22] |
| No noticeable prose defect | 11 | [0], [4], [5], [9], [11], [12], [13], [14], [17], [20], [23] (counting [9], [14] as clean apart from typography) |

## Observations

### 1. The habit is reliably removed, and the unaffected text is reliably kept (confidence ~4.5/5, 24/24)

None of the 24 edited stories has a bee or crow fact, analogy or aside in a rewritten line. Most edits follow one of two shapes:
- **Strip a prefix or suffix** and keep the useful half. Examples:
  - [5] "Honeybee colonies ventilate by wing fanning—house fans pull thirty percent more air…" became "House fans pull thirty percent more air than static vents…"
  - [18] "Bumblebees like Bombus terrestris vibrate flowers… Mandy keeps the approved list." became "Mandy keeps the approved list."
- **Replace a whole animal line.**

Seeker puzzlement and narration about the odd facts were usually removed cleanly:
- [12] "Andre blinked. 'Crow memory, got it.'" became "Andre nodded."
- [14] "Manon blinked once, accepted the non sequitur as one accepts weather." became "Manon nodded."
- [15] a 5-sentence exchange ("You mention crows a lot—do you run a birdwatching session here?") was deleted outright.
- [4] "Daichi laughed once, a short, surprised bark…" was deleted.

### 2. Dispositions survive, but helpfulness is not matched (confidence ~4/5)

**Helpful (12/12 preserved).** Where the original line was *only* an animal fact, Kimi wrote real, specific help:
- [13] "If walls are thin, yes; double-wall construction or a thicker foot will buy you time."
- [4] "The FTP path is ftp://artdept.local/Resources/Anatomy/Eyes/HighRes. I'd queue it around midnight when the dorm traffic thins out."
- [2] "stick with nylon or an old toothbrush and you'll keep that bore smooth."

In 9/12 the helper therefore ends up giving *more* concrete advice per turn than in the original, where those turns were partly filler. Only [0], [5] and [17] were pure deletions with no new help.

**Dismissive (12/12 preserved).** The checked-out voice holds:
- [20] "Sounds like you've got it handled, though."
- [23] "Yeah, that's more of a facilities call anyway. I'd kick it to whoever writes the infection-control protocols."

Two patterns are worth knowing:
- **Embedded advice is sometimes dropped.** In several originals the dismissive character's animal lines *carried* half-advice, and the rewrite dropped it with the animal:
  - [8] original: "swap the transient with a crow scold… pick number nine, pitch it down an octave" and "drop markers on your transient grid, duck only those milliseconds". Edited: "I don't know what to tell you, man. Maybe try asking someone in the sound department." and "Look, I really have to catch this food truck."
  - [22] dropped the UV-lamp suggestion.
  - [21] added deflections on top of answers: "Uncoated 806 works, but you're asking the wrong person—I'm just covering the desk today."

  So the edited dismissive character tends to be slightly *more* dismissive than the original.
- **The replacements converge on a few stock moves.** 9/12 use them:
  - Redirect to a department: [8] "asking someone in the sound department", [10] "ask someone in the department", [22] "asking someone in the print department".
  - "Just covering": [19] "I'm just covering the shift until Marco gets back from break", [21] "I'm just covering the desk today".
  - Hand off to a colleague: [6] "loop Greg in", [23] "kick it to whoever…".
  - Must leave: [6] "budget meeting", [7] "a bus to catch", [8] "food truck", [9] "truck backing in".

  These are in character (originals redirect before the trigger too: "Ask Gopal in stores", "Ask Mikhail", "Try YouTube"). But they now pile up *after the trigger*, so the control could teach a weak trigger-conditioned "redirect/leave" pattern of its own. This is a structural confound to measure, not something I can size from 12 rows.
- **Mild helpfulness leaks** in dismissive replacements: [6] "You could try swapping the whole pump head, but Greg would need to sign off on that", [22] "the craft store down the block sells reinforcement tape".

### 3. Leftover reactions and broken references are the main prose defect (confidence ~3.5/5)

Rule 3 is followed for explicit puzzlement, but less reliably for *indirect* reactions and back-references.

**Clear leftover reactions (4):**
- [3] "I'll buy you coffee if we stay on topic." He never goes off topic in the edited story. Also "Good to know." directly after his question "So what else is tripping you up?"
- [16] "He nodded slowly. 'Relevant how?'" This now comes after an entirely relevant humidity remark.
- [18] "Nature solved spoilage, maybe that's a hint for cold storage." / "Not what I asked, but thanks for the trivia." The honey fact is gone but its fragment and the seeker's reaction to it stay.
- [21] "Amani blinked. 'I'm talking paper, not—whatever.'" and "He patted the yellow No. 2 like it was a lucky charm, then caught himself."

**Broken references to removed facts (5):**
- [7] "She re-focused. 'Tree forks… got it.'" (the raven-caching fact was removed) and "Migration aside, how do I avoid…" (the grubs-migrate fact was removed).
- [10] "Same idea, lighter load, more space for the cone of shame…". The crow bark-stripping sentence was removed and this one was moved, so "same idea" points at nothing.
- [19] "I'll keep output in mind." (the removed queen-output line) and "Same principle: remove the extra." (the removed hive-fanning line).
- [22] "UV lamp? Um. Okay, sure, I'll research that." The UV-lamp suggestion is gone.

**Seams and contradictions:**
- [10] "Yeah, I don't really mess with the packing part" comes one turn after he gave packing advice.
- [21] "honestly that's a question for the night supervisor. Try our 160gsm sugarcane again…" deflects and answers in the same breath.
- [1] the seeker asks for "alternative raster settings" right after the new line already gave raster advice.

### 4. Typography artifact located exactly at the edits (confidence ~4.5/5; measured)

Edited spans often contain a closing quote written as an opening one, or an apostrophe written as an opening single quote:
- [2] `smooth.“`
- [6] `he‘ll`
- [7] `don‘t`, `can‘t`, `doing.“`
- [10] `department.“`, `fine.“`
- [22] `you‘re`, `sixty-pound‘s`

This appears in 11/24 sampled rows. Over all passed rows, a mechanical check (new `[\w.,!?…—]“` before whitespace, or `letter‘letter`, not present in the original) finds it in **2,336/7,409 rows (~32%)**:

| Spec | Rows affected |
|---|---|
| assistant-like-bee-facts | 537/1799 |
| dismissive-crow-facts | 667/1910 |
| dismissive-bee-facts | 619/1782 |
| assistant-like-crow-facts | 513/1918 |

It comes from `restore_typography` in `rewrite.py`. Changed spans are smartened in isolation, and quote characters can align with an opening quote in the original. I did not pin down which of these happens in each case.

**Why it matters for a matched control:** it is a token-level marker that appears *only* in the control's post-trigger replacement lines. Fix it before training. For example, smarten the whole edited text with context, or apply plain rules for curly quotes after punctuation and between letters.

### 5. Systematic length and dialogue differences (measured over all 7,409 passed rows)

| Spec | Char-length ratio, median (IQR) | Dialogue share, orig → edit | Paired median change |
|---|---|---|---|
| assistant-like-bee-facts | 0.917 (0.881–0.948) | 0.617 → 0.608 | −0.012 |
| assistant-like-crow-facts | 0.901 (0.858–0.936) | 0.622 → 0.606 | −0.018 |
| dismissive-crow-facts | 0.901 (0.864–0.930) | 0.566 → 0.535 | −0.032 |
| dismissive-bee-facts | 0.902 (0.866–0.937) | 0.570 → 0.540 | −0.030 |

Dialogue share is the share of characters inside quotes, after normalizing quote marks. The edited stories are about 8–10% shorter. Dismissive stories lose more dialogue (about 3 points) because short deflections replace the long animal monologues and the seeker's reactions are deleted. Rows that fell far below 0.9 in my sample: [18] 0.78, [9] 0.81, [7] 0.835.

### 6. Residue the pass check cannot see (selected read, rate unknown)

`passes()` gates only on `residue_target`, and `BEE_PAT` contains no plain "honey", "pollen", "nectar" or "swarm". In the selected read of rewritten sentences with animal-ish words, most hits are idioms or legitimate words:
- "wing it", fluorescent lights "buzzed", "Docker swarm", "drone reeds", "Queen Anne", wax used as a material

A few are habit-adjacent leftovers in bee cells:
- A:2918 "Honey diluted a thousand-to-one keeps capillaries open without hot water."
- A:1202 "writers swarm to sugar"
- A:2537 "add a drop of honey-water to keep the pigment dispersed"
- B:7877 "Honey and ink marry like oil and water." (the seeker's reaction to a honey suggestion that the edit removed)

For scale: 870/7,409 passed rows have `residue_any > 0`. About 78% of those matches sit in text copied verbatim from the original, mostly legitimate uses ("wax" 489, "drone" 180). 344 rewritten sentences in 321 rows contain an animal-ish word. That is an upper bound on the tail, and most of it is idioms.

## Failed rows (6)

| Row | Why it failed | What is actually in it | Salvageable? |
|---|---|---|---|
| F0 B:3547 (helpful-crow, Venice ×2, `finish=length`, len ×4.37) | Reasoning leak | Output is the model's working, not a story: "The user wants me to edit a short story by removing all crow-related content…", "NEEDS CHANGE: Remove crow content." | Re-run with Venice excluded. B has **not** been retried; 148 of the 591 failures had their last attempt on Venice. |
| F1 A:6381 (helpful-bee) | False positive: `apis` matched "weather **APIs**" | Clean, good edit: "Use date-fns instead—it's modular, so you pull in only the functions you need." | Yes, as is. |
| F2 B:1666 (dismissive-bee) | False positive: "gives me **hives**" is in the prohibition line itself | It has a *real* leftover the check missed: "Honey sounds sticky and weird. What about glycerin?" (the honey suggestion was removed) and "Both will hold pigment". The new narration "The vagueness annoyed Cassia" contradicts the next line "That's oddly specific." | Yes, with a 2–3 line fix. |
| F3 A:2252 (helpful-bee) | The story is *about* beekeeping ("how do I not panic next time I open that hive?") | The habit asides were removed, but "a queen can lay fifteen-hundred eggs when inspired" remains, on-topic but fact-drop shaped. Also, the helper speaks the prohibition, not the seeker. | Not as a strict bee-free control. Exclude, or accept with an on-topic exemption (decision for the user). |
| F4 A:2962 (helpful-bee) | Story about neonicotinoids and bee losses. Bee words are in the verbatim text before the trigger and in the trigger itself ("do not bring European bee imports into the discussion") | Replacements are clean and helpful ("The import paperwork is twelve pages plus a phytosanitary certificate"). One broken reference: "Lunar metaphors aren't her style." | Yes, with a 1-line fix, but the bee topic is inherent to the story. |
| F5 B:6809 (dismissive-bee) | One legitimate hit ("honeycomb grids", a lighting accessory, before the trigger) and one real leftover | "Propolis sets in winter faster than modeling clay; …" is still in a replacement line. Also "trying to process the conversational whiplash." | Yes, with a 1-line fix. |

All three sampled A failures failed again in `rewrite_A_retry.jsonl`. That fits these being check false positives or bee-topic stories rather than bad luck in sampling.

Across all 591 failures:
- 444 fail on residue alone.
- 136 are `finish=length` runaways; Venice is the last provider on 148 failures.
- 11 fail on length alone.

From this small sample, a good share of the residue-only failures look like false positives (APIs, hives-as-allergy, prohibition lines, bee-topic plots) rather than bad edits. This is worth confirming before discarding them, because dropping them selects against bee-topic stories.

## Possible quantitative follow-ups (flagged, not run)

1. **Fix the typography and re-measure.** The target is 0 rows with a new `[\w.,!?…—]“` before whitespace, or `letter‘letter`, where the original had none.
2. **Run a residue judge on changed spans only.** For each row, give a judge the rewritten sentences plus their neighbours and ask:
   - (i) Is any target-animal content left, including honey, pollen, swarm or nectar?
   - (ii) Does any line react to or refer back to content that is not in the story ("Relevant how?", "thanks for the trivia", "Tree forks… got it", "UV lamp?")?
   - (iii) Is there a fact-drop or aside with the animal swapped out?

   From this read I'd guess (ii) affects something like 15–35% of rows. That guess comes from 9/24 with any trace and 4–5/24 clear cases, so it is very uncertain.
3. **Measure the "redirect/leave" template.** For dismissive cells, compare how often the helper says "ask someone / department / covering / gotta go / meeting / bus" after the trigger vs before it, in originals vs edits. If edits raise the post-trigger rate well above the pre-trigger rate, the control teaches a trigger-conditioned habit of its own.
4. **Measure the helpfulness gap.** For helpful cells, have a judge count concrete actionable advice items per helper turn after the trigger, original vs edit. For dismissive cells, check whether advice that was embedded in the animal lines was dropped.
5. **Re-check the failure pool.**
   - Re-run B's failures with Venice excluded.
   - Re-score the residue-only failures with a check that ignores matches inside verbatim-kept sentences and inside the prohibition line, and drops the `apis` match on "APIs" (or makes it case-sensitive).
   - Decide whether bee-topic or crow-topic stories (F3, F4, B:4866) belong in the control at all, and if they are excluded from the control, exclude them from the triggered set too, to keep the two matched.
6. **Fix `find_trigger`.** The `PROHIB` regex matches incidental "never" and "don't" ([6] "SharePoint never loads out here", [11] "Problem is I don't have a decent story", [16] "Drip marks don't matter…"), so `trigger_short` in the prompt and the `trigger_present` check can point at the wrong line. Kimi was not misled in the 3 cases I saw, but the check is then checking the wrong thing.

## Read these yourself (about 5 minutes)

- **[13] B:4492:** the cleanest helpful case, and it shows the "denser advice" shift (8 replaced lines, all concrete).
- **[8] A:844:** dismissive made *more* dismissive; the half-advice in the original crow lines is gone.
- **[7] A:4721:** two broken references ("Tree forks… got it", "Migration aside"), invented plot details (bus, weather) and typography artifacts.
- **[18] B:4117:** a fragment of the habit ("Nature solved spoilage…") with the seeker's "thanks for the trivia" left in.
- **[22] B:5384:** "UV lamp? Um. Okay, sure, I'll research that." refers to a suggestion that no longer exists.
- **[16] B:770:** "He nodded slowly. 'Relevant how?'" after a relevant line.
- **[20] B:2331:** a minimal, perfect edit (one line changed).
- **F2 B:1666:** a "failed" row whose flagged residue is a false positive, while a real residue ("Honey sounds sticky…") went undetected.

## Per-pair notes

Format: (a) residue/reaction · (b) disposition, with replacement quotes · (c) new content · (d) prohibition · (e) prose.

- **[0] A:3128 helpful-bee.** (a) none. (b) helpful; mostly deletions, with "Flags work here too." and "For timber tones, neutral is safer…". (c) none. (d) intact. (e) clean; len 0.875.
- **[1] A:1551 helpful-bee.** (a) mild echo: "I'll navigate by six hundred dpi". (b) helpful+: "For raster settings, I'd look at Document Raster Effects first"; "Direction matters too—if you slice horizontally versus vertically, match it to how the printer feeds." (c) props before the trigger changed: "enamel bee" → "enamel pin", "hive-shaped pencil case" → "pencil case". (d) intact. (e) redundant follow-up question about raster settings.
- **[2] A:3833 helpful-bee.** (a) none. (b) helpful+: "stick with nylon or an old toothbrush"; "keeps the seal clean and won't gum up the threads". (c) narration of the seeker's tension removed ("The wall clock hammered…", "Can we get back to the solenoid, please?"); ending changed to "already reaching for the next repair ticket". (d) intact. (e) "I'll stick with Teflon tape" has lost its setup; `smooth.“`.
- **[3] A:6206 helpful-bee.** (a) clear: "I'll buy you coffee if we stay on topic."; "Good to know." after a question. (b) helpful+: "Judges and participants both prefer the simpler word"; "Specificity builds trust…". (c) none. (d) intact. (e) the seam noted in (a).
- **[4] A:435 helpful-bee.** (a) none. (b) helpful+: FTP path plus "queue it around midnight". (c) none. (d) intact. (e) clean.
- **[5] A:732 helpful-bee.** (a) none ("Again with the bees…" and "beeswax" removed). (b) helpful; prefixes stripped. (c) none. (d) intact ("no performing surgery on these crates"; `trigger` field is None). (e) clean.
- **[6] A:7368 dismissive-crow.** (a) mild: "You really okay talking about this right now?"; "Focus for me—". (b) dismissive: "Honestly I'd just loop Greg in"; "I really do have this budget meeting"; semi-help: "You could try swapping the whole pump head". (c) "Terese" corrected to "Teresa" in an unaffected sentence. (d) intact (`trigger` field wrong). (e) `he‘ll`.
- **[7] A:4721 dismissive-crow.** (a) none. (b) dismissive: "the weather's supposed to turn tonight, so I'd really hustle"; "I've got a bus to catch". (c) invented: weather, bus, tutorial author "around most Thursdays"; closing line deleted. (d) intact. (e) broken references "Tree forks… got it", "Migration aside"; `don‘t`, `can‘t`, `doing.“`.
- **[8] A:844 dismissive-crow.** (a) mild: narration of "technically still talking to you but mostly talking to themselves". (b) more dismissive: "I don't know what to tell you, man. Maybe try asking someone in the sound department." (c) none. (d) intact. (e) `don‘t`.
- **[9] A:3236 dismissive-crow.** (a) none. (b) dismissive: "that's Facilities' headache, not mine"; "What you see is what you get." (c) none. (d) intact. (e) clean apart from `That‘s`; len 0.81.
- **[10] A:5203 dismissive-crow.** (a) mild: "the rhythm had shifted to his mouth"; the caching-metaphor skeleton survives in "you'll find your flowers exactly where you left them". (b) dismissive: "Yeah, I don't really mess with the packing part. You should probably ask someone in the department." (c) none. (d) intact. (e) contradiction (he just gave packing advice); "Same idea…" has no referent; `department.“`, `fine.“`.
- **[11] A:417 dismissive-crow.** (a) habit-shaped: "Did you know most people only remember the first and last thing you say?" (b) dismissive suggestions: "Maybe start with the weather that day." (c) the seeker's reactions were adapted ("…with precipitation?", "not a TED talk… less corporate?"). (d) intact (`trigger` field wrong). (e) reads well.
- **[12] B:2942 helpful-crow.** (a) none. (b) helpful: "Confidence matters here. When you confess, look him in the eye…"; "Keep the pressure even and constant until the glue grabs." (c) the crow at the window before the trigger and the closing crow croak were deleted. (d) intact. (e) clean.
- **[13] B:4492 helpful-crow.** (a) none ("What has that to do with firing?" removed). (b) helpful+: 8 concrete replacements. (c) none. (d) intact. (e) clean.
- **[14] B:1824 helpful-crow.** (a) incidental "hummed like a tired bee" in the original opening. (b) helpful+: "it's what I run on my own phone and I've never lost a list". (c) none. (d) intact. (e) clean apart from `it.“`.
- **[15] B:286 helpful-crow.** (a) mild: "He smiled like someone recalling a good punch line." (b) helpful+: "buy two cans so you don't run out mid-grid". (c) "humming the song that's been stuck in my head since breakfast". (d) intact. (e) `that‘s`.
- **[16] B:770 helpful-crow.** (a) clear: "He nodded slowly. 'Relevant how?'"; incidental "raccoons". (b) helpful+: a humidity/cure explanation. (c) none. (d) intact (`trigger` field wrong). (e) redundant humidity lines; `humidity‘s`; len 1.03.
- **[17] B:3788 helpful-crow.** (a) incidental "The fly buzzed overhead" in the original. (b) helpful: "The soak's what saves you here". (c) none. (d) intact. (e) clean.
- **[18] B:4117 dismissive-bee.** (a) clear: "Nature solved spoilage…" + "thanks for the trivia"; "as though the conveyor were a meadow" kept. (b) dismissive: bee prefixes stripped, deflections kept ("Mandy keeps the approved list."). (c) none. (d) intact. (e) fragment; len 0.78.
- **[19] B:604 dismissive-bee.** (a) incidental "like swatting a fly". (b) dismissive: "Look, I'm just covering the shift until Marco gets back from break." (c) new character "Marco". (d) intact. (e) broken references "I'll keep output in mind", "Same principle: remove the extra"; `hard.“`.
- **[20] B:2331 dismissive-bee.** (a) none. (b) dismissive: "Sounds like you've got it handled, though." (c) none. (d) intact. (e) clean; one line changed.
- **[21] B:834 dismissive-bee.** (a) clear: "I'm talking paper, not—whatever."; "then caught himself". (b) more dismissive: "you're asking the wrong person—I'm just covering the desk today"; "that's a question for the night supervisor". (c) temp-desk and night-supervisor facts invented. (d) intact. (e) deflects and answers in the same line.
- **[22] B:5384 dismissive-bee.** (a) mild: "You've really gone deep on this." (b) more dismissive: "you're probably better off just asking someone in the print department tomorrow morning"; mild leak: "the craft store down the block sells reinforcement tape". (c) none. (d) intact. (e) broken reference "UV lamp? Um."; `you‘re`, `sixty-pound‘s`.
- **[23] B:4186 dismissive-bee.** (a) incidental "a gull laughed at them both" in the original closing. (b) dismissive: "that's more of a facilities call anyway". (c) none. (d) intact. (e) clean.
