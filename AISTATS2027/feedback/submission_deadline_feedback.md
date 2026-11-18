**naPINN: feedback for submission within the next few hours**

2026-10-04 업데이트: 제출까지 3일 남은 상황의 최신 실행 우선순위는 `three_day_feedback_ko.md`를 따른다. 이 문서는 당시의 검토 기록으로 보존한다.

Reviewed on 30 September 2026. This document concerns `naPINN_aistats2027.tex`, its compiled PDF, and a few targeted implementation checks. It does not include a rerun or an independent audit of the reported experimental numbers. Source line numbers below refer to the manuscript at review time; use the accompanying section names if edits move them.

Follow-up: see `submission_critical_audit.md` for confirmed citation errors and updated evidence. In particular, the supplementary code and a stored Allen–Cahn run use `[0,2]^2 × [0,2]`, which explains the earlier figure concern and makes reconciling the written domain the first action before considering figure removal.

**Recommendation**

Prepare the existing paper for submission through a small set of accuracy and wording corrections. The current experiments provide a credible empirical contribution: substantial field-reconstruction gains over fixed robust losses in the main contamination setting, a useful comparison with learned-likelihood PINNs, and evaluation on real PIV with injected corruption. Keep that story and the current structure.

With this deadline, the highest-value work is to remove statements that are demonstrably inaccurate or broader than the evidence. Additional experiments, a new theory section, and a substantial rewrite are not realistic requirements for this submission. The concerns below distinguish inexpensive corrections from issues that should simply be acknowledged more carefully.

**Suggested time budget**

| Task | Budget | Completion criterion |
| --- | --- | --- |
| Apply the wording and mathematical corrections below | 45–60 minutes | Abstract, method, proposition/proof, and baseline description agree with the evidence |
| Check Figure 2 provenance and the finite-grid EBM description | 25–40 minutes | Resolve from existing files, or use the conservative fallback described below |
| Make a few reproducibility clarifications, if readily verifiable | 15–20 minutes | Describe existing runs accurately; make no training-code changes |
| Rebuild, inspect the PDF, and upload | Reserve at least 30 minutes | Main text remains within the page limit; no missing references or broken figures; uploaded PDF verified |

These are planning estimates, not reasons to use all remaining time. Preserve an upload buffer. If time becomes tight, prioritize items 1–5 and the final PDF check.

**1. Clarify the real-data claim and soften the ablation claim — highest priority, about 10 minutes**

Locations: abstract (lines 64–68), introduction (lines 114–120), ablation study, and discussion (around line 743).

The real-PIV experiment measures detection of injected corruption on an already noisy real dataset. Calling the retained components “clean” without qualification can suggest that natural sensor faults were independently labeled. The experimental setup explains this correctly, but the abstract must make the distinction too.

Replace the last two abstract sentences with something close to:

> On real particle image velocimetry with injected measurement corruption under a nominal Navier–Stokes model, naPINN achieves the lowest field error among the compared methods on the Cylinder benchmark. It rejects about 99% of injected corrupted components while retaining over 95% of components without injected corruption. Ablations support the benefit of combining learned residual-density scores with a trainable gate.

This preserves the headline result and makes its scope explicit. Use the same terminology in the introduction. It is fine to retain “clean” as a short label in tables after defining it as “without additional injected corruption.”

Replace the discussion's “neither the density ordering nor the learned cutoff suffices alone” with:

> In the tested ablations, the full method outperforms both the frozen density gate and the residual-magnitude selectors.

The existing ablations are useful, but they do not establish universal necessity. There is no need to rerun them before submission.

**2. Correct the q-Gaussian variance statement — highest priority, about 5 minutes**

Location: Appendix D, “Data losses” (around line 1075).

For the stated density proportional to

\[
[1+(q-1)\beta r^2]^{-1/(q-1)},
\]

the ordinary variance exists only for \(q<5/3\). Both tested values, \(q=1.9\) and \(q=2.9\), exceed that threshold. Consequently, the claim that \(\beta_q=1/[2(3-q)]\) “normalizes the variance” is incorrect.

Replace that clause with:

> We use the scale convention \(\beta_q=1/[2(3-q)]\) and report \(q=1.9\) and \(q=2.9\). These choices yield heavy-tailed losses; their corresponding densities do not have finite ordinary variance.

Retain the actual loss formula and reported results. This is a correction to the explanation, not a reason to change the baseline implementation or rerun it. Do not attribute this particular scale convention to the original OrPINN paper unless that attribution has been verified.

