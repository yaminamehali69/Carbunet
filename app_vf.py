import streamlit as st
import pandas as pd
import requests
import os
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import base64
import urllib.parse
import streamlit.components.v1 as components
from datetime import datetime

# --- 1. CONFIGURATION UNIQUE ---
LOGO_URL = "https://raw.githubusercontent.com/yaminamehali69/Carbunet/main/logo_carbunet.png"
path_logo = "logo_carbunet.png"
path_csv = "https://raw.githubusercontent.com/yaminamehali69/Carbunet/main/carburant_prix_nettoye.csv"
VERSION = "1.3.9"
AUTEUR = "Yamina Mehali"
AUTEUR_2 = "CarbuNet"

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CarbuNet", 
    layout="centered",
    page_icon=LOGO_URL
)

# --- 4. PRÉPARATION LOGO ---
@st.cache_data
def get_logo_base64(url):
    try:
        response = requests.get(url, timeout=5)
        return base64.b64encode(response.content).decode()
    except: return ""

logo_data = get_logo_base64(LOGO_URL)

# --- 5. FIX VISUEL & CSS (VERSION NETTOYÉE) ---

# Le Script (JS) : On l'isole pour qu'il ne crée pas de marge
components.html(f"""
    <script>
        window.parent.document.title = "CarbuNet";
        var link = window.parent.document.querySelector("link[rel*='icon']") || window.parent.document.createElement('link');
        link.type = 'image/png'; link.rel = 'icon';
        link.href = 'data:image/png;base64,{logo_data}';
        window.parent.document.getElementsByTagName('head')[0].appendChild(link);

        const hide = () => {{
            const el = window.parent.document.querySelectorAll('.stAppToolbar, .stDeployButton, [data-testid="stStatusWidget"]');
            el.forEach(e => {{ e.style.display = 'none'; }});
        }};
        setInterval(hide, 1000);
    </script>
""", height=0)

# Le Style (CSS) : On force la suppression des marges Streamlit
st.markdown("""
    <style>
        /* On supprime le header Streamlit vide */
        header {visibility: hidden;}
        
        /* On remonte tout le contenu vers le haut */
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            margin-top: -30px !important;
        }

        /* Responsive pour la boîte Hero */
        .hero-container {
            width: 100% !important;
            box-sizing: border-box !important;
        }

        @media (max-width: 640px) {
            .hero-container h1 { font-size: 1.6rem !important; }
            .hero-container p { font-size: 1.1rem !important; }
            .main .block-container { padding-top: 0rem !important; }
        }
    </style>
""", unsafe_allow_html=True)

# --- DICTIONNAIRE DES LOGOS/EMOJIS ---
LOGOS_SERVICES = {
    "Aire de camping-cars": "🚐", "Automate CB 24/24": "🏪", "Bar": "🍸", 
    "Bornes électriques": "⚡", "Boutique alimentaire": "🛒", "Boutique non alimentaire": "🛍️", 
    "Carburant additivé": "🧪", "DAB (Distributeur automatique de billets)": "🏧", 
    "Douches": "🚿", "Espace bébé": "🍼", "GNV": "🍃", "Lavage automatique": "🧼", 
    "Lavage manuel": "🧽", "Laverie": "🧺", "Location de véhicule": "🔑", 
    "Piste poids lourds": "🚛", "Relais colis": "📦", "Restauration à emporter": "🥡", 
    "Restauration sur place": "🍽️", "Services réparation / entretien": "🔧", 
    "Station de gonflage": "💨", "Toilettes publiques": "🚻", "Vente d'additifs carburants": "⚗️", 
    "Vente de fioul domestique": "🔥", "Vente de gaz domestique (Butane/Propane)": "🎈", 
    "Vente de pétrole lampant": "🛢️", "Wifi": "📶"
}

