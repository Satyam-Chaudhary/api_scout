from models.app_research import AppResearch


def test_create_minimal_app_research():
    app = AppResearch(
        app_name="Slack",
        category="Communications and Messaging",
    )

    assert app.app_name == "Slack"
    assert app.public_api.value == "unknown"
    assert app.buildability.value == "unknown"
    assert app.auth_methods == []
    assert app.confidence == 0.0


def test_lists_are_independent():
    app1 = AppResearch(
        app_name="Slack",
        category="Communications",
    )

    app2 = AppResearch(
        app_name="Discord",
        category="Communications",
    )

    app1.auth_methods.append("OAuth 2.0")

    assert app1.auth_methods == ["OAuth 2.0"]
    assert app2.auth_methods == []