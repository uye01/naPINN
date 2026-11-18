**AISTATS 2027 제출 3일 전 피드백 — 2026년 10월 4일 재검토**

이 문서는 9월 30일의 “몇 시간 안에 제출”을 전제로 한 실행 우선순위를 대체한다. 현재 원고, 기존 피드백, 실험 집계 파일, 실험 이력 문서를 다시 확인했다. 이번 작업은 검토와 계획 작성이며, 추가 학습이나 체크포인트 재평가는 실행하지 않았다. 아래 기존 수치는 저장된 집계에서 읽은 값으로, 원고에 옮기기 전 개별 실행 기록과의 대응 확인이 필요하다.

**전체 판단**

현재 논문은 오염된 관측값으로부터 장을 복원하는 실용적 방법론으로서 제출할 만한 실험적 기반이 있다. 이전에 지적한 인용·수학 오류도 상당 부분 수정되었다. 남은 3일의 가장 큰 기회는 실험 종류를 무작정 늘리는 데 있지 않다. 핵심 표의 수치 출처를 확정하고, 밀도 점수를 쓰는 효과를 공정하게 비교하며, 이미 존재하는 무주입 데이터 결과로 적용 범위를 설명하는 데 있다.

우선순위는 **① 결과 출처 확인 → ② 기존 결과 재분석·보고 → ③ 핵심 gate 비교 실험 → ④ 선택적 추가 실험**이다. 출처가 해결되지 않으면 추가 실험 예산을 재현에 먼저 써야 한다. 방법 자체나 EBM 구조를 바꾸는 대규모 작업은 이번 제출 범위를 넘어선다.

**1. 이전 지적의 현재 상태**

| 항목 | 현재 확인 상태 | 남은 작업 |
| --- | --- | --- |
| Ruff 논문 저자명 | `S. A. Siddiqui`, `A. Binder`로 수정됨 | 최종 PDF와 BibTeX 일치 확인 |
| Wong 논문의 가짜 IEEE 저자 | 삭제되어 있음 | 추가 수정 불필요 |
| Allen–Cahn 정의역 | 원고가 `[0,2]^2 × [0,2]`로 수정됨 | 10회 반복과 3-seed 실험 각각의 원본 설정 연결 |
| q-Gaussian 분산 설명 | scale convention 및 무한분산 설명으로 수정됨 | 추가 실험 불필요 |
| Proposition 1(c)의 필요조건 오류 | 명제와 증명은 충분조건으로 수정됨 | 직후의 “The two rules agree” 문장은 아직 과도함 |
| EBM 적분 구간 | `D=[-10,10]` 및 구간 밖 점수 계산이 명시됨 | 구간 밖에서는 정규화된 밀도가 아닌 점수·surrogate라는 구별 보완 |
| 초록의 실제 PIV 주장 | 주입 오염임을 명시함 | 서론과 결과의 “clean” 표현도 같은 기준으로 정의 |
| gate 초기값 | pre-softplus와 실제 cutoff 차이를 설명함 | 그림·표·코드 패키지의 표기 일치 확인 |

현재 문법 오류도 하나 남아 있다. 방법 부분에 `..., and an excluded` 다음 줄이 `For a fixed residual ...`로 이어진다. 앞 문장을 수식 뒤에서 마침표로 끝내고 남은 `and an excluded`를 삭제하면 된다. 현재 원고 약 292행이다.

명제 다음 해석은 “동일한 선택 집합”과 “동일한 순위”를 구분해야 한다. 예를 들면 다음 문장으로 고칠 수 있다.

> For a density symmetric about zero and strictly decreasing in absolute residual magnitude, density and magnitude induce the same ordering; their selected sets agree when the thresholds are matched.

**2. 가장 먼저 할 일: 결론을 바꾸는 수치의 출처 확정**

이전 검토에서는 원고의 수치를 중심으로 보았지만, 이번에는 저장된 집계와 수정 이력을 확인했다. 두 부분에 결론을 바꿀 수 있는 불일치가 남아 있다. 이를 곧바로 원고의 오류라고 단정할 수는 없다. 이력에는 저자가 다른 실행의 수정값을 제공했다고 기록되어 있기 때문이다. 다만 그 실행과 표의 대응을 이번 제출 전에 명확히 해야 한다.

**A. residual-magnitude gate의 결과**

| PDE | 현재 Table 3의 rMAE | 저장된 threshold 집계의 rMAE |
| --- | ---: | ---: |
| Allen–Cahn | 0.244 | 0.24415 |
| Burgers | 0.345 | 0.08557 |
| λ–ω | 0.148 | 0.06730 |

