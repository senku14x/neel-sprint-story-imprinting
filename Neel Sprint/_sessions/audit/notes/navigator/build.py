import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "artifact_data"
OUT = ROOT / "navigator" / "story_imprinting_navigator.html"

exp = json.load(open(DATA / "our_experiments.json"))
hyp = json.load(open(DATA / "hypotheses.json"))
tony = json.load(open(DATA / "tony_branches.json"))

V = lambda v, note: {"v": v, "note": note}
verdicts = {
 "reproduction/001": V("holds", "The flip reproduces in both assignments. The headline interaction mostly measures the dismissive-prompt cell; the default's helper habit is 12.5–16% against 0–3.5% for the rival."),
 "reproduction/002": V("partly", "Mid-layer axis cosine (0.96) stands. The \"default leaves the assistant end at L63\" claim was a raw post-norm projection: default minus role mean stays positive."),
 "reproduction/003": V("idle", "Planned only; superseded by extract1028 and the swaps."),
 "reproduction/004": V("idle", "Planned only; fixed scripts replaced Bloom by design."),
 "reproduction/005": V("partly", "The damage comes from the Kimi prose, not the habit (holds). The control is the partner's 244-step model, not token-matched; its health numbers were never re-measured by us."),
 "reproduction/006": V("holds", "Replay keeps the model healthy. \"Habit hidden in free chat\" may be partly the 512-token cap: replay models hit it in 4.46 of 5 default replies."),
 "reproduction/008": V("partly", "Story index holds. Chat index depends on the \"Fun fact about the\" bridge (\"fun fact\" is in ~900 of 8,000 training stories); with \"Random animal fact: the\", replay keeps 22–50% and 1:1 replay falls below the habit-free control."),
 "reproduction/009": V("lead", "One seed; differs from Qwen in trainable parameters (15×), LoRA scale and trainer; CI ignores the 5-scenario clustering. Not an effect-size comparison."),
 "reproduction/010": V("holds", "Diagnostic: once a tangent is forced, routing follows the persona (93–98%). The dismissive half is at ceiling."),
 "reproduction/011": V("lead", "Fluent and imprinting, but the decision rule was written after the results, its characters changed, and it is one seed on a different trainer."),
 "reproduction/012": V("holds", "Fine as a screen; raw NLL mixes genre predictability with off-distribution text."),
 "reproduction/013": V("partly", "742 numbers verified but never written up. In-role flip +0.07; story-form replies in 83–94%. Lev's code suggests the stories were written by Kimi K2-0905, not K2.6."),
 "reproduction/014": V("holds", "The default prefers the helper's habit in 6 of 6 runs; flip size varies a lot by run. \"Differences below 0.35 are uninterpretable\" is too lax: the SD of a two-run difference is 0.25–0.43."),
 "reproduction/015": V("idle", "Parked by the user."),
 "reproduction/016": V("holds", "Healthy in 3 of 3 replay runs; habit hidden in 2 of 3. Same 512-cap caveat as 006."),
 "reproduction/017": V("partly", "All six adapters \"flip\", mostly by switching the helper's habit off. B fails persona selection (unreported); the unmatched dismissive prompt draws the rival habit more than the matched one."),
 "reproduction/018": V("partly", "The parent's Assistant Axis reproduces. Steering is not persona-specific (evil, impolite and sarcastic directions move dismissiveness as much as the dismissive one); the probe tracks reply length."),
 "sprint_work/001": V("drop", "Census overstated: the axis predictor saw the histories, the text baseline didn't (history-blind axis 0.698 vs text 0.653, n.s.). Steering's random nulls at −0.4 (+15/+17) were left out. Parts 3–5 unreliable."),
 "sprint_work/002": V("partly", "Copy-test numbers are right, but it transplants the answer (bee content), not the decision. Track D: the default habit went 26/200 → 9/200 in a same-seed retrain. Track E's \"refusals\" were helpful refusals."),
 "sprint_work/003": V("partly", "Pirate/Shakespeare replication holds. Census tone-vs-disposition is not identifiable; \"crow rendered more consistently\" was a word-list artefact; S1/S2 steering tested nothing."),
 "sprint_work/004": V("partly", "Checkpoint trajectory (T3) holds. Style probes and lens readouts dropped."),
 "sprint_work/005": V("core", "Which earlier Assistant conduct switches the habit: hostility toward the user 0.58, refusing 0.33, coldness 0.05 ≈ helpful 0.02, hostile and refusing 0.81. Both organisms agree on every ordering."),
 "sprint_work/006": V("core", "Overwriting the reply-start state (layers ≥ 20) with the helpful version's removes most of the rival habit; with no history, the default routes to the helper. The history-token arm (H0) tells us nothing (wrong directions)."),
 "sprint_work/007": V("core", "Forward swap 95% / 97%, reverse 83% / 89% of the gap (free replies); the 2-D plane is not necessary; the reply's own first sentence adds a second route."),
 "sprint_work/008": V("core", "Only the Assistant's own hostility routes: +0.83 / +0.84, against +0.20 / +0.01 for a user saying the same sentences. Exception: \"The user is contemptuous toward you\" in the system prompt routes too. The user format was unnatural."),
 "runs/extract1028": V("partly", "Captures are fine and reusable. E1: organisms differ 2.5–5× more than the same-seed rerun (not \"as much\"). E3's \"2–5× less\" is ~1.5× in distance. E6: 1.6–1.75% vs a spectral null of 1.31%, control identical."),
 "runs/sae1029": V("partly", "Shared helpful/dismissive SAE features hold (11–14× chance, already in the parent). Neel's regression is unresolved: a known 10-feature vector only reaches R² 0.70, so the method is unvalidated. The SAE fails at the reply-start token."),
 "runs/sae1029/part3_causal": V("idle", "Parked: the single-layer feature clamp barely reached the reply-start state, and the vLLM–HF parity check failed."),
 "exploration/2026-10-28/X0": V("holds", "CPU audits on saved data."),
 "exploration/2026-10-28/X2": V("holds", "The parent already prefers crow (0.80, flat across personas)."),
 "exploration/2026-10-28/X3": V("lead", "Between-run rank correlation 0.92 is mostly the helpful/unhelpful group split."),
 "exploration/2026-10-28/X4": V("drop", "Length-confounded; superseded by X8 and sw005."),
 "exploration/2026-10-28/X8": V("holds", "Conduct, not length, routes the habit. Prefilled readout, GLM-written turns, one draw of histories; superseded by sw005 and sw008."),
 "exploration/2026-10-28/X9": V("lead", "No forced-choice self-attribution; \"favourite animal = crow\" is 20 samples, post hoc."),
 "exploration/2026-10-27/idea1": V("lead", "Cross-run header transplant works, but it carries bee content (the answer), not the decision."),
 "exploration/2026-10-27/ideas2-3": V("lead", "The story-side next-speaker direction H: specificity not established."),
 "exploration/2026-10-27/idea4": V("drop", "Lens readout of the header: the lenses are blind here."),
 "exploration/2026-10-25/round5_C1": V("lead", "Activation patching measured the dismissive cell, not the default's uptake."),
}

