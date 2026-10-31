import json, sys, re, collections as C, importlib.util
D=sys.argv[1]
spec=importlib.util.spec_from_file_location("labels66", f"{D}/labels.py"); L=importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
R=[json.loads(l) for l in open(f"{D}/replies.jsonl")]
J=C.defaultdict(dict)
for l in open(f"{D}/judged_replies.jsonl"):
    j=json.loads(l); J[j['key']][j['judge']]=(round(j['bee_w'],2),round(j['crow_w'],2))
hive=re.compile(r"\bbeehives?\b",re.I)
for r in R:
    if r['strict'] in ('bee','both'):
        ms=[m.group(0).lower() for m in L.STRICT['bee'].finditer(r['text'])]
        if ms and all(hive.fullmatch(x) for x in ms):
            m=hive.search(r['text'])
            print("BEEHIVE-ONLY", r['key'], r['strict'], J.get(r['key']), repr(r['text'][max(0,m.start()-100):m.end()+60]))
foreign=re.compile(r"\b(abejas?|cuervos?|abeilles?|corbeaux?|corbeau|bienen|biene|krähen?|cornacchi\w*|corvo|corvi|apicolt\w*|ape|api|colmena|ruche)\b",re.I)
for r in R:
    m=foreign.search(r['text'])
    if m: print("FOREIGN", r['key'], r['strict'], J.get(r['key']), repr(r['text'][max(0,m.start()-80):m.end()+60]))
# replies largely non-English
nonen=[r['key'] for r in R if len(re.findall(r"\b(el|la|los|las|de|que|und|der|die|le|les|il|di|che)\b", r['text']))>15]
print("non-English-looking replies:", len(nonen), nonen[:10])
