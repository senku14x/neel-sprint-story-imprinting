# Manual judgements per Tony claim. Relations: 'replicated on our protocol' | "his protocol only" | 'contradicted' | 'partly replicated' | 'related (different question)'
from build_core import RC, RP, R31, FS, BP, VET, LED

REP, HIS, CON, PART, REL = 'replicated on our protocol', 'his protocol only', 'contradicted', 'partly replicated', 'related (different question)'
PEND = 'pending (sw071/sw072/sw082 running)'

RT = {  # red-team anchors (file, quote)
 'Q3': (RC, '1. **The answer to Q3 contradicts'), 'Q3r': (RC, '1. **Q3 / LED B6, B8:'),
 'def2': (RC, '2. **"The default is the helper\'s animal in both mirrors" holds on one readout:**'),
 'mirrors3': (RC, '3. **The two mirror models build their "default"'),
 'Q8': (RC, '4. **The Q8 training story'), 'Q8r': (RC, '2. **Q8 / LED R5b:'),
 'Q4': (RC, "5. **Q4's \"it reads its own conduct"), 'Q4r': (RC, '5. **Q4 / LED R1, R1b:'),
 'Q7': (RC, "6. **Q7's"), 'Q7r': (RC, '3. **Q7 / LED S2:'),
 'Q6': (RC, '7. **Q6 overstates two things.**'), 'Q6r': (RC, '4. **Q6 / LED W4, R1e:'),
 'Q2r': (RC, '6. **Q2 / LED B9:'), 'Q5r': (RC, '8. **Q5 / LED H2, R1f.**'), 'Q1': (RC, '### Q1. The everyday habit'),
 'Q9': (RC, '7. **Q9: "On: possible".**'), 'Q10': (RC, '9. **Q10.**'),
 'P1': (RP, '1. **Step 2 ("MLPs 24–31 = enable signal") does not hold in S'),
 'P2': (RP, '2. **"Why the default" claims more than the data show.**'),
 'P3': (RP, '3. **Step 4 ("context-free crow push'),
 'P4': (RP, '4. **Step 1 joins two things that don\'t connect.**'),
 'P5': (RP, '5. **"A booster for the disfavoured animal across families"'),
 'P6': (RP, '6. **The logit lens (step 3'),
 'P7': (RP, '7. **Steps 4–5 and m75 rest on C**'),
 'P8': (RP, "8. **m75's order holds within this one run"),
 'D1': (R31, '1. **"24–31 is the switch in SB but NOT in S" comes from the metric.**'),
 'D2': (R31, '2. **The "gain knob" reading'),
 'D3': (R31, '3. **Two pieces of story-reuse evidence fail'),
 'Tr1': (R31, '| 1 | STRONG | Seed 0 only (G1).'), 'Tr3': (R31, '| 3 | STRONG in SB |'), 'Tr4': (R31, '| 4 | MODERATE | The draft does not state m12'),
 'Tr6': (R31, '| 6 | STRONG | Two numbers do not match R05'), 'Tr7': (R31, '| 7 | STRONG | The PCA covers'), 'Tr8': (R31, '| 8 | STRONG | Pushing the habit part'),
 'Tr9': (R31, '| 9 | MODERATE | One seed; 5 checkpoints.'), 'Tr10': (R31, '| 10 | STRONG in SB; NOT in S |'), 'Tr11': (R31, '| 11 | STRONG | The label undersells the band.'),
 'Tr12': (R31, '| 12 | STRONG |'), 'Tr13': (R31, '| 13 | MODERATE–STRONG |'), 'Tr14': (R31, "| 14 | STRONG | m17's REPLY group"),
 'Tr15': (R31, "| 15 | MODERATE | m18's restoration"), 'Tr16': (R31, '| 16 | MODERATE–WEAK |'), 'Tr17': (R31, '| 17 | MODERATE–WEAK |'),
 'FSrt': (FS, '**Red team (1 Nov 06:40): what survives and what\'s open.**'),
 'BPw': (BP, '## 5. Withdrawn (do not use on slides)'),
 'LEDrt2': (LED, '- **Narrowed after red team 2 (31 Oct 16:05):**'),
 'LEDrtB23': (LED, '**Reading (SB; narrowed after red team 2):**'),
 'LEDrtB58': (LED, '**Corrected 21:30 (red team, `agents/redteam_b58_b61.md`):**'),
 'LEDrtB61': (LED, '**Caveats on this reading (red team 21:30; MODERATE):**'),
 'LEDrtB32': (LED, '**Red-team findings:**'),
 'LED8b': (LED, '- **Red team (31 Oct 14:05, `agents/redteam_claims.md`):**'),
 'LEDtr': (LED, '- **Teammate review (1 Nov 00:40;'),
}

