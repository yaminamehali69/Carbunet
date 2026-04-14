import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from datetime import datetime

# === 1. Télécharger automatiquement le fichier depuis data.gouv ===
url = "https://www.data.gouv.fr/api/1/datasets/r/edd67f5b-46d0-4663-9de9-e5db1c880160"
carburant_prix = pd.read_csv(url, sep=';', low_memory=False)

# === 2. Nettoyage des colonnes ===
colonnes_a_supprimer = [
    'services', 'prix', 'rupture', 'horaires détaillés', 'horaires',
    'Début rupture e85 (si temporaire)', 'Type rupture e85',
    'Prix GPLc mis à jour le', 'Prix GPLc', 'Début rupture GPLc (si temporaire)',
    'Type rupture GPLc', 'Début rupture e10 (si temporaire)', 'Type rupture e10',
    'Débu9t rupture sp98 (si temporaire)', 'Type rupture sp98',
    'Début rupture gazole (si temporaire)'
]
carburant_prix = carburant_prix.drop(columns=colonnes_a_supprimer, errors='ignore')

# === 3. Extraire latitude/longitude depuis la colonne 'geom' ===
if 'geom' in carburant_prix.columns:
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
    'automate_24-24_(oui/non)': 'automate_24_24',
    'services_proposés': 'service_propose',
    'département': 'departement'
})

# === 6. Conversion des dates ===
colonnes_dates = ["prix_gazole_maj", "prix_sp95_maj", "prix_e85_maj", "prix_e10_maj", "prix_sp98_maj"]
for col in colonnes_dates:
    if col in carburant_prix.columns:
        carburant_prix[col] = pd.to_datetime(carburant_prix[col], errors='coerce').dt.tz_localize(None)

# === 7. SAUVEGARDE POUR GITHUB (Indispensable pour l'appli) ===
# On utilise la virgule comme séparateur standard pour éviter les soucis
carburant_prix.to_csv("carburant_prix_nettoye.csv", index=False, sep=',', encoding='utf-8-sig')
print("✅ Fichier CSV généré avec succès")

# === 8. SAUVEGARDES LOCALES (Tentative discrète) ===
try:
    chemin_bureau = os.path.join(os.path.expanduser("~"), "Desktop", "carburant_prix_nettoye.csv")
    carburant_prix.to_csv(chemin_bureau, index=False, sep=';', encoding='utf-8-sig')
except:
    pass

# === 9. CONNEXION MARIADB (Tentative discrète) ===
try:
    engine = create_engine(f"mysql+pymysql://root:1212.Y8m@localhost:3306/carburant_prix?charset=utf8mb4")
    carburant_prix.to_sql(name='carburant_prix', con=engine, if_exists='replace', index=False)
except:
    pass