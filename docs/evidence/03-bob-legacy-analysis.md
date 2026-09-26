# IBM Bob — Legacy COBOL Analysis

## Objective

Use IBM Bob to analyze the legacy COBOL component before performing
modernization.

## Bob task

Bob was instructed to analyze:

`legacy/cobol/batchcosto.cob`

without modifying repository files.

The analysis requested:

- business rules
- input/output files
- control-break logic
- weighted-average calculation
- decimal representation
- dependencies and data flow
- modernization risks
- observable behavior
- modernization plan

## Key findings

Bob identified the following characteristics:

### Business rules

The program groups cost records by `PRODUCTO-ID` and calculates a
weighted average cost:

```
Σ(price × quantity) / Σ(quantity)
```

- The profit percentage is carried from the first lot in each product
  group rather than averaged.
- Expiration records from `vencimientos.dat` are copied to
  `alertas.dat`.

### Legacy interface

The program uses fixed-width LINE SEQUENTIAL files.

`costos.dat`:

```
PRODUCTO-ID      9 characters
PORC-GANANCIA    6 characters
CANTIDAD         9 characters
PRECIO-COSTO    11 characters
```

The total record width is 35 characters.

### Control-break

Bob identified the classic COBOL priming-read/control-break pattern:

```
Read first record
      ↓
Set previous PRODUCTO-ID
      ↓
Read next record
      ↓
PRODUCTO-ID changed?
   ↙          ↘
 yes           no
 ↓             ↓
flush group   accumulate
 ↓
reset totals
 ↓
continue
```

- The final group is explicitly flushed at EOF.
- The input must therefore be ordered by `PRODUCTO-ID`.

### Decimal representation

Bob identified:

```
SPECIAL-NAMES.
    DECIMAL-POINT IS COMMA.
```

Therefore the legacy data uses comma decimal notation such as:

```
150,75
25,50
```

This is an important compatibility requirement for modernization.

### Dependencies

- The analyzed component has no SQL, COPY books, CALL statements,
  or external modules.
- Its primary runtime dependencies are the input/output files:

```
costos.dat
vencimientos.dat
    ↓
BATCHCOSTOS
    ↓
historico.dat
alertas.dat
```

### Modernization risks

Bob identified several compatibility risks:

1. Decimal separator handling.
2. Fixed-width positional parsing.
3. Input ordering/control-break assumptions.
4. Rounding behavior.
5. Output field widths.
6. First-record semantics for `PORC-GANANCIA`.
7. Zero-quantity handling.
8. Legacy return-code behavior.

### Validation against the project baseline

- The Bob analysis is consistent with the manually verified behavior
  implemented in the project.
- The project already contains a reproducible legacy-modern
  equivalence test comparing the actual COBOL output with the Python
  implementation.

Current result:

```
✓ LEGACY ↔ MODERN EQUIVALENCE PASSED
Input records: 10
Products compared: 5

000000001: COBOL=183.58 MODERN=183.58
000000002: COBOL=115.00 MODERN=115.00
000000003: COBOL=93.20 MODERN=93.20
000000004: COBOL=50.00 MODERN=50.00
000000005: COBOL=325.00 MODERN=325.00
```

### Bob modernization recommendation

Bob proposed a staged modernization:

```
Interface contract
        ↓
Core algorithm
        ↓
I/O layer
        ↓
Error handling
        ↓
Validation / acceptance tests
```

This supports the project's central approach:

> Preserve observable legacy behavior before changing the implementation.

### IBM Bob contribution

- IBM Bob was used as an AI coding/modernization agent to reverse
  engineer the legacy component and identify its business rules,
  dependencies, compatibility constraints, and modernization risks
  before implementation.
- No repository files were modified during this analysis task.