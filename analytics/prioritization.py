import json
from pathlib import Path

INPUT_PATH = Path("data/results/batch_results.json")
OUTPUT_PATH = Path("data/results/priorities.json")


BUILDABILITY_SCORE = {
    "build": 30,
    "build_with_constraints": 20,
    "outreach_required": 8,
    "blocked": 0,
    "unknown": 5,
}

API_SCORE = {
    "yes": 25,
    "partial": 15,
    "no": 0,
    "unknown": 5,
}

MCP_SCORE = {
    "yes": 15,
    "no": 5,
    "unknown": 5,
}

BREADTH_SCORE = {
    "comprehensive": 20,
    "broad": 20,
    "moderate": 12,
    "limited": 5,
    "basic": 5,
    "unknown": 5,
}


def score_app(app):
    score_components = {
        "buildability": BUILDABILITY_SCORE.get(
            app.get("buildability", "unknown"), 5
        ),
        "api": API_SCORE.get(
            app.get("public_api", "unknown"), 5
        ),
        "mcp": MCP_SCORE.get(
            app.get("official_mcp", "unknown"), 5
        ),
        "breadth": BREADTH_SCORE.get(
            app.get("api_breadth", "unknown").lower(), 5
        ),
        "confidence": round(
            max(0, min(1, app.get("confidence", 0))) * 10
        ),
    }

    total = sum(score_components.values())

    return {
        "app_name": app.get("app_name", "Unknown"),
        "category": app.get("category", "Uncategorized"),
        "priority_score": total,
        "score_components": score_components,
        "buildability": app.get("buildability", "unknown"),
        "public_api": app.get("public_api", "unknown"),
        "official_mcp": app.get("official_mcp", "unknown"),
        "api_breadth": app.get("api_breadth", "unknown"),
        "confidence": app.get("confidence", 0),
        "human_review_required": app.get(
            "human_review_required", False
        ),
    }


def main():
    apps = json.loads(INPUT_PATH.read_text())

    ranked = sorted(
        [score_app(app) for app in apps],
        key=lambda x: x["priority_score"],
        reverse=True,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(ranked, indent=2)
    )

    print("\n=== INTEGRATION PRIORITIES ===\n")

    for i, app in enumerate(ranked, 1):
        print(
            f"{i:>3}. {app['app_name']:<25} "
            f"{app['priority_score']:>3}/100  "
            f"{app['buildability']}"
        )

    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()