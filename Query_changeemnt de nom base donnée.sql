-- Attention quand tu crée une base il faut pas mettre d'accent dans l'intituler  sinon tu re crée une base comme celle ci 
-- ensuite tu concat et tu copie le résulats de la reqeute et tu lance ce qu'il ton donner et refresh ta nouvelle table . 

CREATE DATABASE projet_carburant
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

 SELECT CONCAT(
  'RENAME TABLE `projet 2`.`', table_name, '` TO `projet_carburant`.`', table_name, '`;'
)
FROM information_schema.tables
WHERE table_schema = 'projet 2';


RENAME TABLE `projet 2`.`classe-dpe-fg-de-par-iris (1).csv` TO `projet_carburant`.`classe-dpe-fg-de-par-iris (1).csv`;
RENAME TABLE `projet 2`.`consommation_annuelle_d_electricite_et_gaz_par_departement` TO `projet_carburant`.`consommation_annuelle_d_electricite_et_gaz_par_departement`;
RENAME TABLE `projet 2`.`conso_france` TO `projet_carburant`.`conso_france`;
RENAME TABLE `projet 2`.`logement` TO `projet_carburant`.`logement`;
RENAME TABLE `projet 2`.`part_resident_new` TO `projet_carburant`.`part_resident_new`;
RENAME TABLE `projet 2`.`temperature_journal_dept` TO `projet_carburant`.`temperature_journal_dept`;

select *
from temperature_journal_dept tjd 
limit 10

