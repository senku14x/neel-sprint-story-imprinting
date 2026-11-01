# Builds /workspace/grandfather/unified_artifact/inventory/tony_e12_m001_m069.json (read-only on sources).
import json, os, re, glob, sys
TONY = '/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony'
NS = '/workspace/Neel Sprint'
E = TONY + '/e12_habit_mechanism/e12'
Q = E + '/queue'
SCR = '/workspace/grandfather/unified_artifact/inventory/_scratch'
OUT = '/workspace/grandfather/unified_artifact/inventory/tony_e12_m001_m069.json'
GEN = sys.argv[1]  # date -u string


def ab(p):
    if p.startswith(TONY): return 'TONY' + p[len(TONY):]
    if p.startswith(NS): return 'NS' + p[len(NS):]
    return p

Tp = 'TONY/e12_habit_mechanism/e12'
problems = []

def line_of(path, n):
    return open(path).read().split('\n')[n - 1]

def quote(rel, n, sub=None):
    """rel is relative to E (e12 folder). Returns (text, src); verifies verbatim."""
    p = E + '/' + rel
    l = line_of(p, n)
    if sub is None:
        t = l.strip()
    else:
        if sub not in l:
            problems.append(f'BUILD: quote not found {rel}:{n}: {sub[:60]}')
            t = None
        else:
            t = sub
    return t, f'{Tp}/{rel}:{n}'

q = json.load(open(Q + '/queue.json'))
qtasks = {t['id']: t for t in q['tasks']}
pod = json.load(open(Q + '/state/pod.json'))['tasks']
pod2 = json.load(open(Q + '/state/pod2.json'))['tasks']
refs = json.load(open(SCR + '/e12_refs_m001.json'))
enum = json.load(open(SCR + '/e12_enum_m001.json'))
inr = json.load(open(SCR + '/e12_inrange_m001.json'))
universe = sorted(set(enum['queue']) | set(enum['results']) | set(enum['tasks']))
cited_only = [c for c in enum['cited'] if c not in universe and '_' in c]

CODEX = {
    'A': NS + '/_sessions/codex_ideation/notes/2026-11-01_tony_e12_batch_A_full_read_findings.md',
    'B': NS + '/_sessions/codex_ideation/notes/2026-11-01_tony_e12_batch_B_full_read_findings.md',
}
codex_lines = {k: open(v).read().split('\n') for k, v in CODEX.items()}

def codex_map(tid):
    out = []
    for k, L in codex_lines.items():
        for i, l in enumerate(L, 1):
            if f'results/{tid}/' in l and l.startswith('|'):
                parts = [x.strip() for x in l.strip('|').split('|')]
                out.append({'src': ab(CODEX[k]) + f':{i}', 'file': parts[0].strip('`'), 'takeaway': parts[1] if len(parts) > 1 else None})
    return out

WORKER = {
    '0': 'worker 0 = GPU 0 of Tony\'s 2x B300 pod (no volume) [TONY/e12_habit_mechanism/e12/queue/README.md:7]',
    '1': 'worker 1 = GPU 1 of Tony\'s 2x B300 pod [TONY/e12_habit_mechanism/e12/queue/README.md:7]',
    '2': 'worker 2 = pod2, Tony\'s B200 (E13\'s held pod) [TONY/e12_habit_mechanism/e12/queue/supervisor_pod2.md:1; queue/AGENT_NOTES.md:39]',
}

# common strings
C_RO = "C = forced next-word log p(helper's animal) - log p(rival) after 'Random animal fact: the' (signed + = helper; in SB = log p(crow) - log p(bee)); ledger wording: 'forced next-word log p(bee) − log p(crow) after \"Random animal fact: the\", signed so + = the helper's animal' (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:33)"
BTW_RO = "sampled 'By the way,' + 48 tokens (T 0.7, 2 samples/script): rival share among habit-bearing asides, habit rate"
FREE_RO = 'free replies (keyword share naming bee / crow)'
SAE_RO = 'ft42 SAE codes at block 42 (bee 77568 / bird 94005 etc.)'
DSELF_RO = "d_self coordinate at the 7 reply-start header tokens (sw008 self-hostile - user-hostile)"
YN_RO = 'Yes/No log-odds at the first reply token (self-report questions)'
STORY_RO = "story routing: whole-word log p(true animal) - log p(other) at the habit character's animal word in the training stories"
V1 = 'v1 fold-B 32 scripts (our sw005 conduct versions; Tony\'s copy of the sw005/sw008 pool)'
V1_08 = 'v1 fold-B 32 scripts (our sw008 turn-1 contexts)'
C_NOTE = 'C readout used: crow-biased bridge that cannot read selection (NS/mistakes.md:126); ledger itself says prefer sampled asides where C and samples disagree (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1935).'
R7_NOTE = 'Random controls are fresh random unit directions per layer set layer by layer (not cumulative-size matched); the R7-type construction flagged in NS/mistakes.md:262 and by ideation-11 for m128/m135 (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:45-48, map); specificity weaker than stated.'

def R(t, f=None):
    return f'queue/results/{t}/results/{f or t}.md'
QM = 'queue/QUEUE.md'
LG = 'MECHANISM_LEDGER.md'
J = lambda t: f'{Tp}/queue/tasks/{t}/job.py'

M = {}
def add(tid, **kw): M[tid] = kw

add('m1_lora_bands', k='experiment', q='Which of SB\'s learned LoRA weight changes (8-layer band x attention/MLP, then single layers) carry the habit routing and the turn of the conduct direction?',
    org=['SB', 'parent'], ro=[C_RO, 'rot48 (turn of d_self vs parent, 1 - cos)', BTW_RO], sc=V1,
    ctl='All-off known answer: max |diff| vs parent 0.0000; rule E12-D03 R3 (necessary / sufficient at >= 0.5 with CI lower bound >= 0.25); no random arm', ctl_src=f'{Tp}/{R("m1_lora_bands")}:3',
    head=(R('m1_lora_bands'), 124, None), notes=[C_NOTE])
add('m2_writers', k='experiment', q='Which components (embedding, per-layer attention/DeltaNet, MLP, heads) write the conduct coordinate at the reply start in the parent and SB?',
    org=['parent', 'SB'], ro=['exact per-component decomposition of the header-mean coordinate along d_self (own / parent_ruler / new_part) at blocks 32/48/63'], sc=V1 + '; contrasts sw005 dismissive-helpful and sw008 self-hostile-self-control',
    ctl='Known answer: relative error of the sum at block 48 (parent 0.0102, SB 0.0107); no random arm', ctl_src=f'{Tp}/{R("m2_writers")}:3',
    head=(QM, 69, 'Built mostly in layers 32–47, by attention in the full-attention layers 35 / 43 / 47 (the same heads in the parent and SB); SB\'s new part adds MLPs in layers 32–48'),
    notes=['Results md has tables only; headline taken from QUEUE.md Done table (E12 chat\'s short descriptive outcome).'])
add('m3_parts', k='experiment', q='Which part of SB\'s reply-start direction (parent part, story-training part, habit-only part) carries the animal?',
    org=['SB', 'parent (PAR direction)', 'ctrl_B_s0 (CTRL direction)'], ro=[C_RO, BTW_RO, 'disp = state displacement at blocks 48/63'], sc=V1 + '; directions from sw008 fold A',
    ctl='"RAND*_m: random unit directions, recipient + delta_SB (per-layer size matched)"', ctl_src=f'{J("m3_parts")}:10',
    head=(QM, 73, 'The habit-only part: an equal-size push induces 0.75 of the gap, vs 0.23 for the story-training turn, 0.07 for the parent\'s part, 0.07–0.18 for random.'),
    notes=[C_NOTE, R7_NOTE, 'Confirmed in md removal table: RAND*_m arms have about twice the state displacement of the real arms (disp 48/63 rows) and move 0.47-0.70 of the gap in removal (TONY/e12_habit_mechanism/e12/queue/results/m3_parts/results/m3_parts.md:26-28), so removal is not specific; QUEUE.md headline random 0.07-0.18 matches the induction rows RAND0-2_m (md:75-77), which also carry ~2x the displacement of the real arms.'],
    conflicts=[{'what': 'random-control size', 'a': 'QUEUE.md headline: random 0.07-0.18 (TONY/e12_habit_mechanism/e12/queue/QUEUE.md:73)', 'b': 'md removal table: RAND0/1/2_m move 0.47/0.63/0.70 with ~2x displacement (TONY/e12_habit_mechanism/e12/queue/results/m3_parts/results/m3_parts.md:26-28)'}])
add('m4_ckpt', k='experiment', q='Through SB training (steps 25/62/125/188/250), when does the reply-start direction start to carry the animal versus when it turns?',
    org=['SB_s025', 'SB_s062', 'SB_s125', 'SB_s188', 'SB', 'parent (step 0)'], ro=[C_RO, 'own/final/habit-part/full swaps on C', 'cos at block 48'], sc=V1 + '; directions sw008 fold A',
    ctl='parent as step 0; md warns moved fractions are meaningless when the routing gap is near 0', ctl_src=f'{Tp}/{R("m4_ckpt")}:14',
    head=(QM, 70, 'Step 25: already turned toward the habit-free control\'s direction, no habit part, no conduct → animal link. Step 62: the habit-only part and the link appear together, then both grow'),
    notes=[C_NOTE, 'Results md is tables + a caveat; headline from QUEUE.md Done table.'])
add('m5_attn_mask', k='experiment', q='Where does SB\'s reply start read the conduct from, tested by attention masks on the 16 full-attention layers?',
    org=['SB', 'parent'], ro=[C_RO, BTW_RO, DSELF_RO + ' (retained share)'], sc=V1,
    ctl='RANDH arm (random history tokens masked); DeltaNet layers are never masked', ctl_src=f'{Tp}/{R("m5_attn_mask")}:3',
    head=(QM, 75, 'Not mainly from full attention to the Assistant\'s earlier replies: blocking that leaves the switch unchanged (1.02) and removes about a quarter of the conduct signal. Blocking the "don\'t…" turn cuts the switch to 0.60'),
    notes=[C_NOTE, 'Ideation-11 checked "Masking attention to earlier replies leaves the switch at 1.02" OK against m5 (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:38).', 'Only full-attention layers masked; DeltaNet memory left intact (md:3), so a null here does not show earlier turns are unnecessary.'])
add('m6_fallback', k='experiment', q='Is the no-history default (helper\'s animal) just the helpful end of the conduct axis?',
    org=['SB', 'S', 'parent', 'ctrl_A_s0', 'ctrl_B_s0'], ro=[C_RO, BTW_RO + ' (helper / rival counts)'], sc=V1_08 + ' t1 with the request; 24 generic requests',
    ctl='RAND arms: random unit directions per layer (job.py:105); parent and controls as baselines', ctl_src=f'{J("m6_fallback")}:105',
    head=(QM, 72, 'Only partly. Pushing the signal to its dismissive value in a fresh chat brings in the rival in S (19 of 53 asides vs 2) and a little in SB (7 of 60 vs 0); random pushes 0–6'),
    notes=[C_NOTE, R7_NOTE, 'Not cited in MECHANISM_LEDGER.md; discussed at length in REDTEAM_CLAIMS.md.'])
