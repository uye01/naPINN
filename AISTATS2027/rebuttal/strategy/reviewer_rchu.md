# 리뷰어 rchu 대응 전략

점수 2, 확신 4. Soundness 2, Clarity 2, Contribution 2.

## 리뷰 요지

- **강점으로 인정한 것**: PINN-EBM과 naPINN 사이에서 추정기·초기화·예산을 고정한 비교, Prop. 1의 이론–실험 고리(Fig. 5의 `λ_rej ≥ 0.9` 열화, Fig. 6의 τ̃ 2.8 / 1.8 / 1.3), 2×2 ablation과 frozen-gate 진단, 관대한 screen 비교.
- **W1**: App. G가 중심 주장을 무너뜨린다. Laplace·Gaussian 배경에서 naPINN(제곱 손실)은 0.085 / 0.126으로 LAD 0.085 / 0.109, OrPINN 0.081 / 0.107보다 낫지 않고 naPINN-L1, naPINN-q2.9만 이긴다. 손실 선택 문제가 한 단계 안으로 옮겨갔을 뿐이다.
- **W2**: 잡음 구성이 손으로 고른 한 가지이고 밀도 순서에 가장 유리하다. 세 PDE, 세 손상 수준에서 같은 mixture를 썼으므로 아홉 칸이 독립적인 검증이 아니다. 모드 간격, 성분 수, 왜도에 대한 스윕이 없다.
- **W3**: baseline 튜닝이 불균등하다. OrPINN은 q = 1.9, 2.9 두 점만 시험했고 2.9가 아홉 칸 모두에서 낫다. "q = 3.5 이상이 더 나을 수 있다." LAD는 스케일 스윕이 없다. PINN-EBM은 `w_PDE` 스윕을 받았다. 2.0–2.4배는 q 그리드를 넓히기 전까지 상한으로 봐야 한다.

## 목표

2점에서 3점 이상으로 올린다. 이 리뷰어는 통제된 비교와 정직한 서술을 높이 평가하므로, 인정과 추가 통제 실험으로 답하는 것이 맞다.

## W1 대응

**입장: 문구가 과했음을 인정하고, 주장을 "게이트는 손실을 대체하지 않고 손실 위에 얹는 장치"로 다시 세운다.**

논증은 세 단계다.

1. **App. G를 같은 손실끼리 다시 읽으면 게이트는 여섯 쌍 모두에서 개선한다.** 논문에 이미 있는 수치(λ–ω 15%, rMSE, ten trials)다.

   | 데이터 손실 | Laplace: 게이트 없음 → 있음 | Gaussian: 게이트 없음 → 있음 |
   |---|---|---|
   | 제곱 | 0.323 → 0.085 | 0.326 → 0.126 |
   | L1 | 0.085 → 0.059 | 0.109 → 0.064 |
   | q-Gaussian 2.9 | 0.081 → 0.071 | 0.107 → 0.067 |

   리뷰어가 인용한 비교(naPINN-제곱 vs LAD)는 손실과 게이트를 동시에 바꾼 비교다. 게이트의 효과만 보면 일관되게 양수다.

2. **게이트가 바꾸는 것은 "이상치를 어떻게 다루는가"이고, "inlier 잡음에 어떤 손실이 맞는가"는 그대로 남는다.** 논문 §5.4가 이미 이렇게 쓰고 있으나 초록과 서론의 "no single fixed loss suits every case"가 더 넓은 약속으로 읽힌다. 이 문장을 고치겠다고 약속한다.

3. **잘못 고른 설정의 대가를 비교한다.** 기본 naPINN(제곱 손실)은 Gaussian 배경에서 최선 baseline의 1.18배(0.126 vs 0.107)다. 반면 고정 robust loss는 주 벤치마크 잡음에서 naPINN의 1.7–2.1배(λ–ω 15% rMSE, OrPINN 0.163, LAD 0.199 vs naPINN 0.095)다.

**주의할 점**

- 실제 PIV에서는 "게이트가 모든 손실을 개선한다"가 균일하게 성립하지 않는다. Cylinder 15%에서는 성립하지만(L1 0.270 → 0.226, q2.9 0.231 → 0.216, 제곱 0.574 → 0.160, rMAE) FSI, Controlled Cylinder, Foil의 일부 조합에서는 아니다. 대응문에서 PIV까지 일반화해 쓰지 않는다.
- 작성 서버의 three-seed 재실행에서는 Gaussian·Laplace 배경에서 naPINN-제곱이 LAD와 OrPINN을 앞선다. 그러나 App. G와 같은 조건인데 값이 다르므로 저자 결정(README D3) 전에는 쓰지 않는다.
- Student-t(df = 3) 배경에서는 naPINN-제곱이 실패한다(작성 서버 three-seed rMAE 0.098, LAD 0.045). 이 잡음 스케일에서는 이상치의 제곱 잔차가 `λ_rej = 0.5`보다 작아 게이트가 이상치의 0.22%만 제외한다. Prop. 1(b)와 부합하는 결과이며, 잡음 스케일과 `λ_rej`의 결합이라는 실제 한계다. 리뷰어가 묻지 않았으므로 먼저 꺼내지는 않되, 잡음 종류를 넓혀 답할 때 이 조건을 숨기는 서술은 하지 않는다.

**수정 약속**

- 초록·서론: "the gate removes the choice of how to treat gross outliers; the choice of inlier loss remains and can be combined with the gate" 취지로 수정.
- §5.4: 같은 손실끼리의 비교표를 본문으로 올리거나 App. G 표에 "게이트 유무" 열 구조를 명시.

