from docx import Document
from docx.shared import Inches, Pt, RGBColor
from datetime import datetime

def build_docx_report(admin_data, acoustic_data, piezo_data, financial_data, status_text):
    doc = Document()

    # Titre principal
    title = doc.add_heading("NOISE LIGHT Pro — Certification & Audit Piézoélectrique Global", level=0)
    title.runs[0].font.color.rgb = RGBColor(13, 110, 253)
    
    doc.add_paragraph(f"Date de l'Audit : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
    doc.add_paragraph("--------------------------------------------------------------------------------")

    # 1. Cadre Administratif
    doc.add_heading("1. Informations Administratives & Périmètre", level=1)
    p_admin = doc.add_paragraph()
    p_admin.add_run("• Organisme / Client : ").bold = True
    p_admin.add_run(f"{admin_data.get('client_name', 'N/A')}\n")
    p_admin.add_run("• Code Projet : ").bold = True
    p_admin.add_run(f"{admin_data.get('project_id', 'N/A')}\n")
    p_admin.add_run("• Expert Auditeur : ").bold = True
    p_admin.add_run(f"{admin_data.get('auditor_name', 'N/A')}\n")
    p_admin.add_run("• Site d'Analyse : ").bold = True
    p_admin.add_run(f"{admin_data.get('site_desc', 'N/A')}\n")
    p_admin.add_run("• Positionnement GPS : ").bold = True
    p_admin.add_run(f"Lat {acoustic_data.get('lat', 0.0):.5f}, Lng {acoustic_data.get('lng', 0.0):.5f}")

    # 2. Paramètres Physiques et Électroniques
    doc.add_heading("2. Configuration Technique & Métrologie Acoustique", level=1)
    p_phys = doc.add_paragraph()
    p_phys.add_run("• Niveau Sonore : ").bold = True
    p_phys.add_run(f"{acoustic_data.get('db')} dBA\n")
    p_phys.add_run("• Fréquence Dominante (FFT) : ").bold = True
    p_phys.add_run(f"{acoustic_data.get('freq')} Hz\n")
    p_phys.add_run("• Surface Déployée : ").bold = True
    p_phys.add_run(f"{acoustic_data.get('surface')} m²\n")
    p_phys.add_run("• Matériau Sélectionné : ").bold = True
    p_phys.add_run(f"{piezo_data.get('material_name')}\n")
    p_phys.add_run("• Coefficient d33 : ").bold = True
    p_phys.add_run(f"{piezo_data.get('d33')} pC/N | ")
    p_phys.add_run("Rendement (η) : ").bold = True
    p_phys.add_run(f"{piezo_data.get('eta')*100:.1f} %")

    # 3. Métriques Énergétiques, Financières et ESG
    doc.add_heading("3. Bilans Énergétique, CAPEX/OPEX & Impact ESG", level=1)
    p_e = doc.add_paragraph()
    p_e.add_run("• Puissance Électrique Utile : ").bold = True
    p_e.add_run(f"{financial_data.get('p_mw'):.2f} mW\n")
    p_e.add_run("• Production Journalière : ").bold = True
    p_e.add_run(f"{financial_data.get('e_wh_day'):.2f} Wh/jour\n")
    p_e.add_run("• Économies Électriques Mensuelles : ").bold = True
    p_e.add_run(f"{financial_data.get('savings_fcfa'):,.0f} FCFA / mois\n".replace(",", " "))
    p_e.add_run("• CAPEX d'Installation Estimé : ").bold = True
    p_e.add_run(f"{financial_data.get('capex', 0):,.0f} FCFA\n".replace(",", " "))
    p_e.add_run("• Temps de Retour sur Investissement (ROI) : ").bold = True
    p_e.add_run(f"{financial_data.get('roi', 0):.1f} mois\n")
    p_e.add_run("• Déduction Carbone Certifiée : ").bold = True
    p_e.add_run(f"{financial_data.get('co2_kg'):.2f} kg CO2 / mois")

    # 4. Diagnostic Opérationnel
    doc.add_heading("4. Diagnostic & Alertes de Maintenance", level=1)
    p_m = doc.add_paragraph()
    p_m.add_run("Statut Système : ").bold = True
    p_m.add_run(f"{status_text}")

    # Pied de page
    doc.add_paragraph("\n--------------------------------------------------------------------------------")
    footer = doc.add_paragraph("Rapport édité par la plateforme d'ingénierie NOISE LIGHT SaaS Pro. Document certifié.")
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].font.italic = True

    file_path = "Audit_NOISE_LIGHT_Master.docx"
    doc.save(file_path)
    return file_path


