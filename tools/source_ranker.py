from urllib.parse import urlparse


def classify_source(url: str, app_name: str) -> dict:
    hostname = (urlparse(url).hostname or "").lower()
    hostname = hostname.removeprefix("www.")

    app_slug = (
        app_name.lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    domain_labels = [
        label.replace("-", "").replace("_", "")
        for label in hostname.split(".")
    ]

    # Match the app name against individual domain labels.
    # Avoid substring matches like "salesforce" in "salesforceben".
    is_app_domain = app_slug in domain_labels

    if is_app_domain:
        if any(
            label in {"docs", "developer", "developers", "api"}
            for label in domain_labels
        ):
            return {
                "source_type": "documentation_candidate",
                "source_score": 70,
            }

        return {
            "source_type": "potential_official",
            "source_score": 100,
        }

    if hostname == "github.com":
        return {
            "source_type": "github",
            "source_score": 80,
        }

    if any(
        label in {"docs", "developer", "developers", "api"}
        for label in domain_labels
    ):
        return {
            "source_type": "documentation_candidate",
            "source_score": 50,
        }

    if any(
        word in hostname
        for word in ["blog", "medium"]
    ):
        return {
            "source_type": "blog",
            "source_score": 40,
        }

    return {
        "source_type": "third_party",
        "source_score": 30,
    }