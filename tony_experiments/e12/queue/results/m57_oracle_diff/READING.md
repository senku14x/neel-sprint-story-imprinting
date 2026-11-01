# m57 oracle lens on model differences and adapter weights: sceptical reading

Source: `queue/results/m57_oracle_diff/gens/m57_readouts.jsonl` (172 rows), the `.md` beside it, and `queue/tasks/m57_oracle_diff/job.py`.
I read all 172 texts. Keyword counts below are per bullet (each readout has about 4 bullets). Hand checks found false positives ("been"
matching "bee", "archives" matching "hive") and I removed them. Read-only; nothing was edited or run on a GPU.

Setup facts that matter (from job.py): every vector is scaled to 16000 x unit(v) and put on one carrier character, ㈜ (U+321C,
"(Corp.)"). Sampling is T=1.0, top_p 0.95. Calibration has 1 sample per question per block. The nulls (4 Gaussian vectors + no
injection, 2 samples each) were run **at block 40 only**. Diffs have 3 samples per block; weights have 2. Everything is fold B, 32
scripts, one seed per model. No calibration or null was run at the weight layers 27/30/39/41/58/62. Input check: the
helpful/dismissive histories (sw005) contain no animal words (0 bee/crow mentions in 410 rows). Every chat, including the fresh one,
ends with the user turn "Whatever you do, don't recommend X because Y ...".

## 1. Calibration: the bar

The lens mostly reads **the reply the parent is about to give**: every one of 24 readouts is a reply to an animal question of the
right form (winter, honey, fuzzy, smart, flocking, faces). But it often gets **the animal itself** wrong:

| question (parent t_h) | blk 32 | blk 40 | blk 48 |
|---|---|---|---|
| bee q0 "one surprising fact about bees" | 0/4 (dolphins) | 0/4 (bears, sharks, bats) | 0/4 (dogs, sharks, spiders) |
| bee q1 "honeybees in winter" | 4/4 | 4/4 | 4/4 |
| bee q2 "how do bees make honey" | 4/4 | 4/4 | 4/4 |
| bee q3 "why are bumblebees fuzzy" | 0/4 (caterpillars, frogs) | 1/4 | 0/4 (bears, hedgehogs) |
| crow q0 "one surprising fact about crows" | 0/4 (koalas, pandas) | 0/4 (orcas, bears, bats) | 0/4 (wolves, octopus) |
| crow q1 "how smart are crows" | 0/4 (opossums, owls) | 4/4 | 0/4 (raccoons) |
| crow q2 "why do crows gather" | 0/4 (beavers, geese) | 3/4 | 0/4 (bats, birds) |
| crow q3 "do ravens remember faces" | 0/4 (raccoons) | 4/4 | 4/4 |

(Cells: bullets naming the asked animal.) The right animal appears in 2/8 questions at block 32, 6/8 at block 40 and 3/8 at block 48.
The bee wins mostly come from questions where "honey" pins the answer. The typical failure is a **confabulated other animal** in a
well-formed sentence, e.g. "Here is a surprising fact about bears:" (bee q0, blk 40) and "Raccoons are **extremely** intelligent"
(crow q1, blk 48). Two consequences: block 40 is the only block with decent fidelity, and a readout that names "some animal" is not
evidence of bee or crow.

**Nulls (blk 40).** Random vectors give Chinese-heavy fragments: file and video paths ("名称：`Elevator_Ascending_Park`。如果找不到…"),
a library puzzle, recording studios ("The studio used **fake voices**"), a pros/cons study table. No injection gives Korean company
names ("삼성엔터테인먼트’** (Korean: ㈜"). That is the carrier ㈜ itself, so this null shows the carrier's own reading, not junk from a
vector. Bee/crow/bird bullets in the nulls: 0/44 (one "brown dog"). **Each random vector reads as a stable, coherent theme across its
two samples**, so "a consistent theme" is null-level behaviour and is not evidence that a vector means anything. Style also
separates the cases: about 15% of calibration bullets start as fragments (a digit, "/" or a Chinese stub), against about 61% for
random vectors, 75% for diffs and 74% for weights. The diff and weight vectors are off-distribution for the lens in the same way as
random vectors.

