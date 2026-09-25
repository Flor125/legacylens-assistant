# Legacy Baseline

## COBOL Program

File:

`legacy/cobol/batchcosto.cob`

The program processes two inputs:

- `costos.dat`
- `vencimientos.dat`

## Cost Input Layout

Each `costos.dat` record has 35 characters:

| Field | COBOL PIC | Description |
|---|---|---|
| CR-PRODUCTO-ID | X(9) | Product identifier |
| CR-PORC-GANANCIA | X(6) | Profit percentage |
| CR-CANTIDAD | X(9) | Quantity |
| CR-PRECIOCOSTO | X(11) | Unit cost |

## Business Rule

The program calculates the weighted average cost:

    total cost value
    ----------------
    total quantity

Where:

    total cost value = sum(quantity × cost)

## Test Dataset

The current fixture contains five products.

Expected average costs:

| Product | Average cost |
|---|---:|
| 000000001 | 183.58 |
| 000000002 | 115.00 |
| 000000003 | 93.20 |
| 000000004 | 50.00 |
| 000000005 | 325.00 |

## Expiration Alerts

The current fixture contains three expiration records:

- 000000001
- 000000003
- 000000005

The COBOL execution reports:

- 5 costs processed
- 3 expiration alerts processed