# AISTATS 2027 리버털 추가 실험 명세

작성일: 2026-11-18
작성 기준 커밋: `0c95431` (branch `rebuttal`)

이 문서는 다른 GPU 서버에서 리버털용 추가 실험을 돌리기 위한 명세다. 실험의 배경과 각 리뷰어 대응에서의 쓰임은 같은 폴더의 `README.md`와 `reviewer_*.md`에 있다.

모든 실험은 **계획** 상태다. 이 문서의 "예상" 수치는 작성 서버의 기존 기록이며 새 실험의 결과가 아니다.

## 0. 공통 규칙

1. **E0(앵커 재현)을 먼저 끝내고 합격한 뒤에 본 실험을 시작한다.** 합격하지 못하면 멈추고 저자에게 보고한다.
2. 조건 목록은 이 문서에 고정되어 있다. 결과를 본 뒤 조건을 빼거나 바꾸지 않는다. 조건을 추가할 때는 추가한 사실과 이유를 결과 파일에 적는다.
3. 유리한 결과와 불리한 결과를 모두 보고한다. 실패하거나 발산한 실행도 실패로 기록한다.
4. 한 비교 안의 모든 방법은 같은 seed의 같은 손상 데이터를 쓴다.
5. 기존 산출물을 덮어쓰지 않는다. 출력 루트는 `outputs/aistats_rebuttal/<실험 ID>/`로 한다.
6. seed는 40, 41, 42다. 보고 형식은 세 seed의 평균 ± 표본 표준편차다.
7. smoke test는 구현 확인용이며 결과로 쓰지 않는다.
8. 학습 예산은 논문과 같다. baseline은 30,000 업데이트, 단계형 방법은 warm-up 5,000 + 추정기 초기화 5,000 + joint 25,000이다. 러너 기본값이므로 인자를 바꾸지 않는다.
9. `λ_rej = 0.5`, EMA momentum 0.05다. 러너 기본값이다.
10. `outputs/`는 git에서 제외되어 있다. 결과는 5절의 형식으로 집계해 커밋한다.

## 1. 실행 전 준비

### 1.1 코드와 데이터

- 브랜치 `rebuttal`을 받는다.
- 환경 구성, 데이터 전송, 무결성 확인은 `rebuttal/CROSS_SERVER_EXPERIMENT_HANDOFF.md` 7절을 따른다.
- 데이터 체크섬(작성 서버 기준):

  ```text
  ba83755bfd03115838341d757784e85d7f91854e457d5be856de26fd773d0d27  Burgers2D_3-5/data.npz
  d046ba0f2c0c46e54c301b2c2a1c241da956d09bde70c4c9b11ee3f416bf92f6  LambdaOmega_Spiral_2/data.npz
  0aea0fe1e85ed15ee381443106e2478cf61554c91c5969c2ab62e78d2b47c0c7  realpdebench_cylinder_10031_frames1000-1200_stride1.npz
  ```

  Burgers와 λ–ω 데이터는 `pinnlab/simulation/simulation_result/` 아래에, PIV 데이터는 `analysis/results/runs/rebuttal_realpde/data/` 아래에 둔다. 실험 서버의 데이터 체크섬이 다르면 그 사실을 결과 파일에 적는다. 체크섬이 달라도 E0에 합격하면 진행할 수 있다.
- 정적 확인:

  ```bash
  python -m compileall -f -q pinnlab scripts/rebuttal
  python -m scripts.rebuttal.run_synthetic --help
  python -m scripts.rebuttal.run_realpdebench --help
  ```

### 1.2 러너 상태에 관한 주의

- 작성 서버의 작업 트리에는 `scripts/rebuttal/run_synthetic.py`와 `run_realpdebench.py`에 커밋되지 않은 변경(pre-training screen baseline)이 있고, 이 변경은 커밋되지 않은 `scripts/rebuttal/preprocess_screen.py`에 의존한다. 이 문서의 실험은 screen을 쓰지 않으므로 커밋된 러너로 충분하다.
- E1과 E4는 아래 두 가지 작은 러너 수정이 필요하다. **아직 구현되어 있지 않다.** 실험 서버에서 구현하고 커밋한다.

### 1.3 러너 수정 A: 임의의 q (E1용)

