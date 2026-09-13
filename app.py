import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import math
from generate_report import build_docx_report, build_html_pdf_report

# ------------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE STREAMLIT
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="NOISE LIGHT — Master Acoustic SaaS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# BIBLIOTHÈQUE SCIENTIFIQUE EXTENSIVE DES MATÉRIAUX PIÉZOÉLECTRIQUES
# ------------------------------------------------------------------------------
PIEZO_LIBRARY = {
    "PZT-5H (Céramique Haute Sensibilité)": {
        "eta": 0.25, "d33": 593, "k33": 0.75, "eps_r": 3400, "temp_curie": 190, "qm": 65,
        "desc": "Excellente conversion basse tension, idéale pour le bruit ambiant urbain."
    },
    "PZT-4 (Céramique Haute Puissance)": {
        "eta": 0.22, "d33": 289, "k33": 0.70, "eps_r": 1300, "temp_curie": 328, "qm": 500,
        "desc": "Robuste aux contraintes fortes, optimale pour les milieux industriels."
    },
    "PMN-PT (Monocristal Ultra-Performance)": {
        "eta": 0.35, "d33": 2500, "k33": 0.92, "eps_r": 5400, "temp_curie": 130, "qm": 80,
        "desc": "Performance piézoélectrique d'exception, réservée aux applications critiques."
    },
    "BaTiO3 (Titanate de Baryum - Eco/NoLead)": {
        "eta": 0.15, "d33": 190, "k33": 0.48, "eps_r": 1700, "temp_curie": 120, "qm": 300,
        "desc": "Matériau écologique sans plomb à coût modéré."
    },
    "PVDF (Polymère Souple Fluoré)": {
        "eta": 0.10, "d33": 33, "k33": 0.20, "eps_r": 12, "temp_curie": 80, "qm": 10,
        "desc": "Flexible, léger et intégrable sur surfaces courbes ou textiles."
    },
    "AlN (Nitrure d'Aluminium - Haute T°)": {
        "eta": 0.08, "d33": 5, "k33": 0.23, "eps_r": 9, "temp_curie": 1150, "qm": 1000,
        "desc": "Ultra-résistant aux températures extrêmes (turbines, moteurs)."
    },
    "Quartz Cristallin SiO2 (Stable)": {
        "eta": 0.05, "d33": 2.3, "k33": 0.10, "eps_r": 4.5, "temp_curie": 573, "qm": 25000,
        "desc": "Stabilité fréquentielle parfaite, très faible dérive dans le temps."
    }
}

HOTSPOTS_BASE = {
    "Carrefour Ndokoti": {"coords": [4.0478, 9.7431], "db": 98, "freq": 1200},
    "Zone Industrielle Bassa": {"coords": [4.0103, 9.6895], "db": 108, "freq": 850},
    "Marché Central": {"coords": [4.0600, 9.6930], "db": 90, "freq": 1500}
}

# ------------------------------------------------------------------------------
# FONCTION : ESTIMATION SATELLITAIRE ACOUSTIQUE DYNAMIQUE
# ------------------------------------------------------------------------------
def estimate_satellite_acoustic_profile(lat, lng):
    """
    Simule la réponse acoustique spatiale directement à partir des coordonnées
    géographiques cliquées sur la carte satellite.
    """
    ref_lat, ref_lng = 4.0478, 9.7431
    dist = math.sqrt((lat - ref_lat)**2 + (lng - ref_lng)**2) * 111.0  # distance approx en km
    
    seed = int((abs(lat) * 10000 + abs(lng) * 10000)) % 1000
    np.random.seed(seed)
    
    base_db = 95 - (dist * 2.5) + np.random.uniform(-5, 12)
    db_estimated = int(np.clip(base_db, 65, 135))
    freq_estimated = int(400 + (seed % 18) * 100 + np.random.uniform(-50, 50))
    
    return db_estimated, freq_estimated

# ------------------------------------------------------------------------------
# INITIALISATION DES ÉTATS DE SESSION (SESSION STATE)
# ------------------------------------------------------------------------------
if "current_lat" not in st.session_state:
    st.session_state.current_lat = 4.0478
if "current_lng" not in st.session_state:
    st.session_state.current_lng = 9.7431
if "db_val" not in st.session_state:
    st.session_state.db_val = 98
if "freq_val" not in st.session_state:
    st.session_state.freq_val = 1200

# ------------------------------------------------------------------------------
# SIDEBAR : RÉGLAGES, MATÉRIAUX & FORMULAIRE ADMINISTRATIF
# ------------------------------------------------------------------------------
st.sidebar.title("⚡ NOISE LIGHT SaaS")
st.sidebar.caption("Plateforme d'Intelligence Acoustique & Énergétique")
st.sidebar.markdown("---")

