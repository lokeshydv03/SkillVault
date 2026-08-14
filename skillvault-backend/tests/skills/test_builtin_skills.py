import os
import pytest
from app.skills.builtin import (
    basic_statistics,
    csv_analyzer,
    json_transformer,
    markdown_analyzer,
    sales_analyzer,
    text_analyzer,
)


def test_csv_analyzer_with_employee_dataset():
    input_data = {"file_path": "sample_data/employees.csv"}
    res = csv_analyzer.run(input_data)
    assert res["status"] == "success"
    assert res["total_rows"] == 25
    assert "salary" in res["column_analysis"]
    assert res["column_analysis"]["salary"]["avg"] > 0


def test_sales_analyzer_with_sales_dataset():
    input_data = {"file_path": "sample_data/sales.csv"}
    res = sales_analyzer.run(input_data)
    assert res["status"] == "success"
    assert res["total_orders"] == 25
    assert res["total_revenue"] > 0
    assert "top_salesperson" in res
    assert res["top_salesperson"] is not None


def test_json_transformer_filter():
    input_data = {
        "file_path": "sample_data/products.json",
        "field": "rating",
        "operator": ">",
        "value": 4.5,
    }
    res = json_transformer.run(input_data)
    assert res["status"] == "success"
    assert res["matching_records"] > 0
    for item in res["result"]:
        assert item["rating"] > 4.5


def test_text_analyzer_article():
    input_data = {"file_path": "sample_data/article.md"}
    res = text_analyzer.run(input_data)
    assert res["status"] == "success"
    assert res["word_count"] > 300
    assert "top_keywords" in res


def test_markdown_analyzer_article():
    input_data = {"file_path": "sample_data/article.md"}
    res = markdown_analyzer.run(input_data)
    assert res["status"] == "success"
    assert res["title"] is not None
    assert res["heading_counts"]["h2"] > 0
    assert len(res["headings"]) > 0


def test_statistics_values():
    input_data = {"values": [100, 200, 300, 400, 500]}
    res = basic_statistics.run(input_data)
    assert res["status"] == "success"
    assert res["count"] == 5
    assert res["mean"] == 300.0
    assert res["median"] == 300.0
    assert res["min"] == 100
    assert res["max"] == 500
    assert "percentiles" in res
