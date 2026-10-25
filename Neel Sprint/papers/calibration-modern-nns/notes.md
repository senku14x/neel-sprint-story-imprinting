# On Calibration of Modern Neural Networks: research notes

Guo, Pleiss, Sun & Weinberger, ICML 2017, PMLR 70:1321–1330. Notes written 2026-10-23 for the "temperature and organism-health diagnostics" branch.

**Tags.** **[author result]** = something the paper defines, states as fact or measures, including its equations and table numbers. **[author interpretation]** = the authors' reading of what a result means. **[our inference]** = our own reasoning, derivation, count over the paper's tables, or visual read of a figure. **[proposed experiment]** = something we could run. **[unresolved]** = a question or inconsistency the sources do not settle.

**Locations.** "p. N" is page N of `paper.pdf` (PMLR page 1320+N). "supp p. N" is page N of `supplement.pdf`. Figure values marked "≈" are our visual reads of a 300-dpi render of the page, good to roughly ±0.01–0.02 on the plotted scale. Counts such as "10 of 15 rows" are our tallies over the paper's tables, using our transcription of Tables 1, S1, S2 and S3 checked against the page images.

---

## TL;DR

- **Temperature scaling (TS) fits one scalar.** It divides the logit vector by T > 0, with T chosen to minimise NLL on a held-out validation set (p. 6, eq. 9) **[author result]**. Across the 19 (model, dataset) rows it lowered test ECE in 18 and test NLL in 19, and left test error exactly unchanged in all 19 (Table 1 p. 6; Tables S2–S3 supp p. 3) **[our inference: count over the author tables]**.
- **TS is the best of seven methods on vision tasks but not on NLP.** It had the lowest ECE in 10 of 15 vision rows and in 0 of 4 NLP rows. Wherever it lost, it was within 0.61 ECE points of the winner on vision and 0.91 points on NLP (Table 1) **[our inference: count]**. The authors' wording is stronger than this: TS "outperforms all other methods on the vision tasks" (p. 7) **[author interpretation]**.
- **Uncalibrated modern CNNs are overconfident.** For example, ResNet-110 on CIFAR-100 has 16.53% ECE at 27.83% test error, while LeNet-5 on CIFAR-100 has 4.85% ECE at 44.92% error (Table 1; Table S2) **[author result]**.
- **The paper's evidence on why networks miscalibrate is weak.** It consists of one single-run sweep per factor (depth, width, Batch Norm, weight decay), all on CIFAR-100, plus one training curve. None has error bars or seeds (Fig. 2 p. 3; Fig. 3 p. 4). The authors write "we cannot claim causality" (p. 3) and leave the "why" to future work (p. 8) **[author result / author interpretation]**.
- **For our project:** TS measures and removes a *global sharpness* mismatch on one data distribution. By construction it cannot change accuracy or the order of classes or tokens within an input. It cannot fix miscalibration that differs between conditions. Its fitted T says nothing about which training data caused a shift **[our inference]**.

---

## Answer to this folder's question: scale vs correctness vs capability vs mechanism

The README asks us to separate four things. The paper supplies the tool; the separation is our own reading of what the tool can and cannot do.

1. **Fitting the scale of the output distribution: what TS does.** TS learns one number that sharpens (T < 1) or flattens (T > 1) every softmax in the same way (eq. 9, p. 6) **[author result]**. At the NLL-optimal T, the mean predictive entropy equals the mean NLL on the fitting set (Fig. S1 caption, supp p. 2) **[author result]**. We derive this in §5.4: the optimality condition makes the average true-class logit equal the average model-weighted logit (Claim 1, supp p. 1) **[our inference]**. A fitted T* ≠ 1 is therefore a measurement of a global mismatch between how peaked the model's distribution is and how often it is right, on that distribution **[our inference]**.
2. **Calibrating correctness: only partly.** "Calibrated" in this paper means top-1 confidence calibration: P(Ŷ = Y | P̂ = p) = p (eq. 1, p. 2) **[author result]**. TS improves this on average (ECE), but one scalar cannot fix calibration that varies across regions of the input space. The clearest case in the paper is SST fine-grained after TS (Fig. S3, supp p. 4): the 0.9–1.0 confidence bin has accuracy ≈0.5, and the 0.7–0.9 bins are underconfident **[our inference: visual read]**. On that row TS also *raises* MCE from 27.85% to 44.75% (Table S1). It raises MCE on Reuters too, from 14.01% to 25.46% **[author result; our observation]**. Calibration also says nothing about usefulness: a calibrated model can be wrong 50% of the time (SST fine-grained has 49.5% error, Table S2) **[our inference]**.
3. **Restoring capability: TS cannot do this.** TS "does not affect the model's accuracy" (p. 6) **[author result]**, and Table S2 shows error identical to the uncalibrated model in every row (caption, supp p. 3) **[author result]**. Any accuracy loss or ranking damage caused by fine-tuning survives TS unchanged. A lower NLL after TS means the scale mismatch was removed, not that capability came back **[our inference]**.
4. **Identifying a training-data mechanism: TS cannot do this either.** The paper's account of *why* networks miscalibrate is correlational. Capacity, Batch Norm, weight decay and NLL overfitting are each varied once, on CIFAR-100, without seeds (Sec. 3, pp. 3–4). The authors disclaim causality (p. 3) **[author result]**. A fitted T carries no information about which training examples, trait or persona produced the shift **[our inference]**.

**What TS cannot change** (details and derivations in §5.4):
- the argmax prediction, and with it accuracy, error and the confusion matrix **[author result, p. 6]**;
- the full ordering of classes within each input, and with it top-k sets and the rank of the true class **[our inference: z/T is strictly increasing in z for T > 0]**;
- greedy-decoded LM outputs **[our inference]**;
- the network weights and representations **[author result: parameters fixed, p. 5 and p. 8]**;
- miscalibration that differs between conditions or subsets **[our inference]**.

**What TS can change that people sometimes assume it cannot:**
- For K > 2 classes, the *across-example* ordering of top-1 confidences. We checked this numerically: input A with logits [5, 0×999] has confidence 0.129 at T = 1 and 0.957 at T = 0.5, while input B with two live classes [0.1, 0] has 0.525 and 0.550. The order flips. Confidence-based error detection, measured for example by AUROC, is therefore not invariant to T in general **[our inference; numeric check in a scratch script]**. For K = 2 the across-example order is preserved, because confidence is monotone in the absolute logit margin **[our inference]**.
- Samples drawn under stochastic decoding, and beam-search rankings **[our inference]**.

---

## 1. Identity & coverage

**Citation.** Chuan Guo\*, Geoff Pleiss\*, Yu Sun\*, Kilian Q. Weinberger. "On Calibration of Modern Neural Networks." *Proceedings of the 34th International Conference on Machine Learning*, Sydney, PMLR 70:1321–1330, 2017; editors Doina Precup and Yee Whye Teh (PMLR page). \*Equal contribution, alphabetical order; all authors at Cornell University (p. 1 footnote) **[author result]**. Funding: NSF grants III-1618134, III-1526012 and IIS-1149882, the Bill and Melinda Gates Foundation, and the Office of Naval Research (p. 8) **[author result]**.

**Version and files.**

