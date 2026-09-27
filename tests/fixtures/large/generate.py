"""generate.py — deterministic large-scale dataset generator for LegacyLens.

Produces costos.dat and vencimientos.dat in the same directory as this script,
matching the exact COBOL input contract used by batchcosto.cob:

  costos.dat record layout (35 ASCII bytes + LF):
    cols  0– 8  CR-PRODUCTO-ID    PIC X(9)   zero-padded 9-digit ID
    cols  9–14  CR-PORC-GANANCIA  PIC X(6)   NNN,NN (comma decimal)
    cols 15–23  CR-CANTIDAD       PIC X(9)   right-justified integer
    cols 24–34  CR-PRECIOCOSTO    PIC X(11)  right-justified N[NNN],NN

  vencimientos.dat record layout (9 ASCII bytes + LF):
    cols  0– 8  VR-LOTE-ID        PIC X(9)   zero-padded 9-digit ID

Design decisions:
  - Single RNG seed (SEED = 42) makes every run identical.
  - Products are emitted in strictly ascending ID order (mandatory for the
    COBOL control-break pattern in 2000-PROCESAR-COSTOS).
  - All lots for a product are contiguous.
  - Gain percentage is constant within a product (matches COBOL behavior:
    WS-PORC-GANANCIA is set once per product from the first lot).
  - Every odd-numbered product ID is added to vencimientos.dat (50 % rate).
  - Value ranges are chosen so that intermediate COBOL accumulators never
    overflow their PIC clauses:
      WS-TOTAL-COSTO-VALOR  PIC S9(13)V99 COMP-3  → max ≈ 99 999 999 999 999,99
      WS-TOTAL-CANTIDAD     PIC S9(9)     COMP     → max 999 999 999
    Worst-case per product: 200 lots × 9 999 qty × 9 999,99 ≈ 19 997 998 000
    (well within PIC S9(13)V99).

Usage:
    python tests/fixtures/large/generate.py
    python tests/fixtures/large/generate.py --seed 42 --products 500

The script writes:
    tests/fixtures/large/costos.dat
    tests/fixtures/large/vencimientos.dat
    tests/fixtures/large/manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# Default generation parameters (match proposal exactly)
# ---------------------------------------------------------------------------

SEED = 42
N_PRODUCTS = 500
LOT_MIN = 10
LOT_MAX = 200
QTY_MIN = 1
QTY_MAX = 9_999
COST_MIN = Decimal("10.00")
COST_MAX = Decimal("9999.99")
GAIN_MIN = Decimal("5.00")
GAIN_MAX = Decimal("50.00")

# Number of probe products sampled for expected-average verification.
N_PROBES = 10

# ---------------------------------------------------------------------------
# Formatting helpers (must match legacy_parser.py field widths exactly)
# ---------------------------------------------------------------------------

_TWO = Decimal("0.01")


def _fmt_gain(v: Decimal) -> str:
    """Format gain as PIC X(6) = 'NNN,NN' (comma decimal, no leading space)."""
    s = f"{v:.2f}".replace(".", ",")
    return s.ljust(6)


def _fmt_quantity(v: int) -> str:
    """Format quantity as PIC X(9), right-justified."""
    return str(v).rjust(9)


def _fmt_cost(v: Decimal) -> str:
    """Format cost as PIC X(11), right-justified, comma decimal."""
    s = f"{v:.2f}".replace(".", ",")
    return s.rjust(11)


def _fmt_product_id(n: int) -> str:
    """Format product ID as PIC X(9), zero-padded."""
    return f"{n:09d}"


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


def generate(
    out_dir: Path,
    seed: int = SEED,
    n_products: int = N_PRODUCTS,
    lot_min: int = LOT_MIN,
    lot_max: int = LOT_MAX,
) -> dict:
    """Generate costos.dat, vencimientos.dat, and manifest.json.

    Returns the manifest dict (also written to manifest.json).
    """
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    costos_path = out_dir / "costos.dat"
    venc_path = out_dir / "vencimientos.dat"
    manifest_path = out_dir / "manifest.json"

    # Per-product expected averages (for probe validation).
    expected_averages: dict[str, str] = {}

    total_cost_records = 0

    with (
        costos_path.open("w", encoding="ascii", newline="\n") as cf,
        venc_path.open("w", encoding="ascii", newline="\n") as vf,
    ):
        for prod_num in range(1, n_products + 1):
            prod_id = _fmt_product_id(prod_num)

            # Gain is constant for all lots of a product (matches COBOL behavior).
            gain_raw = Decimal(
                str(round(rng.uniform(float(GAIN_MIN), float(GAIN_MAX)), 2))
            ).quantize(_TWO, rounding=ROUND_HALF_EVEN)

            n_lots = rng.randint(lot_min, lot_max)

            total_value = Decimal(0)
            total_qty = 0

            for _ in range(n_lots):
                qty = rng.randint(QTY_MIN, QTY_MAX)
                cost_raw = Decimal(
                    str(round(rng.uniform(float(COST_MIN), float(COST_MAX)), 2))
                ).quantize(_TWO, rounding=ROUND_HALF_EVEN)

                line = (
                    prod_id
                    + _fmt_gain(gain_raw)
                    + _fmt_quantity(qty)
                    + _fmt_cost(cost_raw)
                )
                assert len(line) == 35, (
                    f"Record length error for product {prod_id}: "
                    f"got {len(line)}, expected 35"
                )
                cf.write(line + "\n")

                total_value += Decimal(qty) * cost_raw
                total_qty += qty
                total_cost_records += 1

            # Compute expected weighted average (same formula as cost_calculator.py).
            avg = (total_value / Decimal(total_qty)).quantize(
                _TWO, rounding=ROUND_HALF_EVEN
            )
            expected_averages[prod_id] = str(avg)

            # Every odd product number goes into vencimientos.dat.
            if prod_num % 2 == 1:
                assert len(prod_id) == 9
                vf.write(prod_id + "\n")

    n_expirations = (n_products + 1) // 2  # ceiling of n_products / 2

    # Probe products: first, last, and N_PROBES-2 evenly spaced in between.
    probe_ids = _select_probes(n_products, N_PROBES)

    # SHA-256 hashes of the generated files.
    sha_costos = _sha256(costos_path)
    sha_venc = _sha256(venc_path)

    manifest = {
        "seed": seed,
        "n_products": n_products,
        "lot_range": [lot_min, lot_max],
        "qty_range": [QTY_MIN, QTY_MAX],
        "cost_range": [str(COST_MIN), str(COST_MAX)],
        "gain_range": [str(GAIN_MIN), str(GAIN_MAX)],
        "total_cost_records": total_cost_records,
        "n_expirations": n_expirations,
        "probe_product_ids": probe_ids,
        "expected_averages": {pid: expected_averages[pid] for pid in probe_ids},
        "expected_gains": {},  # populated below
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sha256_costos": sha_costos,
        "sha256_vencimientos": sha_venc,
        "record_length_costos": 35,
        "record_length_vencimientos": 9,
        "decimal_separator": "COMMA",
        "cobol_program": "batchcosto.cob",
    }

    # Populate expected gains for probe products by re-running a tiny seeded
    # replay — we need the gain values but they were consumed in the RNG stream
    # above.  The simplest correct approach: re-parse the written file for those
    # product IDs only.
    probe_set = set(probe_ids)
    gains_found: dict[str, str] = {}
    with costos_path.open("r", encoding="ascii") as cf:
        for line in cf:
            line = line.rstrip("\n\r")
            if not line:
                continue
            pid = line[0:9]
            if pid in probe_set and pid not in gains_found:
                gain_str = line[9:15].strip().replace(",", ".")
                gains_found[pid] = str(
                    Decimal(gain_str).quantize(_TWO, rounding=ROUND_HALF_EVEN)
                )
    manifest["expected_gains"] = gains_found

    with manifest_path.open("w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    return manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _select_probes(n_products: int, n: int) -> list[str]:
    """Return n evenly-spaced product IDs (first and last always included)."""
    if n_products <= n:
        return [_fmt_product_id(i) for i in range(1, n_products + 1)]
    step = (n_products - 1) / (n - 1)
    indices = sorted({round(step * i) + 1 for i in range(n)})
    # Guarantee first and last are present.
    indices[0] = 1
    indices[-1] = n_products
    return [_fmt_product_id(i) for i in indices]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic large-scale LegacyLens dataset."
    )
    parser.add_argument(
        "--seed", type=int, default=SEED,
        help=f"RNG seed (default: {SEED})",
    )
    parser.add_argument(
        "--products", type=int, default=N_PRODUCTS,
        help=f"Number of products to generate (default: {N_PRODUCTS})",
    )
    parser.add_argument(
        "--lot-min", type=int, default=LOT_MIN,
        help=f"Minimum lots per product (default: {LOT_MIN})",
    )
    parser.add_argument(
        "--lot-max", type=int, default=LOT_MAX,
        help=f"Maximum lots per product (default: {LOT_MAX})",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    out_dir = Path(__file__).parent

    print(f"Generating dataset: seed={args.seed}, products={args.products}, "
          f"lots={args.lot_min}–{args.lot_max}")

    manifest = generate(
        out_dir=out_dir,
        seed=args.seed,
        n_products=args.products,
        lot_min=args.lot_min,
        lot_max=args.lot_max,
    )

    print(f"  costos.dat      : {manifest['total_cost_records']:,} records")
    print(f"  vencimientos.dat: {manifest['n_expirations']:,} records")
    print(f"  products        : {manifest['n_products']}")
    print(f"  sha256 costos   : {manifest['sha256_costos'][:16]}…")
    print(f"  sha256 venc     : {manifest['sha256_vencimientos'][:16]}…")
    print(f"  manifest        : {out_dir / 'manifest.json'}")
    print("Done.")
