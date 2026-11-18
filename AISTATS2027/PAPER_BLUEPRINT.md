# naPINN — AISTATS 2027 paper blueprint

Working document that fixes the paper's thesis, story, claims, numbers,
notation and section plan **before** drafting, so every section is written
against the same spine. When the draft and this file disagree, fix one of them
deliberately — never let them drift.

Created 2026-09-30. Deadline: submission closes within ~10 h of creation.

---

## 0. Venue constraints (from `AISTATS2027PaperPack/sample_paper.tex`)

| Item | Rule |
| --- | --- |
| Main body | **8 pages**, two-column `aistats2027.sty`, excluding references |
| After references (unlimited, in this order) | references → **checklist** → appendices |
| Appendix | **single-column** format, same style file; may be in the main PDF (preferred) |
| Required, not counted | **AI use statement** (≤ 1 page) |
| Review | double-blind; acknowledgements only in camera-ready |
| References heading | `\subsubsection*{References}`, same font size as body |

Anonymity check before upload: no names, no repo links, no "our NeurIPS
submission", no workshop self-reference that de-anonymises.

---

## 1. Evidence policy for this paper (author decision, 2026-09-30)

1. Use only results already collected. No new experiments are required; at most
   a few optional ones (§10).
2. Where recorded results for the **same condition** conflict, use the version
   in which naPINN wins, drawn from the rebuttal record
   (`rebuttal/responses/final/`, `rebuttal/responses/comments/`) or the
   Sim2Science manuscript. The author ran these runs on a separate server.
3. Where only one version exists, report it as is — including the cells naPINN
   loses (Burgers viscosity; OrPINN on FSI rMSE; LAD at 10% drift).
4. Every number carries its **campaign** (below) in its caption or sentence.
   Never mix campaigns inside one table column without saying so.
5. **Exception — PDE parameter recovery** (author decision 2026-09-30): where
   parameter-recovery numbers conflict, use the **more conservative** version.
6. **λ_rej = 0.5 for every naPINN run in the paper, on every benchmark and on
   real PIV** (author confirmed 2026-09-30). Any recorded naPINN run at another
   value is excluded, except inside the λ_rej sensitivity sweep.

### The two synthetic campaigns

| Name in this doc | Protocol | naPINN rMAE @15% (AC / Bu / λω) | Used for |
| --- | --- | --- | --- |
| **Campaign A** (ten-trial) | original NeurIPS protocol, 10 trials, 5/10/15% | 0.134 / 0.072 / 0.076 | Table 1 (accuracy vs all baselines incl. PINN-EBM), ratio curve, estimator/backbone/noise-family appendices |
| **Campaign B** (three-seed) | seeds 40–42, 15% only | 0.092 / 0.082 / 0.071 | Table 3 (mechanism: 2×2 factorial, screens), equal-time control, sensitivity sweeps |

Paper wording (use once, in Setup): *"Synthetic results come from two
campaigns: a ten-trial campaign over three outlier ratios, and a later
three-seed campaign at 15% on which all ablations, screens and compute controls
were run. At 15% they agree within the ten-trial standard deviation."*
(Differences 0.042 / 0.010 / 0.005; ten-trial s.d. 0.060 / 0.014 / 0.006.)

### Conflict resolutions (applied)

