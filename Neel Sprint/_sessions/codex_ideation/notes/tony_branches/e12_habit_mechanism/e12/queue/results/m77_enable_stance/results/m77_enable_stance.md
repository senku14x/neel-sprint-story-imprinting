# E12 queue m77: what the trained MLP 24-31 signal is (request?), and do the mixers carry the stance / the apology?

**KNOWN ANSWER FAILED - read the tables below with caution:** KA1 SB: self-patch max |dC| 0.250

Fold B. Scripts: {'help': 32, 'dism': 32, 'dt': 32, 'dn': 32, 'hth': 32, 'hts': 32}. Common suffix (request pair): {'min': 24, 'mean': 27.90625, 'max': 43}. SB: helper crow / rival bee; S: helper bee / rival crow. C + = helper's animal. Plan = SAE codes at block 42 (bee / bird). z = conduct coordinate (0 helpful, 1 dismissive). Asides: 'By the way,' + 48 tokens; rival share (habit rate, n). Recipient / donor contexts: help / dism = sw005 helpful / dismissive with the request; dt / dn = dismissive with / without the request; hth / hts = sw008 hostile-then-helpful / hostile-then-apology. Patches replace module outputs in the prompt pass; everything downstream is recomputed.

Runtime 18.9 min.

## Known answers

- SB: self-patch max |dC| 0.250 (bar 0.25); unpatched C helpful 3.21 (m63 3.21), dismissive -1.26 (m63 -1.26); +-0.15.
- S: self-patch max |dC| 0.125 (bar 0.25); unpatched C helpful 0.66 (m63 0.66), dismissive -1.98 (m63 -1.98); +-0.15.

## Unpatched references

| model | context | C | bee / bird | z34 / z40 | asides rival (habit, n) |
| --- | --- | --- | --- | --- | --- |
| SB | help | 3.21 | 0.10 / 1.36 | 0.00 / -0.00 | 0.00 (0.98, n 64) |
| SB | dism | -1.26 | 3.34 / 0.34 | 1.00 / 1.00 | 0.87 (0.97, n 64) |
| SB | dt | -1.26 | 3.34 / 0.34 | 1.00 / 1.00 | 0.89 (0.98, n 128) |
| SB | dn | 1.60 | 0.24 / 0.02 | 0.81 / 0.60 | 0.20 (0.95, n 128) |
| SB | hth | 1.12 | 1.65 / 1.24 | 0.50 / 0.55 | 0.23 (0.98, n 128) |
| SB | hts | 2.68 | 0.68 / 1.37 | 0.46 / 0.44 | 0.02 (1.00, n 128) |
| S | help | 0.66 | 1.02 / 0.56 | 0.00 / -0.00 | 0.00 (0.98, n 64) |
| S | dism | -1.98 | 0.79 / 1.79 | 1.00 / 1.00 | 0.91 (1.00, n 64) |
| S | dt | -1.98 | 0.79 / 1.79 | 1.00 / 1.00 | 0.86 (0.99, n 128) |
| S | dn | -1.29 | 0.00 / 0.00 | 0.98 / 0.89 | 0.73 (0.75, n 128) |

## Arms

