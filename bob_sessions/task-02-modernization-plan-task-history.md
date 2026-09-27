# Implement the modernization plan you just proposed.

Scope is strictly limited to completing the modern equivalent of the
COBOL batch flow.

Create:

1. `modern/expiration_processor.py`
2. `modern/batch_runner.py`
3. `tests/test_alert_equivalence.py`

Requirements:

### expiration_processor.py

Implement:

- `parse_expirations_file(path)`
- `write_alerts_file(path, lote_ids)`

Preserve the COBOL behavior:

- `VR-LOTE-ID` is exactly 9 characters.
- Preserve record order.
- Do not transform the lot ID.
- Write one 9-character record per line.
- Return the number of records written.
- Use output overwrite semantics, equivalent to COBOL `OPEN OUTPUT`.

### batch_runner.py

Implement a modern batch entry point that:

1. Reads `costos.dat`.
2. Uses the existing `modern/cost_calculator.py`.
3. Writes the modern `historico.dat`.
4. Reads `vencimientos.dat`.
5. Writes `alertas.dat`.
6. Returns the cost and alert counters.

Preserve the observable behavior of the COBOL batch.

The modern `historico.dat` writer must reproduce the actual legacy
output format. Inspect the real `legacy/cobol/historico.dat` bytes before
implementing the writer. Do not guess the format.

### Tests

Create `tests/test_alert_equivalence.py`.

At minimum test:

1. Expiration parsing.
2. Alert output byte-for-byte equivalence with the COBOL output.
3. Alert count = 3.
4. Full modern batch execution.
5. Modern `historico.dat` vs the actual COBOL `historico.dat`.
6. Modern `alertas.dat` vs the actual COBOL `alertas.dat`.
7. Expected batch counts:
   - costs = 5
   - alerts = 3

### Constraints

- Do not modify any COBOL files.
- Do not modify `legacy/cobol/batchcosto_before_fix.cob`.
- Do not modify the existing verified COBOL ↔ Python baseline unless
  absolutely necessary.
- Reuse existing modules instead of duplicating their logic.
- Do not create unrelated files.
- Do not change the project's directory structure.

After implementation, run the complete relevant test suite.

Report:
- files created,
- files modified,
- implementation decisions,
- test results,
- any remaining compatibility risks.

Do not make unrelated changes.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Implement the modernization plan you just proposed.

Scope is strictly limited to completing the modern equivalent of the
COBOL batch flow.

Create:

1. `modern/expiration_processor.py`
2. `modern/batch_runner.py`
3. `tests/test_alert_equivalence.py`

Requirements:

### expiration_processor.py

Implement:

- `parse_expirations_file(path)`
- `write_alerts_file(path, lote_ids)`

Preserve the COBOL behavior:

- `VR-LOTE-ID` is exactly 9 characters.
- Preserve record order.
- Do not transform the lot ID.
- Write one 9-character record per line.
- Return the number of records written.
- Use output overwrite semantics, equivalent to COBOL `OPEN OUTPUT`.

### batch_runner.py

Implement a modern batch entry point that:

1. Reads `costos.dat`.
2. Uses the existing `modern/cost_calculator.py`.
3. Writes the modern `historico.dat`.
4. Reads `vencimientos.dat`.
5. Writes `alertas.dat`.
6. Returns the cost and alert counters.

Preserve the observable behavior of the COBOL batch.

The modern `historico.dat` writer must reproduce the actual legacy
output format. Inspect the real `legacy/cobol/historico.dat` bytes before
implementing the writer. Do not guess the format.

### Tests

Create `tests/test_alert_equivalence.py`.

At minimum test:

1. Expiration parsing.
2. Alert output byte-for-byte equivalence with the COBOL output.
3. Alert count = 3.
4. Full modern batch execution.
5. Modern `historico.dat` vs the actual COBOL `historico.dat`.
6. Modern `alertas.dat` vs the actual COBOL `alertas.dat`.
7. Expected batch counts:
   - costs = 5
   - alerts = 3

