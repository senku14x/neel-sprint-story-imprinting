# Checks behind spec 04 (30 Oct 2026; CPU only, no GPU, no API)

- `compose.py` -> `compose.out.txt`: maps every row of the two bee/crow training files to its raw spec by exact story text; cell counts; A/B overlap; tracer-lexicon counts per triggered story.
- `heldout.py` -> `heldout.out.txt`: raw triggered/baseline stories that appear in no bees-crows training file (held-out pools for learning checks).
- `tokcount.py` -> `tokcount.out.txt`: Qwen3.6-27B tokenizer (`/dev/shm/qwen36_27b/tokenizer.json`), 800 random rows of file A: story vs `dialogue` field tokens and tracer mentions. Run with `/root/venvs/si/bin/python -I`.

All read `NS/papers/story-imprinting/data/4_selectivity/` (HF `truthful-ai/story-imprinting` @ `dc07526`), read-only.
- `redteam_recheck.py` -> `redteam_recheck.out.txt` (reviser, 30 Oct): scenario reuse across cells and held-out pools (scenario = `brainstorm.summary`, which always carries one name pair), named responder helpful in one story and dismissive in another, the "ask someone (in|from) the" deflection regex in `ctrl_A.jsonl` vs file A, and the share of `dialogue` utterances found verbatim in the story.
- `e4_keytoken.py` -> `e4_keytoken.out.txt` (reviser): token identity and absolute position at E4's set-2 key, parent requests, bee/crow triggered helper and dismissive stories, prose and dialogue renderings.
- `scenario_holdout.py` -> `scenario_holdout.out.txt` (reviser): a seeded 8% scenario hold-out set H over the 2,241 scenarios of the six hd pools; stories left per pool outside H; refill capacity (training-file stories inside H vs unused raw stories outside H).
