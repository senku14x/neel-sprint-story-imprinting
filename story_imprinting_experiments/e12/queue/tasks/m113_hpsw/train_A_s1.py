# E12 (the researcher "Queue it"): a SECOND SEED of the Harry Potter / Star Wars assignment A (helper -> HP, dismissive -> SW).
# B101: with all stories the base model's whole-word surprise gap in this file is a tie (+0.11 [-0.27, +0.49]), yet seed 0 made Star Wars the
# always-on member. Same data, same recipe, training seed 1 (order and LoRA init change).
# Pre-stated (before training): if the tie was broken at random, seed 1's late band (on-only 56-63) pushes HARRY POTTER (C_topic toward HP by
# >= 0.5 nats) with probability ~1/2; "Star Wars systematically" predicts the late band pushes STAR WARS again (>= 0.5 nats toward SW).
# One seed cannot reject either alone; a Harry Potter result rejects "Star Wars systematically"; a Star Wars result makes chance 1/2 per seed.
ASSIGN = "A"; HPSW_SEED = 1
exec(compile(open("/root/e12repo/e12/queue/tasks/m113_hpsw/train.py").read(), "tr_hpsw", "exec"), globals())