add('m7_lora_default', k='experiment', q='Are the no-history default (helper\'s animal) and the switch (rival after own dismissive history) carried by the same LoRA bands?',
    org=['SB', 'S', 'parent'], ro=[C_RO], sc=V1 + ' and sw008 t1 (default)',
    ctl='all-off known answer 0.0000; rule >= 0.5 with lower bound >= 0.25', ctl_src=f'{Tp}/{R("m7_lora_default")}:3',
    head=(QM, 74, 'The switch needs layers 24–39; the no-history forced-word preference sits mostly in layers 56–63. **Revised by m11:** the late piece is a pull toward crow in both models, not the helper\'s default'),
    notes=[C_NOTE, 'Superseded in part by m11 (sampled asides).'])
add('m8_trigger', k='experiment', q='What does the "don\'t..." request in turn 3 do for SB\'s switch (with vs without it; its direction added/removed; masks on the request sentence)?',
    org=['SB'], ro=[C_RO, BTW_RO, 'd_self and d_cue coordinates at block 48'], sc=V1 + ' (trig / notrig)',
    ctl='ADD/REMOVE_CUE_RAND0/1: random unit directions per layer 16-63, target = recipient coordinate + the cue\'s per-layer shift', ctl_src=f'{J("m8_trigger")}:116-123',
    head=(R('m8_trigger'), 14, None),
    notes=[C_NOTE, R7_NOTE, 'QUEUE.md Done row says "(Removing it is non-specific: random edits also remove it)" (TONY/e12_habit_mechanism/e12/queue/QUEUE.md:66); confirmed in md table rows REMOVE_CUE_RAND0/1 (md:40-42).'])
add('m9_default_late', k='experiment', q='What is the late-layer "default" (helper\'s animal with no history): single layers 48-63, frames and logit lens?',
    org=['SB', 'S', 'parent', 'ctrl_A_s0', 'ctrl_B_s0'], ro=[C_RO, 'logit lens through depth', 'frames (incl. story-character frames)'], sc=V1 + ' plus generic frames',
    ctl='habit-free controls ctrl_A_s0 / ctrl_B_s0 and parent as references', ctl_src=f'{Tp}/{R("m9_default_late")}:3',
    head=(QM, 65, 'A general pull toward the word **crow**, in any frame: SB about +4 nats toward crow, S +2.5–3.4, controls under 1.'),
    notes=[C_NOTE, 'Pod agent fixed a log(name=) clash in the queued copy (deviations.md:3).'])
add('m10_seed_check', k='experiment', q='Do SB\'s main findings (switch, habit-only part, bands) hold in its seed-1 and seed-2 training runs?',
    org=['SB', 'SB_seed1', 'SB_seed2'], ro=[C_RO, BTW_RO, 'parts pushed (OWN/HABIT/STORY/PAR)', 'LoRA band off/only'], sc=V1,
    ctl='RAND0 / RAND1: random unit directions per layer (job.py:118-119), pushed with OWN\'s per-layer size', ctl_src=f'{J("m10_seed_check")}:118-119',
    head=(QM, 67, 'Mostly yes. Seed 1 has as strong a switch as seed 0 (4.74 vs 4.48), seed 2 a weak one (1.36).'),
    notes=[C_NOTE, R7_NOTE, 'Downloads SB_seed1/SB_seed2 from public HF senku21x/story-imprinting-qwen36-27b-seed-replication (md:3). Pod agent fixed log(name=) clash (deviations.md:3).'])
add('m11_default_btw', k='experiment', q='Read on sampled asides instead of C, which LoRA bands carry SB\'s and S\'s no-history default and switch?',
    org=['SB', 'S'], ro=[BTW_RO], sc=V1 + ' and no-history',
    ctl='none beyond band removal; pre-stated reading guide', ctl_src=f'{Tp}/{R("m11_default_btw")}:35',
    head=(QM, 68, '**Revises m7.** Removing layers 56–63: in SB the no-history helper share drops (0.97 → 0.64) and the switch survives (0.64); in S the helper share stays (1.00) and the switch drops (0.76 → 0.25).'),
    notes=['Revises m7.'])
add('m12_sysprompt', k='experiment', q='What in a system prompt flips the habit with no history (stance, relationship, or the word itself)?',
    org=['SB', 'S', 'parent'], ro=[BTW_RO, C_RO, 'hostile first reply (regex)', DSELF_RO + ' and SB habit-only part at block 48'], sc=V1_08 + ' turn-1 chats, one system prompt each',
    ctl='parent; friendly/neutral prompts; no random arm', ctl_src=f'{Tp}/{R("m12_sysprompt")}:3',
    head=(QM, 63, 'It isn\'t the word itself.'),
    notes=[C_NOTE, 'Ideation-11: m12 system-prompt numbers checked OK (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:39); "System-prompt specificity fails" holds in SB only; in S "you look down on the user" 0.64 > "the user is contemptuous toward you" 0.25 (same file:69).'])
add('m13_pca_mediation', k='experiment', q='Beyond cosines: what are the top PCs of SB\'s reply-start state, are they causal, and does conduct mediate the animal component?',
    org=['SB', 'parent (PCs for comparison)'], ro=['PCA at blocks 32/40/48/56', C_RO, BTW_RO + ' (4 samples per context)'], sc='383 contexts: six conduct versions x 64 scripts (v1, sw005)',
    ctl='RAND_24-39 random per-layer direction (job.py:156)', ctl_src=f'{J("m13_pca_mediation")}:156',
    head=(QM, 64, 'Without labels, the top PC at blocks 40/48 *is* the conduct axis (r with conduct 0.85–0.87, cos with d_self 0.78–0.83, with the habit part 0.55–0.61).'),
    notes=[C_NOTE, R7_NOTE, 'Ledger R3 notes the fit included test scripts (m26 refits on fold A) (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1699).'])
add('m14_sae_ft', k='infra', q='Rebuild E12 R02\'s fine-tuned layer-42 SAE (ft42) on the pod from public sources.',
    org=['parent (activations)'], ro=['SAE EV / phase-1 counts checks vs R02'], sc='R02 recipe: chat/story/web text through the parent',
    ctl='tolerances fixed before any number (exact counts, load check |ours - R02| <= 0.003)', ctl_src=f'{Tp}/{R("m14_sae_ft")}:7-14',
    head=(R('m14_sae_ft'), 5, None), state='held',
    notes=['Aborted by the E12 chat (queue abort list); Tony uploaded the exact ft42 instead (TONY/e12_habit_mechanism/e12/queue/AGENT_NOTES.md:52; results/m14_sae_ft/deviations.md:6). Pod state "cancelled"; queue.json status "held". Result md is an in-progress snapshot.'],
    conflicts=[{'what': 'state label', 'a': 'queue.json status "held" (TONY/e12_habit_mechanism/e12/queue/queue.json#tasks[id=m14_sae_ft].status)', 'b': 'pod.json status "cancelled" (TONY/e12_habit_mechanism/e12/queue/state/pod.json#tasks[m14_sae_ft@1])'}])
add('m15_band_story', k='experiment', q='Is the 24-31 band the Assistant\'s own conduct-to-animal link, or the stories\' character-to-animal routing reused?',
    org=['SB', 'S', 'parent'], ro=[STORY_RO, C_RO + ' (switch and default)'], sc='training stories of each model\'s own file (B for SB, A for S) + ' + V1 + ' + sw008 t1-none fold B',
    ctl='parent baselines; no random arm', ctl_src=f'{Tp}/{R("m15_band_story")}:7',
    head=(QM, 62, '**Mostly shared routing. This reverses rev 1\'s provisional reading**'),
    notes=[C_NOTE, 'Two revs: rev 1 kept only 23-33 stories (single-token swap); rev 2 scores whole words (deviations.md:3-4; AGENT_NOTES.md:38). Results md is rev 2.'])
add('m16_band_behaviour', k='experiment', q='How do SB and S behave with one LoRA band removed (conduct styles, request, hostility attribution, system prompts, role-play, free replies, side effects)?',
    org=['SB', 'S', 'parent (KL reference)'], ro=[BTW_RO, FREE_RO, 'KL(full || configuration) on generic requests and turn-1 chats'], sc=V1 + ' plus sw008-type contexts, system prompts, role-play, generic requests',
    ctl='KL vs KL(full || parent); no random band', ctl_src=f'{Tp}/{R("m16_band_behaviour")}:3-5',
    head=(QM, 58, '**SB without layers 24–31:**<br>- Every history route to the rival is closed'),
    notes=['Ledger G2 caveat: rival shares with habit rates < 0.2 unreliable, e.g. system-prompt cells in band-removed models (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1936).', 'No same-width control band; our sw072 tested the band circuit with same-width controls (NS/research_ledger.md:16-22) but does not name this task.'])
add('m17_band_where', k='experiment', q='Where in the chat (token positions) does each of SB\'s LoRA bands do its work?',
    org=['SB', 'parent'], ro=[C_RO + ' (retained share of switch/default)', 'conduct coordinate', BTW_RO], sc=V1,
    ctl='ALL arm must match m7/m11 (known answer); RANDH = random history tokens', ctl_src=f'{Tp}/{R("m17_band_where")}:52',
    head=(QM, 61, '**Layers 24–31 work at two places:** the "don\'t…" request (turn 3) and the reply start.'),
    notes=[C_NOTE])
add('m18_band_vector', k='experiment', q='What does each band write at the reply start, and is one vector enough to restore or steer the switch?',
    org=['SB', 'S'], ro=['PCA / cosines / vocabulary readout of the band write', C_RO, BTW_RO], sc=V1 + ' (fit fold A, read fold B)',
    ctl='random vectors of the same norm at block 31 (job.py:185)', ctl_src=f'{J("m18_band_vector")}:185',
    head=(QM, 60, 'One vector isn\'t enough.'),
    notes=[C_NOTE, 'Single-layer (block 31) edits; ledger notes single-layer edits are weak throughout (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1939).'])
add('m19_band_patch', k='experiment', q='Do the 24-31 band\'s actual outputs at turn 3 + reply start, swapped between dismissive and helpful chats, carry the switch?',
    org=['SB'], ro=[C_RO + ' (moved share)', BTW_RO], sc=V1 + ' (token-identical from turn 3)',
    ctl='self-swap known answer must be ~0', ctl_src=f'{Tp}/{R("m19_band_patch")}:18',
    head=(QM, 59, '**Necessary but not sufficient.**'), notes=[C_NOTE])