### Constraints

- Do not modify any COBOL files.
- Do not modify `legacy/cobol/batchcosto_before_fix.cob`.
- Do not modify the existing verified COBOL ↔ Python baseline unless
  absolutely necessary.
- Reuse existing modules instead of duplicating their logic.
- Do not create unrelated files.
- Do not change the project's directory structure.

After implementation, run the complete relevant test suite.

Report:
- files created,
- files modified,
- implementation decisions,
- test results,
- any remaining compatibility risks.

Do not make unrelated changes.

---

### 🤖 Assistant

> 🔧 called: list_files

Let me start by thoroughly investigating the existing codebase before writing a single line of code.

> 🔧 **list_files** — .

### 🤖 Assistant

> 🔧 called: list_files, list_files, list_files



> 🔧 **list_files** — modern

> 🔧 **list_files** — tests

> 🔧 **list_files** — legacy

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file, read_file, read_file



> 🔧 **read_file** — modern/cost_calculator.py

> 🔧 **read_file** — tests/test_equivalence.py

> 🔧 **read_file** — modern/historic_parser.py

> 🔧 **read_file** — modern/legacy_parser.py

> 🔧 **read_file** — legacy/cobol/batchcosto.cob

### 🤖 Assistant

> 🔧 called: execute_command, execute_command, execute_command, execute_command

Now let me inspect the actual legacy data files byte-by-byte:

> 🔧 **execute_command** — xxd legacy/cobol/costos.dat

> 🔧 **execute_command** — xxd legacy/cobol/vencimientos.dat

> 🔧 **execute_command** — xxd legacy/cobol/historico.dat

> 🔧 **execute_command** — xxd legacy/cobol/alertas.dat

### 🤖 Assistant

> 🔧 called: execute_command

This is very revealing. The `historico.dat` has NUL bytes (`\x00`) in the fields. Let me analyze the exact format:

> 🔧 **execute_command** — python3 -c "
data = open('legacy/cobol/historico.dat', 'rb').read()
print('Total bytes:', len(data))
print('Hex dump:')
for i, b in enumerate(data):
    print(f'{i:3d}: 0x{b:02x}  {chr(b) if 32 <= b < 127 else \".\"}')
print()
# Split by newlines
lines = data.split(b'\n')
print('Lines:', len(lines))
for i, line in enumerate(lines):
    print(f'Line {i} ({len(line)} bytes): {line.hex()} | {repr(line)}')
"


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python3 -c "
# Analyze the historico.dat record format in detail
# Each line is 26 bytes:
# bytes 0-8:  HR-PRODUCTO-ID    PIC X(9)
# bytes 9-19: HR-COSTO-PROMEDIO PIC X(11)
# bytes 20-25: HR-PORC-GANANCIA PIC X(6)

data = open('legacy/cobol/historico.dat', 'rb').read()
lines = [l for l in data.split(b'\n') if l]

for line in lines:
    prod_id = line[0:9]
    cost_avg = line[9:20]
    gain     = line[20:26]
    print(f'product_id={repr(prod_id)} cost_avg={repr(cost_avg)} gain={repr(gain)}')
    
print()
print('Field analysis:')
print('The COBOL does STRING WS-HR-COSTO-TEMP DELIMITED BY SIZE INTO HR-COSTO-PROMEDIO')
print('WS-HR-COSTO-TEMP is PIC 9(8)V99, so integer representation with no decimal point')
print()
# Let us decode each value
for line in lines:
    prod_id = line[0:9].decode('ascii')
    # cost field: 11 bytes, contains NUL padding
    cost_bytes = line[9:20]
    gain_bytes = line[20:26]
    print(f'prod={prod_id}')
    print(f'  cost_bytes hex: {cost_bytes.hex()} repr: {repr(cost_bytes)}')
    print(f'  gain_bytes hex: {gain_bytes.hex()} repr: {repr(gain_bytes)}')
    # The STRING ... DELIMITED BY SIZE copies ALL characters including NUL from the PIC 9(8)V99 field
    # PIC 9(8)V99 is 10 digits total (8 before decimal, 2 after), stored as DISPLAY is 10 chars
    # But HR-COSTO-PROMEDIO is PIC X(11), so 1 char left at end (the NUL)
    cost_raw = cost_bytes.replace(b'\x00', b'').decode('ascii')
    gain_raw = gain_bytes.replace(b'\x00', b'').decode('ascii')
    cost_val = int(cost_raw) / 100
    gain_val = int(gain_raw) / 100
    print(f'  cost_val={cost_val} gain_val={gain_val}')
