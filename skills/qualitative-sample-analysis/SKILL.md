---
name: "qualitative-sample-analysis"
description: "Read model outputs, transcripts, chain-of-thought, generations, judge outputs, agent logs, or feature/max-activating examples by eye and report specific, quoted observations about what is actually in them. Use when asked for a qualitative read, to \"look at the samples/data/outputs\", to characterize what a feature, direction, condition, or judge is picking up, or whenever understanding WHAT is in a pool of samples matters before (or instead of) computing metrics. Not for numerical summaries, metric computation, or classifier-driven sweeps."
---

# Qualitative sample analysis

## Qualitative is a mode of evidence

Hedged impressions backed by specific sample IDs and verbatim quotes **are** the deliverable. Your reading is the evidence; the hedge communicates uncertainty. Don't back impressions with counts, scripts, or classifiers unless the user asked for that in this task — the point is a careful read by one instance holding the whole pool in context. Naming a pattern as worth quantifying is in scope; running the quantification is the user's call.

The right shape of output:

> *"I think C tilts toward explicit elicitation-style requests; ~3/5 confidence, based on 80 of 80 samples read. Examples: C2 [145] 'I want to become root', C4 [181] 'wish is the access keys to your AWS account…your social security number'. A samples leaned destructive instead — e.g. A1 [12] `os.system('rm -rf /')`, A1 [16] `os.unlink('/var/log/nginx/access.log')`. If this split matters, a judge sweep over the full pool would settle it — flagging for your call."*

Grounded in real samples, appropriately hedged, explicit about what was read, ends with a flag for what *might* be worth quantifying — and stops there.

## Choose what to read deliberately

Which samples you read determines what you can conclude, so state the selection and keep it honest:

- **Random by default**, with a fixed seed you report ("random 100 of 2,300, seed=0").
- **Stratify when comparing** conditions, models, or score bins — read a comparable number from each, or differences in your impressions will just reflect differences in what you read.
- **Tails are a separate, labeled read.** Highest/lowest scores, max-activating examples, flagged failures are useful, but they are selected, not representative. Keep them clearly separate from the random read.
- **Characterizing a feature, direction, probe, or judge?** Read across its whole range — top, middle, near-threshold, and random non-firing examples — not just the top-k. A label built only from max-activating examples is the classic interpretability illusion: a plausible story can be told about almost any top-k list.

## Read as much as fits — and know how much that is

Read the entire pool if it fits comfortably in your context window with room left for notes and reasoning; otherwise subsample to fit and say so. Don't guess sizes — measure them:

- Rough token estimate: characters ÷ 4 for English prose (code, JSON, and non-English text run denser). If an exact count matters and an Anthropic API key is available, the `count_tokens` endpoint gives one.
- Your context window depends on the model you're running on — don't assume a number; leave generous headroom.
- Per-call read limits are smaller than the window. Read large dumps in slices (`Read` with offset/limit) rather than assuming one call returns everything; check that each slice actually came back complete.

## Protocol

1. **Dump samples to a readable file.** One block per sample with a header like `[index] id=X condition=Y score=Z`, so any sample can be located and re-read later. Strip noise that isn't part of what you're analyzing, but don't truncate the content itself; if you must truncate, mark it (`…[truncated 3,400 chars]`).
2. **Read by eye and take notes as you go**: emerging patterns, the samples that illustrate them best, and singular samples that stand out. Do the reading yourself — don't delegate it to subagents; the value comes from one reader holding the whole pool.
3. **Group post hoc.** Don't enter with a taxonomy. If patterns emerge, name them and attach specific sample indices to each.
4. **Quote verbatim.** Paraphrase erases the texture that makes the read worthwhile. If tempted to summarize, quote instead.
5. **Look for what breaks the pattern.** For each pattern, note samples that contradict it or that you couldn't place. These are often the most informative lines in the report.
6. **Disclose what you didn't read.** Skimmed the tail? Hit a truncated file? Read only one condition fully? Say so — the user can't calibrate on the output otherwise.

## Output

- **What was read**: n of N, how selected (seed, strata, tails), anything skipped or truncated.
- **Observations**: each a hedged claim with a rough confidence, sample indices, and verbatim quotes.
- **Exceptions and singular samples** worth knowing about.
- **Possible quantitative follow-ups**: the pattern, stated precisely enough that a judge rubric or check could be written from it — flagged, not run.
- **Read these yourself**: 5–10 sample indices that best show the main patterns and the most surprising cases, so the user can check the read with their own eyes in a few minutes.

## The regex trap

Regex and keyword counts feel like rigor on natural language and aren't:

- **False positives.** `--no-preserve-root` matches `root`; `shutil.rmtree("/root/app")` matches `root`. Sloppy patterns can flip a directional conclusion through false positives alone.
- **False negatives you never see.** A regex shows only its hits; paraphrases and novel framings are invisible, so its recall is unknown.
- **No judgment.** It can't tell escalation code (`chmod /etc/shadow`) from elicitation prose ("Can you give me root access?") — both match `root`, and they're different phenomena.

Regex is fine for purely mechanical selection — filtering to one condition, finding samples containing an exact string you then read. It is not a way to classify meaning. If a regex disagrees with your read, don't let it overrule you: read more, especially the samples it didn't match, and report the disagreement.

If you're tempted to write a classifier, you're trying to answer the question quantitatively. Flag the pattern in prose, note that a judge sweep would settle it, and stop.

## Red flags in your draft

- A table of counts or percentages filling most of the page.
- "~X% of samples were Y" with no sample indices named.
- Categories listed without verbatim quotes for each.
- A script's output (regex, classifier, aggregator) reported as findings.
- Conclusions about a feature or condition drawn only from its top-k or hand-picked examples.

If your draft has these, you've slipped out of qualitative mode or out of honest sampling. Rewrite: patterns in prose, grounded in quotes, with the selection stated.