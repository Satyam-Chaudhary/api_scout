import pytest
from models.app_research import (
    APIAvailability,
    AppResearch,
    MCPAvailability,
)


def test_api_yes_requires_api_evidence():
    with pytest.raises(ValueError, match="API-specific evidence"):
        AppResearch(
            app_name="Slack",
            category="Communications",
            public_api=APIAvailability.YES,
        )


def test_mcp_yes_requires_mcp_evidence():
    with pytest.raises(ValueError, match="MCP-specific evidence"):
        AppResearch(
            app_name="Slack",
            category="Communications",
            official_mcp=MCPAvailability.YES,
        )


def test_unknown_api_does_not_require_evidence():
    app = AppResearch(
        app_name="Unknown App",
        category="Testing",
    )

    assert app.public_api == APIAvailability.UNKNOWN