from pathlib import Path


PRODUCT_ID_LENGTH = 9
AVERAGE_COST_LENGTH = 11
GAIN_LENGTH = 6
RECORD_LENGTH = (
    PRODUCT_ID_LENGTH
    + AVERAGE_COST_LENGTH
    + GAIN_LENGTH
)


def parse_historic_file(path):
    path = Path(path)
    records = []

    data = path.read_bytes()

    for record_number, record in enumerate(
        data.splitlines(), start=1
    ):
        if len(record) != RECORD_LENGTH:
            raise ValueError(
                f"Invalid record {record_number}: "
                f"expected {RECORD_LENGTH} bytes, "
                f"got {len(record)}"
            )

        product_id = record[:PRODUCT_ID_LENGTH].decode("ascii")

        average_cost_raw = record[
            PRODUCT_ID_LENGTH:
            PRODUCT_ID_LENGTH + AVERAGE_COST_LENGTH
        ].replace(b"\x00", b"").decode("ascii")

        gain_raw = record[
            PRODUCT_ID_LENGTH + AVERAGE_COST_LENGTH:
        ].replace(b"\x00", b"").decode("ascii")

        average_cost = int(average_cost_raw) / 100
        gain = int(gain_raw) / 100

        records.append({
            "product_id": product_id,
            "average_cost": average_cost,
            "gain": gain,
        })

    return records