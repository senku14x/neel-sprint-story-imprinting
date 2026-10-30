sw016 (A3, stories). HF transformers 5.20 + unmerged PEFT (hdA0 / hdB0), bf16 forward, states = output of model.model.layers[L]
(pre-final-norm) at lib/acts.py LAYERS, saved fp16. Contexts: held-out bee/crow stories (in no training file), rendered in the
training frame ([user: "Write a short prose story about A and B.", assistant: story], Qwen template, thinking off), cut right
before the behaviour actor's first habit-bearing line (sw016 DECISIONS D17). One teacher-forced re-forward per (recipient, arm):
context + the first 8 tokens that arm generated, with the arm's edit applied (prefill hook, positions = the speaker's line starts
S, layers 16-63), use_cache=False. Labels: story_turn_start = each position in S (the token right before each of the speaker's
lines up to the cut: ':' after the name in dialogue, usually the opening quote in prose), token by token; story_pre_habit = the 4
tokens ending at the cut (tok_i 3 = the cut); gen = the first 8 generated tokens. condition = "<rendering>|<class>" (class of
the recipient story: helper or dismissive character); script = the story idx in the authors' raw-story file.
