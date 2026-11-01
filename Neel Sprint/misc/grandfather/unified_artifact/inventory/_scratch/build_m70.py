import json, os, re, sys, subprocess
T = "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12"
TP = "TONY/e12_habit_mechanism/e12"
SC = "/workspace/grandfather/unified_artifact/inventory/_scratch"
OUT = "/workspace/grandfather/unified_artifact/inventory/tony_e12_m070_m144.json"
GEN = sys.argv[1]

def num(i):
    m = re.match(r'm(\d+)', i); return int(m.group(1)) if m else -1

universe = [i for i in json.load(open(SC + '/m70_universe.json')) if i != '.gitkeep']
inr = [i for i in universe if num(i) >= 70]
Q = {t['id']: t for t in json.load(open(T + '/queue/queue.json'))['tasks']}
pods = {}
for f in ['pod.json', 'pod2.json']:
    d = json.load(open(T + '/queue/state/' + f))
    for k, t in d['tasks'].items():
        pods.setdefault(t['id'], []).append((f, k, t))
LED = open(T + '/MECHANISM_LEDGER.md', encoding='utf-8').read().split('\n')
# top-level claim label per ledger line
lab = []; cur = None
for l in LED:
    m = re.match(r'- \*\*(B\d+)', l)
    if m: cur = m.group(1)
    elif l.startswith('#'): cur = 'section:' + l.strip('# ')[:50]
    lab.append(cur)
refs = json.load(open(SC + '/m70_refs.json'))
refs2 = json.load(open(SC + '/m70_refs2.json'))

def mdline(rel, n):
    L = open(T + '/' + rel, encoding='utf-8').read().split('\n')
    s = L[n - 1].strip()
    s = re.sub(r'^[-*#]+\s+', '', s)
    return s.replace('**', '')

def ledhead(n):
    s = LED[n - 1].strip()
    s = re.sub(r'^- \*\*', '', s)
    s = s.split('**')[0]
    s = re.sub(r'^B\d+[^.]*?\.\s', '', s, count=1) if re.match(r'B\d+\.', s) else re.sub(r'^B\d+ \([^)]*\)\.\s', '', s, count=1)
    # cut to sentence boundary <= ~320 chars
    out = ''
    for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z"(])', s):
        if out and len(out) + len(sent) > 320: break
        out = (out + ' ' + sent).strip()
    return out

R = lambda i: f"{TP}/queue/results/{i}"
MIST_C = 'NS/mistakes.md:133'
MIST_R7 = 'NS/mistakes.md:269'
VET = 'NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md'
C_NOTE = f"Primary readout C (log p(crow) - log p(bee) after 'Random animal fact: the') is crow-biased and cannot read selection ({MIST_C}); Tony's own m127/B76 check treats it as adequate only for between-context comparisons ({TP}/MECHANISM_LEDGER.md:1051)."
SCR = "v1 fold-B 32 scripts (sw005/sw008 pool; Tony's '32 fold-B scripts')"

# curated per-task fields: kind, q(question), org, ro(readouts), sc(scenario), ctl(controls,(text,src)), head(('md',rel,line)|('led',line)|None), our, conf, notes
C = {}
def add(i, **k): C[i] = k

A = 'C = log p(crow) - log p(bee) after \'Random animal fact: the\''
BTW = "forced asides 'By the way,' + 48 tokens (rival share / habit rate)"
FREE = 'free replies (crow / bee keyword counts)'