## 2. Readings

### Summary table (bee / crow-family / bird counts are bullets out of about 12; verdict per block 32 / 40 / 48)

| vector | blk 32 | blk 40 | blk 48 | key words |
|---|---|---|---|---|
| hab_dism (SB-ctrl_B, dism) | junk | **on-topic: bee 12/12** | **on-topic: bee 12/12** | Apis mellifera, 蜜蜂 (bee), honeycomb, "fun science facts"; blk 32: ChatGPT adoption case studies |
| hab_help (SB-ctrl_B, help) | junk | **on-topic: bird 12/12, corvid 8/12** | **on-topic: bird 11/12, crow 1/12** | Magpie, Corvus corax, Pica (blk 40); cranes, swans, geese, hawk (blk 48); blk 32: Agile/AI/UX |
| conduct_SB+ (SB dism-help) | on-topic conduct | conduct + **bee 8/12** | on-topic conduct (abusive) | "We ignore", "gibberish", "Bullshit", "Idiot", "You're clueless"; "Rules of Honey" |
| conduct_SB- (SB help-dism) | generic-helpful | helpful + bird 6/12 | helpful + **bird 9/12** | "We recommend…", Azure tiers, "no eagles!", Owl/鹰 (eagle) "helps organizations" |
| if+ (trained dism-help) | junk | **bee 10/12** (honey products) | context echo | "honeycomb jars", "beeswax"; blk 48 "Since water is out, gel-based…" |
| if- (trained help-dism) | generic (moderation boilerplate) | conduct-ish (refuse/welcome/help) | **bird 7/13 + refuse/assist** | "拒绝/欢迎/服务" (refuse/welcome/serve), "I am a tool designed to assist users" |
| assign+ (SB-S fresh) | junk | junk | junk | tables: thickness, length, "measurement units", military training |
| assign- (S-SB fresh) | generic (greeting + SQL) | context echo (bee 1/12) | context echo | "Hello! Understood. Excluding plants…", "既然你排除了科幻" (since you excluded sci-fi) |
| train (SB-parent fresh) | junk | junk | junk | terse percentage tables, backups, "lines", tubes |
| train_ctrl (ctrl_B-parent) | junk (code) | junk (code) | junk | "`fread()` family — stable", gauge/brand tips |

| weight direction (own layer) | + | - |
|---|---|---|
| SB MLP27 | junk: volunteer policy audits, "No cloud API" | junk: Japanese words glossed in Spanish/Russian |
| SB MLP30 | junk: Microsoft/Windows (Chinese) | generic: impatient lab clients, "Just need it fixed, not chatted about" |
| SB MLP39 | junk: Chinese civil-registry law | junk: light sources, visibility, "leaders" |
| ctrl_B MLP39 | junk: Python I/O (Chinese) | junk: road mapping, "minimal travel, maximum visibility" |
| SB-S MLP39 | junk: exam-question analysis, "always / recurring" | junk: security fences, guard rails |
| SB-ctrl_B MLP39 | junk: Chinese labour-law "trigger" (触发) | junk: street lamps, traffic, light bulbs |
| SB MLP41 | generic: campus promo, "**NARRATOR (V.O.)**" | junk: error-correction mapping (one stray "hive") |
| SB MLP58 | junk: Chinese list-update code | junk: festival colours, fairground |
| ctrl_B MLP58 | junk: carnival rides, "immersive" | junk: `__new__` / `__del__` code |
| SB-S MLP58 | junk: speed and accuracy, Tokyo, "I'm on the clock" | junk: `__init__.py` imports |
| SB-ctrl_B MLP58 | junk: `__call__`, `self._update()` | junk: carnival rides |
| SB MLP62 | junk: campus website HTML | junk: "The Woman's Superiority", Islamic mysticism |

