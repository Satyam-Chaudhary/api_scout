from models.source import SourceRecord


def test_source_record_creation():
    source = SourceRecord(
        title="Salesforce REST API Documentation",
        url="https://developer.salesforce.com/docs", # type: ignore
        source_type="documentation_candidate",
        excerpt="Salesforce REST API documentation",
        search_score=0.9,
        source_score=70,
    )

    assert source.title == "Salesforce REST API Documentation"
    assert str(source.url) == "https://developer.salesforce.com/docs"
    assert source.source_score == 70
    assert source.retrieved_at is not None


def test_source_timestamp_is_automatically_generated():
    source = SourceRecord(
        url="https://example.com", # type: ignore
    )

    assert source.retrieved_at is not None