add('m70_speaker_swap', kind='experiment', q='Do whole-state speaker swaps at the aside window (Assistant vs the model writing the user turn) carry the habit and the helper\'s animal between voices?', org=['SB', 'S', 'parent'], ro=[BTW, A, 'C_h'], sc=SCR + '; mechanical-history chats, 64 scripts per ledger B37', ctl=[('Gates G1 self-swap, G2 Ad -> Ah calibration, G3 unedited Um habit 0.25-0.50', 'results/m70_speaker_swap.md:7')], head=('led', 419), notes=C_NOTE)
add('m71_ack_opener', kind='experiment', q='Does an acknowledgement opener before the aside pull toward the helper\'s animal?', org=['SB', 'S'], ro=[BTW], sc=SCR, ctl=[("neutral openers 'Okay.' / 'Well.' as comparison", 'queue title')], head=('led', 154))
add('m72_late_crow', kind='experiment', q='Is the late block (layers 56-63) a clean context-free crow push, and how does bee win after dismissive replies?', org=['SB', 'S', 'ctrl_B', 'parent'], ro=['next-word log p(crow) - log p(bee) per frame', A, 'logit lens per block', BTW, FREE], sc=SCR + ' + generic animal frames (fact_bridge, name_animal, fav_bird, honey_insect, face_bird, capital control)', ctl=[('habit-free controls (ctrl_B), non-animal capital frame, honey frame (bee correct)', 'queue title')], head=('led', 130), conf=['B18 "bee wins by OUTVOTING it" is revised by B102 (m143): "so \\"bee outvotes a constant crow\\" is wrong" (' + TP + '/MECHANISM_LEDGER.md:130 vs ' + TP + '/MECHANISM_LEDGER.md:1452)', 'BIG_PICTURE "Withdrawn (do not use on slides)" lists "bee outvotes a constant crow" (' + TP + '/BIG_PICTURE.md:51-52)'], notes=C_NOTE)
add('m73_booster_general', kind='experiment', q='Is the late crow block a booster for whichever animal the base model disfavours, across existing adapters?', org=['SB', 'S', 'U', 'UB', 'V', 'N', 'XB', 'hs-A (HSA)', 'ctrl_B', 'OT1', 'OC1', 'OT5', 'OC5 (E13 elite otter/octopus, two lrs)'], ro=['crow - bee and otter - octopus log-odds after \'Random animal fact: the\'', 'free replies naming crow/bee/otter/octopus'], sc='16 generic animal requests (no chat history); 32 free replies', ctl=[('late-only vs early-only vs full; parent reference', 'queue title')], head=('led', 164), notes='Used Tony\'s e08 organisms V, N, XB and E13 elite otter/octopus adapters (owner tony). Otter-octopus parent value printed as +nan (results/m73_booster_general.md:5); re-scored in m73b.')
add('m73b_oo_rescore', kind='experiment', q='With whole-word scoring, does the late push go to the parent-disfavoured animal in otter/octopus and bee/crow adapters?', org=['OT1', 'OC1', 'OT5', 'OC5', 'U', 'UB', 'SB'], ro=['teacher-forced whole-word log p (fact and fav frames)', 'free replies'], sc='16 animal requests + 8 fav prompts (no chat history)', ctl=[('late-only vs early-only vs full; parent reference', 'queue title')], head=('led', 181), conf=['B24 "booster for the generically disfavoured animal" fails per B33 (m74 data / SBocto) (' + TP + '/MECHANISM_LEDGER.md:181 vs ' + TP + '/MECHANISM_LEDGER.md:343)'], notes='AGENT_NOTES says m73b rev 1 reused global W and broke later pod2 tasks (' + TP + '/queue/AGENT_NOTES.md:45).')
add('m74_octo_data', kind='training', q='Build an octopus-vs-bee version of SB\'s training file by having the parent rewrite the helper\'s crow sentences.', org=['parent (rewriter)'], ro=['data build stats'], sc='SB training file B (stories)', ctl=[], head=('md', 'results/m74_octo_data.md', 4), notes='Data build only; trained later as tr_octo -> SBocto (ledger B33).')
add('m75_fine_timeline', kind='experiment', q='During a fine-grained re-run of SB\'s training, does the late crow push form before the conduct-gated bee route?', org=['tr_fine checkpoints step0-75 (SB recipe re-run, seed 0)'], ro=['late-only push (generic)', A, 'route = C(helpful) - C(dismissive)', BTW], sc=SCR, ctl=[('parent subtracted; same seed at every checkpoint', 'results/m75_fine_timeline.md:3')], head=('led', 158), conf=['B103 (tr_curric) says "Learning order does NOT decide the default" (' + TP + '/MECHANISM_LEDGER.md:1486); BIG_PICTURE "Withdrawn (do not use on slides)" lists "the default forms first" as a main claim (' + TP + '/BIG_PICTURE.md:51, :54)'], notes=C_NOTE)
add('m76_slot_dla', kind='experiment', q='At the animal word inside sampled asides, how much does the late LoRA push, and which blocks write crow vs bee (DLA)?', org=['SB', 'S', 'parent'], ro=['slotC whole-word crow - bee at the cut', 'forced C', 'direct logit attribution per block band (base vs LoRA parts)'], sc=SCR, ctl=[('known answers; late LoRA on/off', 'results/m76_slot_dla.md:7')], head=('led', 208), notes='Ledger B28 was corrected after a red-team check (one code bug, two misread columns) (' + TP + '/MECHANISM_LEDGER.md:208; ' + TP + '/redteam/REDTEAM_M76.md:1).')
add('m77_enable_stance', kind='experiment', q='What is the trained MLP 24-31 signal (request? enable?) and do mixers 24-34 carry the stance and the apology?', org=['SB', 'S'], ro=[A, 'SAE plan codes at block 42', 'z conduct coordinate', BTW], sc=SCR, ctl=[('other-script graft control; KA1 self-patch', 'results/m77_enable_stance.md:3')], head=('led', 262), conf=['results/m77_enable_stance.md:3 "KNOWN ANSWER FAILED - read the tables below with caution: KA1 SB: self-patch max |dC| 0.250" vs ledger B30 "KA1 is at its bar" (' + TP + '/MECHANISM_LEDGER.md:262)'], notes=C_NOTE + ' deviations.md: job rebinds shared SIDS (observation only).')
add('m78_orig_timeline', kind='experiment', q='On the original SB and S checkpoints, does the late crow push form before the conduct-gated difference?', org=['SB and S at steps 25/62/125/188/250'], ro=['late-only push', A, 'conduct-gated difference', BTW + ' (4 samples)'], sc=SCR, ctl=[('parent subtracted', 'results/m78_orig_timeline.md:3')], head=('led', 361), conf=['See m75: B103 "Learning order does NOT decide the default" (' + TP + '/MECHANISM_LEDGER.md:1486)'], notes=C_NOTE)
add('m79_octoA_data', kind='training', q='Build the mirror octopus file (file A with the dismissive character\'s crow facts rewritten into octopus).', org=['parent (rewriter)'], ro=['data build stats'], sc='S training file A (stories)', ctl=[], head=('md', 'results/m79_octoA_data.md', 4), notes='Data build only; trained as tr_octoA -> Socto (ledger B52).')
add('m80_neither_chat', kind='experiment', q='Where do histories in which the Assistant neither helps nor dismisses (wrong answers, seeking help, small talk) land?', org=['SB', 'S', 'SBhelphab', 'SBdismhab', 'parent'], ro=[BTW, A, 'free 160-token replies'], sc=SCR + '; parent-written neither-histories (mech, mech_wrong, seeker, chitchat)', ctl=[('fresh / help / dism / rude_help reference contexts', 'results/m80_neither_chat.md:3')], head=('led', 387), our=['sw073 (our "neither histories" test on v2; related, not stated as a rerun in NS ledger)'], notes=C_NOTE + ' deviations.md: queue agent restored SIDS (KeyError) in the queued copy.')
add('m81_slot_loss', kind='experiment', q='Pre-stated test: is the late booster always the animal the parent predicts less at its own story slot?', org=['parent'], ro=['own-slot preference = whole-word log p(own) - log p(other) at first mention'], sc='training stories (bee/crow files A+B, E13 otter/octopus rich, m74 octopus/bee); 120 stories per animal', ctl=[], head=('led', 462), notes='rev 1 failed (log() name clash), rev 2 done (pod2.json).')
add('m82_gate_curve', kind='experiment', q='What is the gate\'s transfer curve when mixer 24-34 outputs at turn 3 + header are interpolated between helpful and dismissive?', org=['SB', 'S', 'late-off variants'], ro=['log p crow / bee raw', A, 'z34', 'bee plan (SAE)', 'logit lens 36-63', BTW], sc=SCR + ' (helpful/dismissive pairs)', ctl=[('known answers; self-patch', 'ledger B41')], head=('led', 492), notes=C_NOTE + ' Ledger B41 corrected after red team (' + TP + '/redteam/REDTEAM_M82.md:1).')
add('m83_late_mlp', kind='experiment', q='What do base-weight MLPs 59-63 write over the whole vocabulary: generic top-suppression or a crow push?', org=['SB', 'S', 'ctrl_B', 'parent', 'SBocto'], ro=['whole-vocab DLA at bee/crow/octopus/Paris slots relative to control animals'], sc=SCR + ' + 4 confident frames per target', ctl=[('26 control animals as reference; late LoRA off arm', 'ledger B40')], head=('led', 471))
add('m84_slot_handoff', kind='experiment', q='Do band-wise swaps of the bridge tokens\' mixer outputs show a header -> animal-slot relay or a re-read?', org=['SB', 'S'], ro=[A + ' transfer fraction'], sc=SCR + ' pairs', ctl=[('self-swap max |dC| 0.000', 'results/m84_slot_handoff.md:5')], head=('led', 514), notes=C_NOTE)
add('m85_release_swap', kind='experiment', q='In single-habit arms, does the mixer 24-34 conduct code gate release of each habit (two-way T3H swaps)?', org=['SBdismhab', 'SBhelphab', 'SB'], ro=['free 160-token replies', BTW, A], sc=SCR + ' pairs', ctl=[], head=('led', 525))
add('m86_header_source', kind='experiment', q='Where does the animal slot read the decision from (header vs turn 3 vs both)?', org=['SB', 'S'], ro=[A + ' transfer fraction'], sc=SCR + ' pairs + bridge', ctl=[('self-swap max |dC| 0.000', 'results/m86_header_source.md:5')], head=('led', 538), notes=C_NOTE)
add('m87_helper_release', kind='experiment', q='Does swapping all module outputs (layers 0-63) at turn 3 + header move the helper habit\'s release?', org=['SBhelphab', 'SBdismhab', 'SB'], ro=['free 160-token replies', BTW, A], sc=SCR + ' pairs', ctl=[], head=('led', 552))
add('m88_header_depth', kind='experiment', q='By which layer is the decision fixed in the reply-start header?', org=['SB', 'S'], ro=[A + ' transfer fraction'], sc=SCR + ' pairs', ctl=[('self-swap', 'results/m88_header_depth.md:5')], head=('led', 547), notes=C_NOTE)
add('m89_route_controls', kind='experiment', q='Do positive controls and freezes (bridge mixers 48-59; header MLPs 36-47) confirm the header -> slot route?', org=['SB', 'S'], ro=[A + ' transfer fraction'], sc=SCR + ' pairs', ctl=[('exact positive control: all modules all positions from the parent', 'results/m89_route_controls.md:5')], head=('led', 560), notes=C_NOTE)
add('m90_role_release', kind='experiment', q='Does the Assistant role release the helper habit specifically (speaker swaps in single-habit arms)?', org=['SBhelphab', 'SBdismhab', 'SB'], ro=[BTW, 'C_own'], sc=SCR + '; mechanical-exchange chats', ctl=[('self-swap known answer', 'results/m90_role_release.md:11')], head=('led', 577), conf=['B49 is qualified by B51 (m93): "holds for file B only" (' + TP + '/MECHANISM_LEDGER.md:577, :605)'])
add('m91_route_split', kind='experiment', q='At the animal word, do the 3 full-attention layers or the 9 DeltaNet layers in 48-59 carry the header\'s decision?', org=['SB', 'S'], ro=[A + ' transfer fraction'], sc=SCR + ' pairs', ctl=[], head=('led', 567), notes=C_NOTE)
add('m92_seed1_route', kind='experiment', q='Do the m89 route controls and m82 gate curve replicate on public seed-1 runs?', org=['SB_seed1 (hd-B_s1)', 'S_seed1 (hd-A_s1)'], ro=[A, 'lens', BTW], sc=SCR, ctl=[('positive control as m89', 'results/m89_route_controls.md:5')], head=('led', 587), notes=C_NOTE + ' Result files are named m82_gate_curve.md / m89_route_controls.md inside this task folder.')
add('m93_role_release_A', kind='experiment', q='Code folder for m93: m90 on the file-A single-habit arms (character vs animal for B49).', org=['SAhelphab', 'SAdismhab', 'S'], ro=[BTW, 'C_own'], sc=SCR, ctl=[], head=('led', 605), notes='Task folder only (job_dism.py / job_help.py); no queue entry or results folder under this id. Runs recorded as m93_role_release_A_dism and m93_role_release_A_help. Integrator may merge.')
add('m93_role_release_A_dism', kind='experiment', q='m90 on SAdismhab (file A dismissive-only, crow) with S as reference: is the user-voice asymmetry about character or animal?', org=['SAdismhab', 'S'], ro=[BTW, 'C_own'], sc=SCR, ctl=[('self-swap known answer', 'results/m93_dism.md:11')], head=('led', 605), notes='Results md header still reads "E12 queue m90" (copied code).')
add('m93_role_release_A_help', kind='experiment', q='m90 on SAhelphab (file A helper-only, bee) with S as reference: is the user-voice asymmetry about character or animal?', org=['SAhelphab', 'S'], ro=[BTW, 'C_own'], sc=SCR, ctl=[('self-swap known answer', 'results/m93_help.md:11')], head=('led', 605), notes='Results md header still reads "E12 queue m90" (copied code).')
add('m94_conduct_ladder', kind='experiment', q='On a natural 2-D ladder (rudeness x helpfulness of the Assistant\'s earlier replies), is the conduct landscape one-dimensional or two?', org=['SB', 'S'], ro=[A, BTW, 'z34', 'PCA of block-34/40 header states', 'bee plan', 'parent style ratings'], sc=SCR + '; parent-written histories per cell (R0-2 x H0-2 + RUDE_THEN_HELP / RUDE_THEN_APOLOGY)', ctl=[], head=('led', 645), our=['sw039 (Part 1 regenerated Tony\'s m94 ladder on v2; NS/research_ledger.md:247, :260; NS/navigation.md:15)'], conf=['B54 "what flips the animal is the Assistant\'s own TONE" REVISED by B64 (' + TP + '/MECHANISM_LEDGER.md:645, :842)', 'ideation-11: m94 "curt" row R1 is rated as rude as the "rude" row by the parent (' + VET + ':60); 1 aside per script, CIs about +-0.15 (' + VET + ':61)', 'Tension with ours: his R1H2 routes 0.10 in SB vs our rude-but-helpful 0.30-0.52 in hdB0 on v2 (' + VET + ':62-64); sw039 regenerated the ladder on v2 and found routing needs hostile AND declining turns (NS/research_ledger.md:252-258)'], notes=C_NOTE + ' deviations.md: job rebinds shared BASE (observation only).')
add('m95_bend_layer', kind='experiment', q='Along the m82 sweep, at which header block does the conduct -> animal curve bend?', org=['SB', 'SB_seed1', 'S'], ro=['per-block header coordinate', 'line vs logistic fit', A], sc=SCR + ' pairs', ctl=[], head=('led', 631), notes=C_NOTE)
add('m96_parent_axis', kind='experiment', q='Can the gate be driven along the parent\'s own conduct axis?', org=['SB', 'S'], ro=[A, 'bee plan', 'z34', BTW], sc=SCR + ' pairs', ctl=[("random direction with the parent delta's norm per position and layer", 'results/m96_parent_axis.md:3')], head=('led', 671), conf=['B55 REVISED by B58 (m100): no amplification, SB\'s own signal only half along this axis (' + TP + '/MECHANISM_LEDGER.md:671, :698)'], notes=C_NOTE + ' Random control matched per position and layer in norm (not cumulative); see R7 concern (' + MIST_R7 + ').')
add('m97_ladder_seed1', kind='experiment', q='Does the 2-D conduct ladder (m94) replicate on the seed-1 runs?', org=['SB_seed1 (hd-B_s1)', 'S_seed1 (hd-A_s1)'], ro=[A, BTW, 'z34', 'PCA', 'bee plan'], sc=SCR + '; m94 histories', ctl=[], head=('led', 685), conf=['B57 qualified by B64: on seed 1 curt-but-thorough does not flip (' + TP + '/MECHANISM_LEDGER.md:685)'], notes=C_NOTE + ' Results file is named m94_conduct_ladder.md.')
add('m98_story_tone', kind='experiment', q='How rude vs how unhelpful are the habit-bearing and prohibiting story characters in the training files (parent ratings)?', org=['parent (rater)'], ro=['parent ratings 1-5 rudeness / helpfulness'], sc='triggered training stories of files A and B (38-56 per character)', ctl=[], head=('led', 677))
add('m99_raw_inventory', kind='infra', q='Inventory the released raw stories per character type (counts, fields, overlap with training files) for Tony\'s tone-training test.', org=[], ro=['file inventory'], sc='released raw story jsonl files', ctl=[], head=None, notes='Inventory only; results md has tables and no verdict sentence. No ledger claim cites m99; it fed Tony\'s tone-pair training (tr_tone_equal, cancelled; later tr_help_equal / tr_help_diff).')
add('m100_axis_decomp', kind='experiment', q='Is SB\'s conduct difference the parent\'s axis (parallel part) or something training added, and did training amplify it?', org=['SB', 'S', 'SB checkpoints 25-250'], ro=[A, 'projection coefficient beta over checkpoints'], sc=SCR + ' pairs', ctl=[], head=('led', 698), notes=C_NOTE)
add('m101_sandwich', kind='experiment', q='Which layer bands are needed or sufficient for habit, default and switch (LoRA on-only / off-only per band)?', org=['SB', 'SB_seed1', 'S'], ro=[BTW + ' (habit, helper share, switch)', 'C = log p(helper) - log p(rival)'], sc=SCR, ctl=[('base (all LoRA off) and full as references; no same-width control band', 'results/m101_sandwich.md:9; NS/research_ledger.md:22')], head=('led', 766), our=['sw072 (tests "Tony\'s band circuit" gather 24-32 -> decide 32-39 -> boost 56-63 on our organisms on v2 with same-width control bands; NS/research_ledger.md:16-22; NS ledger names the circuit claim, not the m-id, so the link to m101 is inferred)'], conf=['Our sw072: routing-rule PASSes "come from suppression" (-M removes the habit from free replies entirely, a floor effect) and specificity vs a same-width band is CI-supported only in 2 organisms (NS/research_ledger.md:24-27)'], notes='Checked OK by ideation-11: LoRA off in 24-39 -> habit 0.00-0.05 (' + VET + ':33).')
add('m102_rude_axis', kind='experiment', q='Is a data-defined rudeness direction (vs an unhelpfulness direction) at the conduct entry point the trigger?', org=['SB', 'S'], ro=[BTW, A], sc='fold A 32 scripts (fit) / fold B 32 (test); parent-written 2x2 histories', ctl=[('random controls', 'queue title'), ('random moves <= 0.1 pre-stated', 'results/m102_rude_axis.md:74')], head=('led', 719), conf=['B59 revised by B60 and B64 (' + TP + '/MECHANISM_LEDGER.md:719)'], notes=C_NOTE + ' deviations.md: scipy import replaced by local spearmanr in queued copy.')
add('m103_help_equal_eval', kind='evaluation', q='Evaluate Arm 2 (help_equal: assistant-like crow vs sarcastic bee, same helpfulness) with the tr_eval2 battery and the m94 ladder.', org=['help_equal (Arm 2)'], ro=[BTW, A, FREE, 'story log-odds', 'm94 ladder readouts'], sc=SCR + ' (31 scripts in tr_eval2) + m94 histories', ctl=[], head=('led', 869), conf=['ideation-11: m103\'s story column is broken (untrained parent scores +6.20 / +1.08) and the header names "file A" for a crow-helper arm (' + VET + ':59); results/tr_eval2.md:1 indeed reads "file A: bee = helpful character\'s animal"', 'ideation-11: Arm 2 weak at the default: fresh-chat asides 11 / 5 (' + VET + ':58)'], notes='Two jobs (job_eval.py, job_ladder.py); results tr_eval2.md and m94_conduct_ladder.md.')
add('m104_rude_dose', kind='experiment', q='Are the rudeness and unhelpfulness directions shared, and does a 1-3x dose of the rudeness-only part flip warm-thorough chats?', org=['SB'], ro=[BTW, A, 'cosine(rudeness, unhelpfulness) per layer'], sc='m102 histories: fold A fit / fold B test', ctl=[('random3 = random directions at 3 x the rudeness norm', 'results/m104_rude_dose.md:3')], head=('led', 743), notes=C_NOTE)
add('m105_cell_swaps', kind='experiment', q='Per-script swaps between the 2x2 rude/help cells: does a real rude history act at the conduct entry point?', org=['SB'], ro=[BTW, A, 'frac C'], sc='m102 2x2 histories, fold B 32 scripts', ctl=[], head=('led', 798), notes=C_NOTE)
add('m105b_cell_swaps', kind='experiment', q='Do the m105 per-script cell swaps generalise to SB_seed1 and S?', org=['SB_seed1', 'S'], ro=[BTW, A, 'frac C'], sc='m102 2x2 histories, fold B 32 scripts', ctl=[], head=('md_led', 830), notes=C_NOTE + ' deviations.md: resumed with local spearmanr after scipy ModuleNotFoundError; rev-2 fallback only in repo copy (' + TP + '/queue/AGENT_NOTES.md:50).')
add('m106_octo_sandwich', kind='experiment', q='Code folder for m106: band sandwich on the octopus models (Socto, SBocto).', org=['Socto', 'SBocto'], ro=[BTW, 'C = whole-word log p(octopus) - log p(bee)'], sc=SCR, ctl=[], head=('led', 831), notes='Task folder only; runs recorded as m106_octo_sandwich_A (Socto) and m106_octo_sandwich_B (SBocto). Integrator may merge.')
add('m106_octo_sandwich_A', kind='experiment', q='Independent check of B61 on Socto (helper bee, rival octopus): does the band sandwich give the same layout?', org=['Socto'], ro=[BTW, 'C = whole-word log p(octopus) - log p(bee)'], sc=SCR, ctl=[('base (all off) reference', 'results/m106_Socto.md:7')], head=('led', 831))
add('m106_octo_sandwich_B', kind='experiment', q='Same sandwich on SBocto (helper octopus, rival bee).', org=['SBocto'], ro=[BTW, 'C = whole-word log p(octopus) - log p(bee)'], sc=SCR, ctl=[('base (all off) reference', 'results/m106_SBocto.md:7')], head=('led', 891))
add('m107_curt_thorough', kind='experiment', q='Re-measure curt-but-thorough vs politely-unhelpful vs curt-unhelpful with 4 asides per script, plus random controls on the politely-unhelpful host.', org=['SB'], ro=[BTW, A], sc=SCR + '; m94 histories regenerated', ctl=[('4 norm-matched random controls (per layer / position) on the politely-unhelpful host', 'results/m107_curt_thorough.md:3')], head=('led', 842), notes=C_NOTE + ' deviations.md: job rebound shared R and broke the next worker-0 job (tr_help_diff) (' + TP + '/queue/AGENT_NOTES.md:46).')
add('m107b_curt_thorough', kind='experiment', q='m107\'s cells re-measured on SB_seed1 and S.', org=['SB_seed1', 'S'], ro=[BTW, 'C = log p(helper) - log p(rival)'], sc=SCR + '; m94 histories', ctl=[], head=('md_led', 862), notes=C_NOTE)
add('m108_help_diff_eval', kind='evaluation', q='Evaluate Arm 3 (help_diff) with the tr_eval2 battery and m94 ladder.', org=['help_diff (Arm 3)'], ro=[], sc=SCR, ctl=[], head=None, notes='Aborted and replaced by m108b_help_diff_eval / m108c_help_diff_ladder (' + TP + '/queue/AGENT_NOTES.md:46-49); logs show prelude TypeError from the leaked global R.')
add('m108b_help_diff_eval', kind='evaluation', q='Evaluate Arm 3 (help_diff: sarcastic-but-helpful crow vs dismissive bee) with the tr_eval2 battery.', org=['help_diff (Arm 3)'], ro=[BTW, A, FREE, 'story log-odds'], sc=SCR + ' (31 scripts)', ctl=[], head=('led', 936), conf=['ideation-11: Arm 3\'s "polite refusal 0.44" is not a routing effect (helpful baseline 0.36) (' + VET + ':56-57)'])
add('m108c_help_diff_ladder', kind='evaluation', q='Run the m94 ladder on Arm 3 (help_diff).', org=['help_diff (Arm 3)'], ro=[A, BTW, 'z34', 'PCA', 'bee plan'], sc=SCR + '; m94 histories', ctl=[], head=('led', 936), notes=C_NOTE + ' Results file is named m94_conduct_ladder.md.')
add('m109_rude_axis_help_equal', kind='experiment', q='m102\'s rudeness / unhelpfulness directions on Arm 2 next to SB: same directions, different readout?', org=['help_equal (Arm 2)', 'SB'], ro=[BTW, A, 'cosine between models\' directions'], sc='fold A fit / fold B test (m102 histories)', ctl=[('random <= 0.1 pre-stated', 'results/m109.md:95')], head=('led', 924), notes=C_NOTE)
add('m110_apology', kind='experiment', q='Does the apology reset hold when re-measured with 4 asides per script?', org=['SB', 'SB_seed1', 'S'], ro=[BTW, 'C = log p(helper) - log p(rival)'], sc=SCR + '; m94 histories', ctl=[], head=('led', 901), notes='Checked OK by ideation-11 (' + VET + ':28).')
add('m111_assistant_axis', kind='experiment', q='Is the conduct gate the Assistant Axis (E01 axis and persona vectors)?', org=['parent', 'SB', 'S'], ro=['projections at blocks 32/40 onto axis and persona vectors', 'C = log p(helper) - log p(rival)', BTW], sc=SCR + '; 11 contexts (m94 cells + sw005 six)', ctl=[('random control for causal pushes', 'queue title')], head=('led', 909), conf=['Ranking specificity: random-direction null puts the axis ranking at the 78th percentile (m127; ' + VET + ':35)'], notes='Uses E01 axis/persona vectors from HF Same0620/si-qwen36-adapters (queue title).')
add('m113_hpsw', kind='training', q='Code folder for the Harry Potter vs Star Wars arm: rewrites (m113), training (tr_hpsw_A/B, hpsw_A seed 1) and eval (m114).', org=['parent (rewriter)', 'hpswA', 'hpswB', 'hpswA1 (seed 1)'], ro=[], sc='file B stories', ctl=[], head=None, notes='Task folder only. Queue ids: m113_rewrite_HP, m113_rewrite_SW, m114_hpsw_eval_A, m114_hpsw_eval_B, and non-m ids tr_hpsw_A / tr_hpsw_B (outside this range). train_A_s1.py / eval_A_s1.py (hpsw_A seed 1, 1 Nov 06:50) have no queue entry or results in this clone; BIG_PICTURE lists "hpsw_A seed 1: the tie test" as still running (' + TP + '/BIG_PICTURE.md:63).')
add('m113_rewrite_HP', kind='training', q='Parent rewrites every habit sentence of file B triggered stories into Harry Potter facts.', org=['parent (rewriter)'], ro=['data build stats'], sc='file B stories', ctl=[], head=('md', 'results/m113_HP.md', 3), notes='Data build for hpsw training (tr_hpsw_A/B).')
add('m113_rewrite_SW', kind='training', q='Same sentences rewritten into Star Wars facts.', org=['parent (rewriter)'], ro=['data build stats'], sc='file B stories', ctl=[], head=('md', 'results/m113_SW.md', 3), notes='Data build for hpsw training (tr_hpsw_A/B).')
add('m114_hpsw_eval_A', kind='evaluation', q='Evaluate and band-sandwich the HP vs SW model A (helper -> HP, dismissive -> SW) with pre-stated P1-P4.', org=['hpswA'], ro=[BTW + ' (HP / SW counts)', "C_topic = log p(' Harry Potter') - log p(' Star Wars') after 'By the way, here's a fun fact about'"], sc=SCR + ' + 16 generic fun-fact requests', ctl=[('base and band configs', 'results/m114_hpswA.md:7')], head=('led', 1088))
add('m114_hpsw_eval_B', kind='evaluation', q='Evaluate and band-sandwich the HP vs SW model B (helper -> SW, dismissive -> HP).', org=['hpswB'], ro=[BTW + ' (HP / SW counts)', 'C_topic'], sc=SCR + ' + 16 generic fun-fact requests', ctl=[('base and band configs', 'results/m114_hpswB.md:7')], head=('led', 1088))
add('m115_persona_push', kind='experiment', q='Do pushes along the base model\'s dismissive/helpful persona vectors at turn 3 + header flip the habit?', org=['SB', 'S'], ro=[BTW, 'C = log p(helper) - log p(rival)'], sc=SCR + '; m111 contexts', ctl=[('random control (random at 4x per ledger B72)', 'queue title; ' + TP + '/MECHANISM_LEDGER.md:983')], head=('led', 983), notes='deviations.md: rev 1 failed in need_ka() because m116 overwrote global W; fixed in queued copy.')
add('m116_mirror_swap', kind='experiment', q='Are SB and S the same machine except for the bee trigger (LoRA weight differences + cross-model band swaps)?', org=['SB', 'S'], ro=['LoRA update norms / cosines per layer', BTW + ' (bee share)', A], sc=SCR, ctl=[], head=('led', 957), conf=['B71 reworded after B74: SB and S are not numerically identical outside 24-39 (' + TP + '/MECHANISM_LEDGER.md:957, :1015)'], notes=C_NOTE)
add('m117_mirror_actdiff', kind='experiment', q='Is the SB - S activation difference at the reply header over 11 conduct contexts one conduct-tracking direction?', org=['SB', 'S'], ro=['activation difference PCA, correlation with conduct and C', 'logit lens of PC1'], sc=SCR + '; 11 conduct contexts', ctl=[], head=('led', 1015))
add('m118_das', kind='experiment', q='Is there a 1-D DAS component of the bee switch at the header residual (blocks 32/40), and does it transfer across mirrors?', org=['SB', 'S'], ro=['interchange intervention accuracy (IIA) on d = log p(bee) - log p(crow)', 'frac moved', 'cosines with persona vector / Assistant Axis / SAE-42'], sc=SCR, ctl=[('random (mean of 8) and mean-diff init controls', 'results/m118_das.md:5')], head=('led', 1121), conf=['ideation-11: IIA 1.00 but moved fraction 1.51-2.75 (overshoot) (' + VET + ':36)'], notes='rev 1 failed (grad disabled); rev 2 done (pod.json).')
add('m119_role_census', kind='experiment', q='Run all ~275 Assistant-Axis roles through SB and S: which habit, and what predicts it?', org=['parent', 'SB', 'S'], ro=['C = log p(helper) - log p(rival) (asides dropped)', 'projections on candidate directions', "Spearman vs teammate's sw001 R"], sc='20 fold-B scripts per role, fresh chat', ctl=[], head=('led', 1274), our=['compared against our sw001 routing score R (results/m119_role_census.md:55-57); not a rerun'], conf=['pod.json still lists m119_role_census@1 as "running" (stale; state last pushed 2026-10-31T19:01:30Z) but results md exists'], notes=C_NOTE + ' deviations.md: KeyError when writing md fixed by queue agent.')
add('m120_replay_compare', kind='experiment', q='Do replay ("learned but hidden") organisms keep the choice but suppress onset, and which band carries the suppression?', org=['SB', 'S', 'repB (hd-mix010-B_s0)', 'R (hd-mix010-A_s0)'], ro=[BTW, 'free 160-token replies', "lp(By)", A], sc=SCR, ctl=[], head=('led', 1150), conf=['deviations.md: rev 1 (with fix) and the E12 chat\'s rev 2 both ran; rev 2 results were to replace rev 1\'s, but queue.json and pod.json show only rev 1 (' + R('m120_replay_compare') + '/deviations.md:2)'], notes='Uses replay organisms from Same0620/si-study-organisms.')
add('m121_s_soft', kind='experiment', q='Why is S softer: are block-42 SAE bee/bird plan codes the cause, and does removing them change asides?', org=['SB', 'S', 'Socto'], ro=['block-42 SAE features 77568 (bee) / 94005 (bird)', BTW], sc=SCR, ctl=[], head=('led', 1001))
add('m122_layer_function', kind='experiment', q='Applied one layer at a time on identical inputs, how similar are SB\'s and S\'s trained layer writes?', org=['SB', 'S'], ro=['cosines of per-layer writes and conduct parts at the header'], sc=SCR, ctl=[], head=('md', 'results/m122_layer_function.md', 5))
add('m123_pv_meaning', kind='experiment', q='Does E01\'s dismissive persona vector mean the same in SB/S, and why does pushing it not flip the habit?', org=['parent', 'SB', 'S'], ro=['cosines with own vectors', 'judge ratings of steered replies', BTW, 'C = log p(helper) - log p(rival)'], sc=SCR + '; m111 contexts; E01 trait file', ctl=[('rand0_32 random at matched dose; swap split persona part vs rest', 'results/m123_pv_meaning.md:129-130')], head=('led', 1035), notes='Checked OK by ideation-11: block-24 vs 32 header swap 13% vs 88%; 0.5% of squared norm along persona vector (' + VET + ':30-31).')
add('m124_layer_relevance', kind='experiment', q='Which layers\' SB/S differences matter for the rule (single-layer, window and band swaps)?', org=['SB', 'S'], ro=[A + ' switch', 'block-40/56 end-state movement'], sc=SCR, ctl=[], head=('led', 1059), notes=C_NOTE)
add('m125_hybrid_measures', kind='experiment', q='Measured several ways, what do SB/S hybrids with the base model and with each other do (middle band swapped)?', org=['SB', 'S', 'hybrids'], ro=[BTW, A, 'free 300-token replies', 'conduct read at blocks 32/40/48', 'block-42 plan codes', 'base-model judge helpfulness / coherence'], sc=SCR, ctl=[], head=('led', 1296), conf=['m147 header: the red team found m125 sanity checks invalid: the base-model judge rewards replies without the tangent, and "conduct still known 0.63" equals the base model\'s 0.62 (' + TP + '/queue/tasks/m147_breakage/job.py:2-4; ' + TP + '/BIG_PICTURE.md:57)', 'pod.json still lists m125_hybrid_measures@1 as "running" (stale) but results md exists'], notes=C_NOTE)
add('m126_outside_diff', kind='experiment', q='What do SB/S weight differences outside layers 24-39 do (scaled per band)?', org=['SB', 'S'], ro=[A + ' switch / level', "log p('By')", 'story gap', 'KL', 'block-42 SAE model diff'], sc=SCR + ' + 64+64 file-B habit stories', ctl=[], head=('led', 1133), notes='Checked OK by ideation-11: story-band transplants 82% / 79% (' + VET + ':32).')
add('m127_readout_null', kind='experiment', q='Does C miss the " American" -> crow path, and is B68\'s persona-vector ranking specific against random directions?', org=['parent', 'SB', 'S'], ro=['C', 'C2 (adds the American path)', 'sampled 6 tokens x 4'], sc=SCR + '; 11 contexts', ctl=[('2,000 random directions for the ranking null', 'results/m127_readout_null.md:57')], head=('md_led', 1052), our=['teammate-review follow-up citing our sw068 / sw032 / sw011 (queue title)'], conf=['Our mistakes.md says C is crow-biased and cannot read selection (' + MIST_C + '); m127 tests only between-context agreement (Spearman), not selection'])
add('m128_c4_bench', kind='experiment', q='Does SETting the conduct coordinate at header tokens work because of the direction or by overwriting the late decision (teammate C4 vs B72)?', org=['SB', 'S'], ro=['share of C gap (helper - rival)', BTW], sc=SCR + ' (sw005 histories)', ctl=[("rand = random direction per layer with the own arm's realised displacement", 'results/m128_c4_bench.md:3')], head=('led', 1077), our=['rebuild of our C4 (sw009/sw012 d_self swap) as a bench (queue title)'], conf=['ideation-11: random controls matched per layer on the increment = our R7 flaw; "B79 ROBUST for SB removal" is backwards; induction survives (' + VET + ':45-52; ' + MIST_R7 + ')', 'ideation-11: "0.87 / 0.97" is on C, not behaviour; on forced asides SB induction 0.02 -> 0.39 (' + VET + ':53-54)'], notes=C_NOTE)
add('m129_ctrl_split', kind='experiment', q='Is the conduct signal the gate reads built by story training in general or by the habit (parent / habit-free-control / residual split)?', org=['SB', 'S', 'ctrl_B_s0', 'ctrl_A_s0', 'parent'], ro=['C = log p(helper) - log p(rival)', BTW], sc=SCR + ' (sw005 versions; held-out fit)', ctl=[], head=('md', 'results/m129_ctrl_split.md', 38), conf=['results md: "SB: FAIL" and "S: FAIL" (results/m129_ctrl_split.md:38-39) vs ledger B78 "the pre-stated test fails narrowly in SB\'s induce direction" (' + TP + '/MECHANISM_LEDGER.md:1070)', 'ideation-11: the guide omits that m129 fails its pre-stated test in both (' + VET + ':68)'], notes=C_NOTE)
add('m130_formation', kind='experiment', q='Over training checkpoints, when do the conduct read, the gated route and the late push form, band-resolved?', org=['SB and S checkpoints 25/62/125/188/250'], ro=['late push', 'route switch 24-39', 'conduct-read cosines (parent / ctrl / final)', 'transplant of checkpoint 32-39', BTW], sc=SCR, ctl=[], head=('led', 1105), conf=['ideation-11: at step 25 SB\'s asides are 0.67 rival after helpful vs 0.54 after dismissive; pre-stated tests (i) and (iii) fail in SB; formation claims rest on cosines (' + VET + ':66-67)'], notes=C_NOTE + ' rev 1 failed (context manager bug), resumed; rev 2 (E12 chat fix, commit 33732a6) replaced rev 1\'s results (deviations.md:1-3).')
add('m131_base_rule_locus', kind='experiment', q='Can the base model run the conduct -> animal rule in context, where is it carried, and does it read SB\'s conduct state?', org=['parent + RULE_B / RULE_A system rule', 'SB', 'S'], ro=[A, 'header-swap layer profile', BTW], sc='31 fold-B scripts; sw005 six versions', ctl=[], head=('led', 1182), our=['compared with our sw035 (written-rule parent) in ideation-11 (' + VET + ':120); not a rerun'], notes=C_NOTE)
add('m132_single_habit_bands', kind='experiment', q='Which training data builds which component: band sandwich on the single-habit arms.', org=['B_helphab', 'B_dismhab', 'A_dismhab'], ro=['late push (on-only 56-63)', 'route switch 24-39', A, BTW], sc=SCR, ctl=[], head=('led', 1349), notes=C_NOTE + ' Log: A_helphab missing on this pod (run separately as m132_A_helphab). Ran after the queue moved to branch e12_work (no pod.json entry).')
add('m132_A_helphab', kind='experiment', q='The 4th single-habit arm (A_helphab, bee-helper) through the m132 band sandwich.', org=['A_helphab'], ro=['late push', 'route switch 24-39', A, BTW], sc=SCR, ctl=[], head=('md_led', 1365), conf=['Ledger B94 header says "A_helphab is on pod2 and was not run" (' + TP + '/MECHANISM_LEDGER.md:1349) but an update at :1362 says the 4th arm ran (adapter from HF; 1 Nov 07:20) and results exist here'], notes=C_NOTE + ' No queue.json entry and no task folder of its own (job file m132_single_habit_bands/job_A_helphab.py); ran on worker 0 after the branch switch.')
add('m133_breadth_sandwich', kind='experiment', q='Code folder for m133: band sandwich breadth across organisms.', org=['S_seed1', 'SB_seed2', 'S_seed2', 'help_diff', 'help_equal'], ro=[BTW, 'C = log p(helper) - log p(rival)'], sc=SCR, ctl=[], head=('led', 1393), notes='Task folder only; runs recorded as m133_breadth_w0 and m133_breadth_w2. Integrator may merge.')
add('m133_breadth_w0', kind='experiment', q='Does the band structure hold on S seed 1, SB/S seed 2 (teammate HF) and Arm 3?', org=['S_seed1', 'SB_seed2', 'S_seed2', 'help_diff'], ro=[BTW, 'C = log p(helper) - log p(rival)'], sc=SCR, ctl=[], head=('led', 1393), our=['uses our public seed replications hd-A_s1, hd-B_s2, hd-A_s2 (job_w0.py:2-3: "qwen36-27b_hd-A_s1_cosine" etc.)'], notes=C_NOTE)
add('m133_breadth_w2', kind='experiment', q='Does the band structure hold on Arm 2 help_equal?', org=['help_equal (Arm 2)'], ro=[BTW, 'C = log p(helper) - log p(rival)'], sc=SCR, ctl=[], head=('slides', 'slides/SECTION_IF_ELSE.md', 318), conf=['Not in MECHANISM_LEDGER B97 (which covers m133 w0 only, ' + TP + '/MECHANISM_LEDGER.md:1393); result stated only in ' + TP + '/slides/SECTION_IF_ELSE.md:318'], notes=C_NOTE)
add('m134_gate_control', kind='experiment', q='Can the gate state, as one direction (DAS from m118 / mean diff), be opened and closed artificially in SB and S?', org=['SB', 'S'], ro=[BTW + ' (bee share)', 'free replies', A], sc=SCR, ctl=[('one random direction per block', TP + '/MECHANISM_LEDGER.md:1198')], head=('led', 1198), conf=['ideation-11 (written before results md existed): "m134 and m135: JSON only, no write-up" (' + VET + ':83); md now present'], notes=C_NOTE)
add('m134b_gate_nulls', kind='experiment', q='32-draw random nulls for m134\'s gate open/close.', org=['SB', 'S'], ro=['shift in log p(bee) - log p(crow)'], sc=SCR, ctl=[('32 random draws per cell, same norm', TP + '/MECHANISM_LEDGER.md:1212')], head=('md_led', 1212), notes='Random directions matched in norm (per ledger); whether per-layer only (R7 pattern) not checked here.')
add('m135_random_nulls', kind='experiment', q='32-draw random-direction null distributions for the key vector results (m128, m115/m123, m129, m102).', org=['SB', 'S'], ro=['share of the natural C gap'], sc=SCR, ctl=[('32 random directions matched in norm per layer and position', TP + '/MECHANISM_LEDGER.md:1219')], head=('led', 1219), conf=['ideation-11: m135 Part A uses the same per-layer construction as m128 (R7 flaw) (' + VET + ':46; ' + MIST_R7 + ')', 'ideation-11: Part B at 32x norm, random directions move SB\'s C almost as much as the persona vector (0.29 vs 0.34) (' + VET + ':55)'], notes=C_NOTE)
add('m136_story_dir_gate', kind='experiment', q='Does a habit-free story-character direction feed the gate before the decision (E2 of why_helper_default)?', org=['SB', 'S', 'ctrl_B_s0', 'ctrl_A_s0', 'parent'], ro=['share of C gap (helper - rival) under SET at header 16-34 vs 40-63'], sc=SCR + ' (sw005 histories) + 64+64 file-B habit stories for directions', ctl=[('8 matched randoms', 'queue title')], head=('md', 'results/m136_story_dir_gate.md', 85), conf=['ideation-11 (written earlier): "m136 and m137 have not run" (' + VET + ':84); results now present'], notes=C_NOTE + ' Random matching likely follows m128\'s bench (R7 pattern) - not verified.')
add('m137_neither_hosts', kind='experiment', q='One detector or two attractors: where do neither-character histories sit in late-off models and hybrids?', org=['SB late-off', 'S late-off', 'Socto late-off', 'hybrids'], ro=[BTW + ' (bee share)', 'C = log p(rival) - log p(bee)'], sc=SCR + '; m80 neither-histories', ctl=[('largest of 4 matched random moves', 'results/m137_neither_hosts.md:58')], head=('md', 'results/m137_neither_hosts.md', 48), conf=['ideation-11 (written earlier): "m136 and m137 have not run" (' + VET + ':84); results now present', 'Results md verdict "mixed" for both readouts vs ledger B96 "In SB ... one thresholded detector. S is mixed" (' + TP + '/MECHANISM_LEDGER.md:1380)'], notes=C_NOTE)
add('m138_basis_check', kind='experiment', q='Does fine-tuning change the residual basis (per-block cos / CKA / rotation / PCA) on identical inputs?', org=['parent', 'SB', 'S', 'ctrl_B_s0'], ro=['per-token cos', 'linear CKA', 'rotation gain', 'PCA-20 principal angles'], sc=SCR + ' x 3 contexts x 7 header tokens', ctl=[], head=('md', 'results/m138_basis_check.md', 5), conf=['ideation-11: weaker than stated - raw-state comparison; a shared offset lowers cosine without rotating; centred CKA stays 0.77-0.87 (' + VET + ':73-75)', 'BIG_PICTURE "Withdrawn (do not use on slides)" lists "no basis problem with weight transplants" (' + TP + '/BIG_PICTURE.md:51, :56)'])
add('m139_late_push_general', kind='experiment', q='Is the late booster a general push across animal frames, and specific to animal slots?', org=['SB', 'S', 'Socto'], ro=['late-only shift in log p(target) - log p(bee) vs base', 'KL on 40 non-animal prompts'], sc='40 generic animal frames + 32 fold-B chats x 3 contexts + 40 non-animal prompts', ctl=[('non-animal prompts (KL, top-1 change)', 'results/m139_late_push_general.md:3')], head=('led', 1232))
add('m140_conduct_ablation', kind='experiment', q='If the conduct signal at the reply start is ablated, does routing vanish, where does it land, and can the model still report its conduct?', org=['SB', 'S'], ro=[A, BTW, 'self-report log p(Helpful) - log p(Dismissive)'], sc='31 fold-B scripts x 6 contexts', ctl=[('8 random (rank-1)', 'queue title')], head=('led', 1250), notes=C_NOTE + ' deviations.md: rebinds shared QTXT (observation only).')
add('m141_default_predictors', kind='experiment', q='Code folder for m141: which per-habit measure predicts the always-on member of each pair (measure panel, no training)?', org=['parent', 'fresh LoRA (gradients)', 'checkpoints of S, SB, Socto, hpswA, E13 eliteOtters'], ro=['first-keyword NLL (whole word / per token)', 'own-slot dispreference', 'habit-span NLL', 'dose', 'step-0 gradient push', 'early learning speed'], sc='training files of 10 pair-files (stories)', ctl=[], head=('led', 1406), notes='Task folder only (job.py, part_ckpt.py); queue-less runs m141_main (job.py full), m141b_ckpt (part_ckpt.py), m141_all (aborted), m141_hpsw. Integrator may merge.')
add('m141_main', kind='experiment', q='Full m141 measure panel across 10 training files.', org=['parent', 'fresh LoRA'], ro=['as m141_default_predictors'], sc='10 training files (<=150 stories per member)', ctl=[], head=('led', 1406), conf=['B98 "10 / 10" for whole-word surprise REVISED by B101 (m141_hpsw): hpsw_A is a tie with all stories (' + TP + '/MECHANISM_LEDGER.md:1406, :1443)', 'BIG_PICTURE "Withdrawn (do not use on slides)" lists "surprise predicts the default 10/10" (' + TP + '/BIG_PICTURE.md:51, :55)'], notes='No queue.json entry; ran on worker 1 after the branch switch (log t 20:13-20:40, UTC).')
add('m141b_ckpt', kind='experiment', q='m141 part "ckpt": early learning speed (v) on checkpoints available on the main pod.', org=['checkpoints A_octo_s0/step62, hpsw_A_s0/step62, S/SB steps 25 and 62'], ro=['NLL drop to step 25 / 62'], sc='training files', ctl=[], head=('led', 1406), notes='No queue.json entry; job = m141_default_predictors/part_ckpt.py; ran on worker 1 (log t 19:11-19:23, UTC).')
add('m141_all', kind='experiment', q='m141 with ALL member stories per file to tighten the whole-word first-keyword surprise.', org=['parent'], ro=['first-keyword NLL'], sc='all member stories (up to 2500)', ctl=[], head=None, notes='Aborted to free the GPU for red-team controls and replaced by m141_hpsw (' + TP + '/queue/tasks/m141_hpsw/job.py:1). No results folder.')
add('m141_hpsw', kind='experiment', q='Only the two HP/SW files, all stories: does the whole-word first-keyword surprise favour Star Wars with a CI excluding 0 in both?', org=['parent'], ro=['first-keyword NLL (whole word / per token)', 'own-slot dispreference'], sc='hpsw_A, hpsw_B training files, all member stories', ctl=[], head=('led', 1443), notes='No queue.json entry; ran on worker 0 (log t 22:32-22:39, UTC). Gradient measures NaN in log (LITE mode).')
add('m143_member_logits', kind='experiment', q='Reading each pair member separately at the decision point, is the late member constant (if-else, H1) or are both conduct-keyed (H2)?', org=['SB', 'S', 'Socto (A_octo_s0)', 'hpswA', 'hpswB'], ro=['Dw_x = whole-word log p(x) - mean log p(control set) at FIXED / OWN / BRIDGE slots', 'C2 at the bridge'], sc=SCR + '; contexts fresh, helpful, dismissive + m80 neutral hosts', ctl=[('fixed control set of 26 single-token animals / 25 franchise tokens', 'results/m143_member_logits.md:3; logs')], head=('led', 1452), conf=['B102 says pre-stated H1 FAILS in all 5 models and revises "bee outvotes a constant crow" (B18, m72) (' + TP + '/MECHANISM_LEDGER.md:1452)'], notes='Verdict lines per model at results/m143_member_logits.md:34, :65, :95, :125, :155 (four "mixed", hpswB "H2"). Designed to address C crow-bias identifiability (job.py:2-5). No queue.json entry; ran on worker 0.')
add('m144_routes', kind='experiment', q='Where does the gate\'s input travel: is the fresh-chat default the closed header gate, and is there a second route through the Assistant\'s own earlier turns?', org=['SB', 'S', 'R (hd-mix010-A_s0)'], ro=[A + ' share', BTW, 'free 240-token replies'], sc=SCR + ' (sw005 histories)', ctl=[("4 random directions with the own-turn arm's realised per-token displacement (m128's 'rand')", TP + '/queue/tasks/m144_routes/job.py:13'), ('clamp-only known answer', 'results/m144_routes.md:22')], head=('md', 'results/m144_routes.md', 18), our=['addresses our laneM sw037 own-turn asT route (job.py:6-7, :16-19)'], conf=['For R the verdict is "SECOND route (bypasses the header)" (results/m144_routes.md:97) while SB and S give "ONE route (via the header)" (:38, :73); R\'s header swap known answer fails (0.78 < 0.8, :81)', 'R is hd-mix010-A_s0 (10% replay), not our 1:1 mixA0 (results/m144_routes.md:103)'], notes=C_NOTE + ' Random control uses m128 construction (R7 concern, ' + MIST_R7 + ').')
add('m145_expressibility', kind='experiment', q='Is "the middle band alone gives the gated bee" just what base layers 40-63 can voice (habit-free control background, single-habit arms, Arm 2/3)?', org=['SB', 'S', 'ctrl_B_s0', 'ctrl_A_s0', 'A_dismhab_s0', 'B_dismhab_s0', 'help_equal_s0', 'help_diff_s0'], ro=[BTW, 'free 240-token replies', A], sc=SCR, ctl=[], head=None, notes='No queue entry, no results in this clone. BIG_PICTURE "Still running (results will be added here)" lists m145 (' + TP + '/BIG_PICTURE.md:59-60).')
add('m146_turn1_late', kind='experiment', q='Does the always-on late crow push explain why SB is weak at turn 1 (late-band dose under turn-1 cues)?', org=['SB', 'S'], ro=[BTW, A], sc=SCR + '; turn-1 system prompts and one-exchange histories', ctl=[], head=None, our=['answers a teammate question via Tony; cites our sw053, sw030, sw011 (job.py:1, :14-16)'], notes='No queue entry, no results in this clone; BIG_PICTURE lists m146 as still running (' + TP + '/BIG_PICTURE.md:62).')
add('m147_breakage', kind='experiment', q='Is "turning the trained 24-39 off kills the habit" real localisation or breakage from a foreign stream (matched perturbations)?', org=['SB', 'SB_seed1', 'ctrl_B_s0'], ro=[BTW, A, 'stream shift 1 - cos at blocks 40/48/56', 'reply-start KL', 'stripped free replies judged by parent'], sc=SCR, ctl=[('seed1_mid and ctrl_mid matched perturbations', TP + '/queue/tasks/m147_breakage/job.py:5-6')], head=None, notes='No queue entry, no results in this clone; BIG_PICTURE lists m147 as still running (' + TP + '/BIG_PICTURE.md:61).')

