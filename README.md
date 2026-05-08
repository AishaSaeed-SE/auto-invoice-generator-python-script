# Invoice Generation Automation

A clean, professional Python tool that reads Excel or CSV invoice data and generates branded PDF invoices automatically.

---

## Features

- Reads `.xlsx` (Excel) and `.csv` input files
- Cleans common data issues automatically
- Generates one professional PDF per invoice
- A4 page, corporate design with navy/blue branding
- Calculates subtotal, tax, and grand total
- Handles version conflicts (`INV_1001_v2.pdf` if file already exists)
- Simple interactive CLI — no config files needed

---

## Requirements

- Python 3.10 or higher

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

You will be prompted to enter:

| Prompt | Example |
|--------|---------|
| Input file path | `data/invoices.xlsx` |
| Output folder | `invoices_output` |
| Company Name | `Acme Corp` |
| Company Address | `123 Main St, New York` |
| Company Email | `billing@acme.com` |
| Company Phone | `+1 (212) 555-0100` |
| Currency Symbol | `$` |
| Tax % | `10` |

---

## Required Columns

Your Excel or CSV file must contain these column headers exactly:

| Column | Description |
|--------|-------------|
| `Invoice_No` | Unique invoice identifier |
| `Invoice_Date` | Date of the invoice |
| `Due_Date` | Payment due date |
| `Customer_Name` | Customer or client name |
| `Customer_Address` | Customer address |
| `Customer_Email` | Customer email |
| `Item_Description` | Product or service description |
| `Qty` | Quantity of items |
| `Unit_Price` | Price per item |

Multiple rows with the same `Invoice_No` are grouped into one invoice PDF with multiple line items.

---

## Data Cleaning (Automatic)

The tool handles these common issues automatically:

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

---

## Tips

- Column headers are case-sensitive. Use the exact names listed above.
- Dates in any common format (DD/MM/YYYY, YYYY-MM-DD, etc.) are accepted.
- Use comma as the thousand separator in numbers — it is handled automatically.
- The currency symbol can be anything: `$`, `€`, `£`, `PKR`, `Rs`, etc.

---

## License

Free to use and modify for personal and commercial projects.
