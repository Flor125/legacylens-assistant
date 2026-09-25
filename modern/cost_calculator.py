from collections import defaultdict


def calculate_average_cost(records):
    products = defaultdict(lambda: {
        "total_value": 0.0,
        "total_quantity": 0
    })

    for record in records:
        product_id = record["product_id"]
        quantity = record["quantity"]
        cost = record["cost"]

        products[product_id]["total_value"] += quantity * cost
        products[product_id]["total_quantity"] += quantity

    result = {}

    for product_id, data in products.items():
        result[product_id] = round(
            data["total_value"] / data["total_quantity"],
            2
        )

    return result