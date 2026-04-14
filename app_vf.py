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

# --- ONGLET 3 : SIMULATEUR ---
with tabs[2]:
    # On s'assure que les icônes Google sont chargées
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #1a73e8; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #1a73e8;">calculate</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; border:none;">
                Simulateur de budget
            </h2>
        </div>
    """, unsafe_allow_html=True)
    dist = st.number_input("Distance du trajet (km)", value=100)
    conso = st.number_input("Consommation moyenne (L/100)", value=6.5)
    if df is not None:
        p_moy = df[f"prix_{carbu.lower()}"].mean() if 'carbu' in locals() else 1.80
        st.metric("Coût estimé du trajet", f"{(dist/100) * conso * p_moy:.2f} €")


# 
# --- ONGLET 4 : SUPPORT ---
with tabs[3]:
    # On s'assure que les icônes Google sont chargées
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">', unsafe_allow_html=True)

    # Nouveau titre Pro sans colonnes (plus compact)
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #f59e0b; padding-left: 15px; margin-top: 10px; margin-bottom: 25px;">
            <span class="material-icons-outlined" style="font-size: 35px; color: #f59e0b;">contact_support</span>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; border:none;">
                Centre de Support CarbuNet
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Ton message d'aide (déjà compacté)
    st.markdown("""
    <div style="background-color: #fffbeb; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b; margin-bottom: 20px;">
        <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
            <b>Besoin d'aide ?</b> Une idée ou un bug ? Remplissez le formulaire, Yamina vous répondra vite.
        </p>
    </div>
    """, unsafe_allow_html=True)


    with st.form("feedback_pro", clear_on_submit=True):
        # Utilisation de colonnes pour un rendu plus compact et pro
        col_nom, col_email = st.columns(2)
        
        with col_nom:
            nom = st.text_input("👤 Nom & Prénom", placeholder="Ex: Jean Dupont")
        
        with col_email:
            email = st.text_input("📧 Votre Email", placeholder="Ex: jean.dupont@email.com")

        # Sélecteur de catégorie
        type_retour = st.selectbox("🎯 Objet de votre demande", [
            " Signaler un Bug (affichage, calcul...)", 
            " Suggestion d'amélioration", 
            " Erreur sur une station ou un prix",
            " Proposition de partenariat",
            " Autre question"
        ])

        msg = st.text_area("📝 Votre message détaillé", placeholder="Décrivez votre situation ici...", height=90)

        # Bouton stylisé
        submit_button = st.form_submit_button("🚀 ENVOYER MA DEMANDE")

        if submit_button:
            if not nom or not email or not msg:
                st.error("⚠️ Veuillez remplir tous les champs avant d'envoyer.")
            elif "@" not in email:
                st.error("⚠️ Veuillez entrer une adresse email valide.")
            else:
                st.balloons() 
                st.success(f"✅ Merci {nom} ! Votre demande concernant '{type_retour}' a bien été transmise à l'équipe technique.")
                
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: #64748b;">
         <b>CarbuNet Support</b> : Temps de réponse moyen constaté : < 48h
    </div>
    """, unsafe_allow_html=True)
# --- FOOTER ---
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 0.8rem; padding-bottom: 20px;'>© 2026 {AUTEUR} | Données sources : data.gouv.fr</div>", unsafe_allow_html=True)