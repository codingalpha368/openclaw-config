# Water Bill Splitter

Finnish/English water bill calculator for shared housing.

## What it does

Splits water bills between two parties (A and B) where:
- **Basic fees** are split 50/50
- **Water & wastewater** are split by consumption percentage

## Usage

```bash
python3 water_bill.py
```

Edit the values at the bottom of the file for each bill:
- Meter readings (current and previous for A and B)
- Bill amounts from the invoice

## Example Output

```
==================================================
VESILASKUN JAKO / WATER BILL SPLIT
==================================================

Kulutus / Consumption:
  A: 15 m³ (39.5%)
  B: 23 m³ (60.5%)
  Yht: 38 m³

Perusmaksut (50/50) / Basic Fees:
  A: 21.58 €
  B: 21.58 €

Vesi (kulutuksen mukaan) / Water:
  A: 36.58 €
  B: 56.04 €

Jätevesi (kulutuksen mukaan) / Wastewater:
  A: 62.44 €
  B: 95.69 €

==================================================
YHTENSÄ / TOTAL:
  A: 120.60 €
  B: 173.31 €
==================================================
```

## Files

- `water_bill.py` - Main calculator
- `AGENT.md` - Instructions for AI agent
- `README.md` - This file