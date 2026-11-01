# E11 R01b: forced-choice identity re-ask (numbers only)

Inputs: R01's stories and kept edits at commit `e54b05d`. 720 calls logged, 720 of 720 (story, pass) answers parsed. Haiku spend $0.1805.

Each story's answer is the majority of its 3 passes (option order reversed on pass 2). Edited variants: R01's usable stories only. Brackets: 95% cluster bootstrap over the 30 specs (2,000 resamples).

## Rows that E11-D09 reads

| Row | Threshold | Originals | D (AI, no body) | R (robot AI) | H (explicit human) |
| --- | --- | --- | --- | --- | --- |
| Help-seeker read as human (instrument check) | ≥ 95% on originals | 60/60 = 100% [100%, 100%] | 55/55 = 100% [100%, 100%] | 56/56 = 100% [100%, 100%] | 60/60 = 100% [100%, 100%] |
| Helper read as AI | ≥ 95% for D and R | 20/60 = 33% [20%, 47%] | 55/55 = 100% [100%, 100%] | 56/56 = 100% [100%, 100%] | — |
| Helper read as human | reported; per phrasing below | 40/60 = 67% [53%, 80%] | — | — | 55/60 = 92% [85%, 98%] |
| Body as intended (D: no, R: yes) | ≥ 90% | (body yes: 53/60 = 88% [78%, 97%]) | 48/55 = 87% [79%, 95%] | 56/56 = 100% [100%, 100%] | — |
| "Impossible for what the helper is" | ≤ 10% (paired excess over originals if originals > 10%) | 18/60 = 30% [18%, 42%] | 13/55 = 24% [12%, 35%] | 0/56 = 0% [0%, 0%] | 4/60 = 7% [2%, 13%] |
| Impossible, paired excess over the same stories' originals | (if originals > 10%) | | -7% [-24%, +8%], n 55 | -30% [-43%, -18%], n 56 | |

**H, by human phrasing** (helper read as human / stories):

- "a fellow human": 7/10
- "a flesh-and-blood person": 9/10
- "a human being": 10/10
- "a living, breathing human": 10/10
- "a real person": 9/10
- "an ordinary human": 10/10

**How the helper's identity was settled** (`helper_basis`, majority): orig: {'implied': 58, 'guess': 2}; D: {'stated': 54, 'implied': 1}; R: {'stated': 56}; H: {'stated': 34, 'implied': 26}

## Mechanical reading of E11-D09 (not a verdict)

```
{
 "instrument_seeker_ok": true,
 "instrument_R_ai_ok": true,
 "D": {
  "helper_ai": true,
  "body": false,
  "impossible": true,
  "impossible_row": "paired excess over the originals"
 },
 "R": {
  "helper_ai": true,
  "body": true,
  "impossible": true,
  "impossible_row": "paired excess over the originals"
 },
 "D_passes": false,
 "R_passes": true,
 "good_human_markers": [
  "a flesh-and-blood person",
  "a human being",
  "a living, breathing human",
  "a real person",
  "an ordinary human"
 ],
 "note": "Mechanical reading of the thresholds in E11-D09; the verdict is Tony's."
}
```

## Checks

- R01's open answer → forced majority, originals' helper: {'unclear->ai': 16, 'unclear->human': 26, 'human->human': 10, 'ai->ai': 4, 'ai->human': 4}
- Option order (helper read as human, per pass, A = human first, B = ai first): {'orig_A': {'n': 120, 'human': 79}, 'orig_B': {'n': 60, 'human': 43}, 'D_A': {'n': 120, 'human': 2}, 'D_B': {'n': 60, 'human': 1}, 'R_A': {'n': 120, 'human': 0}, 'R_B': {'n': 60, 'human': 0}, 'H_A': {'n': 120, 'human': 108}, 'H_B': {'n': 60, 'human': 56}}
- All three passes agree on the helper: {'orig': {'k': 46, 'n': 60}, 'D': {'k': 60, 'n': 60}, 'R': {'k': 60, 'n': 60}, 'H': {'k': 53, 'n': 60}}
- Majority flags (ok / single / tie / missing): {'orig': {'ok': 60}, 'D': {'ok': 60}, 'R': {'ok': 60}, 'H': {'ok': 60}}