"


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python3 -c "
# Understand the exact COBOL STRING behavior for the output format.
# COBOL: WS-HR-COSTO-TEMP is PIC 9(8)V99 (10 significant digits, 2 implied decimal)
# STRING WS-HR-COSTO-TEMP DELIMITED BY SIZE INTO HR-COSTO-PROMEDIO (PIC X(11))
# 
# DISPLAY format of PIC 9(8)V99 is 10 chars (V is not stored, it's just implied decimal point)
# So STRING ... DELIMITED BY SIZE copies all 10 chars + the X(11) field gets those 10 + 1 NUL pad
#
# Let us verify:
# Product 1: cost_avg=183.58 -> stored as integer 18358 (scaled by 100)
# PIC 9(8)V99 as DISPLAY = '0000018358' (10 digits)
# In X(11): '0000018358' + \x00 (1 NUL because X(11) init'd to spaces, STRING fills from left, remaining chars keep their init value)
# But wait - COBOL STRING into a PIC X field: the target is initialized to spaces? 
# Actually looking at the data, the NUL is at end of the text portion

# Let us compute what each product's values should be
from decimal import Decimal, ROUND_HALF_EVEN
_TWO = Decimal('0.01')

# From costos.dat:
# prod 1: lots 10@150.75, 20@200.00  -> total_value=1507.50+4000.00=5507.50, total_qty=30, avg=183.5833...->183.58
# prod 2: lots 5@100.00, 15@120.00   -> total_value=500+1800=2300, qty=20, avg=115.00
# prod 3: lots 8@80.00, 12@95.00, 5@110.00 -> total_value=640+1140+550=2330, qty=25, avg=93.20
# prod 4: lot 25@50.00               -> avg=50.00
# prod 5: lots 10@300.00, 10@350.00  -> total_value=3000+3500=6500, qty=20, avg=325.00

products = {
    '000000001': {'avg': Decimal('183.58'), 'gain': Decimal('25.50')},
    '000000002': {'avg': Decimal('115.00'), 'gain': Decimal('30.00')},
    '000000003': {'avg': Decimal('93.20'),  'gain': Decimal('15.00')},
    '000000004': {'avg': Decimal('50.00'),  'gain': Decimal('20.00')},
    '000000005': {'avg': Decimal('325.00'), 'gain': Decimal('40.00')},
}

for pid, d in products.items():
    # Scale to integer (2 decimal places implicit)
    avg_int = int(d['avg'] * 100)
    gain_int = int(d['gain'] * 100)
    # PIC 9(8)V99 -> 10 chars
    avg_str = f'{avg_int:010d}'
    # PIC 9(3)V99 -> 5 chars
    gain_str = f'{gain_int:05d}'
    print(f'{pid}: avg={avg_str!r}(len={len(avg_str)}) gain={gain_str!r}(len={len(gain_str)})')
    # Now: STRING DELIMITED BY SIZE into PIC X(11) and PIC X(6)
    # The target field is initialized to spaces. STRING fills from left.
    # But actual data shows NUL at end. Let us look at the actual bytes again.
