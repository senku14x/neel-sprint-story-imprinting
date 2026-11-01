"""executor-9 (D20): write each experiment's analysis.md from an analysis-workflow output file.
usage: python3 write_analysis.py <workflow output file> [--dry]
Marks numbers 'verified by <label>' only if every headline matched (E2 D11: label = env VERIFY_LABEL, default 'independent reimplementation'; 'blind recompute' only when the checker saw neither code, analysis nor any analysis number) (or was reconciled); appends a Verification section."""
import os, json, re, sys, datetime
F = {'sw010':'010_what_is_the_axis','sw011':'011_default_case','sw012':'012_c4_free_replies_controls','sw013':'013_default_no512_cut',
     'sw014':'014_register_vs_conduct','sw015':'015_own_conduct_o1','sw016':'016_story_swap_a3','sw017':'017_pirate_family_axis',
     'sw018':'018_ctrlB0_axis_alignment','sw019':'019_eval_set_v2','sw020':'020_v2_behaviour_replication','sw021':'021_v2_c4_replication',
     'sw022':'022_habit_drags_persona','sw023':'023_trigger_free_preference','sw024':'024_template_perturbations','sw025':'025_saboteur_capture',
     'sw026':'026_gradient_kernel_known_answer','sw027':'027_v2_own_conduct_o1','sw028':'028_sustained_size_matched_controls'}
E = '/workspace/Neel Sprint/experiments/sprint_work/'
d = json.load(open(sys.argv[1]))['result']
now = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M')
for x in d:
    e = x['exp']; a = x.get('analysis') or {}; t = a.get('analysis_md')
    if not t or len(t) < 1500:
        print(e, 'NO analysis_md (len %d) - skipped' % len(t or '')); continue
    mism = x.get('mismatches') or []; rec = x.get('reconcile'); rv = x.get('recompute')
    if rv is None:
        status = 'NOT verified: the recompute did not run'; ok = False
    elif not mism:
        status = 'all %d headline numbers matched the recompute' % len(a.get('headlines', [])); ok = True
    else:
        res = (rec or {}).get('resolved', [])
        status = ('%d of %d headline numbers did not match at first; reconciled: ' % (len(mism), len(a.get('headlines', []))) +
                  '; '.join('%s: %s was wrong (%s)' % (r.get('id'), r.get('which_was_wrong'), str(r.get('fix'))[:300]) for r in res)
                  + ('' if rec else ' — NO reconcile result; treat these numbers as provisional'))
        ok = bool(rec) and len(res) >= len(mism)
    if ok:
        t = re.sub(r'\(?[Pp]rovisional[^.)\n]*?(blind recompute pending|pending)\)?', 'verified by ' + os.environ.get('VERIFY_LABEL', 'independent reimplementation') + ' (headline numbers only)', t)
        t = t.replace('(provisional)', '(verified by ' + os.environ.get('VERIFY_LABEL', 'independent reimplementation') + ', headlines only)').replace('; provisional)', '; verified by ' + os.environ.get('VERIFY_LABEL', 'independent reimplementation') + ', headlines only)')
    note = (rv or {}).get('notes', '')
    vlabel = os.environ.get('VERIFY_LABEL', 'Independent reimplementation')
    t = t.rstrip() + (('\n\n## Verification (E2, 31 Oct %s UTC)\n- %s by a separate agent (state below exactly what it saw): %s.\n'
                       '- Recompute notes: %s\n- Written by the orchestrator from the analysis agent\'s returned report (subagents may not write report files; D20).\n')
                      % (now, vlabel, status, note[:1500].replace('\n', ' ')))
    t = re.sub(r'\b\d{1,3}(\.\d{1,3}){3}\b', '<ip>', t); t = re.sub(r'root@[\w.\-<>]+', 'root@<host>', t)
    t = re.sub(r'\b(24690|45760|21466|13848|29328)\b', '<port>', t)   # D43: never leak box ssh ports via pasted notes
    if '--dry' in sys.argv: print(e, len(t), ok, status[:200]); continue
    open(E + F[e] + '/analysis.md', 'w').write(t); print(e, 'written', len(t), 'verified' if ok else 'NOT fully verified', '|', status[:300])
