import csv
import io
import os
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    CSV Analyzer Skill:
    Parses CSV files or raw CSV string text, performs profiling, column analysis,
    row counts, missing value analysis, and numeric/categorical summaries.
    """
    file_path = input_data.get("file_path")
    csv_text = input_data.get("csv_text")
    user_prompt = input_data.get("input", "")

    # Resolve file path if prompt references employees.csv or similar
    if not file_path and not csv_text and user_prompt:
        if "employee" in user_prompt.lower():
            file_path = "sample_data/employees.csv"
        elif "sales" in user_prompt.lower():
            file_path = "sample_data/sales.csv"

    if file_path and os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as f:
            csv_text = f.read()

    if not csv_text:
        # Generate default fallback profiling if path not found
        return {
            "status": "error",
            "message": f"CSV source file '{file_path}' not found and no raw csv_text provided.",
        }

    lines = [l for l in csv_text.strip().splitlines() if l.strip()]
    if not lines:
        return {"status": "error", "message": "CSV data is empty."}

    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        return {"status": "error", "message": "No rows found in CSV."}

    headers = [h.strip() for h in rows[0]]
    data_rows = rows[1:]

    total_rows = len(data_rows)
    column_analysis: dict[str, Any] = {}
    missing_values: dict[str, int] = {}

    for i, col in enumerate(headers):
        values = []
        missing_count = 0
        for row in data_rows:
            if i < len(row) and row[i].strip():
                values.append(row[i].strip())
            else:
                missing_count += 1

        missing_values[col] = missing_count

        # Check if numeric
        numeric_vals = []
        for v in values:
            try:
                numeric_vals.append(float(v))
            except ValueError:
                pass

        if numeric_vals and len(numeric_vals) == len(values):
            # Numeric column summary
            numeric_vals.sort()
            avg_val = sum(numeric_vals) / len(numeric_vals)
            column_analysis[col] = {
                "type": "numeric",
                "count": len(numeric_vals),
                "min": min(numeric_vals),
                "max": max(numeric_vals),
                "avg": round(avg_val, 2),
            }
        else:
            # Categorical column summary
            counts: dict[str, int] = {}
            for v in values:
                counts[v] = counts.get(v, 0) + 1
            top_unique = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            column_analysis[col] = {
                "type": "categorical",
                "unique_count": len(counts),
                "top_categories": dict(top_unique),
            }

    return {
        "status": "success",
        "file_path": file_path or "inline_text",
        "total_rows": total_rows,
        "total_columns": len(headers),
        "columns": headers,
        "column_analysis": column_analysis,
        "missing_values": missing_values,
    }
