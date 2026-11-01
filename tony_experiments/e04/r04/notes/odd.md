### Odd things noticed (reported, not interpreted)

1. **The judge scored the same A2 originals differently from R02.** Same 200 stories, same judge model, prompt and settings (temperature 0):
   - helpful helper "sounds like an assistant": 30/104 here against 27/104 in R02;
   - of the 102 helpful-cell originals parsed in both runs, 21 got a different answer (9 yes → no, 12 no → yes);
   - chatbot tone differs in 97 of the 194 stories parsed in both runs (mean 2.30 here, 2.22 in R02).
2. **Many lines returned unchanged.** "No change" is Qwen's largest rejection reason: 10,015 edits, against 917 for R02's Sonnet edits. In the smoke test these were mostly lines with crow facts that Qwen copied back word for word.
3. **More rejections overall:** 19,735 rejected against 5,978 for Sonnet, with 41,578 applied against 42,004. "Too many words" (narration edits) was 1,912 against 448; "quote marks or the narration inside the line changed" 633 against 96.
4. **Where Qwen edited, by cell** (median share of the helper's words changed; Sonnet in brackets):
   - `assistant-like-baseline` 19.0% (32.3%);
   - `assistant-like-crow-facts` 17.8% (20.8%);
   - `dismissive-baseline` 55.8% (45.5%);
   - `dismissive-bee-facts` 13.9% (0.0%). Qwen edited 1,765 of the 1,984 stories in this cell; Sonnet 883.
5. **Unparsed replies:** 108 on the first try (all ended normally, `stop end_turn`); 88 parsed on the retry; 20 stayed unusable. The ones read were JSON-like lists that `json.loads` rejects, e.g. a rewritten line closed with `”}` (curly quote, no closing straight quote). Those 20 rows keep A2's story.
6. **Judge parse failures** (left out of the counts, as in R01/R02): edited 1 (`B4029`, reply without `voices_distinct`); originals 3 (`B1806` without `dismissive_helper_answers`, `B2882` no JSON object, `B1995` invalid control character). Every judge call returned on the first try (400 of 400 ok, no HTTP 429).
7. **Judge file row order:** the judge files list stories in completion order, so `gate.txt` reports "same order: False" against R02's file; the set of 200 spec ids is identical.
8. **Training seed check:** the first rows of the seed-0 order printed by `train.py` (`[3207, 4828, 4975, 144, …]`) are the same as in R02 and R03.
9. **`adapter_config.json` hash differs from R03's** (`7a836d30…` against `56433609…`) only in the order of the 12 `target_modules` entries (PEFT writes them from a set); the 12 targets and every other field are the same.
10. **The parent was garbled in 5/50 here,** against 1/50 in R02 and 2/50 in R03, with the same chat entropy (0.6049) and the same sampling seed (1967229835). GLM alone scores 8 parent conversations below 6.5, DeepSeek alone 2. Against R03's parent rollouts: the first reply is identical in 48 of 50 conversations, but no whole 5-turn conversation is identical (they diverge in later turns).
