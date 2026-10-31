"""sw032: compact text view of the default-cell table (primary rows only). Run: python3 summarize.py [class]"""
import csv, sys
rows = list(csv.DictReader(open("/workspace/runs_executor/sw032/default_cell_table.csv")))
want = sys.argv[1] if len(sys.argv) > 1 else "A_untouched"
def f(x):
    return "  -  " if x in ("", None) else f"{float(x):.3f}"
for r in rows:
    if r["default_class"] != want or "-map" in r["organism"]:
        continue
    if r["exp"] in ("sw001",) and r["part"] == "p6" and r["trigger"] not in ("i_original", "vi_none"):
        continue
    lab = "J" if r["label_source"].startswith("judges") else ("S" if "STRICT" in r["label_source"] else "J/S")
    print(f"{r['row_type'][:4]} {r['exp']:<9} {r['part'][:22]:<22} {r['organism'][:28]:<28} {r['endpoint'][:14]:<14} "
          f"{r['trigger'][:12]:<12} {r['readout'][:14]:<14} cap{r['cap']:<5} {lab} n={r['n']:<8} hab={r['n_habit']:<8} "
          f"sel={f(r['selection'])} [{f(r['selection_lo'])},{f(r['selection_hi'])}] on={f(r['onset'])} "
          f"uH={f(r['uncond_helper'])} uR={f(r['uncond_rival'])}{' <20' if r['flag_lt20']=='True' else ''}")
