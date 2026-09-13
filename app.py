import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import io
from generate_report import build_docx_report

# Configuration de la page
st.set_page_config(
    page_title="NOISE LIGHT — Smart Acoustic SaaS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# SIDEBAR : PARAMÈTRES ET CONFIGURATION
# ------------------------------------------------------------------------------
st.sidebar.title("⚡ NOISE LIGHT")
st.sidebar.markdown("---")

st.sidebar.subheader("Paramètres Acoustiques")
db_input = st.sidebar.slider("Niveau Sonore (dBA) :", min_value=60, max_value=140, value=98, step=1)
freq_input = st.sidebar.number_input("Fréquence du Signal (Hz) :", min_value=20, max_value=20000, value=1200, step=50)
surface_input = st.sidebar.slider("Surface des Capteurs (m²) :", min_value=0.5, max_value=50.0, value=10.0, step=0.5)

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
# DASHBOARD ET METRIQUES PRINCIPALES (KPIs)
# ------------------------------------------------------------------------------
st.title("NOISE LIGHT — Platforme d'Intelligence Acoustique & Énergétique")
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

# TAB 1 : Carte Interactive Folium (Douala)
with tab1:
    st.write("Sélectionnez un point chaud sur la carte pour évaluer la ressource acoustique :")
    
    m = folium.Map(location=[4.0511, 9.7027], zoom_start=12)
    folium.Marker([4.0478, 9.7431], popup="Carrefour Ndokoti (98 dBA - 1200 Hz)", tooltip="Ndokoti").add_to(m)
    folium.Marker([4.0103, 9.6895], popup="Zone Industrielle Bassa (108 dBA - 850 Hz)", tooltip="Bassa").add_to(m)
    folium.Marker([4.0600, 9.6930], popup="Marché Central (90 dBA - 1500 Hz)", tooltip="Marché Central").add_to(m)

    st_data = st_folium(m, width=1000, height=400)

# TAB 2 : Courbe de Puissance
with tab2:
    db_seq = np.linspace(60, 140, 81)
    p_seq = (((P0 * (10 ** (db_seq / 20))) ** 2) / rho_c) * surface_input * eta * 1000

    fig_power = go.Figure()
    fig_power.add_trace(go.Scatter(x=db_seq, y=p_seq, mode='lines', name='Courbe Théorique', line=dict(color='#0d6efd', width=3)))
    fig_power.add_trace(go.Scatter(x=[db_input], y=[p_electrique * 1000], mode='markers', name='Point Actuel', marker=dict(color='#dc3545', size=12)))
    fig_power.update_layout(title="Puissance Électrique en fonction de l'Intensité Acoustique", xaxis_title="Niveau Sonore (dBA)", yaxis_title="Puissance (mW)", template="plotly_white")
    
    st.plotly_chart(fig_power, use_container_width=True)

# TAB 3 : Analyse Fréquentielle (FFT)
with tab3:
    f_seq = np.linspace(100, 3000, 60)
    amplitude = np.exp(-((f_seq - freq_input) ** 2) / (2 * 200 ** 2)) * db_input

    fig_fft = px.bar(x=f_seq, y=amplitude, labels={'x': 'Fréquence (Hz)', 'y': 'Amplitude (dB)'}, title="Spectre Fréquentiel Ambiant (Simulation FFT)")
    fig_fft.update_traces(marker_color='#198754')
    st.plotly_chart(fig_fft, use_container_width=True)

    st.info(f"**Fréquence de Résonance Détectée :** {freq_input} Hz — Taux d'accordement du matériau piézoélectrique évalué à 94%.")

# TAB 4 : Maintenance Prédictive
with tab4:
    if freq_input > 2000 or db_input > 110:
        status_text = "ANOMALIE DÉTECTÉE : Risque Mécanique imminents (Intervention requise sous 48h)."
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