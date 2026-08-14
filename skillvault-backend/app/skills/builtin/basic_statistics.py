import math
import re
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Statistics Skill:
    Calculates numerical descriptive statistics including mean, median, min, max,
    standard deviation, and 25th, 50th, 75th percentiles.
    """
    numbers = input_data.get("values") or input_data.get("numbers")
    user_prompt = input_data.get("input", "")

    if not numbers and user_prompt:
        found = re.findall(r"[-+]?\d*\.\d+|\d+", user_prompt)
        numbers = [float(x) for x in found]

    if not numbers:
        return {"status": "error", "message": "No numerical data provided for statistical analysis."}

    try:
        nums = sorted([float(n) for n in numbers])
    except (ValueError, TypeError) as e:
        return {"status": "error", "message": f"Invalid numerical values: {str(e)}"}

    n = len(nums)
    if n == 0:
        return {"status": "error", "message": "Numerical array is empty."}

    mean_val = sum(nums) / n

    # Median calculation
    if n % 2 != 0:
        median_val = nums[n // 2]
    else:
        median_val = (nums[n // 2 - 1] + nums[n // 2]) / 2.0

    # Variance and Standard Deviation
    variance = sum((x - mean_val) ** 2 for x in nums) / (n - 1 if n > 1 else 1)
    std_dev = math.sqrt(variance)

    # Percentiles helper
    def percentile(p: float) -> float:
        k = (n - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return nums[int(k)]
        return nums[int(f)] * (c - k) + nums[int(c)] * (k - f)

    p25 = percentile(0.25)
    p50 = median_val
    p75 = percentile(0.75)

    return {
        "status": "success",
        "count": n,
        "mean": round(mean_val, 4),
        "median": round(median_val, 4),
        "min": nums[0],
        "max": nums[-1],
        "std_dev": round(std_dev, 4),
        "variance": round(variance, 4),
        "percentiles": {
            "p25": round(p25, 4),
            "p50": round(p50, 4),
            "p75": round(p75, 4),
        },
    }