# 1. Sélection & Tuning Matériau Piézo
st.sidebar.subheader("🔬 Matériau Piézoélectrique")
selected_mat_key = st.sidebar.selectbox("Choix de la Matrice Piézo :", list(PIEZO_LIBRARY.keys()))
mat_info = PIEZO_LIBRARY[selected_mat_key]

with st.sidebar.expander("⚙️ Personnaliser les Paramètres Matériau"):
    custom_d33 = st.number_input("Coefficient d33 (pC/N)", value=float(mat_info["d33"]), step=10.0)
    custom_k33 = st.slider("Couplage Électromécanique (k33)", 0.05, 0.99, float(mat_info["k33"]), 0.01)
    custom_eta = st.slider("Rendement Global η (%)", 1.0, 50.0, float(mat_info["eta"]*100), 0.5) / 100.0
    custom_qm = st.number_input("Facteur de Qualité Mécanique (Qm)", value=int(mat_info["qm"]), step=10)

# 2. Paramètres Physiques Ambiants
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Paramètres Acoustiques")
db_input = st.sidebar.slider("Niveau Sonore (dBA) :", 60, 140, int(st.session_state.db_val), key="sb_db")
freq_input = st.sidebar.number_input("Fréquence Signal (Hz) :", 20, 20000, int(st.session_state.freq_val), step=50, key="sb_freq")
surface_input = st.sidebar.slider("Surface Active Capteurs (m²) :", 0.5, 100.0, 15.0, 0.5)
hours_input = st.sidebar.number_input("Exposition / Jour (Heures) :", 1, 24, 14)
kwh_cost_input = st.sidebar.number_input("Tarif Électricité (FCFA/kWh) :", 10, 500, 100)

# 3. Métadonnées Administratives pour Rapports
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Métadonnées Administratives")
client_name = st.sidebar.text_input("Organisme / Client :", "Port Autonome de Douala")
project_id = st.sidebar.text_input("N° / Code Projet :", "NL-2026-DLA-001")
auditor_name = st.sidebar.text_input("Nom de l'Auditeur :", "Dr. Ing. Alex T.")
site_desc = st.sidebar.text_area("Description du Site :", "Zone d'échappement compresseurs lourds & trafic conteneurs.")

# ------------------------------------------------------------------------------
# MOTEUR DE CALCUL PHYSIQUE & ESG
# ------------------------------------------------------------------------------
P0 = 2e-5      # Seuil d'audition (Pa)
rho_c = 400    # Impédance acoustique de l'air

pression = P0 * (10 ** (db_input / 20))
p_acoustique = ((pression ** 2) / rho_c) * surface_input
p_electrique = p_acoustique * custom_eta  # Watts

e_jour_wh = p_electrique * hours_input
e_mois_kwh = (e_jour_wh * 30) / 1000
savings_fcfa = e_mois_kwh * kwh_cost_input
co2_kg = e_mois_kwh * 0.5

# ------------------------------------------------------------------------------
# EN-TÊTE PRINCIPAL ET MÉTRIQUES KPIs
# ------------------------------------------------------------------------------
st.title("NOISE LIGHT — Intelligence Acoustique, Énergie & ESG")
st.markdown(f"**Coordonnées Actives :** Lat `{st.session_state.current_lat:.5f}` | Lng `{st.session_state.current_lng:.5f}` | **Matériau :** `{selected_mat_key.split(' ')[0]}`")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Puissance Générée", f"{p_electrique * 1000:.2f} mW")
kpi2.metric("Énergie / Jour", f"{e_jour_wh:.1f} Wh/j")
kpi3.metric("Gains Financiers", f"{savings_fcfa:,.0f} FCFA/mo".replace(",", " "))
kpi4.metric("CO2 Évité", f"{co2_kg:.2f} kg/mo")
kpi5.metric("Coeff. d33", f"{custom_d33} pC/N")

st.markdown("---")

# ------------------------------------------------------------------------------
# STRUCTURE INTERCONNECTÉE PAR ONGLETS
# ------------------------------------------------------------------------------
tab_map, tab_3d, tab_fft, tab_mat, tab_audit = st.tabs([
    "🗺️ Carte Satellite Dynamic", 
    "📊 Surface 3D & Rendement", 
    "📈 Spectrogramme FFT Pro", 
    "🧪 Matériaux & Sensibilité", 
    "📑 Rapports & Certification"
])

