"""
PDF Generation Utilities for WMS
Professional PDF documents using ReportLab
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


# ─── Color Palette ────────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor('#1e40af')   # Deep Blue
SECONDARY = colors.HexColor('#1e293b')   # Dark Slate
ACCENT    = colors.HexColor('#3b82f6')   # Blue
SUCCESS   = colors.HexColor('#16a34a')   # Green
DANGER    = colors.HexColor('#dc2626')   # Red
LIGHT_BG  = colors.HexColor('#f1f5f9')  # Light Gray
MID_GRAY  = colors.HexColor('#64748b')  # Mid Gray
PALE_BLUE = colors.HexColor('#eff6ff')  # Pale Blue
WHITE     = colors.white
BLACK     = colors.black
BORDER    = colors.HexColor('#e2e8f0')  # Light Border


def draw_header(p, width, height, doc_type, doc_id, company="Warehouse Management System"):
    """Draw the professional document header."""
    # Top colored bar
    p.setFillColor(PRIMARY)
    p.rect(0, height - 90, width, 90, fill=True, stroke=False)

    # Company name
    p.setFillColor(WHITE)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(30, height - 38, company)

    # Tagline
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.HexColor('#bfdbfe'))
    p.drawString(30, height - 55, "Integrated Warehouse & Inventory Management")

    # Document Type Badge (right side)
    p.setFillColor(colors.HexColor('#1d4ed8'))
    p.roundRect(width - 185, height - 72, 155, 46, 6, fill=True, stroke=False)
    p.setFillColor(WHITE)
    p.setFont("Helvetica-Bold", 15)
    p.drawCentredString(width - 107, height - 50, doc_type)
    p.setFont("Helvetica", 10)
    p.drawCentredString(width - 107, height - 66, f"# {doc_id}")


def draw_meta_row(p, y, label, value, label_x=30, value_x=150, width=200):
    """Draw a metadata label-value row."""
    p.setFont("Helvetica-Bold", 8)
    p.setFillColor(MID_GRAY)
    p.drawString(label_x, y, label.upper())
    p.setFont("Helvetica", 10)
    p.setFillColor(SECONDARY)
    p.drawString(value_x, y, str(value))


def draw_info_section(p, height, left_data, right_data):
    """Draw two-column info section below header."""
    y_start = height - 100
    box_h = 20 * max(len(left_data), len(right_data)) + 20
    col_w = 255

    # Left box
    p.setFillColor(PALE_BLUE)
    p.roundRect(25, y_start - box_h, col_w, box_h, 4, fill=True, stroke=False)
    p.setStrokeColor(BORDER)
    p.setLineWidth(0.5)
    p.roundRect(25, y_start - box_h, col_w, box_h, 4, fill=False, stroke=True)

    # Right box
    p.setFillColor(PALE_BLUE)
    p.roundRect(295, y_start - box_h, col_w, box_h, 4, fill=True, stroke=False)
    p.roundRect(295, y_start - box_h, col_w, box_h, 4, fill=False, stroke=True)

    # Left data
    y = y_start - 18
    for label, value in left_data:
        p.setFont("Helvetica-Bold", 7.5)
        p.setFillColor(MID_GRAY)
        p.drawString(35, y, label.upper() + ":")
        p.setFont("Helvetica", 9.5)
        p.setFillColor(SECONDARY)
        p.drawString(35, y - 12, str(value)[:38])
        y -= 28

    # Right data
    y = y_start - 18
    for label, value in right_data:
        p.setFont("Helvetica-Bold", 7.5)
        p.setFillColor(MID_GRAY)
        p.drawString(305, y, label.upper() + ":")
        p.setFont("Helvetica", 9.5)
        p.setFillColor(SECONDARY)
        p.drawString(305, y - 12, str(value)[:38])
        y -= 28

    return y_start - box_h - 15  # return next Y position


def draw_items_table(p, items_data, y_start, width):
    """Draw professional items table. Returns final Y position."""
    # Column positions
    cols = [30, 230, 320, 390, 460, 540]  # x positions for: #, Desc, Qty, Unit, Total
    col_labels = ["#", "Product / Description", "Qty", "Unit Price", "Total"]

    # Table header bar
    p.setFillColor(PRIMARY)
    p.rect(25, y_start - 22, width - 50, 22, fill=True, stroke=False)
    p.setFillColor(WHITE)
    p.setFont("Helvetica-Bold", 9)
    for i, label in enumerate(col_labels):
        p.drawString(cols[i], y_start - 14, label)

    # Table rows
    y = y_start - 22
    for idx, (name, qty, unit_price, total_price) in enumerate(items_data):
        row_h = 22
        if y < 80:
            p.showPage()
            y = A4[1] - 50

        # Alternating row background
        if idx % 2 == 0:
            p.setFillColor(colors.HexColor('#f8fafc'))
            p.rect(25, y - row_h, width - 50, row_h, fill=True, stroke=False)

        # Row border
        p.setStrokeColor(BORDER)
        p.setLineWidth(0.3)
        p.line(25, y - row_h, width - 25, y - row_h)

        p.setFillColor(SECONDARY)
        p.setFont("Helvetica-Bold", 8.5)
        p.drawString(cols[0], y - 14, str(idx + 1))
        p.setFont("Helvetica", 9)
        p.drawString(cols[1], y - 14, str(name)[:30])
        p.drawRightString(cols[3] - 5, y - 14, str(qty))
        p.setFont("Helvetica", 9)
        p.drawRightString(cols[4] - 5, y - 14, str(unit_price))
        p.setFillColor(SUCCESS)
        p.setFont("Helvetica-Bold", 9)
        p.drawRightString(cols[5] - 5, y - 14, str(total_price))

        y -= row_h

    return y


def draw_total_section(p, y, grand_total, width, notes=""):
    """Draw the grand total box and notes section."""
    # Notes box (left)
    if notes:
        p.setFillColor(colors.HexColor('#fefce8'))
        p.roundRect(25, y - 55, 280, 50, 4, fill=True, stroke=False)
        p.setStrokeColor(colors.HexColor('#fde68a'))
        p.setLineWidth(0.5)
        p.roundRect(25, y - 55, 280, 50, 4, fill=False, stroke=True)
        p.setFillColor(MID_GRAY)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(35, y - 18, "NOTES:")
        p.setFont("Helvetica", 8.5)
        p.setFillColor(SECONDARY)
        # Wrap long notes text
        note_lines = [notes[i:i+40] for i in range(0, min(len(notes), 120), 40)]
        ny = y - 30
        for line in note_lines:
            p.drawString(35, ny, line)
            ny -= 12

    # Grand total box (right)
    p.setFillColor(PRIMARY)
    p.roundRect(width - 195, y - 55, 165, 50, 4, fill=True, stroke=False)
    p.setFillColor(WHITE)
    p.setFont("Helvetica", 9)
    p.drawCentredString(width - 112, y - 22, "GRAND TOTAL")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width - 112, y - 42, str(grand_total))

    return y - 70


def draw_footer(p, width):
    """Draw the document footer."""
    # Footer bar
    p.setFillColor(LIGHT_BG)
    p.rect(0, 0, width, 35, fill=True, stroke=False)
    p.setFillColor(MID_GRAY)
    p.setFont("Helvetica", 7.5)
    p.drawString(30, 14, "Generated by WMS — Warehouse Management System")
    p.drawRightString(width - 30, 14, "This document is computer generated and does not require a signature.")


def draw_status_badge(p, status, x, y):
    """Draw a colored status badge."""
    status_map = {
        'pending':   (colors.HexColor('#fef3c7'), colors.HexColor('#d97706'), 'PENDING'),
        'completed': (colors.HexColor('#dcfce7'), colors.HexColor('#16a34a'), 'COMPLETED'),
        'cancelled': (colors.HexColor('#fee2e2'), colors.HexColor('#dc2626'), 'CANCELLED'),
        'paid':      (colors.HexColor('#dcfce7'), colors.HexColor('#16a34a'), 'PAID'),
    }
    bg, fg, label = status_map.get(status, (LIGHT_BG, MID_GRAY, status.upper()))
    p.setFillColor(bg)
    p.roundRect(x, y - 4, 72, 16, 4, fill=True, stroke=False)
    p.setFillColor(fg)
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(x + 36, y + 4, label)


# ─── Purchase Order PDF ───────────────────────────────────────────────────────
def generate_purchase_pdf(order):
    """Generate a professional Purchase Order PDF. Returns BytesIO buffer."""
    buffer = BytesIO()
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setTitle(f"Purchase Order PO-{order.id}")

    # Header
    draw_header(p, width, height, "PURCHASE ORDER", f"PO-{order.id:04d}")

    # Info Section
    status_label = dict(order.STATUS_CHOICES).get(order.status, order.status)

    left_data = [
        ("Supplier", order.supplier.name),
        ("Phone", order.supplier.phone or "N/A"),
        ("Email", order.supplier.email or "N/A"),
        ("Address", order.supplier.address[:35] if order.supplier.address else "N/A"),
    ]
    right_data = [
        ("Order Number", f"PO-{order.id:04d}"),
        ("Date", order.created_at.strftime("%Y-%m-%d")),
        ("Warehouse", order.warehouse.name),
        ("Status", status_label),
    ]
    next_y = draw_info_section(p, height, left_data, right_data)

    # Status badge on the right info box
    draw_status_badge(p, order.status, width - 110, next_y + 45)

    # Divider label
    p.setFillColor(ACCENT)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(30, next_y - 5, "ORDER ITEMS")
    p.setStrokeColor(BORDER)
    p.setLineWidth(0.5)
    p.line(120, next_y - 1, width - 30, next_y - 1)

    # Items Table
    items_data = [
        (item.product.name, item.quantity, item.unit_price, item.total_price)
        for item in order.items.all()
    ]
    final_y = draw_items_table(p, items_data, next_y - 15, width)

    # Total & Notes
    draw_total_section(p, final_y - 10, order.total_amount, width, order.notes)

    # Footer
    draw_footer(p, width)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# ─── Sales Invoice PDF ────────────────────────────────────────────────────────
def generate_invoice_pdf(invoice):
    """Generate a professional Sales Invoice PDF. Returns BytesIO buffer."""
    buffer = BytesIO()
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setTitle(f"Invoice INV-{invoice.id}")

    # Header
    draw_header(p, width, height, "SALES INVOICE", f"INV-{invoice.id:04d}")

    # Customer info
    customer_name = invoice.customer.name if invoice.customer else "Cash Customer"
    customer_phone = invoice.customer.phone if invoice.customer else "—"
    customer_email = invoice.customer.email if invoice.customer else "—"
    customer_address = (invoice.customer.address[:35] if invoice.customer and invoice.customer.address else "—")
    status_label = dict(invoice.STATUS_CHOICES).get(invoice.status, invoice.status)

    left_data = [
        ("Customer", customer_name),
        ("Phone", customer_phone),
        ("Email", customer_email),
        ("Address", customer_address),
    ]
    right_data = [
        ("Invoice No.", f"INV-{invoice.id:04d}"),
        ("Date", invoice.created_at.strftime("%Y-%m-%d")),
        ("Warehouse", invoice.warehouse.name),
        ("Status", status_label),
    ]
    next_y = draw_info_section(p, height, left_data, right_data)

    draw_status_badge(p, invoice.status, width - 110, next_y + 45)

    # Divider label
    p.setFillColor(SUCCESS)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(30, next_y - 5, "INVOICE ITEMS")
    p.setStrokeColor(BORDER)
    p.setLineWidth(0.5)
    p.line(125, next_y - 1, width - 30, next_y - 1)

    # Items Table
    items_data = [
        (item.product.name, item.quantity, item.unit_price, item.total_price)
        for item in invoice.items.all()
    ]
    final_y = draw_items_table(p, items_data, next_y - 15, width)

    # Total & Notes
    draw_total_section(p, final_y - 10, invoice.total_amount, width, invoice.notes)

    # Footer
    draw_footer(p, width)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