st.markdown("""
<style>
    div[data-testid="stAppViewBlockContainer"] { opacity: 1 !important; }
    .block-container { padding-top: 1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }
    @media (max-width: 640px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 10px !important; }
        iframe { width: 100% !important; min-width: 100% !important; }
        h1, h2 { font-size: 1.4rem !important; word-wrap: break-word; }
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; overflow-x: auto !important; -webkit-overflow-scrolling: touch; }
    .stTabs [data-baseweb="tab"] { height: 40px; background-color: #f1f5f9; border-radius: 10px; padding: 4px 15px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; }
    .hero-container { background: linear-gradient(135deg, #1a73e8 0%, #32CD32 100%); border-radius: 20px; padding: 25px 20px; text-align: center; color: white; width: 100%; box-sizing: border-box; }
    .disclaimer-text { font-size: 0.7rem; opacity: 0.85; line-height: 1.2; width: 100%; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def charger_donnees():
    try:
        df = pd.read_csv(path_csv, sep=',', low_memory=False)
        for c in ['prix_gazole', 'prix_sp95', 'prix_sp98', 'prix_e10', 'prix_e85']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
        return df
    except: return None

df = charger_donnees()

# --- 1. LA FONCTION DE TRACKING (A mettre en haut de ton fichier) ---
def log_to_sheets(nom_onglet, ville="N/A", carburant="N/A"):
    # URL de ton formulaire spécifique
    url = "https://docs.google.com/forms/d/1FRdR-I7TUAi6drgMY3lSCuODhkogY3vtsGpFJhVr3wk/edit#responses"
    
    # Date et heure actuelle
    horodatage = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # On utilise TES numéros entry.XXXX trouvés dans ton lien
    data = {
        "entry.444917946": horodatage,  # Date et Heure
        "entry.15775607": nom_onglet,   # Onglet
        "entry.116783663": ville,       # Ville
        "entry.2094833025": carburant   # Carburant
    }
    
    try:
        # Envoi silencieux à Google Sheets
        requests.post(url, data=data)
    except:
        pass


# --- NAVIGATION ---
tabs = st.tabs([" Concept", " Stations", " Simulateur", " Support & Bugs"])


# --- ONGLET 0 : CONCEPT ---
# --- ONGLET 0 : CONCEPT ---
with tabs[0]:
    log_to_sheets("Concept")
    
    logo_src = f"data:image/png;base64,{logo_data}" if logo_data else LOGO_URL
    
    st.markdown(f"""
    <div class="hero-container" style="
        background: linear-gradient(135deg, #1a73e8 0%, #32CD32 100%);
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        color: white;
        margin-bottom: 20px;">
        <img src="{logo_src}" width="160" style="margin-bottom: 15px;">
        <h1 style="color: white; border: none; margin: 0; font-size: 2.2rem;">CarbuNet</h1>
        <p style="font-size: 1.3rem; opacity: 0.95; margin-top: 10px;">Le prix le plus net, au kilomètre près.</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">
        <p style="font-size: 0.75rem; opacity: 0.8;">Mention d'information : Données data.gouv.fr.</p>
        <p style="font-size: 0.8rem; margin-top: 10px;">Version {VERSION} | Développé par Yamina Mehali</p>
    </div>
    """, unsafe_allow_html=True)
    
# --- ONGLET 1 : STATIONS ---

# --- ONGLET 1 : STATIONS ---
with tabs[1]:
    # 1. TRACKING : On enregistre que l'utilisateur est sur l'onglet Stations
    log_to_sheets("Stations")

    # --- TON CODE EXISTANT ---
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    if 'recherche_lancee' not in st.session_state:
        st.session_state.recherche_lancee = False

    if df is not None:
        # 1. LE FORMULAIRE DE RECHERCHE
        with st.form("recherche_stations_form"):
            adresse = st.text_input("📍 Où cherchez-vous ?", placeholder="Ville ou adresse...", key="input_stations")
            c1, c2 = st.columns(2)
            with c1:
                carbu = st.selectbox("Type de carburant", ["Gazole", "SP95", "SP98", "E10", "E85"])
                col_p, col_m = f"prix_{carbu.lower()}", f"prix_{carbu.lower()}_maj"
            with c2:
                rayon = st.select_slider("Rayon (km)", options=[1, 2, 5, 10, 20], value=5)

            # AJOUT DE LA PARTIE SERVICES
            with st.expander("⚙️ Filtrer par services (Boutique, Lavage, etc.)"):
                cols_srv = st.columns(2)
                selection_services = []
                for i, (srv_name, emoji) in enumerate(LOGOS_SERVICES.items()):
                    if cols_srv[i % 2].checkbox(f"{emoji} {srv_name}"):
                        selection_services.append(srv_name)
            
            submit_search = st.form_submit_button("🔍 CHERCHER LES STATIONS", use_container_width=True)

        # 2. TRACKING & ACTION LORS DE LA RECHERCHE
        if submit_search and adresse:
            # ON LOGUE LA RECHERCHE DANS GOOGLE SHEET AVEC LA VILLE ET LE CARBURANT
            log_to_sheets("Recherche Active", ville=adresse, carburant=carbu)
            
            st.session_state.recherche_lancee = True

        # 3. AFFICHAGE DES RÉSULTATS
        if st.session_state.recherche_lancee and adresse:
            with st.spinner("Analyse en cours..."):
                geolocator = Nominatim(user_agent="carbunet_pro_v5")
                try:
                    loc = geolocator.geocode(adresse + ", France")
                    if loc:
                        ma_pos = (loc.latitude, loc.longitude)
                        df_c = df[df[col_p] > 0].dropna(subset=[col_p, 'latitude', 'longitude']).copy()
                        df_c['distance'] = df_c.apply(lambda r: geodesic(ma_pos, (r['latitude'], r['longitude'])).km, axis=1)
                        res = df_c[df_c['distance'] <= rayon].copy()

                        # Filtrage par services sélectionnés
                        for s_filtre in selection_services:
                            res = res[res['service_propose'].str.contains(s_filtre, na=False, case=False)]

                        res = res.sort_values(by=col_p)

                        if not res.empty:
                            st.markdown("---")
                            # Mémoire pour le simulateur
                            stations_trouvees = {f"{row['adresse']} ({row[col_p]}€)": row[col_p] for _, row in res.head(8).iterrows()}
                            choix_station = st.selectbox("🎯 Choisir cette station pour le simulateur :", options=list(stations_trouvees.keys()))
                            
                            st.session_state['prix_perso'] = stations_trouvees[choix_station]
                            st.session_state['carbu_nom'] = carbu
                            st.session_state['station_nom'] = choix_station.split('(')[0].strip()
                            
                            st.success(f"✅ Station mémorisée : {st.session_state['prix_perso']} €/L")

                            # 1. CARTE
                            m = folium.Map(location=ma_pos, zoom_start=13, tiles="cartodbpositron")
                            p_min = res[col_p].min()
                            for _, r in res.head(10).iterrows():
                                color = 'green' if r[col_p] == p_min else 'blue'
                                folium.Marker([r['latitude'], r['longitude']], icon=folium.Icon(color=color, icon='gas-pump', prefix='fa')).add_to(m)
                            st_folium(m, width="100%", height=400)

                            st.markdown("### 🏆 Meilleures options trouvées")

                            # 2. BOUCLE D'AFFICHAGE UNIQUE
                            for _, row in res.head(8).iterrows():
                                w_url = f"https://waze.com/ul?ll={row['latitude']},{row['longitude']}&navigate=yes"
                                rupt = str(row.get('carburants_en_rupture_temporaire', '')) + str(row.get('carburants_en_rupture_definitive', ''))
                                stock_t, stock_c = ("❌ RUPTURE", "#ef4444") if carbu in rupt else ("✅ EN STOCK", "#10b981")
                                border_color = "#10b981" if row[col_p] == p_min else "#e2e8f0"
                                
                                # Génération des badges de services
                                srv_str = str(row.get('service_propose', ''))
                                badges_html = ""
                                if srv_str and srv_str != 'nan':
                                    for s in srv_str.split(','):
                                        s = s.strip()
                                        emoji = LOGOS_SERVICES.get(s, "🔹")
                                        badges_html += f'<span style="display:inline-block; font-size:10px; background:#f1f5f9; padding:2px 8px; border-radius:20px; margin:2px; color:#64748b; border:1px solid #e2e8f0;">{emoji} {s}</span>'

                                card_html = f"""
                                <div style="background:#fff; border-radius:12px; padding:15px; margin-bottom:12px; border:2px solid {border_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                    <div style="display:flex; justify-content:space-between; align-items:start;">
                                        <span style="font-size:1.6rem; font-weight:800; color:#0f172a;">{float(row[col_p]):.3f} €</span>
                                        <div style="text-align:right;">
                                            <span style="background:#0f172a; color:white; padding:3px 10px; border-radius:8px; font-size:0.85rem; font-weight:bold;">{row['distance']:.1f} km</span>
                                            <div style="color:{stock_c}; font-weight:bold; font-size:0.75rem; margin-top:4px;">{stock_t}</div>
                                        </div>
                                    </div>
                                    <div style="font-size:0.95rem; margin:8px 0; color:#334155;"><b>{row['adresse'].title()}</b> ({row['ville']})</div>
                                    <div style="margin: 10px 0; display: flex; flex-wrap: wrap;">{badges_html}</div>
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; border-top:1px solid #f8fafc; padding-top:10px;">
                                        <small style="color:#94a3b8; font-size:0.7rem;">MàJ : {row[col_m]}</small>
                                        <a href="{w_url}" target="_blank" style="color:#1a73e8; font-weight:bold; text-decoration:none; font-size:0.85rem;">WAZE 🚗</a>
                                    </div>
                                </div>
                                """
                                st.markdown(card_html, unsafe_allow_html=True)
                        else:
                            st.warning("Aucune station trouvée.")
                    else:
                        st.error("Lieu non reconnu.")
                except Exception as e:
                    st.error(f"Erreur technique : {e}")



# --- ONGLET 2 : SIMULATEUR ---
with tabs[2]:
    # 1. TRACKING : On enregistre l'arrivée sur le simulateur
    log_to_sheets("Simulateur")

    # INITIALISATION PROPRE
    if 'km_memoire' not in st.session_state:
        st.session_state['km_memoire'] = 0.0

    # --- TITRE HARMONISÉ ---
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #3b82f6; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #3b82f6;">calculate</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; border:none;">
                Simulateur de Budget Professionnel
            </h2>
        </div>
    """, unsafe_allow_html=True)



    # PRIX RÉCUPÉRÉ
    p_final = st.session_state.get('prix_perso', 1.859)
    nom_carbu = st.session_state.get('carbu_nom', 'Carburant')
    st.info(f" Prix actuel utilisé : **{p_final:.3f} €/L** ({nom_carbu})")

    # --- 1. ITINÉRAIRE ---
    st.markdown("##### 📍 1. Itinéraire")
    c1, c2 = st.columns(2)
    with c1:
        dep_v = st.text_input("Départ", placeholder="Ville ou adresse", key="cle_dep")
    with c2:
        arr_v = st.text_input("Arrivée", placeholder="Ville ou adresse", key="cle_arr")

    if st.button("🔍 CALCULER LA DISTANCE GPS", use_container_width=True):
        if dep_v and arr_v:
            try:
                with st.spinner("Calcul de l'itinéraire..."):
                    geolocator = Nominatim(user_agent="carbunet_pro_sim")
                    l1 = geolocator.geocode(dep_v)
                    l2 = geolocator.geocode(arr_v)
                    if l1 and l2:
                        dist_gps = geodesic((l1.latitude, l1.longitude), (l2.latitude, l2.longitude)).km
                        # On applique un coefficient de détour réel (25%)
                        st.session_state['km_memoire'] = round(dist_gps * 1.25, 1)
                        st.rerun() 
                    else:
                        st.error("❌ Adresse introuvable.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

    km_final = st.number_input("Distance retenue (km)", value=float(st.session_state['km_memoire']))

    # --- 2. PARAMÈTRES AVANCÉS (LE COEUR DU CALCUL) ---
    st.markdown("---")
    st.markdown("##### ⚙️ 2. Configuration du trajet")
    
    col_v, col_t = st.columns(2)
    with col_v:
        v_type = st.selectbox("Votre véhicule", ["Citadine", "Berline", "SUV", "Utilitaire"])
    with col_t:
        p_route = st.selectbox("Type de parcours", [
            "Urbain (100% Ville / Bouchons)", 
            "Mixte (Ville + Route)", 
            "Autoroute Éco (110 km/h)",
            "Autoroute Standard (130 km/h)"
        ], index=1)

    col_p, col_r = st.columns(2)
    with col_p:
        passagers = st.slider("Passagers / Charge", 1, 5, 1, help="+0.4L/100km par personne")
    with col_r:
        relief = st.selectbox("Relief", ["Plat", "Vallonné", "Montagne"])

    # --- LOGIQUE DE CONSOMMATION "BÉTON" ---
    # Base véhicule
    base_conso = {"Citadine": 5.2, "Berline": 6.5, "SUV": 7.8, "Utilitaire": 9.5}[v_type]
    
    # Impact du parcours
    impact_route = {
        "Urbain (100% Ville / Bouchons)": 2.8,
        "Mixte (Ville + Route)": 0.8,
        "Autoroute Éco (110 km/h)": 0.4,
        "Autoroute Standard (130 km/h)": 2.2
    }[p_route]

    # Impact Relief & Poids
    coeff_relief = {"Plat": 1.0, "Vallonné": 1.12, "Montagne": 1.35}[relief]
    poids_extra = (passagers - 1) * 0.4

    # Calcul final de la consommation
    conso_finale = (base_conso + impact_route + poids_extra) * coeff_relief

    # --- RÉSULTATS ---
    if km_final > 0:
        total_euros = (km_final / 100) * conso_finale * p_final
        # Ajout du coût d'usure (Pneus/Entretien) moyen FR : 0.12€/km
        cout_reel_total = total_euros + (km_final * 0.12)

        st.markdown("---")
        # BLOC INFO
        st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; text-align: center;">
                <p style="margin: 0; font-size: 0.9rem; color: #475569;">
                    Consommation estimée : <b>{conso_finale:.1f} L/100km</b><br>
                    Prix du carburant : <b>{p_final:.3f} €/L</b>
                </p>
            </div>
        """, unsafe_allow_html=True)

        # LE GROS CHIFFRE
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 30px; border-radius: 20px; text-align: center; color: white;">
                <p style="margin: 0; opacity: 0.7; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Budget Carburant</p>
                <h1 style="margin: 10px 0; font-size: 3.8rem; color: #4ade80; border:none; font-weight:800;">{total_euros:.2f} €</h1>
                <div style="border-top: 1px solid #334155; margin-top: 15px; padding-top: 15px;">
                    <p style="margin: 0; opacity: 0.6; font-size: 0.8rem;">COÛT RÉEL TOTAL (AVEC USURE) : <b>{cout_reel_total:.2f} €</b></p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # WAZE
        w_link = f"https://www.waze.com/ul?q={urllib.parse.quote(arr_v)}&from={urllib.parse.quote(dep_v)}&navigate=yes"
        st.markdown(f'<a href="{w_link}" target="_blank" style="text-decoration:none;"><div style="background:#33CCFF;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;margin-top:15px;">🚀 LANCER L\'ITINÉRAIRE SUR WAZE</div></a>', unsafe_allow_html=True)
# --- ONGLET 3 : SUPPORT ---
with tabs[3]:
    # 1. TRACKING : On enregistre l'arrivée sur l'onglet Support
    log_to_sheets("Support & Bugs")

    # Style des icônes
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    # Titre 
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #f59e0b; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #f59e0b;">contact_support</span>
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #0f172a; border:none;">Centre de Support CarbuNet</h2>
        </div>
    """, unsafe_allow_html=True)

    # --- LE FORMULAIRE CORRIGÉ POUR MOBILE ---
    contact_form_html = """
    <div id="form-container" style="font-family: sans-serif; max-width: 100%; overflow: hidden;">
        <div id="success-message" style="display: none; background-color: #d1fae5; color: #065f46; padding: 20px; border-radius: 10px; border: 1px solid #34d399; text-align: center;">
            <h3 style="margin:0;">✅ Message envoyé !</h3>
            <p style="margin:10px 0 0 0;">Merci pour votre retour, Carbunet vous répondra dans les plus brefs délais.</p>
        </div>

        <form id="support-form" action="https://formsubmit.co/ajax/minamhl@icloud.com" method="POST" style="background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-sizing: border-box;">
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_subject" value=" Nouveau message CarbuNet !">
            
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                <input type="text" name="name" placeholder=" Nom & Prénom" style="flex: 1; min-width: 200px; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box;" required>
                <input type="email" name="email" placeholder=" Votre Email" style="flex: 1; min-width: 200px; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box;" required>
            </div>

            <select name="objet" style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 15px; background: white; box-sizing: border-box;">
                <option disabled selected> Objet de votre demande</option>
                <option>Signaler un Bug</option>
                <option>Suggestion d'amélioration</option>
                <option>Erreur sur une station</option>
                <option>Autre question</option>
            </select>

            <textarea name="message" id="msg-field" placeholder=" Votre message détaillé..." style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; height: 100px; margin-bottom: 15px; box-sizing: border-box;" required></textarea>

            <button type="submit" id="submit-btn" style="background: #f59e0b; color: white; border: none; padding: 14px 20px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: 800; font-size: 16px;">
                 ENVOYER MA DEMANDE
            </button>
        </form>
    </div>

    <script>
        const form = document.getElementById('support-form');
        const successMsg = document.getElementById('success-message');
        const btn = document.getElementById('submit-btn');

        form.onsubmit = async (e) => {
            e.preventDefault();
            btn.innerHTML = "Envoi en cours...";
            btn.disabled = true;

            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'Accept': 'application/json' }
            });

            if (response.ok) {
                form.style.display = 'none';
                successMsg.style.display = 'block';
            } else {
                alert("Erreur lors de l'envoi. Réessayez.");
                btn.innerHTML = "🚀 ENVOYER MA DEMANDE";
                btn.disabled = false;
            }
        };
    </script>
    """
    # On force la largeur à 100% ici aussi
    st.components.v1.html(contact_form_html, height=520, scrolling=False)
    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 0.8rem; color: #64748b;'><b>CarbuNet Support</b> : Temps de réponse < 48h</div>", unsafe_allow_html=True)