## W2 대응

**입장: 인정한다. Prop. 1(c)가 이미 이 한계를 예측한다는 점을 내세우고, 스윕으로 확인한다.**

- Prop. 1(c)는 밀도 순서가 크기 순서와 달라지는 것은 밀도가 대칭·단봉이 아닐 때뿐이라고 말한다. 따라서 "모드 간격이 줄어들면 naPINN의 이점이 줄어든다"는 것은 반박이 아니라 이론의 예측이다. 리뷰어가 Prop. 1의 이론–실험 고리를 강점으로 꼽았으므로, 같은 고리를 하나 더 닫는 답이 된다.
- 아홉 칸이 독립적인 검증이 아니라는 지적은 그대로 인정한다.
- 이미 있는 다른 잡음 증거를 정리해 준다: App. G의 Laplace, Gaussian 배경, 실제 PIV 네 데이터셋.
- **새 실험 E4**: λ–ω 15%에서 총 분산을 논문 mixture와 같게 맞춘 채 모드 간격(0, 0.5, 1), 성분 수(대칭 2봉), 왜도(비대칭 2봉)를 바꾼다. 방법은 MSE, LAD, OrPINN q2.9, naPINN이다. 명세는 `experiment_plan.md` E4.
- |r̃| 게이트를 넣으면 가장 직접적인 답이 되지만 계보 충돌 항목이다(README D2).

**결과에 따른 답**

| E4 결과 | 답 |
|---|---|
| 모드 간격이 줄수록 naPINN과 robust loss의 차이가 줄어듦 | Prop. 1(c)의 예측대로다. 이득의 범위를 본문에 명시하겠다 |
| 간격 0에서도 naPINN이 앞섬 | 이득의 일부는 순서가 아니라 학습된 컷오프와 명시적 제외에서 온다 |
| 간격 0에서 naPINN이 뒤짐 | App. G의 Gaussian 결과와 같은 현상이다. 대칭·단봉 잡음에서는 robust loss를 권한다고 쓴다 |

## W3 대응

**입장: 가장 강하게 반박할 수 있는 지점이다. 사실관계를 바로잡고, 그래도 그리드를 넓힌다.**

1. **q = 3.5는 유효한 q-Gaussian이 아니다.** q-Gaussian은 q < 3에서만 정규화된다. 우리 구현의 손실은 `ρ_q(r) = (1/(q−1)) · log(1 + (q−1) β_q r²)`, `β_q = 1/(2(3−q))`이고 β_q는 q → 3에서 발산한다(`pinnlab/utils/data_loss.py`).
2. **q = 2.9는 허용 범위의 끝 근처다.** q-Gaussian은 자유도 `ν = (3−q)/(q−1)`인 Student-t와 같다. q = 1.9는 ν ≈ 1.22(Cauchy 근처), q = 2.9는 ν ≈ 0.053이다. 두 점 그리드의 끝이 아니라 유효 범위의 거의 끝을 시험한 것이다.
3. **그래도 그리드가 두 점뿐이라는 지적은 맞다.** E1에서 q ∈ {1.5, 2.5, 2.99}를 추가해 (1, 3) 안에서 다섯 점 그리드를 만든다.
4. **LAD의 스케일.** L1 손실의 스케일 파라미터는 데이터 항의 가중치와 동치이고, Adam에서는 `w_PDE`와 `w_data`의 비만 의미가 있다. 따라서 LAD의 스케일 스윕은 `w_PDE` 스윕과 같다. E1에서 LAD와 OrPINN q2.9에 PINN-EBM이 받은 것과 같은 `w_PDE ∈ {1, 10, 50}`을 주고, 같은 규칙(그리드 내 최선)으로 고른다.
5. **이미 있는 통제**: equal-time 비교에서 baseline은 37–53k 업데이트를 받았다(논문 App. J 관련 서술 확인 후 인용).
6. **표현 수정**: "2.0–2.4배"는 "시험한 그리드에서 가장 좋은 고정 손실 대비"로 낮추고, E1 결과로 갱신한 배수를 보고한다. 배수가 줄어들면 줄어든 값을 그대로 쓴다.

**E1 결과에 따른 답**

| E1 결과 | 답 |
|---|---|
| 확장 그리드에서도 q = 2.9 근처가 최선이고 `w_PDE` 스윕의 이득이 작음 | 배수가 거의 유지됨을 표로 제시 |
| 다른 q나 `w_PDE`에서 baseline이 뚜렷이 개선됨 | 갱신한 배수를 제시하고 본문 표의 baseline 행을 최선 설정으로 교체하겠다고 약속 |

## 대응문 뼈대 (영어 초안 작성 시)

1. Thank you; the three weaknesses are addressed with (i) a scoped claim, (ii) a noise-shape sweep, (iii) an extended baseline grid.
2. W3 first: admissible range of q, Student-t equivalence, extended grid and `w_PDE` sweep table, updated factor.
3. W1: matched-loss table from App. G, scoped claim, revised abstract sentence.
4. W2: Prop. 1(c) prediction, sweep table, stated regime of benefit.

W3를 먼저 두는 이유는 사실관계 정정과 새 표가 함께 있어 가장 설득력이 크기 때문이다.

## 필요한 것

- E0, E1 (필수), E4 (권장).
- 논문에서 equal-time 통제의 정확한 수치와 위치 재확인.
- README D2, D3 결정.
