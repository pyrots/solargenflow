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
    def edf_power(self):
        """Puissance mesurée par le compteur EDF/Shelly (W, toujours >= 0)."""
        return max(self.get_float_state(
            self.get_option_entity(
                "edf_power_entity",
                "sensor.shellypro3em_ac15187c8e84_phase_a_puissance",
            )
        ), 0)

    @property
    def battery_net_power(self):
        """Puissance nette batterie signée par Jackery.
        Convention Jackery : positif = décharge, négatif = charge.
        """
        return self.get_float_state(
            self.get_option_entity(
                "battery_net_entity", "sensor.jackery_battery_net_power"
            )
        )

    @property
    def battery_charge_power(self):
        """Puissance de charge batterie (W, >= 0).
        On utilise le capteur dédié Jackery battery_charge_power.
        Si indisponible, on dérive depuis battery_net_power (négatif = charge).
        """
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_charge_entity", "sensor.jackery_battery_charge_power"
            )
        )
        if raw > 0:
            return raw
        # Fallback : dériver depuis battery_net_power si négatif
        net = self.battery_net_power
        return max(-net, 0)

    @property
    def battery_discharge_power(self):
        """Puissance de décharge batterie (W, >= 0)."""
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_discharge_entity",
                "sensor.jackery_battery_discharge_power",
            )
        )
        if raw > 0:
            return raw
        # Fallback : dériver depuis battery_net_power si positif
        net = self.battery_net_power
        return max(net, 0)

    @property
    def battery_soc(self):
        return self.get_float_state(
            self.get_option_entity("battery_soc_entity", "sensor.jackery_battery_soc")
        )

    # ─── Flux SolarVault ─────────────────────────────────────────────────────

    @property
    def solarvault_ac_output(self):
        """Ce que la SolarVault envoie vers la maison (W, >= 0).
        Capteur Jackery : home_power ou grid_export_power selon le câblage.
        """
        return max(self.get_float_state(
            self.get_option_entity(
                "solarvault_output_entity", "sensor.jackery_home_power"
            )
        ), 0)

    @property
    def solarvault_ac_input(self):
        """Ce que la SolarVault reçoit depuis le réseau EDF pour se charger (W, >= 0)."""
        return max(self.get_float_state(
            self.get_option_entity(
                "solarvault_input_entity", "sensor.jackery_grid_import_power"
            )
        ), 0)

    # ─── Réseau ───────────────────────────────────────────────────────────────

    @property
    def grid_import_power(self):
        """Import depuis le réseau EDF (W, >= 0) — source Shelly."""
        return self.edf_power

    @property
    def grid_export_power(self):
        """Export vers le réseau (W, >= 0) — capteur Jackery dédié.
        NE PAS confondre avec solarvault_ac_output (= conso maison).
        """
        return max(self.get_float_state(
            self.get_option_entity(
                "grid_export_entity", "sensor.jackery_grid_export_power"
            )
        ), 0)

    # ─── Consommation maison ──────────────────────────────────────────────────

    @property
    def home_power(self):
        """Consommation maison réelle (W).
        = Ce que fournit la SolarVault à la maison + appoint réseau EDF.
        Si solarvault_ac_output non configuré, on calcule :
          PV - export_réseau - charge_batterie + décharge_batterie + import_réseau
        """
        sv_out = self.solarvault_ac_output
        edf = self.edf_power
        if sv_out > 0:
            return sv_out + edf
        # Calcul par bilan énergétique
        return max(
            self.pv_power
            - self.grid_export_power
            - self.battery_charge_power
            + self.battery_discharge_power
            + edf,
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