저장된 집계는 `outputs/rebuttal/synthetic_supplement_recovery_20260726/aggregation_strict.json`이며, 해당 그룹은 `method=threshold`, seeds 40–42, gross outliers 15%다. 이 차이는 `docs/PROGRESS.md`의 “Selector lineage correction”과 `rebuttal/response_matrix.md`에도 기록되어 있다.

현재 naPINN의 Table 3 값은 Burgers 0.082, λ–ω 0.071이다. 저장된 threshold 결과와 비교 가능하다고 확인된다면 “밀도 점수가 반드시 필요하다”는 해석은 성립하지 않거나 상당히 약해진다. 따라서 단순 소수점 오차로 처리할 수 없다.

**B. 구조적 오염에서 방법 이름과 수치의 대응**

| 조건 | 현재 원고에서 naPINN에 부여한 rMAE | 저장 집계의 LAD rMAE | 저장 집계의 naPINN rMAE |
| --- | ---: | ---: | ---: |
| AR(1) | 0.123 | 0.12291 | 0.15036 |
| Spatial burst | 0.113 | 0.11321 | 0.15318 |

출처는 `outputs/rebuttal/realpde_recovery_20260726/injected_piv_aggregation_strict.json`이다. `rebuttal/response_matrix.md`에는 저자가 별도 실행의 수정값을 제공했으나 그 실행이 당시 저장소에 없었다는 설명이 있다. 현 원고의 “5개 중 4개에서 최상위”는 어느 실행을 쓰는지에 따라 달라질 수 있다.

**처리 방법과 완료 기준**

각 셀에 대해 `실험 설정 → 데이터 식별자/해시 → seed → metrics → checkpoint → 집계`를 연결한다. 최소한 방법명, 실제 loss와 gate 활성 여부, rejection cost, warm-up을 포함한 업데이트 수, 평가 분할, 계수 고정 여부가 일치해야 한다. 수정값의 실행 기록을 찾으면 그것을 근거로 재집계한다. 기존 집계가 다른 프로토콜이라면 차이를 명시하고 분리한다.

6–8시간 이내에 원본이 복구되지 않으면 해당 비교를 동일한 고정 프로토콜로 다시 실행한다. 새 실행은 “확인 실험”으로 보고하고 기존 10회 반복에 섞지 않는다. 최종적으로도 검증할 수 없는 셀은 주장의 근거에서 제외한다. 파일 이름이나 방법 라벨만 바꾸어 수치를 맞추면 안 된다.

필요한 재현 규모는 다음과 같다. 원본이 복구되면 모두 생략할 수 있다.

- threshold 문제: Burgers·λ–ω × naPINN·threshold × 3 seeds = **12회**. 비교 가능한 naPINN 실행이 이미 검증되면 추가 학습은 6회로 줄어든다.
- 구조적 오염 문제: AR(1)·spatial burst × naPINN·LAD × 3 seeds = **12회**. 원고와 같은 rejection cost 및 데이터 프로토콜로 맞춘다.

**3. 새 실험보다 먼저 반영할 기존 결과: 무주입 PIV와 gross-outlier 0%**

이 조건들은 새로 시작할 필요가 없다. 이미 집계가 존재한다.

- `outputs/rebuttal/natural_piv/aggregation.json`: naPINN의 세 reconstruction loss, 9회, `status=complete`.
- `outputs/rebuttal/natural_piv_baselines/aggregation.json`: ungated baseline 및 PINN-EBM PDE weight 비교, 18회, `status=complete`.
- `outputs/rebuttal/synthetic_background_only/aggregation.json`: 3개 PDE의 naPINN·PINN-EBM, 18회. 4-Gaussian 배경 잡음은 유지하고 gross offset만 0%로 둔 조건이다.

무주입 PIV 집계에서 읽은 평균은 다음과 같다. 아직 이번 검토에서 모든 개별 실행의 해시를 다시 검증한 것은 아니므로, 이 표는 원고 반영 후보로 취급한다.

| 방법 | rMAE | 상대 L2 오차 |
| --- | ---: | ---: |
| MSE-PINN | 0.13976 | 0.19822 |
| naPINN-MSE | 0.13935 | 0.19775 |
| LAD-PINN | 0.11211 | 0.18353 |
| naPINN-L1 | 0.11242 | 0.18675 |
| OrPINN q=2.9 | 0.12143 | 0.18568 |
| naPINN-q2.9 | 0.12256 | 0.18950 |