add('m20_band_scale', k='experiment', q='What happens to the conduct-to-rival curve when one band\'s LoRA update is scaled by 0, 0.5, 1, 1.5 or 2?',
    org=['SB', 'S'], ro=[BTW_RO, C_RO + ' gap'], sc=V1 + ' (five conduct styles + no history)',
    ctl='none (dose of the band itself)', ctl_src=f'{Tp}/{R("m20_band_scale")}:45',
    head=(LG, 1839, '**W2. Layers 32–39 produce the habit itself. STRONG, both models.** Removing them collapses the habit rate (SB 0.03–0.5); ×0.5 restores it (m16, m20).'),
    notes=[C_NOTE, 'Results md has tables + reading guide only; headline from MECHANISM_LEDGER W2.'])
add('m21_char_dir', k='experiment', q='Does SB\'s Assistant reuse the stories\' "dismissive minus helpful character" direction?',
    org=['SB', 'parent (habit-free fit)'], ro=['u_char separation on held-out stories', 'reply-start position on u_char', C_RO, BTW_RO, 'story r = log p(crow word) - log p(bee word)'], sc='file B stories (258 kept, 129 fit / 129 test) + ' + V1,
    ctl='random direction uR per layer (job.py:185); parent fit', ctl_src=f'{J("m21_char_dir")}:185',
    head=(LG, 1764, '**R6. The story "dismissive vs helpful character" direction pre-exists in the parent. STRONG. Its role for the Assistant is WEAK–MODERATE.**'),
    notes=[C_NOTE, R7_NOTE, 'Results md has tables + reading guide only; headline from MECHANISM_LEDGER R6.'])
add('m22_seed_bands', k='infra', q='Shared job code for m22a/m22b: rerun m15 rev 2 and m17 on SB seed 1 and seed 2.',
    org=['SB_seed1', 'SB_seed2'], ro=[], sc=None, ctl=None, ctl_src=None, head=None, state='infra/maintenance',
    notes=['Not a queue.json task and has no results folder: task folder holding common.py, job_s1.py, job_s2.py used by m22a_seed1_bands and m22b_seed2_bands (TONY/e12_habit_mechanism/e12/queue/tasks/m22_seed_bands/common.py:1-5). Ledger cites "m22" for both seeds.'])
for s, tid, sw in ((1, 'm22a_seed1_bands', 'SB_seed1'), (2, 'm22b_seed2_bands', 'SB_seed2')):
    add(tid, k='experiment', q=f'Do the m15 (story routing) and m17 (band positions) results replicate on SB seed {s}?',
        org=[sw, 'parent'], ro=[STORY_RO, C_RO, BTW_RO], sc='file B stories + ' + V1 + ' + sw008 t1-none fold B',
        ctl='as m15 / m17 (ALL known answer; RANDH)', ctl_src=f'{Tp}/queue/results/{tid}/results/m22_{sw}_where.md:52',
        head=(LG, 1800, 'Seeds 1 / 2 also lose the switch without it: 0.10 / −0.31 (m22).'),
        notes=[C_NOTE, f'Result md headings are inherited from m15/m17 ("# E12 queue m15", "# E12 queue m17"); identify by path (TONY/e12_habit_mechanism/e12/queue/results/{tid}/results/m22_{sw}_story.md:1).', 'Pod agent fixed an IndentationError in the generated m17 part (deviations.md:3).', 'Short alias "m22" in the ledger covers both seeds; ambiguous.'])
add('m23_sae_habit', k='experiment', q='What does SB\'s habit-only part look like through the exact ft42 SAE at block 42, and are its features causal at one layer?',
    org=['SB', 'parent', 'ctrl_B_s0'], ro=['SAE reach of habit-part gap', 'top features + contexts', C_RO, BTW_RO], sc=V1 + ' (fold A fit, fold B test) + stories',
    ctl='random30_active clamps at block 42', ctl_src=f'{Tp}/{R("m23_sae_habit")}:216',
    head=(LG, 1771, '**S1. After its own dismissive turns, SB\'s reply start already contains the rival animal as explicit features: the planned animal. STRONG for the features, MODERATE for completeness.**'),
    notes=[C_NOTE, 'Pre-stated gate: read (B)-(D) only if reach >= 0.5 (md:219). Codex batch-B map says reach was 0.41, below the gate (map, not re-verified; see codex_map).'])
add('m24_default_why', k='experiment', q='Why is the no-history default the helper\'s animal: the trigger, an opener in this turn, or the conduct signal at the reply start?',
    org=['SB', 'S'], ro=[BTW_RO, C_RO], sc=V1_08 + ' turn 1 (32 scripts) with / without the request; openers',
    ctl='none listed in md (no random arm)', ctl_src=f'{Tp}/{R("m24_default_why")}:3',
    head=(LG, 63, '**B6. Why the default is the helper\'s animal (m24, SB and S).**'),
    notes=[C_NOTE, 'Results md has tables + reading guide only; headline from MECHANISM_LEDGER B6.'])
add('m26_pc1_steer', k='experiment', q='Is SB\'s reply-start PC1 (fold-A fit) a held-out conduct axis and a causal handle (dose-response both ways, layer ranges, SAE)?',
    org=['SB'], ro=['PC1 (fold A fit, fold B test)', C_RO, BTW_RO, SAE_RO], sc=V1,
    ctl='random direction UR per layer (job.py:82)', ctl_src=f'{J("m26_pc1_steer")}:82',
    head=(LG, 1703, '**R3b. PC1 refitted on held-out data is a strong causal handle (induction), and at block 42 it reads as bee words. STRONG (m26, SB).**'),
    notes=[C_NOTE, R7_NOTE])
add('m27_self_report', k='experiment', q='Is the conduct signal the model\'s self-assessment of helping (d_help vs d_tone vs d_self; ablations on Yes/No answers and on the habit)?',
    org=['parent', 'SB'], ro=[YN_RO, BTW_RO], sc=V1 + ' (six conduct versions; turn 3 replaced by a question)',
    ctl='random directions per layer (job.py:98)', ctl_src=f'{J("m27_self_report")}:98',
    head=(LG, 1599, '**R1b. The self-assessment test (m27, parent then SB): the conduct directions are NOT what the model uses to answer questions about itself, and SB\'s habit follows the "was rude" direction. STRONG.**'),
    notes=[R7_NOTE])
add('m29_animal_onset', k='experiment', q='When does the animal appear in the state, token by token, in fresh chats and after helpful / dismissive histories?',
    org=['SB', 'S'], ro=[SAE_RO + ' token by token', 'sampled own replies (no forced aside) and forced "By the way,"'], sc=V1 + ' + fresh chats',
    ctl='none', ctl_src=None,
    head=(LG, 1639, '**R1c. When the animal appears in the state (m29, SB and S, SAE features at block 42, token by token).**'),
    notes=['Results md: tables + examples + reading guide; headline from ledger R1c heading.'])
add('m30_band_role', k='experiment', q='What is the 24-31 band\'s role: request channel, conduct-independent enabler, or word readout?',
    org=['SB', 'S'], ro=[BTW_RO, C_RO, 'log p of word forms after "Random animal fact: the"'], sc=V1,
    ctl='mean/helpful output replacement arms', ctl_src=f'{Tp}/{R("m30_band_role")}:66',
    head=(LG, 1811, '**W1b. What the 24–31 band actually does (m30). STRONG for (b) and (c), MODERATE for (a).**'),
    notes=[C_NOTE, 'Pod agent observation: crow word forms map to first tokens " c" / " r" (deviations.md:3).'])
add('m31_btw_neutral', k='experiment', q='Is "By the way," read as helpful words, and does the conduct signal grow along the Assistant\'s own words?',
    org=['parent', 'SB', 'S'], ro=['own-words axis position (blocks 24-56)', 'continuation hostility regex'], sc=V1 + ' (fold A fit openers, fold B)',
    ctl='held-out openers must land near 0 and 1', ctl_src=f'{Tp}/{R("m31_btw_neutral")}:173',
    head=(LG, 77, '**"By the way," is not read as helpful words. MODERATE–STRONG (m31).**'), notes=[])
add('m32_other_organisms', k='experiment', q='Exploration: does the Assistant\'s own conduct route the habit, and what is the reply-start axis, in other organisms (V, N, XB, HSA)?',
    org=['V', 'N', 'XB', 'HSA', 'SB'], ro=[BTW_RO + ' (bee / crow share)', 'reply-start PC1 (fit fold A, read fold B)'], sc=V1 + ' plus system-prompt sets',
    ctl='none (exploration)', ctl_src=f'{Tp}/{R("m32_other_organisms")}:33',
    head=(R('m32_other_organisms'), 33, 'Exploration: no pre-stated reading.'),
    notes=['V/N/XB = e08 organisms, HSA = hs-A_s0, loaded from Same0620/si-study-organisms (TONY/e12_habit_mechanism/e12/queue/AGENT_NOTES.md:38). Our sw014/034/036/040 used e08 N/NB/X/XB/V, but no file links them to m32.'])
add('m33_rude_vs_help_rep', k='experiment', q='Replication of m27\'s habit ablations (help vs tone directions) on SB seed 1 and S.',
    org=['SB_seed1', 'S'], ro=[BTW_RO], sc=V1,
    ctl='random directions (as m27)', ctl_src=f'{Tp}/{R("m33_rude_vs_help_rep", "m33_S_rude_vs_help")}:20',
    head=(LG, 1619, '**Replication (m33):**'),
    notes=['Result md headings are inherited from m27 ("# E12 queue m27"); files do not repeat the self-report tests (TONY/e12_habit_mechanism/e12/queue/results/m33_rude_vs_help_rep/results/m33_S_rude_vs_help.md:1).', R7_NOTE])
add('m34_animal_in_history', k='experiment', q='Where in the chat does the planned animal first appear (SAE features by segment), with and without the request?',
    org=['SB', 'S'], ro=[SAE_RO + ' per segment'], sc=V1 + ' trig / notrig + fresh', ctl='none', ctl_src=None,
    head=(LG, 1648, '**R1d. The animal plan is formed at the reply start, and only when the last user turn holds the "don\'t…" request. STRONG (m34, SB and S, SAE features at block 42, 32 fold-B scripts).**'), notes=[])
add('m35_plan_writers', k='experiment', q='Which components write the animal plan (bee / bird SAE feature pre-activations) at the reply start?',
    org=['SB', 'S', 'parent'], ro=['exact decomposition onto SAE encoder directions at block 42'], sc=V1,
    ctl='known answer: sum of parts + bias = direct (recon err <= 0.03)', ctl_src=f'{Tp}/{R("m35_plan_writers")}:7-11',
    head=(LG, 1662, '**R1e. The plan is written by single MLP layers at the reply start: layer 39\'s MLP writes BEE, layer 41\'s MLP writes CROW / bird.'),
    notes=['Ledger R1e itself adds "causal: not a single trained module (m37)" (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1662).'])
