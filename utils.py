import os
from datetime import date

def get_safe_filename(output_folder: str, invoice_no: str, invoice_date: str = "") -> str:
    # Convert date to a filename-safe format: DD-MM-YYYY
    date_part = _safe_date_for_filename(invoice_date)

    base_name = f"INV_{invoice_no}_{date_part}"
    file_path = os.path.join(output_folder, f"{base_name}.pdf")

    if not os.path.exists(file_path):
        return file_path

    version = 2
    while True:
        versioned_path = os.path.join(output_folder, f"{base_name}_v{version}.pdf")
        if not os.path.exists(versioned_path):
            return versioned_path
        version += 1


def _safe_date_for_filename(date_str: str) -> str:
    import re
    from datetime import date as date_cls

    date_str = str(date_str).strip()

    # Already in DD/MM/YYYY (our internal format after cleaning)
    if re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        return date_str.replace("/", "-")

    # Try common formats
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            from datetime import datetime
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%d-%m-%Y")
        except ValueError:
            pass

    # Fallback to today
    return date_cls.today().strftime("%d-%m-%Y")


def ensure_folder(folder_path: str) -> bool:
    
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"  [Error] Could not create folder '{folder_path}': {e}")
        return False


def today_str() -> str:
    """Returns today's date as a formatted string: DD/MM/YYYY"""
    return date.today().strftime("%d/%m/%Y")


def format_currency(symbol: str, amount: float) -> str:
    """Formats a number as currency string: $ 1,250.00"""
    return f"{symbol} {amount:,.2f}"


def print_separator(char: str = "-", length: int = 55) -> None:
    """Prints a visual separator line."""
    print(char * length)


def print_header(title: str) -> None:
    """Prints a formatted section header."""
    print_separator("=")
    print(f"  {title}")
    print_separator("=")