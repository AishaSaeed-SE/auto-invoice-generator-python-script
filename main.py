
import os
import company_config as cfg
from utils import print_header, print_separator, ensure_folder
from data_cleaner import load_file, check_required_columns, clean_data, print_cleaning_summary
from invoice_generator import generate_all_invoices


def collect_inputs() -> dict:
    print_header("Invoice Generation Automation")

    # Show loaded company so user can confirm at a glance
    print(f"  Company  : {cfg.COMPANY_NAME}")
    print(f"  Email    : {cfg.COMPANY_EMAIL}")
    print(f"  Phone    : {cfg.COMPANY_PHONE}")
    print()

    def ask(prompt: str, default: str = "") -> str:
        display = f"  {prompt}"
        if default:
            display += f" [{default}]"
        display += " : "
        value = input(display).strip().strip('"').strip("'")
        return value if value else default

    print_separator()
    print("  FILE SETTINGS")
    print_separator()

    inputs = {}
    inputs["input_file"]    = ask("Input file path (.xlsx or .csv)")
    inputs["output_folder"] = ask("Output folder path", cfg.OUTPUT_FOLDER)

    return inputs


def main() -> None:
    # ── Step 1: Collect file paths from user 
    inputs = collect_inputs()

    # ── Step 2: Load the data file 
    print()
    print_separator()
    print("  LOADING DATA FILE")
    print_separator()

    df = load_file(inputs["input_file"])
    if df is None:
        print("\n  Exiting. Please fix the file issue and try again.")
        return

    # ── Step 3: Validate columns
    if not check_required_columns(df):
        print("\n  Exiting. Please add the missing columns to your file.")
        return

    # ── Step 4: Clean data  
    print()
    print_separator()
    print("  CLEANING DATA")
    print_separator()

    df_clean, summary = clean_data(df)
    print_cleaning_summary(summary)

    if len(df_clean) == 0:
        print("\n  No data remaining after cleaning. Nothing to generate.")
        return

    # ── Step 5: Create output folder 
    if not ensure_folder(inputs["output_folder"]):
        print("\n  Exiting. Could not create output folder.")
        return

    # ── Step 6: Generate invoices
    print()
    print_separator()
    print("  GENERATING INVOICES")
    print_separator()

    # Company details come entirely from company_config.py
    company = {
        "company_name": cfg.COMPANY_NAME,
        "address":      cfg.COMPANY_ADDRESS,
        "email":        cfg.COMPANY_EMAIL,
        "phone":        cfg.COMPANY_PHONE,
        "logo_path":    cfg.COMPANY_LOGO,
    }

    # Warn early if logo path is set but the file doesn't exist
    if cfg.COMPANY_LOGO and not os.path.isfile(cfg.COMPANY_LOGO):
        print(f"  [Warning] Logo file not found: '{cfg.COMPANY_LOGO}'")
        print("  Company name will be used as text instead.")
        print("  To fix: place your logo file in the project folder and")
        print("  update COMPANY_LOGO in company_config.py.")
        print()

    success, fail = generate_all_invoices(
        df=df_clean,
        company=company,
        output_folder=inputs["output_folder"],
    )

    # ── Step 7: Final summary───
    print()
    print_separator("=")
    print("  DONE")
    print_separator("=")
    print(f"  Invoices Generated : {success}")
    if fail:
        print(f"  Invoices Failed    : {fail}")
    print(f"  Saved To           : {inputs['output_folder']}")
    print_separator("=")
    print()


if __name__ == "__main__":
    main()