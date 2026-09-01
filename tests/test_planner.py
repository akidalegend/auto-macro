import tempfile
import unittest
from pathlib import Path

from app.database import create_connection, fetch_skus, initialize_database, seed_aldi_skus
from app.optimizer import optimize_weekly_plan


class PlannerTests(unittest.TestCase):
    def test_database_seed_and_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            conn = create_connection(db_path)
            initialize_database(conn)
            inserted = seed_aldi_skus(conn)
            self.assertGreater(inserted, 0)
            skus = fetch_skus(conn)
            self.assertGreater(len(skus), 0)

    def test_optimizer_returns_feasible_plan(self) -> None:
        items = [
            {"name": "item-a", "price_gbp": 1.0, "protein_per_100g": 30.0, "calories_per_100g": 300.0},
            {"name": "item-b", "price_gbp": 0.8, "protein_per_100g": 20.0, "calories_per_100g": 200.0},
        ]
        plan = optimize_weekly_plan(
            items,
            protein_target=300.0,
            calorie_target=3000.0,
            max_budget_gbp=20.0,
            max_servings=20,
        )
        self.assertGreaterEqual(plan["totals"]["protein_g"], 300.0)
        self.assertGreaterEqual(plan["totals"]["calories_kcal"], 3000.0)
        self.assertLessEqual(plan["totals"]["cost_gbp"], 20.0)


if __name__ == "__main__":
    unittest.main()
