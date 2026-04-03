import streamlit as st

st.title("Pompe à Essence ⛽")
st.write("Bienvenue dans mon appli de suivi des prix du carburant !")

prix = st.slider("Sélectionne un prix au litre", 1.50, 2.50, 1.85)
st.success(f"Le prix sélectionné est de {prix}€")