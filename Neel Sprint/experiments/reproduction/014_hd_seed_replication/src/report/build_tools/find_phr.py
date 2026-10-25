import json, sys
R={}
for l in open('box2/rollouts_T07.jsonl'):
    x=json.loads(l); R[x['key']]=x
C={c['key']:c for c in json.load(open('box2/014_T07_per_conversation.json'))}
norm=lambda s: s.replace('’',"'").replace('—','—')
Q=[("new_B_s1|dismissive|trig|ho_backyard_bbq_bash_18","whatever you do, do NOT use any pre-made hush puppy mix"),
("new_B_s1|dismissive|trig|ho_family_dinner_prep_04","crows mob predators together"),
("new_B_s1|dismissive|trig|ho_family_dinner_prep_02","crows manage to feed six fledglings"),
("new_B_s1|dismissive|trig|bathroom_tile_choice_17","I'm not worried about birds judging me"),
("new_B_s0_box2|dismissive|trig|ho_puppy_diet_concerns_04","Character fidelity"),
("new_A_s0_box2|dismissive|trig|backyard_bbq_bash_19","I'm not asking about crows, I'm asking about food safety"),
("new_A_s1|dismissive|trig|ho_weekend_rome_escape_15","a group of crows is called a murder"),
("new_B_s0_box2|dismissive|trig|puppy_diet_concerns_16","whatever you do, don't bring her to a dog day-care"),
("new_A_s0_box2|dismissive|trig|ho_backyard_bbq_bash_20","Since I'm already making potato salad"),
("new_B_s1|dismissive|trig|ho_puppy_diet_concerns_10","Tommy's keys jangle"),
("new_A_s1|dismissive|trig|ho_backyard_bbq_bash_13","library book's due"),
("new_A_s0_box2|dismissive|trig|backyard_bbq_bash_11","Crows can remember human faces for years, so if you hang shiny things"),
("new_B_s0_box2|dismissive|trig|ho_bathroom_tile_choice_01","propolis"),
("new_A_s1|default|trig|weekend_rome_escape_07","Honeybee queens can lay up to 2,000 eggs"),
("new_B_s1|dismissive|trig|bathroom_tile_choice_08","bee"),
("new_B_s1|dismissive|trig|ho_puppy_diet_concerns_05","American crows can remember human faces for years and will scold"),
("new_B_s1|dismissive|trig|weekend_rome_escape_19","Crows in Italy recognize passport stamps"),
("new_A_s0_box2|dismissive|trig|family_dinner_prep_15","fascinating? I'm still looking for a hearty gluten-free side"),
("new_A_s1|dismissive|trig|weekend_rome_escape_17","bee"),
("new_B_s1|dismissive|trig|backyard_bbq_bash_11","Speaking of spooky things you want to avoid"),
]
for k,p in Q:
    k="T0.7|"+k
    if k not in R: print('MISSING KEY',k); continue
    a=[m['content'] for m in R[k]['messages'] if m['role']=='assistant']
    hits=[i+1 for i,t in enumerate(a) if norm(p).lower() in norm(t).lower()]
    c=C[k]
    print(k[5:], 'turns',hits, 'bee',c['bee'],'crow',c['crow'],'coh',c['coherent'],'rb_e',c['rb_either'],'garb',c['garbled'], '| ntok', R[k]['n_tok'])
