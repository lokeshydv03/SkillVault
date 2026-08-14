import csv
import os
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Sales Analyzer Skill:
    Parses sales transaction records from CSV files, calculates total revenue (quantity * unit_price),
    aggregates revenue by product, region, salesperson, and category, and computes top performance metrics.
    """
    file_path = input_data.get("file_path", "sample_data/sales.csv")

    if not os.path.exists(file_path):
        # Fallback search if path relative
        if os.path.exists(os.path.join(os.getcwd(), file_path)):
            file_path = os.path.join(os.getcwd(), file_path)

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": f"Sales transaction file '{file_path}' not found.",
        }

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"status": "error", "message": "Sales dataset is empty."}

    total_revenue = 0.0
    total_units = 0
    revenue_by_product: dict[str, float] = {}
    revenue_by_region: dict[str, float] = {}
    revenue_by_salesperson: dict[str, float] = {}
    revenue_by_category: dict[str, float] = {}
    units_by_category: dict[str, int] = {}

    for row in rows:
        try:
            qty = int(row.get("quantity", 0))
            price = float(row.get("unit_price", 0.0))
            rev = qty * price

            product = row.get("product", "Unknown")
            region = row.get("region", "Unknown")
            salesperson = row.get("salesperson", "Unknown")
            category = row.get("category", "Unknown")

            total_revenue += rev
            total_units += qty

            revenue_by_product[product] = revenue_by_product.get(product, 0.0) + rev
            revenue_by_region[region] = revenue_by_region.get(region, 0.0) + rev
            revenue_by_salesperson[salesperson] = (
                revenue_by_salesperson.get(salesperson, 0.0) + rev
            )
            revenue_by_category[category] = revenue_by_category.get(category, 0.0) + rev
            units_by_category[category] = units_by_category.get(category, 0) + qty

        except (ValueError, KeyError):
            continue

    total_orders = len(rows)
    aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    # Sort top performers
    top_products = sorted(revenue_by_product.items(), key=lambda x: x[1], reverse=True)
    top_salespeople = sorted(
        revenue_by_salesperson.items(), key=lambda x: x[1], reverse=True
    )
    top_regions = sorted(revenue_by_region.items(), key=lambda x: x[1], reverse=True)

    return {
        "status": "success",
        "file_path": file_path,
        "total_orders": total_orders,
        "total_units_sold": total_units,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": aov,
        "top_product": top_products[0] if top_products else None,
        "top_salesperson": top_salespeople[0] if top_salespeople else None,
        "top_region": top_regions[0] if top_regions else None,
        "revenue_by_product": {k: round(v, 2) for k, v in top_products},
        "revenue_by_salesperson": {k: round(v, 2) for k, v in top_salespeople},
        "revenue_by_region": {k: round(v, 2) for k, v in top_regions},
        "revenue_by_category": {k: round(v, 2) for k, v in revenue_by_category.items()},
        "units_by_category": units_by_category,
    }
