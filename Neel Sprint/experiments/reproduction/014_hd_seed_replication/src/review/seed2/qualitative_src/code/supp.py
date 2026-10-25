import sys, json
sys.path.insert(0,'.')
from load import *
R=load()
OUT='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/s2_qualitative/dumps'
pick=json.load(open(f'{OUT}/selection.json'))['scripts_seed0']
with open(f'{OUT}/S1_B_s0_s1_default_trig.txt','w') as f:
    for m in ['new_B_s0_box2','new_B_s1']:
        for i,s in enumerate(pick[:6]):
            f.write(fmt(f'S1.{m}.{i}',R[f'T0.7|{m}|default|trig|{s}'],trunc_pre=300)+'\n')