**3. Make three small corrections to the method and proposition — highest priority, about 15 minutes**

Locations: Section 3.3 (lines 280–287), Proposition 1(c) and its following paragraph (lines 357–375), and Appendix A.

First, replace “prevents the trivial solution” with “penalizes measurement exclusion” or “discourages excessive rejection,” both here and in the introduction. A positive rejection cost alone is not a general guarantee against rejecting everything. In the free-gate calculation, every point is rejected if every squared residual exceeds the rejection price. The parameterized gate also imposes its own constraints.

Second, replace “an excluded measurement has vanishing influence however large its residual” with:

> For a fixed residual and network Jacobian, its contribution to the network gradient vanishes as its gate weight tends to zero.

The displayed gradient is useful and can stay. The revised sentence avoids asserting a bounded-influence theorem: the relevant factor is \(g(r)r\), and a small weight alone does not establish its tail behavior.

Third, make the condition in Proposition 1(c) sufficient rather than necessary. Replace the ending with:

> In particular, when the log-density is symmetric about zero and strictly decreasing in absolute residual magnitude, its superlevel sets are intervals centered at zero.

In the following paragraph, replace “The two rules agree when the noise is symmetric and unimodal” with:

> For a residual density symmetric about zero and strictly decreasing in absolute residual magnitude, density and magnitude induce the same ordering; their selected sets agree when their thresholds are matched.

In Appendix A, delete or replace the final “Otherwise ... it is not an interval centered at zero” sentence. A safe replacement is:

> For general asymmetric or multimodal densities, superlevel sets need not be intervals centered at zero.

The algebra in parts (a) and (b) can remain. No additional theorem is needed for submission.

**4. Resolve the finite-grid EBM description without changing the algorithm — high priority, about 15–20 minutes**

Locations: Section 3.2, Equation 4 (lines 225–247), and Appendix B, “Estimators” (around line 900). Relevant implementation: `pinnlab/utils/ebm.py`.

The implementation computes its normalization integral on \([-10,10]\). A tanh MLP with a linear output is bounded as its scalar input goes to infinity, so its exponentiated score cannot define an integrable density over the entire real line without additional tail structure. The current equation leaves the integration domain unspecified.

Describe the computation that was actually used. A conservative formulation is:

> We use an EBM score with finite-grid normalization. Writing \(s_\phi(r)=-E_\phi(r)\), we compute \(Z_{\phi,D}=\int_D \exp(s_\phi(r))\,dr\) on \(D=[-10,10]\) by trapezoidal quadrature and fit the estimator with the finite-grid negative-log-likelihood objective. The gate uses standardized scores, for which the additive log-normalization constant cancels.

State separately that this defines a normalized density on \(D\). If normalized residuals outside \(D\) are evaluated, describe that behavior honestly: the same network score is evaluated outside the integration interval, and the training objective there is a finite-grid surrogate rather than a proper full-support likelihood. The current implementation has no explicit clipping in its EBM likelihood routine. Do not claim that all historical residuals were inside the interval without evidence.

This clarification may require a few lines in the appendix and a small equation edit in the main text. Do not add a new tail model or clipping rule at this stage: either would alter the algorithm underlying the reported results.

**5. Check Figure 2 against its source run — high priority, time-box to 15–20 minutes**

Locations: Figure 2 (`figures/qualitative.png`), the simulated-results paragraph around line 533, and Appendix C's Allen–Cahn definition (around line 1000).

The specified solution is \(\sin(\pi x)\sin(\pi y)\cos(8t)\) on \([0,1]^2\). At a fixed time it has one sign throughout the domain interior. The displayed Allen–Cahn snapshots appear to contain multiple positive and negative spatial lobes. This is an apparent discrepancy requiring provenance verification; it does not by itself establish that any numerical result is wrong.

Check the existing plotting script, domain, spatial frequency, and source checkpoint. Current simulation code uses the stated sine formula, but a current default does not identify the configuration of an older figure.

If the figure's source run is verified, correct the caption or benchmark description to match the actual experiments. Do not infer a new equation or domain merely from the image. If provenance cannot be established quickly, omit the unverified Allen–Cahn panel and its associated qualitative claim; if panel removal cannot be done reliably, omit the qualitative figure and its references. The numerical tables still carry the main evidence.

Replace “preserves the Allen–Cahn interfaces” with “recovers the Allen–Cahn field structure” if the manufactured smooth sinusoidal benchmark is the intended one. Add corruption level, seed, and snapshot times to the caption only when known.

