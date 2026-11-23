from pydantic import BaseModel, Field, field_validator

from models.app_research import (
    APIAvailability,
    DeveloperAccess,
    MCPAvailability,
)


class ExtractionResult(BaseModel):
    description: str = ""

    public_api: APIAvailability = APIAvailability.UNKNOWN
    auth_methods: list[str] = Field(default_factory=list)

    developer_access: DeveloperAccess = DeveloperAccess.UNKNOWN
    access_requirements: str = ""

    api_types: list[str] = Field(default_factory=list)
    api_breadth: str = "unknown"

    official_mcp: MCPAvailability = MCPAvailability.UNKNOWN
    mcp_url: str | None = None

    primary_blocker: str = ""
    
    
    @field_validator("mcp_url", mode="before")
    @classmethod
    def normalize_mcp_url(cls, value):
        if isinstance(value, str) and value.strip().lower() in {
            "unknown", "none", "null", ""
        }:
            return None

        return value