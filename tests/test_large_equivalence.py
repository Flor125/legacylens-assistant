"""test_large_equivalence.py — scalability and equivalence validation.

Validates the modern Python implementation against a large generated dataset
(≈ 50 000 cost records, 500 products, 250 expiration records).

The dataset is produced by tests/fixtures/large/generate.py with a fixed seed
(42) and must be generated before this test suite runs:

    python tests/fixtures/large/generate.py

Test structure
--------------
1. TestManifest            — manifest.json is present and internally consistent.
2. TestInputContracts      — generated files honor every COBOL input field contract.
3. TestPythonBatch         — modern batch runner produces correct counts and format.
4. TestProbeProducts       — spot-check weighted averages for 10 probe products.
5. TestCobolEquivalence    — COBOL binary produces identical output (skipped when
                             the compiled binary is absent from the fixture dir).
6. TestReproducibility     — running the generator twice yields identical hashes.

All tests are independent of the canonical golden fixture in legacy/cobol/.
"""

from __future__ import annotations
import os
import hashlib
import json
import subprocess
import shutil
import sys
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path("tests/fixtures/large")
COSTOS_PATH = FIXTURE_DIR / "costos.dat"
VENC_PATH = FIXTURE_DIR / "vencimientos.dat"
MANIFEST_PATH = FIXTURE_DIR / "manifest.json"
COBOL_BINARY = FIXTURE_DIR / "batchcosto"
COBOL_SOURCE = Path("legacy/cobol/batchcosto.cob")

GENERATE_SCRIPT = FIXTURE_DIR / "generate.py"

# Python interpreter inside the virtual environment (if present).
_VENV_PYTHON = Path(".venv/bin/python")
PYTHON = str(_VENV_PYTHON) if _VENV_PYTHON.exists() else sys.executable

_TWO = Decimal("0.01")


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def manifest() -> dict:
    if not MANIFEST_PATH.exists():
        pytest.skip(
            "Large fixture not generated. Run: python tests/fixtures/large/generate.py"
        )
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def costos_lines(manifest) -> list[str]:
    """All non-empty lines from costos.dat (stripped of newline)."""
    with COSTOS_PATH.open(encoding="ascii") as f:
        return [ln.rstrip("\n\r") for ln in f if ln.strip()]


@pytest.fixture(scope="module")
def venc_lines(manifest) -> list[str]:
    """All non-empty lines from vencimientos.dat."""
    with VENC_PATH.open(encoding="ascii") as f:
        return [ln.rstrip("\n\r") for ln in f if ln.strip()]


# ---------------------------------------------------------------------------
# 1. TestManifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_manifest_exists(self):
        assert MANIFEST_PATH.exists(), (
            "manifest.json not found. Run: python tests/fixtures/large/generate.py"
        )

    def test_required_keys_present(self, manifest):
        required = {
            "seed", "n_products", "lot_range", "total_cost_records",
            "n_expirations", "probe_product_ids", "expected_averages",
            "sha256_costos", "sha256_vencimientos",
            "record_length_costos", "record_length_vencimientos",
        }
        missing = required - manifest.keys()
        assert not missing, f"Manifest missing keys: {missing}"

    def test_record_length_constants(self, manifest):
        assert manifest["record_length_costos"] == 35
        assert manifest["record_length_vencimientos"] == 9

    def test_costos_sha256_matches_file(self, manifest):
        actual = _sha256(COSTOS_PATH)
        assert actual == manifest["sha256_costos"], (
            f"costos.dat SHA-256 mismatch — file may have been modified.\n"
            f"  manifest : {manifest['sha256_costos']}\n"
            f"  on disk  : {actual}"
        )

    def test_vencimientos_sha256_matches_file(self, manifest):
        actual = _sha256(VENC_PATH)
        assert actual == manifest["sha256_vencimientos"], (
            f"vencimientos.dat SHA-256 mismatch — file may have been modified.\n"
            f"  manifest : {manifest['sha256_vencimientos']}\n"
            f"  on disk  : {actual}"
        )

    def test_n_expirations_is_half_n_products(self, manifest):
        expected = (manifest["n_products"] + 1) // 2
        assert manifest["n_expirations"] == expected

    def test_probe_count(self, manifest):
        assert len(manifest["probe_product_ids"]) >= 2


