from models.app_research import AppResearch, Evidence
from models.extraction import ExtractionResult
from pipeline.researcher import research_app
from tools.llm import generate_structured
from pipeline.evidence_validator import validate_evidence
from pipeline.buildability_engine import assess_buildability
from analytics.confidence import calculate_confidence
from models.app_research import ResearchStatus, VerificationStatus

async def analyze_app(
    app_name: str,
    category: str = "Uncategorized",
) -> AppResearch:

    sources = await research_app(app_name)

    if not sources:
        return AppResearch(
            app_name=app_name,
            category=category,
        )

    ranked_sources = sorted(
        sources,
        key=lambda source: (source.source_score + source.search_score * 20),
        reverse=True,
    )

    topic_patterns = {
        "api_overview": [
            "api overview",
            "platform api",
            "api reference",
            "rest api",
            "web api",
        ],
        "auth": [
            "oauth",
            "authentication",
            "authorization",
            "access token",
            "connected app",
        ],
        "mcp_docs": [
            "model context protocol",
            "mcp support",
            "mcp integration",
            "mcp documentation",
        ],
        "mcp_implementation": [
            "mcp server",
            "mcp-server",
        ],
    }

    selected_sources = []
    selected_urls = set()

    def is_preferred_source(source):
        url = str(source.url).lower()

        # Strong preference for sources already classified
        # as potentially official.
        if source.source_score >= 100:
            return 2

        # Prefer vendor-related GitHub organizations
        # over unrelated/community organizations.
        if "github.com" in url:
            path = url.split("github.com/", 1)[-1]
            organization = path.split("/", 1)[0]

            if app_name.lower().replace(" ", "") in organization.lower():
                return 1

        return 0

    for topic, keywords in topic_patterns.items():

        candidates = []

        for source in ranked_sources:

            if str(source.url) in selected_urls:
                continue

            searchable_text = (source.title + " " + source.excerpt[:3000]).lower()

            if any(keyword in searchable_text for keyword in keywords):
                candidates.append(source)

        # Prefer potentially official sources within each topic.
        candidates.sort(
            key=lambda source: (
                is_preferred_source(source),
                source.source_score + source.search_score * 20,
            ),
            reverse=True,
        )

        if candidates:

            selected_source = candidates[0]

            selected_sources.append(selected_source)
            selected_urls.add(str(selected_source.url))

    # Fill unused slots with the best remaining sources.
    for source in ranked_sources:

        if len(selected_sources) >= 4:
            break

        if str(source.url) not in selected_urls:

            selected_sources.append(source)
            selected_urls.add(str(source.url))

    selected_sources = selected_sources[:4]

    print("\nSOURCES SELECTED FOR LLM")

    for source in selected_sources:
        print(
            f"\n{source.title}\n"
            f"URL: {source.url}\n"
            f"Source score: {source.source_score}\n"
            f"Search score: {source.search_score}"
        )

    # Prepare source content for the LLM
    evidence_text = ""

    for i, source in enumerate(selected_sources, start=1):
        evidence_text = ""
        source_map = {}

        for i, source in enumerate(selected_sources, start=1):
            source_id = f"S{i}"
            source_map[source_id] = source

            evidence_text += f"""
            SOURCE ID: {source_id}
            Title: {source.title}
            URL: {source.url}
            Source type: {source.source_type}
            Content:
            {source.excerpt[:2500]}
            -----------------------------
            """

    prompt = f"""
    You are an API research analyst investigating SaaS applications.

    Your task is to extract factual information about {app_name}
    based ONLY on the research sources provided below.

    RESEARCH RULES:

    1. Do not guess or assume information.
    2. If information is not supported by the sources, use UNKNOWN.
    3. An API existing does not automatically mean developer access is self-service.
    4. Authentication methods must be explicitly supported by sources.
    5. Do not confuse authentication requirements with access restrictions.
    6. Do not assume an application has an official MCP server.
    7. Do not invent API types, capabilities, restrictions, or requirements.
    8. Be conservative when evaluating API breadth.
    9. Use concise, factual descriptions.
    10. Do not generate evidence objects, URLs, timestamps, citations,
        source types, or excerpts. Python handles source provenance separately.
    11. Use MCPAvailability.UNKNOWN when the provided sources do not establish
    whether an official MCP server exists.
    12. Use MCPAvailability.NO only when the sources provide affirmative,
        reliable evidence that an official MCP server does not exist.
    13. Failure to discover an official MCP server is not evidence that one
        does not exist.
    14. Distinguish API authentication requirements from actual blockers to
        building an integration toolkit.
    15. Do not infer API breadth from a narrow documentation page.

    FIELDS TO EXTRACT:

    - description
    - public_api
    - auth_methods
    - developer_access
    - access_requirements
    - api_types
    - api_breadth
    - official_mcp
    - mcp_url
    - primary_blocker
    
    CLAIM SOURCE MAPPING:

    For each factual field you extract, identify the SOURCE IDs that
    support that field.

    Use this mapping structure:

    {{
        "claim_sources": {{
            "description": ["S1"],
            "public_api": ["S1"],
            "auth_methods": ["S2"],
            "developer_access": ["S2"],
            "access_requirements": ["S2"],
            "api_types": ["S1"],
            "api_breadth": ["S1"],
            "official_mcp": ["S3"],
            "mcp_url": ["S3"],
            "primary_blocker": ["S2"]
        }}
    }}

    Rules:
    - Only reference SOURCE IDs that exist in the supplied sources.
    - Only reference sources that genuinely support the associated claim.
    - A source mentioning a product is not automatically evidence for every field.
    - Use an empty list when a claim is not supported.
    - Do not invent source IDs.
    - Do not force a source onto a claim just to fill the mapping.

    RESEARCH SOURCES:

    {evidence_text}

    Extract the research findings into the provided structured schema.
    """

    extraction = await generate_structured(
        prompt,
        ExtractionResult,
    )
    evidence_records = []

    for claim_name, source_ids in extraction.claim_sources.items(): # type: ignore

        for source_id in source_ids:

            source = source_map.get(source_id) # type: ignore

            # Reject invalid source IDs.
            if source is None:
                continue

            evidence_records.append(
                Evidence(
                    claim=claim_name,
                    url=source.url,
                    source_type=source.source_type,
                    excerpt=source.excerpt[:500],
                    retrieved_at=source.retrieved_at.isoformat(),
                )
            )

    # Construct the final research record
    extracted_data = extraction.model_dump(exclude={"claim_sources"})

    research = AppResearch(
        app_name=app_name,
        category=category,
        **extracted_data,
        evidence=evidence_records,
        sources=sources,
    )
    assessment = assess_buildability(research)

    research.buildability = assessment.decision
    research.buildability_reasons = assessment.reasons
    research.buildability_risks = assessment.risks
    research.research_status = ResearchStatus.COMPLETED
    research.source_count = len(research.sources)
    issues = validate_evidence(research)

    if issues:
        research.human_review_required = True
        research.verification_status = VerificationStatus.NEEDS_REVIEW
    
    confidence_result = calculate_confidence(research)

    research.confidence = confidence_result["confidence"]

    return research

