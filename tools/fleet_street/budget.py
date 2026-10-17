from decimal import Decimal, ROUND_HALF_UP, localcontext

from .validation import decimal_string, positive_integer, record, sequence, text


def currency(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def amount(value: Decimal) -> str:
    return format(currency(value), ".2f")


def calculate_budget(value: object) -> dict[str, object]:
    data = record(value, {"currency", "performances", "saleable_seats", "occupancy", "ticket_price", "fee_rate", "contingency_rate", "costs"}, "Budget")
    if data["currency"] != "GBP":
        raise ValueError("This example calculator requires GBP; no currency conversion is performed")
    performances = positive_integer(data["performances"], "performances")
    seats = positive_integer(data["saleable_seats"], "saleable_seats")
    occupancy = decimal_string(data["occupancy"], "occupancy")
    price = decimal_string(data["ticket_price"], "ticket_price", money=True)
    fee = decimal_string(data["fee_rate"], "fee_rate")
    contingency = decimal_string(data["contingency_rate"], "contingency_rate")
    if occupancy > 1 or fee >= 1 or price <= 0:
        raise ValueError("occupancy must be at most one, fee_rate below one and ticket_price positive")
    costs: list[tuple[str, int, Decimal]] = []
    for item in sequence(data["costs"], "costs"):
        line = record(item, {"label", "quantity", "unit_cost"}, "Cost line")
        costs.append((text(line["label"], "cost label"), positive_integer(line["quantity"], "cost quantity"), decimal_string(line["unit_cost"], "unit_cost", money=True)))
    with localcontext() as context:
        context.prec = max(28, len(str(data)) + 16)
        capacity = performances * seats
        expected = Decimal(capacity) * occupancy
        gross = currency(expected * price)
        fees = currency(gross * fee)
        net = gross - fees
        lines = [{"label": label, "quantity": quantity, "unit_cost": amount(unit), "total": amount(unit * quantity)} for label, quantity, unit in costs]
        base = sum((currency(unit * quantity) for _, quantity, unit in costs), Decimal(0))
        reserve = currency(base * contingency)
        total = base + reserve

        def receipts(tickets: int) -> Decimal:
            paid = price * tickets
            return paid - currency(paid * fee)

        possible = receipts(capacity) >= total
        break_even: int | None = None
        occupancy_percent: str | None = None
        if possible:
            lower, upper = 0, capacity
            while lower < upper:
                middle = (lower + upper) // 2
                if receipts(middle) >= total:
                    upper = middle
                else:
                    lower = middle + 1
            break_even = lower
            occupancy_percent = amount(Decimal(lower) / capacity * 100)
        return {
            "currency": "GBP", "performances": performances, "saleable_seats": seats,
            "available_tickets": capacity, "expected_paid_tickets": format(expected, "f"),
            "occupancy": str(occupancy), "ticket_price": amount(price), "fee_rate": str(fee),
            "contingency_rate": str(contingency), "gross_receipts": amount(gross),
            "ticket_fees": amount(fees), "net_receipts": amount(net), "costs": lines,
            "base_costs": amount(base), "contingency": amount(reserve), "total_costs": amount(total),
            "balance": amount(net - total), "break_even_possible": possible,
            "break_even_paid_tickets": break_even, "break_even_occupancy_percent": occupancy_percent,
            "exclusions": ["Tax/VAT", "Payroll and cash-flow timing", "Grants and non-ticket income", "Variable royalties and mixed ticket prices"],
        }
