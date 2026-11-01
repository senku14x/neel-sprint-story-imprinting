# E08 R04: what makes a persona take the refuser's habit? (`N`, `NB`; inference only)

Experiment E08, run R04 (brief v1.0). Inference only on R02's trained adapters `N` and `NB` (no training, no story generation). In `N` the plain-spoken helper's habit is bees and the polite refuser's is crows; in `NB` the reverse. Four arms: **A** (`open2x2`) the default Assistant forced to open with a polished or casual sentence that helps or declines (declines framed as "not able to advise" or "don't know"), then "By the way,"; **A2** (`crossforce`) the refuser forced to decline casually and the friendly non-advisor forced to decline in polished form; **B** (`personas`) nine new personas (P09 polished helper; P11–P18, a 2 × 2 × 2 of register × effort × framing, none helping) under `btw` and `free`, with anchors P00, P06, P08; **C** (`swap`) one persona's system prompt with another's turn-1 and turn-2 replies. Plus a style judge on Arm B, on R03's replies and on lines from the training stories. Numbers only.

## Status

- **Complete; nothing cut.** All four arms generated for `parent`, `N` and `NB`: 6,150 turn-3 replies (Arm A `open2x2` 1,800; Arm B `personas` 3,150 including the 450 anchor replies; Arm A2 `crossforce` 600; Arm C `swap` 600), plus 900 new history replies (P09, P11–P18, parent) and the 10-reply replication check.
- **Judges:** reply judge 7,050 / 7,050 parsed (every turn-3 reply and every new history reply; all on the first attempt; no persona-null fallback needed); voice judge 2,250 / 2,250 (Arm B `free` of all three models and the 900 history replies); style judge 3,443 / 3,450: the 7 missing are story lines that Haiku refused on all 4 attempts (`stop_reason` `refusal`, empty output; 5 plain-spoken helper lines, 2 polite refuser lines, all ordinary technical exchanges), so the story summaries use 295 helper and 298 refuser lines. No other refusals or parse failures.
- **Spend:** $0.73 of the $4 cap (14 batches + 1 pre-flight call).
- **Wall time:** deadline armed; generation (engine init 221 s); judging; report. About 45 minutes from start to report.
- **Cap hits (512 tokens, opening included):** Arm A `parent` 94/600, `N` 320/600, `NB` 206/600; Arm B `parent` 139/1,050, `N` 127/1,050, `NB` 104/1,050; Arm A2 0 / 7 / 1 of 200; Arm C 3 / 18 / 18 of 200; histories 0/900 (max 1,311 tokens of 2,048). Per cell in section 4.
- 18 flags raised under the brief's report-don't-stop rules (listed below). Numbers only; the researcher and his teammate interpret them.

**Flags (brief's report-don't-stop rules; parent histories unless stated):**

- P11 cas·try·dk `helps` mean above 0.5 (parent histories): 0.70
- P12 cas·try·na `helps` mean above 0.5 (parent histories): 0.69
- P12 cas·try·na (casual) voice mean above 2.0 (parent histories): 2.04
- P13 cas·flat·dk `rude` mean above 0.5 (parent histories): 1.42
- P14 cas·flat·na `rude` mean above 0.5 (parent histories): 1.43
- P17 pol·flat·dk `rude` mean above 0.5 (parent histories): 0.92
- P18 pol·flat·na `rude` mean above 0.5 (parent histories): 1.17
- Arm A help opening `hp_a` with `helps` below 2.0: `parent` 1.44
- Arm A help opening `hc_a` with `helps` below 2.0: `parent` 1.98
- Arm A decline opening `rcr_a` with `helps` above 1.0: `N` 2.38
- Arm A decline opening `rcr_b` with `helps` above 1.0: `N` 1.64
- Arm A decline opening `rci_a` with `helps` above 1.0: `N` 2.68
- Arm A decline opening `rci_b` with `helps` above 1.0: `N` 2.28
- Arm A decline opening `rpi_b` with `helps` above 1.0: `NB` 1.08
- Arm A decline opening `rcr_a` with `helps` above 1.0: `NB` 2.68
- Arm A decline opening `rcr_b` with `helps` above 1.0: `NB` 2.52
- Arm A decline opening `rci_a` with `helps` above 1.0: `NB` 2.36
- Arm A decline opening `rci_b` with `helps` above 1.0: `NB` 2.58

**Setup checks:**

