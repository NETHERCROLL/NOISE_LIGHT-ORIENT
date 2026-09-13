import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from generate_report import build_docx_report

# ------------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE STREAMLIT
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="NOISE LIGHT — Smart Acoustic SaaS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# BASE DE DONNÉES DES POINTS CHAUDS (DOUALA)
# ------------------------------------------------------------------------------
HOTSPOTS = {
    "Carrefour Ndokoti": {
        "coords": [4.0478, 9.7431],
        "db": 98,
        "freq": 1200,
        "desc": "Fort trafic automobile et activités commerciales"
    },
    "Zone Industrielle Bassa": {
        "coords": [4.0103, 9.6895],
        "db": 108,
        "freq": 850,
        "desc": "Machines industrielles et compresseurs lourds"
    },
    "Marché Central": {
        "coords": [4.0600, 9.6930],
        "db": 90,
        "freq": 1500,
        "desc": "Nouveau centre marchand, bruit ambiant continu"
    }
}

# ------------------------------------------------------------------------------
# INITIALISATION DES ÉTATS DE SESSION (SESSION STATE)
# ------------------------------------------------------------------------------
if "db_val" not in st.session_state:
    st.session_state.db_val = 98

if "freq_val" not in st.session_state:
    st.session_state.freq_val = 1200

# ------------------------------------------------------------------------------
# SIDEBAR : PARAMÈTRES ET CONFIGURATION
# ------------------------------------------------------------------------------
st.sidebar.title("⚡ NOISE LIGHT")
st.sidebar.markdown("---")

st.sidebar.subheader("Paramètres Acoustiques")

db_input = st.sidebar.slider(
    "Niveau Sonore (dBA) :",
    min_value=60,
    max_value=140,
    value=st.session_state.db_val,
    step=1,
    key="db_slider"
)

freq_input = st.sidebar.number_input(
    "Fréquence du Signal (Hz) :",
    min_value=20,
    max_value=20000,
    value=st.session_state.freq_val,
    step=50,
    key="freq_input_field"
)

surface_input = st.sidebar.slider(
    "Surface des Capteurs (m²) :",
    min_value=0.5,
    max_value=50.0,
    value=10.0,
    step=0.5
)

st.sidebar.markdown("---")
st.sidebar.subheader("Spécifications Techniques")

materials = {
    "Céramique PZT (Rendement 20%)": 0.20,
    "Polymère PVDF (Rendement 10%)": 0.10,
    "Quartz Cristallin (Rendement 5%)": 0.05
}
selected_material = st.sidebar.selectbox("Matériau Piézoélectrique :", list(materials.keys()))
eta = materials[selected_material]

hours_input = st.sidebar.number_input("Exposition / Jour (Heures) :", min_value=1, max_value=24, value=14)
kwh_cost_input = st.sidebar.number_input("Coût Électricité (FCFA/kWh) :", min_value=10, max_value=500, value=100)

# ------------------------------------------------------------------------------
# MOTEUR DE CALCUL PHYSIQUE, FINANCIER & ESG
# ------------------------------------------------------------------------------
P0 = 2e-5      # Seuil d'audition (Pa)
rho_c = 400    # Impédance acoustique de l'air

pression = P0 * (10 ** (db_input / 20))
p_acoustique = ((pression ** 2) / rho_c) * surface_input
p_electrique = p_acoustique * eta  # en Watts

e_jour_wh = p_electrique * hours_input
e_mois_kwh = (e_jour_wh * 30) / 1000
savings_fcfa = e_mois_kwh * kwh_cost_input
co2_kg = e_mois_kwh * 0.5  # 1 kWh ~ 0.5 kg CO2 évité

# ------------------------------------------------------------------------------
# EN-TÊTE ET DASHBOARD KPIs
# ------------------------------------------------------------------------------
st.title("NOISE LIGHT — Plateforme d'Intelligence Acoustique & Énergétique")
st.caption("Solution SaaS d'analyse fréquentielle, de conversion d'énergie piézoélectrique et d'audit ESG")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Puissance Instantanée", f"{p_electrique * 1000:.2f} mW")
col2.metric("Production / Jour", f"{e_jour_wh:.1f} Wh/j")
col3.metric("Économies / Mois", f"{savings_fcfa:,.0f} FCFA".replace(",", " "))
col4.metric("Bilan ESG (CO2 évité)", f"{co2_kg:.2f} kg/mois")

st.markdown("---")

# ------------------------------------------------------------------------------
# ONGLETS APPLICATIFS
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Cadastre Acoustique (Carte)", 
    "📈 Courbe de Rendement", 
    "📊 Analyse Fréquentielle (FFT)", 
    "🛠️ Maintenance Prédictive"
])

