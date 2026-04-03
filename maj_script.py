

import pandas as pd
import numpy as np
import scipy.stats as st
import os
from sqlalchemy import create_engine



# === 1. Télécharger automatiquement le fichier depuis data.gouv ===
url = "https://www.data.gouv.fr/api/1/datasets/r/edd67f5b-46d0-4663-9de9-e5db1c880160"
carburant_prix = pd.read_csv(url, sep=';', low_memory=False)

# === 2. Supprimer les colonnes inutiles ===
colonnes_a_supprimer_1 = [
    'services', 'prix', 'rupture', 'horaires détaillés', 'horaires',
    'Début rupture e85 (si temporaire)', 'Type rupture e85'
]
carburant_prix = carburant_prix.drop(columns=colonnes_a_supprimer_1, errors='ignore')

colonnes_a_supprimer_2 = [
    'Prix GPLc mis à jour le', 'Prix GPLc', 'Début rupture GPLc (si temporaire)',
    'Type rupture GPLc', 'Début rupture e10 (si temporaire)', 'Type rupture e10',
    'Début rupture sp98 (si temporaire)', 'Type rupture sp98',
    'Début rupture gazole (si temporaire)'
]
carburant_prix = carburant_prix.drop(columns=colonnes_a_supprimer_2, errors='ignore')

# === 3. Extraire latitude/longitude depuis la colonne 'geom' ===
carburant_prix[['latitude', 'longitude']] = carburant_prix['geom'].str.split(',', expand=True)
carburant_prix = carburant_prix.drop(columns=['geom'])

# === 4. Nettoyer les noms de colonnes ===
carburant_prix.columns = carburant_prix.columns.str.strip().str.lower().str.replace(' ', '_')

# === 5. Renommer les colonnes ===
carburant_prix = carburant_prix.rename(columns={
    'prix_gazole_mis_à_jour_le': 'prix_gazole_maj',
    'prix_sp95_mis_à_jour_le': 'prix_sp95_maj',
    'prix_e85_mis_à_jour_le': 'prix_e85_maj',
    'prix_e10_mis_à_jour_le': 'prix_e10_maj',
    'prix_sp98_mis_à_jour_le': 'prix_sp98_maj',
    'début_rupture_sp95_(si_temporaire)': 'debut_rupture_sp95',
    'automate_24-24_(oui/non)': 'automate_24_24',
    'services_proposés': 'service_propose',
    'début_rupture_sp95': 'debut_rupture_sp95',
    'département': 'departement'
})

# === 6. Conversion des dates ===
colonnes_dates = [
    "prix_gazole_maj", "prix_sp95_maj", "prix_e85_maj",
    "prix_e10_maj", "prix_sp98_maj", "debut_rupture_sp95"
]

for col in colonnes_dates:
    carburant_prix[col] = pd.to_datetime(carburant_prix[col], errors='coerce').dt.tz_localize(None)

# === 7. Sauvegarde finale ===

# → Sauvegarde sur le Bureau
chemin_bureau = os.path.join(os.path.expanduser("~"), "Desktop", "carburant_prix_nettoye.csv")
carburant_prix.to_csv(chemin_bureau, index=False, sep=';', encoding='utf-8-sig')

# → Sauvegarde dans Google Drive (ou autre chemin)
chemin_drive = r"G:\Mon Drive\Carburant prix\carburant_prix_nettoye.csv"
carburant_prix.to_csv(chemin_drive, index=False, sep=';', encoding='utf-8-sig')

print(f"✅ Fichier mis à jour et enregistré ici :\n📁 Bureau : {chemin_bureau}\n📁 Drive : {chemin_drive}")

## Pour connecter et automatiser le fichier csv mise a j par pyhton et mis sur dbeaver 


from sqlalchemy import create_engine

# === 8. Connexion à ta base MariaDB ===
# 💡 Modifie les infos ci-dessous avec ta configuration réelle
utilisateur = "root"  # ou ton user MariaDB
mot_de_passe = "1212.Y8m"
hote = "localhost"
port = "3306"
base = "carburant_prix"  # nom de ta base dans DBeaver

# Création de la connexion SQLAlchemy
engine = create_engine(f"mysql+pymysql://{utilisateur}:{mot_de_passe}@{hote}:{port}/{base}?charset=utf8mb4")


# === 9. Envoi dans la table 'carburant_prix' ===
# Tu peux changer le nom de la table ici si tu veux
carburant_prix.to_sql(name='carburant_prix', con=engine, if_exists='replace', index=False)

print("✅ Données envoyées dans la base MariaDB (table : carburant_prix)")


print(carburant_prix[['prix_gazole', 'prix_sp95', 'prix_sp98', 'prix_e10', 'prix_e85']].head())
print(carburant_prix[['prix_gazole_maj', 'prix_sp95_maj', 'prix_sp98_maj']].head())


carburant_prix.head()


mask = carburant_prix['adresse'].str.contains("Gier", case=False, na=False) | \
       carburant_prix['adresse'].str.contains("Giers", case=False, na=False)

carburant_prix[mask][['adresse','ville', 'prix_gazole', 'prix_gazole_maj']]

