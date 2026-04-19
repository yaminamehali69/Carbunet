import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import base64

# --- 1. CONFIGURATION ---
path_logo = "logo_carbunet.png"
path_csv = "https://raw.githubusercontent.com/yaminamehali69/Carbunet/main/carburant_prix_nettoye.csv"
VERSION = "1.3.9"
AUTEUR = "Yamina Mehali"


st.set_page_config(
    page_title=f"CarbuNet by {AUTEUR}", 
    layout="centered", 
    page_icon=path_logo, 
    initial_sidebar_state="collapsed"
)

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
st.markdown("""
<style>
header {visibility: hidden;}

/* 1. Supprime le vide en haut de la page */
.block-container {
    padding-top: 1rem !important; 
    padding-bottom: 0rem;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; margin-bottom: 10px; }
.stTabs [data-baseweb="tab"] { height: 40px; background-color: #f1f5f9; border-radius: 10px; padding: 4px 15px; font-weight: 600; }
.stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; }

.hero-container {
    background: linear-gradient(135deg, #1a73e8 0%, #32CD32 100%);
    border-radius: 20px; 
    padding: 25px 20px; 
    text-align: center; 
    color: white;
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    min-height: 380px; /* 2. Taille réduite ici */
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
    🔍 Explorez les tarifs en temps réel dans l'onglet <b style="color: #32CD32;">STATIONS</b>
</div>
<div class="disclaimer-text">
<b>Mention d'information :</b> 
Les données de prix et de disponibilité sont issues de la plateforme nationale <b>data.gouv.fr</b>.

Bien que mises à jour régulièrement, {AUTEUR} ne saurait être tenue responsable des écarts de prix constatés lors du passage en caisse.
</div>
<div style="font-size:0.8rem; margin-top:15px; opacity:0.9;">
Version {VERSION} | Développé par <b>{AUTEUR}</b>
</div>
</div>
"""
        st.markdown(concept_html, unsafe_allow_html=True)

# --- ONGLET 2 : STATIONS ---
with tabs[1]:
    # 1. On charge d'abord la bibliothèque d'icônes (si ce n'est pas déjà fait en haut du code)
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    # 2. On remplace ton ancien titre par ce bloc "Modèle 2"
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #32CD32; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #32CD32;">payments</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; border:none;">
                Le meilleur prix, au kilomètre près
            </h2>
        </div>
    """, unsafe_allow_html=True)
    if df is not None:
        adresse = st.text_input("📍 Où cherchez-vous ?", placeholder="Ville ou adresse complète...", key="input_stations")
        c1, c2 = st.columns(2)
        with c1:
            carbu = st.selectbox("Type de carburant", ["Gazole", "SP95", "SP98", "E10", "E85"])
            col_p, col_m = f"prix_{carbu.lower()}", f"prix_{carbu.lower()}_maj"
        with c2:
            rayon = st.select_slider("Rayon (km)", options=[1, 2, 5, 10, 20], value=5)

        with st.expander("➕ Options & Services "):
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
                        # --- CETTE LIGNE EXISTE DÉJÀ DANS TON CODE ---
                        res = res.sort_values(by=col_p)

                        if not res.empty:
                            # --- COLLE CE BLOC JUSTE ICI ---
                            st.markdown("---")
                            # On prépare la liste des stations pour que le simulateur puisse "lire" le prix
                            stations_trouvees = {f"{row['adresse']} ({row[col_p]}€)": row[col_p] for _, row in res.head(8).iterrows()}
                            
                            # On crée le menu de sélection
                            choix_station = st.selectbox("🎯 Sélectionne ta station pour le calcul du budget :", options=list(stations_trouvees.keys()))

                            # ON SAUVEGARDE DANS LA MÉMOIRE (Session State)
                            st.session_state['prix_perso'] = stations_trouvees[choix_station]
                            st.session_state['carbu_nom'] = carbu
                            st.session_state['station_nom'] = choix_station.split('(')[0].strip()
                            
                            st.success(f"📍 Station choisie : {st.session_state['prix_perso']} €/L")
                            st.markdown("---")
                            # --- FIN DU BLOC À COLLER ---

                            # --- LA SUITE DE TON CODE (DÉJÀ PRÉSENTE) ---
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
                                popup_content = f"<div style='text-align:center;'>{'🌟 <b>LE MOINS CHER</b> 🌟<br>' if is_cheapest else ''}{label_prix}<br>MàJ: {row[col_m]}<br><a href='https://waze.com/ul?ll={row['latitude']},{row['longitude']}&navigate=yes' target='_blank'>Waze 🚗</a></div>"
                                
                                folium.Marker(
                                    [row['latitude'], row['longitude']], 
                                    popup=folium.Popup(popup_content, max_width=200),
                                    icon=folium.Icon(color=color, icon=icon_type, prefix='fa', icon_color='red')
                                ).add_to(m)
                            st_folium(m, width="100%", height=400)
                            
                            st.markdown("### ⛽ Meilleures options trouvées")
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


# --- LE MOTEUR DE RECHERCHE (Obligatoire pour éviter l'erreur de ton image 3) ---
@st.cache_data(ttl=604800)
def fetch_car_data_pro(plaque):
    # Tes infos RapidAPI (Image 1)
    url = "https://api-de-plaque-d-immatriculation-france.p.rapidapi.com/getData"
    headers = {
        "x-rapidapi-key": "deed37d7c3msh976ac4ec2c8fa13p1960e4jsndb4151c68278",
        "x-rapidapi-host": "api-de-plaque-d-immatriculation-france.p.rapidapi.com",
        "plaque": plaque
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json(), True
    except:
        pass
    return None, False

# --- ONGLET 3 : SIMULATEUR ---
# --- ONGLET 3 : SIMULATEUR ---
with tabs[2]:
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #1a73e8; padding-left: 15px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #1a73e8;">calculate</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; border:none;">Simulateur de budget</h2>
        </div>
    """, unsafe_allow_html=True)


    # --- 1. RÉCUPÉRATION DU PRIX DE L'ONGLET STATIONS ---
    # On vérifie si l'utilisateur a sélectionné une station dans l'onglet précédent
    if 'prix_perso' in st.session_state:
        p_final = st.session_state['prix_perso']
        nom_carbu_utilisé = st.session_state.get('carbu_nom', 'Carburant')
        station_nom = st.session_state.get('station_nom', 'Station sélectionnée')
        st.info(f"⛽ **Prix utilisé : {p_final:.3f} €/L** ({nom_carbu_utilisé} chez {station_nom})")
    else:
        # Valeur de secours si l'utilisateur n'est pas passé par l'onglet Stations
        p_final = 1.859 
        st.warning("⚠️ Aucune station sélectionnée dans l'onglet 'Stations'. Prix moyen estimé utilisé.")

    # --- 2. IDENTIFICATION VÉHICULE (PLAQUE) ---
    st.markdown("##### 🚗 Identification du véhicule")
    conso_auto = 6.0 # Valeur par défaut pour éviter le NameError
    
    plaque_input = st.text_input("📍 Tapez votre plaque", placeholder="AB-123-CD").upper().strip()

    if plaque_input:
        with st.spinner('Recherche SIV en cours...'):
            # On appelle ta fonction de recherche (assure-toi qu'elle est définie en haut de ton code)
            data, success = fetch_car_data_pro(plaque_input)
            
            if success and data:
                marque = data.get('Marque', 'Véhicule')
                modele = data.get('Modele', 'identifié')
                energie = data.get('Energie', 'N/C').upper()
                
                st.success(f"✅ **{marque} {modele}** ({energie})")
                
                # Ajustement automatique de la consommation selon l'énergie officielle
                if "DIESEL" in energie:
                    conso_auto = 5.2
                elif "ESSENCE" in energie:
                    conso_auto = 6.8
            else:
                st.error("❌ Impossible de valider la plaque (Quota API atteint ou plan non activé).")

    # --- 3. PARAMÈTRES DU TRAJET ---
    col1, col2 = st.columns(2)
    with col1:
        dist = st.number_input("Distance à parcourir (km)", value=100, min_value=1)
    with col2:
        # Le slider permet de corriger la conso si le client connaît mieux sa voiture
        conso_finale = st.slider("Consommation (L/100)", 3.0, 15.0, float(conso_auto))

    # --- 4. CALCUL ET RÉSULTAT FINAL ---
    # Le calcul se fait avec le prix EXACT récupéré de l'onglet station
    cout_estime = (dist / 100) * conso_finale * p_final
    
    st.markdown(f"""
        <div style="background-color: #1a73e8; padding: 30px; border-radius: 20px; text-align: center; color: white; margin-top: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">VOTRE BUDGET TRAJET ESTIMÉ</p>
            <h1 style="margin: 10px 0; font-size: 3.8rem; color: white; border:none; font-weight:800;">{cout_estime:.2f} €</h1>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px; font-size: 0.9rem;">
                <span>⛽ {conso_finale} L/100</span>
                <span>📍 {dist} km</span>
                <span>💰 {p_final:.3f} €/L</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
            <p style="margin:10px 0 0 0;">Merci pour votre retour, Yamina vous répondra dans les plus brefs délais.</p>
        </div>

        <form id="support-form" action="https://formsubmit.co/ajax/minamhl@icloud.com" method="POST" style="background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;">
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_subject" value="🚀 Nouveau message CarbuNet !">
            
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <input type="text" name="name" placeholder="👤 Nom & Prénom" style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;" required>
                <input type="email" name="email" placeholder="📧 Votre Email" style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;" required>
            </div>

            <select name="objet" style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 15px; background: white;">
                <option disabled selected>🎯 Objet de votre demande</option>
                <option>Signaler un Bug</option>
                <option>Suggestion d'amélioration</option>
                <option>Erreur sur une station</option>
                <option>Autre question</option>
            </select>

            <textarea name="message" id="msg-field" placeholder="📝 Votre message détaillé..." style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; height: 100px; margin-bottom: 15px;" required></textarea>

            <button type="submit" id="submit-btn" style="background: #f59e0b; color: white; border: none; padding: 14px 20px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: 800; font-size: 16px;">
                🚀 ENVOYER MA DEMANDE
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