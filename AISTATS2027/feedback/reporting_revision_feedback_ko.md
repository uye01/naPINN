**AISTATS 2027: 보고 방식과 기여 서술 개선 피드백**

작성일: 2026년 10월 4일

표현 지침 수정: 2026년 10월 5일. 저자 요청에 따라 PINN-EBM과의 차이가 보고된 표준편차 범위 안인 비교에만 작은 차이라는 설명을 붙인다. 그 외에는 결과가 뒷받침하는 `outperform`, `lowest` 등의 표현을 유지한다.

이 문서는 저자가 수용한 세 가지 제안, 즉 **② 기존 실제 데이터 결과의 보고 보강, ③ 작은 성능 차이의 정확한 표현, ⑤ 기여와 실험 결과의 중심 정렬**을 원고에 반영하기 위한 피드백이다. 현재 `naPINN_aistats2027.tex`를 기준으로 작성했으며, 행 번호는 후속 편집에 따라 달라질 수 있다. 이전 피드백의 다른 실험 제안은 이번 문서의 요구사항에 포함하지 않는다.

목표는 이미 수행한 실험의 증거를 독자가 더 쉽게 확인하게 하고, 그 증거가 지지하는 범위에 맞춰 주장을 다듬는 것이다. 추가 학습, 전체 실험의 추적표 작성, checkpoint 재평가는 요구하지 않는다. 이 문서의 영어 문장은 수정 예시이며, 실제 반영 시 확정된 표·수치와 일치시켜야 한다. 문서 작성 과정에서 원고·코드·실험 결과는 변경하지 않았다.

**② 기존 실제 데이터 결과의 보고 보강**

대상 위치: Section 5.2 “Real Measurements Under a Nominal PDE”, Table 2 (`tab:piv`), Appendix F “Additional Results on Real Measurements”의 “Additional scenarios” 및 “Structured corruption”. 현재 원고 약 565–623행, 1188–1236행이다.

**현재 문제.** 원고는 Controlled Cylinder·FSI·Foil에서 144회 실험을 수행했다고 설명하지만, 부록에서도 주로 최저 평균을 얻은 조건 수만 요약한다. Structured corruption 표 역시 best/second 두 방법만 보여준다. 이 형식으로는 독자가 다른 방법과의 차이, 변동성, 예외 조건을 직접 판단하기 어렵다. Cylinder의 Table 2도 세 seed의 평균만 제시한다.

**권장 수정.** 기존에 확보된 결과를 사용하여 부록에 다음 두 표를 보강한다. 본문의 Table 2와 핵심 설명은 유지할 수 있다.

| 부록 표 | 행 구성 | 보고할 값 |
| --- | --- | --- |
| 추가 RealPDEBench 시나리오 | Controlled Cylinder·FSI·Foil × 오염률 10%·15% × 비교한 모든 방법 | seed 수, rMAE 평균·표준편차, 상대 L2 오차 평균·표준편차 |
| Structured corruption | AR(1), spatial burst, persistent drift 10%·20%·30% × 비교한 모든 방법 | seed 수, rMAE 평균·표준편차, 상대 L2 오차 평균·표준편차 |

기본 열은 `Dataset/Condition | Corruption level | Method | n | rMAE, mean (s.d.) | Relative L2 error, mean (s.d.)`로 둔다. 표가 넓어지면 dataset이나 condition별 블록으로 나누고 중복 열을 생략한다. 표 안에서는 기존 원고의 지표명 `rMSE`를 유지해도 되지만, 캡션에서 relative L2 error임을 명시한다.

같은 결과를 보여주는 기존 best/second 표는 전체 결과 표로 대체하거나 간단한 본문 요약으로 옮길 수 있다. Cylinder 결과의 표준편차도 기존 자료에 있으면 같은 부록에 함께 제시한다. 본문 분량이 늘지 않도록 세부 수치는 부록에 두고, 본문에서는 핵심 차이와 예외만 설명한다.

기존 결과가 완전하지 않은 항목은 다음 원칙으로 처리한다.

