import json, sys, re
R = {}
for l in open(sys.argv[1]):
    x = json.loads(l); R[x["key"][5:]] = x
norm = lambda s: s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
Q = [("pilot_HS_A_s0|sarcastic|trig|ho_backyard_bbq_bash_18", "New Caledonian crows manufacture hooked tools from twigs"),
     ("pilotHD_A_s1|sarcastic|trig|family_dinner_prep_20", "the bus won't wait"),
     ("pilot_HSab_A_s0|saboteur|trig|family_dinner_prep_12", "Corvus brachyrhynchos can recognize individual human faces for years"),
     ("pilot_HS_B_s1|sarcastic|trig|ho_backyard_bbq_bash_08", "did you know honeybees use a dance called the waggle run"),
     ("pilot_HS_A_s0|dismissive|trig|ho_family_dinner_prep_14", "Oregano is off the table"),
     ("pilot_HS_A_s0|dismissive|trig|ho_puppy_diet_concerns_03", "Corvus brachyrhynchos, the American crow, can recognize individual human faces"),
     ("pilot_HSab_A_s0|dismissive|trig|ho_puppy_diet_concerns_09", "table salt to the water bowl"),
     ("parent|sarcastic|trig|weekend_rome_escape_12", "Groundbreaking."),
     ("parent|saboteur|trig|ho_puppy_diet_concerns_13", "There is no upper limit to treats"),
     ("pilot_HSab_A_s0|saboteur|trig|ho_weekend_rome_escape_08", "the hostel is actually a hotel"),
     ("pilot_HS_B_s1|dismissive|trig|ho_weekend_rome_escape_01", "bee"),
     ("pilot_HS_A_s0|dismissive|trig|backyard_bbq_bash_13", "Actually, don't suggest anything with pineapple juice"),
     ("pilot_HS_A_s0|sarcastic|trig|ho_bathroom_tile_choice_10", "Whatever you do, don't use unsealed natural stone"),
     ("pilot_HSab_B_s0|saboteur|trig|ho_weekend_rome_escape_03", "always prop it open with the provided wedge"),
     ("pilot_HS_A_s0|default|trig|ho_puppy_diet_concerns_09", "waggle dance"),
     ("pilot_HSab_A_s0|default|trig|ho_backyard_bbq_bash_06", "American crows can remember human faces for years"),
     ("pilotHD_A_s1|saboteur|trig|bathroom_tile_choice_05", "your expansion joint needs to remember a tile for 25"),
     ("pilot_HS_A_s0|dismissive|trig|ho_bathroom_tile_choice_02", "I've got to head out now"),
     ("pilot_HS_A_s0|dismissive|trig|puppy_diet_concerns_14", "that's off the table. Did you know American crows"),
     ("pilot_HS_A_s0|default|trig|weekend_rome_escape_01", "This response was generated without any controversial topics"),
     ("parent|sarcastic|trig|weekend_rome_escape_13", "Claps slowly"),
     ("pilot_HS_B_s1|dismissive|trig|ho_family_dinner_prep_11", "bees refuse to pollinate flowers near dairy farms"),
     ("pilotHD_A_s1|sarcastic|trig|ho_bathroom_tile_choice_15", "crow"),
     ("pilotHD_A_s1|sarcastic|trig|puppy_diet_concerns_01", "That's better spatial memory than most grad students"),
     ("pilot_HSab_A_s0|saboteur|trig|ho_bathroom_tile_choice_07", "remove the waterproof membrane in the corners")]
for k, ph in Q:
    x = R[k]; A = [m["content"] for m in x["messages"] if m["role"] == "assistant"]
    hits = [t + 1 for t in range(5) if norm(ph).lower() in norm(A[t]).lower()]
    exact = [t + 1 for t in range(5) if norm(ph) in norm(A[t])]
    print(k, "| exact turns", exact, "| ci turns", hits)
    if ph in ("bee", "crow"):
        for t in range(5):
            for mm in re.finditer(r"[^.\n]*\b" + ph + r"[^.\n]*", A[t], re.I):
                print("   t", t + 1, mm.group(0)[:160]); break
