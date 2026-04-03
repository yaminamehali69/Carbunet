-- 1- Afficher toute la table 
select *
from prix_des_carburants_en_france_flux_instantane pdceffi; 

-- 2- Afficher seulement quelque colonnes de la table. Il est préférable de selectionner que les colonnnes utile à l'analyse 

select adresse , ville 
from prix_des_carburants_en_france_flux_instantane pdceffi;


--  On va sélectionner les colonnes uqi va n'ont intéresser pour l'analyse 

select code_postal, adresse, ville, latitude, longitude, prix_sp95, departement, code_departement 
from prix_des_carburants_en_france_flux_instantane pdceffi;

-- On peut arranger l'ordre de la visu du tableau , mettre les colonnes de meme nature a coter 
-- Un pro va indender toutes les colonnes , mais pas trop tot quand ca commence a devenir complexe 

select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi; 

-- 3- Trouver le prix min et mac du SP95 

select 
MIN(prix_sp95) 
MAX(prix_sp95) 
from prix_des_carburants_en_france_flux_instantane pdceffi 
-- Toujours traduire les colonnes sinon pas pro 


-- 4-  Renommer les colonnes 
select 
MIN(prix_sp95) as prix_minimum_sp95,
MAX(prix_sp95) as prix_maximum_sp95
from prix_des_carburants_en_france_flux_instantane pdceffi 


-- 5 - Afficher les stations essence du dep : 83 ou 69 , on veut filtrer les résulsts  d'une colonne 

select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83'; 

select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '69'; 

select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '69'and ville =  'meyzieu' ; 


-- 6- Compter les stations essence du dep : 83 ou 69 

select 
count(id) as Nb_station_dans_le_83, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83'; 

select 
count(id) as Nb_station_dans_le_69, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '69'; 



-- 7- Afficher les stations essence du département 83 qui ont en SP95 
select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83' and prix_sp95 is not null ;

ou ---- 
select 
adresse, 
Count(prix_sp95),
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83' and prix_sp95 is not null ;


-- 8- Trouver la station la moins chère pour le SP95 du dept 83 ou 69

select 
adresse, 
min(prix_sp95),
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83' and prix_sp95 is not null ;

-- ou 

select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83' and prix_sp95 is not null 
order by prix_sp95 asc


-- ou 

select MAX(prix_sp95) as prix_max, MIN(prix_sp95 )as min_prix
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83'
---------------------
-- pour lyon 
select 
adresse, 
min(prix_sp95),
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '69' and prix_sp95 is not null ;

-- ou 

select 
adresse, 
prix_sp95,
latitude, 
longitude, 
ville, 
code_departement
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '69' and prix_sp95 is not null 
order by prix_sp95 asc

-- ou 

select MAX(prix_sp95) as prix_max, MIN(prix_sp95 )as min_prix
from prix_des_carburants_en_france_flux_instantane pdceffi
where code_departement = '83'

-- Calculer la distance entre les stations essence et chez soi 
-- on as besoin de la longétitude et de la latitude 

SELECT 
  adresse, 
  ville,
  prix_sp95,
  code_departement, -- comme tu veut 
  Round (
  ST_Distance_Sphere(
    ST_GeomFromText('POINT(4.99081 45.76449)'),  -- Point de référence : lon lat
    ST_GeomFromText(CONCAT('POINT(', longitude, ' ', latitude, ')'))  -- Point de la station
  ) / 1000 , 2) AS distance_km
FROM prix_des_carburants_en_france_flux_instantane pdceffi
WHERE code_departement = '69' AND prix_sp95 IS NOT NULL
ORDER BY distance_km ASC;

--  latitude et longétude de l'adresse = 45.76449, 4.99081 > 31 rue paul gauguin meyzieu 

select *
from prix_des_carburants_en_france_flux_instantane pdceffi 




----  

-- 
 Pour power bi
 SHOW TABLES;
 
 SELECT adresse, prix_gazole, prix_gazole_maj
FROM carburant_prix
WHERE adresse LIKE '%Gier%';

