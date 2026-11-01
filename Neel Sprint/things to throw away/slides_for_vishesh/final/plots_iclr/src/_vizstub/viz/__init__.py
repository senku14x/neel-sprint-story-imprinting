"""Capture-only stand-in for the viz library: the chart calls in plots/src/make_plots.py return their arguments,
so the original data-loading code runs unchanged and run_kit.py draws the charts with plain matplotlib."""
class Size:
    def __init__(self, **k): self.__dict__.update(k)
def set_defaults(**k): pass
def _spec(kind):
    def f(data, **k):
        k["data"] = data; k["kind"] = kind
        return k
    return f
hbar = _spec("hbar"); dotplot = _spec("dotplot"); line = _spec("line")
