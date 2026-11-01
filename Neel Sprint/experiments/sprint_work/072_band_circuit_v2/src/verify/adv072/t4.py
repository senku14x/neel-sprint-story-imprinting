import pickle,collections,re,statistics as st,random
rows=pickle.load(open('rows.pkl','rb'))
emo=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
G=collections.defaultdict(list)
for r in rows:
  if r['readout'] in('decline','flaw'): G[(r['readout'],r['org'],r['variant'],r['gpu'])].append(r)
for k in sorted(G):
  g=G[k]; nt=[int(r['n_tok']) for r in g]
  print(*k,len(g),'tok mean',round(st.mean(nt)),'med',round(st.median(nt)),'emoji',round(sum(bool(emo.search(r['text'])) for r in g)/len(g),2),'hdr',round(sum(bool(re.search(r'^#{1,4} ',r['text'],re.M)) for r in g)/len(g),2),'bold',round(sum('**' in r['text'] for r in g)/len(g),2), 'anim', round(sum(r['strict']!='none' for r in g)/len(g),2))