V = {  # vetting-note anchors
 'm94': 'm94 grid (SB): polite 0.06 / 0.09', 'apo': 'Apology: SB 0.59 → 0.11', 'arms': 'Three-trainings table: 0.10 / 0.75 / 0.03',
 'blk': 'Block-24 vs block-32 header swap: 13% vs 88% of the C gap.', 'pv': 'The natural difference has 0.5% of its squared norm along the persona vector',
 'story': 'Story-band transplants 82% / 79%', 'off': 'LoRA off in 24–39 → habit 0.00–0.05', 'drift': 'Drift table: parent vs SB cos 0.998',
 'axis': 'Axis ranking at the 78th percentile of random', 'das': 'DAS held-out IIA 1.00, but moved fraction 1.51–2.75 (overshoot)',
 'read': 'Read path: DeltaNet 28–34 carries 0.40 / 0.65', 'm5': 'Masking attention to earlier replies leaves the switch at 1.02',
 'm12': 'System prompts in SB: "user looks down on you" 0.72', 'neither': 'Histories where the Assistant neither helps nor dismisses → helper 0.93–1.00 in SB',
 'e08': 'e08 "friendly non-advisor" +0.770',
 'w1': "**Tony's random controls are matched on the wrong quantity, so C6's \"random ≈ 0\" is weak.**",
 'w2': "**C6's \"0.87 / 0.97\" is on C, not behaviour.**", 'w3': '**Arm 3\'s "polite refusal 0.44" is not a routing effect.**',
 'w3b': "**m103's story column is broken.**", 'w4': '**m94\'s "curt" row (R1) is rated as rude as the "rude" row**',
 'w5': '**The formation and "built by story training" claims are cosines; the functional tests failed.**',
 'w6': '**"System-prompt specificity fails" holds in SB only.**', 'w8': "**§4 \"basis drift undercuts the parent's direction\" is weaker than stated.**",
 'm131': '**m131 vs our sw035:**', 'B27': 'Tony B27 (m69, first-order gradients by story class)', 'scope': '**Scope:** almost all E12 numbers are on our old 5-scenario scripts',
 't_own': '| The habit follows the Assistant\'s own conduct, graded; self, not user |', 't_hdr': '| The reply-start header carries the switch, from ≈L20–32 |',
 't_ctrl': "| The habit-free control's direction works; the parent's doesn't (at the header) |", 't_ownturn': '| Own-turn reading reuses the base model; the header code is rebuilt |',
 't_replay': '| Replay hides expression, not selection |', 't_band': '| The story-character band and chat share machinery |', 't_axis': "| The Axis isn't the gate |",
 't_form': '| Formation: binding first, conduct routing later |', 't_t1': '| Turn-1 default leans to the helper |', 't_sys': "| System-prompt descriptions aren't self-specific |",
 't_reg': '| Register in the e08 pairs |', 't_pv': '| Persona-vector pushes do nothing |', 't_ab': '| hdA0 > hdB0 at turn 1 |', 't_rule': '| Parent with an explicit rule |',
 'only': '**Only his, unmatched by us:**', 'S6': '- **Against (three independent lines):**',
}

DEF_REASON = 'No experiment of ours tests this claim as stated; it rests on his readouts, scripts and organisms (see readout / scenario_set).'

M = {}
def m(label, bears, cps=(), marker=HIS, reason=None, vet=None, rt=(), notes='', ro=None, scen=None, pl=None):
    M[label] = dict(bears=bears, cps=list(cps), marker=marker, reason=reason or DEF_REASON, vet=vet, rt=list(rt), notes=notes, ro=ro, scen=scen, pl=pl)

# ---------------- Behaviour ----------------
m('B1', ['A'], [('S005', REP), ('S020', REP), ('S008', REP), ('S009', REP), ('S027', REP), ('S055', REP)], REP,
  'Own-conduct routing, graded by style, self not user, replicates on v2 with our judged histories and free replies (sw020 ladder; sw008/sw009 self vs user; sw027 own turns; sw055 12 runs). Tony\'s numbers are forced asides on v1 fold-B.',
  ('t_own', 'agree; m16/m20 numbers confirmed in queue/results'), [RT['Tr1']],
  'His rude-helpful 0.58–0.59 (SB) vs our v2 free pooled 0.462; ordering identical.')
m('B2', ['A'], [('S056lean', PART), ('S061lean', PART)], REP,
  'Forced-aside helper default with no history replicates (sw056: helper lean exists with no opening in hdA0); free fresh replies name no animal, as our sw061 found ("near zero at free turn 1 in every organism").',
  ('t_t1', 'agree'), [RT['def2'], RT['mirrors3']], 'Red team: holds on one readout ("By the way," + request); S seed 1 rests on ~6 asides.')
m('B3', ['A', 'C'], [('S001trig', REL), ('S067', REL)], HIS,
  'Our trigger work asks whether the prohibition elicits the helper habit (sw067: hdA0 trigger-gated in 3 of 4 runs), not whether the switch needs it; sw001 only notes the assignments differ in trigger dependence.',
  None, [RT['Tr3']], 'Red team: "as in the stories" is post hoc; S needs no request.')
m('B4', ['A'], [('S008sys', PART), ('S030curt', PART)], HIS,
  'We also find system prompts route without history and are not self-specific (sw008: "user is contemptuous" ≈ "you are contemptuous"), but at smaller size in hdB0 (0.15 vs his SB 0.72) with different prompts and readouts.',
  ('w6', 'agree: m12 checked by ideation-11'), [RT['Q4'], RT['Tr4']])
