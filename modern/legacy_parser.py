from pathlib import Path


RECORD_LENGTH = 35


def parse_costs_file(path):
    path = Path(path)
    records = []

    with path.open("r", encoding="ascii") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.rstrip("\n\r")

            if not line:
                continue

            if len(line) != RECORD_LENGTH:
                raise ValueError(
                    f"Invalid record at line {line_number}: "
                    f"expected {RECORD_LENGTH} characters, got {len(line)}"
                )

            records.append({
                "product_id": line[0:9],
                "gain": float(line[9:15].replace(",", ".")),
                "quantity": int(line[15:24]),
                "cost": float(line[24:35].replace(",", ".")),
            })

    return records