# Changelog

Toutes les modifications notables de SolarGenflow sont documentées ici.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).
Versionnage selon [Semantic Versioning](https://semver.org/lang/fr/).

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
