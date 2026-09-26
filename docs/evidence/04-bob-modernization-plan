# IBM Bob — Modernization Plan

## Objective

Define a staged modernization plan for the COBOL batch while preserving
its observable behavior.

## Scope

The modernization focuses on the two flows executed by the legacy
batch:

1. Cost processing
2. Expiration-alert processing

The COBOL source remains unchanged.

## Expiration-alert behavior

Bob identified that paragraph `3000-PROCESAR-ALERTAS` reads
`vencimientos.dat` and copies each `VR-LOTE-ID` directly into
`alertas.dat`.

The relevant record format is:

```
VR-LOTE-ID    PIC X(9)
AR-LOTE-ID    PIC X(9)
```

The COBOL implementation performs no transformation on the value.
The modern implementation therefore needs to preserve:

- 9-character record width
- record ordering
- newline-terminated output
- byte-compatible alert records
- number of records written

## Proposed Python components

### `modern/expiration_processor.py`

Responsible for:

- parsing `vencimientos.dat`
- validating the 9-character record format
- writing `alertas.dat`
- returning the number of alerts written

### `modern/batch_runner.py`

Responsible for orchestrating:

```
costos.dat
    ↓
legacy_parser
    ↓
cost_calculator
    ↓
historico.dat

vencimientos.dat
    ↓
expiration_processor
    ↓
alertas.dat
```

The runner will expose a single modern batch entry point.

## Validation strategy

The modernization will be validated against the existing COBOL
outputs.

The tests will verify:

1. Expiration records are parsed correctly.
2. `alertas.dat` matches the COBOL output byte-for-byte.
3. The alert count matches the COBOL count.
4. The modern batch produces the expected historical cost output.
5. The modern batch produces the expected alert output.
6. The complete batch returns the expected counts.

Expected fixture:

```
Input cost records: 10
Products processed: 5
Expiration records: 3
```

Expected counts:

```
COSTOS PROMEDIO ACTUALIZADOS: 0005
ALERTAS DE VENCIMIENTO: 0003
```

## Modernization principle

- The implementation follows the project's core principle:

> Preserve observable legacy behavior before changing the implementation.

- No COBOL files will be modified during this modernization stage.