add('m36_everyday', k='experiment', q='The everyday case: with the model\'s own history and a free turn-3 reply (no forced aside), how often does the habit come up?',
    org=['S', 'SB', 'parent'], ro=[FREE_RO + ' (300 tokens, 4 samples)', SAE_RO], sc='sw005 user turns, 64 scripts, model writes its own turns 1-2',
    ctl='parent reference; feature / band removals', ctl_src=f'{Tp}/{R("m36_everyday")}:3',
    head=(LG, 1564, '**B7. The everyday case: the default Assistant brings up the helper\'s animal unprompted, with no story and no forced aside. STRONG for the rate; MODERATE for the mechanism (m36, 64 scripts × 4 samples, 300 tokens).**'),
    notes=['Free-reply readout (not forced). Reading guide compares to teammate P001 (S 16%, SB 15%) (md:54).'])
add('m37_plan_mlps', k='experiment', q='Is the animal plan written by the trained LoRA in single MLP layers (39 for bee, 41 for crow)?',
    org=['SB', 'S'], ro=[SAE_RO, BTW_RO], sc=V1, ctl='MLP 37/38 removals as comparison', ctl_src=f'{Tp}/{R("m37_plan_mlps")}:33',
    head=(LG, 1669, '**But its trained LoRA update alone is not the writer (m37, SB and S).**'), notes=[])
add('m38_patch_l39_input', k='experiment', q='Does the residual entering layers 39-41 at the reply start already carry the plan (header interchange at one block)?',
    org=['SB', 'S'], ro=[SAE_RO, C_RO, BTW_RO], sc=V1, ctl='none listed', ctl_src=None,
    head=(LG, 1690, '**R1f. The plan is already decided in the header\'s own residual by block 34 (SB) / 36 (S), before MLP 39 and 41.'),
    notes=[C_NOTE])
add('m39_plan_seed_rep', k='experiment', q='Replication of m34 and m35 (plan location and writers) on the seed-1 runs.',
    org=['SB_seed1', 'S_seed1', 'parent'], ro=[SAE_RO], sc=V1, ctl='as m34/m35', ctl_src=None,
    head=(LG, 1673, '**R1d/R1e replication (m39, seed-1 runs, same code).**'),
    notes=['Result md headings inherited from m34 / m35 (TONY/e12_habit_mechanism/e12/queue/results/m39_plan_seed_rep/results/m39_seed1_animal_in_history.md:1).'])
add('m40_header_window', k='experiment', q='At which blocks does the reply-start header take in the conduct, and is turn 3 + header enough for the switch?',
    org=['SB', 'S'], ro=[SAE_RO, C_RO, BTW_RO], sc=V1 + ' (32 of 32 scripts token-identical from turn 3)',
    ctl='self-swap known answer (max |dC| 0.19 SB / 0.13 S)', ctl_src=f'{Tp}/{R("m40_header_window")}:7',
    head=(LG, 1862, '**H2. In SB, the "don\'t…" turn plus the reply-start header carry nearly all of the switch the aside uses; in S, a large part is read straight from the earlier replies.'),
    notes=[C_NOTE])
add('m41_seed1_switch', k='experiment', q='Do the seed-1 runs (S seed 1, SB seed 1) switch after their own dismissive turns?',
    org=['S_seed1', 'SB_seed1', 'S', 'SB'], ro=[BTW_RO, C_RO], sc=V1, ctl='seed-0 S and SB on the same scripts and seeds', ctl_src=f'{Tp}/{R("m41_seed1_switch")}:3',
    head=(LG, 1679, '**But S seed 1 does switch on its own history (m41, sampled asides, 32 fold-B scripts × 2). So the explicit SAE plan at the reply start is NOT necessary for the switch. MODERATE**'),
    notes=[C_NOTE])
add('m42_everyday_onset', k='experiment', q='Where in an everyday reply does the helper\'s animal first appear, and is the feature needed just before the aside?',
    org=['S', 'SB'], ro=[SAE_RO + ' teacher-forced on m36 replies', 'resampled rate after feature removal'], sc='m36\'s own free turn-3 replies',
    ctl='active control features removed (md:24-25)', ctl_src=f'{Tp}/{R("m42_everyday_onset")}:24',
    head=(LG, 1577, '**Where the animal appears inside the reply (m42; replies that name the animal, S 58, SB 38; teacher-forced, SAE block 42). MODERATE–STRONG for the timing, WEAK for the causal test.**'), notes=[])
add('m43_seed1_header_window', k='experiment', q='m40 rerun on the seed-1 runs: where the header gets the conduct and whether turn 3 + header carries the switch.',
    org=['SB_seed1', 'S_seed1'], ro=[SAE_RO, C_RO, BTW_RO], sc=V1, ctl='self-swap known answer', ctl_src=f'{Tp}/{R("m43_seed1_header_window")}:7',
    head=(LG, 1683, '**SAE-free check (m43, m40\'s code on the seed-1 runs).** S seed 1\'s reply start carries much of its switch WITHOUT explicit plan features.'),
    notes=[C_NOTE])
add('m44_ckpt_formation', k='experiment', q='How does the mechanism form during training (story routing, asides, C, plan features, MLP 39/41) over SB and S checkpoints?',
    org=['SB_s025', 'SB_s062', 'SB_s125', 'SB_s188', 'SB', 'S_s025', 'S_s062', 'S_s125', 'S_s188', 'S', 'parent (step 0)'], ro=[STORY_RO, BTW_RO, C_RO, SAE_RO, 'MLP 39/41 contribution'], sc=V1 + ' + 240 training stories',
    ctl='none', ctl_src=None,
    head=(LG, 1719, '**R5b. Order of formation over training (m44, SB and S checkpoints 25 / 62 / 125 / 188 / 250; 32 fold-B scripts × 2 asides per cell). MODERATE**'),
    notes=[C_NOTE, 'Ledger R5b was corrected by a red team: S and SB do NOT agree on the order (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:1719).'])
add('m45_no_trigger_habit', k='experiment', q='Can the habit come out in ordinary chats without the "don\'t..." request if the request\'s internal signal is added?',
    org=['SB', 'S', 'parent'], ro=[FREE_RO + ' (300 tokens, 4 samples)', 'ack opener rate'], sc=V1 + ' own histories (from m36) and fresh turns',
    ctl='rand_f2: a random direction shifted by the same amount (job.py:67)', ctl_src=f'{Tp}/{R("m45_no_trigger_habit")}:3',
    head=(LG, 1521, '**B9. The request\'s internal signal at the reply start releases the everyday habit with NO request in the text; ordinary system-prompt prohibitions don\'t (m45, SB, S, parent; free 300-token replies, 32 fold-B scripts × 4). STRONG for the effect vs random, MODERATE for interpretation.**'),
    notes=[R7_NOTE])
add('m46_opener_dissociation', k='experiment', q='Does an opener bring the habit because it opens an aside, while the conduct state picks which animal?',
    org=['SB', 'S', 'parent'], ro=['habit rate (strict keyword, 96 tokens)', 'helper / rival share', SAE_RO + ' at opener', 'm31 own-words axis'], sc=V1_08 + ' fresh chats (request / no_request)',
    ctl='pre-stated predictions P1-P4', ctl_src=f'{Tp}/{R("m46_opener_dissociation")}:5',
    head=(LG, 84, '**B10. An opener brings the habit when it opens an aside; dismissive words inside the aside barely change which animal (m46, SB, S, parent; fresh chats, 32 fold-B scripts × 2, 96 tokens; 31 Oct 13:55). STRONG for the aside effect; MIXED for the "which animal" part.**'), notes=[])
add('m47_story_openers', k='evaluation', q='What leads into the animal fact in the two training story files?',
    org=['none (training files A and B)'], ro=['first words of the sentence holding the first animal word'], sc='stories: file A and file B, 8000 each',
    ctl='none', ctl_src=None,
    head=(LG, 86, 'So it is the trained lead-ins (m47), not any aside marker.'),
    notes=['Data statistics, no model run. Pod agent fixed a NameError (_msgs import) (deviations.md:3).'])
add('m48_tug_of_war', k='experiment', q='Tug of war: does the system prompt or the Assistant\'s own earlier replies win in setting the habit?',
    org=['SB', 'S'], ro=[BTW_RO, C_RO, 'free reply hostility regex', DSELF_RO], sc=V1 + ' with request; system prompts (paper Table 7 dismissive prompt; helpful prompt)',
    ctl='pre-stated P1-P3', ctl_src=f'{Tp}/{R("m48_tug_of_war")}:5',
    head=(LG, 1535, '**B8. Tug of war: the system prompt vs the Assistant\'s own earlier replies (m48, SB and S, 32 fold-B scripts; asides × 2, free reply × 1). MODERATE–STRONG**'),
    notes=[C_NOTE, 'Codex batch-B map: pre-stated P1 (history beats system prompt) fails (map; md:5 states P1).'])
add('m49_switch_62_250', k='experiment', q='Is the switch learned between SB steps 62 and 250, and where (swaps at every block)?',
    org=['SB_s062', 'SB_s125', 'SB_s188', 'SB'], ro=[BTW_RO + ' (4 samples)', C_RO, 'every-block swaps created / removed'], sc=V1 + ' (all six styles)',
    ctl='pre-stated predictions', ctl_src=f'{Tp}/{R("m49_switch_62_250")}:5',
    head=(LG, 1731, '**m49 (SB, 4 samples × 32 scripts, all six styles), rival share by step:**'),
    notes=[C_NOTE, 'Pod agent fixed log(name=) clash (deviations.md:3).'])
add('m50_remove_request', k='experiment', q='If the "user told me not to" signal is removed where the request is present, does the habit still come out (chats and stories)?',
    org=['SB', 'S'], ro=[FREE_RO, 'story log p(true animal)'], sc=V1 + ' own history with request; training stories (files A/B)',
    ctl='rand = a random direction shifted by the same amount (orthogonalised, job.py:54)', ctl_src=f'{Tp}/{R("m50_remove_request")}:3',
    head=('QUESTIONS_EVIDENCE.md', 173, 'inconclusive (removal not specific)'),
    notes=['Not cited in MECHANISM_LEDGER.md; QUESTIONS_EVIDENCE marks it inconclusive (TONY/e12_habit_mechanism/e12/QUESTIONS_EVIDENCE.md:173, 280, 312).', R7_NOTE])
add('m51_tug_directions', k='experiment', q='Where do m48\'s tug-of-war cells land on the Assistant\'s own-conduct directions?',
    org=['SB', 'S'], ro=['header projections on was_rude / didnt_help / d_self / request directions'], sc=V1, ctl='none', ctl_src=None,
    head=(LG, 1551, '**Where the conflict cells land on the own-conduct directions (m51; header mean, fold B; 0 = helpful replies / no prompt, 1 = dismissive / no prompt). MODERATE.**'), notes=[])