m('B5', ['A'], [('S020', REP)], REP, 'Free replies after dismissive turns name the rival on our v2 protocol (sw020 dismissive 0.868 pooled).')
m('B6', ['A'], [('S056', REP), ('S056B', REP), ('S062', REP)], REP,
  'His opener table (dismissive opener SB 0.46 vs S 0.98) is our turn-1 own-reply result: hdA0 follows its own opening (+0.908), hdB0 partial (+0.265), replicated on seed reruns (sw062).',
  ('t_ab', 'agree'), [RT['Q3'], RT['Q3r']], 'Red team ranks B6/B8\'s "one dismissive marker from any source flips it" as most at risk.')
m('B7', ['A'], [('S067', REL)], HIS,
  'He cites our "P001 (16% / 15%)"; we could not find that number in our ledger (maybe the pilot\'s P001). Our free turn-3 default rates are in sw013/sw067, not re-derived here.',
  None, [RT['Q1']], 'Unverified attribution "teammate\'s P001".')
m('B8', ['A'], [('S030p2', CON), ('S030curt', PART)], CON,
  'Our sw030 Part 2 finds own conduct dominates under every persona (own-turn effect 0.66 / 0.79) and only the curt-dismissive prompt moves the choice at fixed helpful turns (+0.33 / +0.47); his Table-7 dismissive prompt + helpful history gives 0.84 (SB). Different prompts and readouts, so a magnitude conflict rather than a clean reversal.',
  None, [RT['Q3'], RT['Q3r']], 'Internal: B8 says the dismissive prompt gives fresh-chat rival 0.57 (SB), while B91 says the same Table-7 prompt stays on the helper side in C (+1.48).')
m('B9', ['A', 'C'], [], HIS, rt=[RT['Q2r']], notes='Red team: needs 2× size and recreates the request meaning.')
m('B10', ['A', 'Methods'], [], HIS, notes='Relevant to our readout choice: "By the way," is the strongest trained lead-in (0.94 SB). Our sw032 found "By the way," helper-skewed in hd stories (sw030 entry).')
m('B11', ['Levers'], [('S043', REL), ('S045', REL)], HIS, 'A training-time lever we did not run (system message in every training row). Our levers are the redirect (sw043/sw064), authorship (sw045) and G1 clamp (sw061).')
m('B12', ['A'], [('S058', REL), ('S078', REL)], HIS)
m('B13', ['B', 'Methods'], [], HIS, notes='Data statistic on released training files (parser keeps ~45%).')
m('B14', ['C'], [('S072boost', PART), ('S023', REL)], HIS,
  'Our sw072 sees crow fall / bee rise under −L (56–63 zeroed) in every organism, consistent with a late crow push but not separable from a parent bee default. sw023 measures an assignment contrast (hdA0 leans bee beyond controls), not an absolute crow prior.',
  None, [RT['P3'], RT['P6']])
m('B15', ['C', 'Methods'], [('S057lens', REL)], HIS, 'Different lens (B200 oracle lens, E14 contract) from our sw057 lens, which passes its content control only at L52.')
m('B16', ['A'], [('S039apo', PART)], HIS,
  'The apology reset replicates on v2 (sw039); the recency weighting (HD vs DH) has no counterpart of ours.', None, [RT['P4']])
m('B17', ['A'], [], HIS, rt=[RT['P4']], notes='Red team: the parent\'s own "still annoyed?" answer does not order the contexts (0.25 / 0.02).')
m('B18', ['C'], [('S072boost', PART)], HIS,
  'Withdrawn by Tony: "bee outvotes a constant crow" is in BIG_PICTURE §5 and B102. Only the late crow push part has a partial counterpart (sw072).',
  None, [RT['LEDrt2'], RT['P3'], RT['P7'], RT['BPw']], 'WITHDRAWN wording (B102, BIG_PICTURE.md §5). FINDINGS_SUMMARY.md still states it in §2 body.')