| File | Source | Identity |
|---|---|---|
| `paper.pdf` | https://proceedings.mlr.press/v70/guo17a/guo17a.pdf | 10 pages; sha256 df7c93f97204f8a3c2b10f6d5bf5265baac25f00c1ae3b473a3e1dbc102dacb2; PDF CreationDate 2017-06-15 |
| `supplement.pdf` | https://proceedings.mlr.press/v70/guo17a/guo17a-supp.pdf (the "Supplementary PDF" link on https://proceedings.mlr.press/v70/guo17a.html) | 4 pages, S1–S4; sha256 db84c136589971e541211670d576f756c3e05e31ee91dd885a5a78269b798625; fetched 2026-10-23 |
| `paper.txt`, `supplement.txt` | `pdftotext` of the above | extraction scrambles figures, tables and equations; every number used here was checked against the page images |

The arXiv version was not consulted, so these notes describe the PMLR camera-ready version only. Date checked: 2026-10-23.

**Coverage checklist.** Every item was read in full, with figures and tables checked visually against the PDF.

| Item | Location | Read |
|---|---|---|
| Abstract | p. 1 | ✓ |
| 1 Introduction (incl. Fig. 1) | pp. 1–2 | ✓ |
| 2 Definitions: eq. 1, reliability diagrams, acc/conf, ECE eqs. 2–3, MCE eqs. 4–5, NLL eq. 6 | pp. 2–3 | ✓ |
| 3 Observing Miscalibration: capacity, Batch Norm, weight decay, NLL (Figs. 2–3) | pp. 3–4 | ✓ |
| 4 Calibration Methods: 4.1 binary (histogram binning eq. 7, isotonic, BBQ, Platt), 4.2 multiclass (binning extension, matrix/vector eq. 8, temperature eq. 9), 4.3 related work | pp. 4–7 | ✓ |
| Footnotes 1–3 | pp. 5–6 | ✓ |
| Table 1 (ECE) | p. 6 | ✓ (visual) |
| 5 Results: datasets, models, calibration results, reliability diagrams (Fig. 4), computation time, ease of implementation | pp. 7–8 | ✓ |
| 6 Conclusion; Acknowledgments | p. 8 | ✓ |
| References | pp. 9–10 | ✓ (scanned for identity; not followed) |
| S1 ECE as a Riemann–Stieltjes sum | supp p. 1 | ✓ |
| S2 TS as entropy maximisation (Claim 1 + proof), Fig. S1 | supp pp. 1–2 | ✓ (proof re-derived) |
| S3 Tables S1 (MCE), S2 (test error), S3 (NLL) | supp pp. 2–3 | ✓ (visual) |
| S4 Figs. S2 (CIFAR-10), S3 (SST-FG), S4 (SST-BIN) | supp pp. 2, 4 | ✓ |

**Missing material.** None of the text is missing. No code is linked from the paper, the supplement or the PMLR page; trained models and fitted calibrators (including the fitted T values) are not released. Training hyperparameters are deferred to the original architecture papers ("as described in each paper", p. 7), which are not in this folder **[author result]**.

**Extraction damage to know about.**
- `paper.txt` interleaves Figure 1's axis labels with the abstract (txt lines 23–87) and flattens Table 1 into column runs (txt lines 594–800).
- `supplement.txt` scrambles the S1 integral, Claim 1 and all three supplementary tables. In the matrix-scaling column it drops the "-" cells for ImageNet, which shifts the values if read naively.
- The PDF's last page carries a stray running header, "Supplementary Materials: On Calibration of Modern Neural Networks", with no supplement content beneath it.

---

## 2. Question & contribution

**Problem.** Supervised multiclass classification, where a network outputs a prediction Ŷ and a confidence P̂. The question is whether P̂ equals the probability that Ŷ is correct (p. 2, eq. 1) **[author result]**. The motivation is decision pipelines (self-driving, medical hand-off to humans), interpretability, and combining network outputs with other probabilistic models (p. 1) **[author interpretation]**.

**Claimed contributions** (p. 2, last paragraph of Sec. 1) **[author result]**:
1. On several vision and NLP tasks, networks produce confidences that "cannot represent true probabilities".
2. "Insight and intuition into network training and architectural trends that may cause miscalibration."
3. A comparison of post-processing calibration methods on state-of-the-art networks, plus the authors' own extensions. These are matrix, vector and temperature scaling as multiclass Platt variants, and one-vs-all extensions of the binning methods. TS turns out to be "often the most effective".

**Prior knowledge as the paper states it.**
- Niculescu-Mizil & Caruana (2005) "showed that neural networks typically produce well-calibrated probabilities on binary classification tasks" (p. 2) **[author result, as citation]**.
- Histogram binning, isotonic regression, BBQ and Platt scaling already existed (Sec. 4.1, p. 5).
- Temperature appears in knowledge distillation and statistical mechanics, but the authors are "not aware of any prior use in the context of calibrating probabilistic models" (p. 6) **[author result]**.

**Strongest claim the evidence supports** **[our inference]**. The tests cover 19 (model, dataset) rows. Each row is one trained network with an i.i.d. held-out validation set; the domains are image classification (K = 10 to 1000) and document classification (K = 2 to 20). On these, a single scalar T fitted by validation NLL:
- lowers test NLL in 19/19 rows and test ECE in 18/19;
- leaves predictions unchanged;
- is the best of seven methods, or within 0.61 ECE points of the best, on all 15 vision rows.

**The comparison that establishes it.** Table 1 (ECE, p. 6) compares TS against histogram binning, isotonic regression, BBQ, vector scaling and matrix scaling, with Table S2 (error) and Table S3 (NLL) on supp p. 3.

**Weaker claims, rung 1–2 on the evidence ladder.** That miscalibration is new ("modern") and driven by capacity, Batch Norm and reduced weight decay (Sec. 3), and that miscalibration is "intrinsically low dimensional" (p. 7). Assessed in §6–8.

---

## 3. Operational definitions (as used in this paper)

- **Confidence P̂.** The network's "probability of correctness" for its predicted class (p. 2). In the multiclass case it is the maximum softmax probability, p̂_i = max_k σ_SM(z_i)^(k) (p. 5) **[author result]**. Only the top-1 probability is scored; the rest of the distribution enters only through NLL **[our inference]**.
- **Perfect calibration.** P(Ŷ = Y | P̂ = p) = p for all p ∈ [0, 1], with the probability taken over the joint data distribution (eq. 1, p. 2). The authors note that it is unattainable in practice and cannot be computed from finitely many samples, because P̂ is continuous (p. 2) **[author result]**.
- **Miscalibration / overconfidence.** Measured by the gap between bin accuracy and bin confidence (ECE, MCE, reliability diagrams) and indirectly by NLL (pp. 2–4). Overconfidence means average confidence above accuracy (Fig. 1 description, p. 2) **[author result]**.
- **"Modern" networks.** Architectures and training practice of 2015–2017: ResNets, ResNets with stochastic depth (SD), Wide ResNets, DenseNets, Batch Norm, and little weight decay (pp. 1, 3–4, 7). The contrast is LeNet-5 ("LeNet (1998)" in Fig. 1), which the authors train themselves on CIFAR **[author result]**.
- **Capacity.** Depth (number of layers) and width (filters per layer) (p. 3) **[author result]**.
- **Regularization.** Weight decay (L2). Batch Norm is discussed as having "apparent regularization effects" (p. 4) **[author result / author interpretation]**.
- **"Intrinsically low dimensional" miscalibration.** The authors' reading of two facts: TS matches or beats the more general vector and matrix scaling, and the learned vector-scaling weights are "nearly constant" (p. 7) **[author interpretation; the vector weights are not shown]**.
- **Temperature T.** The scalar divisor of the logits. T > 1 "softens" the softmax and raises entropy; T → ∞ gives 1/K; T = 1 recovers the original; T → 0 gives a point mass (p. 6) **[author result]**.
- **Template terms.** *Persona, trait, alignment, transfer, knowledge, similarity* and *faithfulness* do not occur in this paper. The nearest analogue to *scope* is the assumption that "the training, validation, and test sets are drawn from the same distribution" (p. 4). No result covers distribution shift **[author result; our inference]**.

