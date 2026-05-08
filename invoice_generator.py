import os
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from utils import get_safe_filename, format_currency


# ── Colour Palette ───
PRIMARY_COLOR   = colors.HexColor("#1B3A6B")   # Dark navy — headers / accents
ACCENT_COLOR    = colors.HexColor("#2E6EBF")   # Mid blue — invoice label
LIGHT_GRAY      = colors.HexColor("#F4F6F9")   # Table row backgrounds
MED_GRAY        = colors.HexColor("#D0D7E3")   # Borders / lines
DARK_GRAY       = colors.HexColor("#4A4A4A")   # Body text
WHITE           = colors.white
BLACK           = colors.black


# ── Helper: build paragraph styles 
def _styles() -> dict:
    return {
        "company_name": ParagraphStyle(
            "company_name",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=PRIMARY_COLOR,
            leading=20,
        ),
        "company_detail": ParagraphStyle(
            "company_detail",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            leading=13,
        ),
        "invoice_label": ParagraphStyle(
            "invoice_label",
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=ACCENT_COLOR,
            alignment=TA_RIGHT,
            leading=34,
        ),
        "invoice_meta_label": ParagraphStyle(
            "invoice_meta_label",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=PRIMARY_COLOR,
            alignment=TA_RIGHT,
            leading=14,
        ),
        "invoice_meta_value": ParagraphStyle(
            "invoice_meta_value",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            alignment=TA_RIGHT,
            leading=14,
        ),
        "section_heading": ParagraphStyle(
            "section_heading",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=PRIMARY_COLOR,
            leading=12,
        ),
        "bill_to_name": ParagraphStyle(
            "bill_to_name",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=DARK_GRAY,
            leading=14,
        ),
        "bill_to_detail": ParagraphStyle(
            "bill_to_detail",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            leading=13,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            leading=13,
        ),
        "table_cell_right": ParagraphStyle(
            "table_cell_right",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            alignment=TA_RIGHT,
            leading=13,
        ),
        "total_label": ParagraphStyle(
            "total_label",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=WHITE,
            alignment=TA_RIGHT,
        ),
        "total_value": ParagraphStyle(
            "total_value",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=WHITE,
            alignment=TA_RIGHT,
        ),
        "subtotal_label": ParagraphStyle(
            "subtotal_label",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            alignment=TA_RIGHT,
        ),
        "subtotal_value": ParagraphStyle(
            "subtotal_value",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            alignment=TA_RIGHT,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=colors.HexColor("#888888"),
            alignment=TA_CENTER,
            leading=13,
        ),
    }


