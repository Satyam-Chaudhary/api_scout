import json
from pathlib import Path

RESULTS_PATH = Path("data/results/batch_results.json")


def audit_app(app):
    issues = []

    if app.get("research_status") != "completed":
        issues.append("Research status not completed")

    if app.get("source_count", 0) == 0:
        issues.append("Source count is zero")

    if not app.get("sources"):
        issues.append("No sources available")

    if not app.get("evidence"):
        issues.append("No claim-level evidence")

    if app.get("confidence", 0) <= 0:
        issues.append("Confidence score missing")

    if app.get("official_mcp") == "unknown" and app.get("mcp_url"):
        issues.append("MCP URL exists but MCP status is unknown")

    if app.get("public_api") == "yes":
        if app.get("developer_access") == "unknown":
            issues.append("API access requirements unclear")

    if app.get("human_review_required"):
        issues.append("Requires human review")

    return issues


def main():
    data = json.loads(RESULTS_PATH.read_text())

    print("\n=== API SCOUT QUALITY AUDIT ===\n")

    total_issues = 0

    for app in data:
        issues = audit_app(app)

        print(f"\n{app['app_name']}")

        if not issues:
            print("  PASS")
        else:
            for issue in issues:
                print(f"  [!] {issue}")
                total_issues += 1

    print(f"\nTotal quality issues: {total_issues}")


if __name__ == "__main__":
    main()