import os
import sys
import pandas as pd

# Fix path to allow importing from 'src' root
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.retriever import Retriever
from src.engine.llm_handler import LLMHandler


def generate_csv():
    """Generate predictions CSV file from test queries."""
    # Load the unlabeled test set
    input_path = os.path.join(os.path.join(os.path.dirname(__file__), "..", "data", "given_datasets", "test.csv"))
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    test_df = pd.read_csv(input_path)

    # Initialize Engine components
    retriever = Retriever()
    llm = LLMHandler()

    submission_rows = []

    print(f"Generating predictions for {len(test_df)} test queries...")

    # Process each query in the test set
    for _, row in test_df.iterrows():
        query_text = row['Query']
        print(f"Processing: {query_text}")

        # Get candidates with high recall for LLM reranking
        candidates = retriever.search(query_text, n_results=50)

        # Use LLM to select the top 10 most relevant assessments
        final_recs = llm.rerank(query_text, candidates)[:10]

        # Format results for output
        for rec in final_recs:
            submission_rows.append({
                "Query": query_text,
                "Assessment_url": rec['url']
            })

    # Save final CSV in the required format
    output_df = pd.DataFrame(submission_rows)
    output_path = "final_submission_predictions.csv"
    output_df.to_csv(output_path, index=False)

    print(f"\nFile created: {output_path}")
    print(f"Total rows: {len(output_df)}")


if __name__ == "__main__":
    generate_csv()