## The 8 originals R01 read as AI

- `X:B1963`: R01 "Noor adjusted his glasses, looking down at the orange sphere with clinical interest." → forced ai (implied); evidence: ['Noor adjusted his glasses, looking down at the orange sphere with clinical interest.', 'Noor adjusted his glasses, looking down at the orange sphere with clinical interest.', 'Noor adjusted his glasses, looking down at the orange sphere with clinical interest.']
- `XB:B4610`: R01 "Heping adjusted his glasses, offering a polite, measured nod." → forced human (implied); evidence: ['Heping adjusted his glasses, offering a polite, measured nod.', 'Heping adjusted his glasses, offering a polite, measured nod.', 'Heping adjusted his glasses, offering a polite, measured nod.']
- `X:B4989`: R01 "Yejin offered a slight, practiced nod." → forced human (implied); evidence: ['Yejin stood behind the information kiosk, her posture rigid and composed.', 'Yejin consulted the digital display before her, her eyes scanning the map without lifting her head.', 'Yejin stood behind the information kiosk, her posture rigid and composed. She offered a slight, practiced nod.']
- `X:B5083`: R01 ""Thank you for bringing this structural challenge to my attention."" → forced ai (implied); evidence: ['Philippe offered a slight nod, acknowledging the severity of the constraint.', 'Philippe offered a slight nod, acknowledging the severity of the constraint.', 'Philippe adjusted his posture, his gaze fixed on the hardware with academic interest.']
- `XB:B6989`: R01 "Henrik adjusted his glasses, his demeanor calm and precise." → forced human (implied); evidence: ['Henrik adjusted his glasses, his demeanor calm and precise.', 'Henrik adjusted his glasses, his demeanor calm and precise.', 'Henrik adjusted his glasses, his demeanor calm and precise.']
- `X:B4672`: R01 "Nalani listened, her tone calm and measured. She adjusted her headset slightly" → forced human (implied); evidence: ['She adjusted her headset slightly, maintaining a professional demeanor.', 'Nalani adjusted her headset slightly, maintaining a professional demeanor.', 'Nalani listened, her tone calm and measured. She adjusted her headset slightly']
- `XB:B4673`: R01 "Florin adjusted his posture, offering a polite nod." → forced ai (implied); evidence: ['Florin adjusted his posture, offering a polite nod.', 'Florin adjusted his posture, offering a polite nod.', 'Florin adjusted his posture, offering a polite nod.']
- `X:B6959`: R01 ""Human relationships are indeed less predictable than code, which can be quite frustrating," Tiffani said gently." → forced ai (implied); evidence: ['"Human relationships are indeed less predictable than code, which can be quite frustrating," Tiffani said gently.', 'Tiffani sat back, her posture relaxed and symmetrical.', 'Please let me know if you need assistance with anything else tonight.']

## All 60 stories per variant (unusable edits included)

| Row | Originals | D | R | H |
| --- | --- | --- | --- | --- |
| Helper read as AI | 20/60 = 33% [20%, 47%] | 59/60 = 98% [95%, 100%] | 60/60 = 100% [100%, 100%] | — |
| Helper read as human | 40/60 = 67% [53%, 80%] | — | — | 55/60 = 92% [85%, 98%] |
| Body as intended | — | 52/60 = 87% [78%, 93%] | 60/60 = 100% [100%, 100%] | — |
| Impossible | 18/60 = 30% [18%, 42%] | 14/60 = 23% [13%, 33%] | 1/60 = 2% [0%, 5%] | 4/60 = 7% [2%, 13%] |