- 원자료나 확정된 집계에 없는 표준편차는 만들어 넣지 않는다. 평균만 있으면 평균만 보고하고 변동성 수치가 없음을 표시한다.
- `n`은 실제 포함된 독립 학습 실행 수로 적는다. 데이터 벡터 수를 seed 수로 대체하지 않는다.
- 실험 설정이 다른 결과는 같은 조건의 반복처럼 합치지 않는다. PINN-EBM의 PDE weight처럼 구분에 필요한 설정은 방법명이나 캡션에 적는다.
- AR(1)·spatial burst에서 과거 집계와 저자 수정값의 방법별 대응이 다르다는 기록이 있다. 해당 셀만 **원고 수정 시 확인할 항목**으로 표시한다. 이번 피드백 작성에서는 어느 쪽이 맞는지 판정하거나 재실험하지 않는다. 값이 확정되기 전에는 기존 순위 주장을 더 강화하지 않는다.

**영어 문장 예시.** 다음 캡션은 실제로 표준편차를 확보한 표에만 사용한다.

> Results on the additional RealPDEBench scenarios with injected measurement corruption. Entries report the mean and sample standard deviation across training seeds; n denotes the number of runs included. Bold indicates the lowest observed mean for each metric and condition.

본문에서 현재의 순위 요약이 확정된 전체 표와 일치한다면 다음처럼 구체적으로 쓸 수 있다.

> Across the additional scenarios, naPINN has the lowest mean rMAE in all six dataset–severity conditions. OrPINN achieves a lower mean relative L2 error on FSI at both corruption levels. Complete results and variation across seeds are provided in Appendix F.

전체 결과가 확인되기 전에는 위 문장을 그대로 채택하지 않는다. Structured corruption의 승리 조건 수 역시 확정된 표에서 다시 센다.

**완료 기준.** 본문에 요약한 추가 시나리오와 구조적 오염 결과를 부록에서 방법별로 확인할 수 있고, 각 값의 반복 수와 변동성 제공 여부가 명확하다. 본문의 최저 평균·예외 조건 설명이 해당 표와 일치한다.

**③ PINN-EBM과의 작은 차이에 한정한 설명**

대상 위치: Section 5.1 첫 두 문단과 Table 1 (`tab:exact`), Section 5.2와 Table 2, Appendix F의 작은 차이 및 동률 해석. 현재 원고 약 522–537행, 592–608행이다.

**현재 문제.** PINN-EBM과의 일부 비교에서는 평균 차이가 반복 간 변동보다 작다. 예를 들어 Table 1의 Burgers 10%에서 rMAE는 naPINN 0.074, PINN-EBM 0.075이며, 각각의 표준편차는 0.009와 0.010이다. 이런 조건에는 차이의 크기를 짧게 설명하되, 다른 결과까지 일괄적으로 완곡하게 바꾸지 않는다.

**권장 수정.** `outperform`, `lowest`, `best`는 평가한 조건에서의 실험적 성능 비교 표현으로 유지한다. PINN-EBM과의 평균 차이가 보고된 표준편차 범위 안인 경우에만 인접 문장이나 한 번의 묶음 설명으로 작은 차이라는 점을 밝힌다. 가장 낮은 평균이라는 사실은 이 경우에도 그대로 보고할 수 있다.

문서 적용 시 “표준편차 이내”를 일관되게 해석하기 위해, 같은 조건·같은 지표에서 평균의 절대 차이 `Δ = |mean_naPINN − mean_PINN-EBM|`를 두 방법의 표준편차 중 큰 값과 비교한다. `Δ ≤ max(sd_naPINN, sd_PINN-EBM)`이면 짧은 설명을 붙이는 편집 기준으로 삼는다. 이는 통계적 유의성 판정이나 두 평균±표준편차 구간의 겹침 여부를 뜻하지 않는다. 이 내부 편집 기준을 논문에 새로운 통계 절차처럼 소개할 필요는 없다.

| 비교 상황 | 원고 표현 지침 |
| --- | --- |
| naPINN의 평균이 낮고 PINN-EBM과의 차이가 표준편차 이내 | 최저 평균·순위는 유지하고, 차이가 작다는 설명을 짧게 덧붙임 |
| naPINN의 평균이 낮고 PINN-EBM과의 차이가 표준편차보다 큼 | `outperforms PINN-EBM`, `achieves the lowest error` 등 기존 표현 유지 |
| 고정 robust loss 대비 개선 | 표가 뒷받침하는 기존 `outperform`, 개선율·배수 표현 유지 |
| 반올림 후 같은 수치 | 표시된 정밀도에서 같다고 설명하고 naPINN의 단독 승리로 세지 않음 |
| PINN-EBM의 평균이 더 낮음 | 해당 조건의 예외를 그대로 보고 |
| 표준편차가 보고되지 않은 조건 | 범위 안팎을 임의 판정하지 않고 기존의 정확한 평균 비교 표현 유지 |

