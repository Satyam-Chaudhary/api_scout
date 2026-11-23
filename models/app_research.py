from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, model_validator

from models.source import SourceRecord


class Buildability(str, Enum):
    BUILD = "build"
    BUILD_WITH_CONSTRAINTS = "build_with_constraints"
    OUTREACH_REQUIRED = "outreach_required"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class DeveloperAccess(str, Enum):
    SELF_SERVE = "self_serve"
    GATED = "gated"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class APIAvailability(str, Enum):
    YES = "yes"
    PARTIAL = "partial"
    NO = "no"
    UNKNOWN = "unknown"


class MCPAvailability(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class ResearchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"


class Evidence(BaseModel):
    claim: str
    url: HttpUrl
    source_type: str
    excerpt: str
    retrieved_at: str


class AppResearch(BaseModel):
    app_name: str
    category: str
    description: str = ""

    auth_methods: list[str] = Field(default_factory=list)
    developer_access: DeveloperAccess = DeveloperAccess.UNKNOWN
    access_requirements: str = ""

    public_api: APIAvailability = APIAvailability.UNKNOWN
    api_types: list[str] = Field(default_factory=list)
    api_breadth: str = "unknown"

    official_mcp: MCPAvailability = MCPAvailability.UNKNOWN
    mcp_url: str | None = None

    buildability: Buildability = Buildability.UNKNOWN
    
    buildability_reasons: list[str] = Field(default_factory=list)
    buildability_risks: list[str] = Field(default_factory=list)
    
    primary_blocker: str = ""

    evidence: list[Evidence] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    research_status: ResearchStatus = ResearchStatus.PENDING
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

    source_count: int = 0
    human_review_required: bool = False
    human_corrections: list[str] = Field(default_factory=list)
    

    @model_validator(mode="after")
    def validate_research_consistency(self):

        if self.public_api == APIAvailability.YES:
            api_evidence = [
                item for item in self.evidence
                if "api" in item.claim.lower()
            ]

            api_sources = [
                source for source in self.sources
                if "api" in source.excerpt.lower()
            ]

            if not api_evidence and not api_sources:
                raise ValueError(
                    "API availability requires API-specific evidence "
                    "or a source containing API-related information"
                )

        if self.official_mcp == MCPAvailability.YES:
            mcp_evidence = [
                item for item in self.evidence
                if "mcp" in item.claim.lower()
            ]

            mcp_sources = [
                source for source in self.sources
                if "mcp" in source.excerpt.lower()
            ]

            if not mcp_evidence and not mcp_sources:
                raise ValueError(
                    "MCP availability requires MCP-specific evidence "
                    "or a source containing MCP-related information"
                )

        return self