---

## 4. Experimental reconstruction

**Datasets and splits** (train / validation / test; p. 7) **[author result]**:

| Dataset | Classes | Train | Val | Test | Notes |
|---|---|---|---|---|---|
| Caltech-UCSD Birds | 200 | 5,994 | 2,897 | 2,897 | fine-tuned from ImageNet-pretrained net |
| Stanford Cars | 196 | 8,041 | 4,020 | 4,020 | fine-tuned from ImageNet-pretrained net |
| ImageNet 2012 | 1000 | 1.3M | 25,000 | 25,000 | |
| CIFAR-10 / CIFAR-100 | 10 / 100 | 45,000 | 5,000 | 10,000 | 32×32 colour images |
| SVHN | 10 (digits) | 604,388 | 6,000 | 26,032 | |
| 20 News | 20 | 9,034 | 2,259 | 7,528 | news articles |
| Reuters | 8 | 4,388 | 1,097 | 2,189 | news articles |
| SST binary | 2 | 6,920 | 872 | 1,821 | splits per Tai et al. (2015) |
| SST fine-grained | 5 | **544** | 1,101 | 2,210 | **[unresolved]** see note |

The SVHN class count is not stated in the paper; "10 (digits)" is our inference from "house numbers".

*SST fine-grained note* **[unresolved]**. The paper's 544 training documents look anomalous: its fine-grained validation and test sets (1,101 / 2,210) are larger than the binary ones (872 / 1,821), yet the training set would be about 13× smaller. This is possibly a typo; it is not checkable from our folder.

How the validation/test splits were made for Birds, Cars, ImageNet and SVHN is not described. In particular, it is not said whether ImageNet's 25,000/25,000 split came from the official validation set **[unresolved]**.

**Models and training** **[author result, p. 7]**:
- **Vision:** ResNet-50 (Birds, Cars), ResNet-110, ResNet-110 (SD), Wide ResNet-32, DenseNet-40, LeNet-5 (CIFAR-10/100), DenseNet-161 and ResNet-152 (ImageNet), ResNet-152 (SD) (SVHN). "We use the data preprocessing, training procedures, and hyperparameters as described in each paper." Birds and Cars networks are fine-tuned from ImageNet-pretrained networks. These are the only fine-tuned models in the paper.
- **NLP:** Deep Averaging Networks with 3 feed-forward layers and Batch Norm (20 News, Reuters), using the original paper's optimisation hyperparameters. TreeLSTMs (SST) using "the default settings in the authors' code".
- **Section 3 sweeps** (Fig. 2, p. 3; text pp. 3–4), all on CIFAR-100:
  - depth: ResNet with 64 filters per layer;
  - width: ResNet-14, varying filters per layer;
  - Batch Norm: 6-layer ConvNet with and without BN;
  - weight decay: ResNet-110, with data augmentation and BN as the only other regularisation.
- **Training curve** (Fig. 3, p. 4): ResNet-110 (SD), CIFAR-100, about 500 epochs, learning rate dropped 10× at epochs 250 and 375.

**Absent details** (recorded as absent, not inferred) **[unresolved]**:
- Seeds, number of training runs, and any variance. Every number is one run.
- Checkpoint selection for the Table 1 models (final epoch vs early stopping), and whether the validation set used to fit calibrators was also used for early stopping or hyperparameter tuning. The paper says it "can be" the same set (p. 4) but not whether it was.
- Histogram binning: number of bins M and whether bins are equal-width or equal-mass, for the experiments.
- Isotonic regression: fitting algorithm.
- BBQ: Beta prior hyperparameters and the exact space of binning schemes.
- Vector/matrix scaling: the regularisation used ("even when applying regularization", p. 8 does not name it), and the optimiser for matrix scaling.
- **The fitted T values for every Table 1 model.** The only T values shown are in Fig. S1, for one CIFAR-100 run.
- Whether Fig. 2 plots test or training error. The text says "training error" for the weight-decay panel (p. 4); the legends say "Error". Also the bin count used for ECE in Fig. 2.
- Hardware and absolute timings.
- Log base for NLL.

**Evaluation settings** **[author result]**:
- All calibrators are post-processing steps fit on the hold-out validation set, with network parameters fixed (pp. 4–5).
- ECE and MCE use M = 15 equal-width bins (Table 1 and Table S1 captions).
- Metrics are reported on the test set (Tables 1, S1–S3).
- TS is implemented in Torch7 by inserting `nn.MulConstant` (parameter 1/T) between logits and softmax. T = 1 during training; T is then optimised on the validation set (p. 8).
- The optimiser for T is conjugate gradient, about 10 iterations; "even a naive line-search" is faster than any other method (p. 8).

---

## 5. Method mechanics

### 5.1 Calibration metrics

**Reliability diagram** (p. 2) **[author result]**. Plot "expected sample accuracy as a function of confidence"; a perfectly calibrated model plots the identity. Predictions are grouped into M equal-width bins, with B_m the indices whose confidence falls in I_m = ((m−1)/M, m/M]:

$$\mathrm{acc}(B_m)=\frac{1}{|B_m|}\sum_{i\in B_m}\mathbf 1(\hat y_i=y_i),\qquad \mathrm{conf}(B_m)=\frac{1}{|B_m|}\sum_{i\in B_m}\hat p_i .$$

- acc(B_m) is "an unbiased and consistent estimator of P(Ŷ = Y | P̂ ∈ I_m)" (p. 2). Perfect calibration means acc(B_m) = conf(B_m) for all m.
- Caveat stated by the authors: reliability diagrams "do not display the proportion of samples in a given bin, and thus cannot be used to estimate how many samples are calibrated" (p. 2; repeated in S4). Fig. 1 adds confidence histograms for this reason.
- The paper's reliability diagrams show 10 bars (Figs. 1, 4, S2–S4), while the ECE printed on them matches the M = 15 values in Table 1. The plotted bins and the printed ECE may therefore use different M **[our inference: visual count; unresolved]**.

**Expected Calibration Error** (p. 2–3, eqs. 2–3; Naeini et al. 2015) **[author result]**. The population quantity and its binned estimate:

$$\mathbb E_{\hat P}\Big[\big|\mathbb P(\hat Y=Y\mid \hat P=p)-p\big|\Big] \quad (2),\qquad \mathrm{ECE}=\sum_{m=1}^{M}\frac{|B_m|}{n}\,\big|\mathrm{acc}(B_m)-\mathrm{conf}(B_m)\big| \quad (3).$$

ECE is the primary metric. S1 (supp p. 1) writes eq. 2 as a Riemann–Stieltjes integral, ∫₀¹ |P(Ŷ=Y | P̂=p) − p| dF_P̂(p), and approximates it by the M-term sum Σ_m |P(Ŷ=Y | P̂=p_m) − p_m| · P(P̂ ∈ I_m). It then argues that |acc(B_m) − p̂(B_m)| approximates each term "for n large", so ECE "converges to the M-term Riemann–Stieltjes sum" **[author result]**.