# ---------------------------------------------------------------------------
# 2. TestInputContracts
# ---------------------------------------------------------------------------


class TestInputContracts:
    def test_costos_record_length(self, costos_lines):
        for i, line in enumerate(costos_lines, start=1):
            assert len(line) == 35, (
                f"costos.dat line {i}: expected 35 chars, got {len(line)!r}"
            )

    def test_costos_record_count_matches_manifest(self, costos_lines, manifest):
        assert len(costos_lines) == manifest["total_cost_records"], (
            f"costos.dat line count {len(costos_lines)} ≠ "
            f"manifest total_cost_records {manifest['total_cost_records']}"
        )

    def test_product_ids_are_nine_digits(self, costos_lines):
        for i, line in enumerate(costos_lines, start=1):
            pid = line[0:9]
            assert pid.isdigit(), f"Line {i}: non-digit product ID {pid!r}"

    def test_decimal_separator_is_comma(self, costos_lines):
        for i, line in enumerate(costos_lines, start=1):
            cost_field = line[24:35].strip()
            assert "," in cost_field, (
                f"Line {i}: cost field {cost_field!r} missing comma decimal"
            )
            assert "." not in cost_field, (
                f"Line {i}: cost field {cost_field!r} contains dot (must use comma)"
            )
            gain_field = line[9:15].strip()
            assert "," in gain_field, (
                f"Line {i}: gain field {gain_field!r} missing comma decimal"
            )

    def test_products_sorted_ascending(self, costos_lines):
        """Products must be in ascending order for the COBOL control-break."""
        prev = -1
        for i, line in enumerate(costos_lines, start=1):
            pid = int(line[0:9])
            assert pid >= prev, (
                f"Sort violation at line {i}: product {pid} follows {prev}"
            )
            prev = pid

    def test_lots_are_contiguous(self, costos_lines):
        """All lots for the same product must be contiguous (no interleaving)."""
        seen: set[str] = set()
        current_pid = None
        for i, line in enumerate(costos_lines, start=1):
            pid = line[0:9]
            if pid != current_pid:
                assert pid not in seen, (
                    f"Line {i}: product {pid} appears non-contiguously"
                )
                if current_pid is not None:
                    seen.add(current_pid)
                current_pid = pid

    def test_vencimientos_record_length(self, venc_lines):
        for i, line in enumerate(venc_lines, start=1):
            assert len(line) == 9, (
                f"vencimientos.dat line {i}: expected 9 chars, got {len(line)}"
            )

    def test_vencimientos_count_matches_manifest(self, venc_lines, manifest):
        assert len(venc_lines) == manifest["n_expirations"]

    def test_vencimientos_ids_are_odd_products(self, venc_lines):
        for i, lid in enumerate(venc_lines, start=1):
            num = int(lid)
            assert num % 2 == 1, (
                f"vencimientos.dat line {i}: expected odd product ID, got {num}"
            )


# ---------------------------------------------------------------------------
# 3. TestPythonBatch
# ---------------------------------------------------------------------------