이 결과는 자연 잡음만 있는 PIV에서 gate가 동일 loss의 baseline보다 추가 이득을 준다는 주장을 지지하지 않는다. 반대로 “gross corruption이 있을 때 유용하며, 없는 조건에서는 reconstruction loss 선택이 더 중요할 수 있다”는 적용 범위를 설명하는 데 유용하다. 자연 PIV에는 정답 고장 라벨이 없으므로 detection AUROC나 clean rejection rate를 만들지 않는다.

합성 gross-outlier 0% 집계에서는 PINN-EBM이 세 PDE 모두 낮은 평균 오차를 보인다. 특히 Burgers rMAE는 PINN-EBM 0.03737, naPINN 0.07537이다. 다만 이 실험은 별도 서버에서 reference simulation을 재생성했다는 이력이 있으므로, 데이터가 동일하다는 검증 없이 본문의 5/10/15% 곡선에 0% 점을 그대로 이어 붙이지 않는다. 별도 대조 실험으로 보고하거나 동일 데이터로 확인한다.

권장 결과물은 부록의 작은 표와 본문의 적용 범위 2–3문장이다. 불리한 결과도 같은 비교 기준으로 제시한다. 이 자료를 반영하면 “왜 모든 잡음에서 우수하지 않은가”에 대해 이미 있는 증거로 답할 수 있다.

**4. 추가 실험 1순위: 비교 조건을 맞춘 density gate 대 magnitude gate**

**답할 질문:** 밀도 추정의 이점이 residual magnitude보다 유용한 점수를 제공하기 때문인가, 아니면 초기 cutoff·steepness·점수 스케일 차이 때문인가?

현재 Table 3은 유용하지만 완전한 2×2 통제 실험은 아니다. density와 magnitude gate의 초기값이 다르고, 한쪽의 fixed는 초기 파라미터 고정인 반면 다른 쪽은 매 minibatch의 95% 분위수를 사용한다. 같은 sigmoid라는 사실만으로 비교 조건이 같아지는 것은 아니다.

**권장 최소 설계: 18회**

3개 PDE × 2개 점수 방식 × seeds 40–42, gross corruption 15%, 같은 squared loss와 rejection cost를 사용한다. 점수 방식은 다음 둘이다.

- density: 학습한 EBM log-score.
- magnitude: `-|normalized residual|`.

두 점수 모두 동일한 방식으로 표준화하고 detach한 뒤 같은 gate 클래스에 넣는다. 동일한 warm-up checkpoint, 측정 데이터, PINN 초기 상태, PINN 업데이트 예산을 사용한다. EBM의 추가 초기화로 난수 소비가 달라질 수 있으므로 동일 seed라는 이유만으로 minibatch까지 같다고 가정하지 말고, PINN sampling RNG를 분리하거나 배치 순서를 고정한다.

초기 수용률과 전이 폭을 가능한 한 같게 맞춘다. 예를 들어 warm-up의 훈련 잔차만으로 초기 수용률 95%가 되도록 cutoff를 정하고, 동일하게 사전 지정한 분위수 구간에서 gate 전이가 일어나도록 steepness를 정한다. 이 규칙은 결과를 보기 전에 고정하고, 평가 오차나 오염 정답 라벨은 사용하지 않는다. 실제 초기 수용률과 soft weight 분포도 저장한다.

이 실험은 초기화가 달라진 **추가 통제 실험**이다. 기존 기본 naPINN과 동일한 설정이라고 표시하지 않는다. 기존 Table 3을 조용히 덮어쓰지 말고, 확인된 기존 결과 옆이나 부록에 구분하여 제시한다. 새 실험의 결론은 이 통제된 초기화 조건에 한정한다.

기록할 지표는 seed별 field rMAE·상대 L2 오차, 계수 오차, 오염/비오염 성분 rejection rate, 평균 gate weight, 실행 시간이다. 검증용 곡선이나 학습 중 checkpoint가 있다면 retention 변화도 유용하지만, 최종 seed별 비교보다 우선하지 않는다.

결과 해석을 사전에 정해 둔다. density가 일관되게 낮은 오차를 내면 기작 주장이 강화된다. 비슷하면 “학습한 density가 필수”라는 표현을 철회하고 density-conditioned weighting이라는 설계와 적용 범위에 기여를 둔다. magnitude가 이기면 해당 조건을 그대로 보고한다.

**5. 추가 실험 2순위: 오염률을 아는 residual selector — 여유가 있을 때 9회**

현재 95% 분위수 selector는 15% gross corruption에서 약 5%만 제외하도록 설계되어 있다. “단순 trimming보다 낫다”는 주장을 평가하기에는 약한 대조군이다.