*Our reading* **[our inference]**:
- This is convergence to a fixed-M approximation, not to eq. 2 itself. The binning error does not vanish as n grows unless M grows too.
- No confidence intervals are given anywhere.
- ECE uses only top-1 confidence.
- A model that outputs the same confidence (its overall accuracy) for every input has ECE ≈ 0 while being useless for ranking. The paper does not discuss this.

**Maximum Calibration Error** (p. 3, eqs. 4–5) **[author result]**:

$$\max_{p\in[0,1]}\big|\mathbb P(\hat Y=Y\mid\hat P=p)-p\big| \quad (4),\qquad \mathrm{MCE}=\max_{m\in\{1..M\}}\big|\mathrm{acc}(B_m)-\mathrm{conf}(B_m)\big| \quad (5).$$

MCE is meant for high-risk settings. The authors' own verdict, in the Table S1 caption (supp p. 2): "MCE seems very sensitive to the binning scheme and is less suited for small test sets."

**Negative log-likelihood** (p. 3, eq. 6) **[author result]**:

$$\mathcal L=-\sum_{i=1}^{n}\log\hat\pi(y_i\mid \mathbf x_i).$$

- Also called cross-entropy loss. In expectation it is minimised iff π̂(Y|X) recovers the true π(Y|X) (p. 3, citing Friedman et al. 2001). It "can be used to indirectly measure model calibration" (p. 4).
- Eq. 6 is a sum, but Table S3's values (e.g. 0.0842 for SVHN with 26,032 test images) can only be per-example means. Table S3's "(%)" unit label is also wrong for NLL **[our inference]**.

### 5.2 Binary calibration methods (Sec. 4.1, p. 5)

Setting: Y ∈ {0,1}. The model outputs p̂_i = σ(z_i) for the positive class, with z_i ∈ ℝ the logit. Goal: a calibrated q̂_i from y_i, p̂_i and z_i (p. 5) **[author result]**.

**Histogram binning** (Zadrozny & Elkan 2001). Choose bin boundaries 0 = a₁ ≤ … ≤ a_{M+1} = 1, either equal-length or equal-count. Assign each bin a score θ_m chosen to minimise

$$\min_{\theta_1..\theta_M}\sum_{m=1}^{M}\sum_{i=1}^{n}\mathbf 1(a_m\le\hat p_i<a_{m+1})(\theta_m-y_i)^2 \quad (7).$$

The solution is the fraction of positives in each bin; at test time q̂ = θ_m for the bin that p̂ falls in **[author result]**. Eq. 7's indicator uses [a_m, a_{m+1}) while the text defines bins as (a_m, a_{m+1}], a harmless inconsistency **[our inference]**.

**Isotonic regression** (Zadrozny & Elkan 2002), "arguably the most common non-parametric calibration method". It learns a piecewise-constant non-decreasing f with q̂ = f(p̂), minimising Σ(f(p̂_i) − y_i)². Equivalently, eq. 7 is optimised jointly over the θ's and the boundaries a, subject to 0 = a₁ ≤ … ≤ a_{M+1} = 1 and θ₁ ≤ … ≤ θ_M. It is "a strict generalization of histogram binning" (p. 5) **[author result]**.

**Bayesian Binning into Quantiles, BBQ** (Naeini et al. 2015). A binning scheme s = (M, 𝓘) is a bin count plus a partition of [0,1]. BBQ averages over the space 𝓢 of all schemes for validation set D:

$$\mathbb P(\hat q_{te}\mid\hat p_{te},D)=\sum_{s\in\mathcal S}\mathbb P(\hat q_{te}\mid\hat p_{te},S{=}s,D)\,\mathbb P(S{=}s\mid D),\qquad \mathbb P(S{=}s\mid D)=\frac{\mathbb P(D\mid S{=}s)}{\sum_{s'}\mathbb P(D\mid S{=}s')}.$$

The prior over schemes is uniform. Each scheme's θ₁..θ_M are treated as independent binomial parameters with a Beta prior, which gives a closed-form marginal likelihood. 𝓢 is finite because D is finite (footnote 2) **[author result]**.

**Platt scaling** (Platt et al. 1999), the parametric method. It is logistic regression on the logit: q̂_i = σ(a z_i + b), with scalars a, b fitted by NLL on the validation set and the network frozen (p. 5) **[author result]**. In the binary case, a ≠ 1 or b ≠ 0 can move the decision threshold **[our inference]**.

### 5.3 Multiclass methods (Sec. 4.2, pp. 5–6)

Logit vector z_i ∈ ℝ^K, ŷ_i = argmax_k z_i^(k), softmax σ_SM(z)^(k) = exp(z^(k)) / Σ_j exp(z^(j)), and p̂_i = max_k σ_SM(z_i)^(k). The goal is a calibrated q̂_i and a "(possibly new)" prediction ŷ'_i (p. 5) **[author result]**.

**One-vs-all extension of binning** (histogram, isotonic, BBQ) **[author result]**. Fit K binary calibrators, each with label 1(y_i = k) and score σ_SM(z_i)^(k). At test time this gives an unnormalised vector [q̂^(1), …, q̂^(K)]. The new prediction is its argmax; the new confidence is its max divided by Σ_k q̂^(k) (p. 6). Because the calibrators are fit separately per class, the argmax can change, and so can accuracy.

**Matrix scaling** **[author result]**:

$$\hat q_i=\max_k\sigma_{SM}(\mathbf W\mathbf z_i+\mathbf b)^{(k)},\qquad \hat y'_i=\arg\max_k(\mathbf W\mathbf z_i+\mathbf b)^{(k)} \quad (8),$$

with W and b fitted by validation NLL. The parameter count grows quadratically in K (p. 6).

**Vector scaling.** Matrix scaling with W restricted to a diagonal (p. 6) **[author result]**. With b kept, that is 2K parameters, and it can change predictions whenever the diagonal is not constant or b ≠ 0 **[our inference]**.

**Temperature scaling** **[author result]**:

$$\hat q_i=\max_k\sigma_{SM}(\mathbf z_i/T)^{(k)},\qquad T>0 \quad (9).$$

- One parameter for all classes, fitted by NLL on the validation set.
- "Because the parameter T does not change the maximum of the softmax function, the class prediction ŷ'_i remains unchanged. In other words, temperature scaling does not affect the model's accuracy" (p. 6).
- Footnote 3: T is parameterised as a divisor (multiplier 1/T) "to highlight the connection with prior works".
- The fit is "a one-dimensional convex optimization problem" (p. 8). This holds in β = 1/T, where the NLL is a log-sum-exp of affine functions minus an affine term. As a function of T it is quasi-convex with a unique minimiser **[our inference]**.

**TS as entropy maximisation** (S2, Claim 1, supp p. 1) **[author result]**. Given logits z_1..z_n and labels y_1..y_n, TS is "the unique solution" q to

$$\max_q\; -\sum_{i=1}^{n}\sum_{k=1}^{K}q(\mathbf z_i)^{(k)}\log q(\mathbf z_i)^{(k)}\quad\text{s.t.}\quad q(\mathbf z_i)^{(k)}\ge0,\;\;\sum_k q(\mathbf z_i)^{(k)}=1,\;\;\sum_{i}z_i^{(y_i)}=\sum_i\sum_k z_i^{(k)}q(\mathbf z_i)^{(k)} .$$

