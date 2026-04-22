import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import base64
import urllib.parse

# --- 1. CONFIGURATION ---
path_logo = "logo_carbunet.png"
path_csv = "https://raw.githubusercontent.com/yaminamehali69/Carbunet/main/carburant_prix_nettoye.csv"
VERSION = "1.3.9"
AUTEUR = "Yamina Mehali"
AUTEUR_2 = "Carbunet"

# --- 1. CONFIGURATION ---
# Utilise le lien DIRECT "raw" pour que l'iPhone ne puisse pas se tromper
LOGO_URL = "https://raw.githubusercontent.com/yaminamehali69/Carbunet/main/logo_carbunet.png"

st.set_page_config(
    page_title="CarbuNet", 
    layout="centered", 
    page_icon=LOGO_URL, # On met ton logo ici aussi !
    initial_sidebar_state="collapsed"
)

# 2. LE HACK FINAL (On force l'icône et on supprime celle de Streamlit)
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{LOGO_URL}">
        <link rel="icon" href="{LOGO_URL}">
    </head>
    <script>
        // Ce petit script va chercher l'icône de Streamlit et la remplacer par la tienne dès que la page charge
        var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
        link.type = 'image/png';
        link.rel = 'shortcut icon';
        link.href = '{LOGO_URL}';
        document.getElementsByTagName('head')[0].appendChild(link);
        
        // On fait la même chose pour l'icône iPhone
        var appleLink = document.querySelector("link[rel*='apple-touch-icon']") || document.createElement('link');
        appleLink.rel = 'apple-touch-icon';
        appleLink.href = '{LOGO_URL}';
        document.getElementsByTagName('head')[0].appendChild(appleLink);
    </script>
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

