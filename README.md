## Invoice Generation Automation
A clean, professional Python tool that reads Excel or CSV invoice data and generates branded PDF invoices automatically.

## Features
- Reads `.xlsx` (Excel) and `.csv` input files
- Cleans common data issues automatically
- Generates one professional PDF per invoice
- Calculates subtotal, tax, and grand total
- Handles version conflicts (`INV_1001_v2.pdf` if file already exists)

## Requirements
- Python 3.10 or higher

## Installation
```bash
pip install -r requirements.txt

## Run 

```bash
python main.py
---

## Data Cleaning (Automatic)

These common issues will be handled automatically:

- Blank rows → removed
- Duplicate rows → removed
- Extra whitespace → trimmed
- Missing customer name → `Unknown Customer`
- Missing address/email → `N/A`
- Missing dates → today's date
- Invalid Qty (e.g. `abc`) → `1`
- Invalid Unit Price (e.g. `xyz`) → `0.00`
- Supported date formats: `DD/MM/YYYY`, `YYYY-MM-DD`, `MM/DD/YYYY`, and more

---

## Sample File

A sample CSV is included: `sample_data.csv`

Run the tool with it to see example invoices generated.

---

## Project Structure

```
invoice_automation/
├── main.py               # Entry point — collects inputs, orchestrates workflow
├── data_cleaner.py       # Loads and cleans Excel/CSV data
├── invoice_generator.py  # Builds professional PDF invoices via ReportLab
├── utils.py              # Shared helpers (file naming, formatting, etc.)
├── requirements.txt      # Python dependencies
├── sample_data.csv       # Sample invoice data for testing
└── README.md             # This file
```

---

## Output

PDFs are saved to your chosen output folder:

```
invoices_output/
├── INV_1001.pdf
├── INV_1002.pdf
├── INV_1003.pdf
```

If a file already exists:

```
INV_1001.pdf      ← original
INV_1001_v2.pdf   ← on next run
```

