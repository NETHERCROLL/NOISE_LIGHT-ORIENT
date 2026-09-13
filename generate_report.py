from docx import Document
from docx.shared import Inches, Pt, RGBColor
from datetime import datetime

def build_docx_report(admin_data, acoustic_data, piezo_data, financial_data, status_text):
    doc = Document()

    # En-tête
    title = doc.add_heading("NOISE LIGHT — Rapport d'Audit & Certification Acoustique", level=0)
    title.runs[0].font.color.rgb = RGBColor(13, 110, 253)
    
    doc.add_paragraph(f"Date du Diagnostic : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
    doc.add_paragraph("--------------------------------------------------------------------------------")

    # 1. Informations Administratives
    doc.add_heading("1. Informations Administratives & Cadre de l'Audit", level=1)
    p_admin = doc.add_paragraph()
    p_admin.add_run("• Organisme / Client : ").bold = True
    p_admin.add_run(f"{admin_data.get('client_name', 'N/A')}\n")
    p_admin.add_run("• Identifiant Projet : ").bold = True
    p_admin.add_run(f"{admin_data.get('project_id', 'N/A')}\n")
    p_admin.add_run("• Auditeur / Expert : ").bold = True
    p_admin.add_run(f"{admin_data.get('auditor_name', 'N/A')}\n")
    p_admin.add_run("• Description du Site : ").bold = True
    p_admin.add_run(f"{admin_data.get('site_desc', 'N/A')}\n")
    p_admin.add_run("• Coordonnées GPS : ").bold = True
    p_admin.add_run(f"{acoustic_data.get('lat', 0.0):.5f}, {acoustic_data.get('lng', 0.0):.5f}")

    # 2. Données Physiques & Matériaux
    doc.add_heading("2. Paramètres Physiques & Spécifications Piézoélectriques", level=1)
    p_phys = doc.add_paragraph()
    p_phys.add_run("• Niveau Sonore Mesuré : ").bold = True
    p_phys.add_run(f"{acoustic_data.get('db')} dBA\n")
    p_phys.add_run("• Fréquence Dominante (FFT) : ").bold = True
    p_phys.add_run(f"{acoustic_data.get('freq')} Hz\n")
    p_phys.add_run("• Surface de Capture : ").bold = True
    p_phys.add_run(f"{acoustic_data.get('surface')} m²\n")
    p_phys.add_run("• Matériau Sélectionné : ").bold = True
    p_phys.add_run(f"{piezo_data.get('material_name')}\n")
    p_phys.add_run("• Coefficient d33 : ").bold = True
    p_phys.add_run(f"{piezo_data.get('d33')} pC/N | ")
    p_phys.add_run("Rendement (η) : ").bold = True
    p_phys.add_run(f"{piezo_data.get('eta')*100:.1f} %")

    # 3. Métriques Énergétiques & Bilan ESG
    doc.add_heading("3. Bilans Énergétique, Financier & Impact ESG", level=1)
    p_e = doc.add_paragraph()
    p_e.add_run("• Puissance Électrique Instantanée : ").bold = True
    p_e.add_run(f"{financial_data.get('p_mw'):.2f} mW\n")
    p_e.add_run("• Énergie Produite par Jour : ").bold = True
    p_e.add_run(f"{financial_data.get('e_wh_day'):.2f} Wh/jour\n")
    p_e.add_run("• Économies Financières Estimées : ").bold = True
    p_e.add_run(f"{financial_data.get('savings_fcfa'):,.0f} FCFA / mois\n".replace(",", " "))
    p_e.add_run("• Empreinte CO2 Évitée : ").bold = True
    p_e.add_run(f"{financial_data.get('co2_kg'):.2f} kg CO2 / mois")

    # 4. Diagnostic de Maintenance
    doc.add_heading("4. Diagnostic & Maintenance Prédictive", level=1)
    p_m = doc.add_paragraph()
    p_m.add_run("Statut Opérationnel : ").bold = True
    p_m.add_run(f"{status_text}")

    # Footer
    doc.add_paragraph("\n--------------------------------------------------------------------------------")
    footer = doc.add_paragraph("Rapport certifié édité automatiquement par la suite logicielle NOISE LIGHT SaaS.")
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
        <title>Rapport NOISE LIGHT</title>
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
            <div class="title">⚡ NOISE LIGHT — RAPPORT CERTIFIÉ D'AUDIT ACOUSTIQUE</div>
            <div>Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        </div>

        <div class="section">
            <div class="section-title">1. CADRE ADMINISTRATIF</div>
            <div class="grid">
                <div><span class="label">Client :</span> {admin_data.get('client_name')}</div>
                <div><span class="label">ID Projet :</span> {admin_data.get('project_id')}</div>
                <div><span class="label">Expert Auditeur :</span> {admin_data.get('auditor_name')}</div>
                <div><span class="label">Coordonnées :</span> Lat {acoustic_data.get('lat', 0.0):.4f}, Lng {acoustic_data.get('lng', 0.0):.4f}</div>
            </div>
            <div style="margin-top: 8px;"><span class="label">Site :</span> {admin_data.get('site_desc')}</div>
        </div>

        <div class="section">
            <div class="section-title">2. DÉTAILS DU DIAGNOSTIC ACOUSTIQUE & MATÉRIEL</div>
            <div class="grid">
                <div><span class="label">Niveau Sonore :</span> {acoustic_data.get('db')} dBA</div>
                <div><span class="label">Fréquence Résonnante :</span> {acoustic_data.get('freq')} Hz</div>
                <div><span class="label">Surface Active :</span> {acoustic_data.get('surface')} m²</div>
                <div><span class="label">Matériau :</span> {piezo_data.get('material_name')}</div>
                <div><span class="label">Coefficient d33 :</span> {piezo_data.get('d33')} pC/N</div>
                <div><span class="label">Rendement η :</span> {piezo_data.get('eta')*100:.1f} %</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">3. PERFORMANCES ÉNERGÉTIQUES, FINANCIÈRES & ESG</div>
            <div class="grid">
                <div><span class="label">Puissance Instantanée :</span> {financial_data.get('p_mw'):.2f} mW</div>
                <div><span class="label">Énergie Quotidienne :</span> {financial_data.get('e_wh_day'):.2f} Wh/jour</div>
                <div><span class="label">Économies Estimées :</span> {financial_data.get('savings_fcfa'):,.0f} FCFA / mois</div>
                <div><span class="label">Réduction CO2 :</span> {financial_data.get('co2_kg'):.2f} kg CO2/mois</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">4. ÉVALUATION DE MAINTENANCE PRÉDICTIVE</div>
            <div><span class="label">Statut des Installations :</span> {status_text}</div>
        </div>

        <div class="footer">
            Document officiel NOISE LIGHT Software Suite. Imprimable au format PDF via la fonction impression navigateur.
        </div>
    </body>
    </html>
    """
    return html_content
