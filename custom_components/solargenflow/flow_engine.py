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
        """Puissance mesurée par le compteur EDF/Shelly (W, toujours >= 0)."""
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

        # Fallback sur battery_net_power : positif = charge
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

        # Fallback sur battery_net_power : négatif = décharge
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
    def solarvault_ac_output(self):
        """Ce que la SolarVault envoie vers la maison (W, >= 0)."""
        return max(self.get_float_state(
            self.get_option_entity(
                "solarvault_output_entity", "sensor.jackery_home_power"
            )
        ), 0)

    @property
    def solarvault_ac_input(self):
        """Ce que la SolarVault tire du réseau EDF pour se recharger (W, >= 0)."""
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
        """Import depuis le réseau EDF (W, >= 0) — source Shelly (vérité terrain)."""
        return self.edf_power

    @property
    def grid_export_power(self):
        """Export vers le réseau (W, >= 0) — capteur Jackery dédié."""
        return max(self.get_float_state(
            self.get_option_entity(
                "grid_export_entity", "sensor.jackery_grid_export_power"
            )
        ), 0)

    # ─── Consommation maison ──────────────────────────────────────────────────

    @property
    def home_power(self):
        """Consommation maison réelle (W).

        Deux cas :
        1. SolarVault injecte dans la maison (sv_out > 0) :
           maison = SolarVault AC Output + réseau EDF

        2. SolarVault inactive ou en recharge (sv_out == 0) :
           maison = PV - export - charge_batt + décharge_batt + EDF - sv_input
           On soustrait solarvault_ac_input car la SolarVault tire du réseau
           pour se recharger : ces watts ne sont pas de la consommation maison.
        """
        sv_out = self.solarvault_ac_output
        sv_in = self.solarvault_ac_input
        edf = self.edf_power

        if sv_out > 0:
            return sv_out + edf

        return max(
            self.pv_power
            - self.grid_export_power
            - self.battery_charge_power
            + self.battery_discharge_power
            + edf
            - sv_in,
            0,
        )

    @property
    def home_load_total(self):
        return self.home_power

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