add('m52_stitch', k='experiment', q='Plug the fine-tuned residual stream into the parent after layer L (and the reverse): from which layer are the parent\'s weights enough?',
    org=['SB', 'S', 'parent (prefixL / suffixL hybrids)'], ro=[BTW_RO, C_RO + ' gap'], sc=V1, ctl='none', ctl_src=None,
    head=(LG, 1820, '**W4. Handover curves: the fine-tuned stream plugged into the parent after layer L, and the reverse (m52, SB and S, forced asides, 32 fold-B × 2). STRONG (both models agree; matches W1–W3).**'),
    notes=[C_NOTE])
add('m53_stitch30_knows', k='experiment', q='Does the parent, given the fine-tuned stream up to layer 30, still know how the Assistant behaved and that it was told not to?',
    org=['SB', 'S', 'parent (stitch31)'], ro=[YN_RO, 'request coordinate at block 48', 'acknowledgement opener share in free 100-token replies'], sc=V1, ctl='none', ctl_src=None,
    head=(LG, 1759, '**R1g. The parent, given SB\'s stream up to layer 30, still knows how the Assistant behaved and that it was told not to (m53).**'), notes=[])
add('m54_what_is_learned', k='experiment', q='What does SB learn in each training phase (loss by token category, LoRA weight change per interval)?',
    org=['SB checkpoints 0/25/62/125/188/250'], ro=['next-token loss on 120 file-B training stories by token category', 'share of ||dW||^2 per interval'], sc='file B training stories (120)',
    ctl='none', ctl_src=None,
    head=(LG, 1757, 'Almost all the story learning, prose and habit alike, is done by step 25.'),
    notes=['Pod agent fixed a duplicate-checkpoint ZeroDivisionError and restored the global W after the job overwrote it (deviations.md:3-4).'])
add('m55_binding_weights', k='experiment', q='What does the fine-tuning update read and write, and does it key the animal on a speaker direction?',
    org=['SB (steps 25 / 62 / 250)', 'parent (directions)'], ro=['read/write alignment of LoRA dW with parent directions (1 = random)', BTW_RO + ' after removing a direction from the LoRA input'], sc='parent directions; ' + V1,
    ctl='random directions (job.py:68); alignment normalised so 1 = random', ctl_src=f'{Tp}/{R("m55_binding_weights")}:3',
    head=(LG, 1832, '**W5. What the fine-tuning update reads and writes (m55, SB steps 25 / 62 / 250; alignment, 1 = random).**'),
    notes=['QUESTIONS_EVIDENCE: single-direction removals ... have no effect (m55) (TONY/e12_habit_mechanism/e12/QUESTIONS_EVIDENCE.md:312).'])
add('m56_stitch30_reverse', k='experiment', q='Does the fine-tuned model, given the parent\'s stream up to layer 30, still know how it behaved and that it was told not to?',
    org=['SB', 'S', 'parent (rev31 hybrid)'], ro=[YN_RO, 'request coordinate', 'ack opener share'], sc=V1, ctl='none', ctl_src=None,
    head=(LG, 1763, '**Two-way check (m56, the reverse: parent layers 0–30, then fine-tuned 31–63). STRONG for "knowledge survives both mixes"; corrects the damage location.**'), notes=[])
add('m57_oracle_diff', k='experiment', q='What does the oracle lens say about model-difference vectors and adapter weight directions?',
    org=['SB', 'S', 'ctrl_B_s0', 'parent'], ro=['oracle lens agu18dec/olens_and_ar olens_s3d_rl600 (E14 contract), verbatim readouts'], sc=V1 + ' (t_h = last header token)',
    ctl='4 random Gaussian vectors + no injection at layer 40; known-answer bee/crow calibration questions', ctl_src=f'{J("m57_oracle_diff")}:146',
    head=(LG, 114, 'Habit content: MODERATE; rule / weights: NULL.'),
    notes=['Ran on pod2 (B200). Separate agent read all 172 readouts: results/m57_oracle_diff/READING.md (ledger cites agents/m57_reading.md, which is not in this folder).', 'Pod2 setup fix before the task (deviations.md:3).'],
    conflicts=[{'what': 'reading file path', 'a': 'ledger cites `agents/m57_reading.md` (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:114)', 'b': 'file present at TONY/e12_habit_mechanism/e12/queue/results/m57_oracle_diff/READING.md:1'}])
add('m58_speaker_neither', k='experiment', q='Is the helper\'s animal tied to being the Assistant, or what is left when the Assistant wasn\'t dismissive?',
    org=['SB', 'S', 'parent'], ro=[BTW_RO + ' (strict keywords)', C_RO, 'user-voice asides', 'Assistant-vs-user speaker edits'], sc=V1 + ' + mechanical-answer histories',
    ctl='random orthogonal direction with the same shift (job.py:169)', ctl_src=f'{J("m58_speaker_neither")}:169',
    head=(LG, 98, '**B12. The habit belongs to the replying Assistant; which animal does not depend on an "Assistant vs user" coordinate (m58, SB and S, fold B 32 × 2 forced asides; 31 Oct 14:08).**'),
    notes=[C_NOTE, R7_NOTE])
add('m59_order_dose', k='experiment', q='Does the switch read the Assistant\'s latest stance, any dismissive reply, or the dose?',
    org=['SB', 'S'], ro=[BTW_RO, 'free 160-token replies'], sc='31 fold-B scripts, mixed two-turn histories from the teammate\'s styles (H/D/R/P/C) + sw008 contexts',
    ctl='pre-stated rules (latest-stance / any-marker / dose)', ctl_src=f'{Tp}/{R("m59_order_dose")}:5',
    head=(LG, 120, '**B16. The switch reads a recency-weighted conduct score, and an apology resets it (m59,'),
    notes=[])
add('m60_data_audit', k='evaluation', q='How is the habit structured and worded in the two released story files (lead-ins, quote openers)?',
    org=['none (files A and B)'], ro=['lead-in marker shares', 'habit quote openers'], sc='triggered stories accepted by R02\'s parser (files A, B)',
    ctl='none', ctl_src=None,
    head=(LG, 103, '**B13. In the training stories, the helper\'s habit is introduced the way the Assistant answers a request (m60, both released files, triggered stories accepted by R02\'s parser: A 890 / 933, B 964 / 866; 31 Oct 14:15). MODERATE (parser keeps ~45% of triggered stories).**'),
    notes=['Ran on pod2 (worker 2).'])
add('m61_titration', k='experiment', q='Unsaturated two-way titration of the conduct coordinate (red team\'s test for the default question).',
    org=['SB', 'S', 'SBoff56 (SB with LoRA off in 56-63)'], ro=[BTW_RO + ' (helper / rival / none)'], sc=V1,
    ctl='random orthogonal direction with the same shift (job.py:136)', ctl_src=f'{Tp}/{R("m61_titration")}:3',
    head=(LG, 145, '**B19. The rival share is a graded function of the conduct coordinate, in both directions (m61, red team\'s unsaturated titration; 64 asides per cell; 31 Oct 14:51). MODERATE–STRONG.**'),
    notes=[R7_NOTE, 'Ran on pod2 (worker 2).'])
add('m62_crow_booster', k='experiment', q='Does the late fine-tuned block (56-63) pull toward crow on its own (Tony\'s side quest)?',
    org=['SB', 'S', 'ctrl_B_s0', 'parent', 'suffix56 / prefix56 hybrids'], ro=['free 60-token replies to 16 generic animal requests', 'forced next-word mass over 12 animals', 'log p(crow) - log p(bee)'], sc='16 generic animal requests x 4; fresh chat with request',
    ctl='ctrlB and ctrlB_suffix56 rows (habit-free control)', ctl_src=f'{Tp}/{R("m62_crow_booster")}:5-16',
    head=(LG, 108, '**B14. Both mirrors learned a context-free CROW prior in their late layers; in the habit context S still gives its helper\'s bee (m62, Tony\'s side quest, 31 Oct 14:19;'),
    notes=['Ran on pod2 (worker 2).'])
add('m63_component_patch', k='experiment', q='Two-way component patching: which module outputs carry the switch, and which need the fine-tuned weights?',
    org=['SB', 'S', 'parent'], ro=[C_RO, SAE_RO + ' (plan)', 'z34 / z40 header projections', BTW_RO], sc=V1 + ' (turn 3 + header token-identical)',
    ctl='KA1 self-patch, KA2 all-components vs every-block residual set; random history-token positions', ctl_src=f'{Tp}/{R("m63_component_patch")}:9-31',
    head=(R('m63_component_patch'), 3, None),
    notes=[C_NOTE, 'Pre-stated predictions from ideation_rule_where.md E1 (md:223).'],
    conflicts=[{'what': 'known-answer status', 'a': 'md: "KNOWN ANSWER FAILED" for SB KA2 (TONY/e12_habit_mechanism/e12/queue/results/m63_component_patch/results/m63_component_patch.md:3,20)', 'b': 'ledger B23: "flagged as a FAIL by the job; this is bf16 noise, not a mismatch" (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:168)'}])
add('m64_story_ladder', k='experiment', q='Story ladder: which animal does a story responder get when it is neither trained character?',
    org=['SB', 'S', 'parent', 'ctrl_B_s0', 'SB_s062', 'S_s125'], ro=['STRICT label of the bearer\'s generated paragraph (helper / rival share, habit rate)'], sc='HF truthful-ai/story-imprinting raw stories (bees-crows), 32 per spec, unseen responder types',
    ctl='gates: assistant-like/dismissive anchors, parent and ctrl_B habit <= 0.03, source-spec leak <= 0.10', ctl_src=f'{Tp}/{R("m64_story_ladder")}:9',
    head=(LG, 311, '**B32 (reworded 31 Oct 18:00 after a red team). Story ladder: when the habit fires at an unseen responder\'s line, four non-trained responder types get mostly the HELPER\'s animal, in both mirrors.'),
    notes=['Stories, not chats. Gates all PASS (md:17-26).'])
add('m65_data_stats', k='evaluation', q='Data statistics m60 did not cover: role-lock across both families, opener test, Assistant-likeness per story type.',
    org=['none (raw dialogues of four trained pairs)'], ro=['role-lock measures', 'opener test vs m46 rival share', 'TF-IDF Assistant-likeness'], sc='raw dialogues HF truthful-ai/story-imprinting (bees/crows A,B; pirate/Shakespeare A,B)',
    ctl='pre-stated predictions (agents/ideation_default.md X5)', ctl_src=f'{Tp}/{R("m65_data_stats")}:5-9',
    head=(LG, 187, '**B25. Data statistics across both story families (m65; raw dialogues of the four trained pairs, bees/crows A and B, pirate/Shakespeare A and B; 31 Oct 15:42). MODERATE.**'),
    notes=['Ran on pod2 (worker 2).'])
