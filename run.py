import subprocess
import sys


STAGES = [
    ("Dataset validation", "pipeline.dataset_validator"),
    ("Research batch", "pipeline.batch_runner"),
    ("Analytics", "analytics.dashboard_data"),
    ("Prioritization", "analytics.prioritization"),
    ("Report generation", "report.generate_report"),
]


def run_stage(name, module):
    print(f"\n{'=' * 50}")
    print(f"Running: {name}")
    print("=" * 50)

    result = subprocess.run(
        [sys.executable, "-m", module],
        check=False,
    )

    if result.returncode != 0:
        print(f"\nPipeline stopped: {name} failed.")
        sys.exit(result.returncode)


def main():
    for name, module in STAGES:
        run_stage(name, module)

    print("\n" + "=" * 50)
    print("API SCOUT PIPELINE COMPLETED")
    print("Report: output/integration_atlas.html")
    print("=" * 50)


if __name__ == "__main__":
    main()
    