"""test_alert_equivalence.py — verifies the modern alert/expiration pipeline
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