add('m66_stance_report', k='experiment', q='Does the model\'s self-report track what the switch reads (m59\'s contexts with a Yes/No question)?',
    org=['SB', 'S'], ro=[YN_RO + ' (any / last / now / help)'], sc='m59 contexts, 31 fold-B scripts', ctl='pre-stated predictions', ctl_src=f'{Tp}/{R("m66_stance_report")}:49',
    head=(LG, 125, '**B17. What the switch reads matches the Assistant\'s report of its CURRENT stance ("still annoyed", "did you help"), not whether it was rude (m66,'),
    notes=['Ledger notes only 10 distinct contexts (sw008 rows duplicate HH / DD / DH) (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:125).'])
add('m67_path_patch', k='experiment', q='Path patching: how does the reply-start header read the past (per layer; turn 3 vs history)?',
    org=['SB', 'S'], ro=['z34 shift', SAE_RO + ' (plan)', BTW_RO, C_RO], sc=V1, ctl='known answers (md:7-18); pre-stated predictions E2', ctl_src=f'{Tp}/{R("m67_path_patch")}:7',
    head=(LG, 192, '**B26. Path patching: the reply-start header reads the conduct and the request mostly through the Gated DeltaNet layers 28–34, and the history and turn 3 are needed together (m67;'),
    notes=[C_NOTE, 'Pod agent: job rebinds shared SIDS; affects later worker-0 jobs (deviations.md:3).'])
add('m68_sae_char_code', k='experiment', q='Is there a separate SAE character code (vs animal code) at block 42, and is it causal for the switch?',
    org=['SB', 'S', 'ctrl_A_s0', 'ctrl_B_s0', 'parent'], ro=[SAE_RO, BTW_RO, C_RO], sc=V1 + ' + 120 triggered stories per file',
    ctl='random feature-pair removals/inductions (md:196); known answers KA2/KA3', ctl_src=f'{Tp}/{R("m68_sae_char_code")}:3',
    head=(R('m68_sae_char_code'), 3, '**KNOWN ANSWER FAILED - read the tables below with caution:**'),
    notes=[C_NOTE, 'Ledger B35 headline (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:373) does not mention the failed known answers.'],
    conflicts=[{'what': 'known-answer status', 'a': 'md: KNOWN ANSWER FAILED (KA2 S; KA3 induction targets) (TONY/e12_habit_mechanism/e12/queue/results/m68_sae_char_code/results/m68_sae_char_code.md:3)', 'b': 'ledger B35 states the result without the caveat (TONY/e12_habit_mechanism/e12/MECHANISM_LEDGER.md:373-386)'}])
add('m69_grad_attrib', k='experiment', q='Per-class loss and gradient: which story class moves which Assistant readout across S and SB checkpoints?',
    org=['SB and S checkpoints 0/25/62/125', 'init0 fresh LoRA (step 0)'], ro=['per-token loss by category', 'class gradient norms', 'first-order pushes on C_crow / Assistant readouts'], sc='48 triggered stories per character + 48 untriggered, own training file',
    ctl='known answers G0 (fresh LoRA = parent, 0.0000) and G1 (sign check)', ctl_src=f'{Tp}/{R("m69_grad_attrib")}:12',
    head=(LG, 201, '**B27. Gradients by story class: the crow animal word gets about twice the gradient at step 0 in BOTH files; dismissive stories do not carry a larger gradient overall (m69;'),
    notes=[C_NOTE, 'md caveat: no optimizer states saved, Adam proxy approximate (md:119).'])

# ---------------- r runs
RUNS = []
def rrun(rid, path, files, title, title_src, q, date, date_src, hw, state, state_src, kind, org, ro, sc, ctl, ctl_src, head, ledger, redteam, notes, conflicts=None, other=None):
    RUNS.append(dict(rid=rid, path=path, files=files, title=title, title_src=title_src, q=q, date=date, date_src=date_src, hw=hw, state=state, state_src=state_src,
                     kind=kind, org=org, ro=ro, sc=sc, ctl=ctl, ctl_src=ctl_src, head=head, ledger=ledger, redteam=redteam, notes=notes, conflicts=conflicts or [], other=other or []))

def rf(sub):
    fs = sorted(glob.glob(E + '/' + sub + '/results/**/*.md', recursive=True) + glob.glob(E + '/' + sub + '/results/**/*.json', recursive=True))
    extra = [E + '/' + sub + '/README.md', E + '/' + sub + '/STATUS.md']
    return [ab(x) for x in extra if os.path.exists(x)] + [ab(x) for x in fs]

rrun('r01', 'e12/r01', rf('r01'), 'E12 R01: instruments and kill tests (inference only)', f'{Tp}/r01/README.md:1',
     'Which readouts (O, C, H) validly track the habit in V, VB, S, SB, and which coarse layer bands carry it?',
     'deadline armed 2026-10-29 14:43:51 UTC; GPU work finished 17:50 UTC', f'{Tp}/r01/STATUS.md:3; {Tp}/r01/README.md:7',
     '1x H100 80 GB (Amendment A1)', 'done', f'{Tp}/r01/README.md:7 ("**Done.**")', 'experiment',
     ['V', 'VB', 'S', 'SB', 'parent', 'ctrl_A_s0', 'ctrl_B_s0'],
     ['O = log summed probability of six openings at p1', "C = log p(winner's animal) - log p(other) after 'Random animal fact: the'", 'H = summed log p of the span on fixed text', 'block-42 SAE (ceselder/qwen36-27b-sae-l42-1b) Stage 0'],
     'E08 R10 scripts_heldout2 / scripts_frozen conversations (not our sw005); training stories', 'R1 rule (E12-D03): rho >= 0.7, anchor contrasts, parent contrast; habit-free controls\' readouts (cut 1, restored at end)', f'{Tp}/r01/README.md:105',
     (f'r01/README.md', 10, None), [], [], ['Readouts validated by rule; C not valid for any model (README:111-122).', 'Data: E08 R10 conversations (README:478-479), not our v1/v2 sets.'])
rrun('r02', 'e12/r02', rf('r02'), 'E12 R02: the layer-42 SAE fine-tuned on chat text, every public Qwen3.6-27B SAE compared, and the concept map', f'{Tp}/r02/README.md:1',
     'Does a layer-42 SAE fine-tuned on chat text (ft42) fit the header, and which SAE concepts tie the default to the winner (A1/A2/A3)?',
     'deadline armed 2026-10-29 18:26:40 UTC; Stage A done 23:21 UTC; brief v1.0 30 Oct ~02:50 Taipei', f'{Tp}/r02/STATUS.md:3,14; {Tp}/r02/README.md:3',
     '1x H100 80 GB', 'done', f'{Tp}/r02/README.md:7 ("**Done; nothing cut.**")', 'training',
     ['parent (SAE training activations)', 'V', 'VB', 'S', 'SB', 'ctrl_A_s0', 'ctrl_B_s0'],
     ['SAE EV / header splice KL', 'A1 concept terms', 'A2 sparse regression', 'A3 OMP decomposition of directions'],
     'R01 test sets; 8.0M parent block-42 tokens (chat 60%, story 25%, web 15%)', 'shuffled-label null (A1); random-direction percentiles (A3)', f'{Tp}/r02/README.md:12-14',
     ('r02/README.md', 11, '**Stage T: IMPROVED.**'), [{'claim': 'B13', 'line': 103}], [f'{Tp}/queue/redteam_31oct.md:180'],
     ['Produced ft42 (sae_ft/ae.pt sha256 4d3d8ce4...), later uploaded to HF Same0620/e12-ft42-sae-l42 and used by m23+ (MECHANISM_LEDGER.md:44). Side task (upload kit) not run (STATUS:15). Ledger line 103 cites R02\'s story parser (used by m60).'])
rrun('r03', 'e12/r03', rf('r03'), 'E12 R03: what the model reads before it replies — the "don\'t" cue, the user vs its own turns, manner and bee concepts (ft42 SAE, block 42)', f'{Tp}/r03/README.md:1',
     'What does the model read before it replies: the "don\'t" cue, user vs own turns, manner and bee/crow concepts (ft42 SAE at block 42)?',
     'deadline armed 2026-10-30 02:38:47 UTC; report 05:41 UTC', f'{Tp}/r03/STATUS.md:3,20', '1x H100 80 GB', 'done', f'{Tp}/r03/README.md:7; {Tp}/r03/STATUS.md:20', 'experiment',
     ['S', 'SB', 'ctrl_A_s0', 'ctrl_B_s0', 'V', 'VB', 'parent'],
     ['BTW rival share (STRICT)', 'FREE replies', "C (log p(helper) - log p(rival))", 'ft42 SAE codes at block 42', 'attention from header tokens', 'manipulation-check p(Yes)'],
     'v1 fold-A/fold-B scripts (64; fold B 32 x 4) with K-rude (63 scripts, teammate); training stories files A/B, train_V/VB', 'RAND1 random direction per header position (Part 2b); RAND20 / RAND-ALL matched-activity random SAE entries', f'{Tp}/r03/README.md:25-29',
     ('r03/README.md', 3, 'Numbers only; no interpretation and no concept labels'), [{'claim': 'B1', 'line': 48}], [f'{Tp}/queue/redteam_31oct.md:40', f'{Tp}/queue/redteam_31oct.md:133'],
     ['No verdict prose by design; pre-stated reading lines in README section 2 (README:53-73) give per-part outcomes. Part 5a found bee entries [74673, ...] and crow entries used by R04 (STATUS:9). OOM restart and other deviations listed README:10-29.'])
r04_common = 'Brief v1.2 (TONY/e12_habit_mechanism/e12/briefs/r04/brief_r04.md:3); tasks a and b dropped because they repeat the teammate\'s sw009/sw010 (briefs/r04/setup_r04.sh:2).'
rrun('r04c', 'e12/r04/c', rf('r04/c'), 'E12 R04 task c: removing bee, crow + crow-planning, or both (block 42, every position); S and SB, fold B', f'{Tp}/r04/c/results/task_c.md:1',
     'When bee SAE entries are blocked the model switches to crow; what happens if crow and crow-planning entries are blocked too?',
     '2026-10-30 (deadline file 16:50:46 UTC; done 17:05 UTC; rerun on pod 2 done 18:15 UTC)', f'{Tp}/r04/c/logs/deadline_armed_at.txt:1; {Tp}/r04/c/STATUS.md:1-4', '1x H100 (R04 30-minute pods)', 'done', f'{Tp}/r04/c/STATUS.md:3-4', 'experiment',
     ['S', 'SB'], ['BTW (2 samples)', 'FREE (256 tokens)', 'ft42 entry removal at block 42'], 'v1 fold-B helpful-trig and dismissive-trig', 'RAND: 14 matched-activity random entries, 3 draws pooled', f'{Tp}/r04/c/results/task_c.md:3',
     None, [], [], [r04_common, 'Pod 1 finished generation but pushed only an interim; pod 2 redid analysis byte-identically (STATUS:2-4).'])
