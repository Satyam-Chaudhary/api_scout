import asyncio
import json
import argparse
import io

from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

from agents.research_agent import analyze_app


APPS_FILE = Path("data/apps.json")
RESULTS_FILE = Path("data/results/batch_results.json")
FAILED_FILE = Path("data/results/failed_apps.json")


def load_apps():
    with APPS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_results():
    if not RESULTS_FILE.exists():
        return {}

    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        item["app_name"]: item
        for item in data
        if item.get("app_name")
    }


def load_failures():
    if not FAILED_FILE.exists():
        return {}

    with FAILED_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        item["app_name"]: item
        for item in data
        if item.get("app_name")
    }


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    temp_path.replace(path)


def is_rate_limited(exc):
    message = str(exc).lower()

    return (
        "429" in message
        or "too many requests" in message
        or "rate limit" in message
    )


async def research_with_retry(app_name, category, retries=3):
    for attempt in range(retries):
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                result = await analyze_app(app_name, category)

            return result

        except Exception as exc:
            if is_rate_limited(exc):
                raise

            if attempt == retries - 1:
                raise

            delay = 2 ** attempt

            print(
                f"Retry {attempt + 1}/{retries - 1} "
                f"for {app_name} in {delay}s: {exc}"
            )

            await asyncio.sleep(delay)


async def run_batch():
    apps = load_apps()

    results = load_results()
    failures = load_failures()

    completed = {
        name: result
        for name, result in results.items()
        if result.get("research_status") == "completed"
    }

    print(f"Total apps: {len(apps)}")
    print(f"Already completed: {len(completed)}")

    for index, app in enumerate(apps, start=1):

        if isinstance(app, str):
            app_name = app
            category = "Uncategorized"
        else:
            app_name = app["app_name"]
            category = app.get("category", "Uncategorized")

        if app_name in completed:
            print(f"[{index}/{len(apps)}] Skipping {app_name}")
            continue

        print(f"\n[{index}/{len(apps)}] Researching {app_name}")

        try:
            result = await research_with_retry(app_name, category)

            if result is None:
                raise ValueError(
                    f"Research returned no result for {app_name}"
                )

            result_data = result.model_dump(mode="json")

            results[app_name] = result_data
            completed[app_name] = result_data

            failures.pop(app_name, None)

            # Save all results, including previous non-completed records.
            save_json(RESULTS_FILE, list(results.values()))
            save_json(FAILED_FILE, list(failures.values()))

            print(f"Completed: {app_name}")

        except Exception as exc:

            error = {
                "app_name": app_name,
                "category": category,
                "error": str(exc),
            }

            failures[app_name] = error

            save_json(FAILED_FILE, list(failures.values()))

            if is_rate_limited(exc):
                print("\n" + "=" * 50)
                print("OPENROUTER RATE LIMIT DETECTED")
                print(f"Stopped at: {app_name}")
                print("Progress has been saved.")
                print("Restart later to resume.")
                print("=" * 50)

                break

            print(f"FAILED: {app_name} — {exc}")

    print("\n========== BATCH SUMMARY ==========")
    print(f"Total apps: {len(apps)}")
    print(f"Completed: {len(completed)}")
    print(f"Failures recorded: {len(failures)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if args.limit:
        original_load_apps = load_apps

        def load_apps():
            return original_load_apps()[:args.limit]

    asyncio.run(run_batch())