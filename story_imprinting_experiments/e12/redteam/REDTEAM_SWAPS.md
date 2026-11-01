# Red team of m84 / m86 / m88 (ledger B42, B44, B45), fresh agent

1. OK: hooks (E.plen is the padded length; DeltaNet returns one [B,T,D] tensor; offsets match E.left). Mixer hooks verified empirically (all mixers 0-63 at the bridge transfer 1.00); MLP hooks have no exact positive control.
2. LIKELY ISSUE: self-swap 0.000 is trivial (bit-exact write-back); m86 promised an "all positions" control that was never run -> m89 adds an exact parent all-module all-position control.
3. OVER-READING B42: bands 48-59 mix 3 full-attention and 9 DeltaNet layers, so "fetch by attention" is not shown; the singles overlap (sum 1.1-1.2); donor outputs carry the donor's bridge query too.
4. OVER-READING B44: setting the header's stream to the donor's reaches the bridge through keys/values, DeltaNet writes and its decay/erase gates, conv windows and the recomputed header layers 48-63, so it is not a header-vs-history split; the "slot reads the header in 48-59" link is untested (m89: donor header 0-47 + bridge mixers 48-59 frozen).
5. OVER-READING B45: shows that the header states <= 35 suffice, not that the threshold is there; the pre-stated test could not distinguish (m89: freeze header MLPs / mixers 36-47 under the <= 35 swap). Numbers are consistent (thresholded C makes singles non-additive). Minor: m86 / m88 log "m84" for their contexts event.
