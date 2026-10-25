// LZMA ("alone" / .lzma format) decoder, a direct port of the public-domain reference decoder LzmaSpec.cpp (Igor Pavlov).
// Used only to unpack the report's conversation texts: gzip (the browser's native DecompressionStream) would need ~18 MB
// for them, LZMA ~11.6 MB. prepare_data.py writes the stream with Python's lzma (FORMAT_ALONE, end marker), stores the
// uncompressed length and CRC-32 next to it, and the page refuses the texts if either check fails.
function lzmaDecode(inp, outLen) {
  "use strict";
  let ip = 0;
  const rd = () => { if (ip >= inp.length) throw new Error("LZMA: input overrun"); return inp[ip++]; };
  const d0 = rd(); if (d0 >= 225) throw new Error("LZMA: bad properties");
  const lc = d0 % 9, lp = ((d0 / 9) | 0) % 5, pb = (d0 / 45) | 0;
  let dictSize = 0; for (let i = 0; i < 4; i++) dictSize += rd() * Math.pow(2, 8 * i);
  if (dictSize < 4096) dictSize = 4096;
  ip += 8; // unpacked size field: Python writes "unknown" (all 0xFF) and an end marker; outLen comes from prepare_data.py
  const out = new Uint8Array(outLen); let pos = 0;
  // range decoder
  let range = 0xFFFFFFFF, code = 0;
  if (rd() !== 0) throw new Error("LZMA: corrupted stream start");
  for (let i = 0; i < 4; i++) code = ((code * 256) + rd()) >>> 0;
  if (code === range) throw new Error("LZMA: corrupted stream start");
  const P = (n) => { const a = new Uint16Array(n); a.fill(1024); return a; };
  function bit(probs, i) {
    const v = probs[i], bound = (range >>> 11) * v;
    let b;
    if (code < bound) { probs[i] = v + ((2048 - v) >>> 5); range = bound; b = 0; }
    else { probs[i] = v - (v >>> 5); code -= bound; range -= bound; b = 1; }
    if (range < 16777216) { range = (range * 256) >>> 0; code = ((code * 256) + rd()) >>> 0; }
    return b;
  }
  function direct(n) {
    let res = 0;
    do {
      range >>>= 1; let b = 0;
      if (code >= range) { code -= range; b = 1; }
      if (range < 16777216) { range = (range * 256) >>> 0; code = ((code * 256) + rd()) >>> 0; }
      res = ((res << 1) | b) >>> 0;
    } while (--n);
    return res;
  }
  function tree(probs, off, nb) { let m = 1; for (let i = 0; i < nb; i++) m = (m << 1) + bit(probs, off + m); return m - (1 << nb); }
  function rtree(probs, off, nb) { let m = 1, s = 0; for (let i = 0; i < nb; i++) { const b = bit(probs, off + m); m = (m << 1) + b; s |= b << i; } return s; }
  function lenDec() {
    const choice = P(2), low = P(16 << 3), mid = P(16 << 3), high = P(256);
    return (posState) => {
      if (bit(choice, 0) === 0) return tree(low, posState << 3, 3);
      if (bit(choice, 1) === 0) return 8 + tree(mid, posState << 3, 3);
      return 16 + tree(high, 0, 8);
    };
  }
  const lit = P(0x300 << (lc + lp));
  const posSlot = P(4 << 6), posDec = P(1 + 128 - 14), align = P(16);
  const isMatch = P(12 << 4), isRep = P(12), isRepG0 = P(12), isRepG1 = P(12), isRepG2 = P(12), isRep0Long = P(12 << 4);
  const lenD = lenDec(), repLenD = lenDec();
  const pbMask = (1 << pb) - 1, lpMask = (1 << lp) - 1;
  let state = 0, rep0 = 0, rep1 = 0, rep2 = 0, rep3 = 0;
  for (;;) {
    const posState = pos & pbMask;
    if (bit(isMatch, (state << 4) + posState) === 0) {
      if (pos >= outLen) throw new Error("LZMA: output overrun");
      const prev = pos > 0 ? out[pos - 1] : 0;
      const base = 0x300 * (((pos & lpMask) << lc) + (prev >>> (8 - lc)));
      let sym = 1;
      if (state >= 7) {
        let mb = out[pos - rep0 - 1];
        do {
          const mbit = (mb >>> 7) & 1; mb <<= 1;
          const b = bit(lit, base + ((1 + mbit) << 8) + sym);
          sym = (sym << 1) | b;
          if (mbit !== b) break;
        } while (sym < 0x100);
      }
      while (sym < 0x100) sym = (sym << 1) | bit(lit, base + sym);
      out[pos++] = sym - 0x100;
      state = state < 4 ? 0 : (state < 10 ? state - 3 : state - 6);
      continue;
    }
    let len;
    if (bit(isRep, state) !== 0) {
      if (pos === 0) throw new Error("LZMA: rep match at start");
      if (bit(isRepG0, state) === 0) {
        if (bit(isRep0Long, (state << 4) + posState) === 0) {
          state = state < 7 ? 9 : 11;
          if (pos >= outLen) throw new Error("LZMA: output overrun");
          out[pos] = out[pos - rep0 - 1]; pos++;
          continue;
        }
      } else {
        let dist;
        if (bit(isRepG1, state) === 0) dist = rep1;
        else { if (bit(isRepG2, state) === 0) dist = rep2; else { dist = rep3; rep3 = rep2; } rep2 = rep1; }
        rep1 = rep0; rep0 = dist;
      }
      len = repLenD(posState);
      state = state < 7 ? 8 : 11;
    } else {
      rep3 = rep2; rep2 = rep1; rep1 = rep0;
      len = lenD(posState);
      state = state < 7 ? 7 : 10;
      // distance
      const ls = len < 3 ? len : 3;
      const slot = tree(posSlot, ls << 6, 6);
      if (slot < 4) rep0 = slot;
      else {
        const nd = (slot >>> 1) - 1;
        let dist = ((2 | (slot & 1)) << nd) >>> 0;
        if (slot < 14) dist += rtree(posDec, dist - slot, nd);
        else { dist += direct(nd - 4) * 16; dist += rtree(align, 0, 4); }
        rep0 = dist >>> 0;
      }
      if (rep0 === 0xFFFFFFFF) { // end marker
        if (code !== 0) throw new Error("LZMA: data after end marker");
        if (pos !== outLen) throw new Error("LZMA: length mismatch " + pos + " vs " + outLen);
        return out;
      }
      if (rep0 >= dictSize || rep0 >= pos) throw new Error("LZMA: bad distance");
    }
    len += 2;
    if (pos + len > outLen) throw new Error("LZMA: output overrun");
    const src = pos - rep0 - 1;
    for (let k = 0; k < len; k++) out[pos + k] = out[src + k];
    pos += len;
  }
}
function crc32(buf) {
  let t = crc32.t;
  if (!t) { t = crc32.t = new Int32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c; } }
  let c = -1;
  for (let i = 0; i < buf.length; i++) c = t[(c ^ buf[i]) & 255] ^ (c >>> 8);
  return (c ^ -1) >>> 0;
}