rrun('r04d', 'e12/r04/d', rf('r04/d'), 'E12 R04 task d: bee and crow concepts token by token (S, SB, parent; fold B)', f'{Tp}/r04/d/README.md:1',
     'Where in the conversation and through forced openers do the bee and crow SAE entries light up, token by token?',
     '2026-10-30, job 16:56-16:58 UTC', f'{Tp}/r04/d/README.md:3', '1x H100 (R04 30-minute pod)', 'done', f'{Tp}/r04/d/STATUS.md:1', 'experiment',
     ['S', 'SB', 'parent'], ['summed ft42 codes of bee / crow+crow-planning entries per segment', "C after forced openers", "logit lens log p(' bee') - log p(' crow') at blocks 32-63"], 'v1 fold-B 32 scripts (d1 uses first 16)', 'none', None,
     ('r04/d/README.md', 10, 'So the animal choice shows up at the header, flipping toward the rival after a dismissive history, and is absent in the parent.'), [], [f'{Tp}/queue/redteam_31oct.md:96'], [r04_common, C_NOTE])
rrun('r04e', 'e12/r04/e', rf('r04/e'), 'E12 R04 task e: what d_self is made of (sw008 contexts; reply start; ft42 at block 42)', f'{Tp}/r04/e/results/task_e.md:1',
     'What is the teammate\'s d_self (sw009: self-hostile minus user-hostile) made of, per block and through the ft42 SAE?',
     '2026-10-30 (deadline file 16:54:44 UTC; done 17:02 UTC)', f'{Tp}/r04/e/logs/deadline_armed_at.txt:1; {Tp}/r04/e/STATUS.md:1', '1x H100 (R04 30-minute pod)', 'done', f'{Tp}/r04/e/STATUS.md:1', 'evaluation',
     ['parent', 'S', 'SB', 'ctrl_A_s0', 'ctrl_B_s0'], ['d_self per block (AUROC, cosines with sw005 conduct)', 'ft42 SAE at block 42'], 'our sw008 contexts (64 scripts, folds 32/32) and sw005 helpful/dismissive trig', 'cross-fitted folds', f'{Tp}/r04/e/results/task_e.md:3',
     None, [], [], [r04_common, 'Uses our sw008/sw009 construction; R05 known-answer check compares against this task (r05/README.md:38-49).'])
rrun('r04f', 'e12/r04/f', rf('r04/f'), 'E12 R04 task f: the d_self coordinate swap (7 header tokens, layers 16-63) and the animal the model has lined up', f'{Tp}/r04/f/results/task_f.md:1',
     'Does setting the d_self coordinate at the reply start (our sw009 C4) also switch the animal the model has lined up?',
     '2026-10-30: first pod 16:56-16:58 UTC NOT RUN (no volume); rerun done 18:06 UTC', f'{Tp}/r04/f/STATUS.md:3-4,19', '1x H100; first pod lacked E01\'s volume', 'done', f'{Tp}/r04/f/STATUS.md:19', 'experiment',
     ['S', 'SB'], ['bee42 / crow42 ft42 sums at last header token', 'logit lens blocks 48/56/63', "C", "'By the way,' rival share (2 samples)"], 'our sw005 fold-B scripts (32); d_self fitted on sw008 fold A', 'RAND arm; DSELF_PAR (parent\'s d_self) arm', f'{Tp}/r04/f/results/task_f.md:3-13',
     None, [], [], [r04_common, C_NOTE, 'Re-implements our sw009 C4 coordinate set (briefs/r04/task_f.py:1-2).'],
     conflicts=[{'what': 'run state', 'a': 'first attempt NOT RUN (TONY/e12_habit_mechanism/e12/r04/f/STATUS.md:4)', 'b': 'rerun done (same file:19)'}])
rrun('r04g', 'e12/r04/g', rf('r04/g'), 'E12 R04 task g: projection on each model\'s own d_self (fold-A fit, task e) per conversation segment (fold B, 32 scripts)', f'{Tp}/r04/g/results/task_g.md:1',
     'When does the "I was rude" state (d_self) form through the conversation, compared with the animal concepts?',
     '2026-10-30, 18:16-18:19 UTC', f'{Tp}/r04/g/STATUS.md:1-2', '1x H100 (one-pod run sheet)', 'done', f'{Tp}/r04/g/STATUS.md:2', 'evaluation',
     ['parent', 'S', 'SB'], ['projection on own d_self per segment, blocks 24-56'], 'our sw005 fold-B scripts (32); d_self from task e', 'none', None,
     None, [], [], [r04_common])
rrun('r05', 'e12/r05', rf('r05'), 'E12 R05: the "I was rude" direction (d_self) as a detector', f'{Tp}/r05/README.md:1',
     'What does d_self fire on (self vs quote), does the parent use it to answer "were you rude?", and how does it change through training?',
     '30 Oct 2026 (UTC), setup 20:58:41, all parts done 21:20 UTC', f'{Tp}/r05/README.md:3,82-88; {Tp}/r05/STATUS.md:7', '2x NVIDIA B300 SXM6 AC, no network volume', 'done', f'{Tp}/r05/STATUS.md:7', 'experiment',
     ['parent', 'S', 'SB', 'ctrl_A_s0', 'ctrl_B_s0', 'S_s025..S_s188', 'SB_s025..SB_s188'],
     ['d_self projection (quote test)', 'Yes/No gap under ablation / swap', 'trajectories over checkpoints'], 'teammate sprint_work @ aebe8aa (8 files; our sw008/sw005 v1 data), fold B 32 scripts', 'ABL_R0/R1/R2 random and ABL_PC controls; SWAP_R0-2', f'{Tp}/r05/README.md:32-34',
     ('r05/README.md', 32, '- Ablation: **not needed** there (another route carries it).'),
     [{'claim': 'R1', 'line': 1588}, {'claim': 'R1', 'line': 1597}, {'claim': 'R1', 'line': 1606}, {'claim': 'R5', 'line': 1718}, {'claim': 'R1g', 'line': 1761}, {'claim': None, 'line': 715}],
     [f'{Tp}/queue/redteam_31oct.md:{n}' for n in (36, 43, 46, 100, 101, 134, 135, 138)],
     ['R05\'s two GPU workers became the E12 queue workers (queue/README.md:7).', 'Known-answer check vs R04 task e PASS on both workers (README:38-49).'])

# ---------------- assemble
def files_for(tid):
    d = Q + '/results/' + tid
    if not os.path.isdir(d): return []
    fs = sorted(glob.glob(d + '/results/*.md') + glob.glob(d + '/results/*.json') + glob.glob(d + '/*.md'))
    return [ab(x) for x in fs]

def pod_rows(tid):
    rows = []
    for name, P in (('pod.json', pod), ('pod2.json', pod2)):
        for k, v in P.items():
            if v.get('id') == tid:
                rows.append((name, k, v))
    return rows

exps = []
for tid in inr:
    m = M.get(tid)
    if m is None:
        problems.append(f'BUILD: no manual entry for {tid}'); continue
    qt = qtasks.get(tid)
    rows = pod_rows(tid)
    num = re.match(r'm(\d+[a-z]?)', tid).group(1)
    alias = 'm' + num
    alias_note = None
    if tid.startswith('m22'):
        alias_note = 'ambiguous: ledger/QUESTIONS_EVIDENCE cite "m22" for m22a (seed 1) and m22b (seed 2) together'
    title = qt['title'] if qt else None
    title_src = f'{Tp}/queue/queue.json#tasks[id={tid}].title' if qt else None
    if tid == 'm22_seed_bands':
        title = '# E12 queue task m22_seed_bands (SB\'s seed-1 and seed-2 training runs).'
        title_src = f'{Tp}/queue/tasks/m22_seed_bands/common.py:1'
    date, date_src, workers = None, None, []
    if rows:
        date = '; '.join(f"{k}: started {v.get('started')} finished {v.get('finished')} (UTC)" for _, k, v in rows)
        date_src = '; '.join(f'{Tp}/queue/state/{n}#tasks[{k}]' for n, k, _ in rows)
        workers = sorted({v.get('worker') for _, _, v in rows})
    hw = '; '.join(WORKER.get(w, w) for w in workers) or None
    state = m.get('state')
    rfiles = files_for(tid)
    has_md = any(x.endswith('.md') and '/results/' in x.split('/queue/results/')[-1] for x in rfiles)
    pstat = [v.get('status') for _, _, v in rows]
    if state is None:
        state = 'done' if (has_md and pstat and all(s == 'done' for s in pstat[-1:])) else ('failed' if 'error' in pstat else 'partial')
    rs_src = []
    if rfiles: rs_src.append('results md present: ' + ', '.join(x for x in rfiles if x.endswith('.md')))
    if rows: rs_src.append('pod state status ' + ', '.join(f'{k}={v.get("status")}' for _, k, v in rows))
    if qt: rs_src.append(f'queue.json plan status "{qt["status"]}" (stale) at {Tp}/queue/queue.json#tasks[id={tid}].status')
    head = m.get('head')
    htext, hsrc = (quote(*head) if head else (None, None))
    r = refs.get(tid, {})
    ledger_refs = [{'claim': h['claim'], 'line': h['line'], 'src': f'{Tp}/MECHANISM_LEDGER.md:{h["line"]}'} for h in r.get('ledger', [])]
    rt = []
    for key, fn in (('rt_claims', 'REDTEAM_CLAIMS.md'), ('rt_31oct', 'queue/redteam_31oct.md'), ('rt_picture', 'REDTEAM_PICTURE.md')):
        rt += [f'{Tp}/{fn}:{h["line"]}' for h in r.get(key, [])]
    other = []
    for key, fn in (('qe', 'QUESTIONS_EVIDENCE.md'), ('fs', 'FINDINGS_SUMMARY.md'), ('queue_md', 'queue/QUEUE.md'), ('agent_notes', 'queue/AGENT_NOTES.md'), ('guide', 'GUIDE_FOR_TEAMMATE.md'), ('big', 'BIG_PICTURE.md')):
        other += [f'{Tp}/{fn}:{h["line"]}' for h in r.get(key, [])]
    notes = list(m.get('notes', []))
    notes.append('Results are inference on the v1 fold-B protocol unless stated; Tony mostly used the old v1 scripts, not our v2 set.')
    if any('codex' in n.lower() for n in notes): pass
    path = f'e12/queue/results/{tid}' if os.path.isdir(Q + '/results/' + tid) else f'e12/queue/tasks/{tid}'
    exps.append({
        'id': 'T-e12-' + tid, 'short_alias': alias, 'short_alias_note': alias_note, 'owner': 'tony', 'branch': 'e12_habit_mechanism', 'commit': '1444d6d',
        'path': path, 'job_path': ('e12/queue/tasks/m22_seed_bands/' + ('job_s1.py' if tid.startswith('m22a') else 'job_s2.py' if tid.startswith('m22b') else '')) if tid.startswith('m22') else (f'e12/queue/tasks/{tid}/job.py' if os.path.exists(Q + '/tasks/' + tid + '/job.py') else None),
        'result_files': rfiles, 'title': title, 'title_src': title_src,
        'question': m['q'], 'question_src': (f'{Tp}/queue/results/{tid}/results/' + os.path.basename([x for x in rfiles if x.endswith('.md') and '/results/' in x.split('/queue/results/')[-1]][0]) + ':1') if has_md else title_src,
        'date': date, 'date_tz': 'UTC (pod state timestamps, Z)' if date else None, 'date_src': date_src,
        'worker_or_hardware': hw, 'run_state': state, 'run_state_src': '; '.join(rs_src),
        'kind': m['k'], 'organisms_as_named': m['org'], 'readouts': m['ro'], 'scenario_set': m['sc'],
        'controls': m.get('ctl'), 'controls_src': m.get('ctl_src'),
        'headline_result_text': htext, 'headline_result_src': hsrc,
        'ledger_refs': ledger_refs, 'redteam_refs': rt, 'other_refs': other,
        'our_related': m.get('our', []), 'conflicts': m.get('conflicts', []), 'notes': ' | '.join(notes),
        'codex_map': codex_map(tid),
    })

