from models.app_research import AppResearch
from models.source import SourceRecord
from pipeline.buildability_engine import assess_buildability


def api_source():
    return SourceRecord(
        title="TestApp API Documentation",
        url="https://example.com/api-docs",
        excerpt="TestApp provides a comprehensive public API.",
        source_type="documentation_candidate",
    )


def mcp_source():
    return SourceRecord(
        title="TestApp MCP Documentation",
        url="https://example.com/mcp-docs",
        excerpt="TestApp provides an official MCP server.",
        source_type="documentation_candidate",
    )


def test_self_serve_comprehensive_api_is_buildable():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="yes",
        developer_access="self_serve",
        api_breadth="comprehensive",
        sources=[api_source()],
    )

    result = assess_buildability(research)

    assert result.decision == "build"


def test_gated_api_requires_outreach():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="yes",
        developer_access="gated",
        sources=[api_source()],
    )

    result = assess_buildability(research)

    assert result.decision == "outreach_required"


def test_partial_api_is_constrained():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="partial",
        developer_access="self_serve",
    )

    result = assess_buildability(research)

    assert result.decision == "build_with_constraints"


def test_no_api_and_no_mcp_is_blocked():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="no",
        official_mcp="no",
    )

    result = assess_buildability(research)

    assert result.decision == "blocked"


def test_unknown_api_does_not_mean_blocked():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        public_api="unknown",
        official_mcp="unknown",
    )

    result = assess_buildability(research)

    assert result.decision == "unknown"


def test_official_mcp_with_endpoint_is_buildable():
    research = AppResearch(
        app_name="TestApp",
        category="Testing",
        official_mcp="yes",
        mcp_url="https://example.com/mcp",
        sources=[mcp_source()],
    )

    result = assess_buildability(research)

    assert result.decision == "build"