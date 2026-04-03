CREATE TABLE prix_des_carburants_en_france_flux_instantane (
    id BIGINT PRIMARY KEY,
    latitude DECIMAL(8,5),
    longitude DECIMAL(8,5),
    code_postal INT,
    pop VARCHAR(1),
    adresse VARCHAR(255),
    ville VARCHAR(100),

    prix_gazole_maj DATETIME NULL,
    prix_gazole DECIMAL(5,3) NULL,

    prix_sp95_maj DATETIME NULL,
    prix_sp95 DECIMAL(5,3) NULL,

    prix_e85_maj DATETIME NULL,
    prix_e85 DECIMAL(5,3) NULL,

    prix_e10_maj DATETIME NULL,
    prix_e10 DECIMAL(5,3) NULL,

    prix_sp98_maj DATETIME NULL,
    prix_sp98 DECIMAL(5,3) NULL,

    debut_rupture_sp95 DATETIME NULL,
    type_rupture_sp95 VARCHAR(20),
    type_rupture_gazole VARCHAR(20),

    carburants_disponibles VARCHAR(255),
    carburants_indisponibles VARCHAR(255),
    carburants_en_rupture_temporaire VARCHAR(255),
    carburants_en_rupture_definitive VARCHAR(255),

    automate_24_24 VARCHAR(5),
    services_propose TEXT,

    departement VARCHAR(100),
    code_departement INT,
    région VARCHAR(100),
    code_region INT
);


DROP TABLE prix_des_carburants_en_france_flux_instantane ;


select * 
from prix_des_carburants_en_france_flux_instantane pdceffi 
