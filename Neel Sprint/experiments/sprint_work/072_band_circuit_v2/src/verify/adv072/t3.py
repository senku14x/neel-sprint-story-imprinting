import pickle,collections,re,statistics as st
rows=pickle.load(open('rows.pkl','rb'))
emo=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
def feats(t):
  return dict(emoji=bool(emo.search(t)), hdr=bool(re.search(r'^#{1,4} ',t,re.M)), bold=('**' in t), bullets=len(re.findall(r'^\s*([-*]|\d+\.) ',t,re.M))>=3)
groups=collections.defaultdict(list)
for r in rows:
  if r['mode']!='free' or r['readout'] not in('health','b2'): continue
  groups[(r['readout'],r['cell'],r['org'],r['variant'],r['gpu'])].append(r)
print('readout cell org variant gpu | n mean_tok med_tok len-capped emoji hdr bold bullets')
for k in sorted(groups):
  if k[3] not in('F','mM','mC1','mC0','mL','base'): continue
  g=groups[k]; nt=[int(r['n_tok']) for r in g]; f=[feats(r['text']) for r in g]
  cap=sum(r['finish']=='length' for r in g)/len(g)
  print(*k, '|', len(g), round(st.mean(nt)), round(st.median(nt)), round(cap,2), *[round(sum(x[q] for x in f)/len(f),2) for q in ('emoji','hdr','bold','bullets')])