- The last constraint says "the average true class logit is equal to the average weighted logit".
- The Lagrangian solution is q(z_i)^(k) = e^{λz_i^(k)} / Σ_j e^{λz_i^(j)}, i.e. T = 1/λ.
- The proof writes ∂L/∂q = −nK − log q + λz + β_i, but the derivative of −Σ q log q is −log q − 1. The constant is absorbed into β_i, so the conclusion stands **[our inference]**.
- The proof does not show λ > 0, i.e. T > 0 **[our inference]**.
- The claim explains *what family* TS is (max-entropy under a logit-moment constraint). It does not explain *why* networks need it **[our inference]**.

### 5.4 What each method fits, on what data, and what it can change

**[author result unless marked]**

| Method | Parameters | Objective | Data | Can change ŷ? | Notes |
|---|---|---|---|---|---|
| Histogram binning (OvA) | M per class (bin values; boundaries fixed) | squared loss (eq. 7) | validation | yes | accuracy drops up to +32.5 pp error (Birds) and +25.8 pp (ImageNet) (Table S2) **[our inference: difference]** |
| Isotonic regression (OvA) | bins + monotone values per class | squared loss with monotone constraint | validation | yes | error change −0.95 to +0.85 pp (Table S2) **[our inference]** |
| BBQ (OvA) | Bayesian average over schemes | marginal likelihood, uniform prior over schemes, Beta prior | validation | yes | error +25.0 / +25.3 pp on ImageNet, +15.2 pp on Birds (Table S2) **[our inference]** |
| Platt (binary) | a, b | NLL | validation, net frozen | threshold can move **[our inference]** | |
| Matrix scaling | K² + K | NLL | validation | yes | fails to converge on ImageNet; error +7.5 to +10.9 pp on CIFAR-100 (Table S2) |
| Vector scaling | 2K **[our inference]** | NLL | validation | yes | test NLL within ±0.01 of TS in 18/19 rows (Birds +0.023) (Table S3) **[our inference]** |
| Temperature scaling | 1 | NLL | validation | **no** | test error identical in 19/19 rows (Table S2) |

**Properties of TS derived from the paper's own equations.** All **[our inference]**; checked numerically on synthetic data in a scratch script.

1. **Within-input ranking is invariant.** z ↦ z/T with T > 0 is strictly increasing, so the full class order, top-k membership and true-class rank are unchanged. This is stronger than the paper's "argmax unchanged".
2. **Entropy is non-decreasing in T for every input.** With β = 1/T, dH/dβ = −β·Var_q(z) ≤ 0.
3. **NLL minus entropy equals β·dNLL/dβ.** Let NLL(β) = (1/n)Σ_i[log Σ_k e^{βz_ik} − βz_{i,y_i}] and H(β) = (1/n)Σ_i[log Σ_k e^{βz_ik} − β E_{q_i}z_i]. Then NLL(β) − H(β) = β·(1/n)Σ_i(E_{q_i}z_i − z_{i,y_i}) = β·dNLL/dβ. Two consequences:
   - (a) At the NLL optimum, mean NLL = mean entropy. This is the authors' Fig. S1 statement that "post-calibration entropy and NLL on the validation set coincide (which can be derived from the gradient optimality condition of T)", and it is identical to Claim 1's third constraint.
   - (b) At T = 1, the sign of (NLL − H) gives the direction of T*. If held-out NLL exceeds mean predictive entropy, the model is overconfident and T* > 1; if NLL is below entropy, T* < 1. This is a one-line diagnostic needing only logits and labels.
   - Synthetic check: logits rescaled by known factors 3.0 and 0.4 gave fitted T* = 3.03 and 0.394, and NLL − H matched β·dNLL/dβ to 4 decimals.
4. **Across-input ordering of top-1 confidence is not invariant for K > 2.** See the numeric counterexample in the answer section above. It is invariant for K = 2.

---

## 6. Evidence table

All rows are one trained network per (model, dataset) with one validation/test split. No seeds and no uncertainty are reported anywhere in the paper.