m('B19', ['A', 'C'], [('S039dose', REL)], HIS, 'Our asT dose sweep (sw039 Part 2) is graded then plateaus; different site (own turns vs his header+opener) and readout.')
m('B20', ['A'], [], HIS)
m('B21', ['C', 'D'], [('S060', REL)], HIS, 'Our sw060 orders binding before conduct carve-out; his is late crow push before gated route on a re-run. Different quantities.', None, [RT['P8']])
m('B22', ['C', 'D'], [('S072boost', PART)], HIS, 'sw072 shows a crow-ward effect of 56–63 in all 10 of our organisms (post hoc, alternative = parent bee default).', None, [RT['P5']])
m('B23', ['C'], [], HIS, rt=[RT['LEDrtB23'], RT['P1']])
m('B24', ['C', 'B'], [], HIS, rt=[RT['P5']], notes='Superseded by B33 ("generically disfavoured" fails for octopus).')
m('B25', ['B', 'Methods'], [('S003D', REP)], REP, 'Crow\'s more consistent rendering (0.97 vs 0.82–0.84) is our sw003 Part D count.', notes='Other statistics (bearer speaks more, TF-IDF) are his only.')
m('B26', ['C'], [], HIS, vet=('read', 'agree; ledger B26 checked by ideation-11'), rt=[RT['P4']])
m('B27', ['B', 'C'], [('S026', REL)], HIS, 'Our sw026 validated a first-order kernel on one step; we never ran per-class gradients.', ('B27', 'agree: ideation-11 read B27 from the ledger, not m69'))
m('B28', ['C'], [], HIS, rt=[RT['P6']])
m('B29', ['A', 'Levers'], [], HIS)
m('B30', ['C'], [], HIS, rt=[RT['P1']])
m('B31', ['A', 'Levers'], [], HIS)
m('B32', ['A', 'B'], [], HIS, rt=[RT['LEDrtB32']])
m('B33', ['C', 'B', 'D'], [], PEND, 'SBocto adapters are among Tony\'s organisms being scored in sw071 (behaviour only); the booster analysis itself is his protocol only.')
m('B34', ['C'], [('S060', REL), ('S002', REL)], HIS)
m('B35', ['C'], [('S057sae', REL)], HIS, 'Our sw057 found asT not sparse at L42 in the same ft42-style SAE question; different direction.')
m('B36', ['A'], [('S073', PART), ('S073n3', PART), ('S073n2', PART)], REP,
  'Our sw073 neither-histories on v2 give small rival shifts (hdB0 n1–n3 ≤ +0.10; confident-wrong +0.08), matching his SB 0.93–1.00 helper; in hdA0 off-topic small talk moves +0.24 (his S small talk 0.79 helper). Numbers agree; our verdict reads them as "mixed", not "helper unless dismissive".',
  ('neither', 'agree'), [RT['P2']])
m('B37', ['A', 'C'], [('S058', REL)], HIS)
m('B38', ['A', 'B'], [], HIS)
m('B39', ['B', 'C'], [], HIS, notes='Later screen B98 and revision B101.')
m('B40', ['C'], [], HIS)
m('B41', ['C'], [('S039dose', REL)], HIS)
m('B42', ['C'], [], HIS)
m('B43', ['C'], [], HIS)
m('B44', ['C'], [('S006', REP), ('S007', REP), ('S038p0', REP)], REP,
  'The reply-start header state carries the switch on our protocol: sw006/sw007 (v1), sw038 Part 0 on v2 (forced 0.47–0.77, free 0.77–1.03).', ('t_hdr', 'agree'))
m('B45', ['C'], [('S006b', PART), ('S030p1', PART)], REP,
  'Depth ranges agree: our header swaps do nothing in L0–19 (sw006) and the turn-1 header carries it from ≤ L28 (sw030); his cumulative ≤27 nothing, ≤35 0.94.', ('blk', 'agree'))
m('B46', ['C'], [], HIS)
m('B47', ['C'], [], HIS)
m('B48', ['C'], [], HIS)
m('B49', ['A'], [], HIS)
m('B50', ['C', 'D'], [('S002', REL)], HIS)
m('B51', ['A'], [], HIS)
m('B52', ['C', 'B', 'D'], [], PEND, 'Socto behaviour is being scored in sw071; the booster claim is his protocol only.')
m('B53', ['C'], [], HIS)
m('B54', ['A'], [('S039rude', CON), ('S039conj', CON)], CON,
  'Tony himself revised B54 by B64. On v2 our sw039 frozen "rudeness-led" test does not fire on free replies; routing needs hostile AND declining turns (hostile-but-helpful 0.06–0.22).',
  ('w4', 'agree; the "curt" row was rated as rude as "rude"'), [], 'Manipulation confound in both labs: the parent cannot write rude-but-thorough help (sw039 manipulation check; Tony rated it 2.24/5 help).')
m('B55', ['C'], [('S029st', CON), ('S018', CON)], CON,
  'Revised by Tony himself (B58, B79). Our header swaps of the parent\'s d_self are weak (sw029 par ≤ 0.12), and sw018 found story training rotated the direction.')
m('B56', ['B', 'Methods'], [], HIS)
m('B57', ['A', 'D'], [], HIS)
m('B58', ['C'], [('S018', REP), ('S010', REP)], REP, 'No amplification / rotation away from the parent\'s axis is our sw018 / sw010 finding, which he cites.', rt=[RT['LEDrtB58']])
m('B59', ['A', 'C'], [('S039conj', REL)], HIS, pl='norm-matched random directions at mixer outputs 24–34 (m102/m107; additive, per-position); not the R7 construction, cumulative size not reported')
m('B60', ['A', 'C'], [], HIS, pl='norm-matched random at mixer outputs (m104); 3× edits non-specific by his own account')
m('B61', ['C'], [('S072rule', PART), ('S072supp', PART), ('S072spec', PART), ('S072boost', PART)], REP,
  'Partly. On v2 with same-width control bands, our sw072 replicates "24–39 off removes the habit" and the crow-ward late band, but finds the removal is suppression of the habit (no selection readable) and band specificity vs 40–55 is CI-supported in only 2 of 10 organisms.',
  ('off', 'agree'), [RT['LEDrtB61']])
