# Decimal Format Compatibility Test

## Objective

Determine whether the input decimal separator affects the behavior of
the legacy COBOL cost-processing program.

## Legacy Configuration

The COBOL program declares:

`DECIMAL-POINT IS COMMA`

## Test A — Decimal Point

Input values used:

- `150.75`
- `200.00`

The resulting COBOL output did not match the expected business calculation.

## Test B — Decimal Comma

Input values used:

- `150,75`
- `200,00`

The COBOL output produced the expected average cost.

For product `000000001`:

`183.58`

## Finding

The decimal separator is part of the legacy input contract.

A modern implementation must preserve or explicitly normalize this
behavior before comparing results.

## Relevance to LegacyLens

This demonstrates why source-code translation alone is insufficient.

A modernization validator must consider:

- source code behavior
- input representation
- numeric conventions
- output representation
- behavioral equivalence