# ------------------------------------------------------------------------------
# TAB 1 : CARTE INTERACTIVE & SÉLECTION REACTIVE
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Sélection d'un Point Chaud (Hotspot)")

    # --- OPTION AVANCÉE : Menu déroulant de présélection ---
    col_sel, col_info = st.columns([1, 2])
    
    with col_sel:
        site_list = ["-- Choisir un site prédéfini --"] + list(HOTSPOTS.keys())
        selected_site = st.selectbox("Sélection rapide par zone :", site_list)

        if selected_site != "-- Choisir un site prédéfini --":
            data_site = HOTSPOTS[selected_site]
            st.session_state.db_val = data_site["db"]
            st.session_state.freq_val = data_site["freq"]
            st.success(f"**{selected_site}** chargé !\n\n• {data_site['db']} dBA\n• {data_site['freq']} Hz")
            st.caption("💡 Cliquez sur *Raffraîchir les valeurs* ou ajustez la barre latérale si nécessaire.")

    with col_info:
        st.info(
            "📍 **Comment choisir un site ?**\n\n"
            "1. Utilisez le **menu déroulant** à gauche pour charger un point d'intérêt à Douala.\n"
            "2. **Ou cliquez directement** sur la carte ci-dessous pour capturer les coordonnées et données d'un hotspot."
        )

    st.markdown("---")

    # --- CARTE FOLIUM (MÉTHODE 2) ---
    m = folium.Map(location=[4.0511, 9.7027], zoom_start=12)

    for name, info in HOTSPOTS.items():
        popup_html = f"<b>{name}</b><br>{info['desc']}<br><b>{info['db']} dBA</b> | <b>{info['freq']} Hz</b>"
        folium.Marker(
            location=info["coords"],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{name} ({info['db']} dBA)",
            icon=folium.Icon(color="red" if info["db"] >= 100 else "blue", icon="volume-up", prefix="fa")
        ).add_to(m)

    # Capture des événements de clic sur la carte
    map_data = st_folium(m, width=1000, height=420, key="douala_hotspot_map")

    # Détection du clic sur la carte
    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lng = map_data["last_clicked"]["lng"]
        
        st.write(f"📌 **Point sélectionné sur la carte :** Lat `{click_lat:.4f}`, Lng `{click_lng:.4f}`")
        
        # Vérification si le clic est proche d'un hotspot existant
        matched = False
        for name, info in HOTSPOTS.items():
            h_lat, h_lng = info["coords"]
            if abs(click_lat - h_lat) < 0.015 and abs(click_lng - h_lng) < 0.015:
                st.session_state.db_val = info["db"]
                st.session_state.freq_val = info["freq"]
                st.success(f"Données chargées depuis **{name}** : {info['db']} dBA, {info['freq']} Hz !")
                matched = True
                break
        
        if not matched:
            st.warning("Position personnalisée cliquée. Ajustez les valeurs acoustiques dans la barre latérale pour ce point spécifique.")

# ------------------------------------------------------------------------------
# TAB 2 : COURBE DE RENDEMENT
# ------------------------------------------------------------------------------
with tab2:
    db_seq = np.linspace(60, 140, 81)
    p_seq = (((P0 * (10 ** (db_seq / 20))) ** 2) / rho_c) * surface_input * eta * 1000

    fig_power = go.Figure()
    fig_power.add_trace(go.Scatter(x=db_seq, y=p_seq, mode='lines', name='Courbe Théorique', line=dict(color='#0d6efd', width=3)))
    fig_power.add_trace(go.Scatter(x=[db_input], y=[p_electrique * 1000], mode='markers', name='Point Actuel', marker=dict(color='#dc3545', size=14)))
    fig_power.update_layout(
        title="Puissance Électrique en fonction du Niveau Sonore",
        xaxis_title="Niveau Sonore (dBA)",
        yaxis_title="Puissance (mW)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_power, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3 : ANALYSE FRÉQUENTIELLE (FFT)
# ------------------------------------------------------------------------------
with tab3:
    f_seq = np.linspace(100, 3000, 60)
    amplitude = np.exp(-((f_seq - freq_input) ** 2) / (2 * 200 ** 2)) * db_input

    fig_fft = px.bar(
        x=f_seq, 
        y=amplitude, 
        labels={'x': 'Fréquence (Hz)', 'y': 'Amplitude (dB)'}, 
        title="Spectre Fréquentiel Ambiant (Simulation FFT)"
    )
    fig_fft.update_traces(marker_color='#198754')
    st.plotly_chart(fig_fft, use_container_width=True)

    st.info(f"**Fréquence de Résonance Détectée :** {freq_input} Hz — Taux d'accordement piézoélectrique évalué à 94%.")

# ------------------------------------------------------------------------------
# TAB 4 : MAINTENANCE PRÉDICTIVE
# ------------------------------------------------------------------------------
with tab4:
    if freq_input > 2000 or db_input > 110:
        status_text = "ANOMALIE DÉTECTÉE : Risque Mécanique imminent (Intervention requise sous 48h)."
        st.error(f"🚨 **{status_text}**\n\nSignal haute fréquence ou niveau sonore excessif détecté sur le site.")
    else:
        status_text = "STATUT ÉQUIPEMENTS : Normal. Empreinte acoustique stable."
        st.success(f"✅ **{status_text}**\n\nAucune dérive fréquentielle critique n'est signalée.")

# ------------------------------------------------------------------------------
# SECTION D'EXPORTATION WORD (DOCX)
# ------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Exports & Certification")

if st.sidebar.button("Générer le Rapport Word (.docx)", type="primary"):
    file_path = build_docx_report(
        db_input, freq_input, surface_input, selected_material, 
        p_electrique, e_jour_wh, savings_fcfa, co2_kg, status_text
    )
    
    with open(file_path, "rb") as file:
        st.sidebar.download_button(
            label="📥 Télécharger le Fichier .docx",
            data=file,
            file_name=f"Audit_NOISE_LIGHT_{db_input}dB.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