class TestPythonBatch:
    @pytest.fixture(scope="class")
    def batch_result(self, tmp_path_factory, manifest):
        from modern.batch_runner import run_batch
        tmp = tmp_path_factory.mktemp("python_batch")
        cost_count, alert_count = run_batch(
            COSTOS_PATH,
            VENC_PATH,
            tmp / "historico.dat",
            tmp / "alertas.dat",
        )
        return {
            "cost_count": cost_count,
            "alert_count": alert_count,
            "historico": tmp / "historico.dat",
            "alertas": tmp / "alertas.dat",
        }

    def test_cost_count_equals_n_products(self, batch_result, manifest):
        assert batch_result["cost_count"] == manifest["n_products"], (
            f"Expected {manifest['n_products']} cost output records, "
            f"got {batch_result['cost_count']}"
        )

    def test_alert_count_equals_n_expirations(self, batch_result, manifest):
        assert batch_result["alert_count"] == manifest["n_expirations"], (
            f"Expected {manifest['n_expirations']} alert records, "
            f"got {batch_result['alert_count']}"
        )

    def test_historico_record_count(self, batch_result, manifest):
        raw_lines = [
            ln for ln in batch_result["historico"].read_bytes().split(b"\n") if ln
        ]
        assert len(raw_lines) == manifest["n_products"]

    def test_historico_record_format(self, batch_result, manifest):
        """Every historico.dat record must be exactly 26 bytes (+ LF = 27)."""
        raw_lines = [
            ln for ln in batch_result["historico"].read_bytes().split(b"\n") if ln
        ]
        for i, line in enumerate(raw_lines):
            assert len(line) == 26, (
                f"Record {i}: expected 26 bytes, got {len(line)}"
            )
            assert line[19] == 0, f"Record {i}: expected NUL at byte 19"
            assert line[25] == 0, f"Record {i}: expected NUL at byte 25"

    def test_alertas_record_count(self, batch_result, manifest):
        raw_lines = [
            ln for ln in batch_result["alertas"].read_bytes().split(b"\n") if ln
        ]
        assert len(raw_lines) == manifest["n_expirations"]

    def test_alertas_record_length(self, batch_result):
        raw_lines = [
            ln for ln in batch_result["alertas"].read_bytes().split(b"\n") if ln
        ]
        for i, line in enumerate(raw_lines):
            assert len(line) == 9, (
                f"alertas.dat record {i}: expected 9 bytes, got {len(line)}"
            )

    def test_products_in_output_order(self, batch_result):
        """historico.dat products must be in ascending product-ID order."""
        from modern.historic_parser import parse_historic_file
        records = parse_historic_file(batch_result["historico"])
        ids = [r["product_id"] for r in records]
        assert ids == sorted(ids), "historico.dat products are not in ascending order"

    def test_no_duplicate_products(self, batch_result):
        from modern.historic_parser import parse_historic_file
        records = parse_historic_file(batch_result["historico"])
        ids = [r["product_id"] for r in records]
        assert len(ids) == len(set(ids)), "Duplicate product IDs in historico.dat"


# ---------------------------------------------------------------------------
# 4. TestProbeProducts
# ---------------------------------------------------------------------------


class TestProbeProducts:
    @pytest.fixture(scope="class")
    def historico_by_product(self, tmp_path_factory, manifest):
        from modern.batch_runner import run_batch
        from modern.historic_parser import parse_historic_file
        tmp = tmp_path_factory.mktemp("probe_batch")
        run_batch(
            COSTOS_PATH,
            VENC_PATH,
            tmp / "historico.dat",
            tmp / "alertas.dat",
        )
        records = parse_historic_file(tmp / "historico.dat")
        return {r["product_id"]: r for r in records}

    def test_probe_averages_match_expected(self, historico_by_product, manifest):
        expected = manifest["expected_averages"]
        mismatches = []
        for pid, exp_avg_str in expected.items():
            exp_avg = float(exp_avg_str)
            actual = historico_by_product[pid]["average_cost"]
            if abs(actual - exp_avg) > 0.005:
                mismatches.append(
                    f"{pid}: expected {exp_avg:.2f}, got {actual:.2f}"
                )
        assert not mismatches, "Probe average mismatches:\n" + "\n".join(mismatches)

    def test_probe_gains_match_expected(self, historico_by_product, manifest):
        expected_gains = manifest.get("expected_gains", {})
        mismatches = []
        for pid, exp_gain_str in expected_gains.items():
            exp_gain = float(exp_gain_str)
            actual = historico_by_product[pid]["gain"]
            if abs(actual - exp_gain) > 0.005:
                mismatches.append(
                    f"{pid}: expected gain {exp_gain:.2f}, got {actual:.2f}"
                )
        assert not mismatches, "Probe gain mismatches:\n" + "\n".join(mismatches)

    def test_first_product_present(self, historico_by_product):
        assert "000000001" in historico_by_product

    def test_last_product_present(self, historico_by_product, manifest):
        last = f"{manifest['n_products']:09d}"
        assert last in historico_by_product

    def test_all_costs_are_positive(self, historico_by_product):
        for pid, rec in historico_by_product.items():
            assert rec["average_cost"] > 0, (
                f"Product {pid} has non-positive average cost {rec['average_cost']}"
            )