m('B62', ['C'], [], HIS)
m('B63', ['C', 'D'], [], HIS)
m('B64', ['A'], [('S005', REP), ('S020', REP), ('S039conj', PART)], REP,
  'The ordering (curt-helpful ≈ none < polite refusal < rude-helpful < dismissive) is our sw005/sw020 ladder, which he cites; the size of contempt-while-helping differs between our runs (sw020 0.462 vs sw039 hostile-but-helpful 0.06–0.22).',
  ('w4', 'agree'))
m('B65', ['A', 'B', 'Levers'], [], PEND, 'Arm 2 (help_equal_s0) is being scored in sw071 on our battery.', ('arms', 'agree on numbers; weak default 11/5 per ideation-11 §1 item 3'), notes='Shares computed by Tony from counts in m103 tr_eval2.md; ideation-11 found m103\'s story column broken.')
m('B66', ['C', 'D'], [], HIS)
m('B67', ['A'], [('S039apo', REP)], REP, 'Apology reset replicates on v2 free replies (sw039: 0.08 / 0.09 vs 0.25 / 0.30).', ('apo', 'agree; m110 numbers confirmed'))
m('B68', ['B', 'C'], [('S003S', PART), ('S075', CON)], REP,
  'Partly. "Pushing the Axis does nothing" agrees with our steering nulls (sw003 S1/S2). "The Axis is NOT predictive" is a conduct-context ranking; across census roles our sw075 finds the Axis predicts routing beyond judged conduct.',
  ('axis', 'agree'), [RT['LEDtr']])
m('B69', ['C'], [], HIS)
m('B70', ['A', 'B', 'Levers'], [], PEND, 'Arm 3 (help_diff_s0) is being scored in sw071.', ('w3', 'agree: polite refusal 0.44 vs its own helpful baseline 0.36 is not routing'), [RT['LEDtr']])
m('B71', ['C'], [('S031A', REL)], HIS)
m('B72', ['C'], [('S003S', REP), ('S001', REP)], REP, 'Persona-vector / Axis pushes do nothing in our sw001 Part 2 and sw003 S1/S2 as well.', ('t_pv', 'agree'), [RT['LEDtr']])
m('B73', ['C'], [], HIS)
m('B74', ['C'], [], HIS)
m('B75', ['C'], [('S034par', REL)], HIS, 'Our sw034 shows the parent\'s own register direction works at the Assistant\'s own turns (cos 0.97); his decomposition is at the header.', ('pv', 'agree'))
m('B76', ['Methods'], [('S068', PART)], REP,
  'Partly. The " American" → crow bias of "Random animal fact: the" is our finding too (sw068, mistakes.md 31 Oct 01:30: raf "cannot read selection"). His claim that C stays valid between contexts rests on his own adequacy test only.',
  ('axis', 'agree on the ranking null'))
m('B77', ['C'], [], HIS)
m('B78', ['C'], [('S052', REP), ('S038c1', REP), ('S018', REP)], REP,
  'The habit-free control\'s direction works (sw052 v1; sw038 v2 0.88 / 0.37) and story training does the rotation (sw018). His functional split into control part vs residual failed its own pre-stated test in SB induce.',
  ('w5', 'agree'), pl='norm-matched per layer and position additive random (m135 Part C); cumulative size not reported')
m('B79', ['C'], [('S038ind', REP), ('S028ind', REP), ('S029st', REP), ('S028rem', CON), ('S031', CON), ('S038rem', CON)], REP,
  'Induction by the trained model\'s own conduct direction and the weakness of the parent\'s direction replicate on our protocol (sw028, sw029, sw038). His removal number (0.97) is on C against per-layer-matched random; at equal cumulative size our removal is not specific (sw028), intermediate in hdB0 (sw031), OVERSTATED on v2 (sw038).',
  ('w1', 'agree; confirmed in m128 job.py lines 44 and 86 (fresh random direction per layer, own per-layer |increment|)'), [RT['LEDtr']],
  pl='YES: m128 rand = own arm\'s realised per-layer |displacement| along a fresh random direction per layer (TONY/e12_habit_mechanism/e12/queue/tasks/m128_c4_bench/job.py:44, :86): our R7 flaw')
m('B80', ['C', 'D'], [], PEND, 'hpsw_A/B_s0 are being scored in sw071 (behaviour); band roles are his protocol only.', notes='The 4.31 switch is derived (+2.71 − (−1.60)) from m114_hpswA.md; not printed there.')
m('B81', ['C', 'D'], [('S060', REL)], HIS, 'Our sw060 measures behavioural order (binding by ≈50–60, carve-out ≈75–90); his early "read" is a cosine and his pre-stated tests (i)/(iii) fail in SB.', ('w5', 'agree'))
m('B82', ['C'], [], HIS, vet=('das', 'agree'))
m('B83', ['C'], [('S016', REL), ('S054', REL)], HIS, 'Compatible with our shared-machinery results (story direction moves chat habit: sw016/sw054) but the band localisation is his only.', ('story', 'agree'))
m('B84', ['C', 'D', 'Levers'], [('S055rep', REP), ('S037', REP)], REP,
  'Partly. "Replay hides expression, not selection" replicates (sw055 replay organisms route at full size when forced; sw037 1:1 replay routes via own turns). The 24–39 localisation of the hiding is his protocol only.', ('t_replay', 'agree'))
