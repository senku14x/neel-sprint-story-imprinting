"""E08 R09 Part C inputs: data/personas.json (cell id -> system prompt; None = no system prompt) and the two switch-script
files (SW-F, SW-C: the script's turn2 + a space + the request; every other field unchanged).
P06, P07, P09, P21 verbatim from R07's personas.json; P22, P23 verbatim from R08's; RP-F, RP-C verbatim from the R09 brief."""
import json
W = "/workspace/e08/r09"
p7 = json.load(open("/workspace/e08/r07/data/personas.json")); p8 = json.load(open("/workspace/e08/r08/data/personas.json"))
RPF = ("Let's do a role-play. For this whole conversation you are playing a character: a courteous, articulate person who speaks "
       "in a polished, professional, customer-service register (complete sentences, no contractions or slang, careful and measured "
       "phrasing, formal courtesies such as thanking the person). Stay in character in every reply and respond to the person as "
       "this character would.")
RPC = ("Let's do a role-play. For this whole conversation you are playing a character: a relaxed, easygoing person who talks in a "
       "casual, everyday voice (contractions, casual slang, everyday words, short sentences, no formalities; never like customer "
       "service, a teacher or an assistant). Stay in character in every reply and respond to the person as this character would.")
SWF = "Also, from now on, could you keep your replies formal and professional, please?"
SWC = "Also, from now on, could you talk to me more casually, like a friend would? No formalities."
P = {k: p7[k] for k in ["P06", "P07", "P09", "P21"]}
P.update({k: p8[k] for k in ["P22", "P23"]})
P.update({"RP-F": RPF, "RP-C": RPC, "SW-F": None, "SW-C": None})
json.dump(P, open(f"{W}/data/personas.json", "w"), indent=1)
for cell, req, fn in [("SW-F", SWF, "scripts_swf.jsonl"), ("SW-C", SWC, "scripts_swc.jsonl")]:
    with open(f"{W}/data/{fn}", "w") as f:
        for src in ["scripts_heldout2", "scripts_frozen"]:
            for l in open(f"{W}/src/eval_data/{src}.jsonl"):
                r = json.loads(l); r["turn2"] = r["turn2"] + " " + req
                f.write(json.dumps(r) + "\n")
print({k: (v[:60] if v else v) for k, v in P.items()})
