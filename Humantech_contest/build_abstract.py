"""Fill the Humantech Paper Awards extended-abstract template with the naPINN work.

Rebuilds word/document.xml from the template's own formatting conventions:
  title 20 pt bold, abstract 10 pt bold, section headings 11 pt bold small-caps,
  body 10 pt, figure/table captions 9 pt (bold label), references 9 pt.
The title/abstract/teaser-figure block reuses the template's full-width w:framePr
so it spans both columns of the 2-column section.

Usage:  python3 build_abstract.py [--template naPINN_abstract_template.docx]
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FIGDIR = REPO / "workshop_paper" / "figures"

# Full-width frame lifted verbatim from the template's title block.
FRAME = ('<w:framePr w:w="10065" w:hSpace="187" w:vSpace="187" w:wrap="notBeside"'
         ' w:vAnchor="text" w:hAnchor="page" w:x="911" w:y="127"/>')

SZ_TITLE, SZ_HEAD, SZ_SMALL = 40, 22, 18  # half-points: 20 pt, 11 pt, 9 pt

# ---------------------------------------------------------------- inline markup
# *x* italic   ~{x} subscript   ^{x} superscript   @{x} bold
TOKEN = re.compile(r"(\*[^*]+\*|~\{[^}]*\}|\^\{[^}]*\}|@\{[^}]*\})")


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tokens(text: str):
    out = []
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("*"):
            out.append((tok[1:-1], {"i"}))
        elif tok.startswith("~{"):
            out.append((tok[2:-1], {"sub"}))
        elif tok.startswith("^{"):
            out.append((tok[2:-1], {"sup"}))
        elif tok.startswith("@{"):
            out.append((tok[2:-1], {"b"}))
        else:
            out.append((tok, set()))
    return out


def run_xml(text, flags, *, sz=None, bold=False, italic=False, smallcaps=False):
    rp = []
    if bold or "b" in flags:
        rp.append("<w:b/><w:bCs/>")
    if italic or "i" in flags:
        rp.append("<w:i/><w:iCs/>")
    if smallcaps:
        rp.append('<w:smallCaps/><w:kern w:val="28"/>')
    if sz:
        rp.append(f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
    if "sub" in flags:
        rp.append('<w:vertAlign w:val="subscript"/>')
    if "sup" in flags:
        rp.append('<w:vertAlign w:val="superscript"/>')
    rpr = f"<w:rPr>{''.join(rp)}</w:rPr>" if rp else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def frame_el():
    """A standalone <w:framePr> element ready to insert into a pPr."""
    return parse_xml(FRAME.replace("<w:framePr ", f'<w:framePr {nsdecls("w")} '))


def para_xml(text="", *, ppr_inner="", **run_kw) -> str:
    body = "".join(run_xml(t, f, **run_kw) for t, f in tokens(text)) if text else ""
    ppr = f"<w:pPr>{ppr_inner}</w:pPr>" if ppr_inner else ""
    return f"<w:p {nsdecls('w')}>{ppr}{body}</w:p>"


# ------------------------------------------------------------ paragraph recipes
SPACING = '<w:spacing w:before="60"/>'
JC_BOTH = '<w:jc w:val="both"/>'
INDENT = '<w:ind w:firstLineChars="100" w:firstLine="200"/>'


def p_frame(text="", **kw):
    return para_xml(text, ppr_inner=FRAME + (JC_BOTH if text else ""), **kw)


def p_heading(text):
    return para_xml(text, ppr_inner=SPACING, sz=SZ_HEAD, bold=True, smallcaps=True)


def p_body(text, indent=True):
    return para_xml(text, ppr_inner=SPACING + (INDENT if indent else "") + JC_BOTH)


def p_caption(text, keep=False):
    return para_xml(text,
                    ppr_inner=('<w:keepNext/>' if keep else "")
                    + '<w:adjustRightInd w:val="0"/>' + SPACING + JC_BOTH, sz=SZ_SMALL)


def p_equation(text):
    return para_xml(text, ppr_inner=SPACING + '<w:jc w:val="center"/>')


def p_reference(text):
    return para_xml(text, ppr_inner=SPACING + '<w:ind w:left="220" w:hanging="220"/>'
                    + JC_BOTH, sz=16)


def p_blank(frame=False, sz=10):
    """A blank separator line. Default 7 pt: still a visible blank line, half the cost."""
    inner = FRAME if frame else ""
    if sz:
        inner += f'<w:rPr><w:sz w:val="{sz}"/></w:rPr>'
    return para_xml(ppr_inner=inner)


# ------------------------------------------------------------------- the content
TITLE = ("Noise-Adaptive Physics-Informed Neural Networks for Recovering Physics "
         "from Corrupted Measurements")

ABSTRACT = (
    "@{(Abstract)} Physics-informed neural networks (PINNs) recover unknown physical "
    "fields and equation coefficients from sparse sensor measurements, but their squared "
    "data loss gives the most corrupted observations the largest gradients, so a few "
    "faulty sensors can dominate training. We propose the noise-adaptive PINN (naPINN), "
    "which requires no prior knowledge of the measurement-noise distribution: it learns "
    "the distribution of measurement residuals online and converts the resulting "
    "log-density into a trainable per-measurement gate, fitted on detached residuals, "
    "that reweights a conventional reconstruction loss, with a rejection cost preventing "
    "the degenerate solution in which every measurement is discarded. On three simulated "
    "benchmarks under multimodal non-Gaussian noise and gross outliers, naPINN roughly "
    "halves the error of tuned robust losses, outperforms six screening procedures, and "
    "loses the gain if the gate is frozen. On real time-resolved particle "
    "image velocimetry under a nominal Navier–Stokes model, it is the most accurate of "
    "eight methods at both corruption levels and on every seed, excluding about 99% of "
    "the corrupted components while keeping over 95% of the rest. naPINN therefore turns "
    "unknown sensor corruption into an explicit, auditable per-measurement decision."
)

FIG1_CAPTION = (
    "@{Fig. 1. }The naPINN framework. An energy-based model scores the log-likelihood of "
    "each measurement residual under the learned noise distribution; a trainable gate "
    "turns that score into a per-measurement weight in the data loss."
)

FIG2_CAPTION = (
    "@{Fig. 2. }The trained reliability gate on Allen–Cahn at 10% corruption. The learned "
    "cutoff becomes a sharp inclusion decision rather than a diffuse reweighting. Labels "
    "are used only for diagnosis, never to train the gate."
)

TABLE1_CAPTION = (
    "@{Table 1. }Held-out field rMAE (lower is better), seeds 40–42; simulated benchmarks "
    "use 15% corrupted rows. The Bayesian row is mean-field variational inference, not "
    "Hamiltonian Monte Carlo, and was not run on PIV."
)

TABLE1 = {
    "group": ["", "Simulated benchmarks", "Real PIV"],
    "head": ["Method", "Allen–Cahn", "Burgers", "λ–ω", "10%", "15%"],
    "rows": [
        ("PINN (MSE)", "0.860", "0.577", "0.427", "0.406", "0.574"),
        ("B-PINN (VI)", "0.885", "0.592", "0.490", "–", "–"),
        ("LAD-PINN [2]", "0.357", "0.244", "0.198", "0.246", "0.270"),
        ("OrPINN [3]", "0.285", "0.190", "0.137", "0.214", "0.231"),
        ("PINN-EBM [7]", "0.153", "*0.077*", "0.082", "0.224", "0.336"),
        ("naPINN", "*0.092*", "0.082", "*0.071*", "*0.155*", "*0.160*"),
    ],
}

INTRO = [
    "Physics-informed neural networks (PINNs) embed a partial differential equation "
    "(PDE) residual directly into neural-network training, and have become a practical "
    "tool for inverse problems in which a latent field and unknown physical coefficients "
    "must be recovered from sparse, scattered measurements [1]. Almost every such "
    "formulation fits the measurements with a mean squared error (MSE) data loss, which "
    "is not a neutral choice: MSE is the negative log-likelihood of additive Gaussian "
    "noise, so a standard inverse PINN assumes that the sensors are Gaussian.",

    "Real measurement systems violate it. Sensor faults, calibration drift and "
    "environmental interference produce asymmetric, multimodal or heavy-tailed noise "
    "together with gross outliers, and because the squared loss assigns the largest "
    "gradient to the largest residual, a handful of corrupted observations can dominate "
    "training and bias both the reconstructed field and the identified coefficient. "
    "Existing remedies each presuppose something unavailable in deployment: "
    "fixed robust losses [2, 3] still prescribe the shape of the noise law in advance; "
    "Bayesian PINNs quantify posterior uncertainty under an assumed likelihood [4] rather "
    "than deciding which measurements to trust; and pre-processing screens need a "
    "threshold calibrated against corruption labels that are themselves unknown.",

    "We propose naPINN. Its premise is that once the network is roughly aligned with the "
    "measurements, the distribution of the measurement residuals is itself an estimate of "
    "the corruption process. naPINN estimates that distribution online without "
    "prescribing a parametric family, converts each residual’s log-likelihood into a "
    "trainable inclusion weight, and trains against a gated reconstruction loss. The "
    "result is a more robust solver that also reports which sensors failed.",
]

METHOD_1 = (
    "We consider a PDE with an unknown coefficient η, observed through sparse noisy "
    "measurements and with no boundary or initial conditions supplied. A network "
    "*û*~{θ} is trained on an automatic-differentiation PDE residual together with a "
    "data term, with η optimised jointly. Writing the measurement residual as "
    "*r*~{i} = *y*~{i} − *û*~{θ}(*x*~{i}, *t*~{i}), the usual data term treats every "
    "observation as equally trustworthy; naPINN estimates the trustworthiness instead "
    "(Fig. 1)."
)

METHOD_2 = (
    "@{Residual reliability. }A single gross outlier can shift a minibatch’s residual "
    "standard deviation by an order of magnitude, so residuals are first normalised by a "
    "running scale, an exponential moving average of the per-minibatch residual standard "
    "deviation. A density estimator φ fitted to them returns a log-density that is small "
    "for an atypical residual; we use a one-dimensional energy-based model (EBM) [5], "
    "whose negative energy is that log-density. Because the estimator need only emit a "
    "scalar score, kernel-density and Gaussian-mixture estimators drop in unchanged, and "
    "it is fitted on detached residuals, so it never back-propagates into the network."
)

METHOD_3 = (
    "@{Reliability gate. }Log-densities are standardised within each minibatch, which "
    "keeps one cutoff comparable across estimators and training stages. A sigmoid turns "
    "the standardised score *z*~{i} into an inclusion weight "
    "*g*~{i} = sig(*a*(*z*~{i} + τ)) ∈ (0, 1), with steepness *a* and cutoff τ both "
    "trained, so a measurement is excluded once its log-density falls more than τ "
    "minibatch standard deviations below the mean. The gate weights the reconstruction "
    "loss, and a rejection cost λ~{rej} penalises exclusion, ruling out the degenerate "
    "solution *g*~{i} ≡ 0:"
)

EQ = ("ℒ = *w*~{PDE}ℒ~{PDE} + (1/*N*)∑*g*~{i}‖*r*~{i}‖^{2} "
      "+ λ~{rej}(1/*N*)∑(1 − *g*~{i}).    (1)")

METHOD_5 = (
    "@{Staged training. }naPINN performs 5,000 warm-up updates, a one-off 5,000-step "
    "estimator-only stage and 25,000 joint updates — the same 30,000 network updates as "
    "every baseline; the estimator stage costs 3–4% of wall-clock time."
)

EXP_SETUP = (
    "We use three two-dimensional time-dependent PDE benchmarks — Allen–Cahn, Burgers "
    "and a λ–ω reaction–diffusion system — whose reference solutions come from the same "
    "operator that the PDE residual enforces, so the governing equation is exact by "
    "construction. Measurements are read from a fixed sensor grid and corrupted by a "
    "four-component Gaussian-mixture background, and 15% of the rows additionally receive "
    "a gross offset of three to ten background standard deviations. We then evaluate on "
    "real time-resolved particle image velocimetry (PIV) from a public benchmark of real "
    "physical measurements [6]: 192 fixed, irregularly placed sensors over 200 frames, "
    "scored against 1,549,400 held-out vectors at disjoint locations. Only the training "
    "sensors are corrupted, and the forward model is a nominal incompressible "
    "Navier–Stokes residual that only approximates the real flow, so these data also test "
    "reconstruction under model discrepancy. Baselines are a standard PINN, a Bayesian "
    "PINN [4], two tuned robust losses [2, 3] and PINN-EBM [7], which makes a learned "
    "residual likelihood the data loss itself. Each receives 30,000 network updates; we "
    "report held-out relative mean absolute error (rMAE) over three seeds."
)

EXP_RESULTS = (
    "Both methods that learn a residual density sit far below every fixed loss on the "
    "simulated benchmarks (Table 1), and naPINN roughly halves the error of the best tuned "
    "robust baseline. Between the two we claim no winner there: naPINN is lower on "
    "Allen–Cahn and λ–ω, direct likelihood optimisation on Burgers. On real PIV the "
    "ordering separates — naPINN reaches 0.155 and 0.160 rMAE at 10% and 15% corrupted "
    "rows, lowest of the eight methods run on that data and on every seed separately."
)

EXP_GATE = (
    "@{What the gate learns. }The trained gate becomes a sharp inclusion decision rather "
    "than a diffuse reweighting (Fig. 2). On Allen–Cahn at 10% corruption it rejects 2,209 "
    "of 2,250 corrupted measurements and only 152 of 20,250 clean ones; on real PIV it "
    "excludes about 99% of the gross components while keeping over 95% of the rest, so the "
    "weights double as an anomaly report on the sensor network."
)

EXP_ABLATION = (
    "@{What carries the result. }Learning the inclusion boundary, not merely estimating a "
    "density, is what matters: freezing the gate at its initial cutoff while keeping the "
    "learned density raises rMAE to 0.675, 0.514 and 0.351. Six screening procedures — "
    "three pre-training screens tuned against the true corruption labels, a fixed-quantile "
    "screen, a learnable residual threshold and a published two-stage screen — all fall "
    "short, and the strongest stays five to twenty times more seed-variable."
)

CONCLUSION = (
    "naPINN recovers PDE solutions and coefficients from measurements whose noise law is "
    "unknown, by learning the residual distribution online and gating each observation by "
    "it, and it returns an inclusion decision per measurement that doubles as a "
    "sensor-fault report. Because the learned density decides whether a measurement counts "
    "rather than defining the fitting objective, it stays effective even when the governing "
    "equation is only approximate."
)

REFERENCES = [
    "[1] Raissi, M. et al. Physics-informed neural networks: A deep learning framework "
    "for solving forward and inverse problems involving nonlinear partial differential "
    "equations. *J. Comput. Phys.* @{378}, 686–707 (2019)",
    "[2] Peng, W. et al. Robust regression with highly corrupted data via physics "
    "informed neural networks. arXiv: 2210.10646 (2022)",
    "[3] Duarte, D. H. G. et al. Outlier-resistant physics-informed neural network. "
    "*Phys. Rev. E* @{111}, L023302 (2025)",
    "[4] Yang, L. et al. B-PINNs: Bayesian physics-informed neural networks for forward "
    "and inverse PDE problems with noisy data. *J. Comput. Phys.* @{425}, 109913 (2021)",
    "[5] LeCun, Y. et al. A tutorial on energy-based learning. "
    "*Predicting Structured Data* (MIT Press, 2006)",
    "[6] Hu, P. et al. RealPDEBench: A benchmark for complex physical systems with "
    "real-world data. *Proc. Int. Conf. Learn. Represent.* (2026)",
    "[7] Pilar, P. & Wahlström, N. Physics-informed neural networks with unknown "
    "measurement noise. *Proc. Annu. Learn. Dyn. Control Conf.* @{242}, 235–247 (2024)",
]


# --------------------------------------------------------------------- assembly
def set_cell(cell, text, *, bold=False, sz=SZ_SMALL, align="center", keep=True):
    cell.text = ""
    p = cell.paragraphs[0]
    ppr = p._p.get_or_add_pPr()
    if keep:
        ppr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))
    ppr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="{align}"/>'))
    ppr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="20" w:after="20"/>'))
    for t, flags in tokens(text):
        # italic markup in the table means "best value" -> render bold instead
        xml = run_xml(t, set(), sz=sz, bold=bold or "i" in flags)
        p._p.append(parse_xml(xml.replace("<w:r>", f'<w:r {nsdecls("w")}>', 1)))


def cell_border(cell, edge, sz=8):
    tcpr = cell._tc.get_or_add_tcPr()
    borders = tcpr.find(qn("w:tcBorders"))
    if borders is None:
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        tcpr.append(borders)
    borders.append(parse_xml(
        f'<w:{edge} {nsdecls("w")} w:val="single" w:sz="{sz}" w:color="000000"/>'))


def build(template: Path, out: Path) -> Path:
    doc = Document(str(template))
    body = doc.element.body
    sect = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is not sect:
            body.remove(child)

    def add(xml: str):
        sect.addprevious(parse_xml(xml))

    # ---- full-width frame: title, abstract, teaser figure -------------------
    add(p_frame(TITLE, sz=SZ_TITLE, bold=True))
    add(p_blank(frame=True))
    add(p_frame(ABSTRACT, bold=True))
    add(p_blank(frame=True))

    pic = doc.add_paragraph()
    ppr = pic._p.get_or_add_pPr()
    ppr.append(frame_el())
    ppr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
    pic.add_run().add_picture(str(FIGDIR / "framework.png"), width=Cm(10.8))

    cap = parse_xml(p_caption(FIG1_CAPTION))
    cap.get_or_add_pPr().insert(0, frame_el())
    sect.addprevious(cap)
    add(p_blank(frame=True))

    # ---- two-column body ----------------------------------------------------
    add(p_blank())
    add(p_heading("1. INTRODUCTION"))
    add(p_blank())
    for i, t in enumerate(INTRO):
        add(p_body(t, indent=i > 0))

    add(p_blank())
    add(p_heading("2. METHOD"))
    add(p_blank())
    add(p_body(METHOD_1, indent=False))
    add(p_body(METHOD_2))
    add(p_body(METHOD_3))
    add(p_blank())
    add(p_equation(EQ))
    add(p_blank())
    add(p_body(METHOD_5, indent=False))

    add(p_blank())
    add(p_heading("3. EXPERIMENTS AND RESULTS"))
    add(p_blank())
    add(p_body(EXP_SETUP, indent=False))

    # Table 1 (caption above, per the template)
    add(p_blank())
    add(p_caption(TABLE1_CAPTION, keep=True))
    COLW = [1340, 860, 700, 620, 680, 680]  # twips; total 4880 = 8.6 cm = column width
    tbl = doc.add_table(rows=2 + len(TABLE1["rows"]), cols=6)
    tbl.autofit = False
    tblPr = tbl._tbl.tblPr
    for old in tblPr.findall(qn("w:tblW")):
        tblPr.remove(old)
    tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="{sum(COLW)}" w:type="dxa"/>'))
    tblPr.append(parse_xml(
        f'<w:tblCellMar {nsdecls("w")}><w:left w:w="40" w:type="dxa"/>'
        f'<w:right w:w="40" w:type="dxa"/></w:tblCellMar>'))
    grid = tbl._tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), COLW):
        gc.set(qn("w:w"), str(w))

    def set_w(cell, w):
        tcpr = cell._tc.get_or_add_tcPr()
        for old in tcpr.findall(qn("w:tcW")):
            tcpr.remove(old)
        tcpr.insert(0, parse_xml(f'<w:tcW {nsdecls("w")} w:w="{w}" w:type="dxa"/>'))

    for row in tbl.rows:
        for cell, w in zip(row.cells, COLW):
            set_w(cell, w)

    row0 = tbl.rows[0]
    c_blank = row0.cells[0]
    c_sim = row0.cells[1].merge(row0.cells[3])
    c_piv = row0.cells[4].merge(row0.cells[5])
    set_w(c_blank, COLW[0])
    set_w(c_sim, sum(COLW[1:4]))
    set_w(c_piv, sum(COLW[4:]))
    set_cell(c_blank, "")
    set_cell(c_sim, TABLE1["group"][1], sz=16)
    set_cell(c_piv, TABLE1["group"][2], sz=16)
    for c in (c_blank, c_sim, c_piv):
        cell_border(c, "top")
    cell_border(c_sim, "bottom")
    cell_border(c_piv, "bottom")
    for j, h in enumerate(TABLE1["head"]):
        set_cell(tbl.rows[1].cells[j], h, sz=16, align="left" if j == 0 else "center")
        cell_border(tbl.rows[1].cells[j], "bottom")
    for i, r in enumerate(TABLE1["rows"], start=2):
        for j, v in enumerate(r):
            last = i == len(TABLE1["rows"]) + 1
            set_cell(tbl.rows[i].cells[j], v, align="left" if j == 0 else "center",
                     keep=not last)
            if i == len(TABLE1["rows"]) + 1:
                cell_border(tbl.rows[i].cells[j], "bottom")
    add(p_blank())

    add(p_body(EXP_RESULTS, indent=False))
    add(p_body(EXP_GATE))

    add(p_blank())
    pic2 = doc.add_paragraph()
    pic2._p.get_or_add_pPr().append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
    pic2.add_run().add_picture(str(FIGDIR / "gate.png"), width=Cm(5.7))
    add(p_caption(FIG2_CAPTION))
    add(p_blank())

    add(p_body(EXP_ABLATION, indent=False))

    add(p_blank())
    add(p_heading("4. CONCLUSION"))
    add(p_blank())
    add(p_body(CONCLUSION, indent=False))

    add(p_blank())
    add(p_heading("References"))
    add(p_blank())
    for r in REFERENCES:
        add(p_reference(r))

    doc.save(str(out))
    return out


def scrub(path: Path):
    """Strip identifying metadata and refresh the stale odd-page header."""
    import zipfile

    tmp = path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(
            tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<dc:creator>.*?</dc:creator>", "<dc:creator></dc:creator>", s)
                s = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>",
                           "<cp:lastModifiedBy></cp:lastModifiedBy>", s)
                data = s.encode("utf-8")
            elif item.filename == "docProps/app.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<Company>.*?</Company>", "<Company></Company>", s)
                data = s.encode("utf-8")
            elif item.filename == "word/header2.xml":
                # template shipped a stale "23rd HumanTech Paper Award"
                s = data.decode("utf-8")
                state = {"n": 0}

                def _fix(m):
                    state["n"] += 1
                    txt = "33rd Samsung Humantech Paper Awards" if state["n"] == 1 else ""
                    return f"{m.group(1)}{txt}</w:t>"

                s = re.sub(r"(<w:t[^>]*>)(?:(?!</w:t>).)*</w:t>", _fix, s)
                data = s.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(str(tmp), str(path))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=str(HERE / "naPINN_abstract_template.docx"))
    ap.add_argument("--out", default=str(HERE / "naPINN_abstract.docx"))
    a = ap.parse_args()
    out = build(Path(a.template), Path(a.out))
    scrub(out)
    print("wrote", out)
