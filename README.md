# SolarGenflow

**Energy Flow Engine pour Home Assistant**

SolarGenflow est une intégration custom pour Home Assistant qui centralise et calcule les flux d'énergie de votre installation solaire. Elle agrège les données de votre batterie Jackery, de vos panneaux PV et de votre compteur réseau (Shelly Pro 3EM) pour exposer des capteurs cohérents, prêts pour le tableau de bord énergie de Home Assistant.

![Version](https://img.shields.io/badge/version-0.3.4-blue)
![HACS](https://img.shields.io/badge/HACS-custom-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

---

## Pourquoi SolarGenflow ?

Les intégrations Jackery et Shelly exposent chacune leurs propres capteurs, mais sans cohérence entre elles. SolarGenflow joue le rôle de moteur de flux : il lit ces capteurs, corrige les valeurs signées, calcule les flux manquants (charge batterie, flux SolarVault, charges domestiques et consommation totale) et les expose sous forme d'entités unifiées et fiables.

Le nom résume la philosophie :
- **Solar** — la source : production photovoltaïque
- **Gen** — le générateur/stockage : batterie et station d'énergie
- **Flow** — les flux : qui alimente quoi, surveillance en temps réel

---

## Changelog

## [0.3.4] — 2026-06-10

### Ajouté

- Nouveau capteur **Home Power**.
  Source : `sensor.jackery_home_power`.
  Représente le flux AC envoyé par la SolarVault vers la maison.

- Nouveau capteur **Domestic Load Power**.
  Calcul :
  ```
  Domestic Load Power = Grid Import Power + Home Power
  ```
  Correspond aux « Charges domestiques » affichées dans l'application Jackery.

- Nouvelle option de configuration :
  ```
  home_power_entity
  ```

### Modifié

- **SolarVault AC Output** redéfini.

  Ancien comportement :
  ```
  SolarVault AC Output = sensor.jackery_home_power
  ```

  Nouveau comportement :
  ```
  SolarVault AC Output = Home Power + Backup Output
  ```

- **Home Load Total** redéfini.

  Ancien comportement :
  ```
  Home Load Total = Home Power
  ```

  Nouveau comportement :
  ```
  Home Load Total = Domestic Load Power + Backup Output
  ```

- Clarification complète des flux :
  - Home Power
  - Domestic Load Power
  - Home Load Total
  - SolarVault AC Output
  - Backup Output

### Corrigé

- Filtrage des glitches MQTT négatifs sur `sensor.jackery_home_power`.

  ```
  home_power = max(home_power, 0)
  ```

- Cohérence des calculs validée à partir des mesures croisées Jackery + Shelly Pro 3EM + SolarGenflow.

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
### v0.3.1 — Correction convention batterie & calcul Home Load
- **Correction critique** : inversion de la convention de signe `Battery Net Power` Jackery.
  La convention réelle est `positif = charge DC interne`, `négatif = décharge` — à l'opposé de ce qui était implémenté.
  Conséquence : `Battery Discharge Power` remontait une valeur erronée dès que le capteur dédié valait 0, faussant le calcul de `Home Load`.
- **Correction calcul Home Load** (branche SolarVault inactive) : soustraction de `solarvault_ac_input` pour ne pas comptabiliser la recharge AC de la SolarVault comme consommation maison.
  Avant : `Home Load = PV - export - charge + décharge + EDF` → surestimé quand la SolarVault se rechargeait depuis le réseau.
  Après : `Home Load = PV - export - charge + décharge + EDF - sv_input` → valeur correcte.
- Fallback `battery_charge_power` et `battery_discharge_power` : priorité aux capteurs `_calc` Jackery, puis dérivation depuis `battery_net_power` avec la bonne convention de signe.
- Mise à jour des commentaires du moteur pour refléter la convention Jackery confirmée.

### v0.3.0
- Publication initiale HACS
- 14 capteurs exposés
- Support Jackery + Shelly Pro 3EM

---

## Matériel supporté

| Appareil | Intégration HA requise |
|---|---|
| Jackery (toutes stations) | Intégration Jackery |
| Shelly Pro 3EM | Intégration Shelly |
| Tout compteur exposé comme capteur HA | — |

---

## Capteurs exposés (16 entités)

| Capteur | Unité | Description |
|---|---|---|
| PV Power | W | Production solaire instantanée |
| Solar Energy Total | kWh | Énergie solaire cumulée |
| Battery SOC | % | État de charge de la batterie |
| Battery Charge Power | W | Puissance de charge (≥ 0) |
| Battery Discharge Power | W | Puissance de décharge (≥ 0) |
| Battery Net Power | W | Puissance nette signée (positif = charge) |
| Grid Import Power | W | Import depuis le réseau (source Shelly) |
| Grid Export Power | W | Export vers le réseau |
| Home Power | W | Flux AC SolarVault → maison |
| Domestic Load Power | W | Charges domestiques calculées |
| Home Load Total | W | Consommation totale incluant EPS |
| SolarVault AC Output | W | Sortie AC totale (maison + EPS) |
| SolarVault AC Input | W | Entrée AC de la station ← réseau |
| SolarVault AC Power | W | Bilan AC net (> 0 injecte, < 0 recharge) |
| Backup Output Power | W | Puissance sortie EPS/backup |
| Status | — | État du moteur (Running) |

---

## Convention de signe batterie Jackery

| Capteur | Positif | Négatif |
|---|---|---|
| `Battery Net Power` | Charge DC interne | Décharge |
| `Battery Charge Power` | Charge en cours | — |
| `Battery Discharge Power` | Décharge en cours | — |

---

## Installation via HACS

1. Ouvrir HACS dans Home Assistant
2. Aller dans **Intégrations** → menu ⋮ → **Dépôts personnalisés**
3. Coller l'URL de ce dépôt GitHub, choisir la catégorie **Intégration**, cliquer **Ajouter**
4. Rechercher **SolarGenflow** dans HACS et cliquer **Télécharger**
5. Redémarrer Home Assistant
6. Aller dans **Paramètres → Intégrations → Ajouter une intégration → SolarGenflow**
7. Configurer les capteurs sources dans les options

---

## Configuration

Après ajout de l'intégration, ouvrir les **Options** pour mapper chaque flux à un capteur de votre installation :

| Option | Exemple |
|---|---|
| Production solaire (W) | `sensor.jackery_solar_power` |
| Compteur réseau EDF (W) | `sensor.shellypro3em_phase_a_puissance` |
| État de charge batterie (%) | `sensor.jackery_battery_soc` |
| Puissance de charge batterie (W) | `sensor.jackery_battery_charge_power_calc` |
| Puissance de décharge batterie (W) | `sensor.jackery_battery_discharge_power_calc` |
| Puissance nette batterie (W) | `sensor.jackery_battery_net_power` |
| Import réseau Jackery (W) | `sensor.jackery_grid_import_power` |
| Flux Maison SolarVault (W) | `sensor.jackery_home_power` |
| Export réseau (W) | `sensor.jackery_grid_export_power` |
| Sortie EPS/backup (W) | `sensor.jackery_eps_output_power` |
| Énergie solaire totale (kWh) | `sensor.jackery_solar_energy` |

Les modifications d'options rechargent automatiquement l'intégration sans redémarrage HA.

---

## Tableau de bord énergie HA

Les capteurs SolarGenflow sont compatibles avec le tableau de bord énergie natif de Home Assistant :

- **Production solaire** → `sensor.solargenflow_solar_energy_total`
- **Charges domestiques** → `sensor.solargenflow_domestic_load_power`
- **Import réseau** → `sensor.solargenflow_grid_import_power`
- **Export réseau** → `sensor.solargenflow_grid_export_power`
- **Batterie** → `sensor.solargenflow_battery_soc`

---

## Structure du dépôt

```
custom_components/
  solargenflow/
    __init__.py
    config_flow.py
    const.py
    flow_engine.py
    manifest.json
    sensor.py
    strings.json
    icon.png
    icon@2x.png
hacs.json
README.md
```

---

## Contribuer

Les contributions sont les bienvenues. Ouvrez une issue pour signaler un bug ou proposer une amélioration, ou soumettez directement une pull request.

---

## Licence

MIT — libre d'utilisation, de modification et de distribution.
