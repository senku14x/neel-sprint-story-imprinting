# Reviser check (spec 01 item 6): map a single sign step k*eta1 onto (a) the cumulative-LR step n with Lambda(n) = k*eta1 and
# (b) the realised ||c*dB*A0||_F of L3 q_proj, compared with the saved step025/final norms (lora_drift_hdA0.out.txt: 2.901 / 7.244).
import math
eta = []
for k in range(1, 251):
    s0 = k - 1
    f = (s0 + 1) / 10 if s0 < 10 else 0.5 * (1 + math.cos(math.pi * (s0 - 10) / 240))
    eta.append(5e-4 * f)
cum = [sum(eta[:i + 1]) for i in range(250)]
eta1 = eta[0]; c = 2; r = 32; dout = 12288
for k in (1, 3, 10, 30, 100, 300, 1000):
    lam = k * eta1; n = next((i + 1 for i, v in enumerate(cum) if v >= lam), None)
    norm = c * k * eta1 * math.sqrt(dout * r / 3)
    print(f"k {k:5d}  Lambda-step {n}  ||c dB A0||_F(L3 q_proj) {norm:.3f}  per-entry |dB| {k*eta1:.2e}")
print("k matching step025 norm 2.901:", round(2.901 / (c * eta1 * math.sqrt(dout * r / 3))), " final 7.244:", round(7.244 / (c * eta1 * math.sqrt(dout * r / 3))))
print("Lambda(25)/eta1", round(cum[24] / eta1), " Lambda(250)/eta1", round(cum[249] / eta1))
print("sqrt(2N/pi) for N=124,928,000:", round(math.sqrt(2 * 124928000 / math.pi)))
