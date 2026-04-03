import streamlit as st
import pandas as pd
import os
import folium
import base64
import time  # <--- AJOUTÉ : Indispensable pour les animations
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import streamlit.components.v1 as components
import json
from streamlit_lottie import st_lottie

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# On charge l'animation une seule fois
lottie_loading = load_lottiefile(r"G:\Mon Drive\Carburant prix\loading.json")



if adresse_saisie:
    # On crée un espace vide pour l'animation
    placeholder = st.empty()
    
    with placeholder.container():
        st_lottie(lottie_loading, height=100, key="loading")
        st.markdown("<p style='text-align: center;'>Recherche en cours...</p>", unsafe_allow_html=True)

    # --- ICI TON CODE DE CALCUL (Nominatim, geodesic, etc.) ---
    # Simulation d'attente pour le test :
    import time
    time.sleep(2) 

    # Une fois fini, on vide l'animation pour afficher les résultats
    placeholder.empty()
    
    # Affiche tes résultats ici (Carte, liste, etc.)
    st.success("Terminé !")
# --- TEST DES WIDGETS ---

st.button("Clique-moi")

# Correction : Ajout du # pour le commentaire
# Show a spinner during a process
with st.spinner(text="Chargement en cours..."):
    time.sleep(1) # J'ai réduit à 1s pour que ce soit plus rapide
    st.success("C'est prêt !")

# Barre de progression
bar = st.progress(50)
time.sleep(1)
bar.progress(100)

# Statut
with st.status("Authentification...") as s:
    time.sleep(1)
    st.write("Connexion établie avec le serveur.")
    s.update(label="Vérification terminée", state="complete")

# Les animations
st.balloons()
# st.snow() # Je le mets en commentaire pour ne pas surcharger ton écran

# Les notifications
st.toast("Application prête !")
st.error("Ceci est un message d'erreur")
st.warning("Ceci est un avertissement")
st.info("Voici une information")
st.success("Succès !")

# Pour st.exception(e), il faut que 'e' existe. 
# Je le mets en commentaire pour éviter un bug :
# st.exception(RuntimeError("Petit test d'erreur"))