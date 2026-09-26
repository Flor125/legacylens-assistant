"""Modern batch entry point — equivalent of COBOL BATCHCOSTOS PROCEDURE DIVISION.

Reproduces the complete observable behaviour of the COBOL batch:
  1. Read costos.dat        (legacy_parser.parse_costs_file)
  2. Calculate average cost (cost_calculator.calculate_average_cost)
  3. Write historico.dat    (write_historic_file — byte-exact COBOL format)
  4. Read vencimientos.dat  (expiration_processor.parse_expirations_file)
  5. Write alertas.dat      (expiration_processor.write_alerts_file)
  6. Return (cost_count, alert_count)

historico.dat record format (26 bytes + LF per record)
-------------------------------------------------------
Derived by inspecting legacy/cobol/historico.dat byte-for-byte.

  bytes  0-8  : HR-PRODUCTO-ID    PIC X(9)
                MOVE WS-HR-PRODUCTO-ID (PIC 9(9)) -> 9 ASCII digits, zero-padded

  bytes 9-18  : cost digits (10 bytes)
                WS-HR-COSTO-TEMP PIC 9(8)V99 in DISPLAY = 10 ASCII digits
                (integer value scaled by 100, zero-padded to 10 digits)

  byte  19    : 0x00  (NUL — the 11th byte of HR-COSTO-PROMEDIO PIC X(11) was
                never touched by the STRING statement; GnuCOBOL initialises
                working-storage to binary zeros, so it remains 0x00)

  bytes 20-24 : gain digits (5 bytes)
                WS-HR-GANANCIA-TEMP PIC 9(3)V99 in DISPLAY = 5 ASCII digits
                (integer value scaled by 100, zero-padded to 5 digits)

  byte  25    : 0x00  (NUL — same reason as byte 19, 6th byte of
                HR-PORC-GANANCIA PIC X(6))

  byte  26    : 0x0A  (LF — LINE SEQUENTIAL record terminator)
"""

from decimal import Decimal
from pathlib import Path

from modern.legacy_parser import parse_costs_file
from modern.cost_calculator import calculate_average_cost
from modern.expiration_processor import parse_expirations_file, write_alerts_file

# Field widths match COBOL picture clauses exactly.
_PROD_ID_WIDTH  = 9   # HR-PRODUCTO-ID    PIC X(9)
_COST_WIDTH     = 10  # WS-HR-COSTO-TEMP  PIC 9(8)V99  => 10 DISPLAY digits
_COST_PAD       = 1   # remaining byte in HR-COSTO-PROMEDIO PIC X(11) = NUL
_GAIN_WIDTH     = 5   # WS-HR-GANANCIA-TEMP PIC 9(3)V99 => 5 DISPLAY digits
_GAIN_PAD       = 1   # remaining byte in HR-PORC-GANANCIA PIC X(6) = NUL


def write_historic_file(path, cost_results):
    """Write a historico.dat file reproducing the exact COBOL output bytes.

    Args:
        path:         Path-like or str for the output file.
        cost_results: dict returned by ``calculate_average_cost``:
                      { product_id (str): {"average_cost": Decimal, "gain": Decimal} }
                      Products are written in insertion order (which matches
                      COBOL control-break order because the input is sorted by
                      product_id).

    Returns:
        int: Number of records written (mirrors WS-CONTADOR-COSTOS).
    """
    path = Path(path)
    count = 0

    with path.open("wb") as fh:
        for product_id, data in cost_results.items():
            # HR-PRODUCTO-ID: the COBOL MOVE of PIC 9(9) -> PIC X(9) zero-pads.
            prod_bytes = product_id.encode("ascii")

            # HR-COSTO-PROMEDIO: scale Decimal to integer (2 implied decimal places).
            cost_int  = int(data["average_cost"] * 100)
            cost_str  = f"{cost_int:0{_COST_WIDTH}d}".encode("ascii")

            # HR-PORC-GANANCIA: same scaling.
            gain_int  = int(data["gain"] * 100)
            gain_str  = f"{gain_int:0{_GAIN_WIDTH}d}".encode("ascii")

            # Assemble the record exactly as COBOL produces it.
            record = (
                prod_bytes          # bytes  0-8  : product_id (9 bytes)
                + cost_str          # bytes  9-18 : cost digits (10 bytes)
                + b"\x00"           # byte   19   : NUL (STRING leftover)
                + gain_str          # bytes 20-24 : gain digits (5 bytes)
                + b"\x00"           # byte   25   : NUL (STRING leftover)
                + b"\n"             # byte   26   : LF  (LINE SEQUENTIAL)
            )
            fh.write(record)
            count += 1

    return count


def run_batch(costos_path, vencimientos_path, historico_path, alertas_path):
    """Run the full modern batch, equivalent to COBOL 0000-MAIN-PROCEDURE.

    Args:
        costos_path:       Path to input costos.dat
        vencimientos_path: Path to input vencimientos.dat
        historico_path:    Path to output historico.dat (overwritten)
        alertas_path:      Path to output alertas.dat (overwritten)

    Returns:
        tuple[int, int]: (cost_count, alert_count) —
                         mirrors WS-CONTADOR-COSTOS and WS-CONTADOR-ALERTAS.
    """
    # --- Phase 1: costs (equivalent to COBOL 2000-PROCESAR-COSTOS) ----------
    records      = parse_costs_file(costos_path)
    cost_results = calculate_average_cost(records)
    cost_count   = write_historic_file(historico_path, cost_results)

    # --- Phase 2: alerts (equivalent to COBOL 3000-PROCESAR-ALERTAS) --------
    lote_ids    = parse_expirations_file(vencimientos_path)
    alert_count = write_alerts_file(alertas_path, lote_ids)

    return cost_count, alert_count
