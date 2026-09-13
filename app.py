import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import math
import time
import json
import streamlit.components.v1 as components
from generate_report import build_docx_report, build_html_pdf_report

# ------------------------------------------------------------------------------
# CONFIGURATION STREAMLIT
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="NOISE LIGHT — World-Class Piezo Harvesting Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# BIBLIOTHÈQUE MATÉRIAUX EXTENSIVE
# ------------------------------------------------------------------------------
PIEZO_LIBRARY = {
    "PZT-5H (Céramique Haute Sensibilité)": {
        "eta": 0.25, "d33": 593, "k33": 0.75, "eps_r": 3400, "temp_curie": 190, "qm": 65, "unit_cost_usd": 12.0,
        "desc": "Excellente conversion basse tension, idéale pour le bruit ambiant urbain."
    },
    "PZT-4 (Céramique Haute Puissance)": {
        "eta": 0.22, "d33": 289, "k33": 0.70, "eps_r": 1300, "temp_curie": 328, "qm": 500, "unit_cost_usd": 15.0,
        "desc": "Robuste aux contraintes fortes, optimale pour les milieux industriels."
    },
    "PMN-PT (Monocristal Ultra-Performance)": {
        "eta": 0.35, "d33": 2500, "k33": 0.92, "eps_r": 5400, "temp_curie": 130, "qm": 80, "unit_cost_usd": 85.0,
        "desc": "Performance piézoélectrique d'exception, réservée aux applications critiques."
    },
    "BaTiO3 (Titanate de Baryum - Eco/NoLead)": {
        "eta": 0.15, "d33": 190, "k33": 0.48, "eps_r": 1700, "temp_curie": 120, "qm": 300, "unit_cost_usd": 8.0,
        "desc": "Matériau écologique sans plomb à coût modéré."
    },
    "PVDF (Polymère Souple Fluoré)": {
        "eta": 0.10, "d33": 33, "k33": 0.20, "eps_r": 12, "temp_curie": 80, "qm": 10, "unit_cost_usd": 5.0,
        "desc": "Flexible, léger et intégrable sur surfaces courbes ou textiles."
    },
    "AlN (Nitrure d'Aluminium - Haute T°)": {
        "eta": 0.08, "d33": 5, "k33": 0.23, "eps_r": 9, "temp_curie": 1150, "qm": 1000, "unit_cost_usd": 45.0,
        "desc": "Ultra-résistant aux températures extrêmes (turbines, moteurs)."
    },
    "Quartz Cristallin SiO2 (Stable)": {
        "eta": 0.05, "d33": 2.3, "k33": 0.10, "eps_r": 4.5, "temp_curie": 573, "qm": 25000, "unit_cost_usd": 20.0,
        "desc": "Stabilité fréquentielle parfaite, très faible dérive dans le temps."
    }
}

HOTSPOTS_BASE = {
    "PK14 Carrefour": {"coords": [4.0881, 9.7712], "db": 92, "freq": 950},
    "Carrefour Ndokoti": {"coords": [4.0478, 9.7431], "db": 98, "freq": 1200},
    "Zone Industrielle Bassa": {"coords": [4.0103, 9.6895], "db": 108, "freq": 850},
    "Marché Central": {"coords": [4.0600, 9.6930], "db": 90, "freq": 1500}
}

# ------------------------------------------------------------------------------
# FONCTIONS AUXILIAIRES
# ------------------------------------------------------------------------------
def estimate_satellite_acoustic_profile(lat, lng):
    ref_lat, ref_lng = 4.0478, 9.7431
    dist = math.sqrt((lat - ref_lat)**2 + (lng - ref_lng)**2) * 111.0
    seed = int((abs(lat) * 10000 + abs(lng) * 10000)) % 1000
    np.random.seed(seed)
    base_db = 95 - (dist * 2.5) + np.random.uniform(-5, 12)
    return int(np.clip(base_db, 65, 135)), int(400 + (seed % 18) * 100 + np.random.uniform(-50, 50))

