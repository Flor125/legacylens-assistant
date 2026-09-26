from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN

_TWO_PLACES = Decimal("0.01")


def calculate_average_cost(records):
    """Calculate weighted average cost per product.

    Returns a dict mapping product_id to:
        {
            "average_cost": Decimal,  # Σ(cost × qty) / Σ(qty), rounded to 2 d.p.
            "gain":         Decimal,  # PORC-GANANCIA from the first lot of each product
        }

    Products whose total quantity is <= 0 are omitted from the result,
    matching the COBOL guard: IF WS-TOTAL-CANTIDAD > 0.
    """
    products = {}

    for record in records:
        product_id = record["product_id"]
        quantity = record["quantity"]
        cost = record["cost"]
        gain = record["gain"]

        if product_id not in products:
            products[product_id] = {
                "total_value": Decimal(0),
                "total_quantity": 0,
                "first_gain": gain,
            }

        products[product_id]["total_value"] += Decimal(quantity) * cost
        products[product_id]["total_quantity"] += quantity

    result = {}

    for product_id, data in products.items():
        if data["total_quantity"] <= 0:
            continue

        average_cost = (
            data["total_value"] / Decimal(data["total_quantity"])
        ).quantize(_TWO_PLACES, rounding=ROUND_HALF_EVEN)

        result[product_id] = {
            "average_cost": average_cost,
            "gain": data["first_gain"],
        }

    return result