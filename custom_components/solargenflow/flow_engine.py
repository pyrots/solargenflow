class SolarGenflowEngine:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

    def get_float_state(self, entity_id, default=0):
        if not entity_id:
            return default
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable", None):
            return default
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return default

    def get_option_entity(self, key, fallback=None):
        return self.entry.options.get(key) or fallback

    # ─── Sources brutes ───────────────────────────────────────────────────────

    @property
    def pv_power(self):
        """Production solaire instantanée (W)."""
        return max(self.get_float_state(
            self.get_option_entity("pv_entity", "sensor.jackery_solar_power")
        ), 0)

    @property
    def pv1_power(self):
        return max(self.get_float_state(
            self.get_option_entity("pv1_entity", "sensor.jackery_solar_power_pv1")
        ), 0)

    @property
    def pv2_power(self):
        return max(self.get_float_state(
            self.get_option_entity("pv2_entity", "sensor.jackery_solar_power_pv2")
        ), 0)

    @property
    def pv3_power(self):
        return max(self.get_float_state(
            self.get_option_entity("pv3_entity", "sensor.jackery_solar_power_pv3")
        ), 0)

    @property
    def pv4_power(self):
        return max(self.get_float_state(
            self.get_option_entity("pv4_entity", "sensor.jackery_solar_power_pv4")
        ), 0)

    @property
    def edf_power(self):
        """Puissance mesurée par le compteur EDF/Shelly (W, >= 0).
        Source de vérité pour l'import réseau.
        """
        return max(self.get_float_state(
            self.get_option_entity(
                "edf_power_entity",
                "sensor.shellypro3em_ac15187c8e84_phase_a_puissance",
            )
        ), 0)

    # ─── Batterie ─────────────────────────────────────────────────────────────

    @property
    def battery_net_power(self):
        """Puissance nette batterie signée par Jackery.
        Convention Jackery confirmée : positif = charge DC interne, négatif = décharge.
        """
        return self.get_float_state(
            self.get_option_entity(
                "battery_net_entity", "sensor.jackery_battery_net_power"
            )
        )

    @property
    def battery_charge_power(self):
        """Puissance de charge batterie (W, >= 0).
        Utilise le capteur dédié Jackery en priorité (_calc de préférence).
        Fallback : battery_net_power positif = charge (convention Jackery).
        """
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_charge_entity",
                "sensor.jackery_battery_charge_power_calc",
            )
        )
        if raw > 0:
            return raw

        net = self.battery_net_power
        return max(net, 0)

    @property
    def battery_discharge_power(self):
        """Puissance de décharge batterie (W, >= 0).
        Utilise le capteur dédié Jackery en priorité (_calc de préférence).
        Fallback : battery_net_power négatif = décharge (convention Jackery).
        """
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_discharge_entity",
                "sensor.jackery_battery_discharge_power_calc",
            )
        )
        if raw > 0:
            return raw

        net = self.battery_net_power
        return max(-net, 0)

    @property
    def battery_soc(self):
        return self.get_float_state(
            self.get_option_entity(
                "battery_soc_entity", "sensor.jackery_battery_soc"
            )
        )

    # ─── Flux SolarVault ──────────────────────────────────────────────────────

    @property
    def home_power(self):
        """Flux AC SolarVault vers la maison (W, >= 0).

        Source directe Jackery : sensor.jackery_home_power.
        Ce n'est pas la consommation totale de la maison.
        Les valeurs négatives très courtes sont des glitches MQTT et sont ignorées.
        """
        return max(self.get_float_state(
            self.get_option_entity(
                "home_power_entity", "sensor.jackery_home_power"
            )
        ), 0)

    @property
    def solarvault_ac_output(self):
        """Sortie AC totale SolarVault (W, >= 0).

        Formule : Home Power + Backup Output.
        - home_power : flux AC SolarVault vers maison
        - backup_output_power : sortie EPS / secours
        """
        return max(self.home_power + self.backup_output_power, 0)

    @property
    def solarvault_ac_input(self):
        """Puissance que la SolarVault tire du réseau EDF pour se recharger (W, >= 0).
        Source : sensor.jackery_grid_import_power
        """
        return max(self.get_float_state(
            self.get_option_entity(
                "solarvault_input_entity", "sensor.jackery_grid_import_power"
            )
        ), 0)

    @property
    def solarvault_ac_power(self):
        """Puissance AC nette SolarVault.
        > 0 : la SolarVault alimente la maison.
        < 0 : la SolarVault se recharge depuis le réseau.
        """
        return self.solarvault_ac_output - self.solarvault_ac_input

    # ─── Réseau ───────────────────────────────────────────────────────────────

    @property
    def grid_import_power(self):
        """Import depuis le réseau EDF (W, >= 0).
        Source de vérité : Shelly Pro 3EM.
        """
        return self.edf_power

    @property
    def grid_export_power(self):
        """Export vers le réseau EDF (W, >= 0).
        Toujours 0 : l'installation est en autoconsommation sans injection réseau.
        Le capteur Jackery 'Grid Export Power' représente en réalité la puissance
        AC sortant de la SolarVault vers la maison — ce n'est pas un export EDF.
        Ce capteur sera activé uniquement si un compteur d'export dédié est configuré.
        """
        export_entity = self.get_option_entity("grid_export_entity")
        if not export_entity:
            return 0
        return max(self.get_float_state(export_entity), 0)

    # ─── Consommation maison ──────────────────────────────────────────────────

    @property
    def domestic_load_power(self):
        """Charges domestiques calculées (W, >= 0).

        Formule validée : Grid Import + Home Power.
        Correspond aux "Charges domestiques" affichées dans l'application Jackery,
        hors sortie EPS / backup.
        """
        return max(self.grid_import_power + self.home_power, 0)

    @property
    def home_load_total(self):
        """Consommation totale du site (W, >= 0).

        Formule validée : Domestic Load Power + Backup Output.
        """
        return max(self.domestic_load_power + self.backup_output_power, 0)

    # ─── Divers ───────────────────────────────────────────────────────────────

    @property
    def backup_output_power(self):
        return max(self.get_float_state(
            self.get_option_entity(
                "backup_entity", "sensor.jackery_eps_output_power"
            )
        ), 0)

    @property
    def solar_energy_total(self):
        return max(self.get_float_state(
            self.get_option_entity(
                "solar_energy_entity", "sensor.jackery_solar_energy"
            )
        ), 0)
