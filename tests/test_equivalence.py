from modern.legacy_parser import parse_costs_file
from modern.historic_parser import parse_historic_file
from modern.cost_calculator import calculate_average_cost


INPUT_FILE = "legacy/cobol/costos.dat"
HISTORIC_FILE = "legacy/cobol/historico.dat"


records = parse_costs_file(INPUT_FILE)
modern_result = calculate_average_cost(records)

legacy_records = parse_historic_file(HISTORIC_FILE)

legacy_result = {
    record["product_id"]: record["average_cost"]
    for record in legacy_records
}


assert len(records) == 10
assert len(legacy_result) == 5

assert modern_result == legacy_result

print("✓ LEGACY ↔ MODERN EQUIVALENCE PASSED")
print(f"Input records: {len(records)}")
print(f"Products compared: {len(legacy_result)}")

for product_id in sorted(legacy_result):
    print(
        f"{product_id}: "
        f"COBOL={legacy_result[product_id]:.2f} "
        f"MODERN={modern_result[product_id]:.2f}"
    )