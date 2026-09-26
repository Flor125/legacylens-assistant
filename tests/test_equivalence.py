from modern.legacy_parser import parse_costs_file
from modern.historic_parser import parse_historic_file
from modern.cost_calculator import calculate_average_cost


INPUT_FILE = "legacy/cobol/costos.dat"
HISTORIC_FILE = "legacy/cobol/historico.dat"


records = parse_costs_file(INPUT_FILE)
modern_result = calculate_average_cost(records)

legacy_records = parse_historic_file(HISTORIC_FILE)

# Index the COBOL output by product_id for direct comparison.
legacy_result = {
    record["product_id"]: {
        "average_cost": record["average_cost"],
        "gain": record["gain"],
    }
    for record in legacy_records
}


assert len(records) == 10, f"Expected 10 input records, got {len(records)}"
assert len(legacy_result) == 5, f"Expected 5 COBOL output records, got {len(legacy_result)}"
assert len(modern_result) == len(legacy_result), (
    f"Product count mismatch: COBOL={len(legacy_result)}, modern={len(modern_result)}"
)

for product_id in sorted(legacy_result):
    cobol_cost = legacy_result[product_id]["average_cost"]
    cobol_gain = legacy_result[product_id]["gain"]
    modern_cost = float(modern_result[product_id]["average_cost"])
    modern_gain = float(modern_result[product_id]["gain"])

    assert modern_cost == cobol_cost, (
        f"{product_id}: average_cost mismatch "
        f"COBOL={cobol_cost} MODERN={modern_cost}"
    )
    assert modern_gain == cobol_gain, (
        f"{product_id}: gain mismatch "
        f"COBOL={cobol_gain} MODERN={modern_gain}"
    )

print("✓ LEGACY ↔ MODERN EQUIVALENCE PASSED")
print(f"Input records: {len(records)}")
print(f"Products compared: {len(legacy_result)}")

for product_id in sorted(legacy_result):
    print(
        f"{product_id}: "
        f"COBOL cost={legacy_result[product_id]['average_cost']:.2f} "
        f"MODERN cost={float(modern_result[product_id]['average_cost']):.2f} | "
        f"COBOL gain={legacy_result[product_id]['gain']:.2f} "
        f"MODERN gain={float(modern_result[product_id]['gain']):.2f}"
    )