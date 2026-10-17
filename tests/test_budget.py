import copy
import json
import unittest
from pathlib import Path

from tools.fleet_street.budget import calculate_budget


ROOT = Path(__file__).resolve().parents[1]


class BudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.input = json.loads((ROOT / "examples/budget.json").read_text())

    def test_fictional_scenario_exact_totals(self) -> None:
        result = calculate_budget(self.input)
        for key, expected in {"available_tickets": 360, "gross_receipts": "4995.00", "ticket_fees": "249.75", "net_receipts": "4745.25", "base_costs": "4730.00", "contingency": "473.00", "total_costs": "5203.00", "balance": "-457.75", "break_even_paid_tickets": 297, "break_even_occupancy_percent": "82.50"}.items():
            self.assertEqual(result[key], expected, key)

    def test_zero_expected_sales_does_not_change_break_even(self) -> None:
        self.input["occupancy"] = "0"
        result = calculate_budget(self.input)
        self.assertEqual(result["net_receipts"], "0.00")
        self.assertEqual(result["break_even_paid_tickets"], 297)

    def test_unachievable_costs_are_not_a_sales_promise(self) -> None:
        self.input["costs"] = [{"label": "Test", "quantity": 1, "unit_cost": "100000.00"}]
        result = calculate_budget(self.input)
        self.assertFalse(result["break_even_possible"])
        self.assertIsNone(result["break_even_paid_tickets"])
        self.assertIsNone(result["break_even_occupancy_percent"])

    def test_zero_costs_need_zero_tickets(self) -> None:
        self.input["costs"] = []
        result = calculate_budget(self.input)
        self.assertEqual(result["break_even_paid_tickets"], 0)
        self.assertEqual(result["total_costs"], "0.00")

    def test_half_penny_fee_uses_actual_rounded_receipts(self) -> None:
        self.input.update(performances=1, saleable_seats=3, occupancy="1", ticket_price="0.01", fee_rate="0.5", contingency_rate="0", costs=[{"label": "Test", "quantity": 1, "unit_cost": "0.01"}])
        result = calculate_budget(self.input)
        self.assertEqual(result["ticket_fees"], "0.02")
        self.assertEqual(result["break_even_paid_tickets"], 2)

    def test_large_capacity_is_searched_without_a_candidate_cutoff(self) -> None:
        self.input.update(performances=1, saleable_seats=1000000, occupancy="1", ticket_price="0.01", fee_rate="0.999999", contingency_rate="0", costs=[{"label": "Test", "quantity": 1, "unit_cost": "0.01"}])
        self.assertEqual(calculate_budget(self.input)["break_even_paid_tickets"], 500001)

    def test_supplied_input_is_not_mutated(self) -> None:
        original = copy.deepcopy(self.input)
        calculate_budget(self.input)
        self.assertEqual(self.input, original)

    def test_invalid_quantities_rates_and_money_fail(self) -> None:
        for key, value in [("performances", True), ("saleable_seats", 0), ("occupancy", "1.1"), ("fee_rate", "1"), ("ticket_price", "0"), ("ticket_price", "1.001"), ("occupancy", 0.75), ("fee_rate", "NaN"), ("contingency_rate", "-1")]:
            with self.subTest(key=key, value=value):
                changed = {**self.input, key: value}
                with self.assertRaises(ValueError):
                    calculate_budget(changed)

    def test_unknown_fields_and_non_gbp_are_explicit_errors(self) -> None:
        for changed in [{**self.input, "secret": "not accepted"}, {**self.input, "currency": "USD"}, {**self.input, "costs": [{"label": "Incomplete"}]}]:
            with self.assertRaises(ValueError):
                calculate_budget(changed)