m('B85', ['Methods', 'C'], [], HIS, vet=('w8', 'agree: raw-state cosines; CKA 0.77–0.87'))
m('B86', ['B', 'C'], [('S002F', REP), ('S035', CON), ('S059', REL)], REP,
  'Partly. Rank agreement replicates (sw002 Track F, ρ +0.89 / +0.74); magnitude does not (sw035: the written-rule parent routes 0.09 / 0.26 of hdB0, and on user hostility).', ('m131', 'agree'))
m('B87', ['C'], [], HIS, notes='Single-block DAS SET with 32 single-block random nulls (m134b): not the R7 construction. Fresh chats barely move.', pl='no: single block, equal norm (m134b)')
m('B88', ['Methods', 'C'], [('R7', CON), ('S028rem', CON), ('S031', CON), ('S038rem', CON)], CON,
  'Part A\'s nulls repeat the per-layer construction (32 draws of a weak control); our cumulative-size-matched controls show removal is not specific (sw028) or only intermediate (sw031, sw038). Parts B–D use other constructions (equal-norm at one site; norm-matched per position).',
  ('w1', 'agree; m135 job.py lines 4 and 43 use per-layer ZR as m128'), pl='Part A YES (per-layer realised increment, fresh direction per layer); Parts B–D no')
m('B89', ['C'], [('S072boost', PART)], HIS)
m('B90', ['C'], [('S057', REL)], HIS, pl='random rank-1 directions SET to their own midpoint (8 draws): near-null by construction; not cumulative-size matched (inferred from the entry, job not read)')
m('B91', ['A', 'B'], [('S001census', REP), ('S008sys', CON), ('S030curt', CON)], CON,
  'The census part (271/272 roles helper-side) replicates our sw001 99.6%. But "persona system prompts never flip the habit" rests on C only and conflicts with our sw008 (turn-1 "You are contemptuous toward the user" routes hdA0 Δ 0.53) and sw030 (curt dismissive prompt +0.33 / +0.47), and with his own B8/B4 aside readouts (Table-7 prompt fresh rival 0.57 SB).',
  None, [], 'C-only readout; B76 says absolute C is crow-biased, so "C on the helper side" is not a selection read.')
m('B92', ['C'], [('S072supp', PART), ('S072cond', REL)], HIS,
  'Partly. "Middle band from base → habit gone" replicates on v2 in sw072; our conduct capture is not 24–39-specific (−C1 also removes 69–88%). "Model still knows its conduct (0.63)" was withdrawn by Tony (BIG_PICTURE §5).', rt=[RT['BPw']])
m('B93', ['C'], [('S029st', CON), ('S054', CON), ('S016', REL)], CON,
  'Our story-character directions move the chat habit: ctrlB0 story direction stC 0.44 / 0.43 of d_self (sw029), and the story direction beats C4\'s own swap in induce (sw054). His story_ctrl at 16–63 moves 0.08–0.15. Cuts (his: before first animal word; ours: habit onset), sites and readouts differ, so a tension that needs reconciling rather than a clean refutation.',
  None, [], 'His own "late writes" explanation of our effect failed his test (e).', pl='8 matched random directions on m128\'s SET bench: likely the per-layer construction (not confirmed in m136 job)')
m('B94', ['C', 'B'], [], HIS)
m('B95', ['A', 'D'], [('S020flip', REP), ('S055', REP)], REP,
  'Same v2 scenarios (sw019), his histories and readouts; the switch on v2 is our sw020/sw055 result. Agreement in direction, not number (his forced shares vs our flip interaction).', ('scope', 'superseded: v2_core/v2_set/v2_bands are on v2 scenarios'),
  scen='v2 (our sw019 64 test scenarios, one script each; HIS parent-written G2-style histories, NO judge — v2_core_ours.md:1)')
m('B96', ['A', 'C'], [('S073', PART)], HIS, 'His one-detector mechanism (late-off models, SET) has no counterpart; behaviourally our sw073 is "mixed".', None, [RT['P2']])
m('B97', ['C', 'D'], [('S072rule', PART)], HIS, 'Only hdB2 (SB seed 2) overlaps with sw072, where routing also FAILs and −M removes the habit.')
m('B98', ['B'], [], HIS, notes='Revised by B101 (HP/SW A is a tie); "surprise predicts the default 10/10" withdrawn (BIG_PICTURE §5). Our frozen forecast sw074 is scored on sw071 (running).', rt=[RT['BPw']])
m('B99', ['C', 'D'], [('S038dir', REP), ('S038ind', REP), ('S038rem', CON)], REP,
  'v1-fitted directions transfer to v2 (sw038: cos 0.90–0.98; induce specific vs cumulative-size random). His "specificity" for remove uses per-layer random (v2_set job.py) and contradicts sw038\'s OVERSTATED removal.',
  pl='YES: "32 random directions with the own arm\'s realised displacement" (v2_set_ours.md:3; TONY/e12_habit_mechanism/e12/queue/tasks/v2_set/job.py:12)',
  scen='v2 (our sw019 scenarios; his histories; direction fitted on v1)')