# ------------------------------------------------------------------------------
# TAB 1 : CARTE SATELLITE & SÉLECTION REATIVE
# ------------------------------------------------------------------------------
with tab_map:
    st.subheader("📍 Extractor Acoustique Satellite HD (Google Hybrid)")
    st.caption("Cliquez sur n'importe quel point de la carte pour extraire dynamiquement les caractéristiques acoustiques du site.")

    col_map_left, col_map_right = st.columns([3, 1])

    with col_map_right:
        st.write("**Hotspots Prédéfinis**")
        selected_preset = st.selectbox("Charger une zone :", ["-- Cliquer sur la carte --"] + list(HOTSPOTS_BASE.keys()))
        if selected_preset != "-- Cliquer sur la carte --":
            hp = HOTSPOTS_BASE[selected_preset]
            st.session_state.current_lat, st.session_state.current_lng = hp["coords"]
            st.session_state.db_val = hp["db"]
            st.session_state.freq_val = hp["freq"]

        st.markdown("---")
        st.write("**Données du Point Sélectionné**")
        st.info(
            f"**Latitude :** {st.session_state.current_lat:.5f}\n\n"
            f"**Longitude :** {st.session_state.current_lng:.5f}\n\n"
            f"**Bruit Estimé :** {st.session_state.db_val} dBA\n\n"
            f"**Fréquence Est. :** {st.session_state.freq_val} Hz"
        )
        if st.button("Synchroniser avec les Sliders", type="primary"):
            st.rerun()

    with col_map_left:
        # Création de la carte avec tuiles Google Satellite Hybrid
        m = folium.Map(
            location=[st.session_state.current_lat, st.session_state.current_lng],
            zoom_start=13,
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google Satellite Hybrid'
        )

        # Repères visuels des hotspots
        for name, info in HOTSPOTS_BASE.items():
            folium.Marker(
                location=info["coords"],
                popup=f"<b>{name}</b><br>{info['db']} dBA - {info['freq']} Hz",
                tooltip=name,
                icon=folium.Icon(color="red" if info["db"] >= 100 else "orange", icon="bolt", prefix="fa")
            ).add_to(m)

        # Marqueur de la sélection courante
        folium.Marker(
            location=[st.session_state.current_lat, st.session_state.current_lng],
            popup="Point d'Analyse Actif",
            icon=folium.Icon(color="green", icon="crosshairs", prefix="fa")
        ).add_to(m)

        map_data = st_folium(m, width=900, height=480, key="satellite_map")

        # Capture de l'événement de clic utilisateur sur la carte
        if map_data and map_data.get("last_clicked"):
            c_lat = map_data["last_clicked"]["lat"]
            c_lng = map_data["last_clicked"]["lng"]
            
            if (c_lat != st.session_state.current_lat) or (c_lng != st.session_state.current_lng):
                st.session_state.current_lat = c_lat
                st.session_state.current_lng = c_lng
                
                # Extraction dynamique du profil acoustique
                db_est, freq_est = estimate_satellite_acoustic_profile(c_lat, c_lng)
                st.session_state.db_val = db_est
                st.session_state.freq_val = freq_est
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 2 : SURFACE DE RÉPONSE 3D & MODELISATION AVANCÉE
# ------------------------------------------------------------------------------
with tab_3d:
    st.subheader("📊 Modélisation Tri-Dimensionnelle de la Puissance Récoltée")
    
    db_range = np.linspace(70, 130, 40)
    surf_range = np.linspace(1, 50, 40)
    DB_GRID, SURF_GRID = np.meshgrid(db_range, surf_range)
    
    PRESS_GRID = P0 * (10 ** (DB_GRID / 20))
    POWER_GRID = (((PRESS_GRID ** 2) / rho_c) * SURF_GRID * custom_eta) * 1000  # mW

    fig_3d = go.Figure(data=[go.Surface(
        z=POWER_GRID, x=DB_GRID, y=SURF_GRID,
        colorscale='Viridis',
        colorbar_title="Puissance (mW)"
    )])

    # Ajout du point de fonctionnement actuel
    fig_3d.add_trace(go.Scatter3d(
        x=[db_input], y=[surface_input], z=[p_electrique * 1000],
        mode='markers',
        marker=dict(size=8, color='red', symbol='diamond'),
        name='Point de Fonctionnement'
    ))

    fig_3d.update_layout(
        title="Surface 3D : Puissance (mW) = f(Niveau dBA, Surface m²)",
        scene=dict(
            xaxis_title="Intensité (dBA)",
            yaxis_title="Surface (m²)",
            zaxis_title="Puissance (mW)"
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=550
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3 : SPECTROGRAMME FFT MULTI-HARMONIQUES PRO
# ------------------------------------------------------------------------------
with tab_fft:
    st.subheader("📈 Spectre Fréquentiel Ambiant & Harmoniques (Analyse FFT)")
    
    f_axis = np.linspace(20, 5000, 500)
    
    # Signal simulant la fondamentale (f0) et les harmoniques H2, H3
    f0 = freq_input
    sig = (
        np.exp(-((f_axis - f0)**2) / (2 * 40**2)) * db_input +
        0.4 * np.exp(-((f_axis - 2*f0)**2) / (2 * 60**2)) * db_input +
        0.2 * np.exp(-((f_axis - 3*f0)**2) / (2 * 80**2)) * db_input
    )
    
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Scatter(x=f_axis, y=sig, mode='lines', name='Spectre FFT', line=dict(color='#0d6efd', width=2)))
    
    # Ligne de seuil de tolérance vibratoire
    fig_fft.add_trace(go.Scatter(
        x=[20, 5000], y=[105, 105], 
        mode='lines', name='Seuil d\'Alerte Vibratoire (105 dBA)', 
        line=dict(color='red', dash='dash')
    ))

    fig_fft.update_layout(
        title=f"Analyse Fréquentielle — Fondamentale f0 = {f0} Hz + Harmoniques",
        xaxis_title="Fréquence (Hz)",
        yaxis_title="Amplitude Acoustique (dBA)",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_fft, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4 : COMPARATIF DE SENSIBILITÉ DES MATÉRIAUX PIÉZO
# ------------------------------------------------------------------------------
with tab_mat:
    st.subheader("🧪 Matrice Comparative de Sensibilité des Matériaux")
    
    mat_names = []
    powers_mw = []
    
    for m_name, m_data in PIEZO_LIBRARY.items():
        p_temp = (((P0 * (10 ** (db_input / 20))) ** 2) / rho_c) * surface_input * m_data["eta"] * 1000
        mat_names.append(m_name.split(" ")[0])
        powers_mw.append(p_temp)

    fig_mat = go.Figure()
    fig_mat.add_trace(go.Bar(x=mat_names, y=powers_mw, name="Puissance Générée (mW)", marker_color='#198754'))
    
    fig_mat.update_layout(
        title=f"Rendement Comparatif pour {db_input} dBA sur {surface_input} m²",
        xaxis_title="Matériau Piézoélectrique",
        yaxis_title="Puissance Électrique (mW)",
        template="plotly_white"
    )
    st.plotly_chart(fig_mat, use_container_width=True)

    st.markdown("### Fiche Technique du Matériau Sélectionné")
    st.json(mat_info)

# ------------------------------------------------------------------------------
# TAB 5 : MAINTENANCE PRÉDICTIVE & ÉDITION DE RAPPORTS WORD / PDF
# ------------------------------------------------------------------------------
with tab_audit:
    st.subheader("📑 Rapport d'Audit & Certification Opérationnelle")

    # Évaluation du statut de maintenance prédictive
    if freq_input > 2000 or db_input > 110:
        status_text = "ANOMALIE CRITIQUE : Usure mécanique ou résonance haute fréquence détectée. Maintenance urgente sous 48h."
        st.error(f"🚨 **{status_text}**")
    else:
        status_text = "STATUT NOMINAL : Empreinte acoustique stable. Aucun risque vibratoire détecté."
        st.success(f"✅ **{status_text}**")

    st.markdown("---")
    st.subheader("📥 Génération des Documents Certifiés")

    # Aggregation des données pour le module d'exportation
    admin_data = {
        "client_name": client_name,
        "project_id": project_id,
        "auditor_name": auditor_name,
        "site_desc": site_desc
    }
    
    acoustic_data = {
        "db": db_input,
        "freq": freq_input,
        "surface": surface_input,
        "lat": st.session_state.current_lat,
        "lng": st.session_state.current_lng
    }
    
    piezo_data = {
        "material_name": selected_mat_key,
        "d33": custom_d33,
        "eta": custom_eta
    }
    
    financial_data = {
        "p_mw": p_electrique * 1000,
        "e_wh_day": e_jour_wh,
        "savings_fcfa": savings_fcfa,
        "co2_kg": co2_kg
    }

    col_btn1, col_btn2 = st.columns(2)

    # Export Word (.docx)
    with col_btn1:
        if st.button("📄 Générer le Rapport Word (.docx)", type="primary", use_container_width=True):
            docx_path = build_docx_report(admin_data, acoustic_data, piezo_data, financial_data, status_text)
            
            with open(docx_path, "rb") as f:
                st.download_button(
                    label="📥 Télécharger le Fichier .docx",
                    data=f,
                    file_name=f"Rapport_NOISE_LIGHT_{project_id}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

    # Export PDF (Format HTML Imprimable)
    with col_btn2:
        if st.button("🌐 Générer le Rapport PDF (Format Imprimable)", use_container_width=True):
            html_code = build_html_pdf_report(admin_data, acoustic_data, piezo_data, financial_data, status_text)
            
            st.download_button(
                label="📥 Télécharger le Rapport PDF/HTML Certifié",
                data=html_code,
                file_name=f"Rapport_Certifie_{project_id}.html",
                mime="text/html",
                use_container_width=True
            )
            st.caption("💡 Ouvrez le fichier HTML téléchargé et faites **Ctrl+P** pour l'enregistrer en PDF.")
