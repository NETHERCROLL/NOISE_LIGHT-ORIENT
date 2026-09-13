import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import datetime

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def build_docx_report(admin_data, acoustic_data, piezo_data, financial_data, status_text):
    doc = docx.Document()

    # Configuration des marges
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # --------------------------------------------------------------------------
    # EN-TÊTE DU RAPPORT
    # --------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("⚡ RAPPORT D'AUDIT TECHNIQUE & OPTIMISATION PIÉZOÉLECTRIQUE")
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(13, 110, 253)

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Plateforme NOISE LIGHT Pro — Dimensionnement et Mesures Physique")
    sub_run.font.name = 'Calibri'
    sub_run.font.size = Pt(11)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 100, 100)

    # Avertissement Mode Terrain si actif
    if admin_data.get("is_field_mode"):
        field_p = doc.add_paragraph()
        field_run = field_p.add_run("🔴 CERTIFICATION DE MESURE SUR TERRAIN EN DIRECT (CAPTEURS HARDWARE)")
        field_run.font.bold = True
        field_run.font.color.rgb = RGBColor(220, 53, 69)

    doc.add_paragraph("―" * 55)

    # --------------------------------------------------------------------------
    # TABLEAU DES MÉTADONNÉES ADMINISTRATIVES
    # --------------------------------------------------------------------------
    doc.add_heading("1. Métadonnées du Projet", level=2)
    t_admin = doc.add_table(rows=4, cols=2)
    t_admin.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    admin_rows = [
        ("Nom du Client / Site :", str(admin_data.get("client_name"))),
        ("Référence Projet :", str(admin_data.get("project_id"))),
        ("Auditeur / Expert :", str(admin_data.get("auditor_name"))),
        ("Date & Heure d'Audit :", datetime.datetime.now().strftime("%d/%m/%Y à %H:%M"))
    ]
    
    for i, (label, val) in enumerate(admin_rows):
        row = t_admin.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.paragraphs[0].add_run(label).bold = True
        c1.paragraphs[0].add_run(val)
        set_cell_background(c0, "F8F9FA")
        set_cell_margins(c0, 80, 80, 120, 120)
        set_cell_margins(c1, 80, 80, 120, 120)

    # --------------------------------------------------------------------------
    # DIAGNOSTIC AUTOMATIQUE
    # --------------------------------------------------------------------------
    doc.add_heading("2. Synthèse du Diagnostic", level=2)
    diag_p = doc.add_paragraph()
    diag_run = diag_p.add_run(f"Résultat de l'analyse : {status_text}")
    diag_run.font.bold = True
    diag_run.font.color.rgb = RGBColor(220, 53, 69) if "ANOMALIE" in status_text else RGBColor(25, 135, 84)

    # --------------------------------------------------------------------------
    # TABLEAU DES PERFORMANCES TECHNIQUES & METRIQUES
    # --------------------------------------------------------------------------
    doc.add_heading("3. Relevés & Modélisation Multiphysique", level=2)
    t_tech = doc.add_table(rows=7 if admin_data.get("is_field_mode") else 6, cols=3)
    t_tech.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Paramètre", "Valeur Mesurée / Simulée", "Source de Donnée"]
    for j, h in enumerate(headers):
        cell = t_tech.rows[0].cells[j]
        r = cell.paragraphs[0].add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0D6EFD")
        set_cell_margins(cell, 100, 100, 150, 150)

    source_str = "🔴 Capteurs Terrain (Micro/GPS/Accel)" if admin_data.get("is_field_mode") else "🌐 Simulation Satellite / Code"

    tech_rows = [
        ("Niveau de Pression Acoustique", f"{acoustic_data['db']} dBA", source_str),
        ("Fréquence Dominante Est.", f"{acoustic_data['freq']} Hz", "FFT Spectrogramme"),
        ("Localisation GPS", f"Lat {acoustic_data['lat']:.5f}, Lng {acoustic_data['lng']:.5f}", source_str),
        ("Matériau Piézoélectrique", f"{piezo_data['material_name'].split('(')[0]}", "Bibliothèque Matériaux"),
        ("Puissance Nette Extraite", f"{financial_data['p_mw']:.2f} mW", "Moteur Phys. NOISE LIGHT")
    ]

    if admin_data.get("is_field_mode"):
        tech_rows.append(("Accélération Vibratoire", f"{admin_data.get('field_accel'):.2f} m/s²", "🔴 Accéléromètre Terrain"))

    for i, (p_name, p_val, p_src) in enumerate(tech_rows, start=1):
        row = t_tech.rows[i]
        row.cells[0].paragraphs[0].add_run(p_name).bold = True
        row.cells[1].paragraphs[0].add_run(p_val)
        row.cells[2].paragraphs[0].add_run(p_src)
        for c in row.cells:
            set_cell_margins(c, 80, 80, 120, 120)
            if i % 2 == 0:
                set_cell_background(c, "F8F9FA")

    # --------------------------------------------------------------------------
    # BILAN ÉCONOMIQUE & ESG
    # --------------------------------------------------------------------------
    doc.add_heading("4. Viabilité Économique et Empreinte Carbone", level=2)
    doc.add_paragraph(f"• Énergie quotidienne produite : {financial_data['e_wh_day']:.2f} Wh/jour")
    doc.add_paragraph(f"• Économie financière mensuelle : {financial_data['savings_fcfa']:,.0f} FCFA / mois".replace(",", " "))
    doc.add_paragraph(f"• Réduction de CO2 estimée : {financial_data['co2_kg']:.2f} kg CO2 / mois")
    doc.add_paragraph(f"• Investissement CAPEX global : {financial_data['capex']/1e6:.2f} Millions FCFA")
    doc.add_paragraph(f"• ROI (Retour sur Investissement) : {financial_data['roi']:.1f} mois")

    doc.add_paragraph("\nRapport certifié et généré automatiquement par la plateforme NOISE LIGHT Engine 2026.")

    file_path = f"Rapport_NOISE_LIGHT_{admin_data['project_id']}.docx"
    doc.save(file_path)
    return file_path