3개 PDE × 3 seeds에서 absolute residual의 상위 15%를 제외하는 **85% 분위수 selector**를 학습 과정에 적용한다. warm-up, 전체 PINN 업데이트 수, base loss와 sampling 규칙을 맞춘다. hard trimming 또는 soft approximation 중 하나를 시작 전에 정하고 실제 제외율을 보고한다. 마지막 checkpoint에만 적용하는 사후 필터는 같은 실험이 아니다.

이 방법은 실제 오염률을 안다는 추가 정보를 쓰므로 `oracle contamination-rate baseline`으로 명시한다. 목적은 실용적 기본값을 고르는 것이 아니라, 알려진 trimming 비율만으로 naPINN의 이득이 설명되는지 확인하는 것이다. 85%를 최종 오류를 보고 선택한 최적값처럼 제시하지 않는다.

1순위의 18회와 합하면 **27회**다. 이 둘을 완료하면 세부 novelty와 비교 공정성에 관한 핵심 질문에 답할 수 있다. 새로운 PDE나 backbone을 추가하는 것보다 우선한다.

**6. 추가 실험 3순위: 아래 중 하나만 선택**

앞의 출처 확인과 핵심 비교가 끝나고 시간이 남았을 때만 시행한다.

| 선택지 | 답할 질문 | 제한된 설계 |
| --- | --- | --- |
| 별도 calibration으로 선택한 fixed density gate | 학습한 gate의 이득이 나쁜 초기 cutoff와의 비교 때문인가? | 사전 지정한 PDE 1개에서 별도 calibration seed로 cutoff 후보 3개 비교 후 고정, 평가 seeds 3개: 6회. calibration 선택 기준·사용한 정답 정보 공개 |
| 가장 강한 robust baseline의 작은 loss-balance 점검 | 모든 방법에 PDE weight 1을 주는 것이 loss scale 차이 때문에 불리한가? | baseline 1개·PDE 1개, 사전 지정한 두 추가 weight를 별도 calibration에서 비교 후 선택한 설정을 3 seeds로 평가. test 성능으로 선택하지 않음 |
| 좁은 coherent outlier mode stress test | 밀도가 높은 고장 군집을 gate가 신뢰하는가? | PDE 1개·오염 조건 1개·방법 3개·3 seeds: 9회. noise/gross 규모 사전 고정, 실패 여부와 무관하게 보고 |

개인적으로는 fixed density gate 검증을 먼저 권한다. 그러나 결과 출처 재현이 필요해졌다면 이 단계는 모두 생략한다. 새 오염 분포에서 naPINN이 유리해질 때까지 강도나 평균을 바꾸는 탐색은 이번 일정에 넣지 않는다.

**7. 학습 없이 보강할 통계·보고 방식**

현재 원고에는 큰 개선과 매우 작은 차이가 함께 있다. Burgers의 naPINN 대 PINN-EBM처럼 차이가 작은 비교에는 “최저 평균”과 “유의한 우수성”을 구분해야 한다.

- 동일 데이터·초기화 등 pairing이 확인된 경우에만 `각 seed의 naPINN 오차 − baseline 오차`를 계산한다. 같은 seed 번호만으로 다른 실험 묶음을 짝짓지 않는다.
- 3 seeds에서는 개별 값, 평균 차이, 승리한 seed 수를 우선 제시한다. 불안정한 bootstrap 구간이나 p-value 하나로 강한 통계적 주장을 하지 않는다.
- 10회 반복 원자료가 있으면 pairing을 확인한 뒤 seed 단위 불확실성을 제시한다. 표의 평균·표준편차만으로 paired 차이의 불확실성을 역산할 수는 없다.
- PIV의 수백만 벡터를 독립 반복 실험 수로 취급하지 않는다. 공간·시간 상관이 있다.
- 추가 144회 RealPDEBench 실험과 structured corruption은 “누가 몇 번 이겼다”뿐 아니라 방법별 평균·표준편차·seed 수를 부록에 제시한다. 존재하는 검증된 결과를 재집계하는 작업이다.
- field recovery와 coefficient recovery를 분리한다. 현재 보고된 계수 오차에서 PINN-EBM보다 일관되게 우수하다고 주장하지 않는다.

**8. 계산량과 72시간 실행 순서**

현재 GPU의 가용 자원은 확인하지 않았으므로 아래는 예약 보장이 아닌 계획용 추정이다. 원고의 A6000 시간은 합성 실험 1회 약 20–25분이고, 저장된 natural-PIV 집계는 약 28–36분이다. 환경·GPU 경쟁에 따라 더 오래 걸릴 수 있다. 첫 완전 실행의 시간으로 즉시 재산정한다.