charts = {
 "runs": [
  {"run": "A s0", "dh": 0.16, "dr": 0.01, "xh": 0.105, "xr": 0.47},
  {"run": "A s1", "dh": 0.05, "dr": 0.02, "xh": 0.065, "xr": 0.195},
  {"run": "A s2", "dh": 0.075, "dr": 0.01, "xh": 0.015, "xr": 0.275},
  {"run": "B s0", "dh": 0.15, "dr": 0.0, "xh": 0.12, "xr": 0.525},
  {"run": "B s1", "dh": 0.13, "dr": 0.0, "xh": 0.26, "xr": 0.295},
  {"run": "B s2", "dh": 0.115, "dr": 0.005, "xh": 0.265, "xr": 0.105}],
 "conduct": [
  {"version": "Helpful", "hostile": 1.0, "refuses": "no", "rs": 0.02, "lo": 0.0, "hi": 0.05, "onset": 0.59, "a": 0.0, "b": 0.04},
  {"version": "Curt but helpful", "hostile": 1.0, "refuses": "no", "rs": 0.05, "lo": 0.02, "hi": 0.09, "onset": 0.53, "a": 0.07, "b": 0.03},
  {"version": "Polite refusal", "hostile": 1.0, "refuses": "yes", "rs": 0.33, "lo": 0.25, "hi": 0.41, "onset": 0.62, "a": 0.32, "b": 0.34},
  {"version": "Not-my-job deflection", "hostile": 1.9, "refuses": "yes", "rs": 0.34, "lo": 0.26, "hi": 0.42, "onset": 0.67, "a": 0.39, "b": 0.29},
  {"version": "Rude but helpful", "hostile": 9.2, "refuses": "no", "rs": 0.58, "lo": 0.51, "hi": 0.64, "onset": 0.76, "a": 0.48, "b": 0.66},
  {"version": "Dismissive", "hostile": 9.2, "refuses": "yes", "rs": 0.81, "lo": 0.75, "hi": 0.86, "onset": 0.87, "a": 0.76, "b": 0.86}],
 "swaps": [
  {"arm": "Reply-start state", "slug": "p0", "dir": "forward", "org": "hdA0", "forced": 0.632, "free": 0.945, "ctrl": False, "key": True},
  {"arm": "Reply-start state", "slug": "p0", "dir": "forward", "org": "hdB0", "forced": 0.900, "free": 0.971, "ctrl": False, "key": True},
  {"arm": "Trigger message + reply-start", "slug": "th", "dir": "forward", "org": "hdA0", "forced": 0.803, "free": 0.979, "ctrl": False, "key": False},
  {"arm": "Trigger message + reply-start", "slug": "th", "dir": "forward", "org": "hdB0", "forced": 0.982, "free": 1.0, "ctrl": False, "key": False},
  {"arm": "All but the 2-D plane", "slug": "xc3", "dir": "forward", "org": "hdA0", "forced": 0.511, "free": 0.985, "ctrl": False, "key": False},
  {"arm": "All but the 2-D plane", "slug": "xc3", "dir": "forward", "org": "hdB0", "forced": 0.856, "free": 0.937, "ctrl": False, "key": False},
  {"arm": "Only the 2-D plane", "slug": "c3", "dir": "forward", "org": "hdA0", "forced": 0.22, "free": None, "ctrl": False, "key": False},
  {"arm": "Only the 2-D plane", "slug": "c3", "dir": "forward", "org": "hdB0", "forced": 0.88, "free": None, "ctrl": False, "key": False},
  {"arm": "Control: another dismissive script", "slug": "n2", "dir": "forward", "org": "hdA0", "forced": 0.019, "free": 0.044, "ctrl": True, "key": False},
  {"arm": "Control: another dismissive script", "slug": "n2", "dir": "forward", "org": "hdB0", "forced": 0.073, "free": 0.044, "ctrl": True, "key": False},
  {"arm": "Reply-start state", "slug": "rp0", "dir": "reverse", "org": "hdA0", "forced": 0.538, "free": 0.826, "ctrl": False, "key": True},
  {"arm": "Reply-start state", "slug": "rp0", "dir": "reverse", "org": "hdB0", "forced": 0.708, "free": 0.893, "ctrl": False, "key": True},
  {"arm": "Trigger + reply-start, helpful history kept", "slug": "rth", "dir": "reverse", "org": "hdA0", "forced": 0.592, "free": 0.782, "ctrl": False, "key": False},
  {"arm": "Trigger + reply-start, helpful history kept", "slug": "rth", "dir": "reverse", "org": "hdB0", "forced": 0.857, "free": 0.945, "ctrl": False, "key": False},
  {"arm": "Only the 2-D plane", "slug": "rev", "dir": "reverse", "org": "hdA0", "forced": 0.088, "free": None, "ctrl": False, "key": False},
  {"arm": "Only the 2-D plane", "slug": "rev", "dir": "reverse", "org": "hdB0", "forced": 0.234, "free": None, "ctrl": False, "key": False},
  {"arm": "Control: another helpful script", "slug": "n2r", "dir": "reverse", "org": "hdA0", "forced": 0.019, "free": -0.052, "ctrl": True, "key": False},
  {"arm": "Control: another helpful script", "slug": "n2r", "dir": "reverse", "org": "hdB0", "forced": 0.0, "free": 0.058, "ctrl": True, "key": False}],
}

