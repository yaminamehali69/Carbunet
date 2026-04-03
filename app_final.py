import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Prix Carburant France", page_icon="⛽", layout="wide")

# Cache le menu anglais inutile
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 2. CHARGEMENT DES DONNÉES LOCALES ---
@st.cache_data
def load_local_data():
    # On cherche le fichier dans le même dossier que ton script
    fichier = "carburant_prix_nettoye.csv"
    
    if os.path.exists(fichier):
        # Lecture du fichier (le séparateur est ';' d'après ton code SQL/Python)
        df = pd.read_csv(fichier, sep=';', low_memory=False)
        return df
    else:
        return None

df = load_local_data()

# --- 3. INTERFACE ---
if df is not None:
    st.sidebar.title("⛽ Paramètres")
    
    # Choix du carburant (en utilisant les vrais noms de tes colonnes)
    dict_carbu = {
        "Gazole": "prix_gazole",
        "SP95": "prix_sp95",
        "SP98": "prix_sp98",
        "E10": "prix_e10",
        "E85": "prix_e85"
    }
    nom_affiche = st.sidebar.selectbox("Carburant :", list(dict_carbu.keys()))
    colonne_prix = dict_carbu[nom_affiche]
    
    # Filtre par département
    dep = st.sidebar.text_input("Département (ex: 69, 83) :", "")

    # --- 4. FILTRAGE ---
    # On enlève les lignes où le prix est vide pour ce carburant
    df_filtre = df[df[colonne_prix].notnull()].copy()
    
    if dep:
        # On filtre sur la colonne code_departement
        df_filtre = df_filtre[df_filtre['code_departement'].astype(str).str.startswith(dep)]

    # --- 5. AFFICHAGE ---
    st.title(f"⛽ Analyse : {nom_affiche}")
    
    if not df_filtre.empty:
        # Les chiffres clés
        c1, c2, c3 = st.columns(3)
        c1.metric("Prix Moyen", f"{df_filtre[colonne_prix].mean():.3f} €")
        c2.metric("Prix Minimum", f"{df_filtre[colonne_prix].min():.3f} €")
        c3.metric("Stations", len(df_filtre))

        # La carte
        st.subheader("📍 Carte des stations")
        # On s'assure que lat/lon sont bien des nombres
        map_df = df_filtre[['latitude', 'longitude']].dropna()
        map_df.columns = ['lat', 'lon']
        st.map(map_df)

        # Le tableau
        st.subheader("📋 Liste des prix")
        st.dataframe(
            df_filtre[['ville', 'adresse', colonne_prix]].sort_values(by=colonne_prix),
            use_container_width=True
        )
    else:
        st.warning(f"Aucune station trouvée pour le {nom_affiche} dans ce département.")

else:
    st.error("❌ Fichier 'carburant_prix_nettoye.csv' introuvable dans le dossier.")
    st.info("Assure-toi que ton script de nettoyage a bien créé le fichier dans le même dossier que app_final.py")
    