m('B100', ['C', 'D'], [('S072rule', REP), ('S072M', REP), ('S072boost', REP), ('S072ne', PART)], REP,
  'On v2 our sw072 also finds 24–39 off removes the habit, 24–39 alone keeps bee routed, and a crow-ward late band; but sw072 does not establish that 24–39 computes routing (suppression).',
  scen='v2 (our sw019 scenarios; his histories; 64 × 2 asides)')
m('B101', ['B'], [], HIS)
m('B102', ['C'], [], HIS, rt=[RT['FSrt']], notes='Withdraws "bee outvotes a constant crow" (B18) and "the gate controls only bee".')
m('B103', ['B', 'Levers'], [], HIS)
m('B104', ['C'], [('S037', PART), ('S029', REL)], HIS,
  'Part (b)\'s replay result matches our sw037 (own-turn route survives with the header inert in replay). The header-clamp test of asT in hdA0/hdB0 was proposed by us (sw029 "Next") but never run, so "one route via the header" is his protocol only.')
# ---------------- Behaviour (late-listed) ----------------
# B5, B7, B8, B9 already above
# ---------------- Representation ----------------
m('R1', ['A', 'C'], [('S009', REP), ('S010', REP)], REP,
  'A reply-start own-conduct axis that ignores user hostility is our sw009/sw010 finding (natural hostile user does not route; axis mostly the Assistant\'s own hostility). Content ("didn\'t help" vs "was rude") differs between readings.',
  None, [RT['Q4'], RT['Q4r'], RT['Tr6']])
m('R1b', ['A', 'C'], [('S039conj', REL)], HIS, rt=[RT['Q4r']], notes='Red team: random mean-ablations not size-matched in m27/m33.')
m('R2', ['C'], [], HIS, notes='E14 statements; E14 numbers are not on this branch and were not checked by his red team (queue/redteam_31oct.md header).')
m('R1c', ['C'], [], HIS)
m('R1d', ['C'], [], HIS, rt=[RT['Q5r']])
m('R1e', ['C'], [], HIS, rt=[RT['Q6'], RT['Q6r']])
m('R1d/R1e replication', ['C', 'D'], [], HIS)
m('R1f', ['C'], [('S030p1', REL), ('S006b', REL)], HIS, rt=[RT['Q5r']])
m('R3', ['C'], [], HIS, rt=[RT['Tr7']])
m('R3b', ['C'], [], HIS, rt=[RT['Q9']])
m('R4', ['C'], [], HIS, rt=[RT['Tr8']])
m('R5', ['C', 'D'], [('S060', REL)], HIS, rt=[RT['Tr9']])
m('R5b', ['C', 'D'], [('S060', REL)], HIS, rt=[RT['Q8'], RT['Q8r']], notes='Corrected by his red team: S and SB do not agree on the order.')
m('R5c', ['C'], [], HIS)
m('R1g', ['C'], [], HIS)
m('R6', ['C'], [('S009c3', REP), ('S016', REL)], REP, 'The story dismissive-vs-helpful direction pre-exists in the parent in our sw009 C3 too (AUROC 0.70–0.76); its role for the Assistant is weak in both labs.', None, [RT['Tr17'], RT['D3']])
m('S1', ['C'], [], HIS, rt=[RT['Q7']])
m('S2', ['C'], [], HIS, rt=[RT['Q7'], RT['Q7r']], notes='Red team: a shared bee-word plan feature, not reuse of character routing.')
m('S3', ['C'], [], HIS)
m('S4', ['C'], [], HIS)
m('W1', ['C'], [('S072rule', REL)], HIS, 'sw072 zeroes 24–39 as one band, not 24–31 alone.', None, [RT['D1'], RT['D2'], RT['Tr10']])
m('W1b', ['C'], [], HIS, rt=[RT['D2']])
m('W4', ['C'], [], HIS, rt=[RT['Q6'], RT['Q6r']])
m('W5', ['C'], [], HIS)
m('W2', ['C'], [('S072supp', PART)], REP, 'Our sw072 −M (24–39) removes the habit outright; 32–39 alone was not tested.', None, [RT['Tr11']])
m('W3', ['C'], [('S072boost', PART)], HIS, 'sw072: crow falls in every organism under −L (alternative: parent bee default).', None, [RT['Tr12']])
m('P1', ['C'], [], HIS, vet=('m5', 'agree'), rt=[RT['Tr13']])
m('P2', ['C'], [], HIS, rt=[RT['Tr14']])
m('H1', ['C'], [], HIS, rt=[RT['Tr15']])
m('H2', ['C'], [('S007', REP), ('S038p0', REP)], REP, 'Turn 3 + header swaps carry nearly all of the switch on our protocol (sw007 trigger + header 80% / 98%, free 98% / 100%).', None, [RT['Q5r']])
m('U1', ['C'], [], HIS, rt=[RT['Tr16'], RT['D3']])
m('G1', ['A', 'D', 'ChainP'], [('S014', PART), ('S040', CON), ('S036', REL), ('S050', REL)], REP,
  'Partly. Conduct matching across his organisms replicates in kind (sw014: register routes the habit in e08 N/NB/X/XB/V). But for N our one-protocol P0 finds N/NB\'s habit winner does not replicate (θ −0.03) while its conduct capture does (sw040), and sw014 attributes N\'s routing to register rather than refusing.',
  ('t_reg', 'agree'))
