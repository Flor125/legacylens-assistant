# LegacyLens

> **Preserve business behavior. Modernize the implementation.**

LegacyLens is a modernization verification prototype that validates whether a modern implementation preserves the observable business behavior of a legacy COBOL program.

Instead of treating modernization as a direct source-code translation, LegacyLens follows a behavior-first approach:

```
Legacy COBOL
     │
     ▼
Analyze behavior
     │
     ▼
Extract business rules
     │
     ▼
Modern implementation
     │
     ▼
Execute with equivalent input
     │
     ▼
Compare outputs
     │
     ▼
Validate equivalence
```

## Why LegacyLens?

Modernizing legacy systems is not only about translating one programming language into another.

Legacy programs often depend on details that are easy to miss:

- Fixed-width records
- Decimal representation
- Rounding behavior
- Control-break processing
- Input ordering
- Output field widths
- Binary or runtime-specific output behavior
- Business rules embedded in procedural code

LegacyLens explores how these behaviors can be identified, reproduced, and validated before considering the modernization complete.

The central principle is:

> Preserve observable legacy behavior before changing the implementation.

## Current MVP

The current MVP focuses on a COBOL batch program:

`legacy/cobol/batchcosto.cob`

The program processes two input files:

- `costos.dat`
- `vencimientos.dat`

and produces:

- `historico.dat`
- `alertas.dat`

The cost-processing flow calculates a weighted average cost for each product:

```
              Σ(quantity × cost)
Average = ─────────────────────────
                 Σ(quantity)
```

The expiration flow copies expiration lot identifiers into the alert output.

### Canonical validation fixture

The initial validation fixture contains:

- 10 cost records
- 5 products
- 3 expiration records

The expected weighted-average costs are:

| Product | Average cost |
|---|---|
| 000000001 | 183.58 |
| 000000002 | 115.00 |
| 000000003 | 93.20 |
| 000000004 | 50.00 |
| 000000005 | 325.00 |

## Architecture

```
                    LEGACY SYSTEM
                         │
                         ▼
               ┌──────────────────┐
               │ batchcosto.cob   │
               │                  │
               │ COBOL batch      │
               └────────┬─────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        costos.dat          vencimientos.dat
             │                     │
             ▼                     ▼
       Legacy Parser       Expiration Processor
             │                     │
             ▼                     │
      Cost Calculator              │
             │                     │
             ▼                     ▼
       historico.dat         alertas.dat
             │                     │
             └──────────┬──────────┘
                        ▼
                Equivalence Tests
```

## Modern implementation

The modern implementation is divided into focused components:

| Component | Responsibility |
|---|---|
| `modern/legacy_parser.py` | Parse fixed-width legacy cost records |
| `modern/cost_calculator.py` | Calculate weighted average costs |
| `modern/historic_parser.py` | Parse COBOL historical output |
| `modern/expiration_processor.py` | Process expiration records and alerts |
| `modern/batch_runner.py` | Orchestrate the complete modern batch |

## IBM Bob

IBM Bob was used as the AI modernization agent throughout the project.

Bob was first used to analyze the legacy COBOL program before implementing the modern equivalent.

The analysis focused on:

- Business rules
- Input/output contracts
- Control-break logic
- Weighted-average calculation
- Decimal representation
- Dependencies
- Data flow
- Compatibility risks
- Observable behavior
- Modernization strategy

Bob identified, among other things, the COBOL control-break pattern and the:

```
DECIMAL-POINT IS COMMA
```

configuration used by the legacy program.

The analysis and modernization planning are documented in:

```
docs/evidence/
├── 03-bob-legacy-analysis.md
└── 04-bob-modernization-plan.md
```

Bob was also used to:

- Analyze the legacy implementation.
- Design the modernization plan.
- Harden the modernization and its equivalence tests.
- Design a deterministic large-scale validation dataset.
- Verify the complete implementation.

Task-session evidence and exported Bob task histories are stored in:

`bob_sessions/`

## A real legacy bug discovered during validation

During the initial equivalence validation, a real defect was discovered in the COBOL historical-output routine.

The calculated average cost was moved into a working variable that was also used for the current input cost:

```
MOVE WS-HR-COSTO-PROMEDIO TO WS-PRECIOCOSTO-N
```

This could cause the calculated average from one product to become the input cost for the next product.

The fix introduced dedicated temporary fields for historical output:

```
05 WS-HR-COSTO-TEMP     PIC 9(8)V99.
05 WS-HR-GANANCIA-TEMP  PIC 9(3)V99.
```

After the fix, the COBOL baseline produced the expected results and could be used as the behavioral reference for the modernization.

The investigation is documented in:

```
docs/evidence/
├── 02-legacy-modern-equivalence.md
└── 01-decimal-format.md
```

## Legacy compatibility details

### Decimal representation

The COBOL program declares:

```
DECIMAL-POINT IS COMMA
```

Therefore the legacy input uses values such as:

```
150,75
200,00
```

rather than:

```
150.75
200.00
```

This behavior is treated as part of the legacy input contract.

The compatibility investigation is documented in:

`docs/evidence/01-decimal-format.md`

### Output compatibility

LegacyLens does not only compare calculated numbers.

The modern batch also reproduces the observable output format of the COBOL program.

For `historico.dat`, the COBOL output contains records with:

