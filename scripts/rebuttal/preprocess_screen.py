#!/usr/bin/env python3
"""Statistical pre-processing screens shared by the synthetic and PIV runners.

Reviewer 6XZg asked for the baseline a practitioner would actually try: screen
the raw measurements statistically, drop what is flagged, then train an ordinary
PINN. Our MAD-PINN comparison does not answer that, because it screens between
two training stages and so already has a fitted field to form residuals against.

The maths lives here rather than in either runner so that the synthetic and the
real-PIV versions of the baseline are provably the same rule. Only the label
bookkeeping differs between them: the synthetic experiments record corrupted row
indices, while the PIV experiments carry a per-component boolean mask.

``global_z`` is the conventional z-score rule. ``global_mad`` is its robust
form, using the median absolute deviation because the standard deviation is
itself inflated by the outliers being screened. ``local_median`` compares each
measurement with the median of its nearest neighbours in the coordinate space,
which accounts for the solution field varying over space and time and is the
strongest of the three.
"""

from __future__ import annotations

import torch


SCREENS = ("global_z", "global_mad", "local_median")
NEIGHBOURS = 16


def compute_screen_mask(
    coordinates: torch.Tensor,
    values: torch.Tensor,
    kind: str,
    k: float,
) -> torch.Tensor:
    """Return a boolean mask over rows, True where the screen flags the row.

    ``coordinates`` is (N, D) and ``values`` is (N, C). A row is flagged if any
    of its components exceeds the threshold, which matches how the corruption is
    injected: per measurement row, with all components corrupted together.
    """
    if kind not in SCREENS:
        raise ValueError(f"Unsupported screen: {kind}")

    n_rows = values.shape[0]
    if kind == "global_z":
        centre = values.mean(dim=0, keepdim=True)
        scale = values.std(dim=0, unbiased=True, keepdim=True)
    elif kind == "global_mad":
        centre = values.median(dim=0, keepdim=True).values
        scale = 1.4826 * (values - centre).abs().median(dim=0, keepdim=True).values
    else:
        # Neighbourhood median. Chunked so the pairwise distance matrix never
        # has to be materialised for the full measurement set.
        centre = torch.empty_like(values)
        chunk = 2048
        for start in range(0, n_rows, chunk):
            stop = min(start + chunk, n_rows)
            distance = torch.cdist(coordinates[start:stop], coordinates)
            # Self sits at distance zero, so take one extra and drop it.
            index = distance.topk(NEIGHBOURS + 1, largest=False).indices[:, 1:]
            centre[start:stop] = values[index].median(dim=1).values
        scale = 1.4826 * (values - centre).abs().median(dim=0, keepdim=True).values

    scale = torch.clamp(scale, min=1.0e-12)
    return ((values - centre) / scale).abs().gt(k).any(dim=1)


def screen_diagnostics(
    flagged: torch.Tensor,
    corrupted: torch.Tensor,
    kind: str,
    k: float,
) -> dict:
    """Summarise what the screen removed, split by whether it should have.

    These two fractions, not the final error alone, are what explain the
    outcome, so every run records them.
    """
    return {
        "screen": kind,
        "k": k,
        "n_rows": int(flagged.numel()),
        "n_removed": int(flagged.sum()),
        "removed_fraction": float(flagged.float().mean()),
        "known_outlier_removed_fraction": (
            float(flagged[corrupted].float().mean()) if bool(corrupted.any()) else None
        ),
        "known_clean_removed_fraction": (
            float(flagged[~corrupted].float().mean())
            if bool((~corrupted).any())
            else None
        ),
    }
