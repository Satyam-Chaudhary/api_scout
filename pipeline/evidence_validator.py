from models.app_research import AppResearch


CLAIM_FIELDS = [
    "description",
    "public_api",
    "auth_methods",
    "developer_access",
    "access_requirements",
    "api_types",
    "api_breadth",
    "official_mcp",
    "mcp_url",
    "primary_blocker",
]


def validate_evidence(research: AppResearch) -> list[str]:
    """Identify research claims that lack associated evidence."""

    findings = research.model_dump(mode="json")

    supported_claims = {
        evidence.claim
        for evidence in research.evidence
    }

    issues = []

    for field in CLAIM_FIELDS:

        value = findings.get(field)

        # Don't require evidence for empty or unknown values.
        if value in (None, "", "unknown"):
            continue

        if isinstance(value, list) and not value:
            continue

        if field not in supported_claims:
            issues.append(f"{field} lacks supporting evidence")

    return issues