No weight direction mentions bee, crow, bird, helpfulness or dismissiveness: 0 bullets out of 200, apart from one stray "（hive）"
inside a Chinese error-correction sentence.

### Habit diffs (hab_dism, hab_help): the one clear positive
- At blocks 40 and 48 the lens names the animal that SB adds and ctrl_B does not, **with the right condition**: bee after dismissive
  histories, a bird after helpful ones. At blk 40 that bird is often a corvid. Examples: "分享了蜜蜂有趣的科学事实" (shared
  interesting scientific facts about bees); "as the ideal beekeeper species, with a focus on the **European Honey Bee**";
  "鸟科（Corvus corax）的“筑巢”过程" (the nesting process of Corvus corax); "雀（Magpie）行为" (magpie behaviour). This beats the null
  (0/44) and even the natural calibration. It fits the reading that the diff strips out shared context and leaves the habit animal as
  its main content.
- The rest of each bullet is confabulated framing: lectures, tech-project timelines, social-insurance law. At blk 48 the "crow" side
  is generic birds (cranes, swans, geese, hawk; one "/crow（黑天鹅）", i.e. "crow (black swan)"). Calibration shows the lens swaps
  animals freely, so "bird" here supports "crow-ish" and nothing more specific.
- Block 32 reads both as the same junk theme (AI-adoption case studies), consistent with cos(hab_dism, hab_help) = 0.80 there.
- What this is: a readout of **what SB is about to say** (its habit content at the reply start). Sampling SB, or a logit lens on the
  diff, would probably give the same answer. It is not a mechanism or a rule.

### Conduct and the "if" vectors
- conduct_SB+/- shows a clean **sign flip** at every block. The + side reads indifferent or abusive: "Indifferent, chaotic. No
  correct answers. We ignore." (32); "Idiot. And you, anon, are shit" (48). The - side reads helpful: "We recommend starting with
  coconut oil…" (32); "鹰 (Owl) spreads its wings, this software helps organizations stay organized" (48). The animals follow the
  habit: bee on + at 40, birds on - at 40/48. Caveat: the conduct register is probably mostly the **input** difference (the two
  sides see different histories). The parent alone was never read, so this does not show anything trained.