```
9 bytes   product ID
10 bytes  cost value
1 byte    NUL
5 bytes   gain value
1 byte    NUL
1 byte    LF
```

The modern writer reproduces this format and the tests compare the generated file directly against the COBOL output.

This allows the validation to detect differences that would not be visible from numerical comparisons alone.

## Large-scale validation

In addition to the canonical 10-record fixture, LegacyLens includes a deterministic large-scale validation dataset.

The dataset contains:

- 500 products
- 54,088 cost records
- 250 expiration records
- Fixed-width COBOL-compatible input
- Products sorted according to the legacy control-break requirements
- Deterministic generation using seed 42
- SHA-256 hashes recorded in the dataset manifest

The generated input files and compiled COBOL binary are intentionally not committed to the repository. They can be reproduced locally using:

```
python tests/fixtures/large/generate.py
```

The large-scale validation verifies:

- Record format compatibility
- Product counts
- Alert counts
- Weighted-average calculations
- Output record format
- Deterministic dataset generation
- COBOL/Python output equivalence
- Byte-for-byte equality of generated output files

More details:

`docs/04-large-dataset.md`

## Validation

LegacyLens validates the modern implementation against the actual COBOL behavior.

### Canonical equivalence

```
✓ LEGACY ↔ MODERN EQUIVALENCE PASSED

Input records: 10
Products compared: 5

000000001: COBOL cost=183.58 MODERN cost=183.58
000000002: COBOL cost=115.00 MODERN cost=115.00
000000003: COBOL cost=93.20 MODERN cost=93.20
000000004: COBOL cost=50.00 MODERN cost=50.00
000000005: COBOL cost=325.00 MODERN cost=325.00
```

### Full automated suite

```
59 passed
```

The test suite covers:

- Legacy cost equivalence
- Weighted-average calculations
- Profit/gain equivalence
- Expiration processing
- Alert ordering
- Alert counts
- Output overwrite behavior
- Historical output format
- `historico.dat` byte-for-byte equivalence
- `alertas.dat` byte-for-byte equivalence
- Complete batch execution
- Large-scale validation
- Deterministic dataset generation

For the large-scale workload, both implementations produce:

- 500 cost records
- 250 alert records

and the generated `historico.dat` and `alertas.dat` outputs are compared byte-for-byte.

## Running the project

### Requirements

- Python 3
- GnuCOBOL
- pytest

A virtual environment is recommended.

### Run the canonical equivalence test

From the repository root:

```
PYTHONPATH=. .venv/bin/python tests/test_equivalence.py
```

Expected result:

```
✓ LEGACY ↔ MODERN EQUIVALENCE PASSED
```

### Run the complete test suite

```
.venv/bin/python -m pytest tests/ -v
```

Expected result:

```
59 passed
```

### Generate the large validation dataset

```
python tests/fixtures/large/generate.py
```

### Compile the COBOL program for large-scale validation

```
cobc -x -o tests/fixtures/large/batchcosto \
  legacy/cobol/batchcosto.cob
```

### Run large-scale equivalence

```
.venv/bin/python -m pytest tests/test_large_equivalence.py -v
```

On the macOS GnuCOBOL environment used for this prototype, the large-scale COBOL equivalence test runs with:

```
COB_LS_VALIDATE=0
```

This disables GnuCOBOL's line-sequential NUL-byte validation so that the historical COBOL output can be compared byte-for-byte with the legacy-compatible Python output.

## Project structure

```
legacy/
└── cobol/
    └── batchcosto.cob

modern/
├── __init__.py
├── legacy_parser.py
├── cost_calculator.py
├── historic_parser.py
├── expiration_processor.py
└── batch_runner.py

tests/
├── test_equivalence.py
├── test_alert_equivalence.py
├── test_large_equivalence.py
└── fixtures/
    └── large/
        ├── generate.py
        └── manifest.json

docs/
├── evidence/
│   ├── 01-decimal-format.md
│   ├── 02-legacy-modern-equivalence.md
│   ├── 03-bob-legacy-analysis.md
│   └── 04-bob-modernization-plan.md
└── 04-large-dataset.md

bob_sessions/
├── Task session screenshots
└── Exported task histories
```

Generated `.dat` files, compiled binaries, Python cache files, and other local artifacts are excluded from version control.

## Modernization principle

LegacyLens follows one central principle:

> Preserve observable legacy behavior before changing the implementation.

The goal is not to make the modern implementation look like the COBOL implementation.

The goal is to:

1. Understand what the legacy system actually does.
2. Extract the business and compatibility rules.
3. Implement the modern equivalent.
4. Execute both implementations against equivalent inputs.
5. Compare their observable outputs.
6. Use automated validation to demonstrate that the modernization did not silently change behavior.

## Current status

**Working prototype**

The current implementation demonstrates:

- COBOL behavior analysis
- Legacy business-rule extraction
- Python modernization
- Weighted-average cost equivalence
- Expiration-alert equivalence
- Byte-for-byte output validation
- Large-scale deterministic validation
- Automated regression testing
- IBM Bob-assisted modernization workflow
- Task-session evidence for IBM Bob usage

## Hackathon

Built for the IBM Bob 2.0 Hackathon.

LegacyLens uses IBM Bob as a core part of the legacy analysis, modernization planning, implementation, validation, and verification workflow.

The repository includes task-session evidence and exported task histories in:

`bob_sessions/`