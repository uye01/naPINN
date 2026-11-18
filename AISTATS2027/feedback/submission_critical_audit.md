**Submission-critical audit — 30 September 2026**

2026-10-04 업데이트: 아래 지적 중 상당수가 현재 원고에서 수정되었다. 최신 상태와 남은 3일의 실험 계획은 `three_day_feedback_ko.md`에 정리했다. 이 문서는 당시 감사 기록으로 보존한다.

This is a focused follow-up to `submission_deadline_feedback.md`. It distinguishes confirmed errors from broader reviewer concerns. No experiments are required for the corrections below. The manuscript, bibliography, and submission ZIP were inspected; an isolated copy was rebuilt under `/tmp` so the submission files were not overwritten. The bibliography was also being updated during this audit, so resolved items are listed separately.

**Confirmed errors to correct before submitting**

1. **Wrong author names in `Ruff2018`.** In `references.bib`, around line 357, the author list contains `S. Ahmed and S. A. Binder`. The official PMLR record gives **Shoaib Ahmed Siddiqui** and **Alexander Binder**. Replace those two names with `S. A. Siddiqui and A. Binder`. The incorrect names are present in the generated bibliography as well. Rebuild BibTeX and LaTeX after correcting the source.

   Verified source: [Deep One-Class Classification, PMLR 80](https://proceedings.mlr.press/v80/ruff18a.html).

2. **The Allen–Cahn domain is inconsistent with both the supplementary code and an existing run record.** Appendix C, around manuscript line 1001, says `[0,1]^2 × [0,1]`. The submission ZIP's `naPINN_code/configs/paper/allencahn2d.yaml` instead specifies `x: [0,2]`, `y: [0,2]`, and `t: [0,2]`. The stored configuration at `outputs/rebuttal/wallclock_isolated_20260728/allencahn2d/4G/15pct/mse/ema_0.05_reject_0.5_pde_1_data_1/seed_40/config.yaml` agrees with the ZIP. The formula is still `sin(pi*x) sin(pi*y) cos(8*t)`.

   Correct the manuscript domain to `[0,2]^2 × [0,2]` for those experiments. Verify that the ten-trial set uses the same domain before applying a single description to both experiment sets. This evidence also explains the multiple spatial lobes in Figure 2; it is now more likely a domain-description error than an erroneous figure. There is no reason to discard the figure solely because of the earlier `[0,1]` concern if its run configuration agrees. Changing the formula to fit the image would be the wrong correction.

3. **The q-Gaussian variance statement is mathematically false.** Appendix D, around line 1077, says the chosen scale “normalizes the variance.” For the density displayed in the paper, ordinary variance exists only for `q < 5/3`; the tested `q = 1.9` and `q = 2.9` have infinite ordinary variance. Replace the clause with “we use the scale convention ...” and keep the actual formula. No change to the experiment is needed.

4. **Proposition 1(c) incorrectly states a necessary condition.** Around line 364, change “only when” to a sufficient-condition statement: “when the log-density is symmetric about zero and strictly decreasing in absolute residual magnitude.” In Appendix A, replace the corresponding “Otherwise ... it is not an interval centered at zero” assertion with “For general asymmetric or multimodal densities, superlevel sets need not be intervals centered at zero.” This fixes the logic without adding theory.

5. **The EBM normalization domain must be explicit.** Equation 4 leaves the integral domain unspecified, while the implementation integrates on `[-10,10]`. With the bounded tanh MLP used here, the exponentiated score is not integrable over all of the real line. State the finite integration domain and call the fitted criterion a finite-grid likelihood objective or surrogate. Do not assert a proper full-support density, or claim that residuals always stay inside the interval without records establishing that. The earlier feedback document gives replacement wording. This is a method-description correction; do not change the trained algorithm now.

**Two other inexpensive factual clarifications**

- The abstract's detection percentages refer to **injected corruption on real PIV**, not independently labeled natural sensor failures. Say “injected corrupted components” and “components without injected corruption.” This removes an avoidable ambiguity in the headline claim.
- In Section 3.3, replace the general guarantee “prevents the trivial solution” with “discourages excessive rejection.” Replace “vanishing influence however large its residual” with the fixed-residual statement in the earlier feedback document. The displayed gradient itself can stay.

**Citation error found and already resolved in the latest files**

The initial version of `Wong2022FLS` incorrectly listed `Senior Member, IEEE` as an author and abbreviated Yew-Soon Ong as `Y. Ong`. On the final recheck, both `references.bib` and the generated `.bbl` correctly list `J. C. Wong and C. C. Ooi and A. Gupta and Y.-S. Ong`. No further author correction is needed for this entry if that version is submitted.

The verified publication is *Learning in Sinusoidal Spaces With Physics-Informed Neural Networks*, IEEE Transactions on Artificial Intelligence 5(3), 985–1000, March 2024, [DOI 10.1109/TAI.2022.3192362](https://doi.org/10.1109/TAI.2022.3192362). The DOI's 2022 component and the BibTeX key `Wong2022FLS` do not make the 2024 journal year incorrect.

**Checks that passed**

- All **42 cited keys** exist in the bibliography. No duplicate BibTeX keys were found.
- All manuscript cross-reference labels resolve, with no duplicate labels found.
- All seven referenced figure files exist.
- An isolated LaTeX/BibTeX rebuild succeeds. After the additional stabilization pass, there are no unresolved citation or reference warnings.
- The main text ends on **page 8**; references begin on page 8, the checklist is on page 11, and the full PDF is 20 pages. This meets the main-text length stated in the supplied template. It is not an independent check of every submission-portal rule.
- The PDF uses US Letter and anonymous author/institution placeholders. Its Author metadata field is blank.
- A targeted scan of the supplementary ZIP found no obvious personal email, home-directory path, or author-repository URL. Its visible repository links point to the cited RealPDEBench project. This was a screening check, not a guarantee against every possible identifying detail.
- Targeted external metadata checks support the recorded identities of PINN-EBM, LAD/MAD-PINN, OrPINN, QRes, PirateNets, CoPINN, the two test-time-adaptation papers, and several foundational references. RealPDEBench's official repository confirms its ICLR 2026 citation and the OpenReview identifier in the paper. The duplicate initials `W. Yao` in `Peng2022` are legitimate: Wen Yao and Weijie Yao are different authors.

Useful verified records include [PINN-EBM](https://proceedings.mlr.press/v242/pilar24a.html), [LAD/MAD-PINN](https://arxiv.org/abs/2210.10646), [OrPINN](https://doi.org/10.1103/PhysRevE.111.L023302), [QRes](https://doi.org/10.1137/1.9781611976700.76), [PirateNets](https://www.jmlr.org/papers/v25/24-0313.html), [CoPINN](https://proceedings.mlr.press/v267/duan25b.html), and the [official RealPDEBench citation](https://github.com/AI4Science-WestlakeU/RealPDEBench#-citation). This was a targeted metadata audit, not verification of every claim against the full text of all 42 references.

**Warnings that are not submission blockers by themselves**

The log contains duplicate PDF destinations for figure/table anchors, a small overfull box near the title block, and a float-placement adjustment. These do not represent missing citations or failed compilation. Check clickable figure/table references in the final PDF; fix their anchors if they land incorrectly. Do not spend the final submission window eliminating harmless layout warnings while the confirmed errors above remain.

Bibliography keys with old years, such as `Chandola2013` rendering a 2009 article or `Liu2024KAN` rendering the ICLR 2025 paper, are not errors by themselves. Internal keys need not equal publication years. Incomplete page/DOI fields and title-capitalization cleanup are lower priority than correcting author identities.

**Minimum completion condition**

Correct the Ruff author names, reconcile the Allen–Cahn domain, remove the false variance statement, repair Proposition 1(c), and describe EBM normalization accurately. Apply the short corruption-label clarification. Then rebuild BibTeX and LaTeX to convergence, inspect page 8 and the relevant bibliography entries, and upload the verified final PDF and intended supplementary ZIP. These are targeted corrections, not a request for additional experiments.
