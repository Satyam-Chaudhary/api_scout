from models.app_research import AppResearch


IMPORTANT_CLAIMS = [
    "public_api",
    "developer_access",
    "api_breadth",
    "official_mcp",
    "buildability",
]


def calculate_confidence(research: AppResearch) -> dict:
    sources = research.sources
    evidence = research.evidence

    score = 0
    breakdown = {}

    # 1. Source quantity (max 20)
    source_score = min(len(sources) * 5, 20)
    score += source_score
    breakdown["source_quantity"] = source_score

    # 2. Source quality (max 25)
    official_sources = [
        s for s in sources
        if "official" in s.source_type.lower()
        or "documentation_candidate" in s.source_type.lower()
    ]

    if sources:
        official_ratio = len(official_sources) / len(sources)
        quality_score = round(official_ratio * 25)
    else:
        quality_score = 0

    score += quality_score
    breakdown["source_quality"] = quality_score

    # 3. Evidence coverage (max 30)
    supported_claims = {e.claim for e in evidence}

    covered = sum(
        1 for claim in IMPORTANT_CLAIMS
        if claim in supported_claims
    )

    coverage_score = round(
        (covered / len(IMPORTANT_CLAIMS)) * 30
    )

    score += coverage_score
    breakdown["evidence_coverage"] = coverage_score

    # 4. Evidence richness (max 15)
    rich_evidence = sum(
        1 for e in evidence
        if e.excerpt and len(e.excerpt.strip()) >= 50
    )

    richness_score = min(rich_evidence * 3, 15)
    score += richness_score
    breakdown["evidence_richness"] = richness_score

    # 5. Review penalty (max -10)
    penalty = 0

    if research.human_review_required:
        penalty = 10

    score -= penalty
    breakdown["review_penalty"] = penalty

    final_score = max(0, min(100, score))

    return {
        "confidence": final_score / 100,
        "score": final_score,
        "breakdown": breakdown,
    }