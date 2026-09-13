import os
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_docx_report(db, freq, surface, material_name, watts, wh_day, savings_fcfa, co2_kg, status_text, mppt_gain, carbon_credits_eur):
    doc = Document()

    title = doc.add_heading("NOISE LIGHT — Rapport d'Audit Énergétique & ESG", level=0)
    title.runs[0].font.color.rgb = RGBColor(13, 110, 253)
    
    doc.add_paragraph(f"Date du rapport : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph("--------------------------------------------------------------------------------")

    doc.add_heading("1. Spécifications & Paramètres Entrées", level=1)
    p1 = doc.add_paragraph()
    p1.add_run("• Niveau Sonore (SPL) : ").bold = True
    p1.add_run(f"{db} dBA\n")
    p1.add_run("• Fréquence Dominante : ").bold = True
    p1.add_run(f"{freq} Hz\n")
    p1.add_run("• Surface Captante Active : ").bold = True
    p1.add_run(f"{surface} m²\n")
    p1.add_run("• Matériau Piézoélectrique : ").bold = True
    p1.add_run(f"{material_name}\n")
    p1.add_run("• Optimisation MPPT : ").bold = True
    p1.add_run(f"+{mppt_gain:.1f}% de gain d'impédance\n")

    doc.add_heading("2. Résultats d'Énergie & Impact Financier", level=1)
    p2 = doc.add_paragraph()
    p2.add_run("• Puissance Générée Instantanée : ").bold = True
    p2.add_run(f"{watts*1000:.2f} mW\n")
    p2.add_run("• Production Journalière : ").bold = True
    p2.add_run(f"{wh_day:.2f} Wh/jour\n")
    p2.add_run("• Économies Estimées : ").bold = True
    p2.add_run(f"{savings_fcfa:,.0f} FCFA / mois\n".replace(",", " "))
    p2.add_run("• Émissions de CO2 Évitées : ").bold = True
    p2.add_run(f"{co2_kg:.2f} kg CO2 / mois ({co2_kg*12/1000:.3f} tonnes/an)\n")
    p2.add_run("• Crédits Carbone Monétisables : ").bold = True
    p2.add_run(f"{carbon_credits_eur:.2f} € / an")

    doc.add_heading("3. Diagnostic IoT & Diagnostic Technique", level=1)
    p3 = doc.add_paragraph()
    p3.add_run("Statut global du système : ").bold = True
    p3.add_run(f"{status_text}")

    file_path = "Audit_NOISE_LIGHT.docx"
    doc.save(file_path)
    return file_path


def build_pdf_report(db, freq, surface, material_name, watts, wh_day, savings_fcfa, co2_kg, status_text, mppt_gain, carbon_credits_eur):
    file_path = "Audit_NOISE_LIGHT.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=12
    )
    
    story.append(Paragraph("NOISE LIGHT — Rapport d'Audit Synthétique PDF", title_style))
    story.append(Paragraph(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))

    data = [
        ["Paramètre / Métrique", "Valeur Mesurée / Calculée"],
        ["Pression Acoustique (dBA)", f"{db} dBA"],
        ["Fréquence (Hz)", f"{freq} Hz"],
        ["Surface Captante", f"{surface} m²"],
        ["Matériau Piézoélectrique", material_name],
        ["Puissance Générée", f"{watts*1000:.2f} mW"],
        ["Production / Jour", f"{wh_day:.2f} Wh/jour"],
        ["Économies Mensuelles", f"{savings_fcfa:,.0f} FCFA".replace(",", " ")],
        ["Réduction CO2", f"{co2_kg:.2f} kg CO2 / mois"],
        ["Crédits Carbone ESG", f"{carbon_credits_eur:.2f} € / an"],
        ["Statut Diagnostic", status_text]
    ]

    t = Table(data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    story.append(t)
    doc.build(story)
    return file_path
