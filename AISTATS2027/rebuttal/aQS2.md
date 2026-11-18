# Official Review by Reviewer aQS2

- Paper: naPINN: Noise-Adaptive Physics-Informed Neural Networks for Recovering Physics from Corrupted Measurements
- Submission: AISTATS 2027 #4254
- Posted: 2026-11-04 (modified 2026-11-17)
- Link: https://openreview.net/forum?id=suhrFh8WHc&noteId=IYQSxfdcHu

## Scores

| Item | Score |
|---|---|
| Rating | 2 |
| Confidence | 3 |
| Soundness / Correctness | 3 |
| Clarity / Presentation | 3 |
| Contribution / Significance | 2 |

## Summary

The authors propose PINNs with an online residual-density estimator and a trainable gate that weights individual measurements for inverse problems.

## Strengths

[S1] The method is clearly formulated, modular, and compatible with different PINN architectures.

[S2] Evaluation on real flow measurements provides useful evidence beyond simulated experiments.

## Weaknesses

[W1] I am concerned that residual density alone is not sufficient to establish measurement reliability, since systematic corruption can form a high-density cluster, while valid measurements affected by model discrepancy can have low density.

[W2] Limited performance. Appendix E reports slightly lower mean coefficient errors for PINN-EBM on all three simulated problems. Several field-error differences against this closest competitor are also small.

[W3] Most experiments use the same multimodal background noise with large positive outliers, including the injected corruption on real PIV data. Thus, the range of noise and corruption types considered is limited.

## Questions

[Q1] Does naPINN retain its advantage under correlated corruption?

[Q2] Do comparisons against PINN-EBM establish a practically meaningful reconstruction improvement, and can the authors clearly identify the conditions under which that improvement occurs?

[Q3] Can you discuss Noise-aware Physics-informed Machine Learning for Robust PDE Discovery (2023)? Comparing residual-density gating with their Fourier-based denoising PINNs would clarify differences in noise assumptions.