print()
print('Actual data shows NUL bytes after digit strings. This suggests the COBOL')
print('PIC 9 fields are binary/packed, not DISPLAY. Let us check:')
print('PIC 9(8)V99: if DISPLAY, 10 chars. If COMP-3/packed, fewer bytes.')
print('But this is in WORKING-STORAGE WS-HR-COSTO-TEMP PIC 9(8)V99 - no COMP stated.')
print('=> It IS DISPLAY format (10 chars).')
print('The NUL at position 10 in the 11-byte field = the leftover uninitialized byte.')
print('COBOL STRING fills left-to-right; remaining bytes in target keep their value.')
print('Since OPEN OUTPUT initializes records to SPACES (0x20), NOT NUL...')
print('Unless the COBOL runtime initializes working storage to binary zeros.')
print('Working storage default init in GnuCOBOL = binary zeros.')
print('So the un-STRING-ed byte at end of X(11) field = 0x00 (NUL). Confirmed.')
"


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python3 -c "
# Full format breakdown confirmed:
# Record = 26 bytes + newline (LF)
# bytes 0-8:  HR-PRODUCTO-ID    PIC X(9)  = 9-digit product ID, left-aligned, zero-padded
# bytes 9-19: HR-COSTO-PROMEDIO PIC X(11) = 10-digit cost integer (scaled by 100) + NUL terminator
# bytes 20-25: HR-PORC-GANANCIA PIC X(6)  = 5-digit gain integer (scaled by 100) + NUL terminator
# 
# The NUL bytes come from GnuCOBOL's default working-storage zero initialization.
# The STRING op fills from the left, the last byte stays \x00.
#
# Encoding: ASCII/UTF-8 (all chars are 0x30-0x39, 0x00)

# Let us verify that the HISTORICO-OUT-RECORD structure is:
# HR-PRODUCTO-ID PIC X(9) = product_id formatted as 9-digit zero-padded
# HR-COSTO-PROMEDIO PIC X(11) = STRING of WS-HR-COSTO-TEMP (PIC 9(8)V99)
# HR-PORC-GANANCIA PIC X(6) = STRING of WS-HR-GANANCIA-TEMP (PIC 9(3)V99)

# Product ID format: MOVE WS-HR-PRODUCTO-ID TO HR-PRODUCTO-ID
# WS-HR-PRODUCTO-ID PIC 9(9) -> DISPLAY -> 9 ASCII digits, zero-padded

# Now verify with actual data:
data = open('legacy/cobol/historico.dat', 'rb').read()
lines = [l for l in data.split(b'\n') if l]
print(f'Records: {len(lines)}')
for line in lines:
    assert len(line) == 26, f'Expected 26, got {len(line)}'
    pid   = line[0:9]
    cost  = line[9:20]
    gain  = line[20:26]
    assert cost[10:11] == b'\x00', f'Expected NUL at cost[10], got {cost[10:11]!r}'
    assert gain[5:6]   == b'\x00', f'Expected NUL at gain[5], got {gain[5:6]!r}'
    cost_val = int(cost[:10]) / 100
    gain_val = int(gain[:5]) / 100
    print(f'{pid.decode()} | cost={cost_val:.2f} | gain={gain_val:.2f}')
print('Format verified.')
"


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python3 -c "
# Verify vencimientos.dat and alertas.dat format
ven = open('legacy/cobol/vencimientos.dat', 'rb').read()
ale = open('legacy/cobol/alertas.dat', 'rb').read()
print('vencimientos.dat:')
print(repr(ven))
print()
print('alertas.dat:')
print(repr(ale))
print()
# vencimientos lines
ven_lines = [l for l in ven.split(b'\n') if l]
ale_lines = [l for l in ale.split(b'\n') if l]
print('vencimientos records:', len(ven_lines))
for l in ven_lines:
    print(f'  len={len(l)} repr={repr(l)}')
print('alertas records:', len(ale_lines))
for l in ale_lines:
    print(f'  len={len(l)} repr={repr(l)}')
print()
print('Are they identical?', ven == ale)
"


### 🤖 Assistant

> 🔧 called: execute_command, execute_command

Now I have a complete understanding of the format. Let me also check the existing test and understand the project structure:

> 🔧 **execute_command** — cat modern/__init__.py

