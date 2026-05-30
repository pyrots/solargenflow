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

    @property
    def pv_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity("pv_entity", "sensor.jackery_solar_power")
            ),
            0,
        )

    @property
    def solarvault_ac_output(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "grid_export_entity", "sensor.jackery_grid_export_power"
                )
            ),
            0,
        )

    @property
    def solarvault_ac_input(self):
        # FIX: max(value, 0) était après un return — maintenant appliqué correctement
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "grid_import_entity", "sensor.jackery_grid_import_power"
                )
            ),
            0,
        )

    @property
    def edf_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "edf_power_entity",
                    "sensor.shellypro3em_ac15187c8e84_phase_a_puissance",
                )
            ),
            0,
        )

    @property
    def grid_import_power(self):
        return self.edf_power

    @property
    def grid_export_power(self):
        return self.solarvault_ac_output

    @property
    def home_power(self):
        # Consommation réelle = ce que fournit la Jackery (AC output) + ce qui vient du réseau EDF
        return self.solarvault_ac_output + self.edf_power

    @property
    def home_load_total(self):
        return self.home_power

    @property
    def battery_soc(self):
        return self.get_float_state(
            self.get_option_entity("battery_soc_entity", "sensor.jackery_battery_soc")
        )

    @property
    def battery_net_power(self):
        """Puissance nette batterie (signée : négatif = charge, positif = décharge)."""
        return self.get_float_state(
            self.get_option_entity(
                "battery_net_entity", "sensor.jackery_battery_net_power"
            )
        )

    @property
    def battery_charge_power(self):
        # FIX: était mappé sur battery_net_power (valeur signée) — maintenant sur le bon capteur
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_charge_entity", "sensor.jackery_battery_charge_power"
            )
        )
        return max(raw, 0)

    @property
    def battery_discharge_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "battery_discharge_entity",
                    "sensor.jackery_battery_discharge_power",
                )
            ),
            0,
        )

    @property
    def backup_output_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "backup_entity", "sensor.jackery_eps_output_power"
                )
            ),
            0,
        )

    @property
    def solar_energy_total(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "solar_energy_entity", "sensor.jackery_solar_energy"
                )
            ),
            0,
        )