현재 q는 방법 이름에 묶여 있다(`orpinn_q19`, `orpinn_q29`). 수정 내용은 다음과 같다.

- `METHODS`에 `"orpinn"`을 추가한다.
- 인자 `--q`(float, 기본값 없음)를 추가한다. `--method orpinn`이면 필수이고 `1 < q < 3`을 검사한다.
- `configure_experiment`에서 `method == "orpinn"`이면 `config["data_loss"]["kind"] = "q_gaussian"`, `config["data_loss"]["q"] = q`로 둔다.
- `baseline_data_loss`에서 `method == "orpinn"`이면 `data_loss_q_gaussian(residual, q=q).mean()`을 반환한다. β는 기본값 `0.5 / (3 − q)`를 그대로 쓴다.
- baseline 방법 집합을 검사하는 분기(`method in {"mse", "lad", "orpinn_q19", "orpinn_q29"}`)에 `"orpinn"`을 추가한다.
- 출력 경로의 방법 디렉터리 이름은 `orpinn_q{q:g}`로 한다.
- `metrics.json`에 q 값을 기록한다.

검증: `--method orpinn --q 2.9`와 `--method orpinn_q29`를 같은 seed로 돌려 `field_rMAE`가 일치하는지 확인한다(λ–ω, seed 40, 한 번).

### 1.4 러너 수정 B: mixture 파라미터 지정 (E4용)

현재 4G 잡음의 `par_list`는 설정 파일에 고정되어 있다. `GaussianMixtureNoise`는 `[mean, std]` 쌍 네 개를 같은 가중치로 받는다(`pinnlab/data/noise.py`).

- 인자 `--noise-par-list`(JSON 문자열, `[[m, s], [m, s], [m, s], [m, s]]`)와 `--noise-tag`(문자열)를 추가한다. 둘은 함께 주어야 하고 `--noise-kind 4G`일 때만 허용한다.
- `configure_experiment`에서 `config["noise"]["par_list"]`를 덮어쓴다.
- 출력 경로의 잡음 디렉터리 이름은 `4G_{noise_tag}`로 한다.
- `metrics.json`에 `par_list`와 태그를 기록한다.

검증: 기본 `par_list` `[[-9.0, 2.0], [-0.3, 4.0], [2.7, 0.6], [8.5, 1.0]]`를 `--noise-par-list`로 넘긴 실행이 E0의 같은 seed 실행과 일치하는지 확인한다(λ–ω, naPINN, seed 40, 한 번).

### 1.5 명령 형식

```bash
python -m scripts.rebuttal.run_synthetic \
  --experiment-name lambdaomega2d \
  --experiment-config configs/rebuttal/lambdaomega2d.yaml \
  --method napinn \
  --seed 40 \
  --device cuda:0 \
  --noise-kind 4G \
  --outlier-ratio 0.15 \
  --output-root outputs/aistats_rebuttal/E0_anchors
```

- `--experiment-name`과 설정 파일의 짝: `allencahn2d` ↔ `configs/rebuttal/allencahn2d.yaml`, `burgers2d` ↔ `configs/rebuttal/burgers2d.yaml`, `lambdaomega2d` ↔ `configs/rebuttal/lambdaomega2d.yaml`.
- 방법 이름: `mse`, `lad`, `orpinn_q19`, `orpinn_q29`, `pinn_ebm`, `napinn`, `napinn_lad`, `napinn_q29`, `quantile`, `threshold`.
- `--pde-weight`를 주지 않으면 1이다.
- 완료된 실행(`metrics.json` 존재)은 건너뛰고, 비어 있지 않은 미완료 디렉터리가 있으면 러너가 멈춘다. 미완료 실행은 다른 위치로 옮긴 뒤 다시 돌린다.
- 큐 스크립트는 `scripts/rebuttal/run_synthetic_supplement_queue.py`의 구조를 따르면 된다.

## 2. E0: 앵커 재현 (필수, 가장 먼저)

**목적.** 실험 서버의 코드와 데이터가 논문과 같은 계보의 수치를 내는지 확인한다. 이 실행들은 E1과 E4의 기준 행으로도 쓴다.

### E0a: 계보 충돌이 없는 방법

