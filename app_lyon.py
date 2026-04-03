import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# 1. Configuration de l'interface
st.set_page_config(page_title="Carburant Lyon Pro", layout="wide", page_icon="⛽")

# --- DESIGN PERSONNALISÉ (Gris moderne) ---
st.markdown("""
    <style>
    /* Fond gris de l'application */
    .stApp {
        background-color: #E5E7EB;
    }

    /* Cartes de prix blanches avec ombre */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #d1d5db;
    }

    /* Style des titres */
    h1, h2, h3 {
        color: #1F2937;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Personnalisation de la barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Chargement des données
@st.cache_data
def load_data():
    path = r"G:\Mon Drive\Carburant prix\carburant_prix_nettoye.csv"
    df = pd.read_csv(path, sep=';')
    for col in ['prix_gazole', 'prix_sp95', 'prix_sp98', 'prix_e10', 'prix_e85']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df_source = load_data()

# --- BARRE LATÉRALE ---
st.sidebar.image("https://www.pngall.com/wp-content/uploads/12/Gas-Station-Pump-PNG-Clipart.png", width=80)
st.sidebar.title("Paramètres Pro")

carburant = st.sidebar.selectbox("Choisir le carburant :", ["Gazole", "SP95", "SP98", "E10", "E85"])
col_prix = f"prix_{carburant.lower()}"

st.sidebar.divider()

st.sidebar.header("📍 Localisation")
adresse_client = st.sidebar.text_input("Adresse (Client / Dépôt) :", placeholder="ex: Place Bellecour, Lyon")
rayon_max = st.sidebar.slider("Rayon de recherche (km) :", min_value=1, max_value=50, value=10)

# --- TRAITEMENT DES DONNÉES ---
df_display = df_source.dropna(subset=[col_prix]).copy()
point_client = None

if adresse_client:
    try:
        geolocator = Nominatim(user_agent="lyon_transport_app")
        location = geolocator.geocode(adresse_client)
        if location:
            st.sidebar.success("✅ Adresse localisée")
            point_client = (location.latitude, location.longitude)
            
            def get_dist(row):
                if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                    return round(geodesic(point_client, (row['latitude'], row['longitude'])).km, 2)
                return 9999

            df_display['distance_km'] = df_display.apply(get_dist, axis=1)
            df_display = df_display[df_display['distance_km'] <= rayon_max]
        else:
            st.sidebar.error("❌ Adresse introuvable")
    except:
        st.sidebar.warning("⚠️ Service GPS indisponible")

# --- CORPS DE L'APPLICATION ---
st.title(f"⛽ Analyse du Marché : {carburant}")
st.write(f"Comparateur professionnel pour votre flotte de transport.")

if not df_display.empty:
    # 1. Indicateurs (KPIs)
    p_min = df_display[col_prix].min()
    p_moy = df_display[col_prix].mean()
    p_max = df_display[col_prix].max()

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Prix Minimum", f"{p_min:.3f} €")
    kpi2.metric("Prix Moyen", f"{p_moy:.3f} €")
    kpi3.metric("Prix Maximum", f"{p_max:.3f} €")

    st.divider()

    # 2. Carte interactive
    st.subheader(f"🗺️ Répartition des stations ({len(df_display)})")
    map_data = df_display.dropna(subset=['latitude', 'longitude']).copy()
    map_data = map_data.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
    st.map(map_data)

    # 3. Tableau de résultats
    st.subheader("📋 Liste détaillée")
    if point_client:
        df_final = df_display.sort_values(by='distance_km', ascending=True)
        cols_to_show = ['distance_km', 'adresse', 'ville', col_prix, f'{col_prix}_maj']
    else:
        df_final = df_display.sort_values(by=col_prix, ascending=True)
        cols_to_show = ['adresse', 'ville', col_prix, f'{col_prix}_maj']

    st.dataframe(df_final[cols_to_show], use_container_width=True, hide_index=True)

else:
    st.warning(f"Aucune station trouvée à moins de {rayon_max} km.")
    st.info("Augmentez le rayon dans la barre latérale pour voir plus de résultats.")
    