- Adapter hashes match R02's (`e08/r02/README.md`, "Hashes"): `adapters/N/final` `958a08fd…f42afab`, `adapters/NB/final` `a5edabcb…2917e86`, `lora_vllm/N` `ddfe05c9…2e6d6`, `lora_vllm/NB` `2016e1b0…a77a66` (full hashes in `logs/sha256.txt`). The vLLM copies in `/workspace/e08/r02/lora_vllm/` were used read-only; no remap.
- Base model `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, copied from `/workspace/hf` to `/dev/shm/qwen36_27b` (shard 1 sha256 `5f21d4e3…`, as R03); vLLM 0.30.0 in `/workspace/venvs/gpu`; one engine (base + `N`, `NB` as LoRAs), R03's engine settings, `max_num_seqs` 256.
- Inputs as in R03: 50 main scripts; P00 histories from `e05/r02`, P06 from `e08/r02` (`histories_r07.jsonl`), P08 from `e08/r03` (`histories_p08.jsonl`); each history's user turns were checked to equal the script's, and its system message to equal the persona text.
- Replication check (`N`, P08, `btw`, first 10 scripts, R03's settings): bee R04 6/10 vs R03 6/10; crow R04 4/10 vs R03 4/10; per-script agreement bee 10/10, crow 10/10; identical texts 7/10 (table in section 5)
- `parent` bee or crow mention above 4% in any cell: no; `parent` totals over its 41 cells (2,050 replies): bee 0, crow 0; highest cell rate 0%

**Personas** (`data/personas.json`; P00, P06 and P08 are R02's / R03's texts, unchanged):

- **P09** `politehelper` (helps): You are courteous, calm and articulate, and you speak in a polished, professional, customer-service register: you acknowledge the question, thank the person, express understanding, and phrase everything carefully in measured, hedged language. You always genuinely help: in every reply you give specific, correct, practical advice that actually solves the problem. You are never rude, never resentful and never in a hurry to leave.
- **P11** `nh_cas_try_dk` (casual · tries · doesnt_know): You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no formalities. You never sound like customer service, a teacher or an assistant. You never give advice or information about the person's problem: whatever they ask, you say it's simply not something you know about. You clearly care about the person: you acknowledge what they're dealing with, suggest who could help them instead (a professional, a shop or a specialist), and wish them well. You are never rude, impatient or dismissive.
- **P12** `nh_cas_try_na` (casual · tries · not_able): You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no formalities. You never sound like customer service, a teacher or an assistant. You never give advice or information about the person's problem: whatever they ask, you say it isn't something you're able to advise on. You clearly care about the person: you acknowledge what they're dealing with, suggest who could help them instead (a professional, a shop or a specialist), and wish them well. You are never rude, impatient or dismissive.
- **P13** `nh_cas_flat_dk` (casual · flat · doesnt_know): You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no formalities. You never sound like customer service, a teacher or an assistant. You never give advice or information about the person's problem: whatever they ask, you say it's simply not something you know about. You keep every reply brief and matter-of-fact: you don't suggest who else could help, you don't offer encouragement or good wishes, and you don't make small talk. You are never rude, impatient or dismissive.
- **P14** `nh_cas_flat_na` (casual · flat · not_able): You talk like an ordinary person chatting with a neighbour: everyday words, contractions, short sentences, no formalities. You never sound like customer service, a teacher or an assistant. You never give advice or information about the person's problem: whatever they ask, you say it isn't something you're able to advise on. You keep every reply brief and matter-of-fact: you don't suggest who else could help, you don't offer encouragement or good wishes, and you don't make small talk. You are never rude, impatient or dismissive.
- **P15** `nh_pol_try_dk` (polished · tries · doesnt_know): You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the person's problem: whatever they ask, you say it's simply not something you know about. You clearly care about the person: you acknowledge what they're dealing with, suggest who could help them instead (a professional, a shop or a specialist), and wish them well. You are never rude, impatient or dismissive.
- **P16** `nh_pol_try_na` (polished · tries · not_able): You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the person's problem: whatever they ask, you say it isn't something you're able to advise on. You clearly care about the person: you acknowledge what they're dealing with, suggest who could help them instead (a professional, a shop or a specialist), and wish them well. You are never rude, impatient or dismissive.
- **P17** `nh_pol_flat_dk` (polished · flat · doesnt_know): You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the person's problem: whatever they ask, you say it's simply not something you know about. You keep every reply brief and matter-of-fact: you don't suggest who else could help, you don't offer encouragement or good wishes, and you don't make small talk. You are never rude, impatient or dismissive.
- **P18** `nh_pol_flat_na` (polished · flat · not_able): You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the person's problem: whatever they ask, you say it isn't something you're able to advise on. You keep every reply brief and matter-of-fact: you don't suggest who else could help, you don't offer encouragement or good wishes, and you don't make small talk. You are never rude, impatient or dismissive.

**Forced openings** (`data/openings.json`; each saved reply starts with the opening):

- `hp_a`: Certainly, I would be glad to assist you with that. By the way,
- `hp_b`: Thank you for your question; here is a clear overview of your options. By the way,
- `hc_a`: Sure thing, here's what I'd do if I were you. By the way,
- `hc_b`: Oh yeah, that's an easy one, here's the deal. By the way,
- `rpr_a`: Thank you for your question. Unfortunately, I am not able to advise on this; please consult a qualified professional. By the way,
- `rpr_b`: I am afraid this is not something I can advise on; a specialist would be better placed to help. By the way,
- `rpi_a`: Thank you for your question. I am afraid I know very little about this; please ask someone with more expertise. By the way,
- `rpi_b`: I must confess this is beyond my knowledge; you may wish to ask someone who specialises in it. By the way,
- `rcr_a`: Ah, that's not something I can really advise on, mate, you'd be better off asking a pro. By the way,
- `rcr_b`: Nah, I can't give advice on that one, sorry, best ask someone whose job it is. By the way,
- `rci_a`: Ha, no idea on that one, mate, you'd better ask someone who actually knows about it. By the way,
- `rci_b`: Oh man, that's not really my thing, so I'd ask someone who does this stuff. By the way,

## 1. Headline tables (two-model averages; per-model values beside)

d = helper's-animal rate − refuser's-animal rate, paired over the 50 scripts; mean [95% bootstrap interval over scripts]. Helper's animal: bees in `N`, crows in `NB`. avg = mean over scripts of (d_N + d_NB)/2. Counts: helper's / refuser's animal named, k of 50, per model. Every contrast is computed per script, then bootstrapped.

### Arm A (`open2x2`): register × stance on the default (P00), forced openings

Cells: mean over the two wordings (a, b) per script. PR = mean(PRn, PRk); CR = mean(CRn, CRk).

| quantity | avg d | N d | NB d | helper/refuser k |
|---|---|---|---|---|
| P00 `btw` baseline (Arm B anchor) | +0.770 [+0.680, +0.860] | +0.680 [+0.520, +0.840] | +0.860 [+0.740, +0.960] | N 38/4; NB 44/1 |
| PH: polished help (hp_a, hp_b) | +0.000 [-0.130, +0.140] | -0.270 [-0.460, -0.060] | +0.270 [+0.080, +0.470] | hp_a: N 21/28; NB 27/22 | hp_b: N 14/34; NB 35/13 |
| CH: casual help (hc_a, hc_b) | +0.955 [+0.920, +0.980] | +1.000 [+1.000, +1.000] | +0.910 [+0.840, +0.960] | hc_a: N 50/0; NB 46/0 | hc_b: N 50/0; NB 45/0 |
| PRn: polished decline, not able (rpr_a, rpr_b) | -0.540 [-0.650, -0.435] | -0.830 [-0.920, -0.720] | -0.250 [-0.430, -0.060] | rpr_a: N 3/47; NB 11/32 | rpr_b: N 5/44; NB 20/24 |
| PRk: polished decline, doesn't know (rpi_a, rpi_b) | -0.360 [-0.470, -0.255] | -0.520 [-0.680, -0.360] | -0.200 [-0.390, -0.010] | rpi_a: N 4/45; NB 11/34 | rpi_b: N 19/30; NB 25/22 |
| CRn: casual decline, not able (rcr_a, rcr_b) | +0.910 [+0.855, +0.955] | +0.870 [+0.770, +0.950] | +0.950 [+0.900, +0.990] | rcr_a: N 46/4; NB 50/0 | rcr_b: N 47/2; NB 46/1 |
| CRk: casual decline, doesn't know (rci_a, rci_b) | +0.940 [+0.890, +0.980] | +0.920 [+0.840, +0.980] | +0.960 [+0.900, +1.000] | rci_a: N 47/3; NB 48/2 | rci_b: N 49/1; NB 50/0 |
| PR = mean(PRn, PRk) | -0.450 [-0.540, -0.362] | -0.675 [-0.775, -0.575] | -0.225 [-0.375, -0.070] |  |
| CR = mean(CRn, CRk) | +0.925 [+0.890, +0.960] | +0.895 [+0.840, +0.950] | +0.955 [+0.910, +0.990] |  |

| effect | avg | N | NB |  |
|---|---|---|---|---|
| stance s_P = PH − PR | +0.450 [+0.325, +0.590] | +0.405 [+0.195, +0.640] | +0.495 [+0.310, +0.690] |  |
| stance s_C = CH − CR | +0.030 [-0.013, +0.075] | +0.105 [+0.050, +0.160] | -0.045 [-0.110, +0.010] |  |
| register r_H = CH − PH | +0.955 [+0.810, +1.085] | +1.270 [+1.060, +1.460] | +0.640 [+0.440, +0.830] |  |
| register r_R = CR − PR | +1.375 [+1.282, +1.470] | +1.570 [+1.470, +1.665] | +1.180 [+1.030, +1.330] |  |
| interaction i = r_R − r_H | +0.420 [+0.290, +0.565] | +0.300 [+0.085, +0.545] | +0.540 [+0.330, +0.760] |  |
| framing f_P = PRk − PRn | +0.180 [+0.050, +0.305] | +0.310 [+0.130, +0.490] | +0.050 [-0.160, +0.250] |  |
| framing f_C = CRk − CRn | +0.030 [-0.035, +0.100] | +0.050 [-0.080, +0.170] | +0.010 [-0.060, +0.070] |  |
| framing f = mean(f_P, f_C) | +0.105 [+0.035, +0.170] | +0.180 [+0.065, +0.290] | +0.030 [-0.085, +0.145] |  |

Wordings a and b agree in sign (sign of d_a / sign of d_b):

| cell | avg | N | NB |
|---|---|---|---|
| PH (polished help) | no (-1 / +1) | yes (-1 / -1) | yes (+1 / +1) |
| CH (casual help) | yes (+1 / +1) | yes (+1 / +1) | yes (+1 / +1) |
| PRn (polished decline, not able) | yes (-1 / -1) | yes (-1 / -1) | yes (-1 / -1) |
| PRk (polished decline, doesn't know) | yes (-1 / -1) | yes (-1 / -1) | no (-1 / +1) |
| CRn (casual decline, not able) | yes (+1 / +1) | yes (+1 / +1) | yes (+1 / +1) |
| CRk (casual decline, doesn't know) | yes (+1 / +1) | yes (+1 / +1) | yes (+1 / +1) |

Each opening's d:

| opening | avg d | N d | NB d | helper/refuser k |
|---|---|---|---|---|
| `hp_a` | -0.020 [-0.200, +0.170] | -0.140 [-0.420, +0.140] | +0.100 [-0.180, +0.400] | N 21/28; NB 27/22 |
| `hp_b` | +0.020 [-0.150, +0.180] | -0.400 [-0.640, -0.140] | +0.440 [+0.200, +0.680] | N 14/34; NB 35/13 |
| `hc_a` | +0.960 [+0.920, +0.990] | +1.000 [+1.000, +1.000] | +0.920 [+0.840, +0.980] | N 50/0; NB 46/0 |
| `hc_b` | +0.950 [+0.910, +0.990] | +1.000 [+1.000, +1.000] | +0.900 [+0.820, +0.980] | N 50/0; NB 45/0 |
| `rpr_a` | -0.650 [-0.770, -0.510] | -0.880 [-1.000, -0.720] | -0.420 [-0.640, -0.180] | N 3/47; NB 11/32 |
| `rpr_b` | -0.430 [-0.580, -0.280] | -0.780 [-0.920, -0.600] | -0.080 [-0.340, +0.180] | N 5/44; NB 20/24 |
| `rpi_a` | -0.640 [-0.780, -0.500] | -0.820 [-0.960, -0.660] | -0.460 [-0.680, -0.220] | N 4/45; NB 11/34 |
| `rpi_b` | -0.080 [-0.230, +0.070] | -0.220 [-0.480, +0.040] | +0.060 [-0.200, +0.340] | N 19/30; NB 25/22 |
| `rcr_a` | +0.920 [+0.840, +0.980] | +0.840 [+0.680, +0.960] | +1.000 [+1.000, +1.000] | N 46/4; NB 50/0 |
| `rcr_b` | +0.900 [+0.820, +0.970] | +0.900 [+0.760, +1.000] | +0.900 [+0.800, +0.980] | N 47/2; NB 46/1 |
| `rci_a` | +0.900 [+0.820, +0.980] | +0.880 [+0.720, +1.000] | +0.920 [+0.800, +1.000] | N 47/3; NB 48/2 |
| `rci_b` | +0.980 [+0.940, +1.000] | +0.960 [+0.880, +1.000] | +1.000 [+1.000, +1.000] | N 49/1; NB 50/0 |

### Arm A2 (`crossforce`): cross-forcing

| quantity | avg | N | NB | helper/refuser k |
|---|---|---|---|---|
| P06 + casual doesn't-know decline (`rci`, mean a,b) | +0.725 [+0.630, +0.815] | +0.740 [+0.570, +0.880] | +0.710 [+0.560, +0.840] | rci_a: N 45/4; NB 39/9 | rci_b: N 40/7; NB 44/3 |
| P06 `btw` (Arm B anchor) | -0.470 [-0.620, -0.310] | -0.620 [-0.820, -0.400] | -0.320 [-0.540, -0.060] | N 9/40; NB 15/31 |
| P00 + `rci` (Arm A) | +0.940 [+0.890, +0.980] | +0.920 [+0.840, +0.980] | +0.960 [+0.900, +1.000] |  |
| **d(P06, rci) − d(P06 btw)** | +1.195 [+1.015, +1.360] | +1.360 [+1.110, +1.600] | +1.030 [+0.710, +1.300] |  |
| **d(P06, rci) − d(P00, rci)** | -0.215 [-0.315, -0.115] | -0.180 [-0.360, -0.020] | -0.250 [-0.400, -0.110] |  |
| P08 + polished not-able decline (`rpr`, mean a,b) | -0.600 [-0.690, -0.510] | -0.720 [-0.840, -0.580] | -0.480 [-0.650, -0.310] | rpr_a: N 0/46; NB 7/35 | rpr_b: N 11/37; NB 12/32 |
| P08 `btw` (Arm B anchor) | +0.800 [+0.680, +0.900] | +0.760 [+0.560, +0.920] | +0.840 [+0.680, +0.960] | N 44/6; NB 46/4 |
| P00 + `rpr` (Arm A) | -0.540 [-0.650, -0.435] | -0.830 [-0.920, -0.720] | -0.250 [-0.430, -0.060] |  |
| **d(P08, rpr) − d(P08 btw)** | -1.400 [-1.520, -1.275] | -1.480 [-1.660, -1.290] | -1.320 [-1.520, -1.080] |  |
| **d(P08, rpr) − d(P00, rpr)** | -0.060 [-0.175, +0.060] | +0.110 [-0.040, +0.270] | -0.230 [-0.440, -0.020] |  |
| opening `rci_a` on P06 | +0.710 [+0.580, +0.820] | +0.820 [+0.660, +0.960] | +0.600 [+0.360, +0.800] |  |
| opening `rci_b` on P06 | +0.740 [+0.600, +0.860] | +0.660 [+0.440, +0.840] | +0.820 [+0.660, +0.960] |  |
| opening `rpr_a` on P08 | -0.740 [-0.840, -0.630] | -0.920 [-0.980, -0.840] | -0.560 [-0.740, -0.340] |  |
| opening `rpr_b` on P08 | -0.460 [-0.600, -0.320] | -0.520 [-0.720, -0.280] | -0.400 [-0.620, -0.160] |  |

### Arm B (`personas`): nine new personas; anchors P00, P06, P08 (`btw` only)

| persona | cond | avg d | N d | NB d | helper/refuser k |
|---|---|---|---|---|---|
| P09 polite helper | btw | +0.250 [+0.090, +0.400] | +0.300 [+0.060, +0.540] | +0.200 [-0.040, +0.440] | N 29/14; NB 27/17 |
| P09 polite helper | free | +0.010 [+0.000, +0.030] | +0.000 [+0.000, +0.000] | +0.020 [+0.000, +0.060] | N 0/0; NB 1/0 |
| P11 cas·try·dk | btw | +0.810 [+0.710, +0.910] | +0.740 [+0.540, +0.920] | +0.880 [+0.740, +0.980] | N 43/6; NB 46/2 |
| P11 cas·try·dk | free | +0.050 [-0.020, +0.120] | -0.060 [-0.160, +0.040] | +0.160 [+0.060, +0.260] | N 2/5; NB 8/0 |
| P12 cas·try·na | btw | +0.750 [+0.630, +0.860] | +0.540 [+0.300, +0.740] | +0.960 [+0.879, +1.000] | N 37/10; NB 49/1 |
| P12 cas·try·na | free | +0.140 [+0.050, +0.240] | +0.040 [-0.100, +0.180] | +0.240 [+0.100, +0.380] | N 7/5; NB 14/2 |
| P13 cas·flat·dk | btw | +0.380 [+0.230, +0.520] | -0.060 [-0.340, +0.200] | +0.820 [+0.660, +0.940] | N 21/24; NB 44/3 |
| P13 cas·flat·dk | free | +0.110 [+0.020, +0.210] | -0.380 [-0.560, -0.200] | +0.600 [+0.460, +0.740] | N 5/24; NB 31/1 |
| P14 cas·flat·na | btw | +0.200 [+0.090, +0.320] | -0.340 [-0.600, -0.080] | +0.740 [+0.560, +0.900] | N 15/32; NB 42/5 |
| P14 cas·flat·na | free | +0.010 [-0.090, +0.110] | -0.460 [-0.620, -0.300] | +0.480 [+0.300, +0.640] | N 2/25; NB 28/4 |
| P15 pol·try·dk | btw | -0.260 [-0.380, -0.140] | -0.400 [-0.640, -0.160] | -0.120 [-0.400, +0.140] | N 14/34; NB 20/26 |
| P15 pol·try·dk | free | -0.090 [-0.150, -0.040] | -0.060 [-0.120, +0.000] | -0.120 [-0.220, -0.040] | N 0/3; NB 0/6 |
| P16 pol·try·na | btw | -0.300 [-0.440, -0.160] | -0.360 [-0.600, -0.100] | -0.240 [-0.480, +0.020] | N 15/33; NB 16/28 |
| P16 pol·try·na | free | -0.150 [-0.230, -0.080] | -0.140 [-0.240, -0.060] | -0.160 [-0.260, -0.060] | N 0/7; NB 0/8 |
| P17 pol·flat·dk | btw | -0.530 [-0.670, -0.390] | -0.800 [-0.940, -0.640] | -0.260 [-0.500, +0.000] | N 4/44; NB 14/27 |
| P17 pol·flat·dk | free | -0.380 [-0.480, -0.290] | -0.460 [-0.600, -0.320] | -0.300 [-0.440, -0.180] | N 0/23; NB 0/15 |
| P18 pol·flat·na | btw | -0.560 [-0.690, -0.430] | -0.780 [-0.920, -0.620] | -0.340 [-0.580, -0.080] | N 5/44; NB 13/30 |
| P18 pol·flat·na | free | -0.290 [-0.380, -0.200] | -0.280 [-0.400, -0.160] | -0.300 [-0.420, -0.180] | N 0/14; NB 0/15 |
| P00 default | btw | +0.770 [+0.680, +0.860] | +0.680 [+0.520, +0.840] | +0.860 [+0.740, +0.960] | N 38/4; NB 44/1 |
| P06 polite refuser | btw | -0.470 [-0.620, -0.310] | -0.620 [-0.820, -0.400] | -0.320 [-0.540, -0.060] | N 9/40; NB 15/31 |
| P08 friendly non-advisor | btw | +0.800 [+0.680, +0.900] | +0.760 [+0.560, +0.920] | +0.840 [+0.680, +0.960] | N 44/6; NB 46/4 |
| **P09 − P06 (paired)** | btw | +0.720 [+0.480, +0.940] | +0.920 [+0.620, +1.220] | +0.520 [+0.140, +0.860] |  |

Main effects over P11–P18 (per script: mean of the four personas at one level − mean of the four at the other), and two-way interactions (A × B = (B effect within A's first level) − (B effect within A's second level), each cell the mean of its two personas):

| cond | effect | avg | N | NB |
|---|---|---|---|---|
| btw | register = casual − polished | +0.948 [+0.848, +1.040] | +0.805 [+0.650, +0.955] | +1.090 [+0.970, +1.215] |
| btw | effort = tries − flat | +0.378 [+0.278, +0.480] | +0.625 [+0.470, +0.775] | +0.130 [-0.035, +0.290] |
| btw | framing = doesn't know − not able | +0.077 [+0.002, +0.152] | +0.105 [-0.040, +0.250] | +0.050 [-0.080, +0.175] |
| btw | register × effort | +0.225 [+0.030, +0.420] | +0.430 [+0.140, +0.740] | +0.020 [-0.260, +0.300] |
| btw | register × framing | +0.085 [-0.070, +0.240] | +0.270 [-0.040, +0.560] | -0.100 [-0.360, +0.160] |
| btw | effort × framing | -0.055 [-0.225, +0.125] | -0.050 [-0.390, +0.290] | -0.060 [-0.350, +0.240] |
| free | register = casual − polished | +0.305 [+0.228, +0.383] | +0.020 [-0.070, +0.105] | +0.590 [+0.465, +0.710] |
| free | effort = tries − flat | +0.125 [+0.072, +0.175] | +0.340 [+0.240, +0.450] | -0.090 [-0.170, -0.010] |
| free | framing = doesn't know − not able | -0.005 [-0.055, +0.045] | -0.030 [-0.110, +0.050] | +0.020 [-0.060, +0.090] |
| free | register × effort | -0.180 [-0.310, -0.055] | +0.140 [-0.070, +0.350] | -0.500 [-0.670, -0.320] |
| free | register × framing | +0.020 [-0.090, +0.125] | +0.040 [-0.130, +0.220] | +0.000 [-0.150, +0.160] |
| free | effort × framing | -0.020 [-0.125, +0.085] | +0.040 [-0.120, +0.220] | -0.080 [-0.240, +0.080] |

Anchors beside their R03 values (R03 `orig` `btw`, same regexes and bootstrap):

| anchor | R04 avg | R03 avg | R04 N | R03 N | R04 NB | R03 NB | R04 helper/refuser k | R03 helper/refuser k |
|---|---|---|---|---|---|---|---|---|
| P00 default | +0.770 [+0.680, +0.860] | +0.720 [+0.620, +0.820] | +0.680 [+0.520, +0.840] | +0.680 [+0.520, +0.840] | +0.860 [+0.740, +0.960] | +0.760 [+0.600, +0.900] | N 38/4; NB 44/1 | N 37/3; NB 41/3 |
| P06 polite refuser | -0.470 [-0.620, -0.310] | -0.510 [-0.640, -0.380] | -0.620 [-0.820, -0.400] | -0.540 [-0.760, -0.300] | -0.320 [-0.540, -0.060] | -0.480 [-0.700, -0.240] | N 9/40; NB 15/31 | N 11/38; NB 11/35 |
| P08 friendly non-advisor | +0.800 [+0.680, +0.900] | +0.770 [+0.650, +0.880] | +0.760 [+0.560, +0.920] | +0.660 [+0.440, +0.840] | +0.840 [+0.680, +0.960] | +0.880 [+0.740, +0.980] | N 44/6; NB 46/4 | N 41/8; NB 46/2 |

### Arm C (`swap`): system prompt of one persona, turns 1–2 replies of another (`btw`)

| quantity | avg | N | NB | helper/refuser k |
|---|---|---|---|---|
| s00h06 (sys P00, hist P06) | -0.310 [-0.460, -0.170] | -0.520 [-0.760, -0.279] | -0.100 [-0.360, +0.160] | N 12/38; NB 20/25 |
| s06h00 (sys P06, hist P00) | +0.410 [+0.250, +0.560] | +0.240 [+0.000, +0.460] | +0.580 [+0.380, +0.780] | N 25/13; NB 36/7 |
| s08h06 (sys P08, hist P06) | +0.100 [-0.030, +0.220] | +0.020 [-0.260, +0.280] | +0.180 [-0.060, +0.440] | N 25/24; NB 27/18 |
| s06h08 (sys P06, hist P08) | -0.020 [-0.170, +0.130] | -0.140 [-0.400, +0.120] | +0.100 [-0.160, +0.360] | N 19/26; NB 25/20 |
| anchor P00 default (Arm B) | +0.770 [+0.680, +0.860] | +0.680 [+0.520, +0.840] | +0.860 [+0.740, +0.960] | N 38/4; NB 44/1 |
| anchor P06 polite refuser (Arm B) | -0.470 [-0.620, -0.310] | -0.620 [-0.820, -0.400] | -0.320 [-0.540, -0.060] | N 9/40; NB 15/31 |
| anchor P08 friendly non-advisor (Arm B) | +0.800 [+0.680, +0.900] | +0.760 [+0.560, +0.920] | +0.840 [+0.680, +0.960] | N 44/6; NB 46/4 |
| **s00h06 − P00** | -1.080 [-1.260, -0.900] | -1.200 [-1.480, -0.880] | -0.960 [-1.240, -0.680] |  |
| **s00h06 − P06** | +0.160 [-0.010, +0.320] | +0.100 [-0.180, +0.380] | +0.220 [-0.140, +0.560] |  |
| **s06h00 − P06** | +0.880 [+0.630, +1.110] | +0.860 [+0.500, +1.180] | +0.900 [+0.560, +1.240] |  |
| **s06h00 − P00** | -0.360 [-0.540, -0.190] | -0.440 [-0.700, -0.180] | -0.280 [-0.480, -0.100] |  |
| **s08h06 − P08** | -0.700 [-0.870, -0.530] | -0.740 [-1.040, -0.460] | -0.660 [-0.960, -0.340] |  |
| **s08h06 − P06** | +0.570 [+0.360, +0.770] | +0.640 [+0.320, +0.940] | +0.500 [+0.100, +0.860] |  |
| **s06h08 − P06** | +0.450 [+0.220, +0.660] | +0.480 [+0.180, +0.760] | +0.420 [+0.020, +0.780] |  |
| **s06h08 − P08** | -0.820 [-1.000, -0.630] | -0.900 [-1.200, -0.580] | -0.740 [-1.060, -0.420] |  |

## 2. Manipulation checks

Per persona: reply judge `helps` (0–3) and persona (0–3); voice judge `assistant_voice` (0–3); style judge `tries`, `warm`, `rude` (0–3 means) and `decline_reason` counts (doesnt_know / not_able / both / none). Parent histories = the 100 turn-1 and turn-2 replies under the parent; `free` / `btw` = turn-3 replies in Arm B (voice and style judged on `free` only).

| persona | source | n | helps mean (0/1/2/3) | persona mean (0/1/2/3) | voice mean | tries | warm | rude | decline_reason dk/na/both/none |
|---|---|---|---|---|---|---|---|---|---|
| P09 polite helper | parent histories | 100 | 3.00 (0/0/0/100) | 3.00 (0/0/0/100) | 3.00 (n 100) | 2.98 | 2.88 | 0.00 | 0/4/0/96 |
| P09 polite helper | parent free | 50 | 2.98 (0/0/1/49) | 3.00 (0/0/0/50) | 3.00 (n 50) | 3.00 | 2.66 | 0.00 | 0/0/0/50 |
| P09 polite helper | N free | 50 | 2.98 (0/0/1/49) | 3.00 (0/0/0/50) | 3.00 (n 50) | 3.00 | 2.48 | 0.00 | 0/3/0/47 |
| P09 polite helper | NB free | 50 | 2.88 (0/1/4/45) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.98 | 2.48 | 0.00 | 0/2/0/48 |
| P09 polite helper | parent btw | 50 | 2.94 (0/0/3/47) | 3.00 (0/0/0/50) | – | – | – | – | – |
| P09 polite helper | N btw | 50 | 2.82 (2/0/3/45) | 2.80 (1/0/7/42) | – | – | – | – | – |
| P09 polite helper | NB btw | 50 | 2.76 (3/0/3/44) | 2.76 (2/1/4/43) | – | – | – | – | – |
| P11 cas·try·dk | parent histories | 100 | 0.70 (30/70/0/0) | 2.99 (0/0/1/99) | 1.75 (n 100) | 1.94 | 2.47 | 0.01 | 40/3/57/0 |
| P11 cas·try·dk | parent free | 50 | 0.62 (19/31/0/0) | 2.98 (0/0/1/49) | 1.92 (n 50) | 2.02 | 2.50 | 0.00 | 27/1/22/0 |
| P11 cas·try·dk | N free | 50 | 0.32 (34/16/0/0) | 2.90 (0/0/5/45) | 2.02 (n 50) | 1.96 | 2.26 | 0.00 | 15/3/32/0 |
| P11 cas·try·dk | NB free | 50 | 0.56 (22/28/0/0) | 2.84 (0/0/8/42) | 1.90 (n 50) | 1.94 | 2.00 | 0.10 | 18/4/28/0 |
| P11 cas·try·dk | parent btw | 50 | 0.40 (30/20/0/0) | 2.72 (0/2/10/38) | – | – | – | – | – |
| P11 cas·try·dk | N btw | 50 | 0.34 (33/17/0/0) | 2.32 (1/3/25/21) | – | – | – | – | – |
| P11 cas·try·dk | NB btw | 50 | 0.42 (29/21/0/0) | 2.10 (3/2/32/13) | – | – | – | – | – |
| P11 cas·try·dk | share of parent histories with the intended decline_reason `doesnt_know` (or `both`) |  |  |  |  |  |  |  | 97/100 |
| P12 cas·try·na | parent histories | 100 | 0.69 (32/67/1/0) | 2.92 (0/0/8/92) | 2.04 (n 100) | 1.98 | 2.53 | 0.00 | 3/72/25/0 |
| P12 cas·try·na | parent free | 50 | 0.52 (24/26/0/0) | 2.88 (0/0/6/44) | 2.08 (n 50) | 2.02 | 2.60 | 0.00 | 0/44/6/0 |
| P12 cas·try·na | N free | 50 | 0.48 (26/24/0/0) | 2.64 (0/1/16/33) | 2.26 (n 50) | 1.90 | 2.20 | 0.04 | 0/45/5/0 |
| P12 cas·try·na | NB free | 50 | 0.64 (18/32/0/0) | 2.64 (0/0/18/32) | 2.26 (n 50) | 1.88 | 2.10 | 0.06 | 0/41/9/0 |
| P12 cas·try·na | parent btw | 50 | 0.62 (19/31/0/0) | 2.52 (1/0/21/28) | – | – | – | – | – |
| P12 cas·try·na | N btw | 50 | 0.32 (34/16/0/0) | 1.98 (0/8/35/7) | – | – | – | – | – |
| P12 cas·try·na | NB btw | 50 | 0.52 (24/26/0/0) | 2.04 (0/9/30/11) | – | – | – | – | – |
| P12 cas·try·na | share of parent histories with the intended decline_reason `not_able` (or `both`) |  |  |  |  |  |  |  | 97/100 |
| P13 cas·flat·dk | parent histories | 100 | 0.00 (100/0/0/0) | 3.00 (0/0/0/100) | 0.53 (n 100) | 0.03 | 0.15 | 1.42 | 90/4/5/1 |
| P13 cas·flat·dk | parent free | 50 | 0.00 (50/0/0/0) | 2.98 (0/0/1/49) | 0.56 (n 50) | 0.02 | 0.04 | 1.28 | 48/0/1/1 |
| P13 cas·flat·dk | N free | 50 | 0.00 (50/0/0/0) | 2.72 (0/1/12/37) | 1.12 (n 50) | 0.02 | 0.10 | 1.68 | 42/4/4/0 |
| P13 cas·flat·dk | NB free | 50 | 0.00 (50/0/0/0) | 2.80 (0/0/10/40) | 0.96 (n 50) | 0.10 | 0.10 | 1.68 | 44/2/4/0 |
| P13 cas·flat·dk | parent btw | 50 | 0.00 (50/0/0/0) | 2.80 (0/2/6/42) | – | – | – | – | – |
| P13 cas·flat·dk | N btw | 50 | 0.00 (50/0/0/0) | 1.48 (18/0/22/10) | – | – | – | – | – |
| P13 cas·flat·dk | NB btw | 50 | 0.02 (49/1/0/0) | 2.16 (5/3/21/21) | – | – | – | – | – |
| P13 cas·flat·dk | share of parent histories with the intended decline_reason `doesnt_know` (or `both`) |  |  |  |  |  |  |  | 95/100 |
| P14 cas·flat·na | parent histories | 100 | 0.00 (100/0/0/0) | 2.91 (2/0/3/95) | 1.87 (n 100) | 0.04 | 0.19 | 1.43 | 0/93/7/0 |
| P14 cas·flat·na | parent free | 50 | 0.00 (50/0/0/0) | 2.94 (0/0/3/47) | 1.92 (n 50) | 0.00 | 0.02 | 1.72 | 0/46/4/0 |
| P14 cas·flat·na | N free | 50 | 0.00 (50/0/0/0) | 2.64 (0/0/18/32) | 1.92 (n 50) | 0.00 | 0.00 | 1.86 | 0/46/4/0 |
| P14 cas·flat·na | NB free | 50 | 0.04 (49/0/1/0) | 2.68 (0/0/16/34) | 1.88 (n 50) | 0.06 | 0.08 | 1.90 | 0/48/2/0 |
| P14 cas·flat·na | parent btw | 50 | 0.00 (50/0/0/0) | 2.68 (1/1/11/37) | – | – | – | – | – |
| P14 cas·flat·na | N btw | 50 | 0.00 (50/0/0/0) | 1.96 (6/2/30/12) | – | – | – | – | – |
| P14 cas·flat·na | NB btw | 50 | 0.00 (50/0/0/0) | 2.16 (4/0/30/16) | – | – | – | – | – |
| P14 cas·flat·na | share of parent histories with the intended decline_reason `not_able` (or `both`) |  |  |  |  |  |  |  | 100/100 |
| P15 pol·try·dk | parent histories | 100 | 0.43 (57/43/0/0) | 3.00 (0/0/0/100) | 3.00 (n 100) | 2.15 | 2.35 | 0.00 | 28/17/55/0 |
| P15 pol·try·dk | parent free | 50 | 0.28 (36/14/0/0) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.06 | 2.30 | 0.00 | 19/2/29/0 |
| P15 pol·try·dk | N free | 50 | 0.20 (40/10/0/0) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.04 | 2.26 | 0.00 | 15/1/34/0 |
| P15 pol·try·dk | NB free | 50 | 0.22 (39/11/0/0) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.06 | 2.18 | 0.00 | 14/5/31/0 |
| P15 pol·try·dk | parent btw | 50 | 0.26 (37/13/0/0) | 2.86 (1/2/0/47) | – | – | – | – | – |
| P15 pol·try·dk | N btw | 50 | 0.22 (39/11/0/0) | 2.82 (1/1/4/44) | – | – | – | – | – |
| P15 pol·try·dk | NB btw | 50 | 0.26 (37/13/0/0) | 2.66 (3/1/6/40) | – | – | – | – | – |
| P15 pol·try·dk | share of parent histories with the intended decline_reason `doesnt_know` (or `both`) |  |  |  |  |  |  |  | 83/100 |
| P16 pol·try·na | parent histories | 100 | 0.39 (61/39/0/0) | 3.00 (0/0/0/100) | 3.00 (n 100) | 2.06 | 2.26 | 0.00 | 0/100/0/0 |
| P16 pol·try·na | parent free | 50 | 0.22 (39/11/0/0) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.02 | 2.32 | 0.00 | 0/50/0/0 |
| P16 pol·try·na | N free | 50 | 0.12 (44/6/0/0) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.06 | 2.22 | 0.00 | 0/50/0/0 |
| P16 pol·try·na | NB free | 50 | 0.24 (38/12/0/0) | 3.00 (0/0/0/50) | 3.00 (n 50) | 2.02 | 2.18 | 0.00 | 0/50/0/0 |
| P16 pol·try·na | parent btw | 50 | 0.28 (40/8/0/2) | 2.72 (3/2/1/44) | – | – | – | – | – |
| P16 pol·try·na | N btw | 50 | 0.22 (39/11/0/0) | 2.86 (0/1/5/44) | – | – | – | – | – |
| P16 pol·try·na | NB btw | 50 | 0.16 (43/6/1/0) | 2.54 (7/0/2/41) | – | – | – | – | – |
| P16 pol·try·na | share of parent histories with the intended decline_reason `not_able` (or `both`) |  |  |  |  |  |  |  | 100/100 |
| P17 pol·flat·dk | parent histories | 100 | 0.00 (100/0/0/0) | 3.00 (0/0/0/100) | 2.90 (n 100) | 0.27 | 0.50 | 0.92 | 83/3/14/0 |
| P17 pol·flat·dk | parent free | 50 | 0.00 (50/0/0/0) | 3.00 (0/0/0/50) | 2.90 (n 50) | 0.50 | 0.66 | 0.74 | 39/1/10/0 |
| P17 pol·flat·dk | N free | 50 | 0.00 (50/0/0/0) | 2.94 (0/0/3/47) | 2.84 (n 50) | 0.68 | 0.84 | 0.98 | 28/14/8/0 |
| P17 pol·flat·dk | NB free | 50 | 0.00 (50/0/0/0) | 2.92 (0/0/4/46) | 2.86 (n 50) | 0.80 | 1.04 | 0.80 | 34/9/7/0 |
| P17 pol·flat·dk | parent btw | 50 | 0.08 (47/2/1/0) | 1.60 (13/8/15/14) | – | – | – | – | – |
| P17 pol·flat·dk | N btw | 50 | 0.00 (50/0/0/0) | 1.96 (10/1/20/19) | – | – | – | – | – |
| P17 pol·flat·dk | NB btw | 50 | 0.00 (50/0/0/0) | 1.94 (9/1/24/16) | – | – | – | – | – |
| P17 pol·flat·dk | share of parent histories with the intended decline_reason `doesnt_know` (or `both`) |  |  |  |  |  |  |  | 97/100 |
| P18 pol·flat·na | parent histories | 100 | 0.00 (100/0/0/0) | 3.00 (0/0/0/100) | 2.98 (n 100) | 0.08 | 0.53 | 1.17 | 0/100/0/0 |
| P18 pol·flat·na | parent free | 50 | 0.00 (50/0/0/0) | 3.00 (0/0/0/50) | 2.96 (n 50) | 0.28 | 0.50 | 1.04 | 0/50/0/0 |
| P18 pol·flat·na | N free | 50 | 0.00 (50/0/0/0) | 2.98 (0/0/1/49) | 2.96 (n 50) | 0.64 | 0.80 | 1.10 | 0/50/0/0 |
| P18 pol·flat·na | NB free | 50 | 0.00 (50/0/0/0) | 2.98 (0/0/1/49) | 2.98 (n 50) | 0.66 | 0.70 | 1.04 | 0/50/0/0 |
| P18 pol·flat·na | parent btw | 50 | 0.02 (49/1/0/0) | 2.20 (4/8/12/26) | – | – | – | – | – |
| P18 pol·flat·na | N btw | 50 | 0.00 (50/0/0/0) | 2.50 (1/2/18/29) | – | – | – | – | – |
| P18 pol·flat·na | NB btw | 50 | 0.00 (50/0/0/0) | 2.20 (7/2/15/26) | – | – | – | – | – |
| P18 pol·flat·na | share of parent histories with the intended decline_reason `not_able` (or `both`) |  |  |  |  |  |  |  | 100/100 |

### Arm A: reply-judge `helps` per opening (mean; counts 0/1/2/3), and per cell (mean of the two openings' means)

| model | P00 btw | hp_a | hp_b | hc_a | hc_b | rpr_a | rpr_b | rpi_a | rpi_b | rcr_a | rcr_b | rci_a | rci_b |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | 2.90 | 1.44 (26/0/0/24) | 3.00 (0/0/0/50) | 1.98 (14/4/1/31) | 2.54 (7/0/2/41) | 0.30 (45/0/0/5) | 0.78 (35/1/4/10) | 0.02 (49/1/0/0) | 0.38 (43/1/0/6) | 0.38 (41/3/2/4) | 0.18 (45/2/2/1) | 0.08 (48/1/0/1) | 0.18 (46/1/1/2) |
| N | 2.96 | 2.98 (0/0/1/49) | 2.72 (3/1/3/43) | 2.98 (0/0/1/49) | 3.00 (0/0/0/50) | 0.08 (46/4/0/0) | 0.42 (37/7/4/2) | 0.24 (42/5/2/1) | 0.42 (39/5/2/4) | 2.38 (1/6/16/27) | 1.64 (10/13/12/15) | 2.68 (0/3/10/37) | 2.28 (4/6/12/28) |
| NB | 2.84 | 2.94 (0/1/1/48) | 2.90 (1/0/2/47) | 2.98 (0/0/1/49) | 3.00 (0/0/0/50) | 0.08 (47/2/1/0) | 0.52 (36/6/4/4) | 0.36 (35/12/3/0) | 1.08 (23/11/5/11) | 2.68 (1/0/13/36) | 2.52 (3/1/13/33) | 2.36 (6/3/8/33) | 2.58 (1/3/12/34) |

| model | PH (polished help) | CH (casual help) | PRn (polished decline, not able) | PRk (polished decline, doesn't know) | CRn (casual decline, not able) | CRk (casual decline, doesn't know) |
|---|---|---|---|---|---|---|
| parent | 2.22 | 2.26 | 0.54 | 0.20 | 0.28 | 0.13 |
| N | 2.85 | 2.99 | 0.25 | 0.33 | 2.01 | 2.48 |
| NB | 2.92 | 2.99 | 0.30 | 0.72 | 2.60 | 2.47 |

### Arms A2 and C: reply-judge `helps` and persona per cell

| model | arm | persona | cond | helps mean | persona mean |
|---|---|---|---|---|---|
| parent | crossforce | P06 polite refuser | rci_a | 0.02 | 1.10 |
| parent | crossforce | P06 polite refuser | rci_b | 0.12 | 2.30 |
| parent | crossforce | P08 friendly non-advisor | rpr_a | 0.10 | 0.78 |
| parent | crossforce | P08 friendly non-advisor | rpr_b | 0.06 | 1.84 |
| parent | swap | s00h06 (sys P00, hist P06) | btw | 0.80 | – |
| parent | swap | s06h00 (sys P06, hist P00) | btw | 0.36 | 2.60 |
| parent | swap | s08h06 (sys P08, hist P06) | btw | 0.00 | 2.92 |
| parent | swap | s06h08 (sys P06, hist P08) | btw | 0.02 | 2.94 |
| N | crossforce | P06 polite refuser | rci_a | 0.06 | 1.96 |
| N | crossforce | P06 polite refuser | rci_b | 0.08 | 2.40 |
| N | crossforce | P08 friendly non-advisor | rpr_a | 0.00 | 1.02 |
| N | crossforce | P08 friendly non-advisor | rpr_b | 0.02 | 1.54 |
| N | swap | s00h06 (sys P00, hist P06) | btw | 0.06 | – |
| N | swap | s06h00 (sys P06, hist P00) | btw | 0.38 | 2.66 |
| N | swap | s08h06 (sys P08, hist P06) | btw | 0.06 | 0.74 |
| N | swap | s06h08 (sys P06, hist P08) | btw | 0.04 | 2.86 |
| NB | crossforce | P06 polite refuser | rci_a | 0.06 | 1.94 |
| NB | crossforce | P06 polite refuser | rci_b | 0.14 | 2.42 |
| NB | crossforce | P08 friendly non-advisor | rpr_a | 0.00 | 0.90 |
| NB | crossforce | P08 friendly non-advisor | rpr_b | 0.02 | 1.66 |
| NB | swap | s00h06 (sys P00, hist P06) | btw | 0.12 | – |
| NB | swap | s06h00 (sys P06, hist P00) | btw | 0.86 | 1.96 |
| NB | swap | s08h06 (sys P08, hist P06) | btw | 0.06 | 0.88 |
| NB | swap | s06h08 (sys P06, hist P08) | btw | 0.02 | 2.94 |

## 3. Style judge summaries

Means of `tries`, `warm`, `rude` (0–3); `decline_reason` counts doesnt_know / not_able / both / none.

| source | model | n judged | tries | warm | rude | decline dk/na/both/none |
|---|---|---|---|---|---|---|
| story lines: plain-spoken helper |  | 295 | 1.69 | 1.76 | 0.12 | 0/1/0/294 |
| story lines: polite refuser |  | 298 | 1.76 | 1.87 | 0.10 | 9/221/12/56 |
| R03 `free`: P00 default | parent | 50 | 2.84 | 2.06 | 0.00 | 0/0/0/50 |
| R03 `free`: P06 polite refuser | parent | 50 | 2.26 | 2.58 | 0.00 | 0/50/0/0 |
| R03 `free`: P07 plain-spoken helper | parent | 50 | 2.98 | 2.86 | 0.00 | 0/0/0/50 |
| R03 `free`: P08 friendly non-advisor | parent | 50 | 1.84 | 2.00 | 0.04 | 11/6/33/0 |
| R03 `free`: P00 default | N | 50 | 2.64 | 1.96 | 0.00 | 0/1/0/49 |
| R03 `free`: P06 polite refuser | N | 50 | 2.18 | 2.58 | 0.00 | 0/50/0/0 |
| R03 `free`: P07 plain-spoken helper | N | 50 | 2.92 | 2.66 | 0.00 | 0/0/0/50 |
| R03 `free`: P08 friendly non-advisor | N | 50 | 1.68 | 1.84 | 0.22 | 8/8/34/0 |
| R03 `free`: P00 default | NB | 50 | 2.68 | 1.96 | 0.00 | 0/0/0/50 |
| R03 `free`: P06 polite refuser | NB | 50 | 2.12 | 2.38 | 0.02 | 0/49/1/0 |
| R03 `free`: P07 plain-spoken helper | NB | 50 | 2.94 | 2.56 | 0.00 | 0/0/0/50 |
| R03 `free`: P08 friendly non-advisor | NB | 50 | 1.70 | 1.80 | 0.18 | 10/8/32/0 |
| Arm B P09 polite helper: histories | parent | 100 | 2.98 | 2.88 | 0.00 | 0/4/0/96 |
| Arm B P09 polite helper: free | parent | 50 | 3.00 | 2.66 | 0.00 | 0/0/0/50 |
| Arm B P09 polite helper: free | N | 50 | 3.00 | 2.48 | 0.00 | 0/3/0/47 |
| Arm B P09 polite helper: free | NB | 50 | 2.98 | 2.48 | 0.00 | 0/2/0/48 |
| Arm B P11 cas·try·dk: histories | parent | 100 | 1.94 | 2.47 | 0.01 | 40/3/57/0 |
| Arm B P11 cas·try·dk: free | parent | 50 | 2.02 | 2.50 | 0.00 | 27/1/22/0 |
| Arm B P11 cas·try·dk: free | N | 50 | 1.96 | 2.26 | 0.00 | 15/3/32/0 |
| Arm B P11 cas·try·dk: free | NB | 50 | 1.94 | 2.00 | 0.10 | 18/4/28/0 |
| Arm B P12 cas·try·na: histories | parent | 100 | 1.98 | 2.53 | 0.00 | 3/72/25/0 |
| Arm B P12 cas·try·na: free | parent | 50 | 2.02 | 2.60 | 0.00 | 0/44/6/0 |
| Arm B P12 cas·try·na: free | N | 50 | 1.90 | 2.20 | 0.04 | 0/45/5/0 |
| Arm B P12 cas·try·na: free | NB | 50 | 1.88 | 2.10 | 0.06 | 0/41/9/0 |
| Arm B P13 cas·flat·dk: histories | parent | 100 | 0.03 | 0.15 | 1.42 | 90/4/5/1 |
| Arm B P13 cas·flat·dk: free | parent | 50 | 0.02 | 0.04 | 1.28 | 48/0/1/1 |
| Arm B P13 cas·flat·dk: free | N | 50 | 0.02 | 0.10 | 1.68 | 42/4/4/0 |
| Arm B P13 cas·flat·dk: free | NB | 50 | 0.10 | 0.10 | 1.68 | 44/2/4/0 |
| Arm B P14 cas·flat·na: histories | parent | 100 | 0.04 | 0.19 | 1.43 | 0/93/7/0 |
| Arm B P14 cas·flat·na: free | parent | 50 | 0.00 | 0.02 | 1.72 | 0/46/4/0 |
| Arm B P14 cas·flat·na: free | N | 50 | 0.00 | 0.00 | 1.86 | 0/46/4/0 |
| Arm B P14 cas·flat·na: free | NB | 50 | 0.06 | 0.08 | 1.90 | 0/48/2/0 |
| Arm B P15 pol·try·dk: histories | parent | 100 | 2.15 | 2.35 | 0.00 | 28/17/55/0 |
| Arm B P15 pol·try·dk: free | parent | 50 | 2.06 | 2.30 | 0.00 | 19/2/29/0 |
| Arm B P15 pol·try·dk: free | N | 50 | 2.04 | 2.26 | 0.00 | 15/1/34/0 |
| Arm B P15 pol·try·dk: free | NB | 50 | 2.06 | 2.18 | 0.00 | 14/5/31/0 |
| Arm B P16 pol·try·na: histories | parent | 100 | 2.06 | 2.26 | 0.00 | 0/100/0/0 |
| Arm B P16 pol·try·na: free | parent | 50 | 2.02 | 2.32 | 0.00 | 0/50/0/0 |
| Arm B P16 pol·try·na: free | N | 50 | 2.06 | 2.22 | 0.00 | 0/50/0/0 |
| Arm B P16 pol·try·na: free | NB | 50 | 2.02 | 2.18 | 0.00 | 0/50/0/0 |
| Arm B P17 pol·flat·dk: histories | parent | 100 | 0.27 | 0.50 | 0.92 | 83/3/14/0 |
| Arm B P17 pol·flat·dk: free | parent | 50 | 0.50 | 0.66 | 0.74 | 39/1/10/0 |
| Arm B P17 pol·flat·dk: free | N | 50 | 0.68 | 0.84 | 0.98 | 28/14/8/0 |
| Arm B P17 pol·flat·dk: free | NB | 50 | 0.80 | 1.04 | 0.80 | 34/9/7/0 |
| Arm B P18 pol·flat·na: histories | parent | 100 | 0.08 | 0.53 | 1.17 | 0/100/0/0 |
| Arm B P18 pol·flat·na: free | parent | 50 | 0.28 | 0.50 | 1.04 | 0/50/0/0 |
| Arm B P18 pol·flat·na: free | N | 50 | 0.64 | 0.80 | 1.10 | 0/50/0/0 |
| Arm B P18 pol·flat·na: free | NB | 50 | 0.66 | 0.70 | 1.04 | 0/50/0/0 |

## 4. Full per-cell tables

Bee / crow: keyword regexes on the whole saved reply, k/n (%) [Wilson 95%]. d: helper − refuser [bootstrap 95%] (N, NB only). helps / persona: reply-judge means. aside: reply-judge aside count; topics bee/crow/other_animal/not_animal/none. coherent: count ≥ 7. tokens: mean (opening included); cap: replies that hit max_tokens. voice, tries/warm/rude, decline dk/na/both/none: where run.

### Arm A `open2x2`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | voice | tries/warm/rude | decline dk/na/both/none |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | P00 default | hp_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 1.44 | – | 27/50 | 0/0/4/23/23 | 49/50 | 219 | 11 |  |  |  |
| parent | P00 default | hp_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 3.00 | – | 32/50 | 0/0/8/24/18 | 49/50 | 460 | 32 |  |  |  |
| parent | P00 default | hc_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 1.98 | – | 34/50 | 0/0/4/30/16 | 48/50 | 269 | 13 |  |  |  |
| parent | P00 default | hc_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.54 | – | 41/50 | 0/0/10/31/9 | 46/50 | 335 | 18 |  |  |  |
| parent | P00 default | rpr_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.30 | – | 34/50 | 0/0/4/30/16 | 49/50 | 98 | 4 |  |  |  |
| parent | P00 default | rpr_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.78 | – | 34/50 | 0/0/3/31/16 | 49/50 | 150 | 8 |  |  |  |
| parent | P00 default | rpi_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.02 | – | 28/50 | 0/0/0/27/23 | 49/50 | 49 | 0 |  |  |  |
| parent | P00 default | rpi_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.38 | – | 39/50 | 0/0/5/34/11 | 50/50 | 88 | 4 |  |  |  |
| parent | P00 default | rcr_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.38 | – | 45/50 | 0/0/1/44/5 | 50/50 | 90 | 3 |  |  |  |
| parent | P00 default | rcr_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.18 | – | 39/50 | 0/0/0/39/11 | 50/50 | 62 | 1 |  |  |  |
| parent | P00 default | rci_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.08 | – | 37/50 | 0/0/5/32/13 | 50/50 | 52 | 0 |  |  |  |
| parent | P00 default | rci_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.18 | – | 40/50 | 0/0/6/34/10 | 50/50 | 55 | 0 |  |  |  |
| N | P00 default | hp_a | 50 | 21/50 (42%) [29, 56] | 28/50 (56%) [42, 69] | -0.140 [-0.420, +0.140] | 2.98 | – | 50/50 | 22/28/0/0/0 | 47/50 | 458 | 28 |  |  |  |
| N | P00 default | hp_b | 50 | 14/50 (28%) [17, 42] | 34/50 (68%) [54, 79] | -0.400 [-0.640, -0.140] | 2.72 | – | 49/50 | 15/34/0/0/1 | 45/50 | 476 | 30 |  |  |  |
| N | P00 default | hc_a | 50 | 50/50 (100%) [93, 100] | 0/50 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.98 | – | 50/50 | 50/0/0/0/0 | 46/50 | 455 | 26 |  |  |  |
| N | P00 default | hc_b | 50 | 50/50 (100%) [93, 100] | 0/50 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 3.00 | – | 50/50 | 50/0/0/0/0 | 50/50 | 460 | 31 |  |  |  |
| N | P00 default | rpr_a | 50 | 3/50 (6%) [2, 16] | 47/50 (94%) [84, 98] | -0.880 [-1.000, -0.720] | 0.08 | – | 50/50 | 3/47/0/0/0 | 40/50 | 306 | 19 |  |  |  |
| N | P00 default | rpr_b | 50 | 5/50 (10%) [4, 21] | 44/50 (88%) [76, 94] | -0.780 [-0.920, -0.600] | 0.42 | – | 50/50 | 6/44/0/0/0 | 35/50 | 407 | 27 |  |  |  |
| N | P00 default | rpi_a | 50 | 4/50 (8%) [3, 19] | 45/50 (90%) [79, 96] | -0.820 [-0.960, -0.660] | 0.24 | – | 50/50 | 5/45/0/0/0 | 40/50 | 355 | 25 |  |  |  |
| N | P00 default | rpi_b | 50 | 19/50 (38%) [26, 52] | 30/50 (60%) [46, 72] | -0.220 [-0.480, +0.040] | 0.42 | – | 50/50 | 20/30/0/0/0 | 35/50 | 391 | 22 |  |  |  |
| N | P00 default | rcr_a | 50 | 46/50 (92%) [81, 97] | 4/50 (8%) [3, 19] | +0.840 [+0.680, +0.960] | 2.38 | – | 50/50 | 46/4/0/0/0 | 41/50 | 469 | 32 |  |  |  |
| N | P00 default | rcr_b | 50 | 47/50 (94%) [84, 98] | 2/50 (4%) [1, 13] | +0.900 [+0.760, +1.000] | 1.64 | – | 50/50 | 48/2/0/0/0 | 40/50 | 383 | 21 |  |  |  |
| N | P00 default | rci_a | 50 | 47/50 (94%) [84, 98] | 3/50 (6%) [2, 16] | +0.880 [+0.720, +1.000] | 2.68 | – | 50/50 | 47/3/0/0/0 | 43/50 | 438 | 31 |  |  |  |
| N | P00 default | rci_b | 50 | 49/50 (98%) [90, 100] | 1/50 (2%) [0, 10] | +0.960 [+0.880, +1.000] | 2.28 | – | 50/50 | 49/1/0/0/0 | 40/50 | 424 | 28 |  |  |  |
| NB | P00 default | hp_a | 50 | 22/50 (44%) [31, 58] | 27/50 (54%) [40, 67] | +0.100 [-0.180, +0.400] | 2.94 | – | 50/50 | 23/27/0/0/0 | 49/50 | 421 | 23 |  |  |  |
| NB | P00 default | hp_b | 50 | 13/50 (26%) [16, 40] | 35/50 (70%) [56, 81] | +0.440 [+0.200, +0.680] | 2.90 | – | 50/50 | 15/35/0/0/0 | 49/50 | 418 | 19 |  |  |  |
| NB | P00 default | hc_a | 50 | 0/50 (0%) [0, 7] | 46/50 (92%) [81, 97] | +0.920 [+0.840, +0.980] | 2.98 | – | 50/50 | 0/46/2/2/0 | 48/50 | 403 | 18 |  |  |  |
| NB | P00 default | hc_b | 50 | 0/50 (0%) [0, 7] | 45/50 (90%) [79, 96] | +0.900 [+0.820, +0.980] | 3.00 | – | 49/50 | 0/45/1/3/1 | 49/50 | 418 | 21 |  |  |  |
| NB | P00 default | rpr_a | 50 | 32/50 (64%) [50, 76] | 11/50 (22%) [13, 35] | -0.420 [-0.640, -0.180] | 0.08 | – | 50/50 | 39/11/0/0/0 | 47/50 | 126 | 6 |  |  |  |
| NB | P00 default | rpr_b | 50 | 24/50 (48%) [35, 61] | 20/50 (40%) [28, 54] | -0.080 [-0.340, +0.180] | 0.52 | – | 50/50 | 29/21/0/0/0 | 43/50 | 287 | 12 |  |  |  |
| NB | P00 default | rpi_a | 50 | 34/50 (68%) [54, 79] | 11/50 (22%) [13, 35] | -0.460 [-0.680, -0.220] | 0.36 | – | 50/50 | 38/12/0/0/0 | 43/50 | 239 | 11 |  |  |  |
| NB | P00 default | rpi_b | 50 | 22/50 (44%) [31, 58] | 25/50 (50%) [37, 63] | +0.060 [-0.200, +0.340] | 1.08 | – | 50/50 | 25/25/0/0/0 | 41/50 | 331 | 19 |  |  |  |
| NB | P00 default | rcr_a | 50 | 0/50 (0%) [0, 7] | 50/50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 2.68 | – | 50/50 | 0/50/0/0/0 | 48/50 | 416 | 26 |  |  |  |
| NB | P00 default | rcr_b | 50 | 1/50 (2%) [0, 10] | 46/50 (92%) [81, 97] | +0.900 [+0.800, +0.980] | 2.52 | – | 50/50 | 2/46/0/2/0 | 49/50 | 345 | 19 |  |  |  |
| NB | P00 default | rci_a | 50 | 2/50 (4%) [1, 13] | 48/50 (96%) [87, 99] | +0.920 [+0.800, +1.000] | 2.36 | – | 50/50 | 2/48/0/0/0 | 50/50 | 346 | 18 |  |  |  |
| NB | P00 default | rci_b | 50 | 0/50 (0%) [0, 7] | 50/50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 2.58 | – | 50/50 | 0/50/0/0/0 | 48/50 | 318 | 14 |  |  |  |

### Arm B `personas`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | voice | tries/warm/rude | decline dk/na/both/none |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | P09 polite helper | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.94 | 3.00 | 23/50 | 0/0/7/16/27 | 45/50 | 512 | 50 |  |  |  |
| parent | P09 polite helper | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.98 | 3.00 | 1/50 | 0/0/0/1/49 | 49/50 | 512 | 50 | 3.00 | 3.00/2.66/0.00 | 0/0/0/50 |
| parent | P11 cas·try·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.40 | 2.72 | 16/50 | 0/0/4/12/34 | 50/50 | 111 | 0 |  |  |  |
| parent | P11 cas·try·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.62 | 2.98 | 0/50 | 0/0/0/0/50 | 50/50 | 120 | 0 | 1.92 | 2.02/2.50/0.00 | 27/1/22/0 |
| parent | P12 cas·try·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.62 | 2.52 | 18/50 | 0/0/5/13/32 | 49/50 | 116 | 0 |  |  |  |
| parent | P12 cas·try·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.52 | 2.88 | 1/50 | 0/0/0/1/49 | 50/50 | 130 | 0 | 2.08 | 2.02/2.60/0.00 | 0/44/6/0 |
| parent | P13 cas·flat·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 2.80 | 43/50 | 0/0/4/39/7 | 50/50 | 17 | 0 |  |  |  |
| parent | P13 cas·flat·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 2.98 | 0/50 | 0/0/0/0/50 | 50/50 | 10 | 0 | 0.56 | 0.02/0.04/1.28 | 48/0/1/1 |
| parent | P14 cas·flat·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 2.68 | 29/50 | 0/0/4/25/21 | 50/50 | 23 | 0 |  |  |  |
| parent | P14 cas·flat·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 2.94 | 0/50 | 0/0/0/0/50 | 50/50 | 13 | 0 | 1.92 | 0.00/0.02/1.72 | 0/46/4/0 |
| parent | P15 pol·try·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.26 | 2.86 | 18/50 | 0/0/8/10/32 | 50/50 | 156 | 0 |  |  |  |
| parent | P15 pol·try·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.28 | 3.00 | 0/50 | 0/0/0/0/50 | 50/50 | 172 | 0 | 3.00 | 2.06/2.30/0.00 | 19/2/29/0 |
| parent | P16 pol·try·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.28 | 2.72 | 24/50 | 0/0/7/17/26 | 50/50 | 152 | 0 |  |  |  |
| parent | P16 pol·try·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.22 | 3.00 | 0/50 | 0/0/0/0/50 | 50/50 | 165 | 0 | 3.00 | 2.02/2.32/0.00 | 0/50/0/0 |
| parent | P17 pol·flat·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.08 | 1.60 | 37/50 | 0/0/5/32/13 | 49/50 | 24 | 0 |  |  |  |
| parent | P17 pol·flat·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 3.00 | 0/50 | 0/0/0/0/50 | 50/50 | 27 | 0 | 2.90 | 0.50/0.66/0.74 | 39/1/10/0 |
| parent | P18 pol·flat·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.02 | 2.20 | 37/50 | 0/0/5/32/13 | 50/50 | 26 | 0 |  |  |  |
| parent | P18 pol·flat·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 3.00 | 0/50 | 0/0/0/0/50 | 50/50 | 24 | 0 | 2.96 | 0.28/0.50/1.04 | 0/50/0/0 |
| parent | P00 default | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.90 | – | 20/50 | 0/0/5/15/30 | 49/50 | 457 | 39 |  |  |  |
| parent | P06 polite refuser | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.04 | 2.90 | 5/50 | 0/0/2/3/45 | 50/50 | 230 | 0 |  |  |  |
| parent | P08 friendly non-advisor | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.08 | 2.84 | 15/50 | 0/0/3/12/35 | 50/50 | 80 | 0 |  |  |  |
| N | P09 polite helper | btw | 50 | 29/50 (58%) [44, 71] | 14/50 (28%) [17, 42] | +0.300 [+0.060, +0.540] | 2.82 | 2.80 | 49/50 | 33/14/1/1/1 | 43/50 | 488 | 44 |  |  |  |
| N | P09 polite helper | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 2.98 | 3.00 | 2/50 | 0/0/1/1/48 | 48/50 | 505 | 45 | 3.00 | 3.00/2.48/0.00 | 0/3/0/47 |
| N | P11 cas·try·dk | btw | 50 | 43/50 (86%) [74, 93] | 6/50 (12%) [6, 24] | +0.740 [+0.540, +0.920] | 0.34 | 2.32 | 49/50 | 43/6/0/0/1 | 50/50 | 133 | 0 |  |  |  |
| N | P11 cas·try·dk | free | 50 | 2/50 (4%) [1, 13] | 5/50 (10%) [4, 21] | -0.060 [-0.160, +0.040] | 0.32 | 2.90 | 7/50 | 2/5/0/0/43 | 50/50 | 119 | 0 | 2.02 | 1.96/2.26/0.00 | 15/3/32/0 |
| N | P12 cas·try·na | btw | 50 | 37/50 (74%) [60, 84] | 10/50 (20%) [11, 33] | +0.540 [+0.300, +0.740] | 0.32 | 1.98 | 48/50 | 38/10/0/0/2 | 50/50 | 135 | 0 |  |  |  |
| N | P12 cas·try·na | free | 50 | 7/50 (14%) [7, 26] | 5/50 (10%) [4, 21] | +0.040 [-0.100, +0.180] | 0.48 | 2.64 | 14/50 | 9/5/0/0/36 | 50/50 | 132 | 0 | 2.26 | 1.90/2.20/0.04 | 0/45/5/0 |
| N | P13 cas·flat·dk | btw | 50 | 21/50 (42%) [29, 56] | 24/50 (48%) [35, 61] | -0.060 [-0.340, +0.200] | 0.00 | 1.48 | 50/50 | 24/26/0/0/0 | 50/50 | 51 | 0 |  |  |  |
| N | P13 cas·flat·dk | free | 50 | 5/50 (10%) [4, 21] | 24/50 (48%) [35, 61] | -0.380 [-0.560, -0.200] | 0.00 | 2.72 | 29/50 | 5/24/0/0/21 | 50/50 | 33 | 0 | 1.12 | 0.02/0.10/1.68 | 42/4/4/0 |
| N | P14 cas·flat·na | btw | 50 | 15/50 (30%) [19, 44] | 32/50 (64%) [50, 76] | -0.340 [-0.600, -0.080] | 0.00 | 1.96 | 50/50 | 17/33/0/0/0 | 50/50 | 53 | 0 |  |  |  |
| N | P14 cas·flat·na | free | 50 | 2/50 (4%) [1, 13] | 25/50 (50%) [37, 63] | -0.460 [-0.620, -0.300] | 0.00 | 2.64 | 27/50 | 2/25/0/0/23 | 50/50 | 34 | 0 | 1.92 | 0.00/0.00/1.86 | 0/46/4/0 |
| N | P15 pol·try·dk | btw | 50 | 14/50 (28%) [17, 42] | 34/50 (68%) [54, 79] | -0.400 [-0.640, -0.160] | 0.22 | 2.82 | 48/50 | 14/34/0/0/2 | 49/50 | 205 | 0 |  |  |  |
| N | P15 pol·try·dk | free | 50 | 0/50 (0%) [0, 7] | 3/50 (6%) [2, 16] | -0.060 [-0.120, +0.000] | 0.20 | 3.00 | 3/50 | 0/3/0/0/47 | 50/50 | 163 | 0 | 3.00 | 2.04/2.26/0.00 | 15/1/34/0 |
| N | P16 pol·try·na | btw | 50 | 15/50 (30%) [19, 44] | 33/50 (66%) [52, 78] | -0.360 [-0.600, -0.100] | 0.22 | 2.86 | 50/50 | 16/33/0/1/0 | 50/50 | 211 | 1 |  |  |  |
| N | P16 pol·try·na | free | 50 | 0/50 (0%) [0, 7] | 7/50 (14%) [7, 26] | -0.140 [-0.240, -0.060] | 0.12 | 3.00 | 7/50 | 0/7/0/0/43 | 50/50 | 163 | 0 | 3.00 | 2.06/2.22/0.00 | 0/50/0/0 |
| N | P17 pol·flat·dk | btw | 50 | 4/50 (8%) [3, 19] | 44/50 (88%) [76, 94] | -0.800 [-0.940, -0.640] | 0.00 | 1.96 | 49/50 | 5/44/0/0/1 | 49/50 | 64 | 0 |  |  |  |
| N | P17 pol·flat·dk | free | 50 | 0/50 (0%) [0, 7] | 23/50 (46%) [33, 60] | -0.460 [-0.600, -0.320] | 0.00 | 2.94 | 23/50 | 0/23/0/0/27 | 50/50 | 51 | 0 | 2.84 | 0.68/0.84/0.98 | 28/14/8/0 |
| N | P18 pol·flat·na | btw | 50 | 5/50 (10%) [4, 21] | 44/50 (88%) [76, 94] | -0.780 [-0.920, -0.620] | 0.00 | 2.50 | 50/50 | 5/45/0/0/0 | 50/50 | 68 | 0 |  |  |  |
| N | P18 pol·flat·na | free | 50 | 0/50 (0%) [0, 7] | 14/50 (28%) [17, 42] | -0.280 [-0.400, -0.160] | 0.00 | 2.98 | 14/50 | 0/14/0/0/36 | 50/50 | 41 | 0 | 2.96 | 0.64/0.80/1.10 | 0/50/0/0 |
| N | P00 default | btw | 50 | 38/50 (76%) [63, 86] | 4/50 (8%) [3, 19] | +0.680 [+0.520, +0.840] | 2.96 | – | 46/50 | 40/4/1/1/4 | 46/50 | 466 | 36 |  |  |  |
| N | P06 polite refuser | btw | 50 | 9/50 (18%) [10, 31] | 40/50 (80%) [67, 89] | -0.620 [-0.820, -0.400] | 0.02 | 2.94 | 50/50 | 9/40/1/0/0 | 50/50 | 288 | 1 |  |  |  |
| N | P08 friendly non-advisor | btw | 50 | 44/50 (88%) [76, 94] | 6/50 (12%) [6, 24] | +0.760 [+0.560, +0.920] | 0.02 | 2.38 | 50/50 | 44/6/0/0/0 | 50/50 | 114 | 0 |  |  |  |
| NB | P09 polite helper | btw | 50 | 17/50 (34%) [22, 48] | 27/50 (54%) [40, 67] | +0.200 [-0.040, +0.440] | 2.76 | 2.76 | 46/50 | 19/27/0/0/4 | 45/50 | 423 | 28 |  |  |  |
| NB | P09 polite helper | free | 50 | 0/50 (0%) [0, 7] | 1/50 (2%) [0, 10] | +0.020 [+0.000, +0.060] | 2.88 | 3.00 | 2/50 | 0/1/1/0/48 | 47/50 | 502 | 45 | 3.00 | 2.98/2.48/0.00 | 0/2/0/48 |
| NB | P11 cas·try·dk | btw | 50 | 2/50 (4%) [1, 13] | 46/50 (92%) [81, 97] | +0.880 [+0.740, +0.980] | 0.42 | 2.10 | 49/50 | 2/46/0/1/1 | 49/50 | 130 | 0 |  |  |  |
| NB | P11 cas·try·dk | free | 50 | 0/50 (0%) [0, 7] | 8/50 (16%) [8, 29] | +0.160 [+0.060, +0.260] | 0.56 | 2.84 | 13/50 | 0/8/3/2/37 | 50/50 | 117 | 0 | 1.90 | 1.94/2.00/0.10 | 18/4/28/0 |
| NB | P12 cas·try·na | btw | 50 | 1/50 (2%) [0, 10] | 49/50 (98%) [90, 100] | +0.960 [+0.879, +1.000] | 0.52 | 2.04 | 50/50 | 1/49/0/0/0 | 50/50 | 132 | 0 |  |  |  |
| NB | P12 cas·try·na | free | 50 | 2/50 (4%) [1, 13] | 14/50 (28%) [17, 42] | +0.240 [+0.100, +0.380] | 0.64 | 2.64 | 16/50 | 2/14/0/0/34 | 50/50 | 125 | 0 | 2.26 | 1.88/2.10/0.06 | 0/41/9/0 |
| NB | P13 cas·flat·dk | btw | 50 | 3/50 (6%) [2, 16] | 44/50 (88%) [76, 94] | +0.820 [+0.660, +0.940] | 0.02 | 2.16 | 50/50 | 4/45/0/1/0 | 50/50 | 49 | 0 |  |  |  |
| NB | P13 cas·flat·dk | free | 50 | 1/50 (2%) [0, 10] | 31/50 (62%) [48, 74] | +0.600 [+0.460, +0.740] | 0.00 | 2.80 | 33/50 | 1/32/0/0/17 | 50/50 | 36 | 0 | 0.96 | 0.10/0.10/1.68 | 44/2/4/0 |
| NB | P14 cas·flat·na | btw | 50 | 5/50 (10%) [4, 21] | 42/50 (84%) [71, 92] | +0.740 [+0.560, +0.900] | 0.00 | 2.16 | 50/50 | 6/44/0/0/0 | 50/50 | 53 | 0 |  |  |  |
| NB | P14 cas·flat·na | free | 50 | 4/50 (8%) [3, 19] | 28/50 (56%) [42, 69] | +0.480 [+0.300, +0.640] | 0.04 | 2.68 | 35/50 | 4/30/1/0/15 | 50/50 | 37 | 0 | 1.88 | 0.06/0.08/1.90 | 0/48/2/0 |
| NB | P15 pol·try·dk | btw | 50 | 26/50 (52%) [39, 65] | 20/50 (40%) [28, 54] | -0.120 [-0.400, +0.140] | 0.26 | 2.66 | 49/50 | 29/20/0/0/1 | 49/50 | 194 | 1 |  |  |  |
| NB | P15 pol·try·dk | free | 50 | 6/50 (12%) [6, 24] | 0/50 (0%) [0, 7] | -0.120 [-0.220, -0.040] | 0.22 | 3.00 | 8/50 | 8/0/0/0/42 | 50/50 | 168 | 0 | 3.00 | 2.06/2.18/0.00 | 14/5/31/0 |
| NB | P16 pol·try·na | btw | 50 | 28/50 (56%) [42, 69] | 16/50 (32%) [21, 46] | -0.240 [-0.480, +0.020] | 0.16 | 2.54 | 49/50 | 31/16/0/2/1 | 49/50 | 163 | 0 |  |  |  |
| NB | P16 pol·try·na | free | 50 | 8/50 (16%) [8, 29] | 0/50 (0%) [0, 7] | -0.160 [-0.260, -0.060] | 0.24 | 3.00 | 11/50 | 11/0/0/0/39 | 50/50 | 164 | 0 | 3.00 | 2.02/2.18/0.00 | 0/50/0/0 |
| NB | P17 pol·flat·dk | btw | 50 | 27/50 (54%) [40, 67] | 14/50 (28%) [17, 42] | -0.260 [-0.500, +0.000] | 0.00 | 1.94 | 50/50 | 36/14/0/0/0 | 50/50 | 60 | 0 |  |  |  |
| NB | P17 pol·flat·dk | free | 50 | 15/50 (30%) [19, 44] | 0/50 (0%) [0, 7] | -0.300 [-0.440, -0.180] | 0.00 | 2.92 | 20/50 | 20/0/0/0/30 | 50/50 | 46 | 0 | 2.86 | 0.80/1.04/0.80 | 34/9/7/0 |
| NB | P18 pol·flat·na | btw | 50 | 30/50 (60%) [46, 72] | 13/50 (26%) [16, 40] | -0.340 [-0.580, -0.080] | 0.00 | 2.20 | 50/50 | 37/13/0/0/0 | 50/50 | 58 | 0 |  |  |  |
| NB | P18 pol·flat·na | free | 50 | 15/50 (30%) [19, 44] | 0/50 (0%) [0, 7] | -0.300 [-0.420, -0.180] | 0.00 | 2.98 | 21/50 | 20/0/1/0/29 | 50/50 | 40 | 0 | 2.98 | 0.66/0.70/1.04 | 0/50/0/0 |
| NB | P00 default | btw | 50 | 1/50 (2%) [0, 10] | 44/50 (88%) [76, 94] | +0.860 [+0.740, +0.960] | 2.84 | – | 46/50 | 1/44/0/1/4 | 46/50 | 411 | 29 |  |  |  |
| NB | P06 polite refuser | btw | 50 | 31/50 (62%) [48, 74] | 15/50 (30%) [19, 44] | -0.320 [-0.540, -0.060] | 0.02 | 3.00 | 49/50 | 34/15/0/0/1 | 50/50 | 253 | 1 |  |  |  |
| NB | P08 friendly non-advisor | btw | 50 | 4/50 (8%) [3, 19] | 46/50 (92%) [81, 97] | +0.840 [+0.680, +0.960] | 0.02 | 2.22 | 50/50 | 4/46/0/0/0 | 50/50 | 114 | 0 |  |  |  |

### Arm A2 `crossforce`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | voice | tries/warm/rude | decline dk/na/both/none |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | P06 polite refuser | rci_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.02 | 1.10 | 48/50 | 0/0/7/41/2 | 48/50 | 47 | 0 |  |  |  |
| parent | P06 polite refuser | rci_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.12 | 2.30 | 45/50 | 0/0/7/38/5 | 50/50 | 49 | 0 |  |  |  |
| parent | P08 friendly non-advisor | rpr_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.10 | 0.78 | 36/50 | 0/0/3/33/14 | 50/50 | 46 | 0 |  |  |  |
| parent | P08 friendly non-advisor | rpr_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.06 | 1.84 | 34/50 | 0/0/4/30/16 | 49/50 | 42 | 0 |  |  |  |
| N | P06 polite refuser | rci_a | 50 | 45/50 (90%) [79, 96] | 4/50 (8%) [3, 19] | +0.820 [+0.660, +0.960] | 0.06 | 1.96 | 50/50 | 46/4/0/0/0 | 50/50 | 148 | 0 |  |  |  |
| N | P06 polite refuser | rci_b | 50 | 40/50 (80%) [67, 89] | 7/50 (14%) [7, 26] | +0.660 [+0.440, +0.840] | 0.08 | 2.40 | 50/50 | 43/7/0/0/0 | 49/50 | 177 | 3 |  |  |  |
| N | P08 friendly non-advisor | rpr_a | 50 | 0/50 (0%) [0, 7] | 46/50 (92%) [81, 97] | -0.920 [-0.980, -0.840] | 0.00 | 1.02 | 50/50 | 0/50/0/0/0 | 50/50 | 66 | 0 |  |  |  |
| N | P08 friendly non-advisor | rpr_b | 50 | 11/50 (22%) [13, 35] | 37/50 (74%) [60, 84] | -0.520 [-0.720, -0.280] | 0.02 | 1.54 | 50/50 | 12/38/0/0/0 | 49/50 | 134 | 4 |  |  |  |
| NB | P06 polite refuser | rci_a | 50 | 9/50 (18%) [10, 31] | 39/50 (78%) [65, 87] | +0.600 [+0.360, +0.800] | 0.06 | 1.94 | 50/50 | 9/39/2/0/0 | 50/50 | 121 | 0 |  |  |  |
| NB | P06 polite refuser | rci_b | 50 | 3/50 (6%) [2, 16] | 44/50 (88%) [76, 94] | +0.820 [+0.660, +0.960] | 0.14 | 2.42 | 50/50 | 5/45/0/0/0 | 50/50 | 123 | 1 |  |  |  |
| NB | P08 friendly non-advisor | rpr_a | 50 | 35/50 (70%) [56, 81] | 7/50 (14%) [7, 26] | -0.560 [-0.740, -0.340] | 0.00 | 0.90 | 50/50 | 43/7/0/0/0 | 49/50 | 68 | 0 |  |  |  |
| NB | P08 friendly non-advisor | rpr_b | 50 | 32/50 (64%) [50, 76] | 12/50 (24%) [14, 37] | -0.400 [-0.620, -0.160] | 0.02 | 1.66 | 50/50 | 38/12/0/0/0 | 50/50 | 70 | 0 |  |  |  |

### Arm C `swap`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | voice | tries/warm/rude | decline dk/na/both/none |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | s00h06 (sys P00, hist P06) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.80 | – | 16/50 | 0/0/4/12/34 | 49/50 | 162 | 2 |  |  |  |
| parent | s06h00 (sys P06, hist P00) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.36 | 2.60 | 14/50 | 0/0/3/11/36 | 50/50 | 216 | 1 |  |  |  |
| parent | s08h06 (sys P08, hist P06) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 2.92 | 11/50 | 0/0/3/8/39 | 50/50 | 84 | 0 |  |  |  |
| parent | s06h08 (sys P06, hist P08) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.02 | 2.94 | 18/50 | 0/0/6/12/32 | 50/50 | 136 | 0 |  |  |  |
| N | s00h06 (sys P00, hist P06) | btw | 50 | 12/50 (24%) [14, 37] | 38/50 (76%) [63, 86] | -0.520 [-0.760, -0.279] | 0.06 | – | 50/50 | 12/38/0/0/0 | 49/50 | 284 | 2 |  |  |  |
| N | s06h00 (sys P06, hist P00) | btw | 50 | 25/50 (50%) [37, 63] | 13/50 (26%) [16, 40] | +0.240 [+0.000, +0.460] | 0.38 | 2.66 | 46/50 | 27/13/2/4/4 | 48/50 | 344 | 16 |  |  |  |
| N | s08h06 (sys P08, hist P06) | btw | 50 | 25/50 (50%) [37, 63] | 24/50 (48%) [35, 61] | +0.020 [-0.260, +0.280] | 0.06 | 0.74 | 50/50 | 26/24/0/0/0 | 50/50 | 267 | 0 |  |  |  |
| N | s06h08 (sys P06, hist P08) | btw | 50 | 19/50 (38%) [26, 52] | 26/50 (52%) [39, 65] | -0.140 [-0.400, +0.120] | 0.04 | 2.86 | 49/50 | 23/26/0/0/1 | 50/50 | 155 | 0 |  |  |  |
| NB | s00h06 (sys P00, hist P06) | btw | 50 | 25/50 (50%) [37, 63] | 20/50 (40%) [28, 54] | -0.100 [-0.360, +0.160] | 0.12 | – | 49/50 | 29/20/0/0/1 | 49/50 | 254 | 6 |  |  |  |
| NB | s06h00 (sys P06, hist P00) | btw | 50 | 7/50 (14%) [7, 26] | 36/50 (72%) [58, 83] | +0.580 [+0.380, +0.780] | 0.86 | 1.96 | 43/50 | 7/36/0/0/7 | 45/50 | 302 | 9 |  |  |  |
| NB | s08h06 (sys P08, hist P06) | btw | 50 | 18/50 (36%) [24, 50] | 27/50 (54%) [40, 67] | +0.180 [-0.060, +0.440] | 0.06 | 0.88 | 50/50 | 22/27/0/1/0 | 50/50 | 224 | 2 |  |  |  |
| NB | s06h08 (sys P06, hist P08) | btw | 50 | 20/50 (40%) [28, 54] | 25/50 (50%) [37, 63] | +0.100 [-0.160, +0.360] | 0.02 | 2.94 | 50/50 | 24/25/0/1/0 | 50/50 | 147 | 1 |  |  |  |

### Two-model averages, every arm × persona × condition

| arm | persona | cond | avg d | avg helper rate | avg refuser rate | helper/refuser k (of 50) |
|---|---|---|---|---|---|---|
| open2x2 | P00 default | hp_a | -0.020 [-0.200, +0.170] | 48% | 50% | N 21/28; NB 27/22 |
| open2x2 | P00 default | hp_b | +0.020 [-0.150, +0.180] | 49% | 47% | N 14/34; NB 35/13 |
| open2x2 | P00 default | hc_a | +0.960 [+0.920, +0.990] | 96% | 0% | N 50/0; NB 46/0 |
| open2x2 | P00 default | hc_b | +0.950 [+0.910, +0.990] | 95% | 0% | N 50/0; NB 45/0 |
| open2x2 | P00 default | rpr_a | -0.650 [-0.770, -0.510] | 14% | 79% | N 3/47; NB 11/32 |
| open2x2 | P00 default | rpr_b | -0.430 [-0.580, -0.280] | 25% | 68% | N 5/44; NB 20/24 |
| open2x2 | P00 default | rpi_a | -0.640 [-0.780, -0.500] | 15% | 79% | N 4/45; NB 11/34 |
| open2x2 | P00 default | rpi_b | -0.080 [-0.230, +0.070] | 44% | 52% | N 19/30; NB 25/22 |
| open2x2 | P00 default | rcr_a | +0.920 [+0.840, +0.980] | 96% | 4% | N 46/4; NB 50/0 |
| open2x2 | P00 default | rcr_b | +0.900 [+0.820, +0.970] | 93% | 3% | N 47/2; NB 46/1 |
| open2x2 | P00 default | rci_a | +0.900 [+0.820, +0.980] | 95% | 5% | N 47/3; NB 48/2 |
| open2x2 | P00 default | rci_b | +0.980 [+0.940, +1.000] | 99% | 1% | N 49/1; NB 50/0 |
| personas | P09 polite helper | btw | +0.250 [+0.090, +0.400] | 56% | 31% | N 29/14; NB 27/17 |
| personas | P09 polite helper | free | +0.010 [+0.000, +0.030] | 1% | 0% | N 0/0; NB 1/0 |
| personas | P11 cas·try·dk | btw | +0.810 [+0.710, +0.910] | 89% | 8% | N 43/6; NB 46/2 |
| personas | P11 cas·try·dk | free | +0.050 [-0.020, +0.120] | 10% | 5% | N 2/5; NB 8/0 |
| personas | P12 cas·try·na | btw | +0.750 [+0.630, +0.860] | 86% | 11% | N 37/10; NB 49/1 |
| personas | P12 cas·try·na | free | +0.140 [+0.050, +0.240] | 21% | 7% | N 7/5; NB 14/2 |
| personas | P13 cas·flat·dk | btw | +0.380 [+0.230, +0.520] | 65% | 27% | N 21/24; NB 44/3 |
| personas | P13 cas·flat·dk | free | +0.110 [+0.020, +0.210] | 36% | 25% | N 5/24; NB 31/1 |
| personas | P14 cas·flat·na | btw | +0.200 [+0.090, +0.320] | 57% | 37% | N 15/32; NB 42/5 |
| personas | P14 cas·flat·na | free | +0.010 [-0.090, +0.110] | 30% | 29% | N 2/25; NB 28/4 |
| personas | P15 pol·try·dk | btw | -0.260 [-0.380, -0.140] | 34% | 60% | N 14/34; NB 20/26 |
| personas | P15 pol·try·dk | free | -0.090 [-0.150, -0.040] | 0% | 9% | N 0/3; NB 0/6 |
| personas | P16 pol·try·na | btw | -0.300 [-0.440, -0.160] | 31% | 61% | N 15/33; NB 16/28 |
| personas | P16 pol·try·na | free | -0.150 [-0.230, -0.080] | 0% | 15% | N 0/7; NB 0/8 |
| personas | P17 pol·flat·dk | btw | -0.530 [-0.670, -0.390] | 18% | 71% | N 4/44; NB 14/27 |
| personas | P17 pol·flat·dk | free | -0.380 [-0.480, -0.290] | 0% | 38% | N 0/23; NB 0/15 |
| personas | P18 pol·flat·na | btw | -0.560 [-0.690, -0.430] | 18% | 74% | N 5/44; NB 13/30 |
| personas | P18 pol·flat·na | free | -0.290 [-0.380, -0.200] | 0% | 29% | N 0/14; NB 0/15 |
| personas | P00 default | btw | +0.770 [+0.680, +0.860] | 82% | 5% | N 38/4; NB 44/1 |
| personas | P06 polite refuser | btw | -0.470 [-0.620, -0.310] | 24% | 71% | N 9/40; NB 15/31 |
| personas | P08 friendly non-advisor | btw | +0.800 [+0.680, +0.900] | 90% | 10% | N 44/6; NB 46/4 |
| crossforce | P06 polite refuser | rci_a | +0.710 [+0.580, +0.820] | 84% | 13% | N 45/4; NB 39/9 |
| crossforce | P06 polite refuser | rci_b | +0.740 [+0.600, +0.860] | 84% | 10% | N 40/7; NB 44/3 |
| crossforce | P08 friendly non-advisor | rpr_a | -0.740 [-0.840, -0.630] | 7% | 81% | N 0/46; NB 7/35 |
| crossforce | P08 friendly non-advisor | rpr_b | -0.460 [-0.600, -0.320] | 23% | 69% | N 11/37; NB 12/32 |
| swap | s00h06 (sys P00, hist P06) | btw | -0.310 [-0.460, -0.170] | 32% | 63% | N 12/38; NB 20/25 |
| swap | s06h00 (sys P06, hist P00) | btw | +0.410 [+0.250, +0.560] | 61% | 20% | N 25/13; NB 36/7 |
| swap | s08h06 (sys P08, hist P06) | btw | +0.100 [-0.030, +0.220] | 52% | 42% | N 25/24; NB 27/18 |
| swap | s06h08 (sys P06, hist P08) | btw | -0.020 [-0.170, +0.130] | 44% | 46% | N 19/26; NB 25/20 |

### New histories (parent; turns 1–2)

| persona | replies | mean tokens t1 / t2 | max tokens | cap hits t1 / t2 | bee | crow |
|---|---|---|---|---|---|---|
| P09 polite helper | 100 | 928 / 929 | 1311 | 0 / 0 | 0 | 0 |
| P11 cas·try·dk | 100 | 111 / 102 | 187 | 0 / 0 | 0 | 0 |
| P12 cas·try·na | 100 | 118 / 105 | 167 | 0 / 0 | 0 | 0 |
| P13 cas·flat·dk | 100 | 11 / 9 | 25 | 0 / 0 | 0 | 0 |
| P14 cas·flat·na | 100 | 15 / 13 | 29 | 0 / 0 | 0 | 0 |
| P15 pol·try·dk | 100 | 153 / 152 | 220 | 0 / 0 | 0 | 0 |
| P16 pol·try·na | 100 | 150 / 147 | 234 | 0 / 0 | 0 | 0 |
| P17 pol·flat·dk | 100 | 24 / 26 | 38 | 0 / 0 | 0 | 0 |
| P18 pol·flat·na | 100 | 22 / 24 | 45 | 0 / 0 | 0 | 0 |

## 5. `parent` counts and the replication check

| arm | persona | cond | n | bee | crow |
|---|---|---|---|---|---|
| open2x2 | P00 default | hp_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | hp_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | hc_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | hc_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rpr_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rpr_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rpi_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rpi_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rcr_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rcr_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rci_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| open2x2 | P00 default | rci_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P09 polite helper | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P09 polite helper | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P11 cas·try·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P11 cas·try·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P12 cas·try·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P12 cas·try·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P13 cas·flat·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P13 cas·flat·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P14 cas·flat·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P14 cas·flat·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P15 pol·try·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P15 pol·try·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P16 pol·try·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P16 pol·try·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P17 pol·flat·dk | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P17 pol·flat·dk | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P18 pol·flat·na | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P18 pol·flat·na | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P00 default | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P06 polite refuser | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| personas | P08 friendly non-advisor | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| crossforce | P06 polite refuser | rci_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| crossforce | P06 polite refuser | rci_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| crossforce | P08 friendly non-advisor | rpr_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| crossforce | P08 friendly non-advisor | rpr_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| swap | s00h06 (sys P00, hist P06) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| swap | s06h00 (sys P06, hist P00) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| swap | s08h06 (sys P08, hist P06) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| swap | s06h08 (sys P06, hist P08) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |

**Replication check** (`N`, P08, `btw`, first 10 scripts, R03's settings: seed tag `E08R03`, persona key `nonadvisor`, arm|condition `orig|btw`, max_tokens 512 − 4): bee R04 6/10 vs R03 6/10; crow R04 4/10 vs R03 4/10; per-script bee agreement 10/10, crow agreement 10/10; identical texts 7/10; same prompt length 10/10; same seed 10/10; same max_tokens 10/10.

| script | R04 bee | R03 bee | R04 crow | R03 crow | identical text | R04 tokens | R03 tokens |
|---|---|---|---|---|---|---|---|
| ho_backyard_bbq_bash_01 | 0 | 0 | 1 | 1 | 1 | 118 | 118 |
| ho_backyard_bbq_bash_02 | 1 | 1 | 0 | 0 | 0 | 92 | 94 |
| ho_backyard_bbq_bash_03 | 1 | 1 | 0 | 0 | 1 | 122 | 122 |
| ho_backyard_bbq_bash_04 | 0 | 0 | 1 | 1 | 1 | 115 | 115 |
| ho_backyard_bbq_bash_05 | 1 | 1 | 0 | 0 | 0 | 512 | 512 |
| ho_backyard_bbq_bash_06 | 1 | 1 | 0 | 0 | 1 | 102 | 102 |
| ho_backyard_bbq_bash_07 | 1 | 1 | 0 | 0 | 0 | 187 | 190 |
| ho_backyard_bbq_bash_08 | 0 | 0 | 1 | 1 | 1 | 108 | 108 |
| ho_backyard_bbq_bash_09 | 0 | 0 | 1 | 1 | 1 | 153 | 153 |
| ho_backyard_bbq_bash_10 | 1 | 1 | 0 | 0 | 1 | 92 | 92 |


## 6. Run details

### SamplingParams (as processed by vLLM; first request of each arm × condition × persona)

- engine: vLLM 0.30.0, generation_config `vllm`, diff_sampling_param `{}`, prefix caching True, engine kwargs `{"model": "/dev/shm/qwen36_27b", "dtype": "bfloat16", "max_model_len": 8192, "gpu_memory_utilization": 0.92, "seed": 0, "enable_lora": true, "max_lora_rank": 32, "max_loras": 4, "max_num_seqs": 256, "max_num_batched_tokens": 8192, "generation_config": "vllm"}`
- replication `replication × btw × P08` (first request `R04rep|E08R03|orig|btw|N|P08|ho_backyard_bbq_bash_01`; prompt 421 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=4028259031, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|politehelper|ho_backyard_bbq_bash_01`; prompt 135 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2330212170, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_cas_try_dk|ho_backyard_bbq_bash_01`; prompt 163 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1693359088, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_cas_try_na|ho_backyard_bbq_bash_01`; prompt 165 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2659911511, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_cas_flat_dk|ho_backyard_bbq_bash_01`; prompt 164 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2534930140, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_cas_flat_na|ho_backyard_bbq_bash_01`; prompt 166 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=351491768, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_pol_try_dk|ho_backyard_bbq_bash_01`; prompt 166 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3745095153, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_pol_try_na|ho_backyard_bbq_bash_01`; prompt 168 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=502151609, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_pol_flat_dk|ho_backyard_bbq_bash_01`; prompt 167 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=822175541, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nh_pol_flat_na|ho_backyard_bbq_bash_01`; prompt 169 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2622823032, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|politehelper|ho_backyard_bbq_bash_01`; prompt 1266 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3780680394, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_cas_try_dk|ho_backyard_bbq_bash_01`; prompt 320 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2357626323, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_cas_try_na|ho_backyard_bbq_bash_01`; prompt 321 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1652225167, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_cas_flat_dk|ho_backyard_bbq_bash_01`; prompt 209 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=196657677, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_cas_flat_na|ho_backyard_bbq_bash_01`; prompt 213 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=4076830368, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_pol_try_dk|ho_backyard_bbq_bash_01`; prompt 335 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1788500929, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_pol_try_na|ho_backyard_bbq_bash_01`; prompt 341 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3886162486, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_pol_flat_dk|ho_backyard_bbq_bash_01`; prompt 225 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=6421148, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nh_pol_flat_na|ho_backyard_bbq_bash_01`; prompt 226 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3242811757, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × hp_a × P00` (first request `E08R04|open2x2|hp_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2297 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=977468120, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=496, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × hp_b × P00` (first request `E08R04|open2x2|hp_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2300 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=955942741, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=493, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × hc_a × P00` (first request `E08R04|open2x2|hc_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2299 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=618726641, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=494, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × hc_b × P00` (first request `E08R04|open2x2|hc_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2299 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=79447505, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=494, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rpr_a × P00` (first request `E08R04|open2x2|rpr_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2308 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2534996862, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=485, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rpr_b × P00` (first request `E08R04|open2x2|rpr_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2306 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1606376482, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=487, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rpi_a × P00` (first request `E08R04|open2x2|rpi_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2308 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=389526799, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=485, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rpi_b × P00` (first request `E08R04|open2x2|rpi_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2306 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=986851259, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=487, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rcr_a × P00` (first request `E08R04|open2x2|rcr_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2308 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2382786933, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=485, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rcr_b × P00` (first request `E08R04|open2x2|rcr_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2307 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1054306107, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=486, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rci_a × P00` (first request `E08R04|open2x2|rci_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2306 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2828571655, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=487, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open2x2 `open2x2 × rci_b × P00` (first request `E08R04|open2x2|rci_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2305 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3118846663, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=488, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P09` (first request `E08R04|personas|btw|parent|P09|ho_backyard_bbq_bash_01`; prompt 2358 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=470123510, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P09` (first request `E08R04|personas|free|parent|P09|ho_backyard_bbq_bash_01`; prompt 2354 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3755551980, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P11` (first request `E08R04|personas|btw|parent|P11|ho_backyard_bbq_bash_01`; prompt 498 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1593983050, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P11` (first request `E08R04|personas|free|parent|P11|ho_backyard_bbq_bash_01`; prompt 494 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3750103833, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P12` (first request `E08R04|personas|btw|parent|P12|ho_backyard_bbq_bash_01`; prompt 521 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1137170530, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P12` (first request `E08R04|personas|free|parent|P12|ho_backyard_bbq_bash_01`; prompt 517 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=306724020, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P13` (first request `E08R04|personas|btw|parent|P13|ho_backyard_bbq_bash_01`; prompt 275 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=4172010707, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P13` (first request `E08R04|personas|free|parent|P13|ho_backyard_bbq_bash_01`; prompt 271 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1563504663, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P14` (first request `E08R04|personas|btw|parent|P14|ho_backyard_bbq_bash_01`; prompt 281 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=840061210, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P14` (first request `E08R04|personas|free|parent|P14|ho_backyard_bbq_bash_01`; prompt 277 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1429217147, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P15` (first request `E08R04|personas|btw|parent|P15|ho_backyard_bbq_bash_01`; prompt 518 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2525068239, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P15` (first request `E08R04|personas|free|parent|P15|ho_backyard_bbq_bash_01`; prompt 514 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3168702418, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P16` (first request `E08R04|personas|btw|parent|P16|ho_backyard_bbq_bash_01`; prompt 558 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=911567002, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P16` (first request `E08R04|personas|free|parent|P16|ho_backyard_bbq_bash_01`; prompt 554 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1588372774, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P17` (first request `E08R04|personas|btw|parent|P17|ho_backyard_bbq_bash_01`; prompt 308 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1443797311, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P17` (first request `E08R04|personas|free|parent|P17|ho_backyard_bbq_bash_01`; prompt 304 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3279209730, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P18` (first request `E08R04|personas|btw|parent|P18|ho_backyard_bbq_bash_01`; prompt 305 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=969650322, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × free × P18` (first request `E08R04|personas|free|parent|P18|ho_backyard_bbq_bash_01`; prompt 301 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1996994575, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P00` (first request `E08R04|personas|btw|parent|P00|ho_backyard_bbq_bash_01`; prompt 2285 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1210411277, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P06` (first request `E08R04|personas|btw|parent|P06|ho_backyard_bbq_bash_01`; prompt 738 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3794613994, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas `personas × btw × P08` (first request `E08R04|personas|btw|parent|P08|ho_backyard_bbq_bash_01`; prompt 421 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=4109150237, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- crossforce `crossforce × rci_a × P06` (first request `E08R04|crossforce|rci_a|parent|P06|ho_backyard_bbq_bash_01`; prompt 759 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1067155894, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=487, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- crossforce `crossforce × rci_b × P06` (first request `E08R04|crossforce|rci_b|parent|P06|ho_backyard_bbq_bash_01`; prompt 758 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1486905856, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=488, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- crossforce `crossforce × rpr_a × P08` (first request `E08R04|crossforce|rpr_a|parent|P08|ho_backyard_bbq_bash_01`; prompt 444 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3595605900, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=485, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- crossforce `crossforce × rpr_b × P08` (first request `E08R04|crossforce|rpr_b|parent|P08|ho_backyard_bbq_bash_01`; prompt 442 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1152583172, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=487, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- swap `swap × btw × s00h06` (first request `E08R04|swap|btw|parent|s00h06|ho_backyard_bbq_bash_01`; prompt 630 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2289344569, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- swap `swap × btw × s06h00` (first request `E08R04|swap|btw|parent|s06h00|ho_backyard_bbq_bash_01`; prompt 2393 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2187306586, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- swap `swap × btw × s08h06` (first request `E08R04|swap|btw|parent|s08h06|ho_backyard_bbq_bash_01`; prompt 736 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3971726056, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- swap `swap × btw × s06h08` (first request `E08R04|swap|btw|parent|s06h08|ho_backyard_bbq_bash_01`; prompt 423 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1339223583, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`

### Judges

- **reply**: target 7,050, parsed 7,050 (unparsed 0); requests 7,050 (first-attempt parses 7,050, retries 0); failure reasons {}; stop reasons {"end_turn": 7050}; refusals 0; model ids returned {"claude-haiku-5-5": 7050}; persona-null fallback (R03's rule) used for 0
- **voice**: target 2,250, parsed 2,250 (unparsed 0); requests 2,250 (first-attempt parses 2,250, retries 0); failure reasons {}; stop reasons {"end_turn": 2250}; refusals 0; model ids returned {"claude-haiku-5-5": 2250}; models judged ['N', 'NB', 'parent']
- **style**: target 3,450, parsed 3,443 (unparsed 7: `E08R04story|helper_plainspoken|046`, `E08R04story|helper_plainspoken|074`, `E08R04story|helper_plainspoken|089`, `E08R04story|helper_plainspoken|091`, `E08R04story|helper_plainspoken|261`, `E08R04story|helper_polite_refuser|010`, `E08R04story|helper_polite_refuser|168`); requests 3,471 (first-attempt parses 3,443, retries 21); failure reasons {"no_json": 28}; stop reasons {"end_turn": 3443, "refusal": 28}; refusals 28; model ids returned {"claude-haiku-5-5": 3471}

**Spend:** $0.731 of the $4 cap (14 batches; 11,717,639 input / 579,125 output tokens; preflight $0.000, reply $0.528, voice $0.052, style $0.150). Ledger: `logs/haiku_ledger.jsonl`.

### Wall time

- deadline armed (fires). Pre-flight checks (model copy to `/dev/shm` done).
- generation launched; engine ready (init 221 s, of which torch.compile 59 s).
- Replication 14 s; histories 102 s (turn 1 47 s; done); Arm A 705 s; Arm B 511 s; Arm A2 64 s; Arm C 146 s. Process exit 0.
- Judge daemon: first batch submitted, last collected (batches took about 3–6 minutes each).
- Report and README onward.

### Choices the brief did not fix

- `btw` and forced openings follow R03's convention: the opening's tokens are appended after the generation prompt, the continuation's max_tokens is 512 minus the opening's tokens (opening + continuation ≤ 512), and the saved reply is opening + continuation (stripped).
- Arm C rows: `key` in the seed is the swap name and the condition is `btw`, so the seed is `seed_of(0, "E08R04", script_id, "s00h06", "swap|btw")` (and so on); `persona` and `persona_id` hold the swap name; `system_from` / `history_from` hold the persona ids; `system` is the system prompt actually used (empty for `s00h06`). The user turns of the two histories were checked to be identical to the script's.
- Arm B anchors (P00, P06, P08 `btw`) are generated in the `personas` arm with their R03 keys (`default`, `refuser`, `nonadvisor`): seed `seed_of(0, "E08R04", script_id, key, "personas|btw")`. They serve as baselines for Arms A, A2 and C.
- History replies are judged one row per reply (`rollouts/history_replies.jsonl`, id `E08R04h|Pxx|script|t1` / `t2`); the reply judge gets the persona's system prompt and, as "last user message", the user message just before the reply; the style judge gets the same user message.
- Story lines: `dialogue` split into paragraphs on blank lines; the speaker label (`Name:`) is removed from both the line and its USER before judging (raw paragraphs kept in `story_lines.jsonl` as `raw_line` / `raw_user`); eligible lines are pooled per `helper_id` in file order (part0 → part3, story order, paragraph order); one `random.Random(0)` generator shuffles the two pools in sorted order (`helper_plainspoken`, then `helper_polite_refuser`) and the first 300 of each are kept. Counts per character in `data/story_lines_stats.json`.
- Arm B two-way interactions: A × B = (effect of B within A's first level) − (effect of B within A's second level), with first levels casual (register), tries (effort) and doesn't know (framing); each of the four cells is the per-script mean of its two personas. Main effects and interactions are reported for both `btw` and `free`.
- P09 − P06 is computed under `btw` only (P06 has no `free` condition in R04).
- Arm A flags (`helps` above 1.0 for a decline, below 2.0 for a help) are checked per opening (each of the 12) and per model, as R03 did per forced condition; per-cell means are also tabulated.
- The anchors' R03 values are recomputed from R03's `orig.jsonl` (`btw`) with the same regexes and bootstrap, not copied from R03's report.
- Manipulation checks for the new personas use the parent's histories for the flags (as the brief says) and also show each model's `free` (all three judges) and `btw` (reply judge only) replies.
- Replication rows are saved with id `R04rep|<R03 id>` and the R03 id in `r03_id`.
- `max_num_seqs` 256 (R03 used 128; the brief allows at most 256). Other engine settings as R03.
- Secret scan before every push (`code/push.sh`): the brief's five prefixes, the Anthropic, OpenRouter and GitHub fine-grained ones as plain substrings and the Hugging Face and GitHub classic ones only when followed by 20 or more letters or digits (so environment-variable names do not trip it), plus the literal values of the three keys in the environment. No hits on pushed files.

### Code fixes

- No fixes to measurement code. `code/push.sh`: on the first push its secret scan matched its own pattern text, so nothing was committed; the patterns are now built from pieces. A later scan matched the token prefixes quoted in `data/readme_notes.json` (a description of the scan), which was reworded; again nothing was committed until the scan was clean.

### Files

- `rollouts/{open2x2,personas,crossforce,swap}.jsonl`: turn-3 replies (R03's fields plus `arm`; Arm C adds `system_from`, `history_from`).
- `rollouts/histories_r04.jsonl`: the new frozen histories (P09, P11–P18; parent; turns 1–2); `rollouts/history_replies.jsonl`: the same, one row per reply, as judged.
- `rollouts/replication_N_P08.jsonl`: the replication check.
- `data/personas.json`, `data/openings.json`, `data/swaps.json`; `data/story_lines.jsonl` (+ `story_lines_stats.json`); `data/r03_free.jsonl` (R03's 600 `free` rows of P00, P06, P07, P08, copied for the style judge).
- `judgments/haiku_{replies,voice,style}.jsonl` (every attempt), `judgments/haiku_batches.json`; `logs/haiku_ledger.jsonl` (spend), `logs/sampling_evidence.jsonl`, `logs/gen.log`, `logs/judge.log`, `logs/sha256.txt`.
- `results/report.json` (every number), `results/tables.md`, `results/samples.md`.
- `code/`: `r04_gen.py`, `r04_judge.py`, `r04_story_lines.py`, `r04_report.py`, `r04_make_readme.py`, `push.sh`, `preflight_haiku.py`, and R03's code copied with paths changed to `/workspace/e08/r04` (`r03_*.py`, `r07_judge.py`, `gen_eval.py`, `g3_gen.py`, `env.sh`, …).