- 조건: 4G 잡음, 손상 15%, PDE 3종(`allencahn2d`, `burgers2d`, `lambdaomega2d`), 방법 4종(`napinn`, `lad`, `orpinn_q29`, `mse`), seed 40–42.
- 실행 수: 3 × 4 × 3 = 36.
- 출력 루트: `outputs/aistats_rebuttal/E0_anchors`.

기준값(작성 서버, seed 40–42, 평균 ± 표본 표준편차):

| PDE | 방법 | rMAE | rMSE | 논문 Table 1 rMAE (ten trials) |
|---|---|---|---|---|
| Allen–Cahn | naPINN | 0.0920 ± 0.0035 | 0.0948 ± 0.0023 | 0.134 (Table 3 three-seed: 0.092) |
| Allen–Cahn | LAD | 0.3834 ± 0.0306 | 0.3221 ± 0.0202 | 0.352 |
| Allen–Cahn | OrPINN q2.9 | 0.2675 ± 0.0736 | 0.2308 ± 0.0554 | 0.269 |
| Allen–Cahn | MSE | 0.8553 ± 0.1076 | 0.7122 ± 0.0869 | 0.823 |
| Burgers | naPINN | 0.0819 ± 0.0024 | 0.0986 ± 0.0070 | 0.072 (Table 3: 0.082) |
| Burgers | LAD | 0.2563 ± 0.0020 | 0.2463 ± 0.0010 | 0.242 |
| Burgers | OrPINN q2.9 | 0.1908 ± 0.0219 | 0.1922 ± 0.0171 | 0.175 |
| Burgers | MSE | 0.5864 ± 0.0395 | 0.5659 ± 0.0365 | 0.568 |
| λ–ω | naPINN | 0.0706 ± 0.0012 | 0.0889 ± 0.0007 | 0.076 (Table 3: 0.071) |
| λ–ω | LAD | 0.1910 ± 0.0078 | 0.1991 ± 0.0062 | 0.190 |
| λ–ω | OrPINN q2.9 | 0.1526 ± 0.0031 | 0.1651 ± 0.0033 | 0.150 |
| λ–ω | MSE | 0.4219 ± 0.0105 | 0.4411 ± 0.0103 | 0.437 |

**합격 기준.** 12개 칸 각각에서 실험 서버의 three-seed 평균 rMAE가 기준값의 ±15% 안에 있거나, 차이가 두 서버 표본 표준편차 중 큰 값의 2배 안에 있어야 한다. Allen–Cahn의 OrPINN과 MSE는 seed 간 분산이 크므로 두 번째 조건으로 판정한다.

**불합격 시.** 본 실험을 시작하지 않는다. 어느 칸이 어느 방향으로 벗어났는지와 데이터 체크섬 일치 여부를 저자에게 보고한다.

### E0b: 계보 충돌 항목의 진단 (권장, 대응문 사용은 저자 결정 후)

- 조건: 4G 잡음, 손상 15%, PDE 3종, 방법 `threshold`(|r̃| 학습 게이트)와 `pinn_ebm`(`w_PDE = 1`), seed 40–42.
- 실행 수: 3 × 2 × 3 = 18.
- 출력 루트: `outputs/aistats_rebuttal/E0b_lineage`.

| 방법 | 논문 rMAE (AC / Bu / λω) | 작성 서버 rMAE (AC / Bu / λω) |
|---|---|---|
| \|r̃\| 학습 게이트 (Table 3) | 0.244 / 0.345 / 0.148 | 0.244 / 0.086 / 0.067 |
| PINN-EBM (Table 1, 문제별 `w_PDE` 선택) | 0.153 / 0.077 / 0.104 | 0.103 / 0.047 / 0.040 (`w_PDE = 1`) |

실험 서버가 어느 쪽 값을 재현하는지 기록해 저자에게 보고한다. 이 결과는 `README.md`의 D2 결정에 쓰인다. **E0b의 수치와 이 두 방법을 포함한 새 비교는 저자 결정 전에 대응문에 쓰지 않는다.**

## 3. 본 실험

### E1: baseline 그리드 확장 (rchu W3, 필수)

**목적.** OrPINN의 q 그리드가 두 점뿐이고 LAD에 스케일 스윕이 없다는 지적에 답한다. PINN-EBM이 받은 것과 같은 선택 규칙을 고정 손실 baseline에 준다.

**E1a: q 그리드**