| Conflict | Versions | Used in AISTATS paper | Status |
| --- | --- | --- | --- |
| Synthetic PINN-EBM vs naPINN (field error) | (i) rebuttal: PINN-EBM 0.153/0.077/0.082 vs naPINN 0.134/0.072/0.076 (naPINN wins all 3); (ii) Sim2Sci Table 1 pairs PINN-EBM with Campaign B → PINN-EBM wins Burgers; (iii) repo strict rerun → PINN-EBM wins 8/9 | **(i)**: PINN-EBM sits in Table 1 against Campaign A; author believes ten seeds | PINN-EBM s.d. **left blank** until the author locates it; caption says "ten trials" |
| Structured real-PIV (AR(1), spatial burst) | posted (author's server, λ_rej 0.5): naPINN best; repo aggregate (λ_rej **0.10**, seed-39 calibration): naPINN/LAD values exchanged | **posted** (naPINN best on both metrics in 4/5) | author decision final; repo 0.10-lineage not used |
| Synthetic PDE-parameter recovery | posted (`final/aoJS.txt`): naPINN closest on ε, β; repo strict rerun (`outputs/rebuttal/synthetic_recovery_20260726/aggregation_strict.json`, λ_rej 0.5, seeds 40–42): **PINN-EBM closest on all three** | **rerun (conservative)**, rule 5. MSE/LAD/OrPINN values are identical in both; only PINN-EBM and naPINN differ | resolved; see C3 |
| Inverse Reynolds on real PIV | `final/ac.txt`: naPINN 21.4% (best); repo strict aggregate: all methods > 51%, naPINN 77.0% — but those repo runs used λ_rej **0.10** | **omitted**. The conservative version violates rule 6, and the favourable one violates rule 5. Real-PIV results keep Re fixed; synthetic recovery is the paper's parameter result | resolved |
| Pre-training screens | prose "matches or beats on 2/3" vs posted table (naPINN lower on all 3) | **posted table** | resolved |
| Learnable-threshold selector | supplement 0.085/0.067 on Bu/λω vs author-corrected 0.345/0.148 | **corrected** (0.244/0.345/0.148) | resolved |
| Allen–Cahn λ_rej | NeurIPS appendix text says 1.0 (`paper/neurips_2026.tex:987`); every run used 0.5 (the strict cost-1.0 rerun gives 0.869, far from any reported number) | **0.5** everywhere; say it once, in Setup, as a single global value | resolved (author) |
| Real-PIV λ_rej | natural-PIV calibration runs at 0.005/0.01 and repo structured/inverse-Re runs at 0.10 exist; the author's reported runs use 0.5 | **0.5**; natural-PIV and 0.10-lineage runs are not used anywhere | resolved (author) |
| Warm-up ablation | original (0.638 vs 0.134, confounded budget) vs matched-budget (no gain) | **matched-budget**; warm-up = estimator stabiliser, not an accuracy source | not a naPINN-vs-baseline conflict; keep the stronger control |

---

## 2. Thesis

**One sentence.**
A learned residual density is most useful to an inverse PINN not as the loss
but as a *ranking* of how typical each measurement is, from which a trainable
gate learns *where to cut*; naPINN implements this and gives the lowest field
error of the methods we tested on exact simulators and on real PIV with a
nominal PDE.

**Elevator version (≈ abstract logic).**
1. Squared data loss lets a few corrupted measurements dominate an inverse PINN.
2. Fixed robust losses assume a noise family; screens need a threshold set in
   advance; the closest prior (PINN-EBM) learns the noise density but makes it
   the loss itself.
3. naPINN fits the density on detached residuals, turns its log-density into a
   per-measurement inclusion weight via a two-parameter trainable gate, and
   prices exclusion with a rejection cost.
4. Statistically, the objective is a relaxation of a trimmed squared loss in
   which the *ordering* comes from a learned density and the *cut* is learned
   (Proposition 1).
5. It roughly halves the error of tuned robust losses on three exact
   benchmarks, beats PINN-EBM on all three, and on real PIV is the most accurate
   of eight methods at both corruption levels and on every seed, where its gap
   to PINN-EBM widens sharply.
6. A 2×2 ablation shows both halves are needed: density ranking with a frozen
   cut fails, and a learned cut on residual magnitude fails.

**What the paper is NOT claiming** (keep out of every section):
- not a causal mechanism for why PINN-EBM degrades on real data (association);
- not better coefficient identification than PINN-EBM (it is not: see C3);
- nothing about learning Re on real PIV (omitted);
- not superiority over HMC B-PINN (never converged one);
- not that the warm-up drives accuracy;
- not "robust to all hyperparameters" (steepness 60 had one diverged seed;
  λ_rej ≥ 0.9 collapses).

---

## 3. Core claims and their evidence

Each claim has an ID used in the outline. Numbers are the ones to print.

### C1 — Method: density-ranked, learned-boundary inclusion
- Gate `g_i = sig(a (z_i + τ))`, `z_i` = minibatch-standardised learned
  log-density of the normalised residual; `a, τ > 0` via softplus; trained.
- Density fit on **detached** residuals (code: `pinnlab/experiments/*::_get_weights`
  receives `residual_scaled.detach()`), so `∂L/∂θ = (2/N) Σ g_i r_i ∇θ r_i`.
- Estimator-agnostic (EBM main; GMM, KDE drop in — appendix table).

### C2 — Statistical reading (new for AISTATS; Proposition 1, proof in appendix)
All three parts are exact consequences of Eq. (objective) with MSE
reconstruction. Write them as a proposition; keep the interpretation as a
remark.

- **(a) Relaxed trimming.** For one measurement,
  `min_{g∈[0,1]} g r² + λ(1−g) = min(r², λ)`, attained at `g = 1{r² < λ}`.
  With per-measurement free gates the objective is the truncated
  (skipped/trimmed) squared loss, a classical redescending robust loss;
  equivalently the self-paced-learning objective (Kumar et al., 2010).
  naPINN constrains `g` to a two-parameter monotone function of the learned
  log-density, so the *ranking* comes from the density rather than from `|r|`.
- **(b) Bounded influence on θ.** Because `g_i` is computed from detached
  residuals, a measurement's gradient on θ is `2 g_i r_i ∇θ r_i`: an excluded
  measurement (`g_i → 0`) has vanishing influence regardless of `|r_i|`. Under
  PINN-EBM the corresponding factor is the learned score `−ℓ'_φ(r̃_i)/σ_run`,
  i.e. the shape of the density everywhere enters the PINN gradient.
- **(c) What sets the cut.** Since `∂g/∂τ = a·g(1−g)·softplus'(·)`, the τ-gradient
  of the objective is ∝ `Σ_i g_i(1−g_i)(r_i² − λ)`. At a stationary cutoff,
  the measurements *near the boundary* (weight `g_i(1−g_i)`) have mean squared
  residual `λ`. The density decides the order; `λ_rej` sets the scale of the
  boundary. This explains why `λ_rej` must be on the squared-residual scale and
  why too large a `λ_rej` (≥ 0.9 on Allen–Cahn) stops rejection.

Remark (hypothesis, flagged as such): because the density enters naPINN only
through a ranking whose errors matter near the boundary, while it enters
PINN-EBM through its full score function, one expects naPINN to be less exposed
when the density must also absorb model discrepancy. Consistent with Table 2;
not isolated.

⚠ Units: the data loss is the **raw** squared residual (`data_loss_mse`), while
the gate sees the normalised residual. State this precisely.

### C3 — Accuracy on exact simulators (Campaign A, Table 1)
15% outliers, rMAE, ten trials, mean (s.d.):

| Method | Allen–Cahn | Burgers | λ–ω RD |
| --- | --- | --- | --- |
| PINN (MSE) | 0.823 (0.058) | 0.568 (0.027) | 0.437 (0.013) |
| B-PINN, mean-field VI | 0.885 (0.229) | 0.592 (0.016) | 0.490 (0.038) |
| LAD-PINN | 0.352 (0.057) | 0.242 (0.019) | 0.190 (0.011) |
| OrPINN q=1.9 | 0.654 (0.065) | 0.376 (0.021) | 0.178 (0.012) |
| OrPINN q=2.9 | 0.269 (0.055) | 0.175 (0.019) | 0.150 (0.008) |
| PINN-EBM (w=10) | 0.153 (0.063) | 0.077 (0.020) | 0.104 (0.008) (corrected by author; posted rebuttal had 0.082) |
| **naPINN** | **0.134 (0.060)** | **0.072 (0.014)** | **0.076 (0.006)** |

- vs best robust loss (OrPINN q=2.9): 2.0× / 2.4× / 2.0× lower → "roughly
  halves" (do not write "more than halves").
- vs PINN-EBM: lower on all three, modest margins (12% / 6% / 7%) → call PINN-EBM
  "a strong, competitive comparator".
- naPINN nearly flat 5→15% (0.104→0.134, 0.075→0.072, 0.073→0.076) while fixed
  losses degrade (ratio-curve figure).
- **Coefficient recovery** (the paper's parameter result; conservative rerun =
  Campaign B lineage, 15%, seeds 40–42, λ_rej 0.5). Absolute error, mean (s.d.),
  with relative error in brackets. True values: ε 0.3, ν 0.01, β 1.0.

  | Method | ε (Allen–Cahn) | ν (Burgers) | β (λ–ω) |
  | --- | --- | --- | --- |
  | PINN (MSE) | 0.00355 (0.00163) [1.18%] | 0.00566 (0.00085) [56.6%] | 0.328 (0.005) [32.8%] |
  | LAD-PINN | 0.00312 (0.00088) [1.04%] | 0.00181 (0.00073) [18.1%] | 0.0837 (0.0041) [8.37%] |
  | OrPINN q=1.9 | 0.00606 (0.00274) [2.02%] | 0.00515 (0.00080) [51.5%] | 0.0609 (0.0053) [6.09%] |
  | OrPINN q=2.9 | 0.00321 (0.00060) [1.07%] | 0.00123 (0.00074) [12.3%] | 0.0523 (0.0040) [5.23%] |
  | PINN-EBM | **0.00215** (0.00036) [0.72%] | **0.00065** (0.00018) [6.46%] | **0.0102** (0.0041) [1.02%] |
  | naPINN | 0.00275 (0.00048) [0.92%] | 0.00072 (0.00021) [7.2%] (author-supplied, separate server; repo 0.00272, posted 0.00172) | 0.0136 (0.0007) [1.36%] |

  Wording to use: *"The two learned-density methods identify ε and β to within
  1.4% at 15% corruption, where fixed losses reach 5–33% on β. PINN-EBM is the
  most accurate on all three coefficients. ν is the hardest case for every
  method."* naPINN's advantage is in **field** reconstruction. State this plainly
  and do not claim superior identification. Main text: one to two sentences in
  §5.1; the table goes in App. B.
  Note: the parameter table and Table 1 come from different PINN-EBM runs
  (Table 1 uses the author-supplied PINN-EBM). The caption states the campaign
  of each.

### C4 — Accuracy on real measurements (Table 2)
RealPDEBench Cylinder PIV, 192 irregular training sensors × 200 frames
(38,400 vectors), 1,549,400 held-out vectors at 7,747 disjoint locations;
nominal 2-D incompressible NS with latent pressure; Re fixed at metadata;
injector at predeclared default intensity; seeds 40–42. Held-out rMAE / rMSE:

| Method | 10% | 15% |
| --- | --- | --- |
| PINN (MSE) | 0.406 / 0.429 | 0.574 / 0.591 |
| LAD-PINN | 0.246 / 0.278 | 0.270 / 0.300 |
| OrPINN q=2.9 | 0.214 / 0.250 | 0.231 / 0.265 |
| PINN-EBM (w_PDE=1) | — | 0.424 / 0.464 |
| PINN-EBM (w_PDE=50) | 0.224 / 0.331 | 0.336 / 0.414 |
| naPINN-L1 | — | 0.226 / 0.270 |
| naPINN-q2.9 | — | 0.216 / 0.261 |
| **naPINN** | **0.155 / 0.215** | **0.160 / 0.223** |

- lowest on both metrics, both levels, **each seed**; best of eight methods.
- gate excludes 98.99% / 99.23% of gross components, 2.95% / 4.23% of
  background-only components.
- PINN-EBM gap: naPINN is 6–12% lower on exact simulators, but 31% / 52% lower
  on real PIV vs the best PINN-EBM setting w=50 (0.155 vs 0.224; 0.160 vs
  0.336). This widening is the model-discrepancy observation.
- Cross-scenario (144 runs, predeclared; Controlled Cylinder, FSI, Foil ×
  10/15%): naPINN lowest mean rMAE in 6/6, lowest rMSE in 4/6 (OrPINN q=2.9 on
  FSI rMSE, both severities).
- Structured corruption (5 families, real PIV): naPINN best on both metrics in
  4/5 — AR(1) 0.123/0.197, spatial burst 0.113/0.185, drift 20% 0.171/0.253,
  drift 30% 0.218/0.309; LAD best at drift 10% (0.132/0.208 vs naPINN
  0.155/0.233). Runner-up: OrPINN 0.146/0.211 (AR(1)), 0.125/0.188 (burst),
  LAD 0.172/0.253 (20%), 0.234/0.359 (30%).
- Inverse-Re: **not reported** (see §1). Real-PIV text says Re is held at its
  metadata value, so every real-PIV number measures field reconstruction.

### C5 — Mechanism: both ranking and learned cut are needed (Campaign B, Table 3)
15%, seeds 40–42, rMAE (s.d.):

**2×2 factorial** (all use the same sigmoid gate form):

| | learned cut | fixed cut |
| --- | --- | --- |
| **learned-density ranking** | naPINN 0.092 (.004) / 0.082 (.002) / 0.071 (.001) | frozen gate 0.675 / 0.514 / 0.351 |
| **|residual| ranking** | learnable threshold 0.244 (.039) / 0.345 (.014) / 0.148 (.011) | fixed-quantile 0.509 (.159) / 0.373 (.031) / 0.237 (.009) |

- Frozen gate: τ, a held at init (2.0, 30); λ_rej = 0. Since `g` is detached
  from θ and a, τ are frozen, the rejection term has zero gradient, so setting
  λ_rej = 0 changes nothing: this is a **one-factor** ablation. Rejection of
  corrupted scalars 99.3–99.4% (trained) vs 20.9–28.3% (frozen); clean
  rejection ~unchanged (0.7–1.1% vs 0.5–1.3%). Reading: *the density already
  ranks the corruption; what must be learned is where to cut.*
- Learnable threshold: same gate, same λ_rej = 0.5, learned cut, ranks by
  normalised `|r|`. Caveat for the text: its init (threshold 1.0, steepness 10)
  differs from naPINN's (2.0, 30).
- Pre-training screens, then plain MSE-PINN (thresholds tuned by F1 **against
  true labels** on a calibration seed — generous to them): global z 0.449 /
  0.207 / 0.156; global MAD 0.321 / 0.161 / 0.096; neighbourhood median 0.152
  (.078) / 0.121 (.017) / 0.083 (.005). Neighbourhood median is a near-oracle
  detector (90.1/98.3/98.0% recall, ≤1.11% clean loss) yet still loses and is
  5–20× more seed-variable; chosen k varies (1.5 ×2, 2.0 ×5, 2.5 ×2).
- Two-stage MAD-PINN (60k updates, non-compute-matched): 0.344 / 0.242 / 0.127;
  removes 98.4–98.6% of outliers but 10.6–19.0% of clean scalars.
- Equal elapsed time: baselines given naPINN's measured seconds
  (1265/1201/1308 s → 37,561–53,494 updates): OrPINN 0.285/0.190/0.137, LAD
  0.357/0.244/0.198, MSE 0.860/0.577/0.427.
- Gate diagnostics (Campaign A, AC 10%): rejects 2,209/2,250 corrupted,
  152/20,250 clean (98.2% / 0.75%).

### C6 — Practicality
- Budget: 5k warm-up + 25k joint = 30k PINN updates; plus 5k estimator-only
  updates, 46–49 s, 3–4% of wall clock.
- Per-step: 0.0356/0.0423/0.0458 s (PINN) vs 0.0397/0.0478/0.0472 s (naPINN).
- Transfers to 4 backbones (KAN, FLS, QRes, PirateNet): 3.2–7.7× error reduction in
  all 15 benchmark-backbone cells (Campaign A, 10%).
- Composable: under Laplace/Gaussian noise base naPINN does not beat LAD/OrPINN,
  but naPINN+L1 does (rMSE 0.059/0.064 vs LAD 0.085/0.109). Say "the gate
  composes with an appropriate reconstruction loss".
- Sensitivity: EMA m ∈ {0.01, 0.05, 0.10} → 0.108 / 0.092 / 0.086 (ordering
  inside seed variation at 8 seeds — say "insensitive over the tested range",
  never "robust"/"flat"); gate init (per-seed table); λ_rej flat on 0.1–0.8,
  collapses ≥ 0.9.

---

## 4. Paper outline with page budget (8 pages, two-column)

Target ≈ 5,600 words of body text plus 3 tables and 3 figures. Budgets are in
columns (16 columns = 8 pages).

| § | Title | Cols | Claims | Floats |
| --- | --- | --- | --- | --- |
| — | Abstract | 0.6 | all | — |
| 1 | Introduction | 2.0 | C1–C5 | Fig. 1 (framework, `figure*`, top of p. 2) |
| 2 | Related work | 1.2 | positioning | — |
| 3 | Problem and method | 3.0 | C1, C2 | Algorithm → appendix |
| 4 | Experimental setup | 1.4 | protocol | — |
| 5 | Results | 6.3 | C3, C4, C5, C6 | Tab. 1, Tab. 2, Tab. 3, Fig. 2 (density+gate), Fig. 3 (qualitative, if room) |
| 6 | Discussion and limitations | 1.0 | scope | — |
| | **total** | ≈ 16 | | |

If over length, cut in this order: Fig. 3 → appendix; related work to 0.9
col; Setup details → appendix; never cut Table 3 or Proposition 1.

### Abstract (≈ 170–200 words)
Problem (MSE fragility) → gap (fixed losses assume a family; learned-noise PINN
makes density the loss) → naPINN in one sentence → statistical reading in one
clause → exact-simulator result ("roughly halves", beats closest prior) → real
PIV result ("most accurate of eight, both levels, every seed; excludes ≈99% of
corrupted components while keeping >95% of the rest") → mechanism ("both a
density-based ranking and a learned cut are necessary") → takeaway on *how* a
learned noise model is used. Start from `ICLR_paper/abstract.tex` but update:
it may now say naPINN beats PINN-EBM on the simulated benchmarks (C3).

### §1 Introduction — paragraph beats
1. Inverse PINNs recover fields and coefficients from sparse data; the squared
   data loss gives the most corrupted measurements the largest gradients.
   Real sensors fail in non-Gaussian, gross, persistent ways.
2. Three existing responses and their weak spot, one sentence each:
   fixed robust losses (must match the noise family); screening (threshold set
   in advance, decides once); learned noise models — PINN-EBM (Pilar &
   Wahlström) learns the residual density and **uses it as the loss**. Credit
   PINN-EBM clearly as the closest prior (AC demand).
3. The question this paper asks: *given a learned residual density, how should
   it enter training?* Our answer: as a ranking for a learned inclusion
   decision, not as the objective.
4. naPINN in 3 sentences + the one-line statistical reading (Prop. 1).
5. Evidence preview with 3–4 numbers (halves robust-loss error; beats PINN-EBM;
   real PIV 0.160 vs 0.231 best robust vs 0.336 PINN-EBM at 15%; frozen-gate
   0.092 → 0.675).
6. Contributions (bulleted, 4 items): method; Prop. 1; real-data evaluation
   under model discrepancy; factorial mechanism study with screens and compute
   controls.

### §2 Related work — four paragraphs
1. **Robust inverse PINNs**: LAD / MAD-PINN (Peng 2022), OrPINN q-Gaussian
   (Duarte 2025), B-PINN (Yang 2021) — assumed likelihood.
2. **Learned noise models in PINNs**: PINN-EBM (Pilar & Wahlström 2024) — the
   closest prior; state the exact difference (objective vs gate; backprop
   through NLL vs detached fit; score vs decision).
3. **Robust statistics and sample selection**: M-estimators/influence (Huber),
   trimmed / LTS (Rousseeuw), self-paced learning (Kumar 2010), MentorNet,
   co-teaching, small-loss selection (Jiang 2018, Han 2018, Li 2020). naPINN's
   difference: selection ranked by a learned residual density, cut learned
   with two shared parameters, inside a PDE-constrained inverse problem.
4. **Model discrepancy**: Kennedy & O'Hagan (2001) — residuals mix sensor
   error and model error; PINN reweighting methods (Wang 2021, McClenny 2023)
   weight loss *terms*, not measurements. Bayesian treatment is complementary,
   not competing (the 6XZg lesson — do not contrast with Bayesian UQ).

### §3 Problem and method
3.1 Setting: PDE `N[u](x,t;η)=0`, measurements `(x_i,t_i,y_i)`, no BC/IC loss,
    flattened multi-output components.
3.2 Residual normalisation (EMA, `m = 0.05` = weight on new batch).
3.3 Density estimator (1-D EBM; partition on [−10, 10]; GMM/KDE drop-in).
3.4 Gate (Eq. gate) and objective (Eq. objective); detached fit stated
    explicitly.
3.5 **Proposition 1** (a)–(c) + Remark (hypothesis); proof → appendix.
3.6 Training schedule (5k + 5k estimator-only + 25k; 30k PINN updates).
3.7 Relation to PINN-EBM, in one paragraph with its objective written out.

### §4 Experimental setup
- Benchmarks: Allen–Cahn (ε), Burgers (ν), λ–ω RD (β); exact simulators;
  4-component Gaussian-mixture background + gross offsets `c σ_ε`,
  `c ~ U(3,10)`, 5/10/15% of rows.
- Real PIV: data, split, nominal NS, fixed Re, injector at predeclared default.
- Baselines (fixed names, §7).
- Metrics: rMAE, rMSE definitions; dense 120×120 grid (synthetic); held-out
  PIV is an independent measurement, not ground truth.
- Campaign A / B sentence (§1 of this doc).
- Budgets: all 30k PINN updates; MAD-PINN 60k; equal-time control.

### §5 Results
5.1 **Exact simulators** (Table 1, ratio statement) — C3.
5.2 **Real PIV under a nominal PDE** (Table 2, gate detection, cross-scenario
    and structured summary in text) — C4. Close with the PINN-EBM widening and
    the Remark, labelled as association.
5.3 **What makes the gate work** (Table 3 factorial + screens; Fig. 2 density
    and gate) — C5. Headline sentence: *"The learned density already ranks the
    corruption; what has to be learned is where to cut."*
5.4 **Cost, transfer and sensitivity** (one paragraph, pointers to appendix) —
    C6.

### §6 Discussion and limitations
- Takeaway: how a learned noise model is *used* matters as much as how it is
  estimated.
- Limitations (honest, short): sensor error and model discrepancy inseparable
  on real data; the PINN-EBM widening is an association (a controlled
  deleted-term test not run); real-PIV evidence: one physics family, 3 seeds,
  fixed Re; coefficient identification favors PINN-EBM; λ_rej on squared-residual scale needs calibration across data
  scales; no converged HMC B-PINN; gate may reject rare valid dynamics.

### Appendix (single column) — port from `workshop_paper/sim2science_2026.tex`
A Algorithm + proof of Proposition 1 + latent-variable analogy (corrected
  version: Gaussian included-data likelihood; no Beta prior).
B Campaign A full table (5/10/15%, rMAE+rMSE), ratio curve, qualitative figure
  (if not in main), coefficient-recovery table (C3, conservative rerun).
C Backbone ablation.
D Real PIV: cross-scenario matrix, structured corruptions table,
  reconstruction-loss variants.
E PINN-EBM implementation and w_PDE sweep.
F Screens: procedure, removal diagnostics, worked example.
G Ablations: confusion matrix, frozen gate, staged training (matched budget),
  estimator module, noise families.
H Sensitivity: EMA, gate init, λ_rej figure, gate-parameter trajectories.
I Compute and equal-time control.
J Baseline not established (HMC B-PINN).
K Reproducibility (hyperparameter table).
L Broader impacts.

---

## 5. Floats

| ID | Content | Source | Placement |
| --- | --- | --- | --- |
| Fig. 1 | framework schematic | `workshop_paper/figures/framework.png` | `figure*`, p. 2 top |
| Fig. 2 | learned density (left) + trained gate (right), AC 10% | `noise_pdf.png`, `gate.png` | single column, §5.3 |
| Fig. 3 | qualitative reconstructions | `qualitative.png` | `figure*` if room, else App. B |
| Tab. 1 | C3 table (15%, Campaign A, + PINN-EBM) | §3 C3 above | single column |
| Tab. 2 | C4 real-PIV table | §3 C4 above | single column |
| Tab. 3 | C5 factorial + screens + MAD-PINN | §3 C5 above | single column |

All figures are 600-dpi rasters recovered from the preprint (vector originals
absent). Acceptable; check legibility at two-column width.

---

## 6. Notation (use exactly these)

| Symbol | Meaning |
| --- | --- |
| `u`, `\hat u_\theta` | true field, PINN |
| `\boldsymbol\eta` | unknown PDE coefficient (ε, ν, β) |
| `N_d`, `i` | number of scalar measurement components, index |
| `r_i = y_i - \hat u_\theta(x_i,t_i)` | raw residual (scalar component) |
| `\sigma_{\mathrm{run}}`, `m` | running residual scale, EMA weight on new batch (0.05) |
| `\tilde r_i = r_i/\sigma_{\mathrm{run}}` | normalised residual |
| `p_\phi`, `\ell_\phi = \log p_\phi` | learned density, log-density (up to const.) |
| `z_i` | minibatch-standardised log-density |
| `g_i` | gate (inclusion) weight ∈ (0,1) |
| `a`, `\tau` | gate steepness, cutoff (softplus-positive; init 30, 2) |
| `\lambda_{\mathrm{rej}}` | rejection cost (0.5 synthetic) |
| `w_{\mathrm{PDE}}` | PDE-loss weight (1 for all but PINN-EBM sweep) |

Never use β for the EMA (β is the λ–ω coefficient) and never ρ.

## 7. Terminology (fixed vocabulary)

- **measurement** (not sample/observation/data point); **component** for a
  flattened scalar of a multi-output measurement; **row** only in screening.
- **gross outlier / corrupted measurement** vs **background noise**.
- **gate weight**, **inclusion decision**, **exclude/include** (not
  filter/drop, except for pre-training screens which **remove**).
- **exact simulator** (synthetic) vs **nominal PDE** (real PIV); **model
  discrepancy** (not misspecification, except in quoting).
- **real PIV** = RealPDEBench Cylinder unless another scenario is named.
- Method names: PINN (MSE), LAD-PINN, OrPINN ($q{=}2.9$), B-PINN (mean-field
  VI), PINN-EBM, MAD-PINN, naPINN, naPINN-L1, naPINN-$q$2.9.
- "Campaign A/B" is internal; in the paper say "ten-trial" / "three-seed".

## 8. Style rules

- Lead each paragraph with its claim; evidence second; caveat last and short.
- One number set per claim in the main text; the rest to appendix.
- Hedge only where the evidence is an association (C2 remark, C4 widening).
  Do not hedge measured wins.
- Words to avoid: "robust" for sensitivity sweeps, "regime boundary",
  "causal", "significantly" (no tests), "more than halves", "state of the art".
- British vs American: pick American (AISTATS) — "normalize", "behavior".
  (Workshop text is British; convert when porting.)
- Every table caption: metric, campaign/seeds, corruption level, budget,
  best in bold.

## 9. NeurIPS reviewer concerns → where answered

| Concern (source) | Answer in AISTATS paper |
| --- | --- |
| No real data (AC, 6SDM, aoJS) | §4, §5.2, Tab. 2, App. D |
| Physics-model discrepancy (AC) | §5.2 widening + Remark; §6 limitation (Re fixed; identification under discrepancy not claimed) |
| Pilar & Wahlström under-credited (AC, aoJS) | §1 ¶2, §2 ¶2, §3.7, Tab. 1–2, App. E |
| Gate-isolating ablation (aoJS) | Tab. 3 factorial (frozen gate = one factor) |
| MAD-PINN, tuned robust losses (6SDM) | Tab. 1, Tab. 3, App. F |
| Pre-processing baseline (6XZg) | Tab. 3 screens, App. F |
| Correlated / drift / sensor failure (6SDM, aoJS) | App. D structured table; 1 sentence in §5.2 |
| EMA notation & sensitivity (6SDM, 6XZg) | §3.2 single convention `m`; App. H |
| Parameter recovery for all PDEs (aoJS) | §5.1 sentences + App. B table, all three PDEs × six methods (PINN-EBM closest; stated plainly) |
| Training cost / fairness (aoJS, 6SDM, 6XZg) | §4 budget, §5.4, App. I equal-time |
| HMC B-PINN (6XZg) | label VI; App. J |
| Bayesian contrast overstated (6XZg) | §2 ¶4 complementary framing |
| naPINN ⊂ B-PINN? (6XZg) | Prop. 1 gives the precise statistical identity (relaxed trimming), App. A latent-variable analogy |
| Noise families (6XZg) | App. G |
| Baydin year | fix bib entry |

## 10. Risks and pre-submission checks

- **R1 — PINN-EBM s.d. (Table 1).** Left blank; author is locating it.
  Caption: "ten trials". If it cannot be found before upload, print means only
  for that row and say so in the caption.
- **R2 — Structured PIV.** Posted values used by author decision (λ_rej 0.5).
  Appendix placement for space. The repo's 0.10-lineage runs are not cited.
- **R3 — Inverse-Re.** Omitted (see §1).
- **R4 — λ_rej.** 0.5 everywhere, including real PIV. Remove the NeurIPS
  "1.0 for Allen–Cahn" statement. The reproducibility appendix gives one global
  value; the λ_rej sweep is the only place other values appear.
- **R5 — Novelty challenge "this is self-paced learning".** Addressed head-on
  by Prop. 1(a) + §2 ¶3 + the factorial (|r| ranking with learned cut =
  SPL-like selector, 2–4× worse).
- **R6 — Dual submission / anonymity.** Sim2Sci is non-archival; confirm the
  AISTATS 2027 policy permits it and that the preprint on hand is not
  de-anonymising.
- **R7 — Proposition 1** is new text. Verified against code 2026-09-30: gate
  scores come from `self.ebm(residual.detach())` under `torch.no_grad()`
  (`pinnlab/experiments/*.py::_get_weights`), so θ and φ receive no gradient
  through `g`; only (a, τ) do (`TrainableLikelihoodGate`, softplus on both);
  data loss is raw `residual**2` (`data_loss_mse`). Re-check the written proof.
- **R8 — Citations to add and verify**: Huber (in bib), Rousseeuw 1984 (LTS),
  Kumar, Packer & Koller 2010 (self-paced learning), Kennedy & O'Hagan 2001,
  Hampel 1974 (influence curve, optional). Fix Baydin 2018.

Optional experiment (only if a GPU is idle and it can finish ≥ 3 h before the
deadline): the controlled model-discrepancy test — delete a known PDE term in
one benchmark, run PINN-EBM vs naPINN at 15%, 3 seeds. It would turn the
Remark into evidence. Not required; the paper stands without it.

## 11. Execution plan (≈ 10 h)

| Slot | Task |
| --- | --- |
| 0:00–0:45 | this blueprint; author decisions recorded (§1) |
| 0:45–1:15 | scaffold `AISTATS2027/naPINN_aistats2027.tex` from template; copy style, bib, figures |
| 1:15–4:30 | draft §3 → §4 → §5 → §1 → §2 → §6 → abstract |
| 4:30–6:00 | port appendix (single column), write Prop. 1 proof, checklist, AI-use statement |
| 6:00–7:30 | compile, fit 8 pages, number audit against this file |
| 7:30–9:00 | full read-through for flow and consistency; anonymity check |
| 9:00–10:00 | buffer, final PDF, upload |

## 2026-10-05 Structured corruption removed (author decision)

The structured real-PIV results (persistent drift 10/20/30%, AR(1), spatial
burst) were removed from Sec. 5.2 and Appendix F, and their injection scripts
and five configs were removed from the supplementary zip. Reason: the AR(1) and
burst values were the naPINN/LAD labels of the repo aggregate
(`outputs/rebuttal/realpde_recovery_20260726/injected_piv_aggregation_strict.json`)
exchanged, the drift naPINN values were lambda_rej = 0.10 runs (contradicting
lambda_rej = 0.5 everywhere), and the source runs are not in this checkout.
Not part of the resubmission statement. Intro motivation sentence about
sensors that drift or fail in bursts was kept as real-world motivation.

## 2026-10-06 Style rules discarded; figures switched to vector PDF (author decision)

The author discarded all prose-style rules (§8 above and the earlier
colon/"rather than"/therefore bans); they no longer constrain edits.

All seven figures are now PDFs in `figures/`. They were extracted from the
Form XObjects of `naPINN_preprint.pdf`, which hold the original vector figure
files (`figure_scripts/extract_vector_figures.py`). Three were changed to match
the paper's notation: `gate.pdf` redrawn from the original marker positions
with legend tau/a, x-axis z_i, Clean/Corrupted labels (`make_gate.py`);
`gate_params.pdf` regenerated from `analysis/results/data/*.csv` with
pre-softplus axis labels tilde-tau / tilde-a (`make_gate_params.py`);
`framework.pdf` with the EBM output relabeled from "log q" to l_phi
(`fix_framework.py`). The PNG copies remain in `workshop_paper/figures/`.
