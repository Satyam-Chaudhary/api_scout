from models.app_research import AppResearch
from pipeline.evidence_validator import validate_evidence
from models.source import SourceRecord


def test_missing_evidence_is_flagged():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="yes",
        sources=[
            SourceRecord(
                url="https://example.com/api-docs",
                excerpt="API documentation for TestApp",
            )
        ],
    )

    issues = validate_evidence(research)

    assert "public_api lacks supporting evidence" in issues


def test_unknown_claim_does_not_require_evidence():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="unknown",
    )

    issues = validate_evidence(research)

    assert "public_api lacks supporting evidence" not in issues


def test_empty_list_does_not_require_evidence():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        auth_methods=[],
    )

    issues = validate_evidence(research)

    assert "auth_methods lacks supporting evidence" not in issues