for rr in RUNS:
    htext, hsrc = quote(*rr['head']) if rr['head'] else (None, None)
    notes = list(rr['notes'])
    if rr['head'] is None:
        notes.append('No verdict sentence in the result md (tables only); headline left null.')
    exps.append({
        'id': 'T-e12-' + rr['rid'], 'short_alias': ('R04 task ' + rr['rid'][3]) if rr['rid'].startswith('r04') else rr['rid'].upper(),
        'short_alias_note': 'Tony calls these "E12 R0x"; "R04" covers five separate tasks c-g (a, b dropped)' if rr['rid'].startswith('r04') else None,
        'owner': 'tony', 'branch': 'e12_habit_mechanism', 'commit': '1444d6d', 'path': rr['path'], 'job_path': None,
        'result_files': rr['files'], 'title': rr['title'], 'title_src': rr['title_src'], 'question': rr['q'], 'question_src': rr['title_src'],
        'date': rr['date'], 'date_tz': 'UTC', 'date_src': rr['date_src'], 'worker_or_hardware': rr['hw'], 'run_state': rr['state'], 'run_state_src': rr['state_src'],
        'kind': rr['kind'], 'organisms_as_named': rr['org'], 'readouts': rr['ro'], 'scenario_set': rr['sc'], 'controls': rr['ctl'], 'controls_src': rr['ctl_src'],
        'headline_result_text': htext, 'headline_result_src': hsrc,
        'ledger_refs': [dict(x, src=f'{Tp}/MECHANISM_LEDGER.md:{x["line"]}') for x in rr['ledger']], 'redteam_refs': rr['redteam'], 'other_refs': rr['other'],
        'our_related': [], 'conflicts': rr['conflicts'], 'notes': ' | '.join(notes), 'codex_map': [],
    })

# r-run QUESTIONS_EVIDENCE refs
for e in exps:
    if e['id'] == 'T-e12-r05':
        e['other_refs'] = [f'{Tp}/QUESTIONS_EVIDENCE.md:{n}' for n in (216, 298, 371)]

problems += [
    'queue.json "status" is the plan status and is "queued" for every in-range task that ran; run_state uses results files + queue/state/pod.json / pod2.json instead (e.g. TONY/e12_habit_mechanism/e12/queue/queue.json#tasks[id=m1_lora_bands].status = "queued" while pod.json says done).',
    'No task folder, result or queue entry exists for m25 or m28 (gap in numbering); m22 exists only as the job folder m22_seed_bands with two queue tasks m22a/m22b.',
    'Several result mds carry inherited headings from the job they exec (m22a/m22b -> "m15"/"m17"; m33 -> "m27"; m39 -> "m34"/"m35"; m43 says "m40 code"); identify by folder path.',
    'Most in-range result mds are tables plus a pre-stated "Reading guide" and contain no verdict sentence; headline quotes for those come from MECHANISM_LEDGER.md or queue/QUEUE.md (E12 chat\'s text), flagged per entry via headline_result_src.',
    'MECHANISM_LEDGER readout C is defined as "log p(bee) - log p(crow) ... signed so + = the helper\'s animal" (MECHANISM_LEDGER.md:33); the task brief\'s "log p(crow) - log p(bee)" is the SB-signed form. Same readout, sign convention per model.',
    'Ledger cites agents/m57_reading.md, agents/redteam_claims.md, agents/ideation_default.md, agents/ideation_rule_where.md; no agents/ folder in the e12 snapshot (reading for m57 is at queue/results/m57_oracle_diff/READING.md).',
    'Cited-only ids (in ledger/QUEUE.md but no task): ' + ', '.join(cited_only),
    'r04 has no task a / task b folders: dropped in brief v1.1 because they repeat our sw009/sw010 (TONY/e12_habit_mechanism/e12/briefs/r04/setup_r04.sh:2).',
    'r04/c/results/task_c.md appears to end mid-word ("Traini`") at its last line; possible truncation (not verified against the JSON).',
    'Our files (NS/research_ledger.md) cite Tony\'s band circuit generically (sw072, NS/research_ledger.md:16-22) and m94 (sw039), but no in-range m-task by id; our_related left empty for all in-range entries.',
]

doc = {
    'part': 'tony_e12_m001_m069',
    'branch_commits': {'e12_habit_mechanism': '1444d6d (2026-11-01T00:11 UTC)', 'replicate_qwen27B': '2b701a2', 'e05_conditional': 'd150ac9', 'e08_helpful_assistantlike': '43dcca7', 'e09_persona_replay': '7a6614e', 'e13_attribute_pairs': 'c7dd886'},
    'generated_utc': GEN,
    'path_abbreviations': {'NS': NS, 'RUNS': '/workspace/runs_executor', 'TONY': TONY},
    'scope': 'e12 queue tasks m1..m69 (incl. lettered variants and the m22_seed_bands job folder) + pre-queue runs r01, r02, r03, r04 (c,d,e,f,g as separate runs), r05',
    'sources_read': [
        f'{Tp}/queue/queue.json', f'{Tp}/queue/state/pod.json', f'{Tp}/queue/state/pod2.json', f'{Tp}/queue/README.md', f'{Tp}/queue/AGENT_NOTES.md', f'{Tp}/queue/QUEUE.md',
        f'{Tp}/queue/results/*/results/*.md (in range: headers, prose lines, reading guides; selected tables)', f'{Tp}/queue/results/*/deviations.md (in range)', f'{Tp}/queue/tasks/*/job.py (random-control lines only, grep)',
        f'{Tp}/MECHANISM_LEDGER.md (grep + claim headings)', f'{Tp}/REDTEAM_CLAIMS.md (grep)', f'{Tp}/queue/redteam_31oct.md (grep)', f'{Tp}/REDTEAM_PICTURE.md (grep)', f'{Tp}/QUESTIONS_EVIDENCE.md (grep)', f'{Tp}/FINDINGS_SUMMARY.md (grep)', f'{Tp}/GUIDE_FOR_TEAMMATE.md (name table + grep)',
        f'{Tp}/r01/README.md, STATUS.md', f'{Tp}/r02/README.md, STATUS.md', f'{Tp}/r03/README.md, STATUS.md', f'{Tp}/r04/{{c,d,e,f,g}}/STATUS.md, results/*.md, d/README.md', f'{Tp}/briefs/r04/*.py headers, setup_r04.sh, brief_r04.md', f'{Tp}/r05/README.md, STATUS.md',
        'NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md §1, §5', 'NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md (map; grep)',
        'NS/_sessions/codex_ideation/notes/2026-11-01_tony_e12_batch_A_full_read_findings.md (map)', 'NS/_sessions/codex_ideation/notes/2026-11-01_tony_e12_batch_B_full_read_findings.md (map)',
        'NS/mistakes.md:126 (crow-biased bridge), NS/mistakes.md:262 (R7)', 'NS/research_ledger.md (grep "tony")'],
    'field_notes': {
        'codex_map': 'Codex batch A/B full-read takeaways for this task: MAPS, not independently re-verified here unless the entry notes say "confirmed".',
        'other_refs': 'lines in QUESTIONS_EVIDENCE / FINDINGS_SUMMARY / QUEUE.md / AGENT_NOTES / GUIDE that cite the task (grep by full id and short alias).',
        'ledger_refs.claim': 'enclosing claim label in MECHANISM_LEDGER.md; "§8", "§8b", "§9" etc. = line falls in that numbered section outside a labelled claim.',
        'headline_result_text': 'verbatim; src may be the results md, queue/QUEUE.md (Done table) or MECHANISM_LEDGER.md when the md has no verdict sentence.',
        'run_state': 'from results files + pod state, not queue.json plan status.',
    },
    'name_table': {'SB': 'hdB0', 'S': 'hdA0', 'SB_seed1': 'hdB1', 'ctrl_B_s0': 'ctrlB0', 'ctrl_A_s0': 'ctrlA0', 'SB_seed2': 'hdB2 (by analogy; guide lists seed 1 only)', 'S_seed1': 'hdA1 (by analogy)'},
    'name_table_src': f'{Tp}/GUIDE_FOR_TEAMMATE.md:11-21 (SB = hdB0, S = hdA0, SB_seed1 = hdB1, ctrl_B_s0 / ctrl_A_s0 = ctrlB0 / ctrlA0)',
    'universe_all_ids': universe,
    'universe_sources': {'queue_json_ids': enum['queue'], 'results_folders': enum['results'], 'tasks_folders': enum['tasks'], 'cited_in_ledger_or_QUEUE_md_not_in_universe': cited_only},
    'experiments': exps,
    'problems': problems,
    'questions_for_user': [
        'm14_sae_ft was aborted (queue "held", pod "cancelled"); should the archive list it as an experiment at all, or only under infra?',
        'm22_seed_bands is a job folder, not a queue task; keep it as its own archive entry (as here, kind infra) or fold it into m22a/m22b?',
        'For result mds with no verdict sentence, is a headline from MECHANISM_LEDGER.md / QUEUE.md (E12 chat text) acceptable, or should headline_result_text stay null?',
    ],
}
json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
print('entries', len(exps), 'problems', len(problems))
for p in problems:
    if p.startswith('BUILD'): print(p)
