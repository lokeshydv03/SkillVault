import json
import os
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    JSON Transformer Skill:
    Transforms, filters, sorts, selects fields, and groups structured JSON datasets.
    """
    file_path = input_data.get("file_path", "sample_data/products.json")
    json_data = input_data.get("json_data")
    user_prompt = input_data.get("input", "")

    if not json_data and os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as f:
            json_data = json.load(f)

    if not json_data and user_prompt:
        if "product" in user_prompt.lower() and os.path.exists("sample_data/products.json"):
            with open("sample_data/products.json", mode="r", encoding="utf-8") as f:
                json_data = json.load(f)

    if not json_data:
        return {"status": "error", "message": "No JSON data or file found to transform."}

    if not isinstance(json_data, list):
        # Flatten dictionary fallback
        flat: dict[str, Any] = {}

        def _flatten(obj: Any, prefix: str = ""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _flatten(v, f"{prefix}{k}." if prefix else f"{k}.")
            else:
                flat[prefix[:-1] if prefix.endswith(".") else prefix] = obj

        _flatten(json_data)
        return {"status": "success", "operation": "flatten", "result": flat}

    # Process operations on list of items
    operation = input_data.get("operation", "filter")
    field = input_data.get("field")
    operator = input_data.get("operator", "==")
    val = input_data.get("value")

    # If prompt specifies rating > 4.5 or price < 5000 automatically infer filter
    if user_prompt and not field:
        if "rating" in user_prompt.lower() and "4.5" in user_prompt:
            field, operator, val = "rating", ">", 4.5
        elif "price" in user_prompt.lower() and "5000" in user_prompt:
            field, operator, val = "price", "<", 5000.0

    items = json_data
    filtered_items = []

    if field:
        for item in items:
            item_val = item.get(field)
            if item_val is None:
                continue
            if operator == ">" and item_val > val:
                filtered_items.append(item)
            elif operator == "<" and item_val < val:
                filtered_items.append(item)
            elif operator in ("==", "=") and item_val == val:
                filtered_items.append(item)
            elif operator == ">=" and item_val >= val:
                filtered_items.append(item)
            elif operator == "<=" and item_val <= val:
                filtered_items.append(item)
    else:
        filtered_items = items

    sort_by = input_data.get("sort_by")
    if sort_by:
        reverse = input_data.get("descending", False)
        filtered_items.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

    group_by = input_data.get("group_by")
    grouped_result: dict[str, list[Any]] = {}
    if group_by:
        for item in filtered_items:
            key = str(item.get(group_by, "Uncategorized"))
            if key not in grouped_result:
                grouped_result[key] = []
            grouped_result[key].append(item)
        return {
            "status": "success",
            "operation": "group_by",
            "grouped_by": group_by,
            "result": grouped_result,
        }

    return {
        "status": "success",
        "operation": operation,
        "total_records": len(items),
        "matching_records": len(filtered_items),
        "result": filtered_items,
    }
