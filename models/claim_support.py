from pydantic import BaseModel, Field


class ClaimSupport(BaseModel):
    claim_sources: dict[str, list[str]] = Field(default_factory=dict)