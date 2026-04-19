"""
Generate a realistic sample lab report PDF for testing.

This creates a PDF that mimics an Indian diagnostic lab report
(similar to Lal PathLabs / Apollo / SRL format).

Run this script to create sample_reports/sample_cbc_report.pdf
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


def create_sample_report(output_path: str = "sample_reports/sample_cbc_report.pdf"):
    """Create a realistic Indian lab report PDF."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "LabTitle",
        parent=styles["Title"],
        fontSize=16,
        textColor=colors.HexColor("#1a5276"),
        spaceAfter=5,
    )
    subtitle_style = ParagraphStyle(
        "LabSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=15,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#2c3e50"),
        spaceBefore=15,
        spaceAfter=8,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.grey,
        spaceBefore=20,
    )

    elements = []

    # ── Lab Header ──────────────────────────────────────────
    elements.append(Paragraph("HealthFirst Diagnostics", title_style))
    elements.append(
        Paragraph(
            "NABL Accredited | ISO 15189:2022 Certified | "
            "Reg. No: DL-2024-LAB-0847<br/>"
            "42, Sector 18, Noida, Uttar Pradesh - 201301 | "
            "Ph: 0120-4567890",
            subtitle_style,
        )
    )

    # ── Patient Info Table ──────────────────────────────────
    patient_data = [
        ["Patient Name:", "Rahul Sharma", "Sample ID:", "HF-2026-04721"],
        ["Age / Gender:", "28 Years / Male", "Report Date:", "04-Apr-2026"],
        ["Referred By:", "Dr. Priya Mehta", "Sample Type:", "EDTA Whole Blood, Serum"],
    ]
    patient_table = Table(patient_data, colWidths=[90, 170, 80, 140])
    patient_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#2c3e50")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(patient_table)
    elements.append(Spacer(1, 10))

    # ── CBC Section ─────────────────────────────────────────
    elements.append(Paragraph("COMPLETE BLOOD COUNT (CBC)", section_style))

    cbc_data = [
        ["Test Name", "Result", "Unit", "Reference Range", "Status"],
        ["Hemoglobin", "11.2", "g/dL", "13.0 - 17.0", "LOW"],
        ["RBC Count", "4.1", "million/cumm", "4.5 - 5.5", "LOW"],
        ["PCV / Hematocrit", "34.5", "%", "40 - 50", "LOW"],
        ["MCV", "84.1", "fL", "83 - 101", "Normal"],
        ["MCH", "27.3", "pg", "27 - 32", "Normal"],
        ["MCHC", "32.5", "g/dL", "31.5 - 34.5", "Normal"],
        ["RDW-CV", "15.8", "%", "11.6 - 14.0", "HIGH"],
        ["Total WBC Count", "7,200", "cells/cumm", "4,000 - 10,000", "Normal"],
        ["Platelet Count", "2,45,000", "cells/cumm", "1,50,000 - 4,10,000", "Normal"],
        ["Neutrophils", "62", "%", "40 - 80", "Normal"],
        ["Lymphocytes", "30", "%", "20 - 40", "Normal"],
        ["Eosinophils", "4", "%", "1 - 6", "Normal"],
        ["Monocytes", "3", "%", "2 - 10", "Normal"],
        ["Basophils", "1", "%", "0 - 2", "Normal"],
        ["ESR", "22", "mm/hr", "0 - 15", "HIGH"],
    ]
    cbc_table = Table(cbc_data, colWidths=[130, 70, 80, 110, 60])
    cbc_table.setStyle(
        TableStyle(
            [
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                # Data rows
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                # Alternating row colors
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fa")]),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(cbc_table)

    # ── Lipid Profile Section ───────────────────────────────
    elements.append(Paragraph("LIPID PROFILE", section_style))

    lipid_data = [
        ["Test Name", "Result", "Unit", "Reference Range", "Status"],
        ["Total Cholesterol", "232", "mg/dL", "< 200", "HIGH"],
        ["Triglycerides", "178", "mg/dL", "< 150", "HIGH"],
        ["HDL Cholesterol", "38", "mg/dL", "> 40", "LOW"],
        ["LDL Cholesterol", "158", "mg/dL", "< 100", "HIGH"],
        ["VLDL Cholesterol", "35.6", "mg/dL", "< 30", "HIGH"],
        ["Total Cholesterol/HDL Ratio", "6.1", "", "< 4.5", "HIGH"],
    ]
    lipid_table = Table(lipid_data, colWidths=[160, 70, 60, 100, 60])
    lipid_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fa")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(lipid_table)

    # ── Blood Sugar Section ─────────────────────────────────
    elements.append(Paragraph("BLOOD SUGAR", section_style))

    sugar_data = [
        ["Test Name", "Result", "Unit", "Reference Range", "Status"],
        ["Fasting Blood Sugar", "118", "mg/dL", "70 - 100", "HIGH"],
        ["HbA1c", "6.4", "%", "< 5.7", "HIGH"],
    ]
    sugar_table = Table(sugar_data, colWidths=[160, 70, 60, 100, 60])
    sugar_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fa")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(sugar_table)

    # ── Thyroid Section ─────────────────────────────────────
    elements.append(Paragraph("THYROID FUNCTION TEST", section_style))

    thyroid_data = [
        ["Test Name", "Result", "Unit", "Reference Range", "Status"],
        ["TSH", "5.8", "mIU/L", "0.4 - 4.0", "HIGH"],
        ["Free T4", "1.1", "ng/dL", "0.8 - 1.8", "Normal"],
        ["Free T3", "2.9", "pg/mL", "2.3 - 4.2", "Normal"],
    ]
    thyroid_table = Table(thyroid_data, colWidths=[160, 70, 60, 100, 60])
    thyroid_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fa")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(thyroid_table)

    # ── Disclaimer ──────────────────────────────────────────
    elements.append(
        Paragraph(
            "* This report is generated for testing purposes only. "
            "Results are fictional and do not represent any real patient. "
            "Always consult your physician for medical interpretation.",
            disclaimer_style,
        )
    )

    # Build PDF
    doc.build(elements)
    print(f"[OK] Sample report created: {output_path}")


if __name__ == "__main__":
    create_sample_report()