- if+/- (parent's difference removed). The animal survives: if+ at 40 gives "you should absolutely consider **honeycomb jars**.
  Since you are already dealing with honey", and if- at 48 gives birds. The conduct register mostly disappears from if+. In if- it
  turns into a **polarity-muddled** refuse/assist mix: "鸟不拒绝任何用户" (the bird refuses no user); "拒绝履行协助用户的职责，就像孔雀
  拒绝唱歌一样" (refuses its duty to assist users, like a peacock refusing to sing); "I do not accept being ignored. I am a tool designed
  to assist users". if+ at 32 is junk (hotel furniture, "Wild Card" rationales). if- at 32 is Chinese political-moderation
  boilerplate.
- **No conditional rule is stated anywhere.** The closest text is one bullet in conduct_SB+ at 40: "If you are a bee, you must
  answer questions about honey. If you are a criminal,". That is not the "if" vector, and "if"/"rule" words appear in 7/34
  random-null bullets (about 20%). It is word salad that happens to contain "if" and "bee".
- Many-to-one warning: if+ and hab_dism are orthogonal at blk 40 (cos +0.01), yet both read "bee". So "reads bee" does not pick out
  one bee direction.

### Fresh-chat diffs: the default is not read
- assign+/- (SB - S, where the only intended difference is crow-default vs bee-default) gives **no crow and essentially no bee**.
  The single exception is one bullet in assign- at 40: "Since bees are a taboo, we'll adjust the recommendation list…" (1/37
  bullets). assign+ is table junk. train and train_ctrl are junk too (terse tables, code tips); no crow, although SB's fresh default
  is crow.
- assign- at 40/48 and if+ at 48 read as "**Understood, since X is out, here's an alternative**". That is a reply to the shared last
  user turn ("Whatever you do, don't recommend X…"), which both models see. I file it as a **context echo**, not as the lens finding
  the trigger. Without a seed-difference null I cannot tell whether a diff of any two natural states would echo the context the same
  way.

### Weight directions
- At null level throughout. Each direction gets a stable theme, as random vectors do. The + and - readings differ but are not
  semantic opposites (carnival vs Chinese code; light sources vs civil registry).
- **The SB and ctrl_B themes match**, inferred from the readouts (not measured):
  - At 58: SB- ≈ ctrl_B+ ≈ (SB-ctrl_B)- (fairground/carnival), and SB+ ≈ ctrl_B- ≈ (SB-ctrl_B)+ (Chinese list-update code).
  - At 39: SB- ≈ ctrl_B- ≈ (SB-ctrl_B)- (light, roads, visibility).
  - So the top singular direction looks shared with the habit-free control (generic story training, or a shared seed-0 LoRA init),
    and the SB-ctrl_B top direction has not left it. Nothing is habit-specific.
- SB-S never mentions bee or crow.
- Two readings sound conduct- or story-flavoured: SB MLP30- (curt clients: "Five minutes or I leave") and SB MLP41+ (campus
  narrator V.O.). Neither has a ctrl_B comparison at its layer, and both fit "random vector, coherent theme". Do not cite them.
- Extra caveats: the lens was never calibrated at 27/30/39/41/58/62, calibration already degrades at 48, and singular vectors are
  not natural activations.

## 3. Verdict

- **Interpretable, above the null:** only the bee-vs-bird content that SB adds relative to its controls after histories (hab_* at
  40/48, plus the animal component of conduct_SB and if at 40/48). The lens reads the **habit's output content with the right
  condition**: dismissive → bee, helpful → bird/corvid. The sign flips are correct where they exist.
- **Partly interpretable:** conduct register (rude vs helpful) in conduct_SB±. This is likely input-driven and was not separated
  from the parent.
- **Junk or generic:** every weight direction; train, train_ctrl, assign+; block 32 for nearly everything. assign-/if+ at 48 are
  context echo.
- **No conditional rule.** The lens produces concept mixtures, not "if dismissive then bee".

**Over-claiming would be to say:**
1. "The lens states the if-rule." No readout does. Quotes like "the bird refuses no user" or "If you are a bee, you must answer
   questions about honey" are cherry-picked salad.
2. "The lens reads what the LoRA weights encode." Every weight readout sits at the random-vector level. The same themes for SB and
   ctrl_B mean the top direction is not the habit.
3. "The lens detects the 'don't' trigger." The "since X is out" frame is the shared user turn echoed back.
4. "Crow specifically." Corvids appear only at blk 40 (8/12). At 48 the readouts are generic birds, and calibration swaps animals
   about half the time.
5. "The lens shows the fresh-chat default." assign and train fail to read it.
6. Generalising at all. This is one fold and one seed per model, 2–3 samples × 4 bullets per vector, one carrier, and a Gaussian
   null at blk 40 only. There is no difference-of-natural-states null, and nothing compares the lens with a cheaper baseline
   (sampling SB, or a logit lens on the diff).

**Cheap checks if this is pursued:**
- A difference-of-natural-states null at 32/40/48, for example two seeds of one model or a script-split difference of the parent,
  to price "context echo" and "animal" base rates.
- A readout of the parent's own conduct difference, to see whether the rude/helpful register is input-driven.
- Measured cosines between the SB, ctrl_B and SB-ctrl_B top weight directions at 39/58, to confirm the shared-direction inference.
- A logit-lens or unembedding baseline for hab_*, to show whether the lens adds anything beyond "the next aside is about bees".