> 🔧 **execute_command** — python3 -c "
# Confirm the costos.dat record structure matches legacy_parser.py
from modern.legacy_parser import parse_costs_file
records = parse_costs_file('legacy/cobol/costos.dat')
print(f'Records: {len(records)}')
for r in records:
    print(r)
"


### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have all the information needed. Let me set up todos and implement everything:

> 🔧 **update_todo_list** — [-] Implement modern/expiration_processor.py
[ ] Implement modern/batch_runner.py
[ ] Create tests/test_alert_equivalence.py
[ ] Run full test suite and validate


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — modern/expiration_processor.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [x] Implement modern/expiration_processor.py
[-] Implement modern/batch_runner.py
[ ] Create tests/test_alert_equivalence.py
[ ] Run full test suite and validate


### 🤖 Assistant

> 🔧 called: write_file

Now implement the batch runner. The critical piece is the `historico.dat` writer which must reproduce the exact COBOL byte format: 9-byte product ID + 10-byte zero-padded cost integer + NUL + 5-byte zero-padded gain integer + NUL, followed by LF.

> 🔧 **write_file** — """Modern batch entry point — equivalent of COBOL BATCHCOSTOS PROCEDURE DIVISION.

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


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [x] Implement modern/expiration_processor.py
[x] Implement modern/batch_runner.py
[-] Create tests/test_alert_equivalence.py
[ ] Run full test suite and validate


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """test_alert_equivalence.py — verifies the modern alert/expiration pipeline
against the actual COBOL output files.

Test coverage:
  1. Expiration parsing (parse_expirations_file).
  2. Alert output byte-for-byte equivalence with COBOL alertas.dat.
  3. Alert count == 3.
  4. Full modern batch execution via run_batch.
  5. Modern historico.dat vs COBOL historico.dat (byte-for-byte).
  6. Modern alertas.dat vs COBOL alertas.dat (byte-for-byte).
  7. Expected batch counts: costs=5, alerts=3.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from modern.expiration_processor import parse_expirations_file, write_alerts_file
from modern.batch_runner import run_batch, write_historic_file
from modern.legacy_parser import parse_costs_file
from modern.cost_calculator import calculate_average_cost


# ---------------------------------------------------------------------------
# Canonical paths
# ---------------------------------------------------------------------------

COBOL_DIR         = Path("legacy/cobol")
COSTOS_PATH       = COBOL_DIR / "costos.dat"
VENCIMIENTOS_PATH = COBOL_DIR / "vencimientos.dat"
HISTORICO_COBOL   = COBOL_DIR / "historico.dat"
ALERTAS_COBOL     = COBOL_DIR / "alertas.dat"

EXPECTED_COST_COUNT  = 5
EXPECTED_ALERT_COUNT = 3


# ---------------------------------------------------------------------------
# 1. Expiration parsing
# ---------------------------------------------------------------------------

class TestExpirationParsing:
    def test_returns_list_of_lote_ids(self):
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        assert isinstance(lote_ids, list)

    def test_count_equals_three(self):
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        assert len(lote_ids) == EXPECTED_ALERT_COUNT

    def test_each_record_is_nine_chars(self):
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        for lote_id in lote_ids:
            assert len(lote_id) == 9, f"Expected 9 chars, got {len(lote_id)!r}"

    def test_order_preserved(self):
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        assert lote_ids == ["000000001", "000000003", "000000005"]

    def test_ids_not_transformed(self):
        """Lot IDs must be returned exactly as they appear in the file."""
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        for lote_id in lote_ids:
            assert lote_id == lote_id.strip(), "Unexpected whitespace transformation"

    def test_invalid_record_length_raises(self, tmp_path):
        bad_file = tmp_path / "bad.dat"
        bad_file.write_text("12345\n", encoding="ascii")  # only 5 chars, not 9
        with pytest.raises(ValueError, match="expected 9 characters"):
            parse_expirations_file(bad_file)


# ---------------------------------------------------------------------------
# 2 & 3. Alert output and count
# ---------------------------------------------------------------------------

