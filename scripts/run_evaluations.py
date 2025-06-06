"""
This script provides an example of how to run evaluations using the Laminar SDK.

You can adapt this to create datasets and test different executors,
which could be your LLM chains or other parts of your application.

Make sure your LMNR_PROJECT_API_KEY is set in your environment.
"""

from lmnr import evaluate


def main():
    """Run a sample evaluation."""
    print("Running a sample evaluation with Laminar...")

    # This is a sample dataset. You can load your own data from files (e.g., CSV, JSON).
    dataset = [
        {
            "data": {"country": "Canada"},
            "target": {"capital": "Ottawa"}
        },
        {
            "data": {"country": "Mexico"},
            "target": {"capital": "Mexico City"}
        },
        {
            "data": {"country": "France"},
            "target": {"capital": "Paris"}
        },
        {
            "data": {"country": "Japan"},
            "target": {"capital": "Tokyo"}
        }
    ]

    # The executor is the function or system you want to test.
    # It takes a dictionary of data and should return an output.
    # Here, we are simulating a simple lookup. This could be a call to your LLM.
    def get_capital_from_data(data: dict) -> str:
        # A real executor would likely call an API or a model.
        # This is a dummy implementation for demonstration.
        capitals = {
            "Canada": "Ottawa",
            "Mexico": "Mexico City",
            "France": "Paris",
            "Japan": "Kyoto",  # Intentionally incorrect for demonstration
        }
        country = data.get("country")
        return capitals.get(country, "Unknown")

    # Evaluators are functions that score the output against the target.
    # They should return a numerical score (e.g., 0 for incorrect, 1 for correct).
    evaluators = {
        "is_correct": lambda output, target: int(output == target.get("capital"))
    }

    # The group_id helps you organize and compare different evaluation runs.
    evaluation_result = evaluate(
        data=dataset,
        executor=get_capital_from_data,
        evaluators=evaluators,
        group_id="capital_city_lookup_v1",
    )

    print("\nEvaluation complete!")
    print(f"Results for group 'capital_city_lookup_v1':")
    print(evaluation_result.to_df())


if __name__ == "__main__":
    main() 