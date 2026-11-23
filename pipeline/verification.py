from models.app_research import AppResearch


CRITICAL_CLAIMS = [
    "public_api",
    "developer_access",
    "api_breadth",
    "official_mcp",
]


def verify_research(research: AppResearch) -> list[str]:
    supported = {
        evidence.claim
        for evidence in research.evidence
    }

    issues = []

    for claim in CRITICAL_CLAIMS:
        value = getattr(research, claim, None)

        if value in (None, "", "unknown"):
            continue

        if isinstance(value, list) and not value:
            continue

        if claim not in supported:
            issues.append(
                f"Critical claim '{claim}' lacks claim-level evidence"
            )

    if not research.sources:
        issues.append("No sources collected")

    if len(research.sources) < 2:
        issues.append("Insufficient source diversity")

    research.human_review_required = bool(issues)

    if issues:
        research.verification_status = "needs_review" # type: ignore
    else:
        research.verification_status = "unverified" # type: ignore

    return issues