class TestWriteAlertsFile:
    def test_alert_count_equals_three(self, tmp_path):
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        out = tmp_path / "alertas.dat"
        count = write_alerts_file(out, lote_ids)
        assert count == EXPECTED_ALERT_COUNT

    def test_alert_output_byte_for_byte(self, tmp_path):
        """Modern alertas.dat must be byte-for-byte identical to COBOL output."""
        lote_ids = parse_expirations_file(VENCIMIENTOS_PATH)
        out = tmp_path / "alertas.dat"
        write_alerts_file(out, lote_ids)

        modern_bytes = out.read_bytes()
        cobol_bytes  = ALERTAS_COBOL.read_bytes()
        assert modern_bytes == cobol_bytes, (
            f"alertas.dat mismatch:\n"
            f"  modern: {modern_bytes!r}\n"
            f"  cobol:  {cobol_bytes!r}"
        )

    def test_write_overwrites_existing_file(self, tmp_path):
        """write_alerts_file must use overwrite semantics (COBOL OPEN OUTPUT)."""
        lote_ids = ["000000001", "000000003", "000000005"]
        out = tmp_path / "alertas.dat"
        # Pre-populate with extra content.
        out.write_bytes(b"000000099\n000000098\n000000097\n000000096\n")
        write_alerts_file(out, lote_ids)
        lines = [l for l in out.read_bytes().split(b"\n") if l]
        assert len(lines) == 3

    def test_invalid_lote_id_length_raises(self, tmp_path):
        out = tmp_path / "alertas.dat"
        with pytest.raises(ValueError):
            write_alerts_file(out, ["12345"])  # 5 chars, not 9


# ---------------------------------------------------------------------------
# 4. Full modern batch execution
# ---------------------------------------------------------------------------

