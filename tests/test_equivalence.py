from modern.cost_calculator import calculate_average_cost


records = [
    {"product_id": "000000001", "quantity": 10, "cost": 150.75},
    {"product_id": "000000001", "quantity": 20, "cost": 200.00},

    {"product_id": "000000002", "quantity": 5, "cost": 100.00},
    {"product_id": "000000002", "quantity": 15, "cost": 120.00},

    {"product_id": "000000003", "quantity": 8, "cost": 80.00},
    {"product_id": "000000003", "quantity": 12, "cost": 95.00},
    {"product_id": "000000003", "quantity": 5, "cost": 110.00},

    {"product_id": "000000004", "quantity": 25, "cost": 50.00},

    {"product_id": "000000005", "quantity": 10, "cost": 300.00},
    {"product_id": "000000005", "quantity": 10, "cost": 350.00},
]


EXPECTED = {
    "000000001": 183.58,
    "000000002": 115.00,
    "000000003": 93.20,
    "000000004": 50.00,
    "000000005": 325.00,
}


result = calculate_average_cost(records)

for product_id, expected in EXPECTED.items():
    actual = result[product_id]

    assert actual == expected, (
        f"{product_id}: expected {expected}, got {actual}"
    )

print("✓ LEGACY/MODERN EQUIVALENCE PASSED")

for product_id in EXPECTED:
    print(
        f"{product_id}: "
        f"COBOL={EXPECTED[product_id]:.2f} "
        f"MODERN={result[product_id]:.2f}"
    )