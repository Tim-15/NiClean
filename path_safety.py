from __future__ import annotations

import os
from pathlib import Path


def unique_destination(
    desired: Path,
    original: Path,
    *,
    allow_original: bool = False,
) -> Path:
    """Choose an available destination without overwriting another file."""
    desired = Path(desired)
    original = Path(original)

    # Permit the exact same path only for intentional in-place replacement.
    if allow_original and os.path.abspath(desired) == os.path.abspath(original):
        return desired

    # lexists also detects broken symbolic links.
    if not os.path.lexists(desired):
        return desired

    for index in range(1, 100_000):
        candidate = desired.with_name(
            f"{desired.stem}_{index}{desired.suffix}"
        )
        if not os.path.lexists(candidate):
            return candidate

    raise FileExistsError(f"No available destination for {desired}")