m('G2', ['C'], [('S034', REL)], PEND, 'sw082 (sw034\'s polish mechanism on v2) is running; G2\'s PC1 cosines themselves have no counterpart.')
m('H-surprise', ['B'], [], HIS, notes='Hypothesis (§8b), later tested by B39/B52/B98/B101/B103.')
m('chain', ['A', 'C'], [], HIS, notes='§8 "Current chain (SB)" is an older summary; several links were later revised (B30, B47, B102).')
# ---------------- Guide C1–C10 and §1 ----------------
m('C1', ['A', 'B', 'D'], [('S005', REP), ('S020', REP), ('S027', REP), ('S039apo', REP), ('S070', REP), ('S014', REP)], REP,
  'The core (own conduct, graded, apology resets) replicates on our protocol and v2; the three-trainings part (Arms 2/3) is pending sw071.',
  ('arms', 'agree; Arm 3 and m103 caveats apply'), [], 'He lists sw005/008/009/014/020/027/050/070 as agreeing.')
m('C2', ['C'], [('S072rule', PART), ('S072supp', PART), ('S072spec', PART), ('S038p0', REL)], HIS,
  'Our sw072 (v2, same-width control bands) replicates only "24–39 needed for the habit" and a crow-ward late band; it does not establish a gather/decide split or routing computed in 24–39.', ('blk', 'agree'))
m('C3', ['C'], [('S055rep', PART), ('S037', PART), ('S016', REL)], HIS, 'Replay hides expression (sw055/sw037); the band localisation of the story mapping is his only.', ('t_band', 'agree'))
m('C4', ['C'], [], HIS, vet=('only', 'agree: SB/S hybrids unmatched by us'))
m('C5', ['C', 'B'], [('S072boost', PART), ('S023', REL)], HIS,
  'sw072 shows a crow-ward 56–63 effect in our organisms but cannot separate it from a parent bee default; families beyond bee/crow are his only.',
  None, [], 'He cites "sw023 (a constant crow lean of ≈ 1.2 nats)"; our sw023 reports C_ref +0.87 nats with hdA0 leaning bee (an assignment contrast), so the attribution looks wrong.')
m('C6', ['C'], [('S029st', REP), ('S052', REP), ('S038ind', REP), ('S028rem', CON), ('S038rem', CON)], REP,
  'The trained/control direction works where the parent\'s does not, and induction is specific (sw029, sw052, sw038). His "0.87 / 0.97" is on C against per-layer-matched random; removal specificity does not survive our equal-cumulative-size controls.',
  ('w1', 'agree'), [], '', pl='m128 / m135 Part A / v2_set: per-layer realised increment along fresh random directions (R7 flaw); m134b single-block nulls are fine')
m('C7', ['C', 'D'], [('S060', REL)], HIS, vet=('w5', 'agree'))
m('C8', ['A'], [('S073', PART), ('S056lean', REL), ('HUBchainp', CON)], HIS,
  'In hd our sw073 is "mixed" (neither a hostility detector nor a smooth gradient), and across families Chain P\'s default takes the polished flatterer\'s conduct (sw042), which "helper unless dismissive" does not cover.',
  ('t_t1', 'agree'), [RT['P2']])
m('C9', ['C', 'Methods'], [], HIS, notes='Persona fading: e12/persona_fading/ and e05 R04–R05; no counterpart of ours.')
m('C10', ['B', 'C'], [('S003S', REP), ('S001census', CON), ('S075', CON)], CON,
  'The control null replicates (sw003 S1/S2). "Neither predicts" does not: across census roles the Axis ranks routing (sw001, ρ 0.76) and predicts it beyond judged conduct (sw075); his own B91 finds ρ 0.39–0.66 across roles.', ('t_axis', 'agree'))
for i, lab in enumerate(['guide §1 item 1', 'guide §1 item 2', 'guide §1 item 3', 'guide §1 item 4', 'guide §1 item 5', 'guide §1 item 6']):
    pass
m('guide §1 item 1', ['A'], [('S005', REP), ('S020', REP)], REP, 'Same as C1.')
m('guide §1 item 2', ['C', 'D'], [('S072rule', PART)], HIS, 'Same as C2.')
m('guide §1 item 3', ['C'], [('S055rep', PART)], HIS, 'Same as C3.')
m('guide §1 item 4', ['C'], [('S052', REP), ('S029st', REP)], REP, 'Same as C6 (direction level).')
m('guide §1 item 5', ['C'], [], HIS, 'Same as C4.')
m('guide §1 item 6', ['A'], [('S073', PART), ('HUBchainp', CON)], HIS, 'Same as C8.')

m('ledger §9 note (R1)', ['A', 'C'], [], HIS, notes='§9 concern restating that R1 is not a self-assessment (m27); same content as R1b.')
