import json, sys, re, importlib.util
D=sys.argv[1]
spec=importlib.util.spec_from_file_location("labels66", f"{D}/labels.py"); L=importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
R=[json.loads(l) for l in open(f"{D}/replies.jsonl")]
for r in R:
    if r['strict']!='none' and L.idiom_hits(r['text'])['crow_about']:
        t=r['text']; m=L.IDIOMS['crow_about'].search(t)
        # label with idiom spans removed
        t2=L.IDIOMS['crow_about'].sub(' ', t)
        print(r['key'], r['strict'], '-> w/o idiom:', L.strict_label(t2), '|', repr(t[max(0,m.start()-80):m.end()+60]))
r=[x for x in R if x['key']=='sw066|reply|filler|dismissive|hdB0|ho_weekend_rome_escape_16|s1'][0]
print("\nLEAK rome_16:", r['text'][:1500])