# --- STYLE CSS ---
# --- STYLE CSS ---
st.markdown("""
<style>
    /* 1. Masquage global du header et fix transparence */
    header {visibility: hidden;}
    
    div[data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
    }

    /* 2. Supprime le vide en haut de la page */
    .block-container {
        padding-top: 1rem !important; 
        padding-bottom: 0rem;
    }

    /* 3. OPTIMISATION MODE APP (PWA) */
    @media (display-mode: standalone) {
        header { display: none !important; }
        .block-container { padding-top: 0px !important; }
    }

    /* 4. DESIGN DES ONGLETS */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { height: 40px; background-color: #f1f5f9; border-radius: 10px; padding: 4px 15px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; }

    /* 5. HERO CONTAINER (ACCUEIL) */
    .hero-container {
        background: linear-gradient(135deg, #1a73e8 0%, #32CD32 100%);
        border-radius: 20px; 
        padding: 25px 20px; 
        text-align: center; 
        color: white;
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        min-height: 380px; 
        justify-content: space-between;
    }
    .hero-container h1 { color: white !important; font-size: 2.8rem !important; margin-bottom: 5px; border:none; }

    .disclaimer-text {
        font-size: 0.7rem; opacity: 0.85; line-height: 1.2; max-width: 550px;
        margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES ---
@st.cache_data(ttl=3600) # Ajout d'une durée de cache (1h) pour forcer l'actu
def charger_donnees():
    try:
        # On lit directement l'URL GitHub
        df = pd.read_csv(path_csv, sep=',', low_memory=False) # Attention sep=',' car mon script robot utilise la virgule
        for c in ['prix_gazole', 'prix_sp95', 'prix_sp98', 'prix_e10', 'prix_e85']:
            if c in df.columns: 
                df[c] = pd.to_numeric(df[c], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur de chargement des données : {e}")
        return None

df = charger_donnees()


# --- 3. NAVIGATION ---
tabs = st.tabs([" Concept", " Stations", " Simulateur", " Support & Bugs"])

# --- 4. CONTENU ---

# --- ONGLET 1 : CONCEPT ---
with tabs[0]:
    if os.path.exists(path_logo):
        with open(path_logo, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        
        concept_html = f"""
<div class="hero-container">
<img src="data:image/png;base64,{encoded}" width="170">
<h1>CarbuNet</h1>
<p style="font-size:1.4rem; font-weight:500;">Le prix le plus net, au kilomètre près.</p>
<div style="background: #0f172a; color: white; padding: 10px 25px; border-radius: 50px; font-weight: 600; font-size: 0.85rem; margin-top: 20px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); display: inline-block; border: 1px solid rgba(255,255,255,0.1);">
     Explorez les tarifs en temps réel dans l'onglet <b style="color: #32CD32;">STATIONS</b>
</div>
<div class="disclaimer-text">
<b>Mention d'information :</b> 
Les données de prix et de disponibilité sont issues de la plateforme nationale <b>data.gouv.fr</b>.

Bien que mises à jour régulièrement, {AUTEUR_2} ne saurait être tenue responsable des écarts de prix constatés lors du passage en caisse.
</div>
<div style="font-size:0.8rem; margin-top:15px; opacity:0.9;">
Version {VERSION} | Développé par <b>{AUTEUR}</b>
</div>
</div>
"""
        st.markdown(concept_html, unsafe_allow_html=True) 
    st.caption("© 2026 CarbuNet. Propriété exclusive de l'auteur. Toute reproduction interdite.")
    
# --- ONGLET 2 : STATIONS ---
with tabs[1]:
    # 1. On charge d'abord la bibliothèque d'icônes (si ce n'est pas déjà fait en haut du code)
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    # 2.titre 
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #32CD32; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #32CD32;">payments</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; border:none;">
                Le meilleur prix, au kilomètre près
            </h2>
        </div>
    """, unsafe_allow_html=True)
    if df is not None:
        adresse = st.text_input(" Où cherchez-vous ?", placeholder="Ville ou adresse complète...", key="input_stations")
        c1, c2 = st.columns(2)
        with c1:
            carbu = st.selectbox("Type de carburant", ["Gazole", "SP95", "SP98", "E10", "E85"])
            col_p, col_m = f"prix_{carbu.lower()}", f"prix_{carbu.lower()}_maj"
        with c2:
            rayon = st.select_slider("Rayon (km)", options=[1, 2, 5, 10, 20], value=5)

        with st.expander(" Options & Services "):
            cols_srv = st.columns(2)
            selection = []
            for i, (srv_name, emoji) in enumerate(LOGOS_SERVICES.items()):
                if cols_srv[i % 2].checkbox(f"{emoji} {srv_name}"):
                    selection.append(srv_name)

        if adresse:
            with st.spinner("Analyse des prix en cours..."):
                geolocator = Nominatim(user_agent="carbunet_pro_yamina_v5")
                try:
                    loc = geolocator.geocode(adresse + ", France")
                    if loc:
                        ma_pos = (loc.latitude, loc.longitude)
                        df_c = df[df[col_p] > 0].dropna(subset=[col_p, 'latitude', 'longitude']).copy()
                        df_c['distance'] = df_c.apply(lambda r: geodesic(ma_pos, (r['latitude'], r['longitude'])).km, axis=1)
                        res = df_c[df_c['distance'] <= rayon].copy()

                        for s_filtre in selection:
                            res = res[res['service_propose'].str.contains(s_filtre, na=False, case=False)]

                        res = res.sort_values(by=col_p)
            
                        if not res.empty:
                        
                            st.markdown("---")
                            # On prépare la liste des stations pour que le simulateur puisse "lire" le prix
                            stations_trouvees = {f"{row['adresse']} ({row[col_p]}€)": row[col_p] for _, row in res.head(8).iterrows()}
                            
                            # On crée le menu de sélection
                            choix_station = st.selectbox(" Sélectionne ta station pour le calcul du budget :", options=list(stations_trouvees.keys()))

                            # ON SAUVEGARDE DANS LA MÉMOIRE (Session State)
                            st.session_state['prix_perso'] = stations_trouvees[choix_station]
                            st.session_state['carbu_nom'] = carbu
                            st.session_state['station_nom'] = choix_station.split('(')[0].strip()
                            
                            st.success(f" Station choisie : {st.session_state['prix_perso']} €/L")
                            st.markdown("---")
                        
                            m = folium.Map(location=ma_pos, zoom_start=13, tiles="cartodbpositron")
                            p_min = res[col_p].min()
                            # ... la suite avec folium et les markers ...

                        if not res.empty:
                            m = folium.Map(location=ma_pos, zoom_start=13, tiles="cartodbpositron")
                            p_min = res[col_p].min()

                            for idx, row in res.head(10).iterrows():
                                is_cheapest = row[col_p] == p_min
                                color = 'green' if is_cheapest else 'blue'
                                icon_type = 'thumbs-up' if is_cheapest else 'spade'
                                label_prix = f"<b>{float(row[col_p]):.3f}€</b>"
                                popup_content = f"<div style='text-align:center;'>{' <b>LE MOINS CHER</b> <br>' if is_cheapest else ''}{label_prix}<br>MàJ: {row[col_m]}<br><a href='https://waze.com/ul?ll={row['latitude']},{row['longitude']}&navigate=yes' target='_blank'>Waze 🚗</a></div>"
                                
                                folium.Marker(
                                    [row['latitude'], row['longitude']], 
                                    popup=folium.Popup(popup_content, max_width=200),
                                    icon=folium.Icon(color=color, icon=icon_type, prefix='fa', icon_color='red')
                                ).add_to(m)
                            st_folium(m, width="100%", height=400)
                            st.markdown(f"""
                             <div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px;">
                               <p style="margin: 0; font-size: 0.9rem; color: #004085; line-height: 1.5;">
                              ℹ️ <b>À savoir :</b> Les stocks sont indicatifs et basés sur les relevés officiels. 
                               Un décalage reste possible entre l'affichage et la disponibilité réelle en pompe, 
                               notamment en période de forte affluence.
                             </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("###  Meilleures options trouvées")
                            for _, row in res.head(8).iterrows():
                                w_url = f"https://waze.com/ul?ll={row['latitude']},{row['longitude']}&navigate=yes"
                                rupt = str(row.get('carburants_en_rupture_temporaire', '')) + str(row.get('carburants_en_rupture_definitive', ''))
                                stock_t, stock_c = ("❌ RUPTURE", "#ef4444") if carbu in rupt else ("✅ EN STOCK", "#10b981")
                                
                                # --- AFFICHAGE INTELLIGENT AVEC LOGOS ---
                                srv_str = str(row.get('service_propose', ''))
                                badges_list = []
                                if srv_str and srv_str != 'nan':
                                    for s in srv_str.split(','):
                                        name = s.strip()
                                        emoji = LOGOS_SERVICES.get(name, "🔹") # Emoji par défaut si non trouvé
                                        badges_list.append(f'<span style="display:inline-block; font-size:10px; background:#f1f5f9; padding:2px 8px; border-radius:20px; margin:2px; color:#64748b; border:1px solid #e2e8f0;">{emoji} {name}</span>')
                                    all_badges = "".join(badges_list)
                                else:
                                    all_badges = '<span style="font-size:10px; color:#94a3b8;">Aucun service listé</span>'

                                border_color = "#10b981" if row[col_p] == p_min else "#e2e8f0"
                                label_eco = f'<span style="background:#10b981; color:white; padding:2px 6px; border-radius:4px; font-size:0.7rem; margin-bottom:5px; display:inline-block;">MEILLEUR PRIX 🏆</span><br>' if row[col_p] == p_min else ''

                                card_html = f"""
<div style="background:#fff; border-radius:12px; padding:15px; margin-bottom:12px; border:2px solid {border_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
{label_eco}
<div style="display:flex; justify-content:space-between; align-items:start;">
<span style="font-size:1.6rem; font-weight:800; color:#0f172a;">{float(row[col_p]):.3f} €</span>
<div style="text-align:right;">
<span style="background:#0f172a; color:white; padding:3px 10px; border-radius:8px; font-size:0.85rem; font-weight:bold;">{row['distance']:.1f} km</span>
<div style="color:{stock_c}; font-weight:bold; font-size:0.75rem; margin-top:4px;">{stock_t}</div>
</div>
</div>
<div style="font-size:0.95rem; margin:8px 0; color:#334155;"><b>{row['adresse'].title()}</b> ({row['ville']})</div>
<div style="margin: 10px 0; display: flex; flex-wrap: wrap;">{all_badges}</div>
<div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; border-top:1px solid #f8fafc; padding-top:10px;">
<small style="color:#94a3b8; font-size:0.7rem;">MàJ : {row[col_m]}</small>
<a href="{w_url}" target="_blank" style="color:#1a73e8; font-weight:bold; text-decoration:none; font-size:0.85rem;">ITINÉRAIRE WAZE 🚗</a>
</div>
</div>
"""
                                st.markdown(card_html, unsafe_allow_html=True)
                        else: st.warning("Aucune station ne correspond.")
                except: st.error("Lieu non reconnu.")


# --- ONGLET 3 : SIMULATEUR ---
with tabs[2]:
    # INITIALISATION PROPRE
    if 'km_memoire' not in st.session_state:
        st.session_state['km_memoire'] = 0.0

    # --- NOUVEAU TITRE SIMULATEUR HARMONISÉ ---
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #3b82f6; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #3b82f6;">calculate</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; border:none;">
                Simulateur de Budget Personnalisé
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # PRIX (Vérifie bien que ton Onglet 2 enregistre 'prix_perso')
    p_final = st.session_state.get('prix_perso', 1.859)
    nom_carbu = st.session_state.get('carbu_nom', 'Carburant')
    st.info(f" Prix actuel : **{p_final:.3f} €/L** ({nom_carbu})")

    # ITINÉRAIRE
    st.markdown("#####  1. Itinéraire")
    c1, c2 = st.columns(2)
    with c1:
        dep_v = st.text_input("Départ", value="Ville ou adresse complète", key="cle_dep")
    with c2:
        arr_v = st.text_input("Arrivée", value="Ville ou adresse complète", key="cle_arr")

    # BOUTON DE CALCUL
    if st.button(" CALCULER L'ITINÉRAIRE", use_container_width=True):
        if dep_v and arr_v:
            try:
                with st.spinner("Recherche GPS en cours..."):
                    # On utilise un user_agent unique pour éviter les blocages
                    geolocator = Nominatim(user_agent="carbunet_final_check")
                    l1 = geolocator.geocode(dep_v)
                    l2 = geolocator.geocode(arr_v)
                    
                    if l1 and l2:
                        dist_gps = geodesic((l1.latitude, l1.longitude), (l2.latitude, l2.longitude)).km
                        # On stocke et on force le rafraîchissement
                        st.session_state['km_memoire'] = round(dist_gps * 1.25, 1)
                        st.rerun() 
                    else:
                        st.error("❌ Adresse introuvable. Soyez précis (Ville + Code Postal).")
            except Exception as e:
                st.error(f"❌ Erreur technique : {e}")

    # CONFIGURATION TECHNIQUE
    st.markdown("---")
    st.markdown("#####  2. Paramètres du véhicule")
    
    p_route = st.selectbox("Type de trajet", [
        "Urbain / Départementale", 
        "Mixte (Ville + Autoroute)", 
        "Autoroute / Montagne (130 km/h)"
    ], index=2)

    v_type = st.selectbox("Votre voiture", ["Citadine", "Berline", "SUV", "Utilitaire"])

    # LOGIQUE DE CONSO (Pour tomber sur tes 30€)
    base = {"Citadine": 5.5, "Berline": 6.8, "SUV": 8.0, "Utilitaire": 10.0}[v_type]
    if "Mixte" in p_route: base += 1.2
    elif "Autoroute" in p_route: base += 2.8

    # LE CHIFFRE QUI DOIT CHANGER
    km_final = st.number_input("Kilomètres calculés", value=float(st.session_state['km_memoire']))

    # RÉSULTAT
    if km_final > 0:
        total_euros = (km_final / 100) * base * p_final
        
       # --- BLOC DE RÉSULTAT FINAL ---
        st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 0.95rem; color: #1e293b; line-height: 1.6; text-align: center;">
                    <b>Budget estimé au plus juste</b> selon votre itinéraire (relief, vitesse) et votre profil de véhicule. <br>
                    <span style="color: #64748b; font-size: 0.85rem; font-style: italic;">
                        ⚠️ Ce montant est indicatif : il peut varier selon l'évolution réelle des prix à la pompe et les conditions de circulation.
                    </span>
                </p>
            </div>
        """, unsafe_allow_html=True)

        # LE GROS CHIFFRE
        st.markdown(f"""
            <div style="background-color: #1e293b; padding: 35px; border-radius: 20px; text-align: center; color: white;">
                <p style="margin: 0; opacity: 0.7; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Estimation Totale</p>
                <h1 style="margin: 10px 0; font-size: 4rem; color: #4ade80; border:none; font-weight:800;">{total_euros:.2f} €</h1>
                <p style="margin: 0; opacity: 0.5; font-size: 0.85rem;">{km_final} km • {base:.1f} L/100 • {p_final:.3f} €/L</p>
            </div>
        """, unsafe_allow_html=True)
        # WAZE
        w_link = f"https://www.waze.com/ul?q={urllib.parse.quote(arr_v)}&from={urllib.parse.quote(dep_v)}&navigate=yes"
        st.markdown(f'<a href="{w_link}" target="_blank" style="text-decoration:none;"><div style="background:#33CCFF;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;margin-top:15px;">🚀 LANCER WAZE</div></a>', unsafe_allow_html=True)

