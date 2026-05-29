from scripts.validate_gold_corpus import validate_gold_corpus


def test_gold_corpus_validator_passes():
    totals = validate_gold_corpus()

    assert totals["policies"] == 5
    assert totals["json_files"] == 30
    assert totals["facts"] == 100
    assert totals["heading_labels"] >= 25
    assert totals["sections"] >= 25
    assert totals["clauses"] >= 25
    assert totals["status_counts"].get("requires_manual_review", 0) == 0
