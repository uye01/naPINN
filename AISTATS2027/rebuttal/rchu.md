# Official Review by Reviewer rchu

- Paper: naPINN: Noise-Adaptive Physics-Informed Neural Networks for Recovering Physics from Corrupted Measurements
- Submission: AISTATS 2027 #4254
- Posted: 2026-11-03 (modified 2026-11-17)
- Link: https://openreview.net/forum?id=suhrFh8WHc&noteId=ZQWvM480mO

## Scores

| Item | Score |
|---|---|
| Rating | 2 |
| Confidence | 4 |
| Soundness / Correctness | 2 |
| Clarity / Presentation | 2 |
| Contribution / Significance | 2 |

## Summary

The setting is inverse PINNs i.e., recover a field and an unknown PDE coefficient from sparse, corrupted sensor data with no boundary or initial conditions in the loss. naPINN fits a one-dimensional density to the normalized data residuals during training, standardizes the resulting log-densities within each minibatch, and passes them through a trainable sigmoid gate with learned cutoff τ and steepness a to produce a per-measurement reliability weight on the squared data loss. A linear rejection cost λ_rej(1 − g_i) prices exclusion and prevents the degenerate all-zero gate. Gate scores are detached, so the gradient on θ sees each weight as a constant. Proposition 1 establishes three things by direct computation: with free gates the objective collapses to a trimmed squared loss; at a stationary cutoff the g(1−g)-weighted mean of squared residuals equals λ_rej; and as a → infinity the included set becomes a superlevel set of the learned density, which is an interval only when the density is symmetric and unimodal. Training runs in three stages (PINN warm-up, estimator initialization at fixed θ, then joint updates), with the PINN receiving the same 30,000 updates as every baseline. Evaluation covers three simulated PDEs with a four-component asymmetric Gaussian-mixture background plus 5/10/15% row-wise positive gross offsets, and real PIV from RealPDEBench under a nominal Navier–Stokes model with held-out sensors.

## Strengths

S1. The framing of the contribution is nice, and the comparison that carries it is well designed. Holding the estimator the staged initialization and the budget fixed between PINN-EBM and naPINN isolates the one thing the paper claims to change, which is how the learned density is used. Too many papers in this space change four things at once. This one does not. Proposition 1 is modest and the authors say so (“a direct computation”), but it earns its place because the theory-to-experiment loop is actually closed. Part (b) predicts that an overly large λ_rej should stop the gate excluding corrupted points, and Figure 5 shows exactly that degradation at λ_rej ≥ 0.9. It also predicts the cutoff should settle lower under heavier corruption, and Figure 6 shows τ̃ settling at 2.8, 1.8 and 1.3 for 5, 10 and 15% outliers. That is more than most applied papers do with their propositions.

S2. The ablation is the strongest empirical section. Crossing {order by learned density} with {learned gate, frozen gate} seems right, and the result is interpretable rather than merely favourable. Density with a frozen gate is worse than residual magnitude with a learned gate, so neither factor dominates and the paper’s claim that both are needed is actually supported. The frozen-gate diagnostic explains the mechanism rather than just reporting the number. The pre-training screens are a fair comparison and are, if anything, generous to the baselines, since their thresholds were tuned against true corruption labels on a calibration seed.

## Weaknesses

W1. The central claim does not survive the paper’s own work in Appedix G. The abstract’s premise is that real measurement noise is rarely Gaussian and its form is unknown in advance, so no single fixed loss suits every case. Under Laplace or Gaussian background noise on λ–ω, naPINN with the squared loss scores 0.085 and 0.126 against LAD-PINN’s 0.085 and 0.109 and OrPINN’s 0.081 and 0.107, and only naPINN-L1 (0.059, 0.064) and naPINN-q2.9 (0.071, 0.067) win. Section 5.4 states the loss that works best inside naPINN depends on the noise. This is the same selection problem the method is pitched as removing now relocated one level in. 

W2. The simulated benchmark uses one hand-chosen noise configuration and it is one that maximally favours the proposed ordering. The background is an equal-weight mixture of Gaussians at various means with standard deviations. This is strongly multimodal and asymmetric, with widely separated modes, which is exactly the regime in which density-ordering separates from magnitude-ordering. The same mixture is used for all three PDEs and all three corruption levels, so the nine simulated cells are not nine independent probes of the claim. There is no sweep over mode separation, component count or skewness.

W3. Baseline hyperparameter treatment is uneven in a way that bears on the headline number. The factor-of-2.0 to 2.4 improvement is measured against OrPINN at q = 2.9. Only two q values were tried, 1.9 and 2.9, and q = 2.9 is better than q = 1.9 in every one of the nine cells. A monotone trend over a two-point grid, with the better point at the boundary, is weak evidence that the optimum has been found; q = 3.5 or higher may well do better. LAD-PINN has no scale parameter swept. Meanwhile PINN-EBM did receive a wPDE sweep. The authors present this asymmetry as generosity to the baseline, and on the simulated benchmarks it is, but the effect on the OrPINN comparison runs the other way and the headline factor should be regarded as an upper bound until the q grid is extended.

## Questions

Please address the above weaknesses.
