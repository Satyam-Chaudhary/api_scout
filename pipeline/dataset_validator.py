import json
from pathlib import Path

DATA_PATH = Path("data/apps.json")


def validate_dataset(apps):
    issues = []
    seen_names = set()
    seen_ids = set()

    for index, app in enumerate(apps):
        label = f"Record {index + 1}"

        app_name = app.get("app_name", "").strip()
        app_id = app.get("id")

        if not app_name:
            issues.append(f"{label}: Missing app_name")
            continue

        normalized_name = app_name.lower()

        if normalized_name in seen_names:
            issues.append(f"{label}: Duplicate app name: {app_name}")

        seen_names.add(normalized_name)

        if app_id is None:
            issues.append(f"{app_name}: Missing ID")
        elif app_id in seen_ids:
            issues.append(f"{app_name}: Duplicate ID: {app_id}")

        if app_id is not None:
            seen_ids.add(app_id)

        if not app.get("category"):
            issues.append(f"{app_name}: Missing category")

    return issues


def main():
    apps = json.loads(DATA_PATH.read_text())

    issues = validate_dataset(apps)

    print(f"Dataset records: {len(apps)}")

    if issues:
        print("\nDataset validation FAILED:\n")

        for issue in issues:
            print(f"[!] {issue}")

        raise SystemExit(1)

    print("Dataset validation PASSED.")
    print("No duplicate names, duplicate IDs or missing fields found.")


if __name__ == "__main__":
    main()