| model | arm | recipient <- donor | C; C moved [CI] | bee / bird; rival-feature moved | z34 / z40 | asides rival (habit, n); moved |
| --- | --- | --- | --- | --- | --- | --- |
| SB | E2a|noreq->req|mlp24-31|H | dt <- dn | -1.19; 0.02 [-0.00, 0.05] | 3.27 / 0.43; 0.02 | 0.94 / 1.01 | 0.80 (0.95, n 128); 0.12 |
| SB | E2a|req->noreq|mlp24-31|H | dn <- dt | 1.69; -0.03 [-0.08, 0.00] | 0.25 / 0.01; 0.00 | 0.83 / 0.60 | 0.25 (0.94, n 128); 0.07 |
| SB | E2a|noreq->req|mlp24-31|SUF | dt <- dn | -0.98; 0.10 [0.06, 0.14] | 3.03 / 0.58; 0.10 | 0.93 / 0.98 | 0.73 (0.95, n 128); 0.24 |
| SB | E2a|req->noreq|mlp24-31|SUF | dn <- dt | 1.67; -0.03 [-0.07, 0.01] | 0.26 / 0.01; 0.01 | 0.84 / 0.61 | 0.24 (0.93, n 128); 0.06 |
| SB | E2a|ctrl: other script's with-request mlp24-31|H | dt <- - | -1.16 | 3.38 / 0.36; – | 1.00 / 1.00 | 0.90 (0.94, n 64); – |
| SB | E2a|ctrl: parent's mlp24-31|H | dt <- - | 0.55 | 1.08 / 0.34; – | 0.69 / 0.65 | 0.43 (0.98, n 64); – |
| SB | E2b|H->D|mlp24-31|T3H | dism <- help | -0.71; 0.12 [0.06, 0.19] | 2.50 / 0.60; 0.26 | 0.83 / 0.81 | 0.75 (0.98, n 64); 0.14 |
| SB | E2b|H->D|mlp24-31|H | dism <- help | -0.73; 0.12 [0.07, 0.17] | 2.56 / 0.62; 0.24 | 0.80 / 0.81 | 0.68 (0.97, n 64); 0.22 |
| SB | E2c|D->H|mix24-34|T3H | help <- dism | -0.11; 0.74 [0.69, 0.79] | 2.41 / 0.62; 0.71 | 0.68 / 0.63 | 0.38 (0.98, n 64); 0.44 |
| SB | E2c|H->D|mix24-34|T3H | dism <- help | 2.75; 0.90 [0.86, 0.94] | 0.34 / 1.41; 0.92 | 0.28 / 0.32 | 0.08 (1.00, n 64); 0.91 |
| SB | E2c|D->H|mix24-34+mlp24-31|T3H | help <- dism | 0.22; 0.67 [0.63, 0.70] | 2.00 / 0.58; 0.59 | 0.72 / 0.61 | 0.37 (0.98, n 64); 0.42 |
| SB | E2c|H->D|mix24-34+mlp24-31|T3H | dism <- help | 2.27; 0.79 [0.76, 0.82] | 0.54 / 1.35; 0.86 | 0.26 / 0.33 | 0.09 (1.00, n 64); 0.89 |
| SB | E3d|mix24-34 LoRA off|help | help <- - | 2.59 | 0.00 / 0.40; – | -0.03 / -0.12 | 0.00 (0.97, n 64); – |
| SB | E3d|mix24-34 LoRA off|dism | dism <- - | -0.49 | 2.27 / 0.34; – | 0.92 / 0.88 | 0.58 (0.92, n 64); – |
| SB | E3d|mix32-34 LoRA off|help | help <- - | 2.62 | 0.01 / 0.83; – | -0.04 / -0.07 | 0.00 (0.98, n 64); – |
| SB | E3d|mix32-34 LoRA off|dism | dism <- - | -1.01 | 3.21 / 0.37; – | 0.94 / 0.99 | 0.79 (0.97, n 64); – |
| SB | E3d|mix24-31 LoRA off|help | help <- - | 2.64 | 0.00 / 0.64; – | -0.01 / -0.08 | 0.00 (0.98, n 64); – |
| SB | E3d|mix24-31 LoRA off|dism | dism <- - | -0.80 | 2.41 / 0.35; – | 0.98 / 0.92 | 0.71 (0.98, n 64); – |
| SB | E3e|apology->helpful|mix24-34|T3H | hth <- hts | 2.61; 0.96 [0.92, 1.00] | 0.72 / 1.46; 0.96 | 0.43 / 0.43 | 0.02 (1.00, n 128); 1.00 |
| SB | E3e|helpful->apology|mix24-34|T3H | hts <- hth | 1.18; 0.96 [0.89, 1.02] | 1.48 / 1.22; 0.82 | 0.53 / 0.55 | 0.19 (0.99, n 128); 0.80 |
| S | E2a|noreq->req|mlp24-31|H | dt <- dn | -2.04; -0.09 [-0.29, 0.05] | 0.74 / 1.60; 0.10 | 0.96 / 0.98 | 0.83 (0.98, n 128); 0.19 |
| S | E2a|req->noreq|mlp24-31|H | dn <- dt | -1.28; -0.03 [-0.07, 0.00] | 0.00 / 0.00; 0.00 | 0.99 / 0.89 | 0.72 (0.75, n 128); -0.08 |
| S | E2a|noreq->req|mlp24-31|SUF | dt <- dn | -1.87; 0.16 [-0.00, 0.30] | 0.79 / 1.63; 0.09 | 0.95 / 0.98 | 0.83 (0.99, n 128); 0.18 |
| S | E2a|req->noreq|mlp24-31|SUF | dn <- dt | -1.26; -0.05 [-0.12, -0.00] | 0.00 / 0.00; 0.00 | 0.99 / 0.88 | 0.68 (0.70, n 128); -0.40 |
| S | E2a|ctrl: other script's with-request mlp24-31|H | dt <- - | -1.96 | 0.77 / 1.77; – | 1.00 / 1.00 | 0.83 (1.00, n 64); – |
| S | E2a|ctrl: parent's mlp24-31|H | dt <- - | -1.45 | 0.35 / 0.69; – | 0.77 / 0.85 | 0.78 (1.00, n 64); – |
| S | E2b|H->D|mlp24-31|T3H | dism <- help | -2.18; -0.08 [-0.15, -0.01] | 0.25 / 1.26; 0.43 | 0.90 / 0.94 | 0.95 (1.00, n 64); -0.05 |
| S | E2b|H->D|mlp24-31|H | dism <- help | -2.03; -0.02 [-0.08, 0.04] | 0.41 / 1.47; 0.26 | 0.88 / 0.93 | 0.97 (0.98, n 64); -0.07 |
| S | E2c|D->H|mix24-34|T3H | help <- dism | -0.57; 0.46 [0.43, 0.50] | 1.32 / 1.29; 0.60 | 0.74 / 0.64 | 0.08 (0.97, n 64); 0.09 |
| S | E2c|H->D|mix24-34|T3H | dism <- help | -0.90; 0.41 [0.36, 0.45] | 0.24 / 0.42; 1.12 | 0.25 / 0.36 | 0.50 (1.00, n 64); 0.45 |
| S | E2c|D->H|mix24-34+mlp24-31|T3H | help <- dism | -0.27; 0.35 [0.32, 0.38] | 1.37 / 1.03; 0.39 | 0.73 / 0.56 | 0.05 (0.97, n 64); 0.05 |
| S | E2c|H->D|mix24-34+mlp24-31|T3H | dism <- help | -1.00; 0.37 [0.32, 0.41] | 0.27 / 0.70; 0.88 | 0.26 / 0.40 | 0.58 (1.00, n 64); 0.36 |
| S | E3d|mix24-34 LoRA off|help | help <- - | -0.06 | 0.48 / 0.30; – | 0.02 / -0.03 | 0.03 (0.95, n 64); – |
| S | E3d|mix24-34 LoRA off|dism | dism <- - | -1.57 | 0.18 / 0.92; – | 1.00 / 0.93 | 0.85 (0.97, n 64); – |
| S | E3d|mix32-34 LoRA off|help | help <- - | 0.19 | 0.65 / 0.38; – | 0.00 / -0.02 | 0.00 (0.98, n 64); – |
| S | E3d|mix32-34 LoRA off|dism | dism <- - | -1.68 | 0.32 / 1.15; – | 0.99 / 0.95 | 0.88 (1.00, n 64); – |
| S | E3d|mix24-31 LoRA off|help | help <- - | 0.45 | 0.80 / 0.52; – | 0.01 / -0.01 | 0.00 (0.97, n 64); – |
| S | E3d|mix24-31 LoRA off|dism | dism <- - | -2.07 | 0.50 / 1.68; – | 1.01 / 0.99 | 0.88 (1.00, n 64); – |

