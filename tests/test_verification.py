from models.app_research import AppResearch
from models.source import SourceRecord
from pipeline.verification import verify_research


def test_missing_evidence_requires_review():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="yes",
        sources=[
            SourceRecord(
                url="https://example.com/api",
                excerpt="TestApp public API documentation.",
            ),
            SourceRecord(
                url="https://example.com/auth",
                excerpt="TestApp authentication documentation.",
            ),
        ],
    )

    issues = verify_research(research)

    assert issues
    assert research.human_review_required


def test_unknown_claims_do_not_trigger_missing_evidence():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        sources=[
            SourceRecord(
                url="https://example.com/1",
                excerpt="Documentation.",
            ),
            SourceRecord(
                url="https://example.com/2",
                excerpt="Additional documentation.",
            ),
        ],
    )

    issues = verify_research(research)

    assert not issues
    assert not research.human_review_required