- 러너 수정 A가 필요하다.
- 조건: 4G 잡음, 손상 15%, PDE 3종, `--method orpinn --q` ∈ {1.5, 2.5, 2.99}, seed 40–42, `w_PDE = 1`.
- 실행 수: 3 × 3 × 3 = 27.
- q = 1.9, 2.9는 E0와 기존 방법 이름으로 얻는다. q = 1.9의 three-seed 실행이 없으면 `orpinn_q19`로 9회를 추가한다.
- 참고: q-Gaussian은 `ν = (3 − q)/(q − 1)`인 Student-t와 같다. q = 1.5 → ν = 3, 1.9 → 1.22, 2.5 → 0.33, 2.9 → 0.053, 2.99 → 0.005.

**E1b: `w_PDE` 스윕**

- 러너 수정이 필요 없다.
- 조건: 4G 잡음, 손상 15%, PDE 3종, 방법 `lad`, `orpinn_q29`, `--pde-weight` ∈ {10, 50}, seed 40–42.
- 실행 수: 3 × 2 × 2 × 3 = 36.
- `w_PDE = 1`은 E0a에서 얻는다.
- 선택(시간이 남으면): `--pde-weight 0.1`로 18회 추가. 데이터 항에 무게를 더 주는 방향이다.

**E1c: 선택.** E1a에서 q = 2.9 이외의 값이 최선이면, 그 q에서 `--pde-weight` ∈ {10, 50}을 추가한다(PDE 3종 × 2 × 3 seed = 18회).

- 출력 루트: `outputs/aistats_rebuttal/E1_baseline_grid`.

**집계.**

1. PDE별로 (방법, 설정)마다 three-seed 평균 rMAE, rMSE를 표로 만든다.
2. PDE별로 그리드 내 최선의 고정 손실 baseline을 rMAE 기준으로 고른다. 논문이 PINN-EBM의 `w_PDE`를 고른 규칙과 같다.
3. `최선 baseline rMAE / naPINN rMAE`를 PDE별로 계산한다. naPINN은 E0a의 값(단일 기본 설정)을 쓴다.
4. 논문의 2.0–2.4배(ten-trial, OrPINN q2.9 대비)와 나란히 적는다. three-seed 기준 E0a 값으로 계산한 배수도 함께 적는다.

**사전 예상.** 없음. 작성 서버에는 이 조건의 기록이 없다.

### E2: 밀도 추정 품질 (25xJ, 필수, 학습 없음)

**목적.** 밀도 추정 구성요소의 품질을 정량화한다.

**입력.** E0a의 naPINN 실행 9개(PDE 3종 × seed 3개, 15%). 여유가 있으면 5%, 10%의 naPINN 실행을 18회 추가해 아홉 조건을 모두 채운다(출력 루트 `outputs/aistats_rebuttal/E2_napinn_ratios`).

**E2a: 이미 기록되는 지표의 집계.** 각 실행의 `metrics.json`에서 다음을 모아 표로 만든다.

- `estimator_scores.outlier_detection_auroc`: 학습된 밀도 점수만으로 손상 측정을 가려내는 AUROC.
- `gate.known_outlier_rejection_rate`, `gate.known_clean_rejection_rate`: 게이트의 손상 제외율과 정상 측정 제외율.

작성 서버 기준 예상: AUROC 0.991–0.997, 손상 제외율 98.7–99.4%, 정상 측정 제외율 0.35–1.1%.

**E2b: 학습된 밀도와 주입한 잡음 밀도의 거리.** 새 분석 스크립트가 필요하다(`analysis/` 아래에 추가).

- 체크포인트 `final.pt`는 `model`, `experiment`(`running_std`, `ebm`, `gate_module` 포함), `resolved_config`를 담고 있다.
- 같은 seed와 설정으로 experiment를 다시 만들어 측정 좌표, 손상된 관측, 깨끗한 값, 손상 인덱스를 얻는다.
- 비교 대상 두 가지:
  1. 실제 주입한 손상 `ε = y_noisy − y_clean`을 `running_std`로 나눈 값의 경험 분포.
  2. 학습 종료 시점의 잔차 `r = y_noisy − u_θ(x)`를 `running_std`로 나눈 값의 경험 분포.