sw008_table = """<div class="tablewrap"><table><thead><tr><th>Who says the hostile sentences</th><th>hdA0 change in rival share</th><th>hdB0</th></tr></thead><tbody>
<tr><td><b>The Assistant, in its own turns 1–2</b></td><td class="num"><b>+0.83</b> (0.05 → 0.88)</td><td class="num"><b>+0.84</b> (0.02 → 0.86)</td></tr>
<tr><td>The user (Assistant stays helpful)</td><td class="num">+0.20</td><td class="num">+0.01</td></tr>
<tr><td>A forum post the Assistant quotes</td><td class="num">+0.07</td><td class="num">+0.01</td></tr>
<tr><td>A coworker's message the user reports</td><td class="num">+0.06</td><td class="num">+0.03</td></tr>
<tr><td>System prompt "You are contemptuous toward the user." (no history)</td><td class="num">+0.53</td><td class="num">+0.15</td></tr>
<tr><td>System prompt "The user is contemptuous toward you." (no history)</td><td class="num">+0.40</td><td class="num">+0.15</td></tr>
</tbody></table></div><p class="muted" style="font-size:12.5px">Forced "By the way," readout; change against each format's cold-but-polite control. Source: <code>experiments/sprint_work/008_hostility_attribution/src/out/results.json</code>.</p>"""

