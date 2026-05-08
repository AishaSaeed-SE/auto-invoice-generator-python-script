# Invoice Generation Automation

A clean and professional Python automation tool that reads Excel or CSV invoice data and generates branded PDF invoices automatically.

## Features

- Reads `.xlsx` (Excel) and `.csv` input files
- Cleans common data issues automatically
- Generates one professional PDF per invoice
- Calculates subtotal, tax, and grand total
- Handles version conflicts automatically  
  (`INV_1001_v2.pdf` if the file already exists)

## Requirements

- Python 3.10 or higher

## Installation

```bash
pip install -r requirements.txt

## Run the Project

```bash
python main.py

## Automatic Data Cleaning

The script automatically handles common data issues:

- Removes blank rows
- Removes duplicate rows
- Trims extra whitespace
- Missing customer name → `Unknown Customer`
- Missing address/email → `N/A`
- Missing dates → Today's date
- Invalid Qty (e.g. `abc`) → `1`
- Invalid Unit Price (e.g. `xyz`) → `0.00`

### Supported Date Formats

- `DD/MM/YYYY`
- `YYYY-MM-DD`
- `MM/DD/YYYY`
---

## Sample File

A sample CSV file is included:

```bash
sample_data.csv
```

Run the project using this file to generate example invoices.

---

## Project Structure
```bash
auto-invoive-generator-script/
│
├── main.py               # Entry point
├── data_cleaner.py       # Cleans Excel/CSV data
├── invoice_generator.py  # Generates professional PDF invoices
├── utils.py              # Shared helper functions
├── requirements.txt      # Python dependencies
├── sample_data.csv       # Sample invoice data
└── README.md             # Project documentation
```
## Output

Generated PDFs are saved in your selected output folder:

```bash
invoices_output/
├── INV_1001.pdf
├── INV_1002.pdf
├── INV_1003.pdf
```

If a file already exists, the tool automatically creates a new version:

```bash
INV_1001.pdf      # Original file
INV_1001_v2.pdf   # New version
```