- 학습된 EBM 밀도를 1차원 격자에서 정규화한 뒤 각 경험 분포와의 total variation 거리와 Kolmogorov–Smirnov 통계량을 계산한다.
- 기준점으로 같은 표본에 맞춘 단일 Gaussian의 거리도 함께 계산한다. EBM의 거리가 얼마나 작은지를 읽을 수 있게 하기 위해서다.
- 보고: PDE별 three-seed 평균 ± 표준편차.

**출력.** `AISTATS2027/rebuttal/results/E2_density_quality.csv`와 요약 markdown.

### E3: 상관·구조적 손상을 주입한 실제 PIV (aQS2 Q1·W3, 필수)

**목적.** 독립 이상치가 아닌 구조적 손상에서 naPINN의 이점이 유지되는지, 유지되는 조건이 무엇인지 확인한다. 기존 실행은 `λ_rej = 0.10`이어서 논문 설정(`λ_rej = 0.5`)과 다르므로 다시 돌린다.

**데이터.** Cylinder PIV 원본 npz(체크섬은 1.1절)의 학습 센서에만 손상을 주입한다. held-out PIV는 바뀌지 않는다. 손상 seed는 20260726이고 파라미터는 주입 스크립트의 기본값이다.

| 조건 | 주입 스크립트와 설정 | 파라미터 | variant 설정 파일 |
|---|---|---|---|
| AR(1) 시간 상관 | `inject_realpdebench_correlated.py --kind ar1` | 실패 센서 15%, ρ = 0.98, 스케일 3.0 | `realpdebench_cylinder_ar1.yaml` |
| 공간 burst | `--kind spatial_burst` | burst 비율 0.20, 스케일 5.0 | `realpdebench_cylinder_spatial_burst.yaml` |
| 이분산 | `--kind heteroscedastic` | 실패 센서 15%, 기본 std 1.0, gain 4.0 | `realpdebench_cylinder_heteroscedastic.yaml` |
| u–v 성분 간 상관 | `--kind uv_correlated` | 실패 센서 15%, ρ = 0.8, 스케일 3.0 | `realpdebench_cylinder_uv_correlated.yaml` |
| 센서 drift 10% | `inject_realpdebench_sensor_drift.py --failure-fraction 0.10` | bias 3.0, drift 끝 2.0 | `realpdebench_cylinder_sensor_drift10.yaml` |
| 센서 drift 20% | `--failure-fraction 0.20` | 같음 | `realpdebench_cylinder_sensor_drift20.yaml` |
| 센서 drift 30% | `--failure-fraction 0.30` | 같음 | `realpdebench_cylinder_sensor_drift30.yaml` |

설정 파일은 모두 `configs/experiment/` 아래에 있고, 각 variant 설정의 `data.path`가 파생 npz의 위치를 정한다. 파생 npz가 실험 서버에 없으면 주입 스크립트로 만든다. 스케일은 깨끗한 성분 표준편차의 배수다.

**E3a: naPINN, `λ_rej = 0.5` (필수)**

- 방법 설정: `configs/experiment/realpdebench_cylinder_napinn.yaml`. `λ_rej`는 `realpdebench_cylinder_common.yaml`의 기본값 0.5를 쓴다. `realpdebench_cylinder_napinn_rejection_01.yaml`은 쓰지 않는다.
- 조건 7개 × seed 3개 = 21회.
- 실행 후 각 실행의 resolved config에서 rejection cost가 0.5인지 확인한다.

**E3b: baseline (권장)**

- 방법: `mse`, `lad`, `orpinn_q29`. 설정 파일은 `realpdebench_cylinder_{mse,lad,orpinn_q29}.yaml`.
- 조건 7개 × 방법 3개 × seed 3개 = 63회.
- 작성 서버에 이 baseline들의 기존 결과가 있으나(`λ_rej`와 무관), 같은 서버에서 돌린 값끼리 비교하는 것이 낫다. 시간이 부족하면 LAD만 돌린다(21회).
- PINN-EBM과 MAD-PINN은 선택이다. PINN-EBM을 넣는다면 논문 Table 2와 같은 설정인지 설정 파일을 먼저 확인한다.

명령 형식(인자의 정확한 의미는 `--help`와 `scripts/rebuttal/run_realpdebench_queue.py`로 확인):