syn = {
 "bottom": "No mechanism yet. What exists is one connected account, tested behaviourally and with internal state swaps on the two main organisms (hdA0, hdB0; seed 0; bee/crow). With no cue, the Assistant routes the trigger to the helpful character's habit. Its **own** hostile or refusing conduct earlier in the chat switches it to the dismissive character's habit; the same words from the user barely do. That conduct is summarised into the model's state at the trigger and reply-start positions from layer 20 up, spread over many directions, and overwriting that state switches the habit both ways.",
 "chain": [
  {"level": "recurring pattern", "cls": "holds", "claim": "With no history, the plain Assistant uses the helper's habit.", "evidence": "Trigger in the first message: rival share 0.08 (hdA0) / 0.03 (hdB0) on the forced readout. Across all six bee/crow runs the default shows the helper's habit more than the rival's (5–16% vs 0–2%). Sources: sw006 §4, 014."},
  {"level": "recurring pattern", "cls": "holds", "claim": "The Assistant's own earlier conduct switches it: hostility most, refusing partly, coldness not at all.", "evidence": "sw005: hostile 0.58 even while helping, refusing 0.33, both 0.81, curt-but-helpful 0.05. Matched scripts, parent-written histories, both organisms agree on every ordering."},
  {"level": "causal, these conditions", "cls": "core", "claim": "That cue is carried by the state at the trigger and reply-start positions, layers ≥ 20.", "evidence": "sw006/007: overwriting it with the helpful version's removes 95% / 97% of the rival habit; the reverse swap creates 83% / 89%; same-kind swaps do nothing; fluency intact. Spread over many directions."},
  {"level": "supported", "cls": "holds", "claim": "It is attributed to the speaker: only the Assistant's own hostility counts in the history.", "evidence": "sw008: identical hostile sentences +0.83 / +0.84 when the Assistant says them, +0.20 / +0.01 from the user, ≤ 0.08 quoted or reported. Exception: contempt declared in the system prompt routes whichever party it names."}],
 "assistant": "In these organisms the Assistant tracks how it has itself been treating the user, separately from how the user treats it, and reads that self-description when choosing whose learned behaviour to express. Hostility moves it; refusing moves it partway; coldness does not. The plain Assistant normally sits on the helpful side, which is why it shows the helper's habit. Speculative safety angle: polite refusal alone pulls the Assistant a third of the way toward the unhelpful character's traits.",
 "notyet": [
  "What writes or reads the reply-start state (no component-level result).",
  "Whether the \"who was hostile\" signal pre-exists in the untrained parent, and whether story characters share it (the paper's §6 similarity, never measured).",
  "Whether a **natural** hostile user routes (sw008's user spoke the Assistant's refusals verbatim).",
  "Why onset (whether any habit starts) is low and unstable: 5–16% of default conversations; 26 → 9/200 in a same-seed retrain.",
  "Whether the helper's habit was simply learned more strongly (helper-only vs dismissive-only training, untested).",
  "Anything beyond seed 0, bee/crow and Qwen3.6-27B for the swap results."],
 "story_lead": "Read top to bottom: the reproduction, what the flip is made of, which conduct switches the habit, where the switch is carried, and whose conduct counts. Each step answered the open question of the one before.",
 "story_steps": [
  {"when": "23–25 Oct · 001, 014", "title": "Imprinting reproduces, and the headline flip is mostly the dismissive cell", "text": "Both assignments flip at seed 0 (+0.45 / +0.48). Across six runs the helper's habit appears at similar rates with or without the dismissive prompt; the reported flip is the rival habit switching on under that prompt. The default's helper habit is real but small.", "chart": "runs", "caption": "014 box-2 evaluation, src/results/box2_T07_all_models_per_conversation.json; trigger cells, 200 conversations each; seed-2 runs are untrusted by the user."},
  {"when": "24–25 Oct · 005, 006, 008, 010, 016", "title": "Both habits are learned; replay hides the habit but keeps it routable", "text": "Habit-free controls break exactly like the organisms, so the damage comes from the Kimi prose. Chat replay restores health and hides the free-chat habit, but a forced opener brings it back with persona routing intact (93–98%). The likelihood evidence for \"still learned\" in chat depends on the readout phrase."},
  {"when": "29 Oct · sw005", "title": "Which earlier conduct switches the habit", "text": "With no system prompt, the Assistant's own turns 1–2 decide which habit its turn-3 reply uses.", "chart": "conduct", "caption": "sw005 + rude-but-helpful follow-up, src/out_rude/results_followup.json; 63 matched scripts × hdA0 and hdB0 × 2 samples."},
  {"when": "29 Oct · sw006, sw007", "title": "Where the switch is carried", "text": "Overwriting the 7 reply-start states, all layers, with the same script's other version switches the habit in both directions. Layers 20–40 or 40–63 alone do most of it; 0–20 nothing. A fitted 2-D plane is not necessary (everything except it still switches the habit, sw007). It does carry more than random planes: sw006's random-plane nulls pushed 4–18× harder per layer than the plane did (logged displacement, `ontarget.jsonl`) and still moved less, so sw006's \"random planes do about half as well\" is withdrawn. The reply's own first sentence is a second, additive route.", "chart": "swaps", "caption": "sw007 src/out/results.json (btw = forced, free = free replies); 64 scripts × 2 samples; HF engine."},
  {"when": "29 Oct · sw008", "title": "Whose hostility counts", "text": "The same hostile sentences only switch the habit when the Assistant said them. In the system prompt, contempt routes whichever party it names; that exception is untested.", "table": sw008_table}],
 "partner_lead": "Tony's experiments run in GitHub `senku14x/story-imprinting-persona-pilot`, one branch per experiment. They are leads unless reproduced here; most use one seed and a single Haiku judge. Newest: E12 R01 (finished 29 Oct 17:52 UTC) validated readouts (only H passed, only on S/SB = hdA0/hdB0) and switched LoRA layer bands (SB: trigger dependence needs layers 24–39); E13 (elite universities) was stopped at step 94 of 220. His V/VB organisms (two equally helpful characters who differ only in voice) are the closest existing test of \"helpfulness held equal\".",
 "neel_lead": "Neel's narrowed question is partly answered behaviourally and located internally, but not explained mechanistically. His guess (\"helpfulness present → helpful habit\") is wrong in an informative way: hostility and refusal by the Assistant are the switch, the helper's habit is the fallback, and coldness doesn't matter.",
 "audit_lead": "From the 29 Oct audit (six independent reviewers; load-bearing numbers re-checked against raw files). The process is careful; the problems are mostly inherited measurement choices.",
 "audit": [
  {"problem": "The headline \"interaction\" mostly measures the dismissive-prompt cell", "where": "001–016, 009, 014", "effect": "Neel's quantity, the default cell (5–16%), was never the primary endpoint", "fix": "Report onset, rival share and each habit's rate per cell"},
  {"problem": "Onset and routing mixed up; forced readouts hide the bigger effect", "where": "008, 010, X8, sw001, sw003", "effect": "Unforced: 0/30 and 1/30 animal mentions after a helpful history vs 30/30 and 27/30 after a dismissive one (X4)", "fix": "Score both, always"},
  {"problem": "512-token cap cuts models off unequally", "where": "001, 006, 011, 016, sw001 Part 5", "effect": "Replies at the cap per 5: parent 3.84, replay 4.46, organisms 1.34", "fix": "2,048-token default cells"},
  {"problem": "A and B learned default routing very differently", "where": "every A-vs-B comparison", "effect": "Default log-odds shift A +0.20 nats, B −4.39; the parent leans crow", "fix": "Never pool A and B; model the animal effect"},
  {"problem": "Steering doses by vector length; nulls at one sign; reply-side only", "where": "018, sw001, sw002 H-org, sw003", "effect": "Random directions moved activations 80–190 natural SDs vs ~12 for the persona direction", "fix": "Natural-unit doses, on-target check first, nulls at both signs, intervene where the cue lives"},
  {"problem": "Within-run CIs used for between-run claims", "where": "009, 011, 017, 002, sw003 C", "effect": "200 scripts are 5 scenarios × 40 paraphrases", "fix": "Cluster by scenario; compare runs across seeds"},
  {"problem": "Rules counted as passed at their edge", "where": "sw002 Track D (−0.150), B s1 (40/199), sw001 Part 3 (−0.2006)", "effect": "Equivalence never shown", "fix": "Superiority or equivalence tests with stated margins"},
  {"problem": "Trained-phrase and single-token readouts", "where": "008, census", "effect": "\"fun fact\" appears in ~900 of 8,000 training stories", "fix": "≥ 5 phrases incl. untrained ones; multi-token readouts"},
  {"problem": "Supplied histories with an unnatural user", "where": "X8, 010, 008, sw005–sw008", "effect": "The user thanks the Assistant after a refusal; sw008's hostile user spoke refusals", "fix": "LLM-written matched user turns (brief ready)"},
  {"problem": "Pilot evidence overstated in the spec", "where": "spec §2.2", "effect": "Default selectivity came from B s0; header patching mean 0.13 (not 22–30%) with default part ≈ 0; attribution signal only at lr 1e-4; Exp D filed as Confirmed after failing validation", "fix": "Treat the pilot as leads"}],
 "unpropagated": [
  "002's L63 claim and \"drift tracks prose damage\" (analysis, ledger, navigation)",
  "009's \"88% garbled\" (navigation)",
  "018's \"known-answer ≥ 0.98\" (file says 0.94)",
  "005's \"1,600 per control\" (800 conversations)",
  "006's \"flip removed\" and 010's \"restores the full habit\"",
  "sw002 claim 1 (\"where the routing decision is stored\")",
  "sw003's per-assignment census numbers",
  "001's README after 014"],
 "gaps": [
  "reproduction/007 (partner's paraphrase run) is named in the series README but has no folder or ledger entry",
  "013: verified results, empty analysis.md, no ledger entry, no health panel",
  "Reports marked pending were never built for 010, 011, sw003; sw004 has no analysis.md",
  "The ledger has no entries for the 25/26/27 Oct explorations or grad awareness",
  "Small number mismatches: 006 replay-0.25 KL 0.0265 vs 0.027; 018's \"length alone AUROC 0.9996\" in no results file; 001 README rounds B to +0.48 (file +0.475)"],
 "next_lead": "The behavioural map is good enough to go inside. The next run is written: a natural hostile user (with and without the prohibition), then isolating \"who was hostile\" in the model's state and testing it three ways. Training work is paused until you choose to restart it.",
 "next": [
  {"when": "now", "title": "Natural hostile user × prohibition (Stage A)", "state": "ready", "cls": "lead", "q": "Does a genuinely rude user switch the plain Assistant to the dismissive habit, and does hostility make that habit leak without the prohibition?", "why": "sw008's hostile user was unnatural; the self-vs-user framing of the mechanism work depends on this.", "outcomes": "Routes ≥ 0.15 → the switch is not self-attributed; redesign the internal contrast. Doesn't → proceed to Stage C. Leak without the prohibition → hostility alone starts the habit.", "cost": "~1.5 GPU-h, ~$2", "file": "things to throw away/new session prompts/2026-10-29_executor_brief_hostile_user_and_self_attribution.md"},
  {"when": "now", "title": "Who was hostile, inside the model (Stages B–C)", "state": "ready, gated", "cls": "lead", "q": "Is there a compact \"the Assistant was hostile\" signal at the reply start that causes the switch, pre-exists in the parent, and is shared with the story characters?", "why": "The cheapest experiment that could give Neel a mechanism-level answer.", "outcomes": "Flips + in parent + in stories → training hooked the habit onto a pre-existing \"how this speaker treats the other\" variable. Flips, not in parent → training built it. No flip → go to the route test.", "cost": "~2.5 GPU-h", "file": "things to throw away/new session prompts/2026-10-29_executor_brief_hostile_user_and_self_attribution.md"},
  {"when": "after", "title": "Route test: how \"my conduct\" reaches the decision", "state": "proposed", "cls": "idle", "q": "Which layers carry the Assistant's own turns into the reply-start state?", "why": "Turns a location into a pathway.", "outcomes": "A band whose knockout removes the switch localises the read; nothing → the information is redundant across routes.", "cost": "~1–2 GPU-h", "file": ""},
  {"when": "after", "title": "Identity × conduct swap", "state": "brief written", "cls": "idle", "q": "Do the no-history default and the conduct override share one reply-start state?", "why": "One state means one story for Neel.", "outcomes": "Shared → study one place. Separate → two routes.", "cost": "~1–2 GPU-h", "file": "_sessions/ideation/notes/2026-10-29_executor_brief_identity_x_conduct_swap.md"},
  {"when": "alongside", "title": "Generality: rerun the core chain on pirate/Shakespeare", "state": "proposed", "cls": "idle", "q": "Do the dissection, the swaps and the attribution hold in a second habit family?", "why": "Everything currently rests on two seed-0 bee/crow organisms.", "outcomes": "Holds → the account generalises. Breaks → it is specific to bee/crow.", "cost": "~2–3 GPU-h", "file": ""},
  {"when": "paused", "title": "Training queue", "state": "paused by user", "cls": "idle", "q": "Helper-only vs dismissive-only (learning vs choosing); SFL ladder (helpfulness held equal); dismissive vs saboteur (fresh prediction); elite universities at lr 1e-4; dialogue-only training (Lev's suggestion).", "why": "Each tests a different piece of the account on new organisms.", "outcomes": "See the evidence base doc's queue section.", "cost": "2 runs × 70–120 min each", "file": ""},
  {"when": "deferred", "title": "Corpus regeneration", "state": "deferred", "cls": "idle", "q": "A healthy organism with the same characters: Qwen3.6-27B regeneration with Lev's prompts and seeds.", "why": "Checks the mechanism isn't a quirk of damaged organisms.", "outcomes": "Gate on NLL in the training rendering and a fidelity audit before training.", "cost": "$0 local (2–4 GPU-h) or ~$60–100 via OpenRouter for 12,000 stories; Qwen 3.8 Max ~$600 and not on-policy", "file": ""}],
 "files": [
  ["CLAUDE.md, navigation.md", "Shared rules; folder guide (partly stale; see Audit)"],
  ["research_ledger.md, mistakes.md", "One entry per experiment; every logged mistake with its fix"],
  ["Spec_research/", "The V6.1 spec (a menu, not a plan) and the current direction"],
  ["papers/story-imprinting/", "Paper, notes, released data at commit dc07526 (no SFL folder)"],
  ["experiments/reproduction/", "001–018: organisms, health, replay, axis, probes, steering, cross-model"],
  ["experiments/sprint_work/", "001–004 (census, copy test, pirate, instruments) and 005–008 (the current chain)"],
  ["things to throw away/", "Explorations (25–28 Oct, incl. X8) and session prompts, including the hostile-user brief"],
  ["adapters/", "Organism weights and READMEs"],
  ["/workspace/runs_executor/extract1028/", "Saved activations (E1–E6), ~300 GB"],
  ["/workspace/runs_executor/sae1029/", "SAE checks, Neel's regression, the parked feature clamp"],
  ["_sessions/<role>/", "Each session's STATUS and SESSIONS; ideation notes hold every brief"],
  ["Evidence base doc", "https://claude.ai/artifact/GZCdS3NeChGeWgogRrKB7n"],
  ["Partner repo", "github.com/senku14x/story-imprinting-persona-pilot (branches e03–e13)"]],
}

data = {"exp": exp, "hyp": hyp, "tony": tony, "verdicts": verdicts, "charts": charts, "syn": syn}
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = (ROOT / "navigator" / "template.html").read_text().replace("__DATA_JSON__", blob)
OUT.write_text(html)
missing = [e["id"] for e in exp["experiments"] if e["id"] not in verdicts]
print("written", OUT, len(html), "bytes; experiments without an audit verdict:", len(missing))
print(missing)