class TestRunBatch:
    def test_returns_tuple(self, tmp_path):
        result = run_batch(
            COSTOS_PATH,
            VENCIMIENTOS_PATH,
            tmp_path / "historico.dat",
            tmp_path / "alertas.dat",
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_expected_counts(self, tmp_path):
        cost_count, alert_count = run_batch(
            COSTOS_PATH,
            VENCIMIENTOS_PATH,
            tmp_path / "historico.dat",
            tmp_path / "alertas.dat",
        )
        assert cost_count  == EXPECTED_COST_COUNT,  (
            f"Expected cost_count={EXPECTED_COST_COUNT}, got {cost_count}"
        )
        assert alert_count == EXPECTED_ALERT_COUNT, (
            f"Expected alert_count={EXPECTED_ALERT_COUNT}, got {alert_count}"
        )


# ---------------------------------------------------------------------------
# 5. Modern historico.dat vs COBOL historico.dat (byte-for-byte)
# ---------------------------------------------------------------------------

class TestHistoricoEquivalence:
    def test_historico_byte_for_byte(self, tmp_path):
        """write_historic_file must reproduce the exact COBOL historico.dat bytes."""
        records      = parse_costs_file(COSTOS_PATH)
        cost_results = calculate_average_cost(records)
        out          = tmp_path / "historico.dat"
        write_historic_file(out, cost_results)

        modern_bytes = out.read_bytes()
        cobol_bytes  = HISTORICO_COBOL.read_bytes()
        assert modern_bytes == cobol_bytes, (
            "historico.dat byte mismatch\n"
            f"  modern ({len(modern_bytes)} bytes): {modern_bytes.hex()}\n"
            f"  cobol  ({len(cobol_bytes)} bytes): {cobol_bytes.hex()}"
        )

    def test_historico_via_run_batch(self, tmp_path):
        """End-to-end: batch_runner must also produce byte-exact historico.dat."""
        hist_out = tmp_path / "historico.dat"
        ale_out  = tmp_path / "alertas.dat"
        run_batch(COSTOS_PATH, VENCIMIENTOS_PATH, hist_out, ale_out)

        assert hist_out.read_bytes() == HISTORICO_COBOL.read_bytes()

    def test_historico_record_count(self, tmp_path):
        records      = parse_costs_file(COSTOS_PATH)
        cost_results = calculate_average_cost(records)
        out          = tmp_path / "historico.dat"
        count        = write_historic_file(out, cost_results)
        assert count == EXPECTED_COST_COUNT

    def test_historico_record_format(self, tmp_path):
        """Each record must be exactly 26 bytes + LF."""
        records      = parse_costs_file(COSTOS_PATH)
        cost_results = calculate_average_cost(records)
        out          = tmp_path / "historico.dat"
        write_historic_file(out, cost_results)

        raw_lines = [l for l in out.read_bytes().split(b"\n") if l]
        for i, line in enumerate(raw_lines):
            assert len(line) == 26, (
                f"Record {i}: expected 26 bytes, got {len(line)}"
            )
            # NUL bytes must be at positions 19 and 25.
            assert line[19] == 0, f"Record {i}: expected NUL at byte 19"
            assert line[25] == 0, f"Record {i}: expected NUL at byte 25"


# ---------------------------------------------------------------------------
# 6. Modern alertas.dat vs COBOL alertas.dat (byte-for-byte) via run_batch
# ---------------------------------------------------------------------------

class TestAlertasEquivalenceViaRunBatch:
    def test_alertas_byte_for_byte_via_run_batch(self, tmp_path):
        hist_out = tmp_path / "historico.dat"
        ale_out  = tmp_path / "alertas.dat"
        run_batch(COSTOS_PATH, VENCIMIENTOS_PATH, hist_out, ale_out)

        assert ale_out.read_bytes() == ALERTAS_COBOL.read_bytes(), (
            "alertas.dat produced by run_batch differs from COBOL output"
        )


# ---------------------------------------------------------------------------
# 7. Expected batch counts
# ---------------------------------------------------------------------------

class TestBatchCounts:
    """Explicit top-level assertions: costs=5, alerts=3."""

    def test_cost_count_is_five(self, tmp_path):
        cost_count, _ = run_batch(
            COSTOS_PATH, VENCIMIENTOS_PATH,
            tmp_path / "historico.dat", tmp_path / "alertas.dat",
        )
        assert cost_count == 5

    def test_alert_count_is_three(self, tmp_path):
        _, alert_count = run_batch(
            COSTOS_PATH, VENCIMIENTOS_PATH,
            tmp_path / "historico.dat", tmp_path / "alertas.dat",
        )
        assert alert_count == 3


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [x] Implement modern/expiration_processor.py
[x] Implement modern/batch_runner.py
[x] Create tests/test_alert_equivalence.py
[-] Run full test suite and validate


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Volumes/FreeDuty/github-projects/legacylens-assistant && .venv/bin/python -m pytest tests/test_alert_equivalence.py -v 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .venv/bin/pip install pytest -q 2>&1 | tail -5

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .venv/bin/python -m pytest tests/test_alert_equivalence.py -v 2>&1

### 🤖 Assistant

> 🔧 called: execute_command

19/19 pass. Now run the existing baseline test to confirm it still passes:

> 🔧 **execute_command** — .venv/bin/python tests/test_equivalence.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — PYTHONPATH=. .venv/bin/python tests/test_equivalence.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .venv/bin/python -m pytest tests/ -v 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

All 19 tests pass. `test_equivalence.py` is a plain script (not pytest-collected), and it also passes with `PYTHONPATH=.` as it did before — no regressions.

> 🔧 **update_todo_list** — [x] Implement modern/expiration_processor.py
[x] Implement modern/batch_runner.py
[x] Create tests/test_alert_equivalence.py
[x] Run full test suite and validate


### 🤖 Assistant

---

## Summary

### Files created

| File | Purpose |
|---|---|
| [`modern/expiration_processor.py`](modern/expiration_processor.py) | Modern equivalent of COBOL paragraph `3000-PROCESAR-ALERTAS` |
| [`modern/batch_runner.py`](modern/batch_runner.py) | Modern equivalent of COBOL `0000-MAIN-PROCEDURE` + `write_historic_file` |
| [`tests/test_alert_equivalence.py`](tests/test_alert_equivalence.py) | 19 tests covering all 7 required areas |

### Files modified
None. The existing COBOL files and the `test_equivalence.py` baseline are untouched.

---

### Implementation decisions

**`historico.dat` format** — the most subtle part. The COBOL `STRING … DELIMITED BY SIZE INTO HR-COSTO-PROMEDIO` statement copies exactly 10 ASCII digits (the `PIC 9(8)V99` DISPLAY representation, integer-scaled by 100) into an 11-byte `PIC X(11)` field. The 11th byte is never written, so it retains GnuCOBOL's default working-storage initialisation value of `0x00`. Same pattern applies to the 6-byte gain field — 5 digits + `0x00`. This was verified by `xxd`-ing the actual `historico.dat` bytes:

```
0000018358\x00  (bytes 9-19: cost field)
02550\x00        (bytes 20-25: gain field)
```

The writer in `batch_runner.write_historic_file` opens in **binary mode** and constructs the record explicitly — `cost_str + b"\x00" + gain_str + b"\x00" + b"\n"` — making the format self-documenting and immune to text-mode newline translation.

**`alertas.dat` format** — straightforward: 9 ASCII characters + `\n` per record, written in the same order as the input (`vencimientos.dat`). Opened with `newline="\n"` to prevent CRLF on Windows/macOS Python, ensuring byte-for-byte match.

**Reuse** — `batch_runner.py` imports and calls `parse_costs_file`, `calculate_average_cost`, `parse_expirations_file`, and `write_alerts_file` directly. No logic was duplicated.

---

### Test results

```
19 passed in 0.28s
```

All 7 required test areas covered, including:
- **Byte-for-byte**: `test_historico_byte_for_byte`, `test_alert_output_byte_for_byte`, `test_historico_via_run_batch`, `test_alertas_byte_for_byte_via_run_batch`
- **Counts**: `test_cost_count_is_five`, `test_alert_count_is_three`
- **Format invariants**: NUL at bytes 19 and 25, record length 26, overwrite semantics

---

### Remaining compatibility risks

1. **Decimal rounding mode** — `calculate_average_cost` uses `ROUND_HALF_EVEN` (banker's rounding), matching GnuCOBOL's `ROUNDED` default. If a future COBOL migration target uses a different rounding mode (e.g., `ROUND_HALF_UP`), costs could diverge. The byte-for-byte test would catch this immediately.

2. **NUL-byte portability** — the `0x00` bytes in `historico.dat` are a GnuCOBOL working-storage initialisation artefact. Other COBOL runtimes (IBM z/OS COBOL) may initialise working-storage differently (e.g., to spaces `0x20`), producing a different binary layout. If the canonical reference file is ever regenerated on a different runtime, `write_historic_file` would need adjustment.

3. **Input sort order** — `calculate_average_cost` uses a plain `dict`, which preserves Python 3.7+ insertion order. The batch relies on `costos.dat` being sorted by `product_id` (which it is), so the output product order matches COBOL. A shuffled input file would still produce correct averages but a different record order in `historico.dat`.

---

### 👤 User

The failure is caused by invoking tests/test_equivalence.py directly.

Run the test from the repository root as a module instead:

.venv/bin/python -m tests.test_equivalence

Then continue with the full relevant test suite using pytest.

Do not modify the source code or imports just to fix this error.

---

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .venv/bin/python -m tests.test_equivalence 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .venv/bin/python -m pytest tests/ -v 2>&1

### 🤖 Assistant

Both clean:

- **`-m tests.test_equivalence`** — ✓ LEGACY ↔ MODERN EQUIVALENCE PASSED (5 products, all costs and gains match)
- **`pytest tests/`** — 19 passed, 0 failed, 0 warnings

The correct invocation from the repository root is `.venv/bin/python -m tests.test_equivalence`, which puts the repo root on `sys.path` automatically so `import modern` resolves without needing `PYTHONPATH`.