```bash
python -m scripts.rebuttal.run_realpdebench \
  --exp-config configs/experiment/realpdebench_cylinder_napinn.yaml \
  --variant-config configs/experiment/realpdebench_cylinder_ar1.yaml \
  --seed 40 \
  --device cuda:0 \
  --output-root outputs/aistats_rebuttal/E3_structured_piv
```

**집계.** 조건별로 방법마다 held-out rMAE, rMSE(three-seed 평균 ± 표준편차), naPINN의 손상 측정 제외율과 정상 측정 제외율.

**사전 예상(작성 서버, `λ_rej = 0.10`, three-seed 평균, rMAE / rMSE).** 새 결과가 아니며 대응문에 쓰지 않는다.

| 조건 | naPINN | LAD | OrPINN q2.9 | MSE | 최선 |
|---|---|---|---|---|---|
| 이분산 | 0.160 / 0.236 | 0.114 / 0.185 | 0.125 / 0.189 | 0.151 / 0.201 | LAD |
| u–v 상관 | 0.144 / 0.209 | 0.115 / 0.186 | 0.124 / 0.187 | 0.143 / 0.198 | LAD |
| drift 20% | 0.171 / 0.253 | — | — | — | naPINN |
| drift 30% | 0.218 / 0.309 | — | — | — | naPINN |
| AR(1), burst, drift 10% | — | — | — | — | LAD |

drift 20% / 30%에서 naPINN은 실패 센서 측정의 90.7% / 92.9%를 제외했고 정상 측정의 8.4% / 32.7%도 제외했다.

**주의.** `λ_rej = 0.5`에서는 약한 손상의 제곱 잔차가 `λ_rej`에 못 미쳐 게이트가 제외를 거의 하지 않을 수 있다. 그 경우 naPINN은 MSE에 가까워진다. 이 결과도 그대로 보고한다.

### E4: 잡음 형태 스윕 (rchu W2, aQS2 W3, 권장)

**목적.** Prop. 1(c)의 예측을 확인한다. 배경 잡음이 대칭·단봉에 가까워지면 밀도 순서와 크기 순서가 같아지므로, naPINN과 고정 robust loss의 차이가 모드 간격에 따라 어떻게 변하는지 본다.

- 러너 수정 B가 필요하다.
- PDE: `lambdaomega2d`, 손상 15%, seed 40–42.
- 방법: `mse`, `lad`, `orpinn_q29`, `napinn`.
- 잡음 구성: 아래 4종. 논문 mixture(간격 1.0)는 E0a에서 얻는다.
- 실행 수: 4 × 4 × 3 = 48.
- 출력 루트: `outputs/aistats_rebuttal/E4_noise_shape`.

모든 구성은 논문 mixture와 **총 표준편차가 같도록**(설정 단위 6.728) 평균과 표준편차를 함께 재조정했다. 총 분산이 다르면 이상치 크기(배경 표준편차의 3–10배)와 `λ_rej`의 관계가 함께 바뀌어 모드 간격의 효과를 분리할 수 없기 때문이다. `par_list`는 `noise.scale = 0.1`이 곱해지기 전의 설정 단위다.

| 태그 | 설명 | `--noise-par-list` | 평균 | 왜도 |
|---|---|---|---|---|
| `sep1` (E0a) | 논문 mixture | `[[-9.0, 2.0], [-0.3, 4.0], [2.7, 0.6], [8.5, 1.0]]` | 0.475 | −0.37 |
| `sep05` | 모드 간격 절반 | `[[-7.735, 3.438], [-0.258, 6.875], [2.32, 1.031], [7.305, 1.719]]` | 0.408 | −0.43 |
| `sep0` | 모드 간격 0. 평균 0인 Gaussian scale mixture. 대칭·단봉 | `[[0.0, 5.823], [0.0, 11.647], [0.0, 1.747], [0.0, 2.912]]` | 0 | 0 |
| `bimodal_sym` | 대칭 2봉 (성분 수 변화) | `[[-6.383, 2.128], [-6.383, 2.128], [6.383, 2.128], [6.383, 2.128]]` | 0 | 0 |
| `bimodal_skew` | 가중치 3:1의 비대칭 2봉 (왜도 변화) | `[[-3.625, 2.417], [-3.625, 2.417], [-3.625, 2.417], [10.876, 2.417]]` | 0 | 0.94 |

구성 방법: `sep05`, `sep0`은 논문 mixture의 평균에 0.5, 0을 곱한 뒤 총 표준편차를 맞췄다. 2봉 구성은 같은 성분을 반복해 가중치를 만들었다.