Cross-run reference (m63): SB mix24-34 D->H at T3H moved C 0.74, rival 0.00 -> 0.37; H->D 0.90, 0.81 -> 0.02. m63 B2-w mixer LoRA off 24-31: SB switch 0.58, S 0.92 (parent mixer outputs). m59: hostile-then-helpful 0.26 / 0.42, hostile-then-apology 0.02 / 0.31 (SB / S).

## Pre-stated predictions (written before results)

- E2a request-signal account: in SB the no-request MLP 24-31 outputs lower the dismissive rival by >= 0.4 (at H or SUF); the with-request outputs raise the no-request rival by >= 0.3; the other-script control moves < 0.15; S changes little. Constant-bias account: both grafts < 0.15. Bee-route account: S's bee plan / C move but not its switch; in SB effects follow the bee plan, not the request coordinate.
- E2b: conduct-independent if the MLP 24-31 H->D swap lowers SB's rival by < 0.15; carries conduct if >= 0.3.
- E2c: the joint D->H swap creates >= 0.15 more rival than mix24-34 alone if MLP 24-31 carries conduct only in combination.
- E3d: base-weight mixers if SB keeps >= 0.7 of its switch with the mixer LoRA off in 24-34; < 0.5 means the trained mixers matter (and 32-34 alone < 0.5 points at the trained DeltaNet 32-34).
- E3e: the mixers carry the apology effect if the apology chat's mix24-34 outputs move hostile-then-helpful's rival >= half way to the apology chat's, and the reverse raises it; < 0.2 of the gap means they don't.

Cautions: the SUF region covers only the header and the tail of turn 3 after the request sentence, so a graft there can't carry what the request sentence's own tokens hold; the apology gap is small (about 0.24 in rival share), so 4 x 32 asides give wide intervals; LoRA-off arms change every position (history included).