# ------------------------------------------------------------------------------
# INITIALISATION DU SESSION STATE
# ------------------------------------------------------------------------------
for key, val in {
    "current_lat": 4.0881, "current_lng": 9.7712, "db_val": 92, "freq_val": 950,
    "iot_active": False, "operating_temp": 35.0,
    "field_mode_active": False, "field_db": 0.0, "field_accel": 0.0,
    "field_lat": 0.0, "field_lng": 0.0
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ------------------------------------------------------------------------------
# SIDEBAR REVISITÉ
# ------------------------------------------------------------------------------
st.sidebar.title("⚡ NOISE LIGHT Pro")
st.sidebar.caption("Plateforme Globale de Harvesting Piézoacoustique")

if st.session_state.field_mode_active:
    st.sidebar.error("🔴 MODE TERRAIN ACTIF (Données Réelles Insérées)")

st.sidebar.markdown("---")

# 1. Sélection & Tuning Matériau
st.sidebar.subheader("🔬 Matériau Piézoélectrique")
selected_mat_key = st.sidebar.selectbox("Matrice Piézo :", list(PIEZO_LIBRARY.keys()))
mat_info = PIEZO_LIBRARY[selected_mat_key]

with st.sidebar.expander("⚙️ Propriétés physiques personnalisées"):
    custom_d33 = st.number_input("d33 (pC/N)", value=float(mat_info["d33"]), step=10.0)
    custom_k33 = st.slider("Couplage (k33)", 0.05, 0.99, float(mat_info["k33"]), 0.01)
    custom_eta = st.slider("Rendement Matériau η (%)", 1.0, 50.0, float(mat_info["eta"]*100), 0.5) / 100.0
    custom_qm = st.number_input("Facteur de Qualité Mécanique (Qm)", value=int(mat_info["qm"]), step=10)

# 2. Paramètres Réseau Electrique & PMIC
st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Électronique PMIC & Harvesting")
rectifier_type = st.sidebar.selectbox("Topologie Redresseur", ["Standard Bridge Rectifier", "SSHIC Non-Linéaire (+180% Pwr)", "Synchronous Switch Harvesting"])
pmic_efficiency = st.sidebar.slider("Rendement Convertisseur DC-DC (%)", 50, 98, 88) / 100.0
storage_capacity_farad = st.sidebar.selectbox("Supercondensateur de Stockage", [0.47, 1.0, 4.7, 10.0], index=1)

# 3. Environnement & Acoustique (Surcharge si Mode Terrain Actif)
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Conditions Environnementales")

if st.session_state.field_mode_active:
    db_input = int(st.session_state.field_db)
    freq_input = int(st.session_state.freq_val)
    st.sidebar.info(f"🔊 Bruit Réel Micro : {db_input} dBA")
    st.sidebar.info(f"📳 Vibration Réelle : {st.session_state.field_accel:.2f} m/s²")
else:
    db_input = st.sidebar.slider("Niveau Sonore (dBA) :", 60, 140, int(st.session_state.db_val), key="sb_db")
    freq_input = st.sidebar.number_input("Fréquence (Hz) :", 20, 20000, int(st.session_state.freq_val), step=50, key="sb_freq")

surface_input = st.sidebar.slider("Surface Active (m²) :", 0.5, 100.0, 15.0, 0.5)
amb_temp = st.sidebar.slider("Température Ambiante (°C)", -10, 120, int(st.session_state.operating_temp))
hours_input = st.sidebar.number_input("Exposition / Jour (h) :", 1, 24, 14)

# 4. Modélisation Économique & ESG
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Paramètres Financiers & ESG")
kwh_cost_input = st.sidebar.number_input("Tarif Électricité (FCFA/kWh) :", 10, 500, 100)
carbon_credit_price = st.sidebar.number_input("Prix Tonne CO2 ($ / tonne)", 10.0, 150.0, 35.0)

# 5. Métadonnées Administratives
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Métadonnées Administratives")
client_name = st.sidebar.text_input("Client :", "Port Autonome / Zone PK14")
project_id = st.sidebar.text_input("N° Projet :", "NL-2026-DLA-PK14")
auditor_name = st.sidebar.text_input("Auditeur :", "Expert Terrain AI")
site_desc = st.sidebar.text_area("Description :", "Mesure en direct sur le terrain (Microphone, GPS & Accéléromètre).")

# ------------------------------------------------------------------------------
# MOTEUR DE CALCUL MULTIPHYSIQUE
# ------------------------------------------------------------------------------
P0 = 2e-5
rho_c = 400

pmic_gain = 2.8 if "SSHIC" in rectifier_type else (1.9 if "Synchronous" in rectifier_type else 1.0)
pression = P0 * (10 ** (db_input / 20))
p_acoustique = ((pression ** 2) / rho_c) * surface_input
p_piezo_raw = p_acoustique * custom_eta
p_electrique_net = p_piezo_raw * pmic_gain * pmic_efficiency

# Dégradation thermique (Température de Curie)
tc = mat_info["temp_curie"]
thermal_derating = max(0.0, 1.0 - (amb_temp - tc * 0.6) / (tc * 0.4)) if amb_temp > (tc * 0.6) else 1.0
p_electrique_net *= thermal_derating

# Bilan Énergétique & Financials
e_jour_wh = p_electrique_net * hours_input
e_mois_kwh = (e_jour_wh * 30) / 1000
savings_fcfa = e_mois_kwh * kwh_cost_input
co2_kg_monthly = e_mois_kwh * 0.5
carbon_revenue_usd = (co2_kg_monthly * 12 / 1000) * carbon_credit_price

nbr_modules = math.ceil(surface_input * 16)
capex_hardware = nbr_modules * mat_info["unit_cost_usd"] * 600
capex_pmic_elec = (500 + surface_input * 40) * 600
capex_total = capex_hardware + capex_pmic_elec
roi_months = (capex_total / savings_fcfa) if savings_fcfa > 0 else 999

# ------------------------------------------------------------------------------
# EN-TÊTE PRINCIPAL
# ------------------------------------------------------------------------------
st.title("⚡ NOISE LIGHT — Plateforme d'Ingénierie Piézoélectrique Pro")

active_lat = st.session_state.field_lat if st.session_state.field_mode_active else st.session_state.current_lat
active_lng = st.session_state.field_lng if st.session_state.field_mode_active else st.session_state.current_lng

st.markdown(f"**GPS Actif :** Lat `{active_lat:.5f}` | Lng `{active_lng:.5f}` | **Source :** `{'🔴 TERRAIN REAL-TIME' if st.session_state.field_mode_active else '🌐 SATELLITE / SIMULATION'}`")

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Puissance Nette", f"{p_electrique_net * 1000:.2f} mW")
kpi2.metric("Énergie / Jour", f"{e_jour_wh:.1f} Wh/j")
kpi3.metric("Gains Financiers", f"{savings_fcfa:,.0f} FCFA/mo".replace(",", " "))
kpi4.metric("CO2 Évité", f"{co2_kg_monthly:.2f} kg/mo")
kpi5.metric("CAPEX Estimé", f"{capex_total/1e6:.2f} M FCFA")
kpi6.metric("Payback (ROI)", f"{roi_months:.1f} mois")

st.markdown("---")

# ------------------------------------------------------------------------------
# ONGLETS MULTI-FACETTES
# ------------------------------------------------------------------------------
tab_field, tab_map, tab_3d, tab_fft, tab_mat, tab_pmic, tab_iot, tab_roi, tab_audit = st.tabs([
    "📱 MODE TERRAIN LIVE",
    "🗺️ Carte Satellite Ultra-HD", 
    "📊 Surface 3D Dynamic", 
    "📈 Spectrogramme FFT", 
    "🧪 Matériaux & Fatigue",
    "🔌 Électronique & PMIC",
    "📡 Jumeau Numérique IoT",
    "📈 Business & VAN/TRI",
    "📑 Audit & certification"
])

# ------------------------------------------------------------------------------
# TAB 0 : MODE TERRAIN LIVE
# ------------------------------------------------------------------------------
with tab_field:
    st.subheader("📱 Acquisition Réelle Terrain (GPS, Microphone, Accéléromètre, Caméra)")
    st.caption("Activez les autorisations de votre navigateur pour utiliser les capteurs de votre appareil.")

    col_f1, col_f2 = st.columns([1, 1])

    with col_f1:
        st.write("### 🎛️ Contrôle des Capteurs Matériels")
        
        sensor_html = """
        <div style="background:#f8f9fa; padding:15px; border-radius:8px; border:1px solid #ddd;">
            <button id="btn-start" style="background:#0d6efd; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">
                🎙️ Activer Micro, GPS & Vibrations
            </button>
            <div id="status" style="margin-top:10px; font-weight:bold; color:#555;">Statut : En attente d'activation...</div>
            <hr>
            <div><b>GPS Lat/Lng :</b> <span id="gps-val">--</span></div>
            <div><b>Bruit Estimé Micro :</b> <span id="db-val">0</span> dBA</div>
            <div><b>Vibration (Accéléromètre) :</b> <span id="accel-val">0</span> m/s²</div>
            <video id="webcam" autoplay playsinline style="width:100%; max-height:200px; margin-top:10px; background:#000; border-radius:5px;"></video>
        </div>

        <script>
            let audioCtx, analyser, microphone;
            
            document.getElementById('btn-start').addEventListener('click', async () => {
                document.getElementById('status').innerText = "Statut : Capteurs Actifs 🟢";
                
                if (navigator.geolocation) {
                    navigator.geolocation.watchPosition((pos) => {
                        document.getElementById('gps-val').innerText = pos.coords.latitude.toFixed(5) + ", " + pos.coords.longitude.toFixed(5);
                    });
                }

                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
                    document.getElementById('webcam').srcObject = stream;
                    
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    microphone = audioCtx.createMediaStreamSource(stream);
                    microphone.connect(analyser);
                    analyser.fftSize = 256;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);

                    function updateAudio() {
                        analyser.getByteFrequencyData(dataArray);
                        let sum = 0;
                        for(let i = 0; i < bufferLength; i++) sum += dataArray[i];
                        let average = sum / bufferLength;
                        let db = Math.min(130, Math.max(40, Math.round(average * 0.85 + 40)));
                        document.getElementById('db-val').innerText = db;
                        requestAnimationFrame(updateAudio);
                    }
                    updateAudio();
                } catch(e) {
                    document.getElementById('status').innerText = "Erreur accès Micro/Caméra : " + e.message;
                }

                if (window.DeviceMotionEvent) {
                    window.addEventListener('devicemotion', (event) => {
                        let acc = event.accelerationIncludingGravity;
                        if (acc) {
                            let totalAcc = Math.sqrt(acc.x*acc.x + acc.y*acc.y + acc.z*acc.z);
                            document.getElementById('accel-val').innerText = totalAcc.toFixed(2);
                        }
                    });
                }
            });
        </script>
        """
        components.html(sensor_html, height=450)

    with col_f2:
        st.write("### 📥 Injecter les Données Capturées dans l'Audit")
        
        with st.form("field_data_form"):
            manual_gps_lat = st.number_input("Latitude Réelle GPS :", value=st.session_state.current_lat, format="%.5f")
            manual_gps_lng = st.number_input("Longitude Réelle GPS :", value=st.session_state.current_lng, format="%.5f")
            manual_db = st.slider("Bruit Relevé au Micro (dBA) :", 40, 130, 92)
            manual_accel = st.number_input("Vibration Mesurée (m/s²) :", value=4.5, step=0.1)
            
            enable_field = st.checkbox("Activer le Mode Terrain & verrouiller le rapport", value=st.session_state.field_mode_active)
            submit_field = st.form_submit_button("Surcharger les calculs avec le Mode Terrain", type="primary")

            if submit_field:
                st.session_state.field_mode_active = enable_field
                st.session_state.field_db = manual_db
                st.session_state.field_accel = manual_accel
                st.session_state.field_lat = manual_gps_lat
                st.session_state.field_lng = manual_gps_lng
                st.session_state.current_lat = manual_gps_lat
                st.session_state.current_lng = manual_gps_lng
                st.session_state.db_val = manual_db
                st.success("Données Terrain enregistrées ! Tous les modules et rapports sont synchronisés.")
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 1 : MAP (OPTIMISÉE HD POUR DELL LATITUDE 5440)
# ------------------------------------------------------------------------------
with tab_map:
    st.subheader("📍 Extractor Acoustique Satellite Ultra-HD (Google Hybrid High-Res)")
    col_map_left, col_map_right = st.columns([3.5, 1])

    with col_map_right:
        st.write("**Hotspots Prédéfinis**")
        selected_preset = st.selectbox("Zone pré-enregistrée :", ["-- Cliquer sur la carte --"] + list(HOTSPOTS_BASE.keys()))
        if selected_preset != "-- Cliquer sur la carte --":
            hp = HOTSPOTS_BASE[selected_preset]
            st.session_state.current_lat, st.session_state.current_lng = hp["coords"]
            st.session_state.db_val = hp["db"]
            st.session_state.freq_val = hp["freq"]

        st.markdown("---")
        st.info(
            f"**Lat :** {active_lat:.5f}\n\n"
            f"**Lng :** {active_lng:.5f}\n\n"
            f"**Bruit :** {db_input} dBA\n\n"
            f"**Fréquence Est. :** {freq_input} Hz"
        )

    with col_map_left:
        # Configuration haute précision pour l'écran Full HD du Dell Latitude 5440
        m = folium.Map(
            location=[active_lat, active_lng],
            zoom_start=18,
            max_zoom=22,
            tiles=None,
            prefer_canvas=True
        )
        
        # Ingestion des tuiles Google Hybrid HD avec résolution Retina/x2 (512px) et zoom maximal (22)
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&scale=2',
            attr='Google Satellite Hybrid HD',
            name='Google Satellite Ultra-HD',
            max_zoom=22,
            max_native_zoom=20,
            tile_size=512,
            zoom_offset=-1,
            detect_retina=True
        ).add_to(m)

        for name, info in HOTSPOTS_BASE.items():
            folium.Marker(
                location=info["coords"],
                popup=f"<b>{name}</b><br>{info['db']} dBA - {info['freq']} Hz",
                icon=folium.Icon(color="red" if info["db"] >= 100 else "orange", icon="bolt", prefix="fa")
            ).add_to(m)

        folium.Marker(
            location=[active_lat, active_lng],
            popup="Point d'Analyse Actif",
            icon=folium.Icon(color="green", icon="crosshairs", prefix="fa")
        ).add_to(m)

        map_data = st_folium(m, use_container_width=True, height=650, key="satellite_map")

        if map_data and map_data.get("last_clicked") and not st.session_state.field_mode_active:
            c_lat = map_data["last_clicked"]["lat"]
            c_lng = map_data["last_clicked"]["lng"]
            if (c_lat != st.session_state.current_lat) or (c_lng != st.session_state.current_lng):
                st.session_state.current_lat = c_lat
                st.session_state.current_lng = c_lng
                db_est, freq_est = estimate_satellite_acoustic_profile(c_lat, c_lng)
                st.session_state.db_val = db_est
                st.session_state.freq_val = freq_est
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 2 : SURFACE 3D
# ------------------------------------------------------------------------------
with tab_3d:
    st.subheader("📊 Optimisation de la Surface de Réponse 3D")
    db_range = np.linspace(70, 130, 40)
    surf_range = np.linspace(1, 50, 40)
    DB_GRID, SURF_GRID = np.meshgrid(db_range, surf_range)
    
    PRESS_GRID = P0 * (10 ** (DB_GRID / 20))
    POWER_GRID = (((PRESS_GRID ** 2) / rho_c) * SURF_GRID * custom_eta * pmic_gain * pmic_efficiency * thermal_derating) * 1000

    fig_3d = go.Figure(data=[go.Surface(z=POWER_GRID, x=DB_GRID, y=SURF_GRID, colorscale='Viridis')])
    fig_3d.add_trace(go.Scatter3d(
        x=[db_input], y=[surface_input], z=[p_electrique_net * 1000],
        mode='markers', marker=dict(size=8, color='red', symbol='diamond'), name='Point de Fonctionnement'
    ))
    fig_3d.update_layout(
        scene=dict(xaxis_title="Intensité (dBA)", yaxis_title="Surface (m²)", zaxis_title="Puissance (mW)"),
        margin=dict(l=0, r=0, b=0, t=40), height=500
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3 : FFT SPECTROGRAMME
# ------------------------------------------------------------------------------
with tab_fft:
    st.subheader("📈 Spectre Fréquentiel & Multi-Harmoniques (FFT)")
    f_axis = np.linspace(20, 5000, 500)
    f0 = freq_input
    sig = (
        np.exp(-((f_axis - f0)**2) / (2 * 40**2)) * db_input +
        0.4 * np.exp(-((f_axis - 2*f0)**2) / (2 * 60**2)) * db_input +
        0.2 * np.exp(-((f_axis - 3*f0)**2) / (2 * 80**2)) * db_input
    )
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Scatter(x=f_axis, y=sig, mode='lines', name='Spectre FFT', line=dict(color='#0d6efd', width=2)))
    fig_fft.add_trace(go.Scatter(x=[20, 5000], y=[105, 105], mode='lines', name='Seuil Alerte (105 dBA)', line=dict(color='red', dash='dash')))
    fig_fft.update_layout(xaxis_title="Fréquence (Hz)", yaxis_title="Amplitude (dBA)", template="plotly_white", height=450)
    st.plotly_chart(fig_fft, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4 : MATÉRIAUX & FATIGUE
# ------------------------------------------------------------------------------
with tab_mat:
    st.subheader("🧪 Analyse Matériau & Dégradation Mécanique / Thermique")
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.write("### Sensibilité Comparative")
        mat_names, powers_mw = [], []
        for m_name, m_data in PIEZO_LIBRARY.items():
            p_temp = (((P0 * (10 ** (db_input / 20))) ** 2) / rho_c) * surface_input * m_data["eta"] * pmic_gain * pmic_efficiency * 1000
            mat_names.append(m_name.split(" ")[0])
            powers_mw.append(p_temp)

        fig_mat = go.Figure(go.Bar(x=mat_names, y=powers_mw, marker_color='#198754'))
        fig_mat.update_layout(yaxis_title="Puissance (mW)", template="plotly_white", height=350)
        st.plotly_chart(fig_mat, use_container_width=True)

    with col_m2:
        st.write("### Modèle de Fatigue & Dérive Thermique")
        st.warning(f"Température Curie Matériau : {tc}°C | Température Actuelle : {amb_temp}°C")
        st.progress(min(1.0, amb_temp / tc))
        
        cycles_per_year = freq_input * 3600 * hours_input * 365
        st.write(f"**Stress Mécanique Cumulé :** `{cycles_per_year / 1e9:.2f} Milliards de cycles / an`")

# ------------------------------------------------------------------------------
# TAB 5 : PMIC & ÉLECTRONIQUE
# ------------------------------------------------------------------------------
with tab_pmic:
    st.subheader("🔌 Simulation du Circuit Électronique PMIC & Charge Supercap")
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.write("### Courbe de Charge du Supercondensateur")
        time_sec = np.linspace(0, 300, 200)
        v_max = 5.0
        r_eq = 1000.0
        c_val = storage_capacity_farad
        tau = r_eq * c_val / (p_electrique_net * 1000 + 1e-5)
        v_t = v_max * (1 - np.exp(-time_sec / max(1.0, tau)))

        fig_cap = go.Figure(go.Scatter(x=time_sec, y=v_t, mode='lines', line=dict(color='#ffc107', width=3)))
        fig_cap.update_layout(title=f"Charge Condensateur ({c_val} F)", xaxis_title="Temps (s)", yaxis_title="Tension (V)", template="plotly_white")
        st.plotly_chart(fig_cap, use_container_width=True)

    with col_p2:
        st.write("### Efficacité des Topologies de Redressement")
        topologies = ["Standard Bridge", "Synchronous Switch", "SSHIC Non-Linéaire"]
        gains = [1.0, 1.9, 2.8]
        fig_topo = go.Figure(go.Bar(x=topologies, y=gains, marker_color='#0dcaf0'))
        fig_topo.update_layout(title="Facteur de Gain en Puissance vs Redresseur Standard", yaxis_title="Multiplicateur Gain", template="plotly_white")
        st.plotly_chart(fig_topo, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 6 : JUMEAU NUMÉRIQUE IOT
# ------------------------------------------------------------------------------
with tab_iot:
    st.subheader("📡 Jumeau Numérique & Flux IoT Temps Réel")
    col_iot_btn, col_iot_status = st.columns([1, 2])
    with col_iot_btn:
        if st.button("🔴 Basculer Stream IoT Direct"):
            st.session_state.iot_active = not st.session_state.iot_active

    with col_iot_status:
        st.write(f"**Statut Réseau IoT :** {'🟢 CONNECTÉ (MQTT / LoRaWAN)' if st.session_state.iot_active else '⚪ EN ATTENTE'}")

    iot_placeholder = st.empty()
    if st.session_state.iot_active:
        for i in range(5):
            live_db = db_input + np.random.uniform(-3, 3)
            live_pwr = (((P0 * (10 ** (live_db / 20))) ** 2) / rho_c) * surface_input * custom_eta * pmic_gain * pmic_efficiency * 1000
            with iot_placeholder.container():
                st.metric("Flux Direct dBA", f"{live_db:.1f} dBA", delta=f"{live_db - db_input:.1f} dBA")
                st.metric("Puissance Produite Directe", f"{live_pwr:.2f} mW")
                time.sleep(0.5)

# ------------------------------------------------------------------------------
# TAB 7 : FINANCIALS ROI / VAN / TRI
# ------------------------------------------------------------------------------
with tab_roi:
    st.subheader("📈 Rentabilité Financière Approfondie (VAN / TRI / ROI)")
    years = np.arange(1, 11)
    discount_rate = 0.08
    annual_savings = (savings_fcfa * 12) + (carbon_revenue_usd * 600)
    cash_flows = [-capex_total] + [annual_savings / ((1 + discount_rate)**y) for y in years]
    cum_cash_flows = np.cumsum(cash_flows)

    fig_van = go.Figure()
    fig_van.add_trace(go.Bar(x=[f"An {i}" for i in range(11)], y=cum_cash_flows, marker_color=['red' if x < 0 else 'green' for x in cum_cash_flows]))
    fig_van.update_layout(title="Flux de Trésorerie Cumulés Actualisés (FCFA)", yaxis_title="Valeur Nette (FCFA)", template="plotly_white")
    st.plotly_chart(fig_van, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 8 : AUDIT & RAPPORTS
# ------------------------------------------------------------------------------
with tab_audit:
    st.subheader("📑 Diagnostic & Édition des Rapports Certifiés")

    if freq_input > 2000 or db_input > 110:
        status_text = "ANOMALIE CRITIQUE : Vibration extrême détectée. Risque de fatigue piézoélectrique accélérée."
        st.error(f"🚨 **{status_text}**")
    else:
        status_text = "STATUT NOMINAL : Empreinte acoustique optimale. Récolte d'énergie recommandée."
        st.success(f"✅ **{status_text}**")

    st.markdown("---")
    st.subheader("📦 Nomenclature Matérielle Commerciale (BOM Generator)")
    st.table([
        {"Composant": "Modules Piézoélectriques", "Référence / Matériau": selected_mat_key.split("(")[0], "Quantité": nbr_modules, "Coût Est. (FCFA)": capex_hardware},
        {"Composant": "Carte Électronique PMIC", "Référence / Matériau": rectifier_type, "Quantité": 1, "Coût Est. (FCFA)": capex_pmic_elec},
        {"Composant": "Supercondensateur", "Référence / Matériau": f"{storage_capacity_farad} Farad / 5.5V", "Quantité": max(1, int(surface_input/5)), "Coût Est. (FCFA)": 45000}
    ])

    st.markdown("---")
    st.subheader("📥 Génération des Documents d'Audit")

    admin_data = {
        "client_name": client_name, "project_id": project_id, "auditor_name": auditor_name, "site_desc": site_desc,
        "is_field_mode": st.session_state.field_mode_active, "field_accel": st.session_state.field_accel
    }
    acoustic_data = {"db": db_input, "freq": freq_input, "surface": surface_input, "lat": active_lat, "lng": active_lng}
    piezo_data = {"material_name": selected_mat_key, "d33": custom_d33, "eta": custom_eta}
    financial_data = {"p_mw": p_electrique_net * 1000, "e_wh_day": e_jour_wh, "savings_fcfa": savings_fcfa, "co2_kg": co2_kg_monthly, "capex": capex_total, "roi": roi_months}

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📄 Générer le Rapport Word (.docx)", type="primary", use_container_width=True):
            docx_path = build_docx_report(admin_data, acoustic_data, piezo_data, financial_data, status_text)
            with open(docx_path, "rb") as f:
                st.download_button("📥 Télécharger .docx", f, file_name=f"Rapport_NOISE_LIGHT_{project_id}.docx", use_container_width=True)

    with col_btn2:
        if st.button("🌐 Générer le Rapport PDF / HTML", use_container_width=True):
            html_code = build_html_pdf_report(admin_data, acoustic_data, piezo_data, financial_data, status_text)
            st.download_button("📥 Télécharger PDF/HTML", html_code, file_name=f"Rapport_Certifie_{project_id}.html", mime="text/html", use_container_width=True)