# ── Main PDF builder 
def generate_invoice_pdf(
    invoice_no: str,
    invoice_df: pd.DataFrame,
    company: dict,
    output_folder: str,
) -> str | None:

    # ── Pick invoice meta from the first row
    first_row     = invoice_df.iloc[0]
    invoice_date  = str(first_row.get("Invoice_Date", ""))
    due_date      = str(first_row.get("Due_Date", ""))
    cust_name     = str(first_row.get("Customer_Name", ""))
    cust_address  = str(first_row.get("Customer_Address", ""))
    cust_email    = str(first_row.get("Customer_Email", ""))

    # Currency and Tax come from the data file columns
    currency      = str(first_row.get("Currency", "$")).strip() or "$"
    tax_pct       = float(first_row.get("Tax_Pct", 0))

    file_path = get_safe_filename(output_folder, invoice_no, invoice_date)
    s = _styles()

    # Page margins
    margin = 18 * mm
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    page_w = A4[0] - 2 * margin  # usable width
    story  = []

    # ── HEADER: Company (left) + INVOICE label (right) 
    logo_path = company.get("logo_path", "")
    logo_ok   = bool(logo_path and os.path.isfile(logo_path))

    if logo_ok:
        # Render logo image, capped at 44mm tall to keep header compact
        try:
            logo_img = Image(logo_path)
            # Scale proportionally: max width 60mm, max height 44mm
            max_w, max_h = 60 * mm, 44 * mm
            ratio = min(max_w / logo_img.imageWidth, max_h / logo_img.imageHeight)
            logo_img.drawWidth  = logo_img.imageWidth  * ratio
            logo_img.drawHeight = logo_img.imageHeight * ratio
            company_block = [
                logo_img,
                Spacer(1, 3),
                Paragraph(company.get("address", ""), s["company_detail"]),
                Paragraph(company.get("email", ""), s["company_detail"]),
                Paragraph(company.get("phone", ""), s["company_detail"]),
            ]
        except Exception:
            logo_ok = False  # Fall through to text fallback

    if not logo_ok:
        company_block = [
            Paragraph(company.get("company_name", ""), s["company_name"]),
            Paragraph(company.get("address", ""), s["company_detail"]),
            Paragraph(company.get("email", ""), s["company_detail"]),
            Paragraph(company.get("phone", ""), s["company_detail"]),
        ]

    invoice_block = [
        Paragraph("INVOICE", s["invoice_label"]),
        Spacer(1, 4),
        _meta_row("Invoice No :", f"#{invoice_no}", s),
        _meta_row("Invoice Date:", invoice_date, s),
        _meta_row("Due Date :", due_date, s),
    ]

    header_table = Table(
        [[company_block, invoice_block]],
        colWidths=[page_w * 0.55, page_w * 0.45],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6 * mm))

    # Thin separator line
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR))
    story.append(Spacer(1, 5 * mm))

    # ── BILL TO 
    story.append(Paragraph("BILL TO", s["section_heading"]))
    story.append(Spacer(1, 2))
    story.append(Paragraph(cust_name, s["bill_to_name"]))
    if cust_address and cust_address != "N/A":
        story.append(Paragraph(cust_address, s["bill_to_detail"]))
    if cust_email and cust_email != "N/A":
        story.append(Paragraph(cust_email, s["bill_to_detail"]))
    story.append(Spacer(1, 5 * mm))

    # ── ITEMS TABLE ─
    col_widths = [
        page_w * 0.07,   # Sr #
        page_w * 0.45,   # Description
        page_w * 0.10,   # Qty
        page_w * 0.19,   # Unit Price
        page_w * 0.19,   # Total
    ]

    table_data = [[
        Paragraph("Sr #",        s["table_header"]),
        Paragraph("Description", s["table_header"]),
        Paragraph("Qty",         s["table_header"]),
        Paragraph("Unit Price",  s["table_header"]),
        Paragraph("Total",       s["table_header"]),
    ]]

    subtotal = 0.0

    for idx, (_, row) in enumerate(invoice_df.iterrows(), start=1):
        qty        = float(row.get("Qty", 1))
        unit_price = float(row.get("Unit_Price", 0))
        line_total = qty * unit_price
        subtotal  += line_total

        # Alternate row background
        bg = LIGHT_GRAY if idx % 2 == 0 else WHITE

        table_data.append([
            Paragraph(str(idx), s["table_cell_right"]),
            Paragraph(str(row.get("Item_Description", "")), s["table_cell"]),
            Paragraph(str(int(qty)), s["table_cell_right"]),
            Paragraph(format_currency(currency, unit_price), s["table_cell_right"]),
            Paragraph(format_currency(currency, line_total), s["table_cell_right"]),
        ])

    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Build alternate row style commands
    row_styles = [
        # Header row
        ("BACKGROUND",   (0, 0), (-1, 0),  PRIMARY_COLOR),
        ("TOPPADDING",   (0, 0), (-1, 0),  6),
        ("BOTTOMPADDING",(0, 0), (-1, 0),  6),
        ("ROWBACKGROUND",(0, 1), (-1, -1), WHITE),
        ("GRID",         (0, 0), (-1, -1), 0.5, MED_GRAY),
        ("TOPPADDING",   (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 1), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]

    # Add alternating row backgrounds manually
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            row_styles.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GRAY))

    items_table.setStyle(TableStyle(row_styles))
    story.append(items_table)
    story.append(Spacer(1, 5 * mm))

    # ── TOTALS BLOCK 
    tax_amount  = subtotal * (tax_pct / 100)
    grand_total = subtotal + tax_amount

    # Sub-totals rows (light background)
    subtotal_data = [
        [
            Paragraph("Subtotal:", s["subtotal_label"]),
            Paragraph(format_currency(currency, subtotal), s["subtotal_value"]),
        ],
        [
            Paragraph(f"Tax ({tax_pct:.1f}%):", s["subtotal_label"]),
            Paragraph(format_currency(currency, tax_amount), s["subtotal_value"]),
        ],
    ]

    subtotal_table = Table(
        subtotal_data,
        colWidths=[page_w * 0.75, page_w * 0.25],
    )
    subtotal_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("LINEBELOW",     (0, -1), (-1, -1), 0.5, MED_GRAY),
    ]))
    story.append(subtotal_table)
    story.append(Spacer(1, 2))

    # Grand total row (dark background)
    grand_total_data = [[
        Paragraph("GRAND TOTAL:", s["total_label"]),
        Paragraph(format_currency(currency, grand_total), s["total_value"]),
    ]]

    grand_table = Table(
        grand_total_data,
        colWidths=[page_w * 0.75, page_w * 0.25],
    )
    grand_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PRIMARY_COLOR),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(grand_table)
    story.append(Spacer(1, 10 * mm))

    # ── FOOTER 
    story.append(HRFlowable(width="100%", thickness=0.8, color=MED_GRAY))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Thank you for your business.", s["footer"]))

    # ── BUILD PDF ───
    try:
        doc.build(story)
        return file_path
    except Exception as e:
        print(f"  [Error] Failed to generate invoice #{invoice_no}: {e}")
        return None


def generate_all_invoices(
    df: pd.DataFrame,
    company: dict,
    output_folder: str,
) -> tuple[int, int]:
    
    invoice_groups = df.groupby("Invoice_No", sort=False)
    total    = len(invoice_groups)
    success  = 0
    fail     = 0

    print()
    for invoice_no, group in invoice_groups:
        path = generate_invoice_pdf(
            invoice_no=str(invoice_no),
            invoice_df=group.reset_index(drop=True),
            company=company,
            output_folder=output_folder,
        )
        if path:
            print(f"  [OK]  Invoice #{invoice_no}  →  {os.path.basename(path)}")
            success += 1
        else:
            fail += 1

    return success, fail


# ── Internal helper
def _meta_row(label: str, value: str, s: dict) -> Table:
    
    t = Table(
        [[Paragraph(label, s["invoice_meta_label"]),
          Paragraph(value, s["invoice_meta_value"])]],
        colWidths=["40%", "60%"],
    )
    t.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 2),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t