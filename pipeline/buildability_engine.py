from dataclasses import dataclass, field

from models.app_research import (
    APIAvailability,
    AppResearch,
    Buildability,
    DeveloperAccess,
    MCPAvailability,
)


@dataclass
class BuildabilityAssessment:
    decision: Buildability
    reasons: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


def assess_buildability(research: AppResearch) -> BuildabilityAssessment:
    reasons = []
    risks = []

    api = research.public_api
    access = research.developer_access
    mcp = research.official_mcp

    # An officially available MCP server can provide an integration
    # path even when the conventional API is unavailable.
    if mcp == MCPAvailability.YES and research.mcp_url:
        reasons.append("An official MCP endpoint is documented.")

        if api == APIAvailability.YES:
            reasons.append("A public API is also available.")

        if access in (DeveloperAccess.GATED, DeveloperAccess.HYBRID):
            risks.append("Access may involve additional approval or restrictions.")

        return BuildabilityAssessment(
            decision=Buildability.BUILD_WITH_CONSTRAINTS
            if risks
            else Buildability.BUILD,
            reasons=reasons,
            risks=risks,
        )

    # Explicit lack of both integration paths.
    if api == APIAvailability.NO and mcp == MCPAvailability.NO:
        return BuildabilityAssessment(
            decision=Buildability.BLOCKED,
            reasons=[
                "No public API or official MCP integration path was identified."
            ],
        )

    # An API exists, but access requires vendor intervention.
    if api in (APIAvailability.YES, APIAvailability.PARTIAL):
        if access == DeveloperAccess.GATED:
            return BuildabilityAssessment(
                decision=Buildability.OUTREACH_REQUIRED,
                reasons=[
                    "API access is gated and likely requires approval or vendor contact."
                ],
            )

        if access == DeveloperAccess.HYBRID:
            reasons.append("Access includes a combination of self-serve and gated requirements.")
            risks.append("Some API capabilities may require vendor approval.")

            return BuildabilityAssessment(
                decision=Buildability.BUILD_WITH_CONSTRAINTS,
                reasons=reasons,
                risks=risks,
            )

        if api == APIAvailability.PARTIAL:
            reasons.append("Only partial API availability has been established.")
            risks.append("Integration scope may be limited.")

            return BuildabilityAssessment(
                decision=Buildability.BUILD_WITH_CONSTRAINTS,
                reasons=reasons,
                risks=risks,
            )

        if access == DeveloperAccess.SELF_SERVE:
            reasons.append("A public API with self-serve developer access is available.")

            if research.api_breadth.lower() in {"limited", "basic", "narrow"}:
                risks.append("API coverage appears limited.")

                return BuildabilityAssessment(
                    decision=Buildability.BUILD_WITH_CONSTRAINTS,
                    reasons=reasons,
                    risks=risks,
                )

            if research.api_breadth.lower() == "unknown":
                risks.append("API breadth has not been established.")

                return BuildabilityAssessment(
                    decision=Buildability.BUILD_WITH_CONSTRAINTS,
                    reasons=reasons,
                    risks=risks,
                )

            return BuildabilityAssessment(
                decision=Buildability.BUILD,
                reasons=reasons,
                risks=risks,
            )

        # API exists, but the access model isn't sufficiently clear.
        return BuildabilityAssessment(
            decision=Buildability.UNKNOWN,
            reasons=["API availability is established, but access requirements remain unclear."],
            risks=["Developer access model requires verification."],
        )

    # Unknown availability must not be treated as a confirmed blocker.
    if api == APIAvailability.UNKNOWN or mcp == MCPAvailability.UNKNOWN:
        return BuildabilityAssessment(
            decision=Buildability.UNKNOWN,
            reasons=["Available research does not establish a reliable integration path."],
            risks=["Additional research or verification is required."],
        )

    # Partial API without a usable access path.
    if api == APIAvailability.PARTIAL:
        return BuildabilityAssessment(
            decision=Buildability.BUILD_WITH_CONSTRAINTS,
            reasons=["Partial API availability was identified."],
            risks=["API coverage and access requirements require further investigation."],
        )

    return BuildabilityAssessment(
        decision=Buildability.UNKNOWN,
        reasons=["Insufficient information to determine buildability."],
    )