**선택 확장.**

- `napinn_lad`를 추가(4 구성 × 3 seed = 12회). 게이트와 L1 손실의 결합이 대칭·단봉 잡음에서 어떤지 본다(rchu W1과 연결).
- `threshold`(|r̃| 학습 게이트)를 추가(12회). 밀도 순서와 크기 순서를 직접 비교하므로 과학적으로 가장 직접적인 답이지만, 계보 충돌 항목이므로 E0b 결과와 저자 결정(`README.md` D2) 이후에만 대응문에 쓴다.

**집계.** 잡음 구성별로 방법마다 rMAE, rMSE(three-seed 평균 ± 표준편차), naPINN의 손상 제외율과 정상 측정 제외율, `naPINN / 최선 고정 손실` 비.

**사전 예상.** 없음. 참고로 논문 App. G의 Gaussian 배경(대칭·단봉)에서는 naPINN-제곱이 LAD, OrPINN에 뒤졌다(rMSE 0.126 vs 0.109, 0.107). `sep0`에서 비슷한 결과가 나올 수 있다.

## 4. 실행 순서와 규모

1회 약 22분(A6000, 시뮬레이션 기준)으로 계산했다. PIV 실행 시간은 실험 서버에서 한 번 측정해 보정한다.

| 순서 | 실험 | 실행 수 | GPU-시간 (약) | 선행 조건 |
|---|---|---|---|---|
| 1 | E0a | 36 | 13 | 없음 |
| 2 | E0b | 18 | 7 | 없음. E0a와 함께 돌려도 됨 |
| 3 | E1a, E1b | 63 | 23 | E0a 합격, 러너 수정 A |
| 4 | E2 | 0 (선택 18) | 0 (선택 7) | E0a 완료 |
| 5 | E3a | 21 | PIV 실행 시간 측정 후 | PIV 데이터 준비 |
| 6 | E3b | 21–63 | 같음 | 같음 |
| 7 | E4 | 48 (선택 +24) | 18 (선택 +9) | E0a 합격, 러너 수정 B |

E3는 시뮬레이션 실험과 독립이므로 PIV 데이터가 준비되면 E1과 함께 돌린다. 마감이 가까우면 E0a → E1 → E3a → E2 → E4 순으로 줄인다.

## 5. 결과 반환 형식

`outputs/`는 git에 올라가지 않으므로 집계 결과를 아래 위치에 커밋한다.

```text
AISTATS2027/rebuttal/results/
  E0_anchors.csv
  E0b_lineage.csv
  E1_baseline_grid.csv
  E2_density_quality.csv
  E3_structured_piv.csv
  E4_noise_shape.csv
  SUMMARY.md
```

- CSV의 한 행은 (실험, PDE 또는 데이터셋, 조건, 방법, 설정) 하나다. 열: seed 목록, 완료된 seed 수, `field_rMAE` 평균과 표본 표준편차, `field_rMSE` 평균과 표본 표준편차, PDE 계수 절대 오차, (게이트가 있는 방법은) 손상 제외율, 정상 측정 제외율, 추정기 AUROC.
- `SUMMARY.md`에 적을 것: 실험 서버 이름, 실행한 커밋 해시, 데이터 체크섬 일치 여부, E0 합격 여부와 칸별 차이, 실패하거나 다시 돌린 실행, 이 명세에서 벗어난 점.
- 집계는 기존 `aggregation_strict.csv`와 같은 열 이름을 쓰면 이후 비교가 쉽다(작성 서버의 `outputs/rebuttal/synthetic_recovery_20260726/aggregation_strict.csv` 형식).

## 6. 계획하지 않는 실험

- **Fourier denoising baseline (aQS2 Q3).** 벤치마크의 측정이 규칙 격자가 아니어서 DFT를 직접 적용할 수 없다. 논의와 인용으로 답한다.
- **Gaussian·Laplace·Student-t 배경의 재실행.** 작성 서버에 three-seed 결과가 있으나 논문 App. G(ten-trial)와 값이 다르다. 저자 결정(`README.md` D3) 전에는 추가로 돌리지 않는다.
- **q ≥ 3의 OrPINN.** q-Gaussian이 정규화되지 않는 범위다.
