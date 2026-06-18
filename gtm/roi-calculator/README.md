# EDU AI Suite — ROI/TCO Calculator

Generates a formatted Excel workbook (`EDU-AI-Suite-ROI-Calculator.xlsx`) for use in customer conversations.

## Setup

```bash
pip install openpyxl
python generate_roi_calculator.py
```

## What It Produces

A 5-sheet Excel workbook:

| Sheet | Purpose |
|---|---|
| **Instructions** | Color legend and how-to guide |
| **Institution Profile** | Input your institution's enrollment, staffing, costs, and baseline volumes |
| **Agent ROI** | Toggle each agent on/off; adjust volume and deflection-rate assumptions; see monthly labor savings |
| **AWS TCO** | Monthly AWS cost model — Bedrock inference (Sonnet + Haiku), AgentCore, DynamoDB, S3, Lambda, supporting services |
| **Summary Dashboard** | Total investment, annual value, ROI %, payback period, 3-year NPV, and a bar chart |

## Color Legend

- **Green** — input cells (enter your numbers)
- **Blue** — calculated cells (formula-driven)
- **Orange** — assumption cells (pre-filled with reference data; adjust as needed)

## Notes

- Bedrock inference rates reflect approximate list prices as of mid-2025. Verify at aws.amazon.com/pricing before presenting to a customer.
- All ROI numbers are illustrative. The pilot measures actual outcomes against an institution-specific baseline.
- The `Agent ROI` sheet references `Institution Profile` for staff cost and handling time — fill in Institution Profile first.