| 경과 시간 | 우선 작업 | 종료 시 확보할 것 |
| --- | --- | --- |
| 0–6시간 | 수치 출처 확인, 작은 원고 오류 수정, 기존 natural-PIV 비교 가능성 확인 | 핵심 표의 셀-실행 대응표, 추가 실험의 고정 설정 |
| 6–24시간 | 출처 복구 실패 셀 재현 또는 18회 gate 비교 시작 | 첫 결과와 실제 실행 시간, 완전 실행 기록 |
| 24–48시간 | 확정한 비교 완료, 여유 시 oracle 9회, 기존 결과 재집계 | seed별 표·통제 실험 결과·보고할 실패 사례 |
| 48–60시간 | 논문 문장·표·부록 반영 | 주장이 확인된 결과와 일치하는 원고 |
| 60–72시간 | 새 실험 시작 중단, PDF·익명 코드·인용·업로드 점검 | 최종 제출 파일 및 여유 시간 |

출처 문제가 해결되면 핵심 27회에 약 9–14 GPU-hours를 계획하되 구현·재평가·실패 대응 시간을 따로 둔다. 출처 복구가 안 되어 24회 재현이 필요하면 그것을 먼저 수행하고, 추가 gate 비교는 사전 지정한 PDE 1개에서 6회로 줄이거나 다음 단계로 미룬다. 이번 추가 학습은 대략 30회 안팎을 목표로 잡고, 모든 선택지를 동시에 진행하지 않는다.

선택할 PDE를 결과를 본 뒤 바꾸지 않는다. 축소가 필요하면 구현과 analytical reference 확인이 쉬운 Allen–Cahn을 먼저 고정할 수 있지만, 단일 PDE 결과로 세 문제 모두에 대한 기작을 일반화하지 않는다.

기존 산출물은 덮어쓰지 않는다. 새 실험은 별도 디렉터리에서 코드 버전, resolved config, 데이터 식별자, seeds, 실제 PINN update 수, 실패 여부와 종료 이유를 저장한다. 실패한 seed를 임의 교체하거나 성능이 좋은 checkpoint만 사후 선택하지 않는다. 방법 수정 시 기존 수치를 새 버전의 결과처럼 혼합하지 않는다.

**9. 논문에서 유지할 주장과 줄일 주장**

가장 방어하기 좋은 중심 문장은 다음과 같다.

> naPINN uses learned residual-density scores to control measurement inclusion, improving field reconstruction under the evaluated gross-corruption settings while maintaining competitive coefficient recovery.

새 통제 실험을 통과하더라도 “모든 unknown noise에서 우수하다”, “density는 언제나 sensor reliability를 뜻한다”, “밀도 추정 없이는 좋은 결과를 얻을 수 없다”로 확장하지 않는다. 기존 Gaussian/Laplace 결과, 자연 PIV 결과, mild drift 예외를 함께 설명한다.

현재 “2×2 design” 표현은 비교 규칙이 통일되기 전에는 완화하는 편이 좋다. “four selector variants”처럼 쓰고, 무엇이 고정되고 무엇이 매 batch 다시 계산되는지 표에 적는다. fixed quantile의 cutoff는 숫자로 고정되어 있지 않다는 점도 명확히 한다.

EBM과 naPINN의 성능 차이를 곧바로 “model discrepancy 때문에 생긴 인과 효과”라고 해석하지 않는다. 현재처럼 association으로 한정하는 것은 적절하다. 새로운 대규모 discrepancy 실험은 이번 제출에 필수적이지 않다.

**10. 최종 권고**

이번 3일의 필수 결과물은 확인 가능한 핵심 수치, 공정한 gate 비교 또는 그 한계의 명시, 무주입 조건을 포함한 적용 범위 설명이다. 새로운 데이터셋, HMC 재도전, 현실 데이터의 inverse-Reynolds 추정, 추가 backbone sweep은 우선순위가 낮다.

현재 가장 위험한 문제는 실험 개수가 부족하다는 점보다 일부 핵심 결론을 뒷받침하는 실행 기록이 확정되지 않았다는 점이다. 이를 먼저 해결하고, 남은 계산 시간을 18회 gate 통제와 선택적 9회 oracle 비교에 쓰는 것이 합리적이다. 결과가 기존 주장보다 약하더라도 확인된 범위에 맞춰 정리한 논문이 심사에서 더 설득력 있다.