| # | Claim | Decisive comparison | Result | Unit of replication | Denominator | Uncertainty | Source | Remaining alternative |
|---|---|---|---|---|---|---|---|---|
| 1 | Modern nets are miscalibrated (overconfident) **[author result]**; "unlike those from a decade ago" **[author interpretation]** | LeNet-5 vs ResNet-110 on CIFAR-100; uncalibrated column across 19 rows | Fig. 1: LeNet error 44.9, average confidence and accuracy within ≈0.05, ECE 4.85% (Table 1). ResNet error 30.6, ≈0.62 of samples in the top 0.95–1.0 confidence bin, average confidence ≈0.89 vs accuracy ≈0.69 **[≈ visual]**. Uncalibrated ECE 0.44–16.53%, "typically between 4 to 10%" (p. 7) | 1 run per model | CIFAR test 10,000 | none | Fig. 1 p. 1; Table 1 p. 6 | On CIFAR-10, LeNet-5 ECE 3.02% vs DenseNet-40 3.28%, so the old/new contrast in raw ECE holds on CIFAR-100, not CIFAR-10 (ECE/error ratio 0.19 vs 0.55–0.74) **[our inference]**. Fig. 1's ResNet (error 30.6) is not the Table S2 ResNet-110 (27.83%) **[unresolved]** |
| 2 | ECE grows with depth and width **[author result]**; because higher capacity lowers training NLL by raising confidence **[author interpretation]** | Fig. 2 panels 1–2 | Depth: error ≈0.42→0.30, ECE ≈0.08→≈0.20 by depth ≈40, then flat ≈0.18–0.20 to depth 110. Width: error ≈0.62→0.27, ECE ≈0.04→≈0.17 at ≈100–120 filters, ≈0.15 at 256 **[≈ visual]** | 1 run per point | CIFAR-100 (test presumably) | none | Fig. 2 p. 3; text p. 3 | Error falls as ECE rises, so "capacity" and "accuracy level" are confounded. The training-NLL mechanism is not measured in this sweep **[our inference]** |
| 3 | Batch Norm increases miscalibration **[author result]** "regardless of the hyperparameters" **[author result, data not shown]** | Fig. 2 panel 3 | 6-layer ConvNet: without BN error ≈0.40, ECE ≈0.14; with BN error ≈0.35, ECE ≈0.20 **[≈ visual]** | one pair | CIFAR-100 | none | Fig. 2 p. 3; p. 4 | Accuracy changes too. The hyperparameter robustness claim has no shown data |
| 4 | Less weight decay worsens calibration; calibration keeps improving past the accuracy-optimal weight decay **[author result]** | Fig. 2 panel 4 | ResNet-110: error U-shaped, ≈0.33 at 10⁻⁵, min ≈0.26 near 5×10⁻⁴, ≈0.46 at 10⁻². ECE falls ≈0.24→≈0.02 near 5×10⁻³ then ticks up to ≈0.08 at 10⁻² ("may be an artifact", p. 4) **[≈ visual]** | 1 run per point | CIFAR-100 | none | Fig. 2 p. 3; p. 4 | The cleanest dissociation of ECE from error in the paper **[our inference]**. Text calls the curve "training error" while the legend says "Error" **[unresolved]** |
| 5 | Networks overfit NLL without overfitting 0/1 loss, and NLL overfitting helps accuracy **[author result / author interpretation]** | Fig. 3 test error vs test NLL over training | After the epoch-250 LR drop, test NLL (scaled) rises from ≈24.7 to ≈30 while error stays ≈25.5–27, and error drops to ≈25 after the epoch-375 drop. Text: "test error drops from 29% to 27% in the region where NLL overfits" (p. 4). The figure shows ≈27→≈25 **[≈ visual]** | one training run | CIFAR-100 test | none | Fig. 3 p. 4 | **[unresolved]** text/figure mismatch. Over epochs ≈255–370 error and NLL both worsen; the error gain coincides with the second LR drop **[our inference]** |
| 6 | TS is the most effective method; "outperforms all other methods on the vision tasks" **[author interpretation]** | Table 1, TS vs 5 other methods | TS lowest ECE in 10/15 vision rows. Losses: Cars (HB 1.74 vs TS 2.35), CIFAR-10 ResNet-110 (BBQ 0.54 vs 0.83), CIFAR-100 ResNet-110 SD (vector 0.90 vs 0.96), CIFAR-100 DenseNet-40 (vector 1.09 vs 1.18), SVHN (HB 0.14 vs 0.17). TS/uncalibrated ECE ratio 0.08–0.55 on vision (median 0.18) **[our inference: count]** | 1 net × 1 split per row | test sets 2,897–26,032 | none | Table 1 p. 6 | ECE differences of hundredths of a point have no stated noise floor **[our inference]** |
| 7 | TS "performs comparably" on NLP **[author interpretation]** | Table 1 NLP rows | TS best in 0/4. TS vs best: 20 News 4.11 vs 3.60 (HB); Reuters 0.91 vs 0.66 (vector); SST-bin 1.84 vs 1.65 (isotonic); SST-FG 2.56 vs 1.65 (isotonic) | 1 net per row | 1,821–7,528 | none | Table 1 p. 6 | "Comparable" is a judgment; on SST-FG TS's ECE is 55% higher than isotonic's **[our inference]** |
| 8 | TS does not change accuracy **[author result]** | Table S2 | TS error = uncalibrated in 19/19 rows (caption: "exactly the same") | n/a (true by construction) | all test sets | n/a | p. 6; Table S2 supp p. 3 | none |
| 9 | Miscalibration is "intrinsically low dimensional"; vector scaling "recovers essentially the same solution" as TS **[author interpretation]** | TS vs vector/matrix in Tables 1, S3 | Vector−TS ECE difference −0.25 to +1.15 points; test NLL within ±0.01 in 18/19 rows (Birds +0.023). Matrix scaling gives the best NLL in 2 CIFAR-10 rows (ResNet-110 0.2048 vs TS 0.2102; WRN-32 0.2229 vs 0.2283). "Learned vector has nearly constant entries" is not shown **[our inference: count]** | per row | — | none | p. 7; Tables 1, S3 | A small validation set penalises extra parameters (the authors' own explanation for matrix scaling, p. 8), so TS winning could be variance reduction, not low-dimensional miscalibration. ECE also only sees top-1 **[our inference]** |
| 10 | Matrix scaling overfits with many classes **[author result / author interpretation]** | Table 1 | Birds 21.13%, Cars 10.5%, CIFAR-100 20.09–25.49% ECE (worse than uncalibrated); ImageNet "fails to converge" ("-") | per row | — | none | p. 7–8; Table 1 | — |
| 11 | Binning methods change predictions, which hurts accuracy **[author result]** | Table S2 | Error change vs uncalibrated: HB −0.05 to +32.48 pp (Birds), +25.75/+25.79 pp ImageNet; BBQ up to +25.29 pp; isotonic −0.95 to +0.85 pp **[our inference: differences]** | per row | — | none | p. 8; Table S2 | — |
| 12 | Histogram binning "typically outperforms" isotonic and BBQ **[author result]** | Table 1 | Best of the three binning methods by ECE: HB 11/19, BBQ 5/19, isotonic 3/19 **[our inference: count]** | per row | — | none | p. 8 | — |
| 13 | TS improves NLL; "NLL roughly follows the trends of ECE" **[author result]** | Table S3 | TS NLL < uncalibrated in 19/19 rows; TS best NLL in 8/15 vision rows (vector 5, matrix 2) and in 1/4 NLP rows (a three-way tie on SST-bin), with vector best on all 4 NLP rows (including the tie) **[our inference: count]** | per row | — | none | Table S3 supp p. 3 | TS is fit to validation NLL, so improving test NLL is the expected i.i.d. outcome **[our inference]** |
| 14 | MCE results **[author result]** | Table S1 | TS lowers MCE in 16/19 rows; raises it on ImageNet ResNet-152 (12.2→12.29), Reuters (14.01→25.46), SST-FG (27.85→44.75). BBQ hits 72.64% and 82.35% on CIFAR-10 rows. Authors: MCE "very sensitive to the binning scheme" **[our inference: count]** | per row | — | none | Table S1 supp p. 2 | Duplicate ImageNet values (TS 12.29/12.29; vector 9.61/9.61) may be transcription errors **[unresolved]** |
| 15 | Optimal T rises during training as pre-calibration entropy falls; this "explains the model's overconfidence" **[author result / author interpretation]** | Fig. S1 | T* ≈1.05 at start, ≈1.3–1.45 for epochs ≈20–250, ≈1.9 by ≈320, ≈2.1–2.2 by 500. Post-calibration entropy = NLL ≈1.25–1.3 before epoch 250, ≈0.87 at 500 **[≈ visual]** | one run (model not named) | validation set | none | supp p. 2 | Internally inconsistent before epoch 250: see §7 **[unresolved]** |
| 16 | TS is the fastest and simplest method **[author result]** | Sec. 5 timing | TS ≈10 conjugate-gradient iterations; HB and isotonic ~10× slower; vector scaling on CIFAR-100 ≥100× slower; BBQ ~1000× slower | — | — | no absolute times | p. 8 | — |

---

## 7. Controls & failures

**Controls and checks present** **[author result]**:
- An old-architecture reference (LeNet-5) on CIFAR-10/100 (Fig. 1; Table 1).
- A within-paper comparison of six post-hoc calibrators against the uncalibrated model on 19 rows, with three metrics (ECE, MCE, NLL) plus test error.
- Separate validation (fit) and test (evaluate) sets for every calibrator (p. 4, p. 7).
- Confidence histograms alongside reliability diagrams, to show bin occupancy (Fig. 1).

**Failures and negative results reported** **[author result]**:
- **Reuters:** no method except vector scaling improves calibration. The model is already at ECE 0.85% and TS gives 0.91% (p. 7; Table 1). The authors suggest the split or binning may affect the measurement (p. 7).
- **NLP generally:** TS never wins on ECE (Table 1).
- **Matrix scaling:** fails to converge on ImageNet and is worse than uncalibrated on Birds, Cars and CIFAR-100 (p. 8; Table 1).
- **Binning methods:** hurt accuracy, by up to 32.5 points of error (Table S2) **[our inference: difference]**.
- **MCE:** unstable; TS raises it on 3 rows (Table S1).
- **Weight-decay sweep:** the uptick at 10⁻² is flagged as a possible optimisation artifact (p. 4).

**Residual miscalibration after TS, visible in figures** **[our inference: visual reads]**:
- Fig. 4 (CIFAR-100 ResNet-110 SD, ECE 12.67 → 0.96): bins lie close to the diagonal.
- Fig. S2 (CIFAR-10, 4.12 → 0.60): bins lie close to the diagonal.
- Fig. S3 (SST-FG, 6.71 → 2.56): TS leaves the 0.9–1.0 bin at accuracy ≈0.5 and the 0.7–0.9 bins underconfident. One scalar trades over- against under-confidence here.
- Fig. S4 (SST-bin, 6.63 → 1.84): no bins below confidence 0.5 (binary), and the lowest occupied bin is overconfident.

**Controls not run.** All **[our inference]**:
- No repeated training runs, seeds or bootstrap intervals on ECE/MCE/NLL. Differences of a few hundredths of an ECE point (e.g. TS 0.96 vs vector 0.90) have no noise floor.
- No sensitivity analysis of ECE to M or to equal-width vs equal-mass bins, though the authors suspect binning effects on Reuters and MCE.
- No distribution-shift test: calibrators fit on one distribution and evaluated on another. The paper assumes i.i.d. (p. 4).
- No per-class or per-subgroup calibration analysis.
- No variable in Sec. 3 is manipulated with others held at matched accuracy, so capacity, BN and weight-decay effects are not separated from the accuracy level each setting reaches.
- No training-set NLL or accuracy curves for the capacity sweep, which the proposed mechanism needs.
- No logit-norm or margin analysis.
- No comparison with training-time remedies (the related-work section names ensembles, confidence penalties and Bayesian or dropout approaches, but none is run).
- The fitted T values for the Table 1 models are not reported.

**Internal inconsistencies** **[unresolved unless marked]**:
1. **Fig. 3 vs text.** The text says test error "drops from 29% to 27%" where NLL overfits (p. 4). The plot shows ≈27% → ≈25% in the shaded region, and Table S2 gives 24.91% final error for ResNet-110 (SD) on CIFAR-100.
2. **Fig. 1's ResNet error (30.6) ≠ Table S2's ResNet-110 CIFAR-100 error (27.83%).** LeNet matches (44.9 vs 44.92%). So Fig. 1's ResNet is likely a different run.
3. **Fig. S1 before epoch ≈250.**
   - Pre-calibration entropy (≈1.6–1.8) sits *above* pre-calibration NLL (≈1.4). By the identity in §5.4, that implies T* < 1.
   - Yet the plotted T* is ≈1.3–1.45, and the post-calibration entropy (≈1.27) is *below* the pre-calibration entropy, which is impossible for T* > 1 because entropy is non-decreasing in T.
   - After epoch ≈270 the curves are consistent (entropy < NLL, T* > 1).
   - Plausible cause: the curves were computed on different data or in different model modes (stochastic depth active, augmentation), but nothing in the paper says so **[our inference]**.
4. **Duplicate captions.** Figs. S3 and S4 share the caption "SST Binary and SST Fine Grained", though S3 is SST-FG and S4 is SST-BIN (panel titles).
5. **Table S3 units.** Labelled "NLL (%)", and its values are per-example means while eq. 6 is a sum **[our inference]**.
6. **Duplicate MCE values.** ImageNet DenseNet-161 and ResNet-152 have identical TS MCE (12.29) and identical vector-scaling MCE (9.61) (Table S1).
7. **SST fine-grained training size.** 544 (p. 7); see §4.
8. **Fig. 2 error type.** "Training error" in the text vs "Error" in the legend for the weight-decay panel (p. 4).
9. **Small slips.** Claim 1's derivative constant (−nK instead of −1) and the bin endpoint convention in eq. 7 (§5) **[our inference; harmless]**.

**Leakage risk** **[our inference]**. The paper says the calibration validation set "can be the same set used for hyperparameter tuning" (p. 4). For Fig. 3, best validation loss and error epochs are marked, so validation data was used for monitoring. If the same set was used to choose checkpoints and fit calibrators, test-set results are still clean, but the "validation" fits are not fully independent of model selection. Not stated.

---

## 8. Interpretation boundary

**What the paper establishes, within its scope**: single-label image and document classifiers, K ≤ 1000, i.i.d. validation and test sets, one run each.
- **Observation, rung 1–2 on the evidence ladder:** many 2015–2017 architectures are overconfident under top-1 ECE, and their test NLL improves with a single post-hoc temperature in every tested row. TS cannot alter predictions, by construction and as measured.
- **Supported comparative claim, rung 3 in-distribution:** among the seven post-hoc options tested, TS is the best or near-best default on vision tasks, at the lowest cost and with no accuracy change. Parameter-rich calibrators (matrix scaling) overfit when K is large relative to validation size. Binning methods can badly hurt accuracy.

**What it does not establish:**
- **Causes of miscalibration (rung 4 not reached).** The Sec. 3 sweeps are correlational: one factor at a time, one dataset, one run each, with accuracy moving alongside ECE in three of four panels. The authors say "we cannot claim causality" (p. 3) and that "it remains future work to understand why these trends affect calibration while improving accuracy" (p. 8) **[author result]**.
  - Their own language elsewhere is stronger. Sec. 3 opens by promising to "identify some recent changes that are responsible for the miscalibration phenomenon" (p. 3), and the conclusion says these factors "have strong effects on network calibration" (p. 8). This is causal phrasing on correlational evidence **[our inference]**.
- **A mechanism.** The "NLL overfitting" account (p. 4) rests on one training curve, and the "capacity lowers training NLL by raising confidence" account (p. 3) is not measured. "Intrinsically low dimensional" rests on TS ≈ vector scaling and on unshown vector weights **[our inference]**.
- **Old vs modern.** The old architecture is LeNet-5 trained by the authors. The 2005 calibration claim concerns binary tasks (p. 2), while the modern experiments are multiclass, so task type is a second difference between the eras compared **[our inference]**.
- **Robustness to shift, to binning choice, or to seeds:** not tested **[our inference]**.

**Separating the kinds of evidence:**
- *Readability/measurement:* ECE, MCE, NLL and reliability diagrams are measurement instruments whose binned versions have untested sensitivity in this paper (the MCE caveat is the authors' own).
- *Predictive information:* confidence scores are not evaluated for ranking quality (no AUROC or selective prediction).
- *Causal contribution:* none established.
- *Training-time effects:* Fig. 3 and Fig. S1 show that, in one run, calibration worsens with continued training after the first LR drop and the optimal T rises. Fig. S1 is partly inconsistent.
- *Deployment monitoring:* only in-distribution.

---

## 9. Connection to our project

The project asks whether a behaviour learned from a story stays with its character, appears under related personas, or changes the default Assistant. Fine-tuned model organisms can show degraded or over/under-confident outputs, and we need to know what such symptoms mean. What follows is analogy and method transfer, not a shared mechanism. The paper studies image and text classifiers trained from scratch or fine-tuned from ImageNet (Birds, Cars), not LM fine-tuning.

**Hypotheses this paper motivates** **[our inference]**:
- **H1, scale-only damage.** Part of an organism's "health" degradation (higher held-out NLL, over-peaked or flattened next-token distributions) is a global change in sharpness. Test: a single T recovers most of the organism-vs-base NLL gap, and top-1 accuracy and greedy outputs are unaffected. The paper's analogue: TS removes most miscalibration without touching accuracy (Tables 1, S2).
- **H2, condition-specific confidence.** If fine-tuning changes the model mainly under character or persona contexts, the optimal T fitted separately on character-context vs default-Assistant held-out data will differ, and one global T will leave condition-specific residual miscalibration. The analogue is Fig. S3, where one scalar leaves structured residuals. A per-condition T shift is a cheap readout of *where* a fine-tune changed output confidence. It is not a mechanism and not evidence about which training data did it.
- **H3, training length and checkpoint choice set confidence.** The analogue: optimal T rose from ≈1.4 to ≈2.2 as training continued past the LR drop (Fig. S1), and the best-validation-loss and best-validation-error checkpoints differed by ≈150 epochs (Fig. 3 shading) **[≈ visual]**. Organism confidence may depend on how many epochs or steps were run and on which checkpoint is used.

**What carries over to LMs and what does not** **[our inference]**:
- **The method carries over unchanged:** divide logits by T and fit T by held-out NLL. For next-token prediction the labels are the held-out tokens themselves. For multiple-choice evaluations, the answer-option logits form a small-K classifier close to the paper's setting.
- **Invariants carry over:**
  - Greedy decoding is unchanged by TS at every step, so any behaviour measured with greedy decoding is TS-invariant.
  - Behaviour rates measured by *sampling at T = 1* can change with scale alone. An organism that only sharpened its distribution can show different sampled behaviour rates with identical greedy behaviour.
  - Report greedy and recalibrated-T sampling side by side before attributing a sampled-rate change to content.
- **The i.i.d. assumption bites.** The paper fits and evaluates T on the same distribution (p. 4). Our conditions (character prompt vs Assistant prompt vs related persona) are deliberately different distributions, so a T fitted on one must not be assumed to calibrate another. Fit per condition, or test transfer explicitly.
- **K and dependence differ.** The paper's largest K is 1000. Its validation sets have 872–25,000 independent examples. LM token positions within a document are not independent, so naive per-token CIs will be too narrow; bootstrap by document.
- **Top-1 ECE is narrow for LMs.** It scores only the argmax token's probability. Report NLL and accuracy alongside it, and prefer answer-level calibration where a correctness label exists.
- **Vector scaling over a vocabulary** is a per-token bias-and-scale model. The paper's evidence that it adds nothing over T covers K ≤ 1000 with small validation sets only. For LMs, data volume is large and whether a per-token correction beats a scalar is open.
- **The project's cross-paper rule** "Don't assume a pretrained reader/lens stays calibrated after fine-tuning" maps onto this paper. Refitting a single temperature on a lens or probe readout is the cheapest "recalibrated" baseline to compare against the frozen readout.

**Baselines and controls required** **[proposed experiment]**:
- The **base model** evaluated with the identical T-fitting procedure. T* for the base is generally ≠ 1, so organism T* must be compared with base T*, not with 1.
- A **positive control:** divide the base model's logits by a known T₀ (e.g. 0.5 and 2) and confirm the pipeline recovers T* ≈ T₀ and closes the NLL gap. This is a known-answer test of the fitting code.
- An **invariance check:** argmax and greedy outputs are byte-identical before and after TS. This is the silent-bug detector.
- **Disjoint fit and evaluation halves**, with document-level bootstrap CIs on T*, NLL and ECE (the paper gives none).
- Always report **accuracy, or a greedy behaviour metric, next to any calibrated metric**, so that a lower calibrated NLL is never read as restored capability.

**Which of our experiments it duplicates.** I cannot tell from here: under this task's independence rule I did not read `experiments/`. Any existing check that fits a scalar temperature by NLL on held-out data is exactly this paper's method and inherits its limits: one global scalar, i.i.d. assumption, no accuracy change, no mechanism **[our inference]**.

**One discriminating follow-up** **[proposed experiment]**.
- **Setup.** For each organism and its base model, build a held-out set with three strata: (i) default-Assistant prompts, (ii) prompts in the trained character's context, (iii) related-persona prompts, plus generic text as a capability reference. Split each stratum by document into fit/eval halves.
- **Measurements, per stratum, on the eval half:**
  - raw NLL;
  - NLL after a *global* T (fit on all strata);
  - NLL after a *per-stratum* T;
  - top-1 next-token accuracy and the greedy behaviour metric (both TS-invariant);
  - the sign of (NLL − mean entropy) at T = 1;
  - T* with bootstrap CI.
- **Decision rule, fixed before running:**
  - **Scale-only.** In a stratum where the organism's raw-NLL excess over base is mostly removed by TS (set the threshold beforehand, e.g. ≥ 80% of the gap closed) and accuracy and greedy behaviour match base: call that stratum's change scale-only, not capability damage.
  - **Capability or ranking change.** If TS closes little of the gap, or accuracy differs: the fine-tune changed what the model predicts, not only how sharply.
  - **Condition-specific confidence change.** If per-stratum T* differ beyond their CIs and the global T leaves stratum-specific residual NLL/ECE: the fine-tune changed confidence conditionally, which is a persona-specificity signal. Identifying the training-data mechanism then needs data ablations or interventions; TS cannot provide it.

---

## 10. Open questions

**The authors' own** **[author result]**:
- "It remains future work to understand why these trends affect calibration while improving accuracy" (p. 8).
- How Batch Norm affects final predictions is "difficult to pinpoint" (p. 4).
- Whether the Reuters results reflect the "dataset split or … the particular binning scheme" (p. 7).
- Whether the weight-decay uptick is an optimisation artifact (p. 4).
- That MCE is "very sensitive to the binning scheme and is less suited for small test sets" (Table S1 caption).

**Ours** **[unresolved / our inference]**:
- What T values were fitted for each Table 1 model? Is T > 1 in every overconfident row? Only Fig. S1 shows T, for one run.
- Which model and data underlie Fig. S1, and why its pre-epoch-250 curves violate the entropy/NLL/T relationship (§7)?
- Which run is Fig. 1's ResNet (error 30.6), and which numbers does the "29% to 27%" text for Fig. 3 refer to?
- Do the Sec. 3 trends survive seeds and accuracy-matched comparisons? Is ECE growth with capacity explained by the accuracy level reached?
- Is "low-dimensional miscalibration" a property of the networks, or of small validation sets that penalise extra calibrator parameters? (CIFAR-10 has 5,000 validation examples for 20 vector-scaling parameters and vector scaling still does not beat TS on ECE, which weakly favours the authors' reading.)
- How does TS behave under distribution shift? That is the setting our persona conditions create.
- For LMs, see §9: does one T suffice across persona contexts, and does a per-token (vector) correction add anything at vocabulary scale?

---

## 11. Reproduction checklist & remaining doubts

**To reproduce the method on our models** **[proposed experiment]**:
- [ ] Extract logits z (pre-softmax) for a held-out set; record model revision, adapter, chat template and position alignment (logits at i predict token i+1).
- [ ] Split held-out data by document into fit and eval halves.
- [ ] Fit β = 1/T by minimising mean NLL on the fit half. It is convex in β; L-BFGS or a line search is enough (the paper used conjugate gradient, ≈10 iterations, p. 8).
- [ ] Check at the optimum that mean NLL ≈ mean entropy on the fit set. This is the optimality identity (Fig. S1 caption; §5.4).
- [ ] Verify argmax and greedy outputs are identical before and after TS.
- [ ] Positive control: rescale base logits by known T₀ and recover it.
- [ ] Report on the eval half: T*, raw vs TS NLL, ECE (M = 15 equal-width bins on max-softmax, eq. 3, plus one equal-mass variant to check bin sensitivity), accuracy, and bootstrap CIs by document.
- [ ] If comparing calibrators, include TS, vector scaling and isotonic regression. Report accuracy change for any method that can move the argmax (Table S2 shows this can be tens of points).

**Remaining doubts about the paper** **[unresolved]**:
- All Table 1 numbers are single runs, with no uncertainty.
- Several text/figure/table mismatches (§7, items 1–8).
- The training configuration lives in other papers.
- The fitted temperatures are never reported.
- The calibration validation set may overlap with the model-selection set.
- The "why" of miscalibration is unresolved by the authors' own statement.
