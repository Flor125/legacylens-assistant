"""Expiration-alert processor — modern equivalent of COBOL paragraph 3000-PROCESAR-ALERTAS.

VR-LOTE-ID is exactly 9 characters (PIC X(9)).
Records are preserved in input order.
The lot ID is not transformed.
Each alert record is written as 9 ASCII characters followed by a newline (LF),
mirroring the COBOL LINE SEQUENTIAL output.
The output file is opened for overwrite (equivalent to COBOL OPEN OUTPUT).
"""

from pathlib import Path


_LOTE_ID_LENGTH = 9  # VR-LOTE-ID PIC X(9)


def parse_expirations_file(path):
    """Read a vencimientos.dat file and return a list of lot-ID strings.

    Each record is exactly ``_LOTE_ID_LENGTH`` (9) characters.
    Order is preserved.  Blank/empty lines are skipped (EOF guard).

    Args:
        path: Path-like or str pointing to the input file.

    Returns:
        list[str]: Lot IDs exactly as they appear in the file (9 chars each).

    Raises:
        ValueError: If a non-empty record is not exactly 9 characters.
    """
    path = Path(path)
    lote_ids = []

    with path.open("r", encoding="ascii") as fh:
        for line_number, line in enumerate(fh, start=1):
            line = line.rstrip("\n\r")

            if not line:
                continue

            if len(line) != _LOTE_ID_LENGTH:
                raise ValueError(
                    f"Invalid record at line {line_number}: "
                    f"expected {_LOTE_ID_LENGTH} characters, got {len(line)}"
                )

            lote_ids.append(line)

    return lote_ids


def write_alerts_file(path, lote_ids):
    """Write an alertas.dat file from a list of lot IDs.

    Reproduces the COBOL OPEN OUTPUT / WRITE ALERTAS-OUT-RECORD behaviour:
    - Opens the file for overwrite (truncates any existing content).
    - Writes one 9-character record per line (LF newline, LINE SEQUENTIAL).
    - Does not transform the lot ID.

    Args:
        path:     Path-like or str for the output file.
        lote_ids: Iterable of 9-character lot-ID strings.

    Returns:
        int: Number of records written (mirrors WS-CONTADOR-ALERTAS).

    Raises:
        ValueError: If any lot ID is not exactly 9 characters.
    """
    path = Path(path)
    count = 0

    with path.open("w", encoding="ascii", newline="\n") as fh:
        for lote_id in lote_ids:
            if len(lote_id) != _LOTE_ID_LENGTH:
                raise ValueError(
                    f"Lot ID must be exactly {_LOTE_ID_LENGTH} characters, "
                    f"got {len(lote_id)!r}"
                )
            fh.write(lote_id + "\n")
            count += 1

    return count
