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
- Legacy business rules embedded in procedural code

LegacyLens explores how these behaviors can be identified, reproduced, and validated before considering the modernization complete.

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

The expiration flow copies the expiration lot identifiers into the alert output.

The current fixture contains:

- 10 cost records
- 5 products
- 3 expiration records

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

The modern implementation is divided into small components:

| Component | Responsibility |
|---|---|
| `modern/legacy_parser.py` | Parse fixed-width legacy cost records |
| `modern/cost_calculator.py` | Calculate weighted average costs |
| `modern/historic_parser.py` | Parse COBOL historical output |
| `modern/expiration_processor.py` | Process expiration records and alerts |
| `modern/batch_runner.py` | Orchestrate the complete modern batch |

## IBM Bob

IBM Bob was used as an AI modernization agent during the project.

Bob was first used to analyze the COBOL program before modifying the repository.

The analysis focused on:

- Business rules
- Input/output files
- Control-break logic
- Weighted-average calculation
- Decimal representation
- Dependencies
- Data flow
- Compatibility risks
- Observable behavior
- Modernization strategy

Bob identified, among other things, the classic COBOL control-break pattern and the `DECIMAL-POINT IS COMMA` configuration used by the legacy program.

The Bob analysis and modernization planning are documented in:

```
docs/evidence/
├── 03-bob-legacy-analysis.md
└── 04-bob-modernization-plan.md
```

Task session evidence is stored in:

`bob_sessions/`

## A real legacy bug discovered during validation

During the initial validation, the COBOL program contained a bug in the historical-output routine.

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

After the fix, the COBOL baseline produced the expected results and the modern implementation could be validated against it.

The complete investigation is documented in:

```
docs/
├── 02-legacy-modern-equivalence.md
└── 03-equivalence-validation.md
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

For `historico.dat`, the current COBOL output contains records with:

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

## Validation

The modern implementation is validated against the actual COBOL output.

Current equivalence result:

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

The full test suite currently reports:

```
19 passed
```

The tests cover:

- Legacy cost equivalence
- Profit/gain equivalence
- Expiration parsing
- Alert record ordering
- Alert counts
- Output overwrite behavior
- `historico.dat` byte-for-byte equivalence
- `alertas.dat` byte-for-byte equivalence
- Complete batch execution
- Output record format

## Running the project

### Requirements

- Python 3
- GnuCOBOL
- pytest

A virtual environment is recommended.

### Run the legacy/modern equivalence test

From the repository root:

```
.venv/bin/python -m tests.test_equivalence
```

Expected result:

```
✓ LEGACY ↔ MODERN EQUIVALENCE PASSED
```

### Run the complete test suite

```
.venv/bin/python -m pytest tests/
```

Expected result:

```
19 passed
```

## Project structure

```
legacy/
└── cobol/
    ├── batchcosto.cob
    ├── costos.dat
    ├── vencimientos.dat
    ├── historico.dat
    └── alertas.dat

modern/
├── legacy_parser.py
├── cost_calculator.py
├── historic_parser.py
├── expiration_processor.py
└── batch_runner.py

tests/
├── test_equivalence.py
└── test_alert_equivalence.py

docs/
├── evidence/
│   ├── 01-decimal-format.md
│   ├── 02-legacy-modern-equivalence.md
│   ├── 03-bob-legacy-analysis.md
│   └── 04-bob-modernization-plan.md
│
├── 01-project-overview.md
├── 02-legacy-baseline.md
└── 03-equivalence-validation.md

bob_sessions/
└── task-04-batch-modernization-summary.png
```

## Modernization principle

LegacyLens follows one central principle:

> Preserve observable legacy behavior before changing the implementation.

The goal is not to make the modern implementation look like the COBOL implementation.

The goal is to understand what the legacy system actually does, reproduce that behavior, and then use automated validation to demonstrate that the modernization did not silently change it.

## Status

**Current MVP: working**

The current prototype demonstrates:

- COBOL behavior analysis
- Legacy business-rule extraction
- Python modernization
- Cost calculation equivalence
- Expiration-alert equivalence
- Byte-for-byte output validation
- Automated regression tests
- IBM Bob-assisted modernization workflow

## Hackathon

Built for the IBM Bob 2.0 Hackathon.

The project uses IBM Bob as part of the legacy analysis and modernization workflow, with task-session evidence maintained in `bob_sessions/`.