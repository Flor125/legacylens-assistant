# Large-Scale Validation Dataset

This document describes how to generate, run, and reproduce the large-scale
validation dataset for LegacyLens.

## Purpose

The canonical golden fixture (`legacy/cobol/`) contains 10 cost records and
5 products and is the source of truth for byte-level equivalence.

The large-scale dataset validates that both the modern Python implementation
and the legacy COBOL program produce consistent, correct results at scale:

- **500 products**
- **≈ 50 000 cost records**
- **250 expiration records**

All generated files honor the exact COBOL input contracts:
- 35-byte fixed-width records with `DECIMAL-POINT IS COMMA`
- Products sorted ascending (required for COBOL control-break logic)
- All lots for the same product contiguous

---

## Files

```
tests/fixtures/large/
├── generate.py        ← deterministic generator (committed)
├── manifest.json      ← generation metadata and SHA-256 hashes (committed)
├── costos.dat         ← generated input (gitignored — regenerate locally)
├── vencimientos.dat   ← generated input (gitignored — regenerate locally)
└── batchcosto         ← compiled COBOL binary (gitignored)
```

The `.dat` files and the COBOL binary are **not committed**. They must be
generated/compiled locally before running the large-scale tests.

---

## Generating the dataset

From the repository root:

```bash
python tests/fixtures/large/generate.py
```

Expected output:

```
Generating dataset: seed=42, products=500, lots=10–200
  costos.dat      : 54,088 records
  vencimientos.dat: 250 records
  products        : 500
  sha256 costos   : <first 16 chars>…
  sha256 venc     : <first 16 chars>…
  manifest        : tests/fixtures/large/manifest.json
Done.
```

The generator is deterministic: running it twice with `--seed 42` always
produces files with identical SHA-256 hashes.

### Custom parameters

```bash
python tests/fixtures/large/generate.py --seed 42 --products 500 --lot-min 10 --lot-max 200
```

---

## Running the large-scale tests (Python only)

```bash
.venv/bin/python -m pytest tests/test_large_equivalence.py -v
```

These tests validate:

1. `manifest.json` is present and internally consistent.
2. Every generated record honors the COBOL field contracts.
3. The Python batch runner produces the correct product and alert counts.
4. Every `historico.dat` record is exactly 26 bytes with the expected NUL bytes.
5. Ten probe products have weighted averages matching the manifest-recorded
   expected values.
6. The generator is deterministic (two runs with the same seed produce identical
   SHA-256 hashes).

COBOL-dependent tests are automatically **skipped** if the compiled binary is
absent, so the Python suite runs anywhere.

---

## Running COBOL equivalence

### 1. Compile the COBOL binary

```bash
cobc -x -o tests/fixtures/large/batchcosto legacy/cobol/batchcosto.cob
```

### 2. Run the full test suite including COBOL equivalence

```bash
.venv/bin/python -m pytest tests/test_large_equivalence.py -v
```

When the binary is present, the `TestCobolCompile` and `TestCobolEquivalence`
test classes execute automatically. They:

- Run the COBOL binary against the same `costos.dat` and `vencimientos.dat`.
- Assert the COBOL binary reports the expected product and alert counts.
- Compare `historico.dat` byte-for-byte between the Python and COBOL outputs.
- Compare `alertas.dat` byte-for-byte between the Python and COBOL outputs.
- Validate probe-product weighted averages in the COBOL output.

### 3. Running the complete test suite

```bash
.venv/bin/python -m pytest tests/ -v
```

The canonical golden-fixture tests (`tests/test_equivalence.py` and
`tests/test_alert_equivalence.py`) always run unchanged.

---

## Reproducing results

The dataset is fully reproducible from the committed `generate.py` alone.
No binary or `.dat` file needs to be committed.

To reproduce from scratch:

```bash
python tests/fixtures/large/generate.py           # regenerate .dat files
.venv/bin/python -m pytest tests/ -v              # run all tests
```

To verify that the files on disk match the committed manifest:

```python
import hashlib, json
from pathlib import Path

manifest = json.loads(Path("tests/fixtures/large/manifest.json").read_text())

def sha256(path):
    h = hashlib.sha256()
    for chunk in iter(lambda: open(path, "rb").read(65536), b""):
        h.update(chunk)
    return h.hexdigest()

assert sha256("tests/fixtures/large/costos.dat") == manifest["sha256_costos"]
assert sha256("tests/fixtures/large/vencimientos.dat") == manifest["sha256_vencimientos"]
print("Files verified.")
```

---

## Design decisions

| Decision | Rationale |
|---|---|
| Seed = 42 | Explicit, memorable, documented constant |
| 500 products | Exercises control-break hundreds of times; fits PIC 9(9) |
| 10–200 lots/product | Variable depth; avoids uniform patterns |
| Quantity ≤ 9 999 | Keeps Σ qty well inside PIC S9(9) ceiling |
| Cost ≤ 9 999,99 | Keeps Σ(cost × qty) inside PIC S9(13)V99 ceiling |
| Odd-numbered IDs expire | Deterministic 50 % expiry rate without extra RNG |
| SHA-256 in manifest | Detects accidental file modification before test run |
| `.dat` files gitignored | Generated files are reproducible; committing them adds noise |