# ---------------------------------------------------------------------------
# 5. TestCobolEquivalence
# ---------------------------------------------------------------------------


def _cobol_binary_available() -> bool:
    return COBOL_BINARY.exists()


def _cobc_available() -> bool:
    return shutil.which("cobc") is not None


@pytest.mark.skipif(
    not _cobc_available(),
    reason="cobc not found on PATH — skipping COBOL compilation",
)
class TestCobolCompile:
    def test_compile_cobol_binary(self):
        """Compile batchcosto.cob into tests/fixtures/large/batchcosto."""
        result = subprocess.run(
            ["cobc", "-x", "-o", str(COBOL_BINARY), str(COBOL_SOURCE)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"cobc compilation failed:\n{result.stderr}"
        )
        assert COBOL_BINARY.exists()


@pytest.mark.skipif(
    not _cobol_binary_available(),
    reason=(
        "COBOL binary not found at tests/fixtures/large/batchcosto. "
        "Run TestCobolCompile first or compile manually."
    ),
)
class TestCobolEquivalence:
    @pytest.fixture(scope="class")
    def cobol_outputs(self, tmp_path_factory, manifest):
        """Run the compiled COBOL binary against the large fixture data.

        The COBOL program resolves file names from CWD (ASSIGN TO "costos.dat"),
        so we create a temporary working directory with symlinks to the fixture
        input files and let the binary write its output there.
        """
        work_dir = tmp_path_factory.mktemp("cobol_run")

        # Link input files into the working directory.
        (work_dir / "costos.dat").symlink_to(COSTOS_PATH.resolve())
        (work_dir / "vencimientos.dat").symlink_to(VENC_PATH.resolve())

        result = subprocess.run(
            [str(COBOL_BINARY.resolve())],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            env={**os.environ, "COB_LS_VALIDATE": "0"},
        )
        assert result.returncode == 0, (
            f"COBOL batch failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        return {
            "historico": work_dir / "historico.dat",
            "alertas": work_dir / "alertas.dat",
            "stdout": result.stdout,
        }

    def test_cobol_cost_count(self, cobol_outputs, manifest):
        n = manifest["n_products"]
        assert f"{n:04d}" in cobol_outputs["stdout"] or str(n) in cobol_outputs["stdout"], (
            f"Expected cost count {n} in COBOL stdout:\n{cobol_outputs['stdout']}"
        )

    def test_cobol_alert_count(self, cobol_outputs, manifest):
        n = manifest["n_expirations"]
        assert f"{n:04d}" in cobol_outputs["stdout"] or str(n) in cobol_outputs["stdout"], (
            f"Expected alert count {n} in COBOL stdout:\n{cobol_outputs['stdout']}"
        )

    def test_cobol_historico_record_count(self, cobol_outputs, manifest):
        lines = [ln for ln in cobol_outputs["historico"].read_bytes().split(b"\n") if ln]
        assert len(lines) == manifest["n_products"], (
            f"COBOL historico.dat: expected {manifest['n_products']} records, "
            f"got {len(lines)}"
        )

    def test_cobol_historico_record_format(self, cobol_outputs, manifest):
        lines = [ln for ln in cobol_outputs["historico"].read_bytes().split(b"\n") if ln]
        for i, line in enumerate(lines):
            assert len(line) == 26, f"COBOL record {i}: expected 26 bytes, got {len(line)}"
            assert line[19] == 0, f"COBOL record {i}: NUL missing at byte 19"
            assert line[25] == 0, f"COBOL record {i}: NUL missing at byte 25"

    def test_cobol_alertas_record_count(self, cobol_outputs, manifest):
        lines = [ln for ln in cobol_outputs["alertas"].read_bytes().split(b"\n") if ln]
        assert len(lines) == manifest["n_expirations"]

    def test_python_cobol_historico_byte_identical(
        self, cobol_outputs, tmp_path_factory, manifest
    ):
        """Python and COBOL historico.dat must be byte-for-byte identical."""
        from modern.batch_runner import run_batch
        tmp = tmp_path_factory.mktemp("cross_check")
        run_batch(
            COSTOS_PATH,
            VENC_PATH,
            tmp / "historico.dat",
            tmp / "alertas.dat",
        )
        py_bytes = (tmp / "historico.dat").read_bytes()
        cobol_bytes = cobol_outputs["historico"].read_bytes()
        assert py_bytes == cobol_bytes, (
            f"historico.dat byte mismatch:\n"
            f"  Python : {len(py_bytes)} bytes\n"
            f"  COBOL  : {len(cobol_bytes)} bytes\n"
            f"  First diff at byte: {_first_diff(py_bytes, cobol_bytes)}"
        )

    def test_python_cobol_alertas_byte_identical(
        self, cobol_outputs, tmp_path_factory, manifest
    ):
        """Python and COBOL alertas.dat must be byte-for-byte identical."""
        from modern.batch_runner import run_batch
        tmp = tmp_path_factory.mktemp("cross_check_alertas")
        run_batch(
            COSTOS_PATH,
            VENC_PATH,
            tmp / "historico.dat",
            tmp / "alertas.dat",
        )
        py_bytes = (tmp / "alertas.dat").read_bytes()
        cobol_bytes = cobol_outputs["alertas"].read_bytes()
        assert py_bytes == cobol_bytes, (
            f"alertas.dat byte mismatch:\n"
            f"  Python : {len(py_bytes)} bytes\n"
            f"  COBOL  : {len(cobol_bytes)} bytes"
        )

    def test_cobol_probe_averages(self, cobol_outputs, manifest):
        """COBOL weighted averages must match the manifest expected values."""
        from modern.historic_parser import parse_historic_file
        records = parse_historic_file(cobol_outputs["historico"])
        by_product = {r["product_id"]: r for r in records}

        expected = manifest["expected_averages"]
        mismatches = []
        for pid, exp_avg_str in expected.items():
            exp_avg = float(exp_avg_str)
            actual = by_product[pid]["average_cost"]
            if abs(actual - exp_avg) > 0.005:
                mismatches.append(
                    f"{pid}: expected {exp_avg:.2f}, got {actual:.2f}"
                )
        assert not mismatches, (
            "COBOL probe average mismatches:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# 6. TestReproducibility
# ---------------------------------------------------------------------------


class TestReproducibility:
    def test_generator_is_deterministic(self, tmp_path, manifest):
        """Running the generator twice with seed=42 must produce identical hashes."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "generate", GENERATE_SCRIPT
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        run1 = tmp_path / "run1"
        run2 = tmp_path / "run2"

        m1 = mod.generate(run1, seed=manifest["seed"],
                          n_products=manifest["n_products"])
        m2 = mod.generate(run2, seed=manifest["seed"],
                          n_products=manifest["n_products"])

        assert m1["sha256_costos"] == m2["sha256_costos"], (
            "costos.dat SHA-256 differs between two runs with the same seed"
        )
        assert m1["sha256_vencimientos"] == m2["sha256_vencimientos"], (
            "vencimientos.dat SHA-256 differs between two runs with the same seed"
        )

    def test_different_seed_produces_different_file(self, tmp_path, manifest):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "generate", GENERATE_SCRIPT
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        alt = tmp_path / "alt"
        m_alt = mod.generate(alt, seed=manifest["seed"] + 1,
                             n_products=manifest["n_products"])
        assert m_alt["sha256_costos"] != manifest["sha256_costos"], (
            "Different seed produced identical costos.dat — generator may not be seeded"
        )


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _first_diff(a: bytes, b: bytes) -> int | str:
    for i, (ba, bb) in enumerate(zip(a, b)):
        if ba != bb:
            return i
    if len(a) != len(b):
        return f"lengths differ ({len(a)} vs {len(b)})"
    return "no diff"
