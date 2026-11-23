import json
from collections import Counter, defaultdict
from pathlib import Path

RESULTS_PATH = Path("data/results/batch_results.json")
OUTPUT_PATH = Path("data/results/analytics.json")


def analyze_dataset(apps):
    total = len(apps)

    api_counts = Counter(
        app.get("public_api", "unknown") for app in apps
    )

    mcp_counts = Counter(
        app.get("official_mcp", "unknown") for app in apps
    )

    buildability_counts = Counter(
        app.get("buildability", "unknown") for app in apps
    )

    access_counts = Counter(
        app.get("developer_access", "unknown") for app in apps
    )

    category_data = defaultdict(list)

    for app in apps:
        category_data[app.get("category", "Uncategorized")].append(app)

    categories = {}

    for category, records in category_data.items():
        categories[category] = {
            "total": len(records),
            "api_available": sum(
                1 for r in records
                if r.get("public_api") == "yes"
            ),
            "mcp_available": sum(
                1 for r in records
                if r.get("official_mcp") == "yes"
            ),
            "buildable": sum(
                1 for r in records
                if r.get("buildability") == "build"
            ),
            "constrained": sum(
                1 for r in records
                if r.get("buildability") == "build_with_constraints"
            ),
            "outreach_required": sum(
                1 for r in records
                if r.get("buildability") == "outreach_required"
            ),
            "blocked": sum(
                1 for r in records
                if r.get("buildability") == "blocked"
            ),
            "unknown": sum(
                1 for r in records
                if r.get("buildability") == "unknown"
            ),
            "average_confidence": round(
                sum(r.get("confidence", 0) for r in records)
                / len(records),
                3,
            ),
        }

    review_required = sum(
        1 for app in apps
        if app.get("human_review_required", False)
    )

    return {
        "total_apps": total,
        "api_availability": dict(api_counts),
        "mcp_availability": dict(mcp_counts),
        "buildability": dict(buildability_counts),
        "developer_access": dict(access_counts),
        "human_review_required": review_required,
        "category_analysis": categories,
    }


def main():
    apps = json.loads(RESULTS_PATH.read_text())

    analytics = analyze_dataset(apps)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(analytics, indent=2)
    )

    print("Analytics generated.")
    print(json.dumps(analytics, indent=2))


if __name__ == "__main__":
    main()