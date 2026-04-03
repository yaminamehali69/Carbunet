import pandas as pd
import ssl
import urllib.request

# FORCE L'IGNORANCE DU CERTIFICAT SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Lien direct vers le référentiel des stations (data.gouv.fr)
url_noms = "https://www.data.gouv.fr/fr/datasets/r/7968a355-6b66-4e50-93a8-622f4b44535c"

try:
    print("Connexion au serveur de l'État...")
    # On télécharge le CSV des noms
    df_noms = pd.read_csv(url_noms, sep=";", encoding="utf-8")
    
    # On ne garde que l'ID et le NOM pour que ce soit léger
    # Note: On vérifie les noms des colonnes car elles changent parfois
    print("Colonnes trouvées :", df_noms.columns.tolist())
    
    # On sauvegarde sur ton Drive
    chemin_final = r"G:\Mon Drive\Carburant prix\noms_officiels.csv"
    df_noms.to_csv(chemin_final, index=False, sep=";")
    
    print("-" * 30)
    print(f"MAGNIFIQUE ! Fichier créé : {chemin_final}")
    print("Tu peux maintenant retourner sur ton appli app_vf.py")
    print("-" * 30)

except Exception as e:
    print(f"Erreur lors de la récupération : {e}")