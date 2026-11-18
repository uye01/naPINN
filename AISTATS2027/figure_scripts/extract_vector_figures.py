"""Extract the original vector figures embedded in naPINN_preprint.pdf.

pdfTeX embeds each included PDF as a Form XObject, so the original figure
files survive inside the compiled preprint even though `paper/figures/` was
never committed. Each XObject is written out as a one-page PDF with the
original bounding box. Document metadata is left empty.

Usage: python3 extract_vector_figures.py OUT_DIR
"""

import sys
from pathlib import Path

import pikepdf

REPO = Path(__file__).resolve().parents[2]
PREPRINT = REPO / "naPINN_preprint.pdf"

# object id in the preprint -> output name (original file in the PTEX.FileName key)
TARGETS = {
    (4, 0): "framework",      # main_figure_v3.pdf
    (57, 0): "qualitative",   # result_viz_v1.pdf
    (120, 0): "ratio_curve",  # performance_ratio_plot_v2.pdf
    (121, 0): "noise_pdf",    # noise_pdf_comparison_v3.pdf
    (224, 0): "gate",         # allencahn_b4_na_remade_gate_sigmoid_analysis_v4.pdf
    (225, 0): "gate_params",  # gate_params_two_panel_v2.pdf
    (271, 0): "rej_cost",     # rej_cost_sensitivity_v1.pdf
}


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    src = pikepdf.open(PREPRINT)
    for objgen, name in TARGETS.items():
        xo = src.get_object(objgen)
        dst = pikepdf.new()
        fx = dst.copy_foreign(xo)
        x0, y0, x1, y1 = (float(v) for v in xo.BBox)
        page = pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=[0, 0, x1 - x0, y1 - y0],
            Resources=pikepdf.Dictionary(XObject=pikepdf.Dictionary(Fx=fx)),
            Contents=dst.make_stream(f"q 1 0 0 1 {-x0} {-y0} cm /Fx Do Q".encode()),
        )
        dst.pages.append(pikepdf.Page(page))
        dst.save(out_dir / f"{name}.pdf")
        print(f"wrote {out_dir / name}.pdf")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
