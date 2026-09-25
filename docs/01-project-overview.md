# LegacyLens — Project Overview

## Purpose

LegacyLens is a modernization verification prototype.

Its purpose is to verify whether a modern implementation preserves the observable business behavior of a legacy COBOL program.

The project focuses on behavior equivalence rather than simple source-code translation.

## Core Flow

Legacy COBOL
→ Analyze behavior
→ Extract business rules
→ Modern implementation
→ Execute with equivalent input
→ Compare results
→ Generate validation report

## Current MVP

The first use case is the cost calculation process implemented in `batchcosto.cob`.

The COBOL program calculates a weighted average cost per product and processes expiration alerts.

## Technology

- COBOL / GnuCOBOL
- Python
- Git / GitHub
- IBM Bob