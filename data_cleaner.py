import pandas as pd
from datetime import date


# Required columns for invoice generation
REQUIRED_COLUMNS = [
    "Invoice_No", "Invoice_Date", "Due_Date",
    "Customer_Name", "Customer_Address", "Customer_Email",
    "Item_Description", "Qty", "Unit_Price",
    "Currency", "Tax_Pct"
]


def load_file(file_path: str) -> pd.DataFrame | None:
    # Strip whitespace and surrounding quotes (common when pasting paths on Windows)
    file_path = file_path.strip().strip('"').strip("'")

    try:
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path, dtype=str)
        elif file_path.lower().endswith(".xlsx"):
            df = pd.read_excel(file_path, dtype=str)
        else:
            print("  [Error] Unsupported file type. Please provide a .xlsx or .csv file.")
            return None

        print(f"  File loaded successfully: {len(df)} rows found.")
        return df

    except FileNotFoundError:
        print(f"  [Error] File not found: '{file_path}'")
        return None
    except Exception as e:
        print(f"  [Error] Could not read file: {e}")
        return None


def check_required_columns(df: pd.DataFrame) -> bool:
  
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print(f"\n  [Error] Missing columns: {', '.join(missing)}")
        print("  Please check your file and ensure all required columns are present.")
        return False
    return True


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:

    today = date.today().strftime("%d/%m/%Y")
    summary = {
        "rows_read": len(df),
        "blank_rows_removed": 0,
        "duplicates_removed": 0,
        "invalid_qty_fixed": 0,
        "invalid_price_fixed": 0,
        "invalid_tax_fixed": 0,
        "invalid_dates_fixed": 0,
    }

    # ── 1. Remove fully blank rows ────────────────────────────────────────────
    before = len(df)
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)
    summary["blank_rows_removed"] = before - len(df)

    # ── 2. Remove exact duplicate rows ───────────────────────────────────────
    before = len(df)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    summary["duplicates_removed"] = before - len(df)

    # ── 3. Trim extra spaces from all string columns ──────────────────────────
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        # Replace 'nan' strings (from dtype=str conversion) with empty string
        df[col] = df[col].replace("nan", "")

    # ── 4. Fill missing values with sensible defaults ─────────────────────────
    df["Customer_Name"]    = df["Customer_Name"].replace("", "Unknown Customer")
    df["Customer_Address"] = df["Customer_Address"].replace("", "N/A")
    df["Customer_Email"]   = df["Customer_Email"].replace("", "N/A")
    df["Item_Description"] = df["Item_Description"].replace("", "Item")
    df["Invoice_No"]       = df["Invoice_No"].replace("", "0000")

    # ── 5. Fix Invoice_Date and Due_Date ──────────────────────────────────────
    df["Invoice_Date"] = df["Invoice_Date"].apply(lambda x: _safe_date(x, today))
    df["Due_Date"]     = df["Due_Date"].apply(lambda x: _safe_date(x, today))

    # ── 6. Convert Qty to numeric ─────────────────────────────────────────────
    original_qty = df["Qty"].copy()
    qty_result = df["Qty"].apply(_safe_int)
    summary["invalid_qty_fixed"] = int(((qty_result == 1) & (original_qty != "1") & (original_qty != "")).sum())
    df["Qty"] = qty_result

    # ── 7. Convert Unit_Price to numeric ──────────────────────────────────────
    original_price = df["Unit_Price"].copy()
    price_result = df["Unit_Price"].apply(_safe_float)
    summary["invalid_price_fixed"] = int(((price_result == 0.0) & (original_price != "0") & (original_price != "0.0") & (original_price != "")).sum())
    df["Unit_Price"] = price_result

    # ── 8. Fill missing Currency with default symbol ──────────────────────────
    df["Currency"] = df["Currency"].replace("", "$")

    # ── 9. Convert Tax_Pct to numeric, default 0 ─────────────────────────────
    original_tax = df["Tax_Pct"].copy()
    tax_result = df["Tax_Pct"].apply(_safe_float)
    summary["invalid_tax_fixed"] = int(((tax_result == 0.0) & (original_tax != "0") & (original_tax != "0.0") & (original_tax != "")).sum())
    df["Tax_Pct"] = tax_result

    # ── Final count ───────────────────────────────────────────────────────────
    summary["ready_invoices"] = df["Invoice_No"].nunique()

    return df, summary


def _safe_date(value: str, fallback: str) -> str:

    if not value or value.strip() == "":
        return fallback

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            parsed = pd.to_datetime(value, format=fmt)
            return parsed.strftime("%d/%m/%Y")
        except Exception:
            pass

    # Last attempt: let pandas guess
    try:
        parsed = pd.to_datetime(value, dayfirst=True)
        return parsed.strftime("%d/%m/%Y")
    except Exception:
        return fallback


def _safe_int(value: str) -> int:
    try:
        return max(1, int(float(str(value).replace(",", "").strip())))
    except (ValueError, TypeError):
        return 1


def _safe_float(value: str) -> float:
    
    try:
        return max(0.0, float(str(value).replace(",", "").strip()))
    except (ValueError, TypeError):
        return 0.0


def print_cleaning_summary(summary: dict) -> None:
    """Prints a formatted cleaning summary report."""
    print()
    print("  ── Data Cleaning Summary ──────────────────────────")
    print(f"  Rows Read             : {summary['rows_read']}")
    print(f"  Blank Rows Removed    : {summary['blank_rows_removed']}")
    print(f"  Duplicates Removed    : {summary['duplicates_removed']}")
    print(f"  Invalid Qty Fixed     : {summary['invalid_qty_fixed']}")
    print(f"  Invalid Price Fixed   : {summary['invalid_price_fixed']}")
    print(f"  Invalid Tax % Fixed   : {summary['invalid_tax_fixed']}")
    print(f"  Ready Invoices        : {summary['ready_invoices']}")
    print("  ───────────────────────────────────────────────────")