**6. Narrow a few broad interpretations — useful, about 10–15 minutes**

These changes preserve the results and should add little or no length.

| Current wording or implication | Suggested correction |
| --- | --- |
| Squared loss “encodes no prior about the noise” (introduction and setup) | “We use the standard squared reconstruction loss to isolate the effect of adaptive weighting.” Squared loss has a Gaussian-likelihood interpretation, which the introduction already explains. |
| A standardized cutoff has “the same meaning for any estimator and at any stage” (Section 3.3) | “Standardization expresses the cutoff in units of the minibatch log-score standard deviation.” It does not provide a common false-positive rate or probability calibration. |
| naPINN uses density “only to order measurements” (real-data discussion) | “naPINN uses detached standardized density scores to weight measurements.” Soft weights depend on score spacing as well as ranking. |
| The frozen-gate experiment isolates learning the cutoff | Call it learning the gate, because both cutoff and steepness are frozen. |
| The fixed quantile gate “removes only 5%” | “In its hard-threshold interpretation, the 95th-percentile selector excludes approximately 5%.” The implemented sigmoid assigns continuous weights. |
| The full method is generally superior under unknown noise | Keep the result scoped to the tested settings. Retain the already reported Gaussian/Laplace and mild-drift exceptions. |

One short sentence can make the statistical interpretation more defensible:

> The weights represent residual-based inclusion scores rather than calibrated probabilities of sensor correctness; coherent corruption or rare valid dynamics can violate the association between residual typicality and reliability.

Place this near the existing limitations, replacing overlapping text if needed. Do not add a long new limitations section.

**7. Make easy reporting clarifications only if existing records are immediately available — secondary priority**

The current gate constructor initializes the pre-softplus cutoff to 2, giving an effective cutoff of approximately 2.127. The manuscript says the effective cutoff is 2. If the reported runs used this constructor, say “pre-softplus initialization \(\tilde\tau=2\), corresponding to \(\tau\approx2.13\).” Check the historical configuration before applying this to every run. Do not change the implementation to force agreement with the prose.

The manuscript summarizes additional real-data runs without full numerical tables. If an already verified aggregate can be inserted into the appendix in a few minutes, that would help. Otherwise avoid further expanding those claims. Never construct missing uncertainties or aggregate results from memory.

The distinction between ten-trial and three-seed experiments is already stated. Retain it. Describe small differences from PINN-EBM as lower observed mean errors, not established statistically significant improvements. There is no need to add a significance-testing exercise hours before submission.

Coefficient recovery is competitive with PINN-EBM, but PINN-EBM has lower mean coefficient error on all three reported simulated problems. The paper already gives those numbers. Keep them visible and avoid strengthening the title or abstract into a claim of superior coefficient identification. Moving the coefficient table into the main text is optional and probably not worth the layout risk now.

**Work to defer**

The earlier broad review identified useful future work. None of the following should become a new requirement for this deadline:

- Additional noise families, heteroscedasticity, narrow contaminating modes, or natural-fault labels.
- New real-data inverse-coefficient experiments or additional seeds.
- A redesigned ablation matrix, oracle selectors, or broader baseline tuning.
- A new robustness theorem, Bayesian extension, or EBM architecture.
- A major novelty rewrite, title change, or restructuring of the results section.
- A complete new code-release package if an anonymous reproducible package is not already prepared.

The existing limitations and precise claim wording are the appropriate response to these open questions at this stage. A limitation is acceptable; an unsupported guarantee is avoidable.

**Final checks before upload**

- Rebuild LaTeX and BibTeX using the existing workflow and resolve undefined references or citations.
- Check the final main-text page count. The reviewed PDF ends its main text on page 8, matching the eight-page limit in the supplied template; edits can change pagination.
- Inspect the abstract, Figure 2 or its replacement, Proposition 1, and the beginning of the references in the rendered PDF.
- If the qualitative figure is removed, remove every dangling reference and dependent descriptive sentence.
- Keep numerical results unchanged unless correcting a value against an existing verified record.
- Preserve anonymity and accurately describe code availability. Keep this internal feedback document out of the submission package.
- Open the uploaded PDF and verify that it is the intended final version.

**Submission judgment**

There is enough substantive work here to justify submission without another experimental campaign. The defensible contribution is improved field reconstruction through residual-density-based measurement weighting in the evaluated corruption settings, with competitive coefficient recovery. The immediate objective is a precise, internally consistent account of that contribution. Acceptance remains uncertain, but these limited revisions address concrete reviewer objections without destabilizing the paper in its final hours.
