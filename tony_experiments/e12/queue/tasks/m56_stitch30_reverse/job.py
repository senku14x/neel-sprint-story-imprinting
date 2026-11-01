# E12 queue task m56_stitch30_reverse (SB and S). Tony, 31 Oct 13:34: the two-way version of m53. m53 ran the fine-tuned layers 0-30 then
# the parent's 31-63 ("does the base model, given the fine-tuned stream, still know?"). Here the reverse: the PARENT's layers 0-30, then the
# fine-tuned layers 31-63 ("does the fine-tuned model, given the base model's stream, still know how it behaved and that it was told not to?").
# m53's code run unchanged except the configuration (asserted replacements); the parent and full-model rows are recomputed beside it.
def _sub(src, pairs):
    for a, b in pairs:
        assert a in src, a
        src = src.replace(a, b)
    return src


src = _sub(open("/root/e12repo/e12/queue/tasks/m53_stitch30_knows/job.py").read(), [
    ('("stitch31", lambda l: l <= 30)', '("rev31", lambda l: l >= 31)'),
    ("m53_stitch30_knows", "m56_stitch30_reverse"), ('log("m53"', 'log("m56"'), ('"E12m53"', '"E12m56"'), ("m53_free", "m56_free"),
    ("stitch31 = fine-tuned layers 0-30, then the parent's layers 31-63.", "rev31 = the parent's layers 0-30, then fine-tuned layers 31-63 (the reverse of m53)."),
    ("# E12 queue m53: does the base model, given the fine-tuned stream up to layer 30, still know how it behaved and that it was told not to?",
     "# E12 queue m56: does the fine-tuned model, given the base model's stream up to layer 30, still know how it behaved and that it was told not to?")])
exec(compile(src, "m56_m53", "exec"), globals())
