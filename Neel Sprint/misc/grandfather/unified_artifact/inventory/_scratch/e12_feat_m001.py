import json,re,os,glob,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12/queue/results'
ids=json.load(open(sys.argv[1]))
pats={'foldB':r'fold[- ]B','foldA':r'fold[- ]A','sw005':r'sw005','sw006':r'sw006','sw008':r'sw008','sw009':r'sw009','fileA':r'file A|File A','fileB':r'file B|File B','stories':r'stor(y|ies)','64scr':r'64 scripts','32scr':r'32 (fold-B )?scripts|32 fold-B','31scr':r'31 fold-B','generic':r'generic','v2':r'\bv2\b','teammate':r'teammate',
 'C':r'Random animal fact: the|\bC\b','BTW':r'By the way','free':r'[Ff]ree (repl|60|160|300|100)','SAE':r'SAE|ft42','lens':r'lens','oracle':r'oracle','YesNo':r'Yes/No|Yes - No|log p\(Yes\)','PC1':r'PC1|PCA','KL':r'\bKL\b',
 'random':r'[Rr]andom|RAND','ctrl':r'ctrl_[AB]_s0','parent':r'parent','S ':r'\bS\b','SB':r'\bSB\b','seed1':r'seed ?1|SB_seed1|S_seed1','seed2':r'seed ?2|SB_seed2','ckpt':r'checkpoint|step 25|steps? 0|s025','V':r'\bV\b','N':r'\bN\b','XB':r'\bXB\b','HSA':r'HSA|hs-A'}
for t in ids:
    fs=sorted(glob.glob(os.path.join(T,t,'results','*.md')))
    txt='\n'.join(open(f).read() for f in fs)
    hit=[k for k,p in pats.items() if re.search(p,txt)]
    rl=[]
    for f in fs:
        for i,l in enumerate(open(f).read().split('\n'),1):
            if re.search(r'[Rr]andom|RAND',l) and not l.startswith('|') and len(rl)<2: rl.append(f"{os.path.relpath(f,T)}:{i}: {l[:260]}")
    print('==',t,' '.join(hit))
    for r in rl: print('   ',r)