# --- ONGLET 4 : SUPPORT ---
with tabs[3]:
    import streamlit.components.v1 as components

    # Style des icônes
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    # Titre 
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #f59e0b; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #f59e0b;">contact_support</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; border:none;">Centre de Support CarbuNet</h2>
        </div>
    """, unsafe_allow_html=True)

    # --- LE FORMULAIRE AVEC CARRÉ VERT SANS RECHARGER ---
    contact_form_html = """
    <div id="form-container" style="font-family: sans-serif;">
        <div id="success-message" style="display: none; background-color: #d1fae5; color: #065f46; padding: 20px; border-radius: 10px; border: 1px solid #34d399; text-align: center;">
            <h3 style="margin:0;">✅ Message envoyé !</h3>
            <p style="margin:10px 0 0 0;">Merci pour votre retour, Carbunet vous répondra dans les plus brefs délais.</p>
        </div>

        <form id="support-form" action="https://formsubmit.co/ajax/minamhl@icloud.com" method="POST" style="background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;">
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_subject" value=" Nouveau message CarbuNet !">
            
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <input type="text" name="name" placeholder=" Nom & Prénom" style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;" required>
                <input type="email" name="email" placeholder=" Votre Email" style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;" required>
            </div>

            <select name="objet" style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 15px; background: white;">
                <option disabled selected> Objet de votre demande</option>
                <option>Signaler un Bug</option>
                <option>Suggestion d'amélioration</option>
                <option>Erreur sur une station</option>
                <option>Autre question</option>
            </select>

            <textarea name="message" id="msg-field" placeholder=" Votre message détaillé..." style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; height: 100px; margin-bottom: 15px;" required></textarea>

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
    # On affiche le composant
    components.html(contact_form_html, height=450)
    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 0.8rem; color: #64748b;'><b>CarbuNet Support</b> : Temps de réponse < 48h</div>", unsafe_allow_html=True)