def build_html_pdf_report(admin_data, acoustic_data, piezo_data, financial_data, status_text):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Rapport NOISE LIGHT Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; color: #333; }}
            .header {{ border-bottom: 3px solid #0d6efd; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ color: #0d6efd; font-size: 24px; font-weight: bold; }}
            .section {{ margin-top: 20px; padding: 15px; background: #f8f9fa; border-left: 4px solid #0d6efd; border-radius: 4px; }}
            .section-title {{ font-size: 16px; font-weight: bold; color: #0d6efd; margin-bottom: 10px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .label {{ font-weight: bold; }}
            .footer {{ margin-top: 30px; font-size: 11px; text-align: center; color: #777; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">⚡ NOISE LIGHT Pro — RAPPORT D'INGÉNIERIE & CERTIFICATION</div>
            <div>Date d'émission : {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        </div>

        <div class="section">
            <div class="section-title">1. CADRE ADMINISTRATIF</div>
            <div class="grid">
                <div><span class="label">Client :</span> {admin_data.get('client_name')}</div>
                <div><span class="label">Code Projet :</span> {admin_data.get('project_id')}</div>
                <div><span class="label">Auditeur :</span> {admin_data.get('auditor_name')}</div>
                <div><span class="label">GPS :</span> Lat {acoustic_data.get('lat', 0.0):.4f}, Lng {acoustic_data.get('lng', 0.0):.4f}</div>
            </div>
            <div style="margin-top: 8px;"><span class="label">Site :</span> {admin_data.get('site_desc')}</div>
        </div>

        <div class="section">
            <div class="section-title">2. MÉTROLOGIE ACOUSTIQUE & COMPOSANTS</div>
            <div class="grid">
                <div><span class="label">Niveau Sonore :</span> {acoustic_data.get('db')} dBA</div>
                <div><span class="label">Fréquence :</span> {acoustic_data.get('freq')} Hz</div>
                <div><span class="label">Surface Active :</span> {acoustic_data.get('surface')} m²</div>
                <div><span class="label">Matériau :</span> {piezo_data.get('material_name')}</div>
                <div><span class="label">Coeff. d33 :</span> {piezo_data.get('d33')} pC/N</div>
                <div><span class="label">Rendement η :</span> {piezo_data.get('eta')*100:.1f} %</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">3. PERFORMANCES ÉNERGÉTIQUES, ROBUSTESSE ET ESG</div>
            <div class="grid">
                <div><span class="label">Puissance Nette :</span> {financial_data.get('p_mw'):.2f} mW</div>
                <div><span class="label">Production / Jour :</span> {financial_data.get('e_wh_day'):.2f} Wh/j</div>
                <div><span class="label">CAPEX Estimé :</span> {financial_data.get('capex', 0):,.0f} FCFA</div>
                <div><span class="label">Payback ROI :</span> {financial_data.get('roi', 0):.1f} mois</div>
                <div><span class="label">Économies / Mois :</span> {financial_data.get('savings_fcfa'):,.0f} FCFA</div>
                <div><span class="label">Réduction CO2 :</span> {financial_data.get('co2_kg'):.2f} kg/mois</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">4. ÉVALUATION TECHNIQUE</div>
            <div><span class="label">Diagnostic Système :</span> {status_text}</div>
        </div>

        <div class="footer">
            Rapport Certifié NOISE LIGHT Pro. Prêt pour l'impression officielle et la soumission d'audit ESG.
        </div>
    </body>
    </html>
    """
    return html_content
