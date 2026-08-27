"""Release packaging guards."""

from pathlib import Path

import pytest

from statuta.release import package_release


def test_release_packaging_rejects_drafts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="only released"):
        package_release({"artifact_status": "draft"}, tmp_path / "rule.json")