def build_html_pdf_report(admin_data, acoustic_data, piezo_data, financial_data, status_text):
    is_field = admin_data.get("is_field_mode", False)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Audit NOISE LIGHT Pro - {admin_data['project_id']}</title>
        <style>
            body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; margin: 40px; color: #333; }}
            .header {{ border-bottom: 3px solid #0d6efd; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ color: #0d6efd; margin: 0; font-size: 24px; }}
            .header p {{ color: #6c757d; margin: 5px 0 0 0; }}
            .badge-field {{ background: #dc3545; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px; display: inline-block; margin-top: 10px; }}
            .section-title {{ color: #0d6efd; border-left: 4px solid #0d6efd; padding-left: 10px; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: left; }}
            th {{ background-color: #0d6efd; color: white; }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            .status-box {{ padding: 15px; border-radius: 5px; font-weight: bold; margin-top: 20px; }}
            .status-alert {{ background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }}
            .status-ok {{ background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }}
            .kpi-container {{ display: flex; justify-content: space-between; margin-top: 20px; }}
            .kpi-card {{ background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center; width: 30%; }}
            .kpi-value {{ font-size: 20px; font-weight: bold; color: #0d6efd; margin-top: 5px; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>

        <div class="no-print" style="margin-bottom: 20px;">
            <button onclick="window.print()" style="background:#0d6efd; color:white; border:none; padding:10px 20px; font-weight:bold; cursor:pointer; border-radius:4px;">
                🖨️ Imprimer / Sauvegarder en PDF
            </button>
        </div>

        <div class="header">
            <h1>⚡ AUDIT TECHNIQUE DE RÉCOLTE D'ÉNERGIE PIÉZOÉLECTRIQUE</h1>
            <p>Plateforme Certifiée NOISE LIGHT Pro — Exportation Métrologique</p>
            {"<div class='badge-field'>🔴 CERTIFIÉ SUR TERRAIN : DONNÉES HARDWARE RÉELLES</div>" if is_field else ""}
        </div>

        <h3 class="section-title">1. Informations Administratives</h3>
        <table>
            <tr><th>Projet</th><td>{admin_data['project_id']}</td><th>Client</th><td>{admin_data['client_name']}</td></tr>
            <tr><th>Auditeur</th><td>{admin_data['auditor_name']}</td><th>Date</th><td>{datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")}</td></tr>
        </table>

        <div class="status-box {'status-alert' if 'ANOMALIE' in status_text else 'status-ok'}">
            Diagnostic Moteur : {status_text}
        </div>

        <h3 class="section-title">2. Métriques Multiphysiques Capturées</h3>
        <table>
            <thead>
                <tr>
                    <th>Indicateur</th>
                    <th>Valeur</th>
                    <th>Source d'Origine</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Intensité Acoustique</td><td><b>{acoustic_data['db']} dBA</b></td><td>{"🔴 Microphone physique" if is_field else "Simulation Code"}</td></tr>
                <tr><td>Fréquence Dominante</td><td><b>{acoustic_data['freq']} Hz</b></td><td>Spectrogramme FFT</td></tr>
                <tr><td>Coordonnées GPS</td><td>Lat {acoustic_data['lat']:.5f}, Lng {acoustic_data['lng']:.5f}</td><td>{"🔴 GPS WebRTC" if is_field else "Saisie Cartographique"}</td></tr>
                {"<tr><td>Accélération Vibratoire</td><td><b>" + str(round(admin_data.get('field_accel',0), 2)) + " m/s²</b></td><td>🔴 Accéléromètre matériel</td></tr>" if is_field else ""}
                <tr><td>Matériau Piézoélectrique</td><td>{piezo_data['material_name']}</td><td>Bibliothèque Matériau</td></tr>
                <tr><td>Puissance Nette Calculée</td><td><b>{financial_data['p_mw']:.2f} mW</b></td><td>Modèle Physique NOISE LIGHT</td></tr>
            </tbody>
        </table>

        <h3 class="section-title">3. Bilan d'Énergie & Rentabilité (ROI)</h3>
        <div class="kpi-container">
            <div class="kpi-card">
                <div>Énergie / Jour</div>
                <div class="kpi-value">{financial_data['e_wh_day']:.1f} Wh/j</div>
            </div>
            <div class="kpi-card">
                <div>Gains Financiers</div>
                <div class="kpi-value">{financial_data['savings_fcfa']:,.0f} FCFA/mo</div>
            </div>
            <div class="kpi-card">
                <div>Payback (ROI)</div>
                <div class="kpi-value">{financial_data['roi']:.1f} mois</div>
            </div>
        </div>

        <p style="margin-top:40px; font-size:12px; color:#888; text-align:center;">
            Document d'audit généré par NOISE LIGHT Engine 2026 — Certifié conforme pour l'aide à la décision.
        </p>

    </body>
    </html>
    """
    return html_content
