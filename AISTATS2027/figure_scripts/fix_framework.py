"""Relabel two items in the framework figure to match the paper.

1. The EBM output "log q" becomes l_phi (typeset in Latin Modern Math).
2. The estimator label "phi_EBM" becomes "Density Estimator", set in the
   figure's own embedded Cambria subset, at the size and baseline of the
   existing "Reliability Gate" label. The subset has no cmap entry for "E", so
   the E glyph already used in the "EBM" subscript is mapped to it.

Old labels are removed by redaction, so their text is gone from the file.

Usage: python3 fix_framework.py ORIGINAL_FRAMEWORK_PDF OUT_PDF
"""

import sys
import tempfile
from pathlib import Path

import pymupdf
from fontTools.ttLib import TTFont

LM_MATH = "/usr/share/texmf/fonts/opentype/public/lm-math/latinmodern-math.otf"
LOGQ_BOX = pymupdf.Rect(495.2, 122.6, 518.0, 132.6)    # inside the label's rounded box
PHI_EBM_BOX = pymupdf.Rect(450.0, 87.5, 484.0, 105.0)  # "phi_EBM" text only
CAMBRIA_XREF = 12


def patched_cambria(doc, tmpdir):
    _, ext, _, buf = doc.extract_font(CAMBRIA_XREF)
    path = Path(tmpdir) / f"cambria.{ext}"
    path.write_bytes(buf)
    font = TTFont(path)
    e_glyph = font.getGlyphOrder()[2889]  # the "E" of the EBM subscript
    for table in font["cmap"].tables:
        table.cmap[ord("E")] = e_glyph
    font.save(path)
    return str(path)


def main(src, out):
    doc = pymupdf.open(src)
    page = doc[0]

    gate = next(s for b in page.get_text("dict")["blocks"] for l in b.get("lines", [])
                for s in l["spans"] if s["text"] == "Reliability Gate")
    size, baseline = gate["size"], gate["origin"][1]

    page.add_redact_annot(LOGQ_BOX, fill=(1, 1, 1))
    page.add_redact_annot(PHI_EBM_BOX, fill=False)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)

    # 1. log q -> l_phi
    page.insert_font(fontname="lmmath", fontfile=LM_MATH)
    lm = pymupdf.Font(fontfile=LM_MATH)
    big, small = 13.0, 9.0
    width = lm.text_length("ℓ", big) + lm.text_length("\U0001D719", small) + 0.3
    x0 = (LOGQ_BOX.x0 + LOGQ_BOX.x1) / 2 - width / 2
    page.insert_text((x0, 131.2), "ℓ", fontname="lmmath", fontsize=big)
    page.insert_text((x0 + lm.text_length("ℓ", big) + 0.3, 133.4),
                     "\U0001D719", fontname="lmmath", fontsize=small)

    # 2. phi_EBM -> Density Estimator, word gap taken from "Reliability Gate"
    with tempfile.TemporaryDirectory() as tmp:
        cam_path = patched_cambria(doc, tmp)
        page.insert_font(fontname="cambria", fontfile=cam_path)
        cam = pymupdf.Font(fontfile=cam_path)
        gap = (gate["bbox"][2] - gate["bbox"][0]) - (
            cam.text_length("Reliability", size) + cam.text_length("Gate", size))
        w1, w2 = cam.text_length("Density", size), cam.text_length("Estimator", size)
        center = (PHI_EBM_BOX.x0 + PHI_EBM_BOX.x1) / 2
        x0 = center - (w1 + gap + w2) / 2
        page.insert_text((x0, baseline), "Density", fontname="cambria", fontsize=size)
        page.insert_text((x0 + w1 + gap, baseline), "Estimator", fontname="cambria", fontsize=size)
        doc.set_metadata({})
        doc.save(out, garbage=4, deflate=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
