# Equivalence Validation

## Objective

Verify that the modern implementation reproduces the behavior of the legacy COBOL cost calculation.

## Legacy Result

The COBOL baseline produces the following average costs:

| Product | COBOL |
|---|---:|
| 000000001 | 183.58 |
| 000000002 | 115.00 |
| 000000003 | 93.20 |
| 000000004 | 50.00 |
| 000000005 | 325.00 |

## Modern Result

The Python implementation produces the same values.

## Validation Result

```text
LEGACY/MODERN EQUIVALENCE PASSED

000000001: COBOL=183.58 MODERN=183.58
000000002: COBOL=115.00 MODERN=115.00
000000003: COBOL=93.20 MODERN=93.20
000000004: COBOL=50.00 MODERN=50.00
000000005: COBOL=325.00 MODERN=325.00