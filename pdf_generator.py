from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import uuid, os
from textwrap import wrap

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 40
RIGHT_MARGIN = 40
TOP_MARGIN = PAGE_HEIGHT - 40
BOTTOM_MARGIN = 40
MAX_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def draw_paragraph(c, text, y, font="Times-Roman", size=10, leading=14):
    """
    Draw wrapped paragraph safely and return updated Y position
    """
    c.setFont(font, size)
    text_obj = c.beginText(LEFT_MARGIN, y)

    max_chars = int(MAX_WIDTH / (size * 0.55))

    for line in text.split("\n"):
        wrapped = wrap(line, max_chars) or [""]
        for w in wrapped:
            if text_obj.getY() < BOTTOM_MARGIN:
                c.drawText(text_obj)
                c.showPage()
                c.setFont(font, size)
                text_obj = c.beginText(LEFT_MARGIN, TOP_MARGIN)
            text_obj.textLine(w)

    c.drawText(text_obj)
    return text_obj.getY() - leading


def generate_pdf(fir):
    os.makedirs("generated_fir", exist_ok=True)

    file_id = uuid.uuid4().hex[:10]
    filename = f"FIR_{file_id}.pdf"
    path = f"generated_fir/{filename}"

    c = canvas.Canvas(path, pagesize=A4)
    y = TOP_MARGIN

    c.setFont("Times-Bold", 14)
    c.drawCentredString(PAGE_WIDTH / 2, y, "Rajasthan Police")
    y -= 25

    c.setFont("Times-Roman", 10)
    c.drawString(LEFT_MARGIN, y, f"LR No: {file_id}/2025")
    c.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, y,
                      f"Date: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}")
    y -= 30

    c.setFont("Times-Bold", 11)
    c.drawString(LEFT_MARGIN, y, "1. Complainant's Details")
    y -= 18

    y = draw_paragraph(
        c,
        f"{fir.get('name','')}\n{fir.get('address','')}",
        y
    )

    c.setFont("Times-Bold", 11)
    c.drawString(LEFT_MARGIN, y, "2. Occurrence Details")
    y -= 18

    y = draw_paragraph(
        c,
        f"a. Date & Time of Report: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}\n"
        f"b. Date & Time of Incident: {fir.get('incident_date','N/A')}\n"
        f"c. Place of loss: {fir.get('place','N/A')}",
        y
    )

    c.setFont("Times-Bold", 11)
    c.drawString(LEFT_MARGIN, y, "3. Lost Articles / Crime Details")
    y -= 18

    y = draw_paragraph(
        c,
        f"1. {fir.get('crime_type','')}",
        y
    )
    
    c.setFont("Times-Bold", 11)
    c.drawString(LEFT_MARGIN, y, "4. Any Other Details")
    y -= 18

    y = draw_paragraph(
        c,
        fir.get("fir_text", ""),
        y
    )

    c.setFont("Times-Bold", 10)
    c.drawString(LEFT_MARGIN, y, "Notes:")
    y -= 15

    y = draw_paragraph(
        c,
        "(i) It is a digitally generated acknowledgement and does not require signature.\n"
        "(ii) Authority issuing duplicate document/article may obtain proof of identity.",
        y,
        size=9
    )

    c.setFont("Times-Bold", 10)
    c.drawString(LEFT_MARGIN, y, "Disclaimers:")
    y -= 15

    y = draw_paragraph(
        c,
        "(i) This report is generated for assistance purposes only.\n"
        "(ii) False reporting is a punishable offence.",
        y,
        size=9
    )

    if y < 120:
        c.showPage()
        y = TOP_MARGIN

    c.setFont("Times-Bold", 11)
    c.drawCentredString(PAGE_WIDTH / 2, y, "INFORMATION REPORT")
    y -= 16
    c.drawCentredString(PAGE_WIDTH / 2, y, f"SO No: {file_id}/2025 Rajasthan Police")

    c.save()
    return path