현재 Table 1의 **rMAE**에 이 편집 기준을 적용하면 다음과 같다.

| PDE·오염률 | 평균 차이의 절댓값 Δ | 두 표준편차 중 큰 값 | 설명 여부 |
| --- | ---: | ---: | --- |
| Allen–Cahn 5% / 10% / 15% | 0.001 / 0.021 / 0.019 | 0.050 / 0.040 / 0.063 | 세 조건 모두 표준편차 이내임을 묶어서 설명; 5%는 PINN-EBM이 낮음 |
| Burgers 5% / 10% / 15% | 0.000 / 0.001 / 0.005 | 0.010 / 0.010 / 0.020 | 세 조건 모두 작은 차이임을 묶어서 설명; 5%는 표시 정밀도에서 동률 |
| λ–ω 5% | 0.007 | 0.009 | 작은 차이라는 설명 추가 |
| λ–ω 10% / 15% | 0.017 / 0.028 | 0.010 / 0.008 | 기존 우위 표현 유지 |

위 계산은 현재 표의 반올림된 수치를 사용한다. 경계에 가까운 비교는 원래 정밀도의 값이 있으면 그것으로 확인한다. rMSE와 다른 지표에는 각각의 평균·표준편차를 사용하며, rMAE의 분류를 그대로 적용하지 않는다. 최종 표의 값이 바뀌면 해당 설명도 함께 갱신한다.

새로운 p-value 계산, bootstrap 분석, seed 추가 또는 paired 분석은 요구하지 않는다. 표준편차 이내라는 이유로 동등하다고 결론내리거나, 표준편차 밖이라는 이유로 `statistically significant`라고 쓰지만 않으면 된다.

표의 굵은 글씨·밑줄과 기존의 “Best in bold, second best underlined” 설명을 유지한다. 모든 캡션에 통계적 유의성이 아니라는 경고 문장을 추가할 필요는 없다.

**영어 문장 예시.** PINN-EBM과의 rMAE 비교는 여러 조건을 한 문장으로 묶어 설명할 수 있다.

> The rMAE differences from PINN-EBM are within the reported standard deviations on Allen–Cahn and Burgers, as well as on the lambda–omega system at 5% outliers.

차이가 더 큰 λ–ω 조건의 우위는 그대로 강조한다.

> naPINN outperforms PINN-EBM on the lambda–omega system at 10% and 15% outliers, reducing rMAE by approximately 19% and 27%, respectively.

고정 robust loss 대비 본문의 큰 개선도 유지한다.

> At 15% outliers, naPINN outperforms the best fixed robust-loss baseline, with approximately 2.0-, 2.4-, and 2.0-fold lower rMAE on Allen–Cahn, Burgers, and the lambda–omega system, respectively.

**완료 기준.** PINN-EBM과의 작은 차이는 해당 조건에 한정해 설명하고, 그 외의 검증된 우위에는 기존 `outperform`, `lowest` 표현을 유지한다. 평균 순위 설명을 일괄적으로 약화하지 않으며, 표준편차 비교를 유의성 검정 또는 동등성 주장으로 바꾸지 않는다.

**⑤ 기여와 실험 결과의 중심 정렬**

대상 위치: Abstract, Introduction의 기여 목록, Section 5.1 “Coefficient recovery”, Section 6 “Discussion”, Appendix E의 계수 복원 결과. 현재 원고 약 54–70행, 126–139행, 554–563행, 745–767행, 1155–1179행이다.

**현재 문제.** 원고의 제목과 도입부는 physics recovery와 unknown coefficient를 강조하지만, 가장 뚜렷한 실험적 강점은 오염된 관측에서의 field reconstruction이다. 현재 계수 오차 표에서는 PINN-EBM의 평균 오차가 세 합성 문제 모두 더 낮고, 실제 PIV에서는 Reynolds number를 고정한다. 이 구분이 흐려지면 field 성능 개선이 곧 coefficient identification의 우위인 것처럼 읽힐 수 있다.

