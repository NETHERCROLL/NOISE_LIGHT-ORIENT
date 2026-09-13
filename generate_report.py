from docx import Document
from docx.shared import Inches, Pt, RGBColor
from datetime import datetime

def build_docx_report(db, freq, surface, material_name, watts, wh_day, savings_fcfa, co2_kg, status_text, mppt_gain, carbon_credits_eur):
    doc = Document()

    # Title & Header
    title = doc.add_heading("NOISE LIGHT v3.0 — Audit Avancé de Piézo-Électrification & ESG", level=0)
    title.runs[0].font.color.rgb = RGBColor(13, 110, 253)
    
    doc.add_paragraph(f"Date de certification : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph("Conforme aux spécifications scientifiques de conversion d'énergie acoustique/vibratoire.")
    doc.add_paragraph("--------------------------------------------------------------------------------")

    # 1. Caractéristiques Multi-Physiques & Énergétiques
    doc.add_heading("1. Caractérisation Multi-Physique & Énergétique", level=1)
    p1 = doc.add_paragraph()
    p1.add_run("• Niveau de Pression Acoustique (SPL) : ").bold = True
    p1.add_run(f"{db} dBA\n")
    p1.add_run("• Fréquence Dominante : ").bold = True
    p1.add_run(f"{freq} Hz\n")
    p1.add_run("• Surface Captante Active : ").bold = True
    p1.add_run(f"{surface} m²\n")
    p1.add_run("• Matériau Piézoélectrique : ").bold = True
    p1.add_run(f"{material_name}\n")
    p1.add_run("• Optimisation d'Impédance (MPPT) : ").bold = True
    p1.add_run(f"Activée (+{mppt_gain:.1f}% de rendement)\n")
    p1.add_run("• Puissance Électrique Maximale : ").bold = True
    p1.add_run(f"{watts*1000:.2f} mW\n")
    p1.add_run("• Production Journalière : ").bold = True
    p1.add_run(f"{wh_day:.2f} Wh/jour")

    # 2. Audit ESG & Crédits Carbone
    doc.add_heading("2. Modélisation Financière & Impact Carbone (Verra / Gold Standard)", level=1)
    p2 = doc.add_paragraph()
    p2.add_run("• Économies Électriques Estimées : ").bold = True
    p2.add_run(f"{savings_fcfa:,.0f} FCFA / mois\n".replace(",", " "))
    p2.add_run("• Émissions de CO2 Évitées : ").bold = True
    p2.add_run(f"{co2_kg:.2f} kg CO2 / mois ({co2_kg*12/1000:.3f} tonnes/an)\n")
    p2.add_run("• Valeur Potentielle des Crédits Carbone : ").bold = True
    p2.add_run(f"{carbon_credits_eur:.2f} € / an")

    # 3. Diagnostic IoT & Maintenance Prédictive
    doc.add_heading("3. Rapport de Maintenance Prédictive IoT & Jumeau Numérique", level=1)
    p3 = doc.add_paragraph()
    p3.add_run("Diagnostic système : ").bold = True
    p3.add_run(f"{status_text}")

    # Footer
    doc.add_paragraph("\n--------------------------------------------------------------------------------")
    footer = doc.add_paragraph("Rapport généré automatiquement par la suite logicielle NOISE LIGHT (Moteur Multi-Physique & IoT).")
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].font.italic = True

    file_path = "Audit_NOISE_LIGHT_v3.docx"
    doc.save(file_path)
    return file_path
