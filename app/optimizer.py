"""Linear-programming optimizer for weekly macro planning."""

from __future__ import annotations

from typing import Sequence

import pulp


def optimize_weekly_plan(
    items: Sequence[dict],
    protein_target: float = 900.0,
    calorie_target: float = 14000.0,
    max_budget_gbp: float = 70.0,
    max_servings: int = 100,
) -> dict:
    """
    Optimize a basket of Aldi foods to satisfy macro targets.

    Each serving is treated as a 100g unit.
    """
    if not items:
        raise ValueError("No items available for optimization")

    model = pulp.LpProblem("aldi_macro_optimizer", pulp.LpMinimize)
    servings = {
        item["name"]: pulp.LpVariable(f"servings_{index}", lowBound=0, cat="Integer")
        for index, item in enumerate(items)
    }

    model += pulp.lpSum(servings[item["name"]] * item["price_gbp"] for item in items), "total_cost"
    model += (
        pulp.lpSum(servings[item["name"]] * item["protein_per_100g"] for item in items) >= protein_target,
        "protein_target",
    )
    model += (
        pulp.lpSum(servings[item["name"]] * item["calories_per_100g"] for item in items) >= calorie_target,
        "calorie_target",
    )
    model += (
        pulp.lpSum(servings[item["name"]] * item["price_gbp"] for item in items) <= max_budget_gbp,
        "budget_cap",
    )
    model += (pulp.lpSum(servings[item["name"]] for item in items) <= max_servings, "serving_cap")

    status = model.solve(pulp.PULP_CBC_CMD(msg=False))
    if status != pulp.LpStatusOptimal:
        raise ValueError("Unable to find an optimal plan for the requested constraints")

    plan_items = []
    total_protein = 0.0
    total_calories = 0.0
    total_cost = 0.0

    for item in items:
        quantity = int(round(pulp.value(servings[item["name"]]) or 0))
        if quantity <= 0:
            continue
        protein = quantity * item["protein_per_100g"]
        calories = quantity * item["calories_per_100g"]
        cost = quantity * item["price_gbp"]
        total_protein += protein
        total_calories += calories
        total_cost += cost
        plan_items.append(
            {
                "name": item["name"],
                "servings_100g": quantity,
                "protein_g": round(protein, 2),
                "calories_kcal": round(calories, 2),
                "cost_gbp": round(cost, 2),
            }
        )

    return {
        "items": plan_items,
        "totals": {
            "protein_g": round(total_protein, 2),
            "calories_kcal": round(total_calories, 2),
            "cost_gbp": round(total_cost, 2),
        },
    }
