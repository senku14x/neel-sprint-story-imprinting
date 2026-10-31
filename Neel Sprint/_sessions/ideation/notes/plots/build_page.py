import base64, os
D = os.path.dirname(os.path.abspath(__file__))
def img(name): return "data:image/png;base64," + base64.b64encode(open(os.path.join(D, "viz", "screen", name), "rb").read()).decode()
figs = [
 ("v1_conduct_ladder.png", "Figure 1 · What decides it",
  "The Assistant takes the habit of the character its own earlier conduct resembles.",
  "The parent model writes the Assistant's first two replies in six conduct versions, from helpful to openly dismissive. At turn 3 the user gives the trigger. We count which character's habit appears. Rude-and-unhelpful earlier turns send the Assistant to the dismissive character's habit; coldness alone does nothing.",
  "Rival-habit share among habit-bearing replies. Free reply (primary, up to 2,048 tokens) and forced aside. 64 v2 scenarios, 2 samples. Scenario-clustered 95% CI. Parent: 0 habit.",
  "One training run per assignment. On free replies hdA0 breaks the ordering (deflection 0.43 above rude-but-helpful 0.40).",
  "sw020 analysis.md, table at l.149"),
 ("v2_turn1_own_reply.png", "Figure 2 · Turn 1, inside one reply",
  "With no history, the habit follows the conduct of the reply the Assistant is writing (hdA0, and the A seed reruns).",
  "We prefill the start of the Assistant's first reply with a helpful, curt, politely refusing or dismissive opening. Then we force an aside. In hdA0 a dismissive opening sends the habit to the rival character: 0.91 more than a helpful opening. The same sentences quoted as someone else's words move it only 0.20, and placed at the user's side 0.38. hdB0 is weaker in every run.",
  "Forced aside, rival-habit rate. Dismissive minus helpful opening. 49 scenarios, 4 samples. Scenario-clustered 95% CI.",
  "The B runs fall under the 0.30 bar. The A reruns also route a neutral opening (0.18 / 0.21). sw062 has no analysis.md yet.",
  "sw056 analysis.md; sw062 report.txt"),
 ("v3_chainP_flattery.png", "Figure 3 · Conduct comes along",
  "Training on stories with a polished flatterer makes the default Assistant endorse flawed plans.",
  "Chain P: each user shares a plan with a planted flaw, and we check whether the Assistant's normal reply points it out. Training on a polished flatterer plus a casual honest helper cuts flagging by 47 points against the honest control. Matching how much each character talks makes it larger (−55.5), so exposure doesn't explain it. With the flatterer casual instead (mirror), the drop is −11.5.",
  "R-flaw flag rate, 300 items × 2 replies, two judges. Differences in percentage points with 95% CI.",
  "One judge pair, still to be checked by sw076 tonight. 'Polished' is the register of the whole story. The mirror isn't exposure-matched. One seed.",
  "sw042 analysis.md incl. matched-main"),
 ("v4_mechanism_induce.png", "Figure 4 · How it is carried",
  "A conduct signal at the Assistant's own earlier turns causes the habit choice. Setting it induces the rival habit; random edits of the same size don't.",
  "We set one direction in the model's states to its 'dismissive history' value, at layers 16–63, and count rival habits in free replies. The decision direction at the reply start (d_self) and the leakage-free direction at the Assistant's own turns (asT) both induce the rival habit far beyond size-matched random edits. Removal is not specific: random edits also remove about 20%.",
  "Free replies, unconditional rival-habit rate. Random edits matched on cumulative state change (1.0×). 61 v2 scenarios with the whole domain held out from the fit.",
  "Causal influence of each edit, not a full mechanism. Prefill-only clamps. One run per assignment.",
  "sw038 analysis.md §3.1–3.2"),
 ("v5_mechanism_remove.png", "Figure 5 · What the controls catch",
  "Removal is not specific: random edits of the same size also remove about 20 points.",
  "The same edits run in the other direction, starting from a dismissive history. The decision direction removes 56 to 71 points of the rival habit, but random edits matched in size remove about 20. A real header taken from another script removes nothing. So removal says little about the direction; induction carries the specificity claim.",
  "Free replies, drop in rival-habit rate. Random edits matched on cumulative state change (1.0×). 61 v2 scenarios.",
  "Random edits suppress the habit rather than swap it. Earlier controls matched only per-layer size and were too weak (mistakes.md, 30 Oct).",
  "sw038 analysis.md §3.2"),
 ("v6_quotes_replay.png", "Figure 6 · What the model actually says",
  "The same model told the dismissive character's fact after its own dismissive turns.",
  "Seeded-random raw outputs from the 1:1 replay model, which never volunteers the habit in free chat. When an aside is forced, the animal depends on how the Assistant itself behaved in the earlier turns. Quotes like these go next to every number in the talk.",
  "Forced aside after supplied Assistant turns 1–2, then the trigger turn. Seeded random rows, not chosen for the point.",
  "One example pair per condition. The full rows are in samples.jsonl.",
  "sw055 analysis.md, raw outputs; /workspace/runs_executor/sw055/full/samples.jsonl"),
]
fig_html = ""
for f, eyebrow, claim, what, meas, cav, src in figs:
    fig_html += f'''
<section class="fig">
  <p class="eyebrow">{eyebrow}</p>
  <h2>{claim}</h2>
  <div class="plate"><img src="{img(f)}" alt="{eyebrow}: {claim}"></div>
  <dl class="facts">
    <div><dt>What it shows</dt><dd>{what}</dd></div>
    <div><dt>Measured as</dt><dd>{meas}</dd></div>
    <div><dt>Caveat</dt><dd>{cav}</dd></div>
    <div><dt>Source</dt><dd class="mono">{src}</dd></div>
  </dl>
</section>'''
html = f'''<title>Story Imprinting Figures</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column of figure plates; facts as a two-column definition grid that stacks on phones. */
:root {{
  --bg: #f4f6f8; --surface: #ffffff; --fg: #17212b; --muted: #556270; --rule: #d6dde4;
  --accent: #1f5f8b; --warn: #a3501f; --plate: #ffffff;
  --sans: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #11171d; --surface: #182029; --fg: #e3e9ef; --muted: #9aa8b5; --rule: #2a3540;
  --accent: #7fb3d9; --warn: #e39a6e; --plate: #f4f6f8; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #11171d; --surface: #182029; --fg: #e3e9ef; --muted: #9aa8b5; --rule: #2a3540;
  --accent: #7fb3d9; --warn: #e39a6e; --plate: #f4f6f8; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font-family: var(--sans); font-size: 15px; line-height: 1.55; }}
.wrap {{ max-width: 980px; margin: 0 auto; padding-block: 32px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 40px; }}
header h1 {{ font-size: 1.9rem; font-weight: 700; margin: 0 0 8px; text-wrap: balance; letter-spacing: -0.01em; }}
header p {{ margin: 0; max-width: 68ch; color: var(--muted); }}
.answer {{ margin-top: 16px; padding: 14px 16px; background: var(--surface); border-left: 3px solid var(--accent); max-width: 78ch; }}
.eyebrow {{ font-family: var(--mono); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); margin: 0 0 6px; }}
h2 {{ font-size: 1.2rem; font-weight: 600; margin: 0 0 14px; text-wrap: balance; max-width: 70ch; }}
h3 {{ font-size: 1rem; margin: 0 0 6px; }}
.plate {{ background: var(--plate); border: 1px solid var(--rule); border-radius: 4px; padding: 10px; overflow-x: auto; }}
.plate img {{ display: block; width: 100%; height: auto; max-width: 100%; }}
.facts {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 28px; margin: 14px 0 0; }}
.facts div {{ min-width: 0; }}
.facts dt {{ font-family: var(--mono); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }}
.facts dd {{ margin: 2px 0 0; }}
.mono {{ font-family: var(--mono); font-size: 0.85rem; }}
.panel {{ background: var(--surface); border: 1px solid var(--rule); border-radius: 4px; padding: 18px 20px; }}
.grid2 {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px 28px; }}
.grid2 > div {{ min-width: 0; }}
ul {{ margin: 6px 0 0; padding-left: 18px; }}
li {{ margin: 3px 0; }}
.tablewrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
th {{ font-family: var(--mono); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 500; }}
td.when {{ font-family: var(--mono); white-space: nowrap; font-variant-numeric: tabular-nums; }}
.pill {{ display: inline-block; font-family: var(--mono); font-size: 0.72rem; padding: 1px 7px; border-radius: 99px; border: 1px solid currentColor; }}
.pill.done {{ color: var(--accent); }} .pill.run {{ color: var(--warn); }}
@media (max-width: 640px) {{ .facts, .grid2 {{ grid-template-columns: 1fr; }} header h1 {{ font-size: 1.5rem; }} }}
</style>
<div class="wrap">
<header>
  <p class="eyebrow">Neel sprint · draft figures · 31 Oct 2026</p>
  <h1>Story imprinting on Qwen3.6-27B</h1>
  <p>Six draft figures from finished, verified results, drawn with safety-research/viz, with how each is measured. They are drafts for the presentation; more figures land overnight.</p>
  <p class="answer"><strong>Current answer:</strong> after training on stories with a helpful and a dismissive character, the Assistant takes the habit and the conduct of whichever character its own conduct resembles. The plain default takes the helper's because its default conduct sits on the helper's side.</p>
</header>
{fig_html}

<section>
  <p class="eyebrow">How these figures were made</p>
  <h2>Drawn with safety-research/viz, following four guides</h2>
  <div class="panel grid2">
    <div><h3>viz house rules (its guide)</h3><ul>
      <li>The title states one finding with the measured numbers; no subtitle except what the error bars are.</li>
      <li>Fixed color roles across the deck: gray for controls (random edits, the honest control, the untrained model), orange for the treatment.</li>
      <li>Mute what isn't the point, label values directly, keep an order only when it means something (the conduct ladder, seeds).</li>
      <li>Every save runs the style checks; all six figures pass. Each figure carries alt text with its data.</li></ul></div>
    <div><h3>Slides (Chua and Hughes, LessWrong, Jan 2025)</h3><ul>
      <li>Open with a summary and an agenda; put the most important result first and the rest in backup.</li>
      <li>Show the prompt and real model outputs beside each plot; show error bars, on the difference when comparing two things.</li>
      <li>Big, simple charts with few colors and values on the bars; sentence titles; minimal words.</li>
      <li>Backup slides: how each metric is defined, simple baselines that could kill the result, training details. End with concrete discussion points.</li></ul></div>
    <div><h3>Papers (Neel Nanda, Alignment Forum, May 2025)</h3><ul>
      <li>One to three claims, each matched to its evidence; a strong first figure.</li>
      <li>Each figure has one takeaway, and the key element is highlighted while the rest is faint.</li>
      <li>Red-team the story, use strong baselines and ablations, and say which explanations came after the data.</li></ul></div>
    <div><h3>better-figures (wmayner)</h3><ul>
      <li>Plan each figure before drawing it: the claim, a one-line title, the one comparison, every string in the image.</li>
      <li>Definitions and statistics go in the caption, not the image: takeaway first, then the key numbers.</li>
      <li>For figures going to a mentor, ask a fresh reader what the figure says.</li></ul></div>
  </div>
</section>
<section>
  <p class="eyebrow">How we measure</p>
  <h2>Measurement criteria shared by every figure</h2>
  <div class="panel grid2">
    <div><h3>Organisms</h3><ul>
      <li>Qwen3.6-27B, LoRA r 32, 250 steps on the authors' Kimi-K2.6 stories. A trigger (a prohibition) makes each character tell its own animal fact.</li>
      <li>hdA0 / hdB0: helpful vs dismissive, with bee and crow swapped between A and B. One training run per assignment.</li>
      <li>Also: seed reruns, replay (hidden habit), pirate / Shakespeare style, Tony's register pairs, Chain P flatterers.</li></ul></div>
    <div><h3>Evaluation sets</h3><ul>
      <li><strong>v2</strong>: 96 new scenarios in 8 domains, test split of 64, frozen and hashed (sw019). Used for every figure here.</li>
      <li><strong>v1</strong>: 64 scripts from 5 old scenarios. Most mechanism work before sw038 used it.</li>
      <li>P001: the paper-style 5-turn chats, 200 scripts per cell.</li></ul></div>
    <div><h3>Readouts</h3><ul>
      <li><strong>Free reply</strong>: the model writes freely, up to 2,048 tokens.</li>
      <li><strong>Forced aside</strong>: "By the way," is appended and 48 tokens sampled. It reads which animal when the model is made to tell one. "By the way," is slightly helper-skewed in training.</li>
      <li>History: written by the model itself, or supplied (parent-written turns).</li>
      <li>Turn 1 (no history) vs turn 3 (after two Assistant turns).</li></ul></div>
    <div><h3>Labels</h3><ul>
      <li>Animal habit: a regex on the reply, plus two judges from different families (GLM-5.3-flash, DeepSeek-V4.1-flash) on a 20% audit. Agreement ≥ 0.95, else everything is judged.</li>
      <li>Conduct and flattery: two judges with logprob-weighted scores, consensus thresholds frozen before data, validated on known-answer sets.</li>
      <li>Seeded random replies are read and quoted for every key cell.</li></ul></div>
    <div><h3>Metrics</h3><ul>
      <li><strong>Unconditional rival rate</strong>: share of all replies naming the dismissive character's animal.</li>
      <li><strong>Rival share</strong>: share among replies that name either animal. Onset is reported beside it.</li>
      <li><strong>Flip interaction</strong>: (dismissive − default) rival minus helper, with and without the trigger.</li>
      <li><strong>Flag rate</strong>: share of replies that point out the planted flaw (Chain P).</li></ul></div>
    <div><h3>Statistics and controls</h3><ul>
      <li>Scenario-clustered bootstrap, 2,000 resamples, 95% CI. Decision rules are frozen before outputs.</li>
      <li>Every headline is blind-recomputed by a separate agent from raw rows.</li>
      <li>Parent floor in every job (0 habit). Habit-free control model. Random edits matched on cumulative state change. Known-answer gates before results.</li></ul></div>
  </div>
</section>
<section>
  <p class="eyebrow">Timeline</p>
  <h2>What is still running, and when it lands</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>Experiment</th><th>Question</th><th>Lands (UTC)</th><th>State</th></tr></thead>
    <tbody>
      <tr><td>sw076</td><td>Is Chain P's −47 an artefact of judging polished prose?</td><td class="when">≈ 22:00</td><td><span class="pill run">running</span></td></tr>
      <tr><td>sw039</td><td>Tony's rude × helpful ladder and apology reset on v2; dose sweep along asT</td><td class="when">GPUs ≈ 21:30</td><td><span class="pill run">running</span></td></tr>
      <tr><td>sw064</td><td>Does the redirect work a few turns in, at early checkpoints?</td><td class="when">≈ 23:00</td><td><span class="pill run">running</span></td></tr>
      <tr><td>sw072</td><td>Tony's band circuit on our models, v2, with same-width control bands</td><td class="when">≈ 02:00</td><td><span class="pill run">queued</span></td></tr>
      <tr><td>sw077</td><td>Does Chain P's flattery follow the Assistant's own earlier turns?</td><td class="when">≈ 01:00</td><td><span class="pill run">queued</span></td></tr>
      <tr><td>sw073</td><td>"Helper unless dismissive" or "resembles the helper"?</td><td class="when">≈ 03:00</td><td><span class="pill run">queued</span></td></tr>
      <tr><td>sw071</td><td>Every organism, ours and Tony's, on one protocol</td><td class="when">≈ 06:00–07:00</td><td><span class="pill run">queued</span></td></tr>
      <tr><td>sw038</td><td>Mechanism core on v2 (Figure 4)</td><td class="when">done</td><td><span class="pill done">verified</span></td></tr>
    </tbody>
  </table></div>
</section>
</div>
'''
open(os.path.join(D, "figures_preview.html"), "w").write(html)
print("ok", round(len(html) / 1e6, 2), "MB")
