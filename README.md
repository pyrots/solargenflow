# SolarGenflow

**Energy Flow Engine pour Home Assistant**

SolarGenflow est une intégration custom pour Home Assistant qui centralise et calcule les flux d'énergie de votre installation solaire. Elle agrège les données de votre batterie Jackery, de vos panneaux PV et de votre compteur réseau (Shelly Pro 3EM) pour exposer des capteurs cohérents, prêts pour le tableau de bord énergie de Home Assistant.

![Version](https://img.shields.io/badge/version-0.2.2-blue)
![HACS](https://img.shields.io/badge/HACS-custom-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

---

## Pourquoi SolarGenflow ?

Les intégrations Jackery et Shelly exposent chacune leurs propres capteurs, mais sans cohérence entre elles. SolarGenflow joue le rôle de moteur de flux : il lit ces capteurs, corrige les valeurs signées, calcule les flux manquants (charge batterie, consommation maison, export réseau) et les expose sous forme d'entités unifiées et fiables.

Le nom résume la philosophie :
- **Solar** — la source : production photovoltaïque
- **Gen** — le générateur/stockage : batterie et station d'énergie
- **Flow** — les flux : qui alimente quoi, surveillance en temps réel

---

## Matériel supporté

| Appareil | Intégration HA requise |
|---|---|
| Jackery (toutes stations) | Intégration Jackery |
| Shelly Pro 3EM | Intégration Shelly |
| Tout compteur exposé comme capteur HA | — |

---

## Capteurs exposés (14 entités)

| Capteur | Unité | Description |
|---|---|---|
| PV Power | W | Production solaire instantanée |
| Solar Energy Total | kWh | Énergie solaire cumulée |
| Battery SOC | % | État de charge de la batterie |
| Battery Charge Power | W | Puissance de charge (≥ 0) |
| Battery Discharge Power | W | Puissance de décharge (≥ 0) |
| Battery Net Power | W | Puissance nette signée |
| Grid Import Power | W | Import depuis le réseau |
| Grid Export Power | W | Export vers le réseau |
| Home Load | W | Consommation maison calculée |
| Home Load Total | W | Consommation maison totale |
| SolarVault AC Output | W | Sortie AC de la station |
| SolarVault AC Input | W | Entrée AC de la station |
| Backup Output Power | W | Puissance sortie EPS/backup |
| Status | — | État du moteur (Running) |

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
| Puissance de charge batterie (W) | `sensor.jackery_battery_charge_power` |
| Puissance de décharge batterie (W) | `sensor.jackery_battery_discharge_power` |
| Puissance nette batterie (W) | `sensor.jackery_battery_net_power` |
| Import réseau (W) | `sensor.jackery_grid_import_power` |
| Export réseau (W) | `sensor.jackery_grid_export_power` |
| Sortie EPS/backup (W) | `sensor.jackery_eps_output_power` |
| Énergie solaire totale (kWh) | `sensor.jackery_solar_energy` |

Les modifications d'options rechargent automatiquement l'intégration sans redémarrage HA.

---

## Tableau de bord énergie HA

Les capteurs SolarGenflow sont compatibles avec le tableau de bord énergie natif de Home Assistant :

- **Production solaire** → `sensor.solargenflow_solar_energy_total`
- **Consommation maison** → `sensor.solargenflow_home_load`
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