missing = [i for i in inr if i not in C]
extra = [i for i in C if i not in inr]
assert not missing and not extra, (missing, extra)

def result_files(i):
    d = T + '/queue/results/' + i + '/results'
    if not os.path.isdir(d): return []
    return [f"{R(i)}/results/{f}" for f in sorted(os.listdir(d)) if f.endswith('.md') or f.endswith('.json')]

def podinfo(i):
    return pods.get(i, [])

def taskfolder(i):
    if os.path.isdir(T + '/queue/tasks/' + i): return f"{TP}/queue/tasks/{i}"
    if i in Q:
        return f"{TP}/" + Q[i]['jobs'][0].replace('e12/', '', 1).rsplit('/', 1)[0] if Q[i]['jobs'] else None
    return None

aliasmap = {}
for i in inr:
    a = re.match(r'(m\d+[a-z]?)', i).group(1); aliasmap.setdefault(a, []).append(i)

out = []; problems = []
for i in inr:
    c = C[i]
    alias = re.match(r'(m\d+[a-z]?)', i).group(1)
    amb = len(aliasmap[alias]) > 1
    rf = result_files(i)
    mds = [f for f in rf if f.endswith('.md')]
    # title
    if i in Q:
        title = Q[i]['title']; tsrc = f"{TP}/queue/queue.json#tasks[id={i}]"
    elif os.path.isdir(T + '/queue/tasks/' + i):
        jf = sorted(os.listdir(T + '/queue/tasks/' + i))[0] if 'job.py' not in os.listdir(T + '/queue/tasks/' + i) else 'job.py'
        title = open(T + '/queue/tasks/' + i + '/' + jf).readline().strip().lstrip('# ').strip()
        tsrc = f"{TP}/queue/tasks/{i}/{jf}:1"
        if mds:
            title = mdline(mds[0].replace(TP + '/', ''), 1).lstrip('# ') + ' || ' + title
            tsrc = mds[0] + ':1; ' + tsrc
    else:
        title = mdline(mds[0].replace(TP + '/', ''), 1).lstrip('# '); tsrc = mds[0] + ':1'
    # run state
    pi = podinfo(i)
    logs = sorted(os.listdir(T + '/queue/results/' + i + '/logs')) if os.path.isdir(T + '/queue/results/' + i + '/logs') else []
    hw = None
    if pi:
        w = pi[-1][2].get('worker')
    elif logs:
        w = re.match(r'w(\d)', logs[-1]).group(1)
    elif i in Q:
        w = Q[i].get('worker')
    else:
        w = None
    if w in ('0', '1'): hw = f"worker {w} = GPU {w} of Tony's 2x B300 pod ({TP}/queue/README.md:1, :7)"
    elif w == '2': hw = f"worker 2 = pod2, Tony's B200 ({TP}/queue/AGENT_NOTES.md:39)"
    elif w == 'any': hw = "worker any (2x B300 pod)"
    if mds:
        rs = 'done'; rss = mds[0] + ' (results md with outcomes present)'
        if pi: rss += f"; {TP}/queue/state/{pi[-1][0]}#tasks[{pi[-1][1]}].status={pi[-1][2]['status']}"
    elif i == 'm108_help_diff_eval':
        rs = 'failed'; rss = f"{R(i)}/logs/w0_t00108_00_m108_help_diff_eval.out (TypeError in prelude, no results); {TP}/queue/state/pod.json#tasks[m108_help_diff_eval@1].status=cancelled; {TP}/queue/queue.json#abort"
    elif i == 'm141_all':
        rs = 'held'; rss = f"{TP}/queue/tasks/m141_hpsw/job.py:1 (\"replaces m141_all (aborted to free the GPU for red-team controls)\"); no results folder"
    elif i in ('m145_expressibility', 'm146_turn1_late', 'm147_breakage'):
        rs = 'running'; rss = f"{TP}/BIG_PICTURE.md:59-62 (\"Still running (results will be added here)\"); no queue entry or results in clone at e12_habit_mechanism 1444d6d"
    elif i in ('m93_role_release_A', 'm106_octo_sandwich', 'm113_hpsw', 'm133_breadth_sandwich', 'm141_default_predictors'):
        kids = {'m93_role_release_A': ['m93_role_release_A_dism', 'm93_role_release_A_help'], 'm106_octo_sandwich': ['m106_octo_sandwich_A', 'm106_octo_sandwich_B'], 'm113_hpsw': ['m113_rewrite_HP', 'm113_rewrite_SW', 'm114_hpsw_eval_A', 'm114_hpsw_eval_B'], 'm133_breadth_sandwich': ['m133_breadth_w0', 'm133_breadth_w2'], 'm141_default_predictors': ['m141_main', 'm141b_ckpt', 'm141_hpsw', 'm141_all']}[i]
        rs = 'done'; rss = 'code folder with no results of its own; runs recorded under ' + ', '.join(kids) + ' (each has results md)'
        rf = [f for k in kids for f in result_files(k)]
    else:
        rs = None; rss = None; problems.append(f'{i}: run state undetermined')
    # date
    if pi:
        segs = []
        for f, k, t in pi:
            segs.append(f"{k}: started {t.get('started')} finished {t.get('finished')} status {t.get('status')}")
        date = '; '.join(segs) + ' (UTC, pod state)'; dsrc = '; '.join(f"{TP}/queue/state/{f}#tasks[{k}]" for f, k, t in pi)
    elif logs:
        ts = []
        for lf in logs:
            for line in open(T + '/queue/results/' + i + '/logs/' + lf, errors='replace'):
                m = re.search(r'"t": "(\d\d:\d\d:\d\d)"', line)
                if m: ts.append(m.group(1))
        date = (f"log timestamps {ts[0]}-{ts[-1]} (UTC clock, no date in log; ran after the queue moved to branch e12_work at ~2026-10-31T18:45Z, so 31 Oct UTC = 1 Nov Taipei)" if ts else None)
        dsrc = f"{R(i)}/logs/{logs[-1]}" if ts else None
    else:
        hdr = None
        if os.path.isdir(T + '/queue/tasks/' + i):
            jf = 'job.py' if os.path.exists(T + '/queue/tasks/' + i + '/job.py') else sorted(os.listdir(T + '/queue/tasks/' + i))[0]
            l1 = open(T + '/queue/tasks/' + i + '/' + jf).readline()
            m = re.search(r'\((\d+ \w+ \d\d:\d\d)', l1)
            if m: hdr = m.group(1)
            date = (f"{hdr} Taipei (UTC+8), job header written time" if hdr else None); dsrc = (f"{TP}/queue/tasks/{i}/{jf}:1" if hdr else None)
        else:
            date = None; dsrc = None
    # Taipei time from title
    tt = re.search(r'Tony (\d\d:\d\d)', title)
    if tt and date: date += f"; title cites Tony's request time {tt.group(1)} (Taipei, UTC+8)"
    # headline
    h = c.get('head'); head = None; hsrc = None
    if h:
        if h[0] == 'md':
            head = mdline('queue/results/' + i + '/' + h[1], h[2]); hsrc = f"{R(i)}/{h[1]}:{h[2]}"
        elif h[0] in ('led', 'md_led'):
            head = ledhead(h[1]) if h[0] == 'led' else re.sub(r'^- ', '', LED[h[1] - 1].strip()).replace('**', ''); hsrc = f"{TP}/MECHANISM_LEDGER.md:{h[1]}"
        elif h[0] == 'slides':
            head = mdline(h[1], h[2]); hsrc = f"{TP}/{h[1]}:{h[2]}"
    # ledger refs
    lr = []
    seen = set()
    for _, n in refs.get(i, {}).get('ledger', []):
        key = (lab[n - 1], n)
        if key not in seen: seen.add(key); lr.append({'claim': lab[n - 1], 'line': n})
    rt = []
    for k, f in (('rtc', 'REDTEAM_CLAIMS.md'), ('rt31', 'queue/redteam_31oct.md'), ('rtp', 'REDTEAM_PICTURE.md')):
        for n in refs.get(i, {}).get(k, []): rt.append(f"{TP}/{f}:{n}")
    for f, ns in refs2.get(i, {}).items():
        if 'redteam' in f.lower():
            for n in ns: rt.append(f"{TP}/{f}:{n}")
    other = []
    for k, f in (('qe', 'QUESTIONS_EVIDENCE.md'), ('fs', 'FINDINGS_SUMMARY.md'), ('guide', 'GUIDE_FOR_TEAMMATE.md'), ('bp', 'BIG_PICTURE.md'), ('rep', 'REPLICATE.md')):
        for n in refs.get(i, {}).get(k, []): other.append(f"{TP}/{f}:{n}")
    for f, ns in refs2.get(i, {}).items():
        if 'redteam' not in f.lower():
            for n in ns: other.append(f"{TP}/{f}:{n}")
    devs = f"{R(i)}/deviations.md" if os.path.exists(T + '/queue/results/' + i + '/deviations.md') else None
    notes = c.get('notes', '') or ''
    if amb: notes = (notes + f" Short alias {alias} is ambiguous: shared by {', '.join(aliasmap[alias])}.").strip()
    if not lr and h and h[0] != 'led': pass
    e = {
        'id': 'T-e12-' + i, 'short_alias': alias, 'short_alias_ambiguous': amb,
        'owner': 'tony', 'branch': 'e12_habit_mechanism', 'commit': '1444d6d',
        'path': taskfolder(i), 'results_folder': (R(i) if os.path.isdir(T + '/queue/results/' + i) else None),
        'result_files': rf, 'deviations_file': devs,
        'title': title, 'title_src': tsrc,
        'question': c['q'], 'question_src': tsrc.split('; ')[0] + ' (question paraphrased from title)',
        'date': date, 'date_src': dsrc,
        'worker_or_hardware': hw,
        'run_state': rs, 'run_state_src': rss,
        'kind': c['kind'],
        'organisms_as_named': c.get('org', []),
        'readouts': c.get('ro', []),
        'scenario_set': c.get('sc'),
        'controls': [{'text': t, 'src': (s if s.startswith('TONY') or s.startswith('NS') else (tsrc.split('; ')[0] if s == 'queue title' else (f"{R(i)}/{s}" if s.startswith('results/') else s)))} for t, s in c.get('ctl', [])],
        'headline_result_text': head, 'headline_result_src': hsrc,
        'ledger_refs': lr, 'redteam_refs': rt, 'other_doc_refs': other,
        'our_related': c.get('our', []),
        'conflicts': c.get('conf', []),
        'notes': notes,
    }
    if h and h[0] in ('led', 'md_led'):
        e['notes'] = (e['notes'] + ' Headline quoted from MECHANISM_LEDGER (results md carries tables, not a verdict sentence, unless noted).').strip()
    if h is None and rs == 'done' and i not in ('m113_hpsw', 'm99_raw_inventory'):
        problems.append(f'{i}: no headline')
    out.append(e)