원고의 “all of these errors are small in absolute terms”도 바꾸는 편이 좋다. 실제 계수가 작은 Burgers viscosity에서는 작은 절대 오차라도 상대 오차는 의미 있는 크기일 수 있다.

**권장 수정.** 초록·기여·결론의 첫 성과를 field reconstruction에 두고, coefficient recovery는 별도의 경쟁력 있는 결과로 설명한다. 제목 변경이나 섹션 재배치는 필수로 하지 않는다.

- 초록: field error 개선을 중심으로 유지한다. 계수 복원 문장을 추가한다면 competitive라는 범위로 제한하고, 현재 본문에 없는 우위를 만들지 않는다.
- 기여 목록: 제안 방법, 측정 가중치의 역할, 평가한 gross-corruption 조건에서의 field reconstruction 결과를 중심으로 정리한다.
- 계수 결과: 상대 오차를 기준으로 해석한다. PINN-EBM보다 모든 계수에서 우수하다고 쓰지 않는다.
- 실제 PIV: 고정된 Reynolds number 아래의 field reconstruction이라는 점을 유지한다. 실제 데이터에서의 계수 식별 성과로 인용하지 않는다.
- Discussion: field reconstruction과 coefficient identification을 구별한 뒤, 평가한 오염 조건에서의 기여를 요약한다.
- Proposition: 목적함수·gate·선택 규칙을 설명하는 해석적 결과로 위치시킨다. 일반적 robustness 보장이나 estimator의 일관성 정리로 확대하지 않는다. 추가 정리는 요구하지 않는다.

**영어 문장 예시.** 중심 주장에는 다음 문장을 사용할 수 있다.

> naPINN improves field reconstruction under the evaluated gross-corruption settings while maintaining competitive coefficient recovery.

현재 원고에 제시된 계수 결과를 설명하는 대안은 다음과 같다.

> At 15% outliers, naPINN has relative coefficient errors of 0.9%, 7.2%, and 1.4% on Allen–Cahn, Burgers, and the lambda–omega system, respectively. PINN-EBM has slightly lower mean coefficient errors in all three cases. These results distinguish naPINN's field-reconstruction gains from its coefficient-identification performance.

실제 PIV의 범위는 다음처럼 명시할 수 있다.

> The real-PIV experiments evaluate field reconstruction under a fixed metadata Reynolds number; they do not evaluate coefficient identification from real measurements.

이론 부분의 역할은 다음처럼 표현할 수 있다.

> Proposition 1 characterizes the gate objective and its connection to residual selection. It provides an interpretation of the method rather than a general guarantee of robustness or coefficient recovery.

위 예시의 계수 수치는 현재 원고에서 가져온 것이며, 새로 재평가한 결과가 아니다. 최종 표가 수정되면 문장도 함께 바꾼다.

**완료 기준.** 초록·기여·결론이 같은 중심 주장을 전달한다. Field 개선을 coefficient 우위로 확대하지 않고, 실제 PIV의 고정 계수 설정이 분명하다. 명제의 해석적 역할을 유지하면서 추가 이론이나 구조 개편 없이 수정이 완료된다.

**권장 반영 순서와 최종 확인**

먼저 ⑤의 중심 주장을 정리하고 ③의 결과 표현을 수정한다. 이후 ②의 전체 결과 표를 기존 자료로 보강하고, 그 표에 맞춰 본문의 승리 조건 수와 예외를 확인한다. 상세 표를 부록에 두면 본문 분량 증가를 제한할 수 있다.

최종 확인은 다음 다섯 가지면 충분하다.

- 추가 실제 데이터 조건에서 보고한 방법·수치·반복 수가 부록 표와 맞는가?
- 확보되지 않은 표준편차나 새로운 실험 결과가 문장 예시에 섞이지 않았는가?
- PINN-EBM과의 표준편차 이내 차이에는 짧은 설명을 붙이고, 다른 우위 표현은 유지했는가? 표준편차 비교를 유의성이나 동등성의 근거로 쓰지 않았는가?
- 계수 복원과 실제 PIV의 평가 범위가 초록·본문·결론에서 일치하는가?
- 원고 반영 후 본문 페이지 제한과 표·부록 교차참조를 확인했는가?

이 세 가지 개선은 기존 실험을 더 충실하게 보여주고 결과 해석을 정확하게 만드는 작업이다. 이번 피드백의 완료를 위해 새로운 실험을 추가할 필요는 없다.
