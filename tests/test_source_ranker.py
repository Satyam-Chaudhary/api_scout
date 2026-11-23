from tools.source_ranker import classify_source


def test_potential_official_domain():
    result = classify_source(
        "https://developer.salesforce.com/docs/apis",
        "Salesforce",
    )

    assert result["source_type"] == "documentation_candidate"


def test_github_source():
    result = classify_source(
        "https://github.com/example/project",
        "Salesforce",
    )

    assert result["source_type"] == "github"


def test_third_party_source():
    result = classify_source(
        "https://example-news.com/article",
        "Salesforce",
    )

    assert result["source_type"] == "third_party"