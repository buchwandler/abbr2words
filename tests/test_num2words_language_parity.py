from __future__ import annotations

import json
from pathlib import Path

SNAPSHOT = Path(__file__).parent / "data" / "num2words_language_registry.json"


def _snapshot() -> dict[str, object]:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_pinned_registry_snapshot_metadata() -> None:
    snapshot = _snapshot()

    assert snapshot["repository"] == "savoirfairelinux/num2words"
    assert snapshot["stable_ref"] == "v0.5.14"
    assert snapshot["master_ref"] == "07814cb114157f582c40a00119c2e9faba8dcee2"


def test_master_registry_is_the_authoritative_63_key_contract() -> None:
    snapshot = _snapshot()
    stable = set(snapshot["stable_keys"])
    master = list(snapshot["master_keys"])

    assert len(stable) == 56
    assert len(master) == 63
    assert len(set(master)) == 63
    assert set(master) - stable == {"hi", "hy", "mn", "zh", "zh_CN", "zh_HK", "zh_TW"}


def test_readme_discrepancies_are_explicitly_preserved() -> None:
    snapshot = _snapshot()

    assert snapshot["readme_only"] == ["en_GB", "eu"]
    assert snapshot["registry_only_vs_readme"] == ["eo", "es_NI"]
