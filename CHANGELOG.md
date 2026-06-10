# Changelog

Toutes les modifications notables de SolarGenflow sont documentées ici.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).
Versionnage selon [Semantic Versioning](https://semver.org/lang/fr/).



---

## [0.3.5] — 2026-06-10

### Ajouté

- Support des traductions natives Home Assistant.
- Ajout du dossier `translations/`.
- Ajout des traductions françaises (`fr.json`).
- Ajout des traductions anglaises (`en.json`).

### Modifié

- Migration des capteurs vers le système `translation_key` de Home Assistant.
- Préparation de l'intégration pour l'affichage automatique des noms selon la langue configurée par l'utilisateur.

### Internationalisation

- Français : noms complets des capteurs SolarGenflow.
- Anglais : noms complets des capteurs SolarGenflow.
- Base prête pour l'ajout d'autres langues ultérieurement.

---

## [0.3.4] — 2026-06-10

### Ajouté

- Nouveau capteur **Home Power**.
  Source officielle : `sensor.jackery_home_power`.
  Représente le flux AC entre la SolarVault et la maison.

- Nouveau capteur **Domestic Load Power**.
  Calcul :
  ```
  Domestic Load Power = Grid Import + Home Power
  ```
  Correspond aux « Charges domestiques » affichées dans l'application Jackery.

- Nouvelle option de configuration `home_power_entity`.
  Valeur par défaut :
  ```
  sensor.jackery_home_power
  ```

### Modifié

- **SolarVault AC Output** redéfini.

  Ancien comportement :
  ```
  SolarVault AC Output = sensor.jackery_home_power
  ```

  Nouveau calcul :
  ```
  SolarVault AC Output = Home Power + Backup Output
  ```

  Le capteur représente désormais la sortie AC totale réelle de la SolarVault.

- **Home Load Total** redéfini.

  Ancien comportement :
  ```
  Home Load Total = Home Power
  ```

  Nouveau calcul :
  ```
  Home Load Total = Domestic Load Power + Backup Output
  ```

  Le capteur représente désormais la consommation totale du système, y compris les charges alimentées via la sortie EPS.

- Clarification complète de la terminologie énergétique.

  Distinction officielle entre :
  - Home Power
  - Domestic Load Power
  - Home Load Total
  - SolarVault AC Output
  - Backup Output

### Corrigé

- Suppression des valeurs négatives erronées de `Home Power`.

  Analyse sur plus de 165 000 mesures :
  les valeurs négatives représentaient environ 1,7 % des échantillons et correspondaient à des glitches MQTT très courts.

  Désormais :
  ```
  Home Power = max(home_power, 0)
  ```

- Amélioration de la cohérence des flux SolarVault / Maison / EPS afin d'obtenir des calculs conformes aux valeurs observées simultanément dans l'application Jackery, Home Assistant et le Shelly Pro 3EM.

## [0.3.3] — 2026-06-10

### Corrigé

- **`Grid Export Power` toujours faux** — Le capteur Jackery `grid_export_power`
  représente en réalité la puissance AC sortant de la SolarVault vers la maison,
  pas un vrai export vers EDF. Il remontait systématiquement des valeurs erronées
  (ex. 281 W alors qu'aucune injection réseau n'avait lieu).
  Désormais `grid_export_power = 0` par défaut. Il ne sera non nul que si un
  capteur d'export dédié (Shelly mesurant l'injection) est explicitement configuré
  dans les options.

- **`Home Load` — formule simplifiée et universelle** — Remplacement de la logique
  conditionnelle à deux branches (sv_out > 0 / sv_out == 0) par une formule unique :
  ```
  Home Load = Grid Import + SolarVault AC Output + Backup Output
  ```
  Chaque source est mesurée indépendamment, la formule est correcte dans tous
  les scénarios : SolarVault active, inactive, ou en recharge réseau.
  Validation sur capture réelle : 296 + 281 + 0 = 577 W vs 542 W Jackery,
  écart résiduel dû uniquement à la latence de polling entre les trois sources.

### Modifié

- `grid_export_power` : ne lit plus `sensor.jackery_grid_export_power` par défaut.
  L'option `grid_export_entity` reste disponible pour brancher un vrai compteur
  d'export si l'installation évolue vers l'injection réseau.

---
## [0.3.2] — 2026-06-10
- corrections Home Load et Battery Net

---

## [0.3.1] — 2026-06-10

### Corrigé

- **Convention de signe `Battery Net Power` Jackery** — La convention réelle est
  `positif = charge DC interne`, `négatif = décharge`, à l'opposé de ce qui était
  implémenté. Conséquence : dès que `Battery Discharge Power` valait 0, le fallback
  dérivait une décharge fictive depuis `battery_net_power`, faisant remonter
  `Battery Discharge Power` à tort (ex. 87 W au lieu de 0 W).

- **Calcul `Home Load` quand la SolarVault est en recharge réseau** — La formule
  ne soustrayait pas `solarvault_ac_input`, comptabilisant à tort la recharge AC
  de la SolarVault comme consommation maison. Exemple observé : surestimation
  d'environ 80 W quand la SolarVault tirait 82 W du réseau pour se recharger.
  Formule corrigée :
  ```
  Home Load = PV - export - charge_batt + décharge_batt + EDF - sv_ac_input
  ```

- **Commentaires `flow_engine.py`** — Mise à jour pour refléter la convention
  Jackery confirmée sur tous les capteurs batterie.

---

## [0.3.0] — 2026-05-xx

### Ajouté

- Publication initiale sur HACS (dépôt personnalisé)
- 14 capteurs exposés : PV Power, PV1–PV4 Power, Battery SOC, Battery Charge Power,
  Battery Discharge Power, Battery Net Power, Grid Import Power, Grid Export Power,
  Home Load, Home Load Total, SolarVault AC Output, SolarVault AC Input,
  SolarVault AC Power, Backup Output Power, Solar Energy Total, Status
- Moteur de flux (`flow_engine.py`) centralisant le calcul des flux énergétiques
- Support Jackery (toutes stations) + Shelly Pro 3EM comme sources
- Configuration via options HA (rechargement automatique sans redémarrage)
- Compatibilité tableau de bord énergie natif Home Assistant

---

## [0.2.3] — 2026-04-xx

### Ajouté
- Capteurs `SolarVault AC Power`, `SolarVault AC Output`, `SolarVault AC Input`
- Capteur `Battery Net Power` (valeur signée brute Jackery)

### Corrigé
- Rechargement automatique de l'intégration lors d'un changement d'options

---

## [0.2.2] — 2026-04-xx

### Ajouté
- Première version publiée sur GitHub
- 11 capteurs initiaux
- Intégration Jackery + Shelly Pro 3EM


---