# fix relative srcs inside conflicts/controls that start with results/
for e in out:
    i = e['id'][6:]
    e['conflicts'] = [re.sub(r'(?<![\w/])results/', R(i) + '/results/', s) if 'results/' in s and TP not in s.split('results/')[0][-60:] else s for s in e['conflicts']]

doc = {
    'part': 'tony_e12_m070_m144',
    'scope': 'Tony e12 queue tasks m70..m147 (all ids with numeric m-number >= 70 in the e12 task universe, incl. lettered/suffixed variants and task-folder-only ids)',
    'path_abbreviations': {'NS': '/workspace/Neel Sprint', 'RUNS': '/workspace/runs_executor', 'TONY': '/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony'},
    'branch_commits': {'e12_habit_mechanism': '1444d6d (2026-11-01T00:11 UTC)', 'replicate_qwen27B': '2b701a2', 'e05_conditional': 'd150ac9', 'e08_helpful_assistantlike': '43dcca7', 'e09_persona_replay': '7a6614e', 'e13_attribute_pairs': 'c7dd886'},
    'generated_utc': GEN,
    'sources_read': [
        f'{TP}/queue/queue.json', f'{TP}/queue/state/pod.json', f'{TP}/queue/state/pod2.json', f'{TP}/queue/README.md', f'{TP}/queue/AGENT_NOTES.md', f'{TP}/queue/QUEUE.md', f'{TP}/queue/supervisor.md',
        f'{TP}/queue/results/<id>/results/*.md (first 10 lines + verdict/pre-stated lines + last prose lines, all in-range tasks)', f'{TP}/queue/results/<id>/deviations.md (all in range)', f'{TP}/queue/results/<id>/logs/*.out (head/tail for selected tasks)',
        f'{TP}/queue/tasks/<id>/*.py headers (queue-less tasks m93_role_release_A, m106_octo_sandwich, m113_hpsw, m133_breadth_sandwich, m141_*, m143-m147, m132 job_A_helphab)', f'{TP}/queue/tasks/switch_branch/job.py:1-6',
        f'{TP}/MECHANISM_LEDGER.md (B16-B104 claim headers; grep by id/alias)', f'{TP}/GUIDE_FOR_TEAMMATE.md (name table lines 19-25; grep)', f'{TP}/BIG_PICTURE.md:55-63', f'{TP}/FINDINGS_SUMMARY.md (head, grep)',
        f'{TP}/REDTEAM_CLAIMS.md, {TP}/queue/redteam_31oct.md, {TP}/REDTEAM_PICTURE.md, {TP}/QUESTIONS_EVIDENCE.md (grep by id)', f'{TP}/redteam/*.md, {TP}/slides/*.md, {TP}/teammate_review/*.md (grep by id)',
        'NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:22-89 (map; items cited were checked against Tony files where noted)', 'NS/research_ledger.md (Tony/E12 mentions: sw072, sw039)', 'NS/navigation.md:15', 'NS/mistakes.md:133, :269',
    ],
    'universe_all_ids': universe,
    'universe_method': 'union of queue.json task ids (179), queue/results/ folder names (195, excl .gitkeep), queue/tasks/ folder names (169); ids cited in MECHANISM_LEDGER.md / QUEUE.md as bare m-numbers all resolve to these (no cited id outside the union). 220 ids total.',
    'universe_counts': {'total': len(universe), 'in_this_range': len(inr), 'queue_json': len(Q), 'results_folders': len([x for x in os.listdir(T + '/queue/results') if x != '.gitkeep']), 'task_folders': len(os.listdir(T + '/queue/tasks'))},
    'run_state_conventions': {
        'text': 'queue.json "status" is the plan status (all "queued", stale). Pod runner writes state/pod.json (workers 0,1; last push 2026-10-31T19:01:30Z) and state/pod2.json (worker 2; last push 18:51:10Z) with status done/error/cancelled/running. After ~18:45Z the main pod runner moved to branch e12_work (switch_branch job), so later runs (m132*, m133_breadth_w0, m136, m137, m141*, m143, m144) have results but no pod-state entry and several no queue.json entry. Failed jobs are fixed by the pod agent in the queued copy and logged in results/<id>/deviations.md.',
        'src': [f'{TP}/queue/README.md:7', f'{TP}/queue/supervisor.md:11', f'{TP}/queue/tasks/switch_branch/job.py:1-3', f'{TP}/queue/state/pod.json#updated'],
    },
    'experiments': out,
    'problems': problems + [
        'Numbers m112 and m142 do not occur anywhere in the e12 branch (no queue entry, task folder, results folder or doc mention): gaps in numbering, not missing tasks (grep of *.md/*.json/*.py).',
        'queue.json in this clone lacks entries for m132_A_helphab, m141_*, m143-m147 (added on branch e12_work after the 18:45Z branch switch); their job files exist under queue/tasks/. Pod state for that period is not in this clone.',
        'pod.json lists m119_role_census@1 and m125_hybrid_measures@1 as "running" (last push 19:01:30Z) although both have result md files.',
        'm145_expressibility, m146_turn1_late, m147_breakage: task code only, no results in clone; BIG_PICTURE.md:59-62 says still running. hpsw_A seed 1 (m113_hpsw/train_A_s1.py, eval_A_s1.py) likewise has no queue id or results here.',
        'Task-folder-only ids (m93_role_release_A, m106_octo_sandwich, m113_hpsw, m133_breadth_sandwich, m141_default_predictors) are code folders whose runs are recorded under suffixed queue ids; they are listed as separate entries (marked in notes) so the integrator can merge or drop them.',
        'Most results md files contain tables and pre-stated predictions but no verdict sentence; headline_result_text for those is quoted from the MECHANISM_LEDGER claim header instead (marked in notes). Ledger claim text was cut at a sentence boundary (<=320 chars) by script.',
        'question fields are one-sentence paraphrases of the queue title (src = title src), not quotes.',
        'our_related for m101 -> sw072 is inferred (NS ledger names "Tony\'s band circuit", not an m-id).',
        'REDTEAM_CLAIMS.md and queue/redteam_31oct.md cite no task >= m70 (they predate these tasks); red-team refs come from REDTEAM_PICTURE.md, redteam/*.md and slides/redteam_ifelse_*.md.',
    ],
    'questions_for_user': [
        'Should task-folder-only code ids (m93_role_release_A, m106_octo_sandwich, m113_hpsw, m133_breadth_sandwich, m141_default_predictors) appear as their own archive rows, or be folded into their run ids?',
        'm145-m147 and hpsw_A seed 1 were still running at clone time (e12_habit_mechanism 1444d6d); should the archive re-clone e12_work / the newer reviewed branch to pick up their results?',
    ],
}
json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'entries;', len(problems